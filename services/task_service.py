from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import UploadFile
import time
from db.models import Task
from schemas.task_schema import TaskCreate, TaskUpdate, TaskInDB
from fastapi.responses import StreamingResponse, FileResponse
import logging

logger = logging.getLogger("todo_app")


def transfer_file(filename: str):
    """Передает файлы"""
    return FileResponse(filename)


async def load_file(upload_file: UploadFile):
    """Асинхронная функция, которая загружает файл"""
    file = upload_file.file
    filename = upload_file.filename
    with open(f"1_{filename}", "wb", ) as f:
        f.write(file.read())
    return {"message": "Загрузка завершена"}

async def load_multiple_file(upload_files: list[UploadFile]):
    """Асинхронная функция, которая загружает несколько файлов"""
    for upload_file in upload_files:
        file = upload_file.file
        filename = upload_file.filename
        with open(f"1_{filename}", "wb", ) as f:
            f.write(file.read())
    return {"message": "Загрузка файлов завершена"}



async def create_task(db: AsyncSession, task: TaskCreate) -> TaskInDB:
    """Асинхронная функция, которая создает таску"""
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        importance=task.importance
    )
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def get_task(db: AsyncSession, task_id: int) -> TaskInDB:
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()
    return task


async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[TaskInDB]:
    result = await db.execute(select(Task).offset(skip).limit(limit))
    tasks = result.scalars().all()
    return tasks


async def update_task(db: AsyncSession, task_id: int, task_update: TaskUpdate) -> TaskInDB:
    """Обновление задачи"""
    try:
        logger.info(f"Attempting to update task {task_id} with data: {task_update}")
        result = await db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalars().first()
        
        if task is None:
            logger.error(f"Task {task_id} not found")
            return None
            
        # Сохраняем старые значения для логирования
        old_values = {
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "importance": task.importance
        }
        
        # Обновляем значения
        task.title = task_update.title
        task.description = task_update.description
        task.status = task_update.status
        task.importance = task_update.importance
        
        await db.commit()
        await db.refresh(task)
        
        logger.info(f"Successfully updated task {task_id}. Old values: {old_values}, New values: {task_update}")
        return task
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        raise


async def patch_task(db: AsyncSession, task_id: int, task_update: TaskUpdate) -> TaskInDB | None:
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()
    if task:
        # Обновляем только те поля, которые переданы в запросе
        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.status is not None:
            task.status = task_update.status
        if task_update.importance is not None:
            task.importance = task_update.importance

        await db.commit()
        await db.refresh(task)
        return task
    return None


async def delete_task(db: AsyncSession, task_id: int) -> str:
    """Удалить таску"""
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()
    if task:
        await db.delete(task)
        await db.commit()
        return f"Таска удалена!"
    return f"Произошла ошибка"

def get_date():
    """Возвращает текущую дату и время в формате YYYY-MM-DD HH:MM:SS"""
    date_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())  # Получаем текущую дату и время в формате YYYY-MM-DD HH:MM:SS
    return date_time
