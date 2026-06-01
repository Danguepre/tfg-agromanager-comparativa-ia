from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class TaskCrop(Base):
    __tablename__ = "task_crops"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    crop_id = Column(Integer, ForeignKey("crops.id", ondelete="CASCADE"))

    task = relationship("Task", back_populates="crops")
    crop = relationship("Crop", back_populates="tasks")