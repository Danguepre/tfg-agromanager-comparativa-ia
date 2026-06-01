"""Modelo de Cultivo."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Crop(Base):
    """Cultivo agrícola. Puede ser público, tener propietario o ser copia de otro."""

    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    scientific_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    owner_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    copied_from_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("crops.id"), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner = relationship("User", back_populates="crops", foreign_keys=[owner_id])
    planting_calendar = relationship("PlantingCalendar", back_populates="crop", uselist=False)
    irrigation = relationship("IrrigationAttributes", back_populates="crop", uselist=False)
    environmental = relationship("EnvironmentalRequirements", back_populates="crop", uselist=False)
    cultivation_guide = relationship("CultivationGuide", back_populates="crop", uselist=False)
    task_crops = relationship("TaskCrop", back_populates="crop")