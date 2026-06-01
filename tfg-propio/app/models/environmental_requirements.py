from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class EnvironmentalRequirements(Base):
    __tablename__ = "environmental_requirements"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"))

    sun_exposure = Column(String)
    min_temp = Column(Float)
    max_temp = Column(Float)
    frost_tolerance = Column(Boolean)

    crop = relationship("Crop", back_populates="environmental")