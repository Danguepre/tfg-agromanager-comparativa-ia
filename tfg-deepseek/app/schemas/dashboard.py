"""Schemas Pydantic para Dashboard de usuario."""

from datetime import date, datetime
from pydantic import BaseModel


class CropSummary(BaseModel):
    """Resumen de un cultivo para dashboard."""
    id: int
    name: str
    scientific_name: str | None = None
    category: str | None = None
    is_public: bool
    is_copied: bool = False
    calendar_phase: int | None = None
    calendar_status: str | None = None
    calendar_active: bool | None = None


class TaskSummary(BaseModel):
    """Resumen de una tarea para dashboard."""
    id: int
    title: str
    status: str
    priority: str
    due_date: datetime | None = None
    is_completed: bool


class CalendarEventSummary(BaseModel):
    """Resumen de evento de calendario para dashboard."""
    id: int
    crop_name: str
    crop_id: int
    phase_index: int
    phase_name: str
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool
    status: str


class IrrigationSummary(BaseModel):
    """Resumen de riego para un cultivo."""
    crop_id: int
    crop_name: str
    frequency_days: int | None = None
    water_needed_mm: float | None = None
    irrigation_method: str | None = None


class EnvironmentalSummary(BaseModel):
    """Resumen ambiental para un cultivo."""
    crop_id: int
    crop_name: str
    min_temperature: float | None = None
    max_temperature: float | None = None
    optimal_temperature: float | None = None
    soil_type: str | None = None
    sunlight_hours: int | None = None


class DashboardSummary(BaseModel):
    """Resumen principal del dashboard."""
    total_personal_crops: int
    total_public_crops: int
    tasks_pending: int
    tasks_completed: int
    upcoming_tasks: list[TaskSummary]
    upcoming_calendar_events: list[CalendarEventSummary]
    active_calendars: int
    completed_calendars: int
    irrigation_summary: list[IrrigationSummary]
    environmental_summary: list[EnvironmentalSummary]