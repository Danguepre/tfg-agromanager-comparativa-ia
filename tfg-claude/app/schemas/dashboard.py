"""
Schemas para dashboard de usuario.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskSummaryInDashboard(BaseModel):
    """Resumen de tarea en dashboard."""

    id: int
    title: str
    status: str
    due_date: Optional[str] = None

    model_config = {"from_attributes": True}


class CropBasicInDashboard(BaseModel):
    """Cultivo básico en dashboard."""

    id: int
    name: str
    crop_type: Optional[str] = None

    model_config = {"from_attributes": True}


class IrrigationSummaryInDashboard(BaseModel):
    """Resumen de riego en dashboard."""

    crop_id: int
    crop_name: str
    water_frequency_days: Optional[int] = None
    water_amount_mm: Optional[float] = None
    irrigation_type: Optional[str] = None


class EnvironmentalSummaryInDashboard(BaseModel):
    """Resumen ambiental en dashboard."""

    crop_id: int
    crop_name: str
    min_temperature_celsius: Optional[float] = None
    max_temperature_celsius: Optional[float] = None
    min_humidity_percent: Optional[float] = None
    max_humidity_percent: Optional[float] = None
    sunlight_hours_per_day: Optional[float] = None


class CalendarPhaseSummaryInDashboard(BaseModel):
    """Resumen de fase del calendario en dashboard."""

    calendar_id: int
    crop_id: int
    crop_name: str
    current_phase: str  # "planting", "transplant", "harvest" o "unknown"
    current_phase_index: int
    status: str  # draft, active, completed


class DashboardSummary(BaseModel):
    """Resumen general del dashboard del usuario."""

    total_personal_crops: int
    total_public_crops_available: int
    total_tasks_pending: int
    total_tasks_completed: int
    total_active_calendars: int
    upcoming_tasks: list[TaskSummaryInDashboard]
    active_calendar_phases: list[CalendarPhaseSummaryInDashboard]


class DashboardCropsResponse(BaseModel):
    """Respuesta de cultivos en dashboard."""

    personal_crops: list[CropBasicInDashboard]
    total_personal: int


class DashboardTasksResponse(BaseModel):
    """Respuesta de tareas en dashboard."""

    pending_tasks: list[TaskSummaryInDashboard]
    completed_tasks: list[TaskSummaryInDashboard]
    total_pending: int
    total_completed: int


class DashboardCalendarResponse(BaseModel):
    """Respuesta de calendarios en dashboard."""

    active_calendars: list[CalendarPhaseSummaryInDashboard]
    completed_calendars: list[CalendarPhaseSummaryInDashboard]


class DashboardIrrigationResponse(BaseModel):
    """Respuesta de riego en dashboard."""

    irrigation_summaries: list[IrrigationSummaryInDashboard]


class DashboardEnvironmentalResponse(BaseModel):
    """Respuesta de requisitos ambientales en dashboard."""

    environmental_summaries: list[EnvironmentalSummaryInDashboard]
