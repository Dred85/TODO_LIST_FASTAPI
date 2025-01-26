import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.database import async_engine
from db.models import Base
from routers import task_router

# Создаем обработчик жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаем таблицы в базе данных
    yield  # Приложение запускается после выполнения этого блока

# Создаем FastAPI-приложение с переданным lifespan
app = FastAPI(lifespan=lifespan)

# Подключаем маршруты
app.include_router(task_router.router)

@app.get("/")
async def root():
    return {"message": "Task Management API"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
