"""Rutas de dashboard de usuario (FASE 7)."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.crop import Crop
from app.models.task import Task
from app.models.planting_calendar import PlantingCalendar
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.environmental_requirements import EnvironmentalRequirements
from app.schemas.dashboard import (
    DashboardSummary,
    TaskSummary,
    CalendarEventSummary,
    IrrigationSummary,
    EnvironmentalSummary,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

PHASE_NAMES = ["Siembra", "Trasplante", "Cosecha"]


def _get_upcoming_tasks(user_id: int, db: Session, limit: int = 10) -> list[TaskSummary]:
    """Obtiene las próximas tareas pendientes del usuario."""
    now = datetime.now(timezone.utc)
    tasks = (
        db.query(Task)
        .filter(Task.owner_id == user_id, Task.is_completed == False)  # noqa: E712
        .order_by(Task.due_date.asc().nulls_last())
        .limit(limit)
        .all()
    )
    return [
        TaskSummary(
            id=t.id,
            title=t.title,
            status=t.status,
            priority=t.priority,
            due_date=t.due_date,
            is_completed=t.is_completed,
        )
        for t in tasks
    ]


def _get_calendar_events(user_id: int, db: Session) -> list[CalendarEventSummary]:
    """Obtiene los eventos activos del calendario para cultivos del usuario."""
    events = (
        db.query(PlantingCalendar)
        .join(Crop, PlantingCalendar.crop_id == Crop.id)
        .filter(
            Crop.owner_id == user_id,
            PlantingCalendar.is_active == True,  # noqa: E712
        )
        .all()
    )
    result = []
    for cal in events:
        phase_name = PHASE_NAMES[cal.current_phase_index] if cal.current_phase_index < len(PHASE_NAMES) else "Desconocida"
        # Determine start/end date based on current phase
        start_date = None
        end_date = None
        if cal.current_phase_index == 0:
            start_date = cal.planting_start
            end_date = cal.planting_end
        elif cal.current_phase_index == 1:
            start_date = cal.transplant_start
            end_date = cal.transplant_end
        elif cal.current_phase_index == 2:
            start_date = cal.harvest_start
            end_date = cal.harvest_end

        result.append(
            CalendarEventSummary(
                id=cal.id,
                crop_name=cal.crop.name,
                crop_id=cal.crop_id,
                phase_index=cal.current_phase_index,
                phase_name=phase_name,
                start_date=start_date,
                end_date=end_date,
                is_active=cal.is_active,
                status=cal.status,
            )
        )
    return result


def _get_irrigation_summary(user_id: int, db: Session) -> list[IrrigationSummary]:
    """Obtiene resumen de riego para cultivos del usuario."""
    records = (
        db.query(IrrigationAttributes)
        .join(Crop, IrrigationAttributes.crop_id == Crop.id)
        .filter(Crop.owner_id == user_id)
        .all()
    )
    return [
        IrrigationSummary(
            crop_id=r.crop_id,
            crop_name=r.crop.name,
            frequency_days=r.frequency_days,
            water_needed_mm=r.water_needed_mm,
            irrigation_method=r.irrigation_method,
        )
        for r in records
    ]


def _get_environmental_summary(user_id: int, db: Session) -> list[EnvironmentalSummary]:
    """Obtiene resumen ambiental para cultivos del usuario."""
    records = (
        db.query(EnvironmentalRequirements)
        .join(Crop, EnvironmentalRequirements.crop_id == Crop.id)
        .filter(Crop.owner_id == user_id)
        .all()
    )
    return [
        EnvironmentalSummary(
            crop_id=r.crop_id,
            crop_name=r.crop.name,
            min_temperature=r.min_temperature,
            max_temperature=r.max_temperature,
            optimal_temperature=r.optimal_temperature,
            soil_type=r.soil_type,
            sunlight_hours=r.sunlight_hours,
        )
        for r in records
    ]


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene resumen completo del dashboard para el usuario autenticado."""
    user_id = current_user.id

    # Total de cultivos personales (propietario)
    total_personal_crops = db.query(Crop).filter(Crop.owner_id == user_id).count()

    # Total de cultivos públicos (no propietario, que puede ver)
    total_public_crops = db.query(Crop).filter(
        Crop.is_public == True,  # noqa: E712
        (Crop.owner_id != user_id) | (Crop.owner_id.is_(None)),
    ).count()

    # Tareas por estado
    tasks_pending = db.query(Task).filter(
        Task.owner_id == user_id,
        Task.is_completed == False,  # noqa: E712
    ).count()
    tasks_completed = db.query(Task).filter(
        Task.owner_id == user_id,
        Task.is_completed == True,  # noqa: E712
    ).count()

    # Calendarios activos/completados para cultivos del usuario
    active_calendars = db.query(PlantingCalendar).join(
        Crop, PlantingCalendar.crop_id == Crop.id
    ).filter(
        Crop.owner_id == user_id,
        PlantingCalendar.status == "active",
    ).count()
    completed_calendars = db.query(PlantingCalendar).join(
        Crop, PlantingCalendar.crop_id == Crop.id
    ).filter(
        Crop.owner_id == user_id,
        PlantingCalendar.status == "completed",
    ).count()

    upcoming_tasks = _get_upcoming_tasks(user_id, db)
    calendar_events = _get_calendar_events(user_id, db)
    irrigation_summary = _get_irrigation_summary(user_id, db)
    environmental_summary = _get_environmental_summary(user_id, db)

    return DashboardSummary(
        total_personal_crops=total_personal_crops,
        total_public_crops=total_public_crops,
        tasks_pending=tasks_pending,
        tasks_completed=tasks_completed,
        upcoming_tasks=upcoming_tasks,
        upcoming_calendar_events=calendar_events,
        active_calendars=active_calendars,
        completed_calendars=completed_calendars,
        irrigation_summary=irrigation_summary,
        environmental_summary=environmental_summary,
    )


@router.get("/crops")
def get_dashboard_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene lista de cultivos del usuario para dashboard."""
    user_id = current_user.id
    crops = db.query(Crop).filter(Crop.owner_id == user_id).all()
    result = []
    for c in crops:
        cal = db.query(PlantingCalendar).filter(PlantingCalendar.crop_id == c.id).first()
        result.append({
            "id": c.id,
            "name": c.name,
            "scientific_name": c.scientific_name,
            "category": c.category,
            "is_public": c.is_public,
            "is_copied": c.copied_from_id is not None,
            "calendar_phase": cal.current_phase_index if cal else None,
            "calendar_status": cal.status if cal else None,
            "calendar_active": cal.is_active if cal else None,
        })
    return result


@router.get("/tasks")
def get_dashboard_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene tareas del usuario para dashboard."""
    user_id = current_user.id
    tasks = db.query(Task).filter(Task.owner_id == user_id).order_by(
        Task.is_completed.asc(),
        Task.due_date.asc().nulls_last(),
    ).all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "priority": t.priority,
            "due_date": t.due_date,
            "is_completed": t.is_completed,
        }
        for t in tasks
    ]


@router.get("/calendar")
def get_dashboard_calendar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene eventos de calendario del usuario para dashboard."""
    return _get_calendar_events(current_user.id, db)


@router.get("/irrigation")
def get_dashboard_irrigation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene resumen de riego del usuario para dashboard."""
    return _get_irrigation_summary(current_user.id, db)


@router.get("/environmental")
def get_dashboard_environmental(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene resumen ambiental del usuario para dashboard."""
    return _get_environmental_summary(current_user.id, db)