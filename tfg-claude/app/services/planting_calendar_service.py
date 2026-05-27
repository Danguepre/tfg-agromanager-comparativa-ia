"""
Servicio de calendario agrícola: CRUD, validaciones, eventos, fases.
"""
from datetime import date, datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.planting_calendar import PlantingCalendar, CalendarStatus
from app.models.crop import Crop
from app.models.user import User, UserRole
from app.schemas.planting_calendar import CalendarEvent


# Nombres de fases
PHASE_NAMES = ["Siembra", "Trasplante", "Cosecha"]


def create_calendar(
    db: Session,
    crop_id: int,
    planting_start: Optional[date],
    planting_end: Optional[date],
    transplant_start: Optional[date],
    transplant_end: Optional[date],
    harvest_start: Optional[date],
    harvest_end: Optional[date],
    current_user: User,
) -> PlantingCalendar:
    """
    Crear calendario agrícola para un cultivo.
    El cultivo debe pertenecer al usuario actual (o es admin).
    Retorna en estado DRAFT, no activado.
    """
    # Validar que el cultivo existe
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise ValueError("Crop not found")

    # Validar permisos: usuario normal solo su cultivo, admin todos
    if current_user.role != UserRole.ADMIN and crop.owner_id != current_user.id:
        raise PermissionError("You can only create calendars for your own crops")

    # Validar que no exista calendario previo para este cultivo
    existing = db.query(PlantingCalendar).filter(PlantingCalendar.crop_id == crop_id).first()
    if existing:
        raise ValueError("Calendar already exists for this crop")

    # Crear calendario
    calendar = PlantingCalendar(
        crop_id=crop_id,
        planting_start=planting_start,
        planting_end=planting_end,
        transplant_start=transplant_start,
        transplant_end=transplant_end,
        harvest_start=harvest_start,
        harvest_end=harvest_end,
        is_active=False,
        current_phase_index=0,
        status=CalendarStatus.DRAFT,
    )
    db.add(calendar)
    db.commit()
    db.refresh(calendar)
    return calendar


def get_calendar_by_id(db: Session, calendar_id: int) -> Optional[PlantingCalendar]:
    """Obtener calendario por ID."""
    return db.query(PlantingCalendar).filter(PlantingCalendar.id == calendar_id).first()


def get_calendar_by_crop_id(db: Session, crop_id: int) -> Optional[PlantingCalendar]:
    """Obtener calendario de un cultivo."""
    return db.query(PlantingCalendar).filter(PlantingCalendar.crop_id == crop_id).first()


def get_user_calendars(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[PlantingCalendar], int]:
    """
    Obtener calendarios del usuario (solo sus cultivos).
    Retorna (calendars, total_count).
    """
    query = db.query(PlantingCalendar).join(Crop).filter(Crop.owner_id == user_id)
    total = query.count()
    calendars = query.offset(skip).limit(limit).all()
    return calendars, total


def update_calendar(
    db: Session,
    calendar_id: int,
    planting_start: Optional[date] = None,
    planting_end: Optional[date] = None,
    transplant_start: Optional[date] = None,
    transplant_end: Optional[date] = None,
    harvest_start: Optional[date] = None,
    harvest_end: Optional[date] = None,
    current_user: Optional[User] = None,
    partial: bool = True,  # Si True, solo actualiza los campos proporcionados
) -> PlantingCalendar:
    """
    Actualizar calendario agrícola.
    Si es usuario normal, valida permisos sobre el cultivo.
    No permite actualizar si ya está ACTIVE o COMPLETED.
    """
    calendar = db.query(PlantingCalendar).filter(PlantingCalendar.id == calendar_id).first()
    if not calendar:
        raise ValueError("Calendar not found")

    # Validar permisos
    if current_user and current_user.role != UserRole.ADMIN:
        crop = calendar.crop
        if crop.owner_id != current_user.id:
            raise PermissionError("You can only update calendars for your own crops")

    # No permitir actualizar si ya está en ejecución
    if calendar.status != CalendarStatus.DRAFT:
        raise ValueError("Cannot update active or completed calendar")

    # Actualizar solo los campos proporcionados (si partial=True)
    # En el contexto del PUT /calendar/{id}, planting_start==None significa "no actualizar"
    # Pero en el contexto del PUT /calendar/crop/{crop_id}, queremos permitir establecer a None
    # Para simplificar, solo actualizamos si el valor es diferente y no None
    if planting_start is not None:
        calendar.planting_start = planting_start
    if planting_end is not None:
        calendar.planting_end = planting_end
    if transplant_start is not None:
        calendar.transplant_start = transplant_start
    if transplant_end is not None:
        calendar.transplant_end = transplant_end
    if harvest_start is not None:
        calendar.harvest_start = harvest_start
    if harvest_end is not None:
        calendar.harvest_end = harvest_end

    db.commit()
    db.refresh(calendar)
    return calendar


