from databases import Database
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

import os
from pathlib import Path
from dotenv import load_dotenv


class Model(DeclarativeBase):
    pass


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем асинхронный движок
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Используем базу данных через библиотеку databases
database = Database(DATABASE_URL)
metadata = MetaData()
