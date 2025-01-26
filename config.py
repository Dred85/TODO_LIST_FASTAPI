from databases import Database
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Model(DeclarativeBase):
    pass

DATABASE_URL = "postgresql+asyncpg://postgres:qwertyuiop123#@localhost/todo_fastapi"

# Создаем асинхронный движок
# engine = create_engine(DATABASE_URL)




async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


# Используем базу данных через библиотеку databases
database = Database(DATABASE_URL)
metadata = MetaData()