"""
Schemas de riego (Irrigation).
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class IrrigationBase(BaseModel):
    """Base para riego."""

    water_frequency_days: Optional[int] = Field(None, ge=1, description="Días entre riegos")
    water_amount_mm: Optional[float] = Field(None, ge=0, description="Milímetros de agua")
    irrigation_type: Optional[str] = Field(None, max_length=100, description="Tipo de riego")
    notes: Optional[str] = Field(None, max_length=500)


class IrrigationCreate(IrrigationBase):
    """Creación de riego."""

    pass


class IrrigationUpdate(BaseModel):
    """Actualización parcial de riego."""

    water_frequency_days: Optional[int] = Field(None, ge=1)
    water_amount_mm: Optional[float] = Field(None, ge=0)
    irrigation_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class IrrigationResponse(IrrigationBase):
    """Respuesta de riego."""

    id: int
    crop_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
