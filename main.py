import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException, Form, Response
from contextlib import asynccontextmanager
import logging
import sys
from logging.handlers import RotatingFileHandler

from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select, func
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.responses import JSONResponse

from db.models import Task
from httpx import request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.testing import db, skip
from starlette.templating import Jinja2Templates

from db.database import async_engine, get_db
from db.models import Base
from routers import task_router
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, HTTPAuthorizationCredentials
import jwt

from schemas.task_schema import TaskCreate, TaskUpdate
from services.task_service import get_date, get_tasks, get_task, create_task, update_task, delete_task

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("todo_app")
logger.setLevel(logging.INFO)

# Добавляем файловый обработчик
file_handler = RotatingFileHandler(
    "/var/log/todo_app/app.log",
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)

# Создаем обработчик жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаем таблицы в базе данных
    yield  # Приложение запускается после выполнения этого блока


# Создаем FastAPI-приложение с переданным lifespan
app = FastAPI(lifespan=lifespan)
# Подключение метрик 
Instrumentator().instrument(app).expose(app)


# Создаем объект схемы OAuth2 для получения токена
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
SECRET_KEY = "mysecretkey"
security = HTTPBearer()

templates = Jinja2Templates(directory="Templates")

# Специфичные маршруты должны быть перед общими
@app.get("/tasks/create", response_class=HTMLResponse)
async def create_task_page(request: Request):
    return templates.TemplateResponse(request=request, name="create_task.html")

# Обрабатываем отправку формы и создаём задачу
@app.post("/tasks/create")
async def create_task_handler(
    title: str = Form(...),
    description: str = Form(""),
    status: str = Form("pending"),
    importance: str = Form("Важное"),
    db: AsyncSession = Depends(get_db)
):
    task_data = TaskCreate(
        title=title,
        description=description,
        status=status,
        importance=importance
    )
    new_task = await create_task(db, task_data)
    logger.info(f"Created new task: {new_task.title}")
    return RedirectResponse(url="/todo", status_code=303)

# Страница редактирования задачи (должна быть перед просмотром задачи!)
@app.get("/tasks/edit/{task_id}", response_class=HTMLResponse)
async def edit_task_page(request: Request, task_id: int, db: AsyncSession = Depends(get_db)):
    """Страница редактирования задачи"""
    try:
        task = await get_task(db, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Editing task page: {task.title}")
        return templates.TemplateResponse(
            "edit_task.html",
            {
                "request": request,
                "task": task
            }
        )
    except Exception as e:
        logger.error(f"Error loading edit page: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": str(e)
            },
            status_code=500
        )

# Обработка формы редактирования
@app.post("/tasks/edit/{task_id}")
async def edit_task_handler(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(""),
    status: str = Form("NEW"),
    importance: str = Form("HIGH"),
    db: AsyncSession = Depends(get_db)
):
    """Обработка формы редактирования"""
    try:
        task_update = TaskUpdate(
            title=title,
            description=description,
            status=status,
            importance=importance
        )
        
        updated_task = await update_task(db, task_id, task_update)
        if updated_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Updated task: {updated_task.title}")
        return RedirectResponse(url=f"/tasks/{task_id}", status_code=303)
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Error updating task: {str(e)}"
            },
            status_code=500
        )

# Удаление задачи
@app.post("/tasks/delete/{task_id}")
async def delete_task_handler(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = await delete_task(db, task_id)
    logger.info(f"Deleted task: {task.title}")
    return RedirectResponse(url="/todo", status_code=303)

# Просмотр задачи
@app.get("/tasks/{task_id}", response_class=HTMLResponse)
async def view_task(request: Request, task_id: int, db: AsyncSession = Depends(get_db)):
    """Просмотр задачи"""
    try:
        task = await get_task(db, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Viewing task: {task.title}")
        response = templates.TemplateResponse(
            "view_task.html",
            {
                "request": request,
                "task": task
            }
        )
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response
    except Exception as e:
        logger.error(f"Error viewing task: {str(e)}")
        error_response = templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": str(e)
            }
        )
        error_response.headers["Content-Type"] = "text/html; charset=utf-8"
        return error_response

@app.post("/tasks/{task_id}")
async def update_task_handler(
    request: Request,
    task_id: int,
    title: str = Form(...),
    description: str = Form(""),
    status: str = Form("pending"),
    importance: str = Form("Важное"),
    db: AsyncSession = Depends(get_db)
):
    """Обработка формы обновления задачи"""
    try:
        task_update = TaskUpdate(
            title=title,
            description=description,
            status=status,
            importance=importance
        )
        
        updated_task = await update_task(db, task_id, task_update)
        if updated_task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Updated task: {updated_task.title}")
        return RedirectResponse(url="/todo", status_code=303)
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_message": f"Error updating task: {str(e)}"
            },
            status_code=500
        )

@app.get("/api/tasks/{task_id}")
async def get_task_api(task_id: int, db: AsyncSession = Depends(get_db)):
    """API endpoint для получения задачи в формате JSON"""
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return JSONResponse(content=task.to_dict())

@app.get("/")
async def root(request: Request):
    """Отображаем главную страницу"""
    logger.info("Accessing root page")
    return templates.TemplateResponse(
        name='index.html',
        context={"request": request, 'date_time': get_date()}
    )

@app.get("/todo", response_class=HTMLResponse)
async def todo_page(request: Request, db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """Переход на страницу со списком задач"""
    logger.info("Accessing todo page")
    tasks = await get_tasks(db, skip, limit)
    tasks_count = len(tasks)
    logger.info(f"Found {tasks_count} tasks")
    return templates.TemplateResponse(
        "todo.html",
        {
            "request": request,
            "tasks": tasks,
            "tasks_count": tasks_count
        }
    )

# Верификация JWT токена
def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials  # Получаем сам токен
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/token")
def login(username: str, password: str):
    # Проверяем логин и пароль
    if username == "dred" and password == "password":
        token = jwt.encode({"user_id": 1}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Invalid credentials")


@app.get("/protected")
def protected_route(user_id: int = Depends(verify_jwt_token)):
    return {"message": f"Hello, user {user_id}"}


@app.get("/about_me")
def get_about_protected(user: int = Depends(verify_jwt_token)):
    """Общая информация о разрабе приложения"""
    return {"message": "разработчик приложения DRED"}


class LogMiddleware(BaseHTTPMiddleware):
    """Этот класс позволяет логировать запросы и ответы"""

    async def dispatch(self, request: Request, call_next):
        # Логируем запрос
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        # Логируем ответ
        logger.info(f"Response: {response.status_code}")
        return response


class HTMLMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки HTML-ответов"""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if isinstance(response, HTMLResponse) or (
            hasattr(response, "template") and 
            hasattr(response, "context")
        ):
            response.headers["Content-Type"] = "text/html; charset=utf-8"
        return response


# Подключаем маршруты
app.include_router(task_router.router)

# Jinja2Templates позволяет использовать шаблоны во вьюхах FastAPI
templates = Jinja2Templates(directory="Templates")  # Указываем где расположен шаблон

# Добавляем middleware в правильном порядке
app.add_middleware(HTMLMiddleware)
app.add_middleware(LogMiddleware)

date_time = get_date()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
