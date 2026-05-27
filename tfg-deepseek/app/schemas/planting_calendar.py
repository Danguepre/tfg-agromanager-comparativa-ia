"""Schemas Pydantic para Calendario Agrícola por Fases (FASE 5)."""

from datetime import date, datetime

from pydantic import BaseModel


class PlantingCalendarCreate(BaseModel):
    """Schema para creación de calendario agrícola."""
    crop_id: int
    planting_start: date | None = None
    planting_end: date | None = None
    transplant_start: date | None = None
    transplant_end: date | None = None
    harvest_start: date | None = None
    harvest_end: date | None = None
    notes: str | None = None


class PlantingCalendarUpdate(BaseModel):
    """Schema para actualización de calendario agrícola."""
    planting_start: date | None = None
    planting_end: date | None = None
    transplant_start: date | None = None
    transplant_end: date | None = None
    harvest_start: date | None = None
    harvest_end: date | None = None
    notes: str | None = None


class PlantingCalendarRead(BaseModel):
    """Schema para respuesta de calendario agrícola."""
    id: int
    crop_id: int
    planting_start: date | None = None
    planting_end: date | None = None
    transplant_start: date | None = None
    transplant_end: date | None = None
    harvest_start: date | None = None
    harvest_end: date | None = None
    is_active: bool = False
    current_phase_index: int = 0
    status: str = "draft"
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CalendarEvent(BaseModel):
    """Evento de calendario calculado por mes/quincena, ignorando el año."""
    month: int
    fortnight: int  # 1 = primera quincena, 2 = segunda quincena
    phase: str
    phase_index: int
    label: str