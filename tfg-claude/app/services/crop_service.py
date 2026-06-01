"""
Servicio de cultivos: CRUD, validaciones, copias.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.user import User, UserRole


def create_crop(
    db: Session,
    name: str,
    description: Optional[str],
    crop_type: Optional[str],
    owner_id: int,
    is_public: bool,
    image_path: Optional[str] = None,
) -> Crop:
    """
    Crear cultivo con riego y requisitos ambientales por defecto.
    Solo admin puede crear cultivos públicos.
    """
    # Validar permisos
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise ValueError("Owner not found")

    if is_public and owner.role != UserRole.ADMIN:
        raise PermissionError("Only admin can create public crops")

    # Crear cultivo
    crop = Crop(
        name=name,
        description=description,
        crop_type=crop_type,
        owner_id=owner_id,
        is_public=is_public,
        image_path=image_path,
    )
    db.add(crop)
    db.flush()  # Obtener ID antes de commit

    # Crear datos de riego por defecto
    irrigation = IrrigationAttributes(crop_id=crop.id)
    db.add(irrigation)

    # Crear datos ambientales por defecto
    environmental = EnvironmentalRequirements(crop_id=crop.id)
    db.add(environmental)

    db.commit()
    db.refresh(crop)
    return crop


def get_crop_by_id(db: Session, crop_id: int) -> Optional[Crop]:
    """Obtener cultivo por ID."""
    return db.query(Crop).filter(Crop.id == crop_id).first()


def get_user_crops(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Crop], int]:
    """
    Obtener cultivos del usuario (incluyendo copias).
    Retorna (crops, total_count).
    """
    query = db.query(Crop).filter(Crop.owner_id == user_id)
    total = query.count()
    crops = query.offset(skip).limit(limit).all()
    return crops, total


def get_published_crops(
    db: Session,
    name_filter: Optional[str] = None,
    crop_type_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Crop], int]:
    """
    Obtener cultivos publicados (catálogo público).
    Retorna (crops, total_count).
    """
    query = db.query(Crop).filter(Crop.is_public == True)  # noqa: E712

    if name_filter:
        query = query.filter(Crop.name.ilike(f"%{name_filter}%"))

    if crop_type_filter:
        query = query.filter(Crop.crop_type.ilike(f"%{crop_type_filter}%"))

    total = query.count()
    crops = query.offset(skip).limit(limit).all()
    return crops, total


def get_user_crops_paginated(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Crop], int]:
    """
    Obtener cultivos del usuario con paginación.
    Retorna (crops, total_count).
    """
    return get_user_crops(db, user_id, skip, limit)


def get_crops_by_user_id(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Crop], int]:
    """
    Obtener cultivos públicos de un usuario.
    Retorna (crops, total_count).
    """
    query = db.query(Crop).filter(
        Crop.owner_id == user_id,
        Crop.is_public == True,  # noqa: E712
    )
    total = query.count()
    crops = query.offset(skip).limit(limit).all()
    return crops, total


def update_crop(
    db: Session,
    crop: Crop,
    name: Optional[str] = None,
    description: Optional[str] = None,
    crop_type: Optional[str] = None,
    image_path: Optional[str] = None,
) -> Crop:
    """Actualizar cultivo."""
    if name is not None:
        crop.name = name
    if description is not None:
        crop.description = description
    if crop_type is not None:
        crop.crop_type = crop_type
    if image_path is not None:
        crop.image_path = image_path

    db.commit()
    db.refresh(crop)
    return crop


def copy_crop_to_user(
    db: Session,
    source_crop_id: int,
    user_id: int,
) -> Crop:
    """
    Copiar cultivo del catálogo a "Mis cultivos" del usuario.
    La copia es independiente (source_crop_id registra el origen).
    """
    source_crop = get_crop_by_id(db, source_crop_id)
    if not source_crop:
        raise ValueError("Source crop not found")

    # Crear copia
    new_crop = Crop(
        name=source_crop.name,
        description=source_crop.description,
        crop_type=source_crop.crop_type,
        image_path=source_crop.image_path,
        owner_id=user_id,
        is_public=False,  # Copia es privada
        source_crop_id=source_crop_id,  # Registrar origen
    )
    db.add(new_crop)
    db.flush()

    # Crear datos de riego por defecto (copiar valores del original si existen)
    if source_crop.irrigation:
        irrigation = IrrigationAttributes(
            crop_id=new_crop.id,
            water_frequency_days=source_crop.irrigation.water_frequency_days,
            water_amount_mm=source_crop.irrigation.water_amount_mm,
            irrigation_type=source_crop.irrigation.irrigation_type,
            notes=source_crop.irrigation.notes,
        )
    else:
        irrigation = IrrigationAttributes(crop_id=new_crop.id)
    db.add(irrigation)

    # Crear datos ambientales por defecto (copiar valores del original si existen)
    if source_crop.environmental:
        environmental = EnvironmentalRequirements(
            crop_id=new_crop.id,
            min_temperature_celsius=source_crop.environmental.min_temperature_celsius,
            max_temperature_celsius=source_crop.environmental.max_temperature_celsius,
            min_humidity_percent=source_crop.environmental.min_humidity_percent,
            max_humidity_percent=source_crop.environmental.max_humidity_percent,
            sunlight_hours_per_day=source_crop.environmental.sunlight_hours_per_day,
            soil_type=source_crop.environmental.soil_type,
            soil_ph_min=source_crop.environmental.soil_ph_min,
            soil_ph_max=source_crop.environmental.soil_ph_max,
        )
    else:
        environmental = EnvironmentalRequirements(crop_id=new_crop.id)
    db.add(environmental)

    db.commit()
    db.refresh(new_crop)
    return new_crop


def delete_crop(db: Session, crop: Crop, current_user: User) -> None:
    """
    Eliminar cultivo.
    - Si es copia, simplemente eliminar.
    - Si es original y es público, mantenerlo (no eliminar, solo desvincular usuario).
    - Si es original y es privado, eliminar completamente.
    """
    # Si es copia, eliminar normalmente
    if crop.source_crop_id is not None:
        db.delete(crop)
        db.commit()
        return

    # Si es original
    if crop.is_public:
        # Convertir a catálogo público (desvincular usuario)
        crop.owner_id = None
        db.commit()
    else:
        # Eliminar completamente si es privado
        db.delete(crop)
        db.commit()


def get_all_crops_paginated(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Crop], int]:
    """
    Obtener todos los cultivos (admin).
    Retorna (crops, total_count).
    """
    query = db.query(Crop)
    total = query.count()
    crops = query.offset(skip).limit(limit).all()
    return crops, total
