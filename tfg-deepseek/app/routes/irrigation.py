"""Rutas para gestión de riego (FASE 6)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.crop import Crop
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.user import User
from app.schemas.irrigation_attributes import (
    IrrigationAttributesCreate,
    IrrigationAttributesRead,
    IrrigationAttributesUpdate,
)

router = APIRouter(prefix="/irrigation", tags=["irrigation"])


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


def _irrigation_to_read(irr: IrrigationAttributes) -> IrrigationAttributesRead:
    """Convierte un modelo IrrigationAttributes a schema de lectura."""
    return IrrigationAttributesRead(
        id=irr.id,
        crop_id=irr.crop_id,
        frequency_days=irr.frequency_days,
        water_needed_mm=irr.water_needed_mm,
        irrigation_method=irr.irrigation_method,
        notes=irr.notes,
        created_at=irr.created_at,
        updated_at=irr.updated_at,
    )


# ──────────────────────────────────────────────
# POST /irrigation/ — Crear riego
# ──────────────────────────────────────────────


@router.post("/", response_model=IrrigationAttributesRead, status_code=status.HTTP_201_CREATED)
def create_irrigation(
    data: IrrigationAttributesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea atributos de riego para un cultivo. Usuario normal solo para sus propios cultivos."""
    crop = _get_crop_or_404(data.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    # Verificar que no exista ya riego para este cultivo
    existing = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.crop_id == data.crop_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este cultivo ya tiene configuración de riego",
        )

    irr = IrrigationAttributes(
        crop_id=data.crop_id,
        frequency_days=data.frequency_days,
        water_needed_mm=data.water_needed_mm,
        irrigation_method=data.irrigation_method,
        notes=data.notes,
    )
    db.add(irr)
    db.commit()
    db.refresh(irr)
    return _irrigation_to_read(irr)


# ──────────────────────────────────────────────
# GET /irrigation/ — Listar riegos
# ──────────────────────────────────────────────


@router.get("/", response_model=list[IrrigationAttributesRead])
def list_irrigation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista configuraciones de riego. Admin ve todos; usuario normal solo los suyos."""
    if current_user.role == "admin":
        records = db.query(IrrigationAttributes).all()
    else:
        records = (
            db.query(IrrigationAttributes)
            .join(Crop, IrrigationAttributes.crop_id == Crop.id)
            .filter(Crop.owner_id == current_user.id)
            .all()
        )
    return [_irrigation_to_read(r) for r in records]


# ──────────────────────────────────────────────
# GET /irrigation/{irrigation_id} — Obtener por ID
# ──────────────────────────────────────────────


@router.get("/{irrigation_id}", response_model=IrrigationAttributesRead)
def get_irrigation(
    irrigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una configuración de riego por su ID."""
    irr = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.id == irrigation_id
    ).first()
    if not irr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración de riego no encontrada",
        )

    crop = _get_crop_or_404(irr.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    return _irrigation_to_read(irr)


# ──────────────────────────────────────────────
# GET /irrigation/crop/{crop_id} — Obtener por cultivo
# ──────────────────────────────────────────────


@router.get("/crop/{crop_id}", response_model=IrrigationAttributesRead)
def get_irrigation_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene la configuración de riego de un cultivo específico."""
    crop = _get_crop_or_404(crop_id, db)
    _verify_crop_ownership(crop, current_user)

    irr = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.crop_id == crop_id
    ).first()
    if not irr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay configuración de riego para este cultivo",
        )

    return _irrigation_to_read(irr)


# ──────────────────────────────────────────────
# PUT /irrigation/{irrigation_id} — Actualizar
# ──────────────────────────────────────────────


@router.put("/{irrigation_id}", response_model=IrrigationAttributesRead)
def update_irrigation(
    irrigation_id: int,
    data: IrrigationAttributesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una configuración de riego. Usuario normal solo puede editar sus propios cultivos."""
    irr = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.id == irrigation_id
    ).first()
    if not irr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración de riego no encontrada",
        )

    crop = _get_crop_or_404(irr.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    if data.frequency_days is not None:
        irr.frequency_days = data.frequency_days
    if data.water_needed_mm is not None:
        irr.water_needed_mm = data.water_needed_mm
    if data.irrigation_method is not None:
        irr.irrigation_method = data.irrigation_method
    if data.notes is not None:
        irr.notes = data.notes

    db.commit()
    db.refresh(irr)
    return _irrigation_to_read(irr)


# ──────────────────────────────────────────────
# DELETE /irrigation/{irrigation_id} — Eliminar
# ──────────────────────────────────────────────


@router.delete("/{irrigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_irrigation(
    irrigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una configuración de riego. Usuario normal solo puede eliminar de sus propios cultivos."""
    irr = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.id == irrigation_id
    ).first()
    if not irr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración de riego no encontrada",
        )

    crop = _get_crop_or_404(irr.crop_id, db)
    _verify_crop_ownership(crop, current_user)

    db.delete(irr)
    db.commit()
    return None