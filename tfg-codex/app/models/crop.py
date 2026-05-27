from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    crop_type: Mapped[str | None] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(255))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    copied_from_crop_id: Mapped[int | None] = mapped_column(ForeignKey("crops.id"))

    owner = relationship("User", back_populates="crops")
    copied_from = relationship("Crop", remote_side=[id])
    planting_calendar = relationship(
        "PlantingCalendar", back_populates="crop", uselist=False, cascade="all, delete-orphan"
    )
    irrigation_attributes = relationship(
        "IrrigationAttributes", back_populates="crop", uselist=False, cascade="all, delete-orphan"
    )
    environmental_requirements = relationship(
        "EnvironmentalRequirements", back_populates="crop", uselist=False, cascade="all, delete-orphan"
    )
    cultivation_guide = relationship(
        "CultivationGuide", back_populates="crop", uselist=False, cascade="all, delete-orphan"
    )
    task_links = relationship("TaskCrop", back_populates="crop", cascade="all, delete-orphan")


class IrrigationAttributes(Base):
    __tablename__ = "irrigation_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), unique=True, nullable=False)
    water_needs: Mapped[str | None] = mapped_column(String(120))
    frequency_days: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    watering_frequency: Mapped[str | None] = mapped_column(String(120))
    water_amount: Mapped[str | None] = mapped_column(String(120))
    recommendations: Mapped[str | None] = mapped_column(Text)

    crop = relationship("Crop", back_populates="irrigation_attributes")


class EnvironmentalRequirements(Base):
    __tablename__ = "environmental_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), unique=True, nullable=False)
    climate: Mapped[str | None] = mapped_column(String(120))
    soil_type: Mapped[str | None] = mapped_column(String(120))
    sun_exposure: Mapped[str | None] = mapped_column(String(120))
    min_temperature_c: Mapped[int | None] = mapped_column(Integer)
    max_temperature_c: Mapped[int | None] = mapped_column(Integer)
    frost_tolerance: Mapped[bool | None] = mapped_column(Boolean)

    crop = relationship("Crop", back_populates="environmental_requirements")

    @property
    def min_temp(self) -> int | None:
        return self.min_temperature_c

    @min_temp.setter
    def min_temp(self, value: int | None) -> None:
        self.min_temperature_c = value

    @property
    def max_temp(self) -> int | None:
        return self.max_temperature_c

    @max_temp.setter
    def max_temp(self, value: int | None) -> None:
        self.max_temperature_c = value


class CultivationGuide(Base):
    __tablename__ = "cultivation_guides"

    id: Mapped[int] = mapped_column(primary_key=True)
    crop_id: Mapped[int] = mapped_column(ForeignKey("crops.id"), unique=True, nullable=False)
    preparation: Mapped[str | None] = mapped_column(Text)
    sowing: Mapped[str | None] = mapped_column(Text)
    care: Mapped[str | None] = mapped_column(Text)
    harvest: Mapped[str | None] = mapped_column(Text)

    crop = relationship("Crop", back_populates="cultivation_guide")
