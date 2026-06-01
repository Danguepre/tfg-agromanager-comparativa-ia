"""
Schemas de cultivo.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CropBase(BaseModel):
    """Base para cultivo."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    crop_type: Optional[str] = Field(None, max_length=100)


class CropCreate(CropBase):
    """Creación de cultivo (multipart, sin imagen en schema)."""

    is_public: bool = False


class CropUpdate(BaseModel):
    """Actualización de cultivo."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    crop_type: Optional[str] = Field(None, max_length=100)


class IrrigationAttributesResponse(BaseModel):
    """Riego."""

    id: int
    water_frequency_days: Optional[int] = None
    water_amount_mm: Optional[float] = None
    irrigation_type: Optional[str] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class EnvironmentalRequirementsResponse(BaseModel):
    """Requisitos ambientales."""

    id: int
    min_temperature_celsius: Optional[float] = None
    max_temperature_celsius: Optional[float] = None
    min_humidity_percent: Optional[float] = None
    max_humidity_percent: Optional[float] = None
    sunlight_hours_per_day: Optional[float] = None
    soil_type: Optional[str] = None
    soil_ph_min: Optional[float] = None
    soil_ph_max: Optional[float] = None

    model_config = {"from_attributes": True}


class UserBasicResponse(BaseModel):
    """Respuesta básica de usuario (para no exponer todo)."""

    id: int
    email: str
    name: str

    model_config = {"from_attributes": True}


class CropResponse(CropBase):
    """Respuesta de cultivo."""

    id: int
    owner_id: Optional[int] = None
    is_public: bool
    source_crop_id: Optional[int] = None
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CropDetailResponse(CropResponse):
    """Respuesta detallada de cultivo con relaciones."""

    owner: Optional[UserBasicResponse] = None
    irrigation: Optional[IrrigationAttributesResponse] = None
    environmental: Optional[EnvironmentalRequirementsResponse] = None

    model_config = {"from_attributes": True}


class CropListResponse(BaseModel):
    """Paginación de cultivos."""

    total: int
    skip: int
    limit: int
    items: list[CropResponse]
