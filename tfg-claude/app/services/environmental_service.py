"""
Servicio de requisitos ambientales: CRUD, validaciones.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.crop import Crop
from app.models.user import User, UserRole


def get_environmental_by_id(db: Session, env_id: int) -> Optional[EnvironmentalRequirements]:
    """Obtener requisitos ambientales por ID."""
    return (
        db.query(EnvironmentalRequirements)
        .filter(EnvironmentalRequirements.id == env_id)
        .first()
    )


def get_environmental_by_crop_id(db: Session, crop_id: int) -> Optional[EnvironmentalRequirements]:
    """Obtener requisitos ambientales de un cultivo."""
    return (
        db.query(EnvironmentalRequirements)
        .filter(EnvironmentalRequirements.crop_id == crop_id)
        .first()
    )


def get_user_environmentals(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[EnvironmentalRequirements], int]:
    """
    Obtener requisitos de cultivos del usuario.
    Retorna (environmentals, total_count).
    """
    query = (
        db.query(EnvironmentalRequirements)
        .join(Crop)
        .filter(Crop.owner_id == user_id)
    )
    total = query.count()
    environmentals = query.offset(skip).limit(limit).all()
    return environmentals, total


def get_all_environmentals(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[EnvironmentalRequirements], int]:
    """
    Obtener todos los requisitos (admin).
    Retorna (environmentals, total_count).
    """
    query = db.query(EnvironmentalRequirements)
    total = query.count()
    environmentals = query.offset(skip).limit(limit).all()
    return environmentals, total


def update_environmental(
    db: Session,
    environmental: EnvironmentalRequirements,
    min_temperature_celsius: Optional[float] = None,
    max_temperature_celsius: Optional[float] = None,
    min_humidity_percent: Optional[float] = None,
    max_humidity_percent: Optional[float] = None,
    sunlight_hours_per_day: Optional[float] = None,
    soil_type: Optional[str] = None,
    soil_ph_min: Optional[float] = None,
    soil_ph_max: Optional[float] = None,
) -> EnvironmentalRequirements:
    """Actualizar requisitos ambientales."""
    if min_temperature_celsius is not None:
        environmental.min_temperature_celsius = min_temperature_celsius
    if max_temperature_celsius is not None:
        environmental.max_temperature_celsius = max_temperature_celsius
    if min_humidity_percent is not None:
        environmental.min_humidity_percent = min_humidity_percent
    if max_humidity_percent is not None:
        environmental.max_humidity_percent = max_humidity_percent
    if sunlight_hours_per_day is not None:
        environmental.sunlight_hours_per_day = sunlight_hours_per_day
    if soil_type is not None:
        environmental.soil_type = soil_type
    if soil_ph_min is not None:
        environmental.soil_ph_min = soil_ph_min
    if soil_ph_max is not None:
        environmental.soil_ph_max = soil_ph_max
    db.commit()
    db.refresh(environmental)
    return environmental


def delete_environmental(db: Session, environmental: EnvironmentalRequirements) -> None:
    """
    Eliminar requisitos ambientales. No elimina el cultivo.
    """
    db.delete(environmental)
    db.commit()


def check_environmental_permission(
    db: Session,
    env_id: int,
    current_user: User,
) -> Optional[EnvironmentalRequirements]:
    """
    Obtener requisito ambiental y validar permisos.
    - Usuario normal solo accede a requisitos de sus cultivos.
    - Admin accede a todos.
    
    Retorna environmental si tiene permiso, None si no existe o sin permiso.
    """
    environmental = get_environmental_by_id(db, env_id)
    if not environmental:
        return None

    crop = environmental.crop
    if current_user.role == UserRole.ADMIN:
        return environmental
    
    if crop.owner_id == current_user.id:
        return environmental
    
    return None
