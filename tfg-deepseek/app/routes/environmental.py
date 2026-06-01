"""Rutas para gestión de requisitos ambientales (FASE 6)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.crop import Crop
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.user import User
from app.schemas.environmental_requirements import (
    EnvironmentalRequirementsCreate,
    EnvironmentalRequirementsRead,
    EnvironmentalRequirementsUpdate,
)

router = APIRouter(prefix="/environmental", tags=["environmental"])


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


def _env_to_read(env: EnvironmentalRequirements) -> EnvironmentalRequirementsRead:
    """Convierte un modelo EnvironmentalRequirements a schema de lectura."""
    return EnvironmentalRequirementsRead(
        id=env.id,
        crop_id=env.crop_id,
        min_temperature=env.min_temperature,
        max_temperature=env.max_temperature,
        optimal_temperature=env.optimal_temperature,
        min_ph=env.min_ph,
        max_ph=env.max_ph,
        optimal_ph=env.optimal_ph,
        soil_type=env.soil_type,
        sunlight_hours=env.sunlight_hours,
        humidity_percent=env.humidity_percent,
        hardiness_zone=env.hardiness_zone,
        notes=env.notes,
        created_at=env.created_at,
        updated_at=env.updated_at,
    )


# ──────────────────────────────────────────────
# POST /environmental/ — Crear requisitos ambientales
# ──────────────────────────────────────────────


@router.post("/", response_model=EnvironmentalRequirementsRead, status_code=status.HTTP_201_CREATED)
def create_environmental(
    data: EnvironmentalRequirementsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea requisitos ambientales para un cultivo. Usuario normal solo para sus propios cultivos."""
    crop = _get_crop_or_404(data.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    # Verificar que no existan ya requisitos ambientales para este cultivo
    existing = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.crop_id == data.crop_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este cultivo ya tiene requisitos ambientales",
        )

    env = EnvironmentalRequirements(
        crop_id=data.crop_id,
        min_temperature=data.min_temperature,
        max_temperature=data.max_temperature,
        optimal_temperature=data.optimal_temperature,
        min_ph=data.min_ph,
        max_ph=data.max_ph,
        optimal_ph=data.optimal_ph,
        soil_type=data.soil_type,
        sunlight_hours=data.sunlight_hours,
        humidity_percent=data.humidity_percent,
        hardiness_zone=data.hardiness_zone,
        notes=data.notes,
    )
    db.add(env)
    db.commit()
    db.refresh(env)
    return _env_to_read(env)


# ──────────────────────────────────────────────
# GET /environmental/ — Listar requisitos ambientales
# ──────────────────────────────────────────────


@router.get("/", response_model=list[EnvironmentalRequirementsRead])
def list_environmental(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista requisitos ambientales. Admin ve todos; usuario normal solo los suyos."""
    if current_user.role == "admin":
        records = db.query(EnvironmentalRequirements).all()
    else:
        records = (
            db.query(EnvironmentalRequirements)
            .join(Crop, EnvironmentalRequirements.crop_id == Crop.id)
            .filter(Crop.owner_id == current_user.id)
            .all()
        )
    return [_env_to_read(r) for r in records]


# ──────────────────────────────────────────────
# GET /environmental/{env_id} — Obtener por ID
# ──────────────────────────────────────────────


@router.get("/{env_id}", response_model=EnvironmentalRequirementsRead)
def get_environmental(
    env_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene requisitos ambientales por su ID."""
    env = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.id == env_id
    ).first()
    if not env:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requisitos ambientales no encontrados",
        )

    crop = _get_crop_or_404(env.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    return _env_to_read(env)


# ──────────────────────────────────────────────
# GET /environmental/crop/{crop_id} — Obtener por cultivo
# ──────────────────────────────────────────────


@router.get("/crop/{crop_id}", response_model=EnvironmentalRequirementsRead)
def get_environmental_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene los requisitos ambientales de un cultivo específico."""
    crop = _get_crop_or_404(crop_id, db)
    _verify_crop_ownership(crop, current_user)

    env = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.crop_id == crop_id
    ).first()
    if not env:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay requisitos ambientales para este cultivo",
        )

    return _env_to_read(env)


# ──────────────────────────────────────────────
# PUT /environmental/{env_id} — Actualizar
# ──────────────────────────────────────────────


@router.put("/{env_id}", response_model=EnvironmentalRequirementsRead)
def update_environmental(
    env_id: int,
    data: EnvironmentalRequirementsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza requisitos ambientales. Usuario normal solo puede editar sus propios cultivos."""
    env = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.id == env_id
    ).first()
    if not env:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requisitos ambientales no encontrados",
        )

    crop = _get_crop_or_404(env.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    if data.min_temperature is not None:
        env.min_temperature = data.min_temperature
    if data.max_temperature is not None:
        env.max_temperature = data.max_temperature
    if data.optimal_temperature is not None:
        env.optimal_temperature = data.optimal_temperature
    if data.min_ph is not None:
        env.min_ph = data.min_ph
    if data.max_ph is not None:
        env.max_ph = data.max_ph
    if data.optimal_ph is not None:
        env.optimal_ph = data.optimal_ph
    if data.soil_type is not None:
        env.soil_type = data.soil_type
    if data.sunlight_hours is not None:
        env.sunlight_hours = data.sunlight_hours
    if data.humidity_percent is not None:
        env.humidity_percent = data.humidity_percent
    if data.hardiness_zone is not None:
        env.hardiness_zone = data.hardiness_zone
    if data.notes is not None:
        env.notes = data.notes

    db.commit()
    db.refresh(env)
    return _env_to_read(env)


# ──────────────────────────────────────────────
# DELETE /environmental/{env_id} — Eliminar
# ──────────────────────────────────────────────


@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environmental(
    env_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina requisitos ambientales. Usuario normal solo puede eliminar de sus propios cultivos."""
    env = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.id == env_id
    ).first()
    if not env:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requisitos ambientales no encontrados",
        )

    crop = _get_crop_or_404(env.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    db.delete(env)
    db.commit()
    return None