from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.planting_calendar import PlantingCalendar
from app.models.crop import Crop
from app.schemas.planting_calendar import (
    PlantingCalendarCreate,
    PlantingCalendarResponse,
    PlantingEvent,
)

router = APIRouter(prefix="/calendar", tags=["Planting Calendar"])


def month_half_from_date(value):
    if value is None:
        return None
    return value.month, 1 if value.day <= 15 else 2


def get_phase_definitions(calendar: PlantingCalendar):
    return [
        ("Siembra", calendar.planting_start, calendar.planting_end),
        ("Trasplante", calendar.transplant_start, calendar.transplant_end),
        ("Cosecha", calendar.harvest_start, calendar.harvest_end),
    ]


def month_half_text(month: int, half: int) -> str:
    half_text = "Primera mitad" if half == 1 else "Segunda mitad"
    month_names = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    if 1 <= month <= 12:
        return f"{half_text} de {month_names[month - 1]}"
    return f"{half_text} del mes {month}"


def build_event(title: str, value):
    month_half = month_half_from_date(value)
    if month_half is None:
        return None
    month, half = month_half
    return PlantingEvent(title=title, month=month, half=half)


def required_calendar_fields(calendar: PlantingCalendar):
    return [
        calendar.planting_start,
        calendar.planting_end,
        calendar.transplant_start,
        calendar.transplant_end,
        calendar.harvest_start,
        calendar.harvest_end,
    ]


def is_calendar_complete(calendar: PlantingCalendar) -> bool:
    return all(required_calendar_fields(calendar))


def validate_calendar_complete(calendar: PlantingCalendar):
    if not is_calendar_complete(calendar):
        raise HTTPException(
            status_code=400,
            detail="Completa las quincenas de siembra, trasplante y cosecha antes de añadir este cultivo al calendario",
        )


def build_phase_event(calendar: PlantingCalendar, phase: str, start, phase_index: int, is_last_phase: bool):
    month_half = month_half_from_date(start)
    if month_half is None:
        return None

    month, half = month_half
    crop_name = calendar.crop.name if calendar.crop else None
    return PlantingEvent(
        title=f"{crop_name} - {phase}" if crop_name else phase,
        month=month,
        half=half,
        crop_id=calendar.crop_id,
        crop_name=crop_name,
        phase=phase,
        phase_index=phase_index,
        is_last_phase=is_last_phase,
    )


def generate_calendar_events(calendar: PlantingCalendar):
    if not calendar.is_active or calendar.status == "completed":
        return []

    phases = get_phase_definitions(calendar)
    phase_count = len(phases)
    phase_index = min(max(calendar.current_phase_index or 0, 0), phase_count - 1)
    phase, start, _ = phases[phase_index]
    event = build_phase_event(calendar, phase, start, phase_index, phase_index == phase_count - 1)
    return [event] if event is not None else []


def get_owned_crop(db: Session, crop_id: int, current_user: dict) -> Crop:
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to manage calendar for this crop")
    return crop


def apply_calendar_data(calendar: PlantingCalendar, data: PlantingCalendarCreate):
    calendar.planting_start = data.planting_start
    calendar.planting_end = data.planting_end
    calendar.transplant_start = data.transplant_start
    calendar.transplant_end = data.transplant_end
    calendar.harvest_start = data.harvest_start
    calendar.harvest_end = data.harvest_end
    calendar.current_phase_index = min(max(calendar.current_phase_index or 0, 0), len(get_phase_definitions(calendar)) - 1)


