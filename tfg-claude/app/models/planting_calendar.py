"""
Modelo PlantingCalendar.
Calendario agrícola asociado a cultivos con fases de siembra, trasplante y cosecha.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base
from app.models.base import TimestampMixin


class CalendarStatus(str, enum.Enum):
    """Estados del calendario."""
    DRAFT = "draft"          # No activado
    ACTIVE = "active"        # Activo y siendo seguido
    COMPLETED = "completed"  # Finalizado


class PlantingCalendar(Base, TimestampMixin):
    """Modelo de calendario agrícola con fases."""

    __tablename__ = "planting_calendars"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False, unique=True)
    
    # Fechas de las fases (DD-MM, sin año)
    planting_start = Column(Date, nullable=True)      # Fecha inicio siembra
    planting_end = Column(Date, nullable=True)        # Fecha fin siembra
    transplant_start = Column(Date, nullable=True)    # Fecha inicio trasplante
    transplant_end = Column(Date, nullable=True)      # Fecha fin trasplante
    harvest_start = Column(Date, nullable=True)       # Fecha inicio cosecha
    harvest_end = Column(Date, nullable=True)         # Fecha fin cosecha
    
    # Estado del calendario
    is_active = Column(Boolean, default=False, nullable=False)
    current_phase_index = Column(Integer, default=0, nullable=False)  # 0=Siembra, 1=Trasplante, 2=Cosecha
    status = Column(String(20), default=CalendarStatus.DRAFT, nullable=False)  # draft, active, completed

    # Relaciones
    crop = relationship("Crop", back_populates="planting_calendars")

    def __repr__(self) -> str:
        return f"<PlantingCalendar(id={self.id}, crop_id={self.crop_id}, status={self.status}, phase_idx={self.current_phase_index})>"
