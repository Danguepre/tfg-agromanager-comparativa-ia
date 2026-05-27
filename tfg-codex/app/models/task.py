from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TaskCrop(Base):
    __tablename__ = "task_crops"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), primary_key=True)

    task = relationship("Task", back_populates="crop_links")
    crop = relationship("Crop", back_populates="task_links")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="pending", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    owner = relationship("User", back_populates="tasks")
    crop_links = relationship("TaskCrop", back_populates="task", cascade="all, delete-orphan")
