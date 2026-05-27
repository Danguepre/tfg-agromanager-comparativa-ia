"""
Modelo Task.
"""
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class TaskStatus(str, Enum):
    """Estados de una tarea."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(Base, TimestampMixin):
    """Modelo de tarea."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    due_date = Column(String, nullable=True)  # ISO 8601 fecha

    # Relaciones
    owner = relationship("User", back_populates="tasks")
    task_crops = relationship("TaskCrop", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, owner_id={self.owner_id}, status={self.status})>"
