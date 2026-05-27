"""
Servicios para dashboard de usuario.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.user import User
from app.models.crop import Crop
from app.models.task import Task, TaskStatus
from app.models.planting_calendar import PlantingCalendar, CalendarStatus
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.environmental_requirements import EnvironmentalRequirements


def get_user_dashboard_summary(db: Session, user_id: int) -> dict:
    """
    Obtener resumen del dashboard del usuario.
    Incluye totales y resúmenes agregados.
    """
    # Total de cultivos personales
    personal_crops_count = db.query(Crop).filter(Crop.owner_id == user_id).count()

    # Total de cultivos públicos disponibles
    public_crops_count = db.query(Crop).filter(Crop.is_public == True).count()  # noqa: E712

    # Total de tareas pending y completed
    pending_tasks = db.query(Task).filter(
        Task.owner_id == user_id,
        Task.status == TaskStatus.PENDING
    ).all()
    pending_count = len(pending_tasks)

    completed_count = db.query(Task).filter(
        Task.owner_id == user_id,
        Task.status == TaskStatus.COMPLETED
    ).count()

    # Próximas tareas pendientes (hasta 5)
    upcoming_tasks = db.query(Task).filter(
        Task.owner_id == user_id,
        Task.status == TaskStatus.PENDING
    ).order_by(Task.due_date).limit(5).all()

    # Calendarios activos
    active_calendars = db.query(PlantingCalendar).join(Crop).filter(
        Crop.owner_id == user_id,
        PlantingCalendar.status == CalendarStatus.ACTIVE
    ).all()

    return {
        "total_personal_crops": personal_crops_count,
        "total_public_crops_available": public_crops_count,
        "total_tasks_pending": pending_count,
        "total_tasks_completed": completed_count,
        "total_active_calendars": len(active_calendars),
        "upcoming_tasks": upcoming_tasks,
        "active_calendars": active_calendars,
    }


def get_user_dashboard_crops(db: Session, user_id: int) -> dict:
    """
    Obtener cultivos del dashboard del usuario.
    """
    crops = db.query(Crop).filter(Crop.owner_id == user_id).all()
    return {
        "personal_crops": crops,
        "total_personal": len(crops),
    }


def get_user_dashboard_tasks(db: Session, user_id: int) -> dict:
    """
    Obtener tareas del dashboard del usuario separadas por estado.
    """
    pending_tasks = db.query(Task).filter(
        Task.owner_id == user_id,
        Task.status == TaskStatus.PENDING
    ).all()

    completed_tasks = db.query(Task).filter(
        Task.owner_id == user_id,
        Task.status == TaskStatus.COMPLETED
    ).all()

    return {
        "pending_tasks": pending_tasks,
        "completed_tasks": completed_tasks,
        "total_pending": len(pending_tasks),
        "total_completed": len(completed_tasks),
    }


def get_user_dashboard_calendars(db: Session, user_id: int) -> dict:
    """
    Obtener calendarios activos y completados del usuario.
    Incluye fase actual de cada calendario.
    """
    active_calendars = db.query(PlantingCalendar).join(Crop).filter(
        Crop.owner_id == user_id,
        PlantingCalendar.status == CalendarStatus.ACTIVE
    ).all()

    completed_calendars = db.query(PlantingCalendar).join(Crop).filter(
        Crop.owner_id == user_id,
        PlantingCalendar.status == CalendarStatus.COMPLETED
    ).all()

    return {
        "active_calendars": active_calendars,
        "completed_calendars": completed_calendars,
    }


def get_user_dashboard_irrigation(db: Session, user_id: int) -> dict:
    """
    Obtener resumen de riego para todos los cultivos del usuario.
    """
    crops = db.query(Crop).filter(Crop.owner_id == user_id).all()
    irrigation_summaries = []

    for crop in crops:
        irrigation = db.query(IrrigationAttributes).filter(
            IrrigationAttributes.crop_id == crop.id
        ).first()

        if irrigation:
            irrigation_summaries.append({
                "crop_id": crop.id,
                "crop_name": crop.name,
                "water_frequency_days": irrigation.water_frequency_days,
                "water_amount_mm": irrigation.water_amount_mm,
                "irrigation_type": irrigation.irrigation_type,
            })

    return {
        "irrigation_summaries": irrigation_summaries,
    }


def get_user_dashboard_environmental(db: Session, user_id: int) -> dict:
    """
    Obtener resumen de requisitos ambientales para todos los cultivos del usuario.
    """
    crops = db.query(Crop).filter(Crop.owner_id == user_id).all()
    environmental_summaries = []

    for crop in crops:
        environmental = db.query(EnvironmentalRequirements).filter(
            EnvironmentalRequirements.crop_id == crop.id
        ).first()

        if environmental:
            environmental_summaries.append({
                "crop_id": crop.id,
                "crop_name": crop.name,
                "min_temperature_celsius": environmental.min_temperature_celsius,
                "max_temperature_celsius": environmental.max_temperature_celsius,
                "min_humidity_percent": environmental.min_humidity_percent,
                "max_humidity_percent": environmental.max_humidity_percent,
                "sunlight_hours_per_day": environmental.sunlight_hours_per_day,
            })

    return {
        "environmental_summaries": environmental_summaries,
    }


def get_calendar_current_phase(calendar: PlantingCalendar) -> str:
    """
    Obtener nombre de la fase actual del calendario.
    """
    phases = ["planting", "transplant", "harvest"]
    if calendar.current_phase_index < len(phases):
        return phases[calendar.current_phase_index]
    return "unknown"
