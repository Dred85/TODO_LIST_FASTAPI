from typing import Optional

from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskBase(BaseModel):
    """Pydantic-схема или Класс схема для валидации данных"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskPut(TaskBase):
    pass


class TaskInDB(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
