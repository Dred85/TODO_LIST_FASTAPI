from pydantic import BaseModel
from datetime import datetime
from enum import Enum




class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskImportance(str, Enum):
    high = "Важное"
    medium = "Среднее"
    low = "Низкое"


class TaskBase(BaseModel):
    """Pydantic-схема или Класс схема для валидации данных"""
    title: str
    description: str | None = None
    status: str = "pending"
    importance: str = "Важное"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    importance: str | None = None


class TaskPut(TaskBase):
    pass


class TaskInDB(TaskBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
