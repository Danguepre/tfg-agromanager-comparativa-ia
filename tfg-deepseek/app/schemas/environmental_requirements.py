"""Schemas Pydantic para Requisitos Ambientales."""

from datetime import datetime

from pydantic import BaseModel


class EnvironmentalRequirementsCreate(BaseModel):
    crop_id: int
    min_temperature: float | None = None
    max_temperature: float | None = None
    optimal_temperature: float | None = None
    min_ph: float | None = None
    max_ph: float | None = None
    optimal_ph: float | None = None
    soil_type: str | None = None
    sunlight_hours: int | None = None
    humidity_percent: float | None = None
    hardiness_zone: str | None = None
    notes: str | None = None


class EnvironmentalRequirementsUpdate(BaseModel):
    min_temperature: float | None = None
    max_temperature: float | None = None
    optimal_temperature: float | None = None
    min_ph: float | None = None
    max_ph: float | None = None
    optimal_ph: float | None = None
    soil_type: str | None = None
    sunlight_hours: int | None = None
    humidity_percent: float | None = None
    hardiness_zone: str | None = None
    notes: str | None = None


class EnvironmentalRequirementsRead(BaseModel):
    id: int
    crop_id: int
    min_temperature: float | None = None
    max_temperature: float | None = None
    optimal_temperature: float | None = None
    min_ph: float | None = None
    max_ph: float | None = None
    optimal_ph: float | None = None
    soil_type: str | None = None
    sunlight_hours: int | None = None
    humidity_percent: float | None = None
    hardiness_zone: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}