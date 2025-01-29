from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
import enum


# Base = declarative_base()
class Base(DeclarativeBase):
    pass


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.pending, nullable=False)
    nice: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)
