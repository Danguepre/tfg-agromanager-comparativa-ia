"""Modelo de Requisitos Ambientales."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EnvironmentalRequirements(Base):
    """Requisitos ambientales para un cultivo."""

    __tablename__ = "environmental_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crop_id: Mapped[int] = mapped_column(Integer, ForeignKey("crops.id"), unique=True, nullable=False)
    min_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    optimal_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    min_ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    optimal_ph: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sunlight_hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    humidity_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    hardiness_zone: Mapped[str | None] = mapped_column(String(50), nullable=True)
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

    crop = relationship("Crop", back_populates="environmental")