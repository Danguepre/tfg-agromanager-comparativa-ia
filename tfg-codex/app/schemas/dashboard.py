from datetime import datetime

from pydantic import BaseModel


class DashboardCropItem(BaseModel):
    id: int
    name: str
    crop_type: str | None = None
    is_public: bool
    copied_from_crop_id: int | None = None


class DashboardTaskItem(BaseModel):
    id: int
    name: str
    description: str | None = None
    status: str
    created_at: datetime
    crop_ids: list[int]


class DashboardTaskCounts(BaseModel):
    pending: int
    completed: int


class DashboardCalendarEvent(BaseModel):
    calendar_id: int
    crop_id: int
    crop_name: str
    phase_index: int
    phase: str
    start_month: int
    start_fortnight: int
    end_month: int
    end_fortnight: int


class DashboardCalendarPhase(BaseModel):
    calendar_id: int
    crop_id: int
    crop_name: str
    phase_index: int
    phase: str
    status: str


class DashboardIrrigationItem(BaseModel):
    crop_id: int
    crop_name: str
    irrigation_id: int | None = None
    watering_frequency: str | None = None
    water_amount: str | None = None
    recommendations: str | None = None


class DashboardEnvironmentalItem(BaseModel):
    crop_id: int
    crop_name: str
    environmental_id: int | None = None
    sun_exposure: str | None = None
    min_temp: int | None = None
    max_temp: int | None = None
    frost_tolerance: bool | None = None


class DashboardSummary(BaseModel):
    total_personal_crops: int
    total_public_crops: int
    total_copied_crops: int
    tasks_by_status: DashboardTaskCounts
    upcoming_pending_tasks: list[DashboardTaskItem]
    active_calendars_total: int
    upcoming_calendar_events: list[DashboardCalendarEvent]
    current_calendar_phases: list[DashboardCalendarPhase]
    irrigation_summary: list[DashboardIrrigationItem]
    environmental_summary: list[DashboardEnvironmentalItem]
