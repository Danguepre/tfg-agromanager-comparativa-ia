"""
Modelo IrrigationAttributes.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class IrrigationAttributes(Base, TimestampMixin):
    """Modelo de atributos de riego."""

    __tablename__ = "irrigation_attributes"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False, unique=True)
    water_frequency_days = Column(Integer, nullable=True)  # Días entre riegos
    water_amount_mm = Column(Float, nullable=True)  # mm de agua
    irrigation_type = Column(String(100), nullable=True)  # "riego por goteo", "aspersión", etc.
    notes = Column(String(500), nullable=True)

    # Relaciones
    crop = relationship("Crop", back_populates="irrigation")

    def __repr__(self) -> str:
        return f"<IrrigationAttributes(id={self.id}, crop_id={self.crop_id}, frequency={self.water_frequency_days}d)>"
