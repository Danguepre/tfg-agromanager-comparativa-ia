from pydantic import BaseModel
from datetime import date
from typing import Optional

class PlantingCalendarBase(BaseModel):
    planting_start: Optional[date] = None
    planting_end: Optional[date] = None
    transplant_start: Optional[date] = None
    transplant_end: Optional[date] = None
    harvest_start: Optional[date] = None
    harvest_end: Optional[date] = None

class PlantingCalendarCreate(PlantingCalendarBase):
    crop_id: int

class PlantingCalendarResponse(PlantingCalendarBase):
    id: int
    crop_id: int
    is_active: bool = False
    current_phase_index: int = 0
    status: str = "draft"

    class Config:
        from_attributes = True

class PlantingEvent(BaseModel):
    title: str
    month: int
    half: int
    crop_id: int | None = None
    crop_name: str | None = None
    phase: str | None = None
    phase_index: int | None = None
    is_last_phase: bool = False
