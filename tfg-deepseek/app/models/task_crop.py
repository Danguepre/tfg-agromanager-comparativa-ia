"""Modelo asociativo Task-Crop (muchos a muchos)."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TaskCrop(Base):
    """Asociación muchos-a-muchos entre tareas y cultivos."""

    __tablename__ = "task_crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    crop_id: Mapped[int] = mapped_column(Integer, ForeignKey("crops.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    task = relationship("Task", back_populates="task_crops")
    crop = relationship("Crop", back_populates="task_crops")