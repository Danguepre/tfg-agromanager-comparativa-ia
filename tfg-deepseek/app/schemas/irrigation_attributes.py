"""Schemas Pydantic para Atributos de Riego."""

from datetime import datetime

from pydantic import BaseModel


class IrrigationAttributesCreate(BaseModel):
    crop_id: int
    frequency_days: int | None = None
    water_needed_mm: float | None = None
    irrigation_method: str | None = None
    notes: str | None = None


class IrrigationAttributesUpdate(BaseModel):
    frequency_days: int | None = None
    water_needed_mm: float | None = None
    irrigation_method: str | None = None
    notes: str | None = None


class IrrigationAttributesRead(BaseModel):
    id: int
    crop_id: int
    frequency_days: int | None = None
    water_needed_mm: float | None = None
    irrigation_method: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}