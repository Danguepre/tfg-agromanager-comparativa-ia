"""
Modelo TaskCrop (relación muchos a muchos entre Task y Crop).
"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class TaskCrop(Base, TimestampMixin):
    """Modelo de relación muchos a muchos entre Task y Crop."""

    __tablename__ = "task_crops"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)

    # Relaciones
    task = relationship("Task", back_populates="task_crops")
    crop = relationship("Crop", back_populates="task_crops")

    def __repr__(self) -> str:
        return f"<TaskCrop(task_id={self.task_id}, crop_id={self.crop_id})>"
