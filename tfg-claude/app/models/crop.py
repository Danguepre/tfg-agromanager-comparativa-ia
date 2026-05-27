"""
Modelo Crop.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class Crop(Base, TimestampMixin):
    """Modelo de cultivo."""

    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    crop_type = Column(String(100), nullable=True)  # "verdura", "fruta", "cereal", etc.
    image_path = Column(String(500), nullable=True)  # Ruta relativa en /uploads/crops/
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # None si es público del sistema
    is_public = Column(Boolean, default=False, nullable=False)
    source_crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)  # Si es copia de otro cultivo

    # Relaciones
    owner = relationship("User", back_populates="crops")
    planting_calendars = relationship("PlantingCalendar", back_populates="crop", cascade="all, delete-orphan")
    irrigation = relationship("IrrigationAttributes", back_populates="crop", uselist=False, cascade="all, delete-orphan")
    environmental = relationship(
        "EnvironmentalRequirements", back_populates="crop", uselist=False, cascade="all, delete-orphan"
    )
    cultivation_guide = relationship("CultivationGuide", back_populates="crop", uselist=False, cascade="all, delete-orphan")
    task_crops = relationship("TaskCrop", back_populates="crop", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Crop(id={self.id}, name={self.name}, owner_id={self.owner_id}, is_public={self.is_public})>"