@router.post("/", response_model=PlantingCalendarResponse)
def create_calendar(
    data: PlantingCalendarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user_role != "admin" and crop.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add calendar to this crop")

    existing = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == data.crop_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Calendar already exists for this crop")

    calendar = PlantingCalendar(**data.dict())
    calendar.is_active = False
    calendar.status = "draft"
    calendar.current_phase_index = 0

    db.add(calendar)
    db.commit()
    db.refresh(calendar)

    return calendar


@router.get("/events", response_model=list[PlantingEvent])
def get_my_calendar_events(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(PlantingCalendar).join(Crop).filter(PlantingCalendar.is_active == True)
    if current_user["role"] != "admin":
        query = query.filter(Crop.user_id == current_user["user_id"])

    calendars = query.all()
    events = []
    for calendar in calendars:
        if is_calendar_complete(calendar):
            events.extend(generate_calendar_events(calendar))
    return events


@router.get("/", response_model=list[PlantingCalendarResponse])
def get_calendars(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] == "admin":
        return db.query(PlantingCalendar).all()
    return db.query(PlantingCalendar).join(Crop).filter(Crop.user_id == current_user["user_id"]).all()


@router.put("/crop/{crop_id}", response_model=PlantingCalendarResponse)
def upsert_calendar_by_crop(
    crop_id: int,
    data: PlantingCalendarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    get_owned_crop(db, crop_id, current_user)

    calendar = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == crop_id
    ).first()

    if calendar is None:
        calendar = PlantingCalendar(crop_id=crop_id)
        db.add(calendar)

    apply_calendar_data(calendar, data)
    calendar.crop_id = crop_id

    if calendar.is_active and not is_calendar_complete(calendar):
        calendar.is_active = False
        calendar.status = "draft"

    db.commit()
    db.refresh(calendar)
    return calendar


@router.post("/crop/{crop_id}/activate", response_model=PlantingCalendarResponse)
def activate_calendar_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    get_owned_crop(db, crop_id, current_user)

    calendar = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == crop_id
    ).first()

    if calendar is None:
        raise HTTPException(
            status_code=400,
            detail="Completa las quincenas de siembra, trasplante y cosecha antes de añadir este cultivo al calendario",
        )

    validate_calendar_complete(calendar)
    if not calendar.is_active:
        calendar.current_phase_index = 0
    calendar.is_active = True
    calendar.status = "active"
    calendar.current_phase_index = min(max(calendar.current_phase_index or 0, 0), len(get_phase_definitions(calendar)) - 1)

    db.commit()
    db.refresh(calendar)
    return calendar


@router.post("/crop/{crop_id}/advance", response_model=PlantingCalendarResponse)
def advance_calendar_phase_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    get_owned_crop(db, crop_id, current_user)

    calendar = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == crop_id
    ).first()

    if calendar is None or not calendar.is_active or calendar.status == "completed":
        raise HTTPException(status_code=400, detail="Este cultivo no está activo en el calendario")

    validate_calendar_complete(calendar)
    last_phase_index = len(get_phase_definitions(calendar)) - 1

    if calendar.current_phase_index >= last_phase_index:
        calendar.status = "completed"
        calendar.is_active = False
    else:
        calendar.current_phase_index += 1
        calendar.status = "active"

    db.commit()
    db.refresh(calendar)
    return calendar


@router.get("/{calendar_id}", response_model=PlantingCalendarResponse)
def get_calendar(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    calendar = db.query(PlantingCalendar).filter(
        PlantingCalendar.id == calendar_id
    ).first()

    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")

    crop = db.query(Crop).filter(Crop.id == calendar.crop_id).first()
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this calendar")

    return calendar


@router.get("/{calendar_id}/events", response_model=list[PlantingEvent])
def get_calendar_events(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    calendar = db.query(PlantingCalendar).filter(
        PlantingCalendar.id == calendar_id
    ).first()

    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")

    crop = db.query(Crop).filter(Crop.id == calendar.crop_id).first()
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this calendar")

    return generate_calendar_events(calendar)


@router.get("/crop/{crop_id}", response_model=PlantingCalendarResponse)
def get_calendar_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view calendar for this crop")

    calendar = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == crop_id
    ).first()

    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found for this crop")

    return calendar


@router.put("/{calendar_id}", response_model=PlantingCalendarResponse)
def update_calendar(
    calendar_id: int,
    data: PlantingCalendarCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    calendar = db.query(PlantingCalendar).filter(
        PlantingCalendar.id == calendar_id
    ).first()

    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")

    crop = db.query(Crop).filter(Crop.id == calendar.crop_id).first()
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this calendar")

    if current_user["role"] != "admin":
        new_crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
        if not new_crop or new_crop.user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to assign this calendar to another user's crop")

    apply_calendar_data(calendar, data)
    calendar.crop_id = data.crop_id
    if calendar.is_active and not is_calendar_complete(calendar):
        calendar.is_active = False
        calendar.status = "draft"

    db.commit()
    db.refresh(calendar)

    return calendar


@router.delete("/{calendar_id}")
def delete_calendar(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    calendar = db.query(PlantingCalendar).filter(
        PlantingCalendar.id == calendar_id
    ).first()

    if not calendar:
        raise HTTPException(status_code=404, detail="Calendar not found")

    crop = db.query(Crop).filter(Crop.id == calendar.crop_id).first()
    if crop is None:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this calendar")

    db.delete(calendar)
    db.commit()

    return {"message": "Calendar deleted"}
