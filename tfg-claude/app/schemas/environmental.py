"""
Schemas de requisitos ambientales (Environmental Requirements).
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EnvironmentalBase(BaseModel):
    """Base para requisitos ambientales."""

    min_temperature_celsius: Optional[float] = Field(None, description="Temperatura mínima")
    max_temperature_celsius: Optional[float] = Field(None, description="Temperatura máxima")
    min_humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    max_humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    sunlight_hours_per_day: Optional[float] = Field(None, ge=0, description="Horas de luz solar")
    soil_type: Optional[str] = Field(None, max_length=100)
    soil_ph_min: Optional[float] = Field(None, ge=0, le=14)
    soil_ph_max: Optional[float] = Field(None, ge=0, le=14)


class EnvironmentalCreate(EnvironmentalBase):
    """Creación de requisitos ambientales."""

    pass


class EnvironmentalUpdate(BaseModel):
    """Actualización parcial de requisitos ambientales."""

    min_temperature_celsius: Optional[float] = None
    max_temperature_celsius: Optional[float] = None
    min_humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    max_humidity_percent: Optional[float] = Field(None, ge=0, le=100)
    sunlight_hours_per_day: Optional[float] = Field(None, ge=0)
    soil_type: Optional[str] = Field(None, max_length=100)
    soil_ph_min: Optional[float] = Field(None, ge=0, le=14)
    soil_ph_max: Optional[float] = Field(None, ge=0, le=14)


class EnvironmentalResponse(EnvironmentalBase):
    """Respuesta de requisitos ambientales."""

    id: int
    crop_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
