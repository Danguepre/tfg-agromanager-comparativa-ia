from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.crop import Crop
from app.models.planting_calendar import PlantingCalendar
from app.models.user import User
from app.schemas.calendar import (
    CalendarEvent,
    PlantingCalendarCreate,
    PlantingCalendarRead,
    PlantingCalendarUpdate,
)


router = APIRouter(prefix="/calendar", tags=["calendar"])

PHASES = (
    ("Siembra", "planting_start", "planting_end"),
    ("Trasplante", "transplant_start", "transplant_end"),
    ("Cosecha", "harvest_start", "harvest_end"),
)


def _is_admin(user: User) -> bool:
    return user.role == "admin"


def _get_crop_or_404(db: Session, crop_id: int) -> Crop:
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    return crop


def _get_calendar_or_404(db: Session, calendar_id: int) -> PlantingCalendar:
    calendar = db.get(PlantingCalendar, calendar_id)
    if calendar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")
    return calendar


def _ensure_can_manage_crop(user: User, crop: Crop) -> None:
    if not _is_admin(user) and crop.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def _ensure_can_manage_calendar(user: User, calendar: PlantingCalendar) -> None:
    _ensure_can_manage_crop(user, calendar.crop)


def _calendar_is_complete(calendar: PlantingCalendar) -> bool:
    required_dates = (
        calendar.planting_start,
        calendar.planting_end,
        calendar.transplant_start,
        calendar.transplant_end,
        calendar.harvest_start,
        calendar.harvest_end,
    )
    return all(required_dates)


def _apply_calendar_update(calendar: PlantingCalendar, payload: PlantingCalendarUpdate) -> None:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in {"current_phase_index", "status", "is_active"} and value is None:
            continue
        setattr(calendar, field, value)

    if calendar.current_phase_index < 0 or calendar.current_phase_index > 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phase index")
    if calendar.is_active and not _calendar_is_complete(calendar):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Calendar dates are incomplete")


def _fortnight(value: date) -> int:
    return 1 if value.day <= 15 else 2


def _event_for_phase(calendar: PlantingCalendar, phase_index: int) -> CalendarEvent | None:
    phase, start_attr, end_attr = PHASES[phase_index]
    start = getattr(calendar, start_attr)
    end = getattr(calendar, end_attr)
    if start is None or end is None:
        return None

    return CalendarEvent(
        calendar_id=calendar.id,
        crop_id=calendar.crop_id,
        crop_name=calendar.crop.name,
        phase_index=phase_index,
        phase=phase,
        start_month=start.month,
        start_fortnight=_fortnight(start),
        end_month=end.month,
        end_fortnight=_fortnight(end),
    )


def _current_phase_events(calendar: PlantingCalendar) -> list[CalendarEvent]:
    if calendar.current_phase_index < 0 or calendar.current_phase_index >= len(PHASES):
        return []
    event = _event_for_phase(calendar, calendar.current_phase_index)
    return [event] if event else []


def _get_calendar_by_crop_or_404(db: Session, crop_id: int) -> PlantingCalendar:
    calendar = db.query(PlantingCalendar).filter(PlantingCalendar.crop_id == crop_id).first()
    if calendar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")
    return calendar


@router.post("/", response_model=PlantingCalendarRead, status_code=status.HTTP_201_CREATED)
def create_calendar(
    payload: PlantingCalendarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlantingCalendar:
    crop = _get_crop_or_404(db, payload.crop_id)
    _ensure_can_manage_crop(current_user, crop)

    calendar = crop.planting_calendar or PlantingCalendar(crop_id=crop.id)
    update_payload = PlantingCalendarUpdate(**payload.model_dump(exclude={"crop_id"}))
    _apply_calendar_update(calendar, update_payload)

    if crop.planting_calendar is None:
        db.add(calendar)
    db.commit()
    db.refresh(calendar)
    return calendar


@router.get("/", response_model=list[PlantingCalendarRead])
def list_calendars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[PlantingCalendar]:
    query = db.query(PlantingCalendar).join(Crop)
    if not _is_admin(current_user):
        query = query.filter(Crop.owner_id == current_user.id)
    return query.order_by(PlantingCalendar.id).all()


@router.get("/events", response_model=list[CalendarEvent])
def list_active_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CalendarEvent]:
    query = db.query(PlantingCalendar).join(Crop).filter(PlantingCalendar.is_active.is_(True))
    if not _is_admin(current_user):
        query = query.filter(Crop.owner_id == current_user.id)

    events: list[CalendarEvent] = []
    for calendar in query.order_by(PlantingCalendar.id).all():
        events.extend(_current_phase_events(calendar))
    return events


@router.put("/crop/{crop_id}", response_model=PlantingCalendarRead)
def update_calendar_by_crop(
    crop_id: int,
    payload: PlantingCalendarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlantingCalendar:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)
    calendar = crop.planting_calendar or PlantingCalendar(crop_id=crop.id)
    _apply_calendar_update(calendar, payload)

    if crop.planting_calendar is None:
        db.add(calendar)
    db.commit()
    db.refresh(calendar)
    return calendar


@router.post("/crop/{crop_id}/activate", response_model=PlantingCalendarRead)
def activate_calendar_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlantingCalendar:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)
    calendar = crop.planting_calendar
    if calendar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")
    if not _calendar_is_complete(calendar):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Calendar dates are incomplete")

    calendar.is_active = True
    calendar.current_phase_index = 0
    calendar.status = "active"
    db.commit()
    db.refresh(calendar)
    return calendar


@router.post("/crop/{crop_id}/advance", response_model=PlantingCalendarRead)
def advance_calendar_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlantingCalendar:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)
    calendar = crop.planting_calendar
    if calendar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calendar not found")

    if calendar.current_phase_index < 2:
        calendar.current_phase_index += 1
        calendar.status = "active"
    else:
        calendar.status = "completed"
        calendar.is_active = False
    db.commit()
    db.refresh(calendar)
    return calendar


@router.get("/{calendar_id}", response_model=PlantingCalendarRead)
def get_calendar(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlantingCalendar:
    calendar = _get_calendar_or_404(db, calendar_id)
    _ensure_can_manage_calendar(current_user, calendar)
    return calendar


@router.get("/{calendar_id}/events", response_model=list[CalendarEvent])
def get_calendar_events(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CalendarEvent]:
    calendar = _get_calendar_or_404(db, calendar_id)
    _ensure_can_manage_calendar(current_user, calendar)
    return _current_phase_events(calendar)


@router.get("/crop/{crop_id}", response_model=PlantingCalendarRead)
def get_calendar_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlantingCalendar:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)
    return _get_calendar_by_crop_or_404(db, crop_id)


@router.put("/{calendar_id}", response_model=PlantingCalendarRead)
def update_calendar(
    calendar_id: int,
    payload: PlantingCalendarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PlantingCalendar:
    calendar = _get_calendar_or_404(db, calendar_id)
    _ensure_can_manage_calendar(current_user, calendar)
    _apply_calendar_update(calendar, payload)
    db.commit()
    db.refresh(calendar)
    return calendar


@router.delete("/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    calendar = _get_calendar_or_404(db, calendar_id)
    _ensure_can_manage_calendar(current_user, calendar)
    db.delete(calendar)
    db.commit()
