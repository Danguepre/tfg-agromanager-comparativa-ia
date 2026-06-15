"""
Rutas de calendario agrícola: CRUD, activación, avance de fases, eventos.
"""
from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.crop import Crop
from app.models.planting_calendar import PlantingCalendar
from app.schemas.planting_calendar import (
    PlantingCalendarCreate,
    PlantingCalendarUpdate,
    PlantingCalendarResponse,
    PlantingCalendarDetailResponse,
    CalendarEventsResponse,
)
from app.services.planting_calendar_service import (
    create_calendar,
    get_calendar_by_id,
    get_calendar_by_crop_id,
    get_user_calendars,
    update_calendar,
    activate_calendar,
    advance_phase,
    get_calendar_events,
    get_user_active_events,
    delete_calendar,
)

router = APIRouter(prefix="/calendar", tags=["calendar"])


# ============================================================================
# POST /calendar/ - Crear calendario
# ============================================================================
@router.post("", response_model=PlantingCalendarResponse, status_code=status.HTTP_201_CREATED)
def create_calendar_endpoint(
    calendar_data: PlantingCalendarCreate,
    crop_id: int = Query(..., description="ID del cultivo"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Crear nuevo calendario agrícola para un cultivo.
    - Usuario normal solo puede crear para sus propios cultivos.
    - Admin puede crear para cualquier cultivo.
    - Calendario se crea en estado DRAFT.
    """
    try:
        calendar = create_calendar(
            db=db,
            crop_id=crop_id,
            planting_start=calendar_data.planting_start,
            planting_end=calendar_data.planting_end,
            transplant_start=calendar_data.transplant_start,
            transplant_end=calendar_data.transplant_end,
            harvest_start=calendar_data.harvest_start,
            harvest_end=calendar_data.harvest_end,
            current_user=current_user,
        )
        return calendar
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create calendars for your own crops",
        )


# ============================================================================
# GET /calendar/ - Listar calendarios del usuario
# ============================================================================
@router.get("", response_model=dict)
def list_user_calendars(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Listar calendarios del usuario autenticado.
    - Usuario normal ve solo sus calendarios.
    - Admin ve todos.
    """
    if current_user.role.value == "admin":
        # Admin ve todos los calendarios
        query = db.query(PlantingCalendar)
        total = query.count()
        calendars = query.offset(skip).limit(limit).all()
    else:
        # Usuario normal ve solo sus calendarios
        calendars, total = get_user_calendars(db, current_user.id, skip, limit)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [PlantingCalendarResponse.model_validate(c) for c in calendars],
    }


# ============================================================================
# GET /calendar/events - Obtener eventos activos del usuario
# ============================================================================
@router.get("/events", response_model=CalendarEventsResponse)
def get_user_events(
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener eventos activos del usuario autenticado.
    - Solo calendarios ACTIVOS.
    - Retorna la fase actual como evento.
    """
    events = get_user_active_events(db, current_user.id)
    return CalendarEventsResponse(
        total=len(events),
        items=events,
    )


# ============================================================================
# GET /calendar/{calendar_id} - Obtener calendario por ID
# ============================================================================
@router.get("/{calendar_id}", response_model=PlantingCalendarDetailResponse)
def get_calendar_detail(
    calendar_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener detalles de un calendario específico.
    - Usuario normal solo ve sus calendarios.
    - Admin ve todos.
    """
    calendar = get_calendar_by_id(db, calendar_id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found",
        )

    # Validar permisos
    if current_user.role.value != "admin":
        if calendar.crop.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own calendars",
            )

    return calendar


# ============================================================================
# GET /calendar/{calendar_id}/events - Obtener eventos del calendario
# ============================================================================
@router.get("/{calendar_id}/events", response_model=CalendarEventsResponse)
def get_calendar_events_endpoint(
    calendar_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener eventos (fases) de un calendario específico.
    - Retorna la fase actual.
    - Usuario normal solo ve sus calendarios.
    """
    calendar = get_calendar_by_id(db, calendar_id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found",
        )

    # Validar permisos
    if current_user.role.value != "admin":
        if calendar.crop.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own calendars",
            )

    try:
        events = get_calendar_events(db, calendar_id)
        return CalendarEventsResponse(
            total=len(events),
            items=events,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# GET /calendar/crop/{crop_id} - Obtener calendario de un cultivo
# ============================================================================
@router.get("/crop/{crop_id}", response_model=PlantingCalendarDetailResponse)
def get_calendar_for_crop(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener el calendario asociado a un cultivo específico.
    - Usuario normal solo para sus cultivos.
    - Admin para cualquier cultivo.
    """
    # Obtener cultivo
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    # Validar permisos
    if current_user.role.value != "admin":
        if crop.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access calendars for your own crops",
            )

    # Obtener calendario
    calendar = get_calendar_by_crop_id(db, crop_id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found for this crop",
        )

    return calendar


# ============================================================================
# PUT /calendar/crop/{crop_id} - Actualizar calendario de un cultivo
# ============================================================================
@router.put("/crop/{crop_id}", response_model=PlantingCalendarResponse)
def update_calendar_for_crop(
    crop_id: int,
    update_data: PlantingCalendarUpdate,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Actualizar el calendario asociado a un cultivo.
    - Usuario normal solo sus cultivos.
    - Admin todos.
    - No se pueden actualizar calendarios ACTIVE o COMPLETED.
    """
    # Obtener cultivo
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    # Validar permisos
    if current_user.role.value != "admin":
        if crop.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update calendars for your own crops",
            )

    # Obtener calendario
    calendar = get_calendar_by_crop_id(db, crop_id)
    if not calendar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar not found for this crop",
        )

    try:
        updated = update_calendar(
            db=db,
            calendar_id=calendar.id,
            planting_start=update_data.planting_start,
            planting_end=update_data.planting_end,
            transplant_start=update_data.transplant_start,
            transplant_end=update_data.transplant_end,
            harvest_start=update_data.harvest_start,
            harvest_end=update_data.harvest_end,
            current_user=current_user,
        )
        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )


# ============================================================================
# PUT /calendar/{calendar_id} - Actualizar calendario
# ============================================================================
@router.put("/{calendar_id}", response_model=PlantingCalendarResponse)
def update_calendar_endpoint(
    calendar_id: int,
    update_data: PlantingCalendarUpdate,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Actualizar calendario por ID.
    - Usuario normal solo sus calendarios.
    - Admin todos.
    """
    try:
        calendar = update_calendar(
            db=db,
            calendar_id=calendar_id,
            planting_start=update_data.planting_start,
            planting_end=update_data.planting_end,
            transplant_start=update_data.transplant_start,
            transplant_end=update_data.transplant_end,
            harvest_start=update_data.harvest_start,
            harvest_end=update_data.harvest_end,
            current_user=current_user,
        )
        return calendar
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST if "not found" not in str(e).lower() else status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own calendars",
        )


# ============================================================================
# DELETE /calendar/{calendar_id} - Eliminar calendario
# ============================================================================
@router.delete("/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_endpoint(
    calendar_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Eliminar un calendario.
    - Usuario normal solo sus calendarios.
    - Admin todos.
    """
    try:
        delete_calendar(db, calendar_id, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own calendars",
        )

    return None


# ============================================================================
# POST /calendar/{calendar_id}/activate - Activar calendario
# ============================================================================
@router.post("/{calendar_id}/activate", response_model=PlantingCalendarResponse)
def activate_calendar_endpoint(
    calendar_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Activar un calendario.
    - Requiere que todas las fechas estén completas.
    - Usuario normal solo sus calendarios.
    - Admin todos.
    """
    try:
        calendar = activate_calendar(db, calendar_id, current_user)
        return calendar
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only activate your own calendars",
        )


# ============================================================================
# POST /calendar/{calendar_id}/advance - Avanzar fase
# ============================================================================
@router.post("/{calendar_id}/advance", response_model=PlantingCalendarResponse)
def advance_phase_endpoint(
    calendar_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Avanzar a la siguiente fase del calendario.
    - Siembra (0) → Trasplante (1)
    - Trasplante (1) → Cosecha (2)
    - Cosecha (2) → Completado e inactivo
    - Solo si el calendario está ACTIVE.
    - Usuario normal solo sus calendarios.
    """
    try:
        calendar = advance_phase(db, calendar_id, current_user)
        return calendar
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only advance phases for your own calendars",
        )