def activate_calendar(
    db: Session,
    calendar_id: int,
    current_user: Optional[User] = None,
) -> PlantingCalendar:
    """
    Activar un calendario.
    - Requiere que todas las fechas (siembra, trasplante, cosecha) estén completadas.
    - Solo usuario propietario o admin.
    - Pasa a estado ACTIVE.
    """
    calendar = db.query(PlantingCalendar).filter(PlantingCalendar.id == calendar_id).first()
    if not calendar:
        raise ValueError("Calendar not found")

    # Validar permisos
    if current_user and current_user.role != UserRole.ADMIN:
        crop = calendar.crop
        if crop.owner_id != current_user.id:
            raise PermissionError("You can only activate calendars for your own crops")

    # Validar que todas las fechas estén presentes
    if not (calendar.planting_start and calendar.planting_end and
            calendar.transplant_start and calendar.transplant_end and
            calendar.harvest_start and calendar.harvest_end):
        raise ValueError("Calendar must have all dates (planting, transplant, harvest) to be activated")

    # Activar
    calendar.is_active = True
    calendar.status = CalendarStatus.ACTIVE
    calendar.current_phase_index = 0  # Siempre comienza en Siembra

    db.commit()
    db.refresh(calendar)
    return calendar


def advance_phase(
    db: Session,
    calendar_id: int,
    current_user: Optional[User] = None,
) -> PlantingCalendar:
    """
    Avanzar a la siguiente fase.
    - Siembra (0) → Trasplante (1)
    - Trasplante (1) → Cosecha (2)
    - Cosecha (2) → Marca como COMPLETED e inactivo
    """
    calendar = db.query(PlantingCalendar).filter(PlantingCalendar.id == calendar_id).first()
    if not calendar:
        raise ValueError("Calendar not found")

    # Validar permisos
    if current_user and current_user.role != UserRole.ADMIN:
        crop = calendar.crop
        if crop.owner_id != current_user.id:
            raise PermissionError("You can only advance phases for your own calendars")

    # Validar que esté activo
    if not calendar.is_active:
        raise ValueError("Calendar must be active to advance phases")

    current_phase = calendar.current_phase_index

    if current_phase == 0:  # Siembra → Trasplante
        calendar.current_phase_index = 1
    elif current_phase == 1:  # Trasplante → Cosecha
        calendar.current_phase_index = 2
    elif current_phase == 2:  # Cosecha → Completado
        calendar.current_phase_index = 2
        calendar.is_active = False
        calendar.status = CalendarStatus.COMPLETED
    else:
        raise ValueError("Invalid phase index")

    db.commit()
    db.refresh(calendar)
    return calendar


def get_calendar_events(
    db: Session,
    calendar_id: int,
) -> list[CalendarEvent]:
    """
    Obtener eventos del calendario.
    Retorna solo la fase actual como evento.
    """
    calendar = db.query(PlantingCalendar).filter(PlantingCalendar.id == calendar_id).first()
    if not calendar:
        raise ValueError("Calendar not found")

    crop = calendar.crop

    # Determinar fechas de la fase actual
    phase_idx = calendar.current_phase_index

    if phase_idx == 0:  # Siembra
        start_date = calendar.planting_start
        end_date = calendar.planting_end
    elif phase_idx == 1:  # Trasplante
        start_date = calendar.transplant_start
        end_date = calendar.transplant_end
    elif phase_idx == 2:  # Cosecha
        start_date = calendar.harvest_start
        end_date = calendar.harvest_end
    else:
        raise ValueError("Invalid phase index")

    event = CalendarEvent(
        phase_index=phase_idx,
        phase_name=PHASE_NAMES[phase_idx],
        start_date=start_date,
        end_date=end_date,
        calendar_id=calendar.id,
        crop_id=crop.id,
        crop_name=crop.name,
        is_active=calendar.is_active,
    )

    return [event]


def get_user_active_events(
    db: Session,
    user_id: int,
) -> list[CalendarEvent]:
    """
    Obtener eventos activos del usuario.
    Solo calendarios activos del usuario.
    """
    calendars = db.query(PlantingCalendar).join(Crop).filter(
        Crop.owner_id == user_id,
        PlantingCalendar.is_active == True,  # noqa: E712
    ).all()

    events = []
    for calendar in calendars:
        phase_idx = calendar.current_phase_index
        crop = calendar.crop

        if phase_idx == 0:
            start_date = calendar.planting_start
            end_date = calendar.planting_end
        elif phase_idx == 1:
            start_date = calendar.transplant_start
            end_date = calendar.transplant_end
        elif phase_idx == 2:
            start_date = calendar.harvest_start
            end_date = calendar.harvest_end
        else:
            continue

        event = CalendarEvent(
            phase_index=phase_idx,
            phase_name=PHASE_NAMES[phase_idx],
            start_date=start_date,
            end_date=end_date,
            calendar_id=calendar.id,
            crop_id=crop.id,
            crop_name=crop.name,
            is_active=calendar.is_active,
        )
        events.append(event)

    return events


def delete_calendar(
    db: Session,
    calendar_id: int,
    current_user: Optional[User] = None,
) -> None:
    """
    Eliminar un calendario.
    Usuario normal solo puede eliminar sus propios calendarios.
    """
    calendar = db.query(PlantingCalendar).filter(PlantingCalendar.id == calendar_id).first()
    if not calendar:
        raise ValueError("Calendar not found")

    # Validar permisos
    if current_user and current_user.role != UserRole.ADMIN:
        crop = calendar.crop
        if crop.owner_id != current_user.id:
            raise PermissionError("You can only delete calendars for your own crops")

    db.delete(calendar)
    db.commit()
