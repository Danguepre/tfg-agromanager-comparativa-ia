from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PlantingCalendar(Base):
    __tablename__ = "planting_calendars"

    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), unique=True, nullable=False)
    planting_start: Mapped[date | None] = mapped_column(Date)
    planting_end: Mapped[date | None] = mapped_column(Date)
    transplant_start: Mapped[date | None] = mapped_column(Date)
    transplant_end: Mapped[date | None] = mapped_column(Date)
    harvest_start: Mapped[date | None] = mapped_column(Date)
    harvest_end: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    current_phase_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="draft", nullable=False)

    crop = relationship("Crop", back_populates="planting_calendar")
