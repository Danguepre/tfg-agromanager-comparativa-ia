"""
Modelo EnvironmentalRequirements.
"""
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class EnvironmentalRequirements(Base, TimestampMixin):
    """Modelo de requisitos ambientales."""

    __tablename__ = "environmental_requirements"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False, unique=True)
    min_temperature_celsius = Column(Float, nullable=True)
    max_temperature_celsius = Column(Float, nullable=True)
    min_humidity_percent = Column(Float, nullable=True)
    max_humidity_percent = Column(Float, nullable=True)
    sunlight_hours_per_day = Column(Float, nullable=True)
    soil_type = Column(String(100), nullable=True)
    soil_ph_min = Column(Float, nullable=True)
    soil_ph_max = Column(Float, nullable=True)

    # Relaciones
    crop = relationship("Crop", back_populates="environmental")

    def __repr__(self) -> str:
        return f"<EnvironmentalRequirements(id={self.id}, crop_id={self.crop_id}, temp={self.min_temperature_celsius}-{self.max_temperature_celsius}°C)>"
