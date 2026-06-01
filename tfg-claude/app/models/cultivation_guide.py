"""
Modelo CultivationGuide.
"""
from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class CultivationGuide(Base, TimestampMixin):
    """Modelo de guía de cultivo."""

    __tablename__ = "cultivation_guides"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False, unique=True)
    preparation = Column(Text, nullable=True)  # Preparación del terreno
    planting_instructions = Column(Text, nullable=True)  # Instrucciones de siembra
    care_instructions = Column(Text, nullable=True)  # Cuidados durante cultivo
    harvesting_instructions = Column(Text, nullable=True)  # Instrucciones de cosecha
    storage_instructions = Column(Text, nullable=True)  # Almacenamiento

    # Relaciones
    crop = relationship("Crop", back_populates="cultivation_guide")

    def __repr__(self) -> str:
        return f"<CultivationGuide(id={self.id}, crop_id={self.crop_id})>"
