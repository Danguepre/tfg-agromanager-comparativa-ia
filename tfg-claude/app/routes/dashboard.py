"""
Rutas de dashboard: resúmenes personalizados para el usuario autenticado.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardSummary,
    DashboardCropsResponse,
    DashboardTasksResponse,
    DashboardCalendarResponse,
    DashboardIrrigationResponse,
    DashboardEnvironmentalResponse,
    TaskSummaryInDashboard,
    CalendarPhaseSummaryInDashboard,
    IrrigationSummaryInDashboard,
    EnvironmentalSummaryInDashboard,
    CropBasicInDashboard,
)
from app.services.dashboard_service import (
    get_user_dashboard_summary,
    get_user_dashboard_crops,
    get_user_dashboard_tasks,
    get_user_dashboard_calendars,
    get_user_dashboard_irrigation,
    get_user_dashboard_environmental,
    get_calendar_current_phase,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /dashboard/summary
    Obtiene resumen general del dashboard del usuario autenticado.
    Incluye: totales, tareas próximas, calendarios activos.
    """
    data = get_user_dashboard_summary(db, current_user.id)

    # Convertir tareas a TaskSummaryInDashboard
    upcoming_tasks = [
        TaskSummaryInDashboard(
            id=task.id,
            title=task.title,
            status=task.status.value,
            due_date=task.due_date,
        )
        for task in data["upcoming_tasks"]
    ]

    # Convertir calendarios a CalendarPhaseSummaryInDashboard
    active_calendar_phases = [
        CalendarPhaseSummaryInDashboard(
            calendar_id=cal.id,
            crop_id=cal.crop_id,
            crop_name=cal.crop.name,
            current_phase=get_calendar_current_phase(cal),
            current_phase_index=cal.current_phase_index,
            status=cal.status,
        )
        for cal in data["active_calendars"]
    ]

    return DashboardSummary(
        total_personal_crops=data["total_personal_crops"],
        total_public_crops_available=data["total_public_crops_available"],
        total_tasks_pending=data["total_tasks_pending"],
        total_tasks_completed=data["total_tasks_completed"],
        total_active_calendars=data["total_active_calendars"],
        upcoming_tasks=upcoming_tasks,
        active_calendar_phases=active_calendar_phases,
    )


@router.get("/crops", response_model=DashboardCropsResponse)
def get_dashboard_crops(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /dashboard/crops
    Obtiene lista de cultivos personales del usuario autenticado.
    """
    data = get_user_dashboard_crops(db, current_user.id)

    personal_crops = [
        CropBasicInDashboard(
            id=crop.id,
            name=crop.name,
            crop_type=crop.crop_type,
        )
        for crop in data["personal_crops"]
    ]

    return DashboardCropsResponse(
        personal_crops=personal_crops,
        total_personal=data["total_personal"],
    )


@router.get("/tasks", response_model=DashboardTasksResponse)
def get_dashboard_tasks(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /dashboard/tasks
    Obtiene tareas del usuario autenticado separadas por estado.
    """
    data = get_user_dashboard_tasks(db, current_user.id)

    pending_tasks = [
        TaskSummaryInDashboard(
            id=task.id,
            title=task.title,
            status=task.status.value,
            due_date=task.due_date,
        )
        for task in data["pending_tasks"]
    ]

    completed_tasks = [
        TaskSummaryInDashboard(
            id=task.id,
            title=task.title,
            status=task.status.value,
            due_date=task.due_date,
        )
        for task in data["completed_tasks"]
    ]

    return DashboardTasksResponse(
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        total_pending=data["total_pending"],
        total_completed=data["total_completed"],
    )


@router.get("/calendar", response_model=DashboardCalendarResponse)
def get_dashboard_calendar(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /dashboard/calendar
    Obtiene calendarios activos y completados del usuario autenticado.
    Incluye fase actual de cada calendario.
    """
    data = get_user_dashboard_calendars(db, current_user.id)

    active_calendars = [
        CalendarPhaseSummaryInDashboard(
            calendar_id=cal.id,
            crop_id=cal.crop_id,
            crop_name=cal.crop.name,
            current_phase=get_calendar_current_phase(cal),
            current_phase_index=cal.current_phase_index,
            status=cal.status,
        )
        for cal in data["active_calendars"]
    ]

    completed_calendars = [
        CalendarPhaseSummaryInDashboard(
            calendar_id=cal.id,
            crop_id=cal.crop_id,
            crop_name=cal.crop.name,
            current_phase=get_calendar_current_phase(cal),
            current_phase_index=cal.current_phase_index,
            status=cal.status,
        )
        for cal in data["completed_calendars"]
    ]

    return DashboardCalendarResponse(
        active_calendars=active_calendars,
        completed_calendars=completed_calendars,
    )


@router.get("/irrigation", response_model=DashboardIrrigationResponse)
def get_dashboard_irrigation(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /dashboard/irrigation
    Obtiene resumen de riego para todos los cultivos del usuario autenticado.
    """
    data = get_user_dashboard_irrigation(db, current_user.id)

    irrigation_summaries = [
        IrrigationSummaryInDashboard(
            crop_id=summary["crop_id"],
            crop_name=summary["crop_name"],
            water_frequency_days=summary["water_frequency_days"],
            water_amount_mm=summary["water_amount_mm"],
            irrigation_type=summary["irrigation_type"],
        )
        for summary in data["irrigation_summaries"]
    ]

    return DashboardIrrigationResponse(
        irrigation_summaries=irrigation_summaries,
    )


@router.get("/environmental", response_model=DashboardEnvironmentalResponse)
def get_dashboard_environmental(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /dashboard/environmental
    Obtiene resumen de requisitos ambientales para todos los cultivos del usuario autenticado.
    """
    data = get_user_dashboard_environmental(db, current_user.id)

    environmental_summaries = [
        EnvironmentalSummaryInDashboard(
            crop_id=summary["crop_id"],
            crop_name=summary["crop_name"],
            min_temperature_celsius=summary["min_temperature_celsius"],
            max_temperature_celsius=summary["max_temperature_celsius"],
            min_humidity_percent=summary["min_humidity_percent"],
            max_humidity_percent=summary["max_humidity_percent"],
            sunlight_hours_per_day=summary["sunlight_hours_per_day"],
        )
        for summary in data["environmental_summaries"]
    ]

    return DashboardEnvironmentalResponse(
        environmental_summaries=environmental_summaries,
    )
