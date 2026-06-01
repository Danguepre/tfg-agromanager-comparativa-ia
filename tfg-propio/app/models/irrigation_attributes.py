from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class IrrigationAttributes(Base):
    __tablename__ = "irrigation_attributes"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"))

    watering_frequency = Column(String)
    water_amount = Column(Float)
    recommendations = Column(Text)

    crop = relationship("Crop", back_populates="irrigation")