
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.crop import Crop
from app.models.planting_calendar import PlantingCalendar
from app.models.user import User
from app.schemas.planting_calendar import (
    CalendarEvent,
    PlantingCalendarCreate,
    PlantingCalendarRead,
    PlantingCalendarUpdate,
)

router = APIRouter(prefix="/calendar", tags=["calendar"])

PHASE_NAMES = {0: "Siembra", 1: "Trasplante", 2: "Cosecha"}


def _get_crop_or_404(crop_id: int, db: Session) -> Crop:
    """Obtiene un cultivo por ID o lanza 404."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cultivo no encontrado",
        )
    return crop


def _verify_crop_ownership(crop: Crop, current_user: User) -> None:
    """Verifica que el usuario sea propietario del cultivo o admin."""
    if current_user.role != "admin" and crop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para gestionar este cultivo",
        )


def _calendar_to_read(cal: PlantingCalendar) -> PlantingCalendarRead:
    """Convierte un modelo PlantingCalendar a PlantingCalendarRead."""
    return PlantingCalendarRead(
        id=cal.id,
        crop_id=cal.crop_id,
        planting_start=cal.planting_start,
        planting_end=cal.planting_end,
        transplant_start=cal.transplant_start,
        transplant_end=cal.transplant_end,
        harvest_start=cal.harvest_start,
        harvest_end=cal.harvest_end,
        is_active=cal.is_active,
        current_phase_index=cal.current_phase_index,
        status=cal.status,
        notes=cal.notes,
        created_at=cal.created_at,
        updated_at=cal.updated_at,
    )


def _compute_events(cal: PlantingCalendar) -> list[dict]:
    """Calcula eventos del calendario por mes y quincena, ignorando el año."""
    events: list[dict] = []

    ranges = [
        ("planting", 0, cal.planting_start, cal.planting_end),
        ("transplant", 1, cal.transplant_start, cal.transplant_end),
        ("harvest", 2, cal.harvest_start, cal.harvest_end),
    ]

    for phase_key, phase_index, start_date, end_date in ranges:
        if not start_date or not end_date:
            continue

        # Ignorar el año: usar mes-día para calcular quincenas
        start_ref = date(2000, start_date.month, start_date.day)
        end_ref = date(2000, end_date.month, end_date.day)
        cross_year = start_ref > end_ref

        month_start = start_ref.month
        month_end = end_ref.month

        # Manejar rangos que cruzan año (ej. noviembre → febrero)
        if cross_year:
            months = list(range(month_start, 13)) + list(range(1, month_end + 1))
        else:
            months = list(range(month_start, month_end + 1))

        for m in months:
            # Usar una tupla (m, día) para comparaciones cross-year
            # Para rangos que no cruzan año: check estándar start <= val <= end
            # Para rangos que cruzan año: val >= start OR val <= end (wraparound)
            q1_start = date(2000, m, 1)
            q1_end = date(2000, m, 15)
            q2_start = date(2000, m, 16)
            q2_end = date(2000, m, 28)

            def _in_range(qs: date, qe: date) -> bool:
                """Comprueba si una quincena [qs, qe] solapa con [start_ref, end_ref]."""
                if cross_year:
                    # Rango envuelve año: solapa si quincena está después de start_ref O antes de end_ref
                    return (qe >= start_ref) or (qs <= end_ref)
                else:
                    # Rango normal: quincena debe estar dentro de [start_ref, end_ref]
                    return qe >= start_ref and qs <= end_ref

            if _in_range(q1_start, q1_end):
                phase_label = PHASE_NAMES[phase_index]
                events.append({
                    "month": m,
                    "fortnight": 1,
                    "phase": phase_label,
                    "phase_index": phase_index,
                    "label": f"{phase_label} - 1ª quincena",
                })

            if _in_range(q2_start, q2_end):
                phase_label = PHASE_NAMES[phase_index]
                events.append({
                    "month": m,
                    "fortnight": 2,
                    "phase": phase_label,
                    "phase_index": phase_index,
                    "label": f"{phase_label} - 2ª quincena",
                })

    return events


def _is_complete(cal: PlantingCalendar) -> bool:
    """Comprueba si el calendario tiene todas las fechas completas."""
    return all([
        cal.planting_start,
        cal.planting_end,
        cal.transplant_start,
        cal.transplant_end,
        cal.harvest_start,
        cal.harvest_end,
    ])


# ──────────────────────────────────────────────
# POST /calendar/ — Crear calendario
# ──────────────────────────────────────────────


@router.post("/", response_model=PlantingCalendarRead, status_code=status.HTTP_201_CREATED)
def create_calendar(
    data: PlantingCalendarCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un calendario agrícola para un cultivo."""
    crop = _get_crop_or_404(data.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    # Verificar que no exista ya un calendario para este cultivo
    existing = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == data.crop_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este cultivo ya tiene un calendario",
        )

    cal = PlantingCalendar(
        crop_id=data.crop_id,
        planting_start=data.planting_start,
        planting_end=data.planting_end,
        transplant_start=data.transplant_start,
        transplant_end=data.transplant_end,
        harvest_start=data.harvest_start,
        harvest_end=data.harvest_end,
        notes=data.notes,
    )
    db.add(cal)
    db.commit()
    db.refresh(cal)
    return _calendar_to_read(cal)


# ──────────────────────────────────────────────
# GET /calendar/ — Listar calendarios del usuario
# ──────────────────────────────────────────────


@router.get("/", response_model=list[PlantingCalendarRead])
def list_calendars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista calendarios. Admin ve todos; usuario normal ve solo los suyos."""
    if current_user.role == "admin":
        calendars = db.query(PlantingCalendar).all()
    else:
        calendars = (
            db.query(PlantingCalendar)
            .join(Crop, PlantingCalendar.crop_id == Crop.id)
            .filter(Crop.owner_id == current_user.id)
            .all()
        )
    return [_calendar_to_read(c) for c in calendars]


# ──────────────────────────────────────────────
# GET /calendar/events — Eventos del usuario
# ──────────────────────────────────────────────


@router.get("/events", response_model=list[CalendarEvent])
def list_user_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve eventos activos del usuario autenticado."""
    calendars = (
        db.query(PlantingCalendar)
        .join(Crop, PlantingCalendar.crop_id == Crop.id)
        .filter(Crop.owner_id == current_user.id)
        .filter(PlantingCalendar.is_active == True)
        .all()
    )

    all_events: list[CalendarEvent] = []
    for cal in calendars:
        raw_events = _compute_events(cal)
        for evt in raw_events:
            all_events.append(CalendarEvent(**evt))

    return all_events


# ──────────────────────────────────────────────
# PUT /calendar/crop/{crop_id} — Actualizar por cultivo
# ──────────────────────────────────────────────


@router.put("/crop/{crop_id}", response_model=PlantingCalendarRead)
def update_calendar_by_crop(
    crop_id: int,
    data: PlantingCalendarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza el calendario de un cultivo."""
    crop = _get_crop_or_404(crop_id, db)
    _verify_crop_ownership(crop, current_user)

    cal = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == crop_id
    ).first()
    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado para este cultivo",
        )

    if data.planting_start is not None:
        cal.planting_start = data.planting_start
    if data.planting_end is not None:
        cal.planting_end = data.planting_end
    if data.transplant_start is not None:
        cal.transplant_start = data.transplant_start
    if data.transplant_end is not None:
        cal.transplant_end = data.transplant_end
    if data.harvest_start is not None:
        cal.harvest_start = data.harvest_start
    if data.harvest_end is not None:
        cal.harvest_end = data.harvest_end
    if data.notes is not None:
        cal.notes = data.notes

    db.commit()
    db.refresh(cal)
    return _calendar_to_read(cal)


# ──────────────────────────────────────────────
# POST /calendar/crop/{crop_id}/activate — Activar
# ──────────────────────────────────────────────


@router.post("/crop/{crop_id}/activate", response_model=PlantingCalendarRead)
def activate_calendar(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Activa el calendario de un cultivo. Requiere fechas completas."""
    crop = _get_crop_or_404(crop_id, db)
    _verify_crop_ownership(crop, current_user)

    cal = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == crop_id
    ).first()
    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado para este cultivo",
        )

    if not _is_complete(cal):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede activar: faltan fechas de siembra, trasplante o cosecha",
        )

    if cal.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede activar un calendario completado",
        )

    if cal.status != "active":
        cal.is_active = True
        cal.status = "active"
        cal.current_phase_index = 0
        db.commit()
        db.refresh(cal)

    return _calendar_to_read(cal)


# ──────────────────────────────────────────────
# POST /calendar/crop/{crop_id}/advance — Avanzar fase
# ──────────────────────────────────────────────


@router.post("/crop/{crop_id}/advance", response_model=PlantingCalendarRead)
def advance_phase(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Avanza a la siguiente fase del calendario."""
    crop = _get_crop_or_404(crop_id, db)
    _verify_crop_ownership(crop, current_user)

    cal = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == crop_id
    ).first()
    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado para este cultivo",
        )

    if not cal.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El calendario no está activo",
        )

    if cal.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El calendario ya está completado",
        )

    current = cal.current_phase_index
    if current == 0:
        # Siembra → Trasplante
        cal.current_phase_index = 1
    elif current == 1:
        # Trasplante → Cosecha
        cal.current_phase_index = 2
    elif current == 2:
        # Cosecha → completado
        cal.current_phase_index = 2
        cal.status = "completed"
        cal.is_active = False

    db.commit()
    db.refresh(cal)
    return _calendar_to_read(cal)


# ──────────────────────────────────────────────
# GET /calendar/{calendar_id} — Obtener calendario por ID
# ──────────────────────────────────────────────


@router.get("/{calendar_id}", response_model=PlantingCalendarRead)
def get_calendar(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un calendario por su ID."""
    cal = db.query(PlantingCalendar).filter(
        PlantingCalendar.id == calendar_id
    ).first()
    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado",
        )

    crop = _get_crop_or_404(cal.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    return _calendar_to_read(cal)


# ──────────────────────────────────────────────
# GET /calendar/{calendar_id}/events — Eventos de un calendario
# ──────────────────────────────────────────────


@router.get("/{calendar_id}/events", response_model=list[CalendarEvent])
def get_calendar_events(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve los eventos calculados de un calendario específico."""
    cal = db.query(PlantingCalendar).filter(
        PlantingCalendar.id == calendar_id
    ).first()
    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado",
        )

    crop = _get_crop_or_404(cal.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    raw_events = _compute_events(cal)
    return [CalendarEvent(**evt) for evt in raw_events]


# ──────────────────────────────────────────────
# GET /calendar/crop/{crop_id} — Obtener por cultivo
# ──────────────────────────────────────────────


@router.get("/crop/{crop_id}", response_model=PlantingCalendarRead)
def get_calendar_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene el calendario de un cultivo específico."""
    crop = _get_crop_or_404(crop_id, db)
    _verify_crop_ownership(crop, current_user)

    cal = db.query(PlantingCalendar).filter(
        PlantingCalendar.crop_id == crop_id
    ).first()
    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado para este cultivo",
        )

    return _calendar_to_read(cal)


# ──────────────────────────────────────────────
# PUT /calendar/{calendar_id} — Actualizar calendario
# ──────────────────────────────────────────────


@router.put("/{calendar_id}", response_model=PlantingCalendarRead)
def update_calendar(
    calendar_id: int,
    data: PlantingCalendarUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un calendario por su ID."""
    cal = db.query(PlantingCalendar).filter(
        PlantingCalendar.id == calendar_id
    ).first()
    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado",
        )

    crop = _get_crop_or_404(cal.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    if data.planting_start is not None:
        cal.planting_start = data.planting_start
    if data.planting_end is not None:
        cal.planting_end = data.planting_end
    if data.transplant_start is not None:
        cal.transplant_start = data.transplant_start
    if data.transplant_end is not None:
        cal.transplant_end = data.transplant_end
    if data.harvest_start is not None:
        cal.harvest_start = data.harvest_start
    if data.harvest_end is not None:
        cal.harvest_end = data.harvest_end
    if data.notes is not None:
        cal.notes = data.notes

    db.commit()
    db.refresh(cal)
    return _calendar_to_read(cal)


# ──────────────────────────────────────────────
# DELETE /calendar/{calendar_id} — Eliminar calendario
# ──────────────────────────────────────────────


@router.delete("/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar(
    calendar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un calendario. Usuario normal solo puede eliminar los suyos."""
    cal = db.query(PlantingCalendar).filter(
        PlantingCalendar.id == calendar_id
    ).first()
    if not cal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendario no encontrado",
        )

    crop = _get_crop_or_404(cal.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    db.delete(cal)
    db.commit()
    return None