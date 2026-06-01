from pydantic import BaseModel


class DashboardTaskSummary(BaseModel):
    id: int
    name: str
    description: str | None = None
    status: str
    crop_id: int | None = None


class DashboardCalendarSummary(BaseModel):
    crop_id: int
    crop_name: str
    phase: str
    month: int
    half: int
    is_last_phase: bool = False


class DashboardCropWarning(BaseModel):
    crop_id: int
    crop_name: str
    reason: str


class DashboardSummaryResponse(BaseModel):
    crops_count: int
    active_calendar_count: int
    pending_tasks_count: int
    overdue_tasks_count: int
    incomplete_phase_crops_count: int
    pending_tasks: list[DashboardTaskSummary]
    active_calendars: list[DashboardCalendarSummary]
    warnings: list[DashboardCropWarning]
