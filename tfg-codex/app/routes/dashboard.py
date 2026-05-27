from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.crop import Crop
from app.models.planting_calendar import PlantingCalendar
from app.models.task import Task
from app.models.user import User
from app.schemas.dashboard import (
    DashboardCalendarEvent,
    DashboardCalendarPhase,
    DashboardCropItem,
    DashboardEnvironmentalItem,
    DashboardIrrigationItem,
    DashboardSummary,
    DashboardTaskCounts,
    DashboardTaskItem,
)


router = APIRouter(prefix="/dashboard", tags=["dashboard"])

PHASES = (
    ("Siembra", "planting_start", "planting_end"),
    ("Trasplante", "transplant_start", "transplant_end"),
    ("Cosecha", "harvest_start", "harvest_end"),
)


def _fortnight(day: int) -> int:
    return 1 if day <= 15 else 2


def _owned_crops_query(db: Session, user: User):
    return db.query(Crop).filter(Crop.owner_id == user.id)


def _task_item(task: Task) -> DashboardTaskItem:
    return DashboardTaskItem(
        id=task.id,
        name=task.name,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        crop_ids=[link.crop_id for link in task.crop_links],
    )


def _calendar_event(calendar: PlantingCalendar) -> DashboardCalendarEvent | None:
    if calendar.current_phase_index < 0 or calendar.current_phase_index >= len(PHASES):
        return None
    phase, start_attr, end_attr = PHASES[calendar.current_phase_index]
    start = getattr(calendar, start_attr)
    end = getattr(calendar, end_attr)
    if start is None or end is None:
        return None
    return DashboardCalendarEvent(
        calendar_id=calendar.id,
        crop_id=calendar.crop_id,
        crop_name=calendar.crop.name,
        phase_index=calendar.current_phase_index,
        phase=phase,
        start_month=start.month,
        start_fortnight=_fortnight(start.day),
        end_month=end.month,
        end_fortnight=_fortnight(end.day),
    )


def _calendar_phase(calendar: PlantingCalendar) -> DashboardCalendarPhase:
    phase = PHASES[calendar.current_phase_index][0] if 0 <= calendar.current_phase_index < len(PHASES) else "Desconocida"
    return DashboardCalendarPhase(
        calendar_id=calendar.id,
        crop_id=calendar.crop_id,
        crop_name=calendar.crop.name,
        phase_index=calendar.current_phase_index,
        phase=phase,
        status=calendar.status,
    )


def _crop_item(crop: Crop) -> DashboardCropItem:
    return DashboardCropItem(
        id=crop.id,
        name=crop.name,
        crop_type=crop.crop_type,
        is_public=crop.is_public,
        copied_from_crop_id=crop.copied_from_crop_id,
    )


def _irrigation_item(crop: Crop) -> DashboardIrrigationItem:
    irrigation = crop.irrigation_attributes
    return DashboardIrrigationItem(
        crop_id=crop.id,
        crop_name=crop.name,
        irrigation_id=irrigation.id if irrigation else None,
        watering_frequency=irrigation.watering_frequency if irrigation else None,
        water_amount=irrigation.water_amount if irrigation else None,
        recommendations=irrigation.recommendations if irrigation else None,
    )


def _environmental_item(crop: Crop) -> DashboardEnvironmentalItem:
    environmental = crop.environmental_requirements
    return DashboardEnvironmentalItem(
        crop_id=crop.id,
        crop_name=crop.name,
        environmental_id=environmental.id if environmental else None,
        sun_exposure=environmental.sun_exposure if environmental else None,
        min_temp=environmental.min_temperature_c if environmental else None,
        max_temp=environmental.max_temperature_c if environmental else None,
        frost_tolerance=environmental.frost_tolerance if environmental else None,
    )


def _active_calendars(db: Session, user: User) -> list[PlantingCalendar]:
    return (
        db.query(PlantingCalendar)
        .join(Crop)
        .filter(Crop.owner_id == user.id, PlantingCalendar.is_active.is_(True))
        .order_by(PlantingCalendar.id)
        .all()
    )


@router.get("/crops", response_model=list[DashboardCropItem])
def dashboard_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DashboardCropItem]:
    return [_crop_item(crop) for crop in _owned_crops_query(db, current_user).order_by(Crop.id).all()]


@router.get("/tasks", response_model=list[DashboardTaskItem])
def dashboard_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DashboardTaskItem]:
    tasks = db.query(Task).filter(Task.user_id == current_user.id).order_by(Task.created_at, Task.id).all()
    return [_task_item(task) for task in tasks]


@router.get("/calendar", response_model=list[DashboardCalendarPhase])
def dashboard_calendar(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DashboardCalendarPhase]:
    return [_calendar_phase(calendar) for calendar in _active_calendars(db, current_user)]


@router.get("/irrigation", response_model=list[DashboardIrrigationItem])
def dashboard_irrigation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DashboardIrrigationItem]:
    crops = _owned_crops_query(db, current_user).order_by(Crop.id).all()
    return [_irrigation_item(crop) for crop in crops]


@router.get("/environmental", response_model=list[DashboardEnvironmentalItem])
def dashboard_environmental(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DashboardEnvironmentalItem]:
    crops = _owned_crops_query(db, current_user).order_by(Crop.id).all()
    return [_environmental_item(crop) for crop in crops]


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummary:
    owned_crops = _owned_crops_query(db, current_user).order_by(Crop.id).all()
    pending_tasks = (
        db.query(Task)
        .filter(Task.user_id == current_user.id, Task.status == "pending")
        .order_by(Task.created_at, Task.id)
        .all()
    )
    completed_tasks_count = db.query(Task).filter(Task.user_id == current_user.id, Task.status == "completed").count()
    active_calendars = _active_calendars(db, current_user)
    events = [event for calendar in active_calendars if (event := _calendar_event(calendar)) is not None]

    return DashboardSummary(
        total_personal_crops=len(owned_crops),
        total_public_crops=sum(1 for crop in owned_crops if crop.is_public),
        total_copied_crops=sum(1 for crop in owned_crops if crop.copied_from_crop_id is not None),
        tasks_by_status=DashboardTaskCounts(pending=len(pending_tasks), completed=completed_tasks_count),
        upcoming_pending_tasks=[_task_item(task) for task in pending_tasks[:5]],
        active_calendars_total=len(active_calendars),
        upcoming_calendar_events=events,
        current_calendar_phases=[_calendar_phase(calendar) for calendar in active_calendars],
        irrigation_summary=[_irrigation_item(crop) for crop in owned_crops],
        environmental_summary=[_environmental_item(crop) for crop in owned_crops],
    )
