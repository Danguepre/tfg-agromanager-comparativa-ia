"""Modelo de Atributos de Riego."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IrrigationAttributes(Base):
    """Atributos de riego para un cultivo."""

    __tablename__ = "irrigation_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crop_id: Mapped[int] = mapped_column(Integer, ForeignKey("crops.id"), unique=True, nullable=False)
    frequency_days: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Frecuencia en días")
    water_needed_mm: Mapped[float | None] = mapped_column(Float, nullable=True, comment="Agua necesaria en mm")
    irrigation_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
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

    crop = relationship("Crop", back_populates="irrigation")