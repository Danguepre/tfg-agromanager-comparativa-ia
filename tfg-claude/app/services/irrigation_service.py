"""
Servicio de riego: CRUD, validaciones.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.irrigation_attributes import IrrigationAttributes
from app.models.crop import Crop
from app.models.user import User, UserRole


def get_irrigation_by_id(db: Session, irrigation_id: int) -> Optional[IrrigationAttributes]:
    """Obtener riego por ID."""
    return db.query(IrrigationAttributes).filter(IrrigationAttributes.id == irrigation_id).first()


def get_irrigation_by_crop_id(db: Session, crop_id: int) -> Optional[IrrigationAttributes]:
    """Obtener riego de un cultivo."""
    return db.query(IrrigationAttributes).filter(IrrigationAttributes.crop_id == crop_id).first()


def get_user_irrigations(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[IrrigationAttributes], int]:
    """
    Obtener riegos de cultivos del usuario.
    Retorna (irrigations, total_count).
    """
    query = (
        db.query(IrrigationAttributes)
        .join(Crop)
        .filter(Crop.owner_id == user_id)
    )
    total = query.count()
    irrigations = query.offset(skip).limit(limit).all()
    return irrigations, total


def get_all_irrigations(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[IrrigationAttributes], int]:
    """
    Obtener todos los riegos (admin).
    Retorna (irrigations, total_count).
    """
    query = db.query(IrrigationAttributes)
    total = query.count()
    irrigations = query.offset(skip).limit(limit).all()
    return irrigations, total


def update_irrigation(
    db: Session,
    irrigation: IrrigationAttributes,
    water_frequency_days: Optional[int] = None,
    water_amount_mm: Optional[float] = None,
    irrigation_type: Optional[str] = None,
    notes: Optional[str] = None,
) -> IrrigationAttributes:
    """Actualizar riego."""
    if water_frequency_days is not None:
        irrigation.water_frequency_days = water_frequency_days
    if water_amount_mm is not None:
        irrigation.water_amount_mm = water_amount_mm
    if irrigation_type is not None:
        irrigation.irrigation_type = irrigation_type
    if notes is not None:
        irrigation.notes = notes
    db.commit()
    db.refresh(irrigation)
    return irrigation


def delete_irrigation(db: Session, irrigation: IrrigationAttributes) -> None:
    """
    Eliminar riego. No elimina el cultivo.
    """
    db.delete(irrigation)
    db.commit()


def check_irrigation_permission(
    db: Session,
    irrigation_id: int,
    current_user: User,
) -> Optional[IrrigationAttributes]:
    """
    Obtener riego y validar permisos.
    - Usuario normal solo accede a riegos de sus cultivos.
    - Admin accede a todos.
    
    Retorna irrigation si tiene permiso, None si no existe o sin permiso.
    """
    irrigation = get_irrigation_by_id(db, irrigation_id)
    if not irrigation:
        return None

    crop = irrigation.crop
    if current_user.role == UserRole.ADMIN:
        return irrigation
    
    if crop.owner_id == current_user.id:
        return irrigation
    
    return None
