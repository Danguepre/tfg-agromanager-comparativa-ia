"""Modelo de Guía de Cultivo."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CultivationGuide(Base):
    """Guía de cultivo detallada para un cultivo."""

    __tablename__ = "cultivation_guides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    crop_id: Mapped[int] = mapped_column(Integer, ForeignKey("crops.id"), unique=True, nullable=False)
    soil_preparation: Mapped[str | None] = mapped_column(Text, nullable=True)
    planting_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    fertilization: Mapped[str | None] = mapped_column(Text, nullable=True)
    pest_management: Mapped[str | None] = mapped_column(Text, nullable=True)
    pruning: Mapped[str | None] = mapped_column(Text, nullable=True)
    harvesting_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    crop = relationship("Crop", back_populates="cultivation_guide")