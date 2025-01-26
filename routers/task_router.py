from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.task_schema import TaskCreate, TaskUpdate, TaskInDB
from services.task_service import create_task, get_task, get_tasks, update_task, delete_task, patch_task
from db.database import get_db

router = APIRouter()

@router.post("/tasks/", response_model=TaskInDB)
async def create_task_endpoint(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await create_task(db, task)

@router.get("/tasks/{task_id}", response_model=TaskInDB)
async def get_task_endpoint(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/tasks/", response_model=list[TaskInDB])
async def get_tasks_endpoint(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_tasks(db, skip, limit)

@router.put("/tasks/{task_id}", response_model=TaskInDB)
async def update_task_endpoint(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    updated_task = await update_task(db, task_id, task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task

# @router.patch("/tasks/{task_id}", response_model=TaskInDB)
# async def update_task_endpoint(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
#     task = await patch_task(db, task_id, task)
#     if task is None:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return task

@router.patch("/tasks/{task_id}", response_model=TaskInDB)
async def update_task_route(task_id: int, task_update: TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await patch_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task



@router.delete("/tasks/{task_id}", response_model=bool)
async def delete_task_endpoint(task_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return success
