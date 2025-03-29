import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from contextlib import asynccontextmanager

from sqlalchemy import select, func

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

from services.task_service import get_date, get_tasks


# Создаем обработчик жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаем таблицы в базе данных
    yield  # Приложение запускается после выполнения этого блока


# Создаем FastAPI-приложение с переданным lifespan
app = FastAPI(lifespan=lifespan)


# Создаем объект схемы OAuth2 для получения токена
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
SECRET_KEY = "mysecretkey"
security = HTTPBearer()
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
        return {"Ваш токен access_token": token, "token_type": "bearer"}
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
        print(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        # Логируем ответ
        print(f"Response: {response.status_code}")
        return response

# Подключаем маршруты
app.include_router(task_router.router)

# Jinja2Templates позволяет использовать шаблоны во вьюхах FastAPI
templates = Jinja2Templates(directory="Templates")  # Указываем где расположен шаблон

# LogMiddleware логирует метод и URL каждого запроса, а также статус-код каждого ответа.
# Middleware добавляется к приложению с помощью метода add_middleware
app.add_middleware(LogMiddleware)

date_time = get_date()


@app.get("/")
async def root(request: Request):
    """Отображаем главную страницу"""
    return templates.TemplateResponse(name='index.html', context={"request":request, 'date_time': date_time})


@app.get("/todo")
async def todo_page(request: Request, db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 100):
    """Переход на страницу добавления задач и получение всех задач из БД"""

    # Подсчитываем количество задач
    result_count = await db.execute(select(func.count(Task.id)))
    # tasks_count = result_count.all() # Получаем количество задач
    # tasks_count = result_count.fetchone()[0]  # Получаем количество задач
    # tasks_count = result_count.fetchall()[0][0]  # Получаем количество задач
    tasks_count = result_count.scalar() # Получаем количество задач

    # Получаем задачи с учётом пагинации
    result_tasks = await db.execute(select(Task).offset(skip).limit(limit))
    tasks = result_tasks.scalars().all()  # Получаем список задач

    return templates.TemplateResponse('todo.html', {"request": request, "tasks": tasks, "tasks_count": tasks_count})


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
