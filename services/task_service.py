from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from db.models import Task
from schemas.task_schema import TaskCreate, TaskUpdate, TaskInDB


async def create_task(db: AsyncSession, task: TaskCreate) -> TaskInDB:
    """Асинхронная функция, которая создает таску"""
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status
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
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()
    if task:
        task.title = task_update.title
        task.description = task_update.description
        task.status = task_update.status
        await db.commit()
        await db.refresh(task)
        return task
    return None


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

        await db.commit()
        await db.refresh(task)
        return task
    return None


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    result = await db.execute(select(Task).filter(Task.id == task_id))
    task = result.scalars().first()
    if task:
        await db.delete(task)
        await db.commit()
        return True
    return False
