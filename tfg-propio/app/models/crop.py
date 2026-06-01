from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    life_cycle = Column(String)
    image_url = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    source_crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="crops")
    source_crop = relationship("Crop", remote_side=[id])
    calendar = relationship("PlantingCalendar", back_populates="crop", uselist=False)
    environmental = relationship("EnvironmentalRequirements", back_populates="crop", uselist=False)
    irrigation = relationship("IrrigationAttributes", back_populates="crop", uselist=False)
    guides = relationship("CultivationGuide", back_populates="crop")
    tasks = relationship("TaskCrop", back_populates="crop")
