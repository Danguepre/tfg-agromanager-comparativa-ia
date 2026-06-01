"""Schemas Pydantic para Guía de Cultivo."""

from datetime import datetime

from pydantic import BaseModel


class CultivationGuideCreate(BaseModel):
    crop_id: int
    soil_preparation: str | None = None
    planting_instructions: str | None = None
    fertilization: str | None = None
    pest_management: str | None = None
    pruning: str | None = None
    harvesting_instructions: str | None = None
    storage: str | None = None
    notes: str | None = None


class CultivationGuideUpdate(BaseModel):
    soil_preparation: str | None = None
    planting_instructions: str | None = None
    fertilization: str | None = None
    pest_management: str | None = None
    pruning: str | None = None
    harvesting_instructions: str | None = None
    storage: str | None = None
    notes: str | None = None


class CultivationGuideRead(BaseModel):
    id: int
    crop_id: int
    soil_preparation: str | None = None
    planting_instructions: str | None = None
    fertilization: str | None = None
    pest_management: str | None = None
    pruning: str | None = None
    harvesting_instructions: str | None = None
    storage: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}