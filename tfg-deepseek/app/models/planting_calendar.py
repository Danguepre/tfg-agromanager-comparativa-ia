"""Modelo de Calendario Agrícola por Fases (FASE 5)."""

from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PlantingCalendar(Base):
    """Calendario agrícola por fases: siembra, trasplante, cosecha."""

    __tablename__ = "planting_calendars"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crop_id: Mapped[int] = mapped_column(Integer, ForeignKey("crops.id"), unique=True, nullable=False)
    planting_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    planting_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    transplant_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    transplant_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    harvest_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    harvest_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    current_phase_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="0=Siembra, 1=Trasplante, 2=Cosecha")
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False, comment="draft|active|completed")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    crop = relationship("Crop", back_populates="planting_calendar")