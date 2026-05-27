from datetime import date

from pydantic import BaseModel, ConfigDict


class PlantingCalendarBase(BaseModel):
    planting_start: date | None = None
    planting_end: date | None = None
    transplant_start: date | None = None
    transplant_end: date | None = None
    harvest_start: date | None = None
    harvest_end: date | None = None


class PlantingCalendarCreate(PlantingCalendarBase):
    crop_id: int


class PlantingCalendarUpdate(PlantingCalendarBase):
    is_active: bool | None = None
    current_phase_index: int | None = None
    status: str | None = None


class PlantingCalendarRead(PlantingCalendarBase):
    id: int
    crop_id: int
    is_active: bool
    current_phase_index: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class CalendarEvent(BaseModel):
    calendar_id: int
    crop_id: int
    crop_name: str
    phase_index: int
    phase: str
    start_month: int
    start_fortnight: int
    end_month: int
    end_fortnight: int
