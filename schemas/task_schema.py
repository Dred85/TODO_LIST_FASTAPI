from pydantic import BaseModel
from datetime import datetime
from enum import Enum




class TaskStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class TaskImportance(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskBase(BaseModel):
    """Pydantic-схема или Класс схема для валидации данных"""
    title: str
    description: str | None = None
    status: str = "NEW"
    importance: str = "HIGH"


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
