from databases import Database
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
from os.path import join, dirname
from dotenv import load_dotenv

class Model(DeclarativeBase):
    pass


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DATABASE_URL = os.environ.get('DATABASE_URL')

# Создаем асинхронный движок
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Используем базу данных через библиотеку databases
database = Database(DATABASE_URL)
metadata = MetaData()
