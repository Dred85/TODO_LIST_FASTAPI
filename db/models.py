from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
import enum
from db.database import Base


# Base = declarative_base()
class Base(DeclarativeBase):
    pass


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskImportance(str, enum.Enum):
    important = "Важное"
    very_important = "Очень важное"
    not_important= "Не важное"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, default="pending")
    importance = Column(String, default="Важное")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __str__(self):
        return f"Task(id={self.id}, title={self.title})"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "importance": self.importance,
            "created_at": self.created_at
        }
