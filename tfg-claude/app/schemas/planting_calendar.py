"""
Schemas de calendario agrícola.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class PlantingCalendarBase(BaseModel):
    """Base para calendario agrícola."""

    planting_start: Optional[date] = Field(None, description="Fecha inicio siembra (DD-MM)")
    planting_end: Optional[date] = Field(None, description="Fecha fin siembra (DD-MM)")
    transplant_start: Optional[date] = Field(None, description="Fecha inicio trasplante (DD-MM)")
    transplant_end: Optional[date] = Field(None, description="Fecha fin trasplante (DD-MM)")
    harvest_start: Optional[date] = Field(None, description="Fecha inicio cosecha (DD-MM)")
    harvest_end: Optional[date] = Field(None, description="Fecha fin cosecha (DD-MM)")


class PlantingCalendarCreate(PlantingCalendarBase):
    """Creación de calendario agrícola."""

    pass


class PlantingCalendarUpdate(BaseModel):
    """Actualización de calendario agrícola."""

    planting_start: Optional[date] = Field(None)
    planting_end: Optional[date] = Field(None)
    transplant_start: Optional[date] = Field(None)
    transplant_end: Optional[date] = Field(None)
    harvest_start: Optional[date] = Field(None)
    harvest_end: Optional[date] = Field(None)


class PlantingCalendarResponse(PlantingCalendarBase):
    """Respuesta de calendario agrícola."""

    id: int
    crop_id: int
    is_active: bool
    current_phase_index: int  # 0=Siembra, 1=Trasplante, 2=Cosecha
    status: str  # draft, active, completed
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlantingCalendarDetailResponse(PlantingCalendarResponse):
    """Respuesta detallada de calendario con información del cultivo."""

    pass


class CalendarEvent(BaseModel):
    """Evento del calendario (fase actual)."""

    phase_index: int  # 0=Siembra, 1=Trasplante, 2=Cosecha
    phase_name: str  # "Siembra", "Trasplante", "Cosecha"
    start_date: date
    end_date: date
    calendar_id: int
    crop_id: int
    crop_name: str
    is_active: bool


class CalendarEventsResponse(BaseModel):
    """Respuesta de eventos del calendario."""

    total: int
    items: list[CalendarEvent]
