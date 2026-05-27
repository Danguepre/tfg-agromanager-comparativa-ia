from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.crop import Crop, EnvironmentalRequirements
from app.models.user import User
from app.schemas.environmental import EnvironmentalCreate, EnvironmentalRead, EnvironmentalUpdate


router = APIRouter(prefix="/environmental", tags=["environmental"])


def _is_admin(user: User) -> bool:
    return user.role == "admin"


def _get_crop_or_404(db: Session, crop_id: int) -> Crop:
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    return crop


def _get_environmental_or_404(db: Session, env_id: int) -> EnvironmentalRequirements:
    environmental = db.get(EnvironmentalRequirements, env_id)
    if environmental is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environmental requirements not found")
    return environmental


def _ensure_can_manage_crop(user: User, crop: Crop) -> None:
    if not _is_admin(user) and crop.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def _apply_environmental_update(
    environmental: EnvironmentalRequirements,
    payload: EnvironmentalUpdate,
) -> None:
    update_data = payload.model_dump(exclude_unset=True)
    if "min_temp" in update_data:
        environmental.min_temperature_c = update_data.pop("min_temp")
    if "max_temp" in update_data:
        environmental.max_temperature_c = update_data.pop("max_temp")
    for field, value in update_data.items():
        setattr(environmental, field, value)


@router.post("/", response_model=EnvironmentalRead, status_code=status.HTTP_201_CREATED)
def create_environmental(
    payload: EnvironmentalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnvironmentalRequirements:
    crop = _get_crop_or_404(db, payload.crop_id)
    _ensure_can_manage_crop(current_user, crop)

    environmental = crop.environmental_requirements or EnvironmentalRequirements(crop_id=crop.id)
    update_payload = EnvironmentalUpdate(**payload.model_dump(exclude={"crop_id"}))
    _apply_environmental_update(environmental, update_payload)
    if crop.environmental_requirements is None:
        db.add(environmental)
    db.commit()
    db.refresh(environmental)
    return environmental


@router.get("/", response_model=list[EnvironmentalRead])
def list_environmental(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EnvironmentalRequirements]:
    query = db.query(EnvironmentalRequirements).join(Crop)
    if not _is_admin(current_user):
        query = query.filter(Crop.owner_id == current_user.id)
    return query.order_by(EnvironmentalRequirements.id).all()


@router.get("/crop/{crop_id}", response_model=EnvironmentalRead)
def get_environmental_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnvironmentalRequirements:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)
    if crop.environmental_requirements is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Environmental requirements not found")
    return crop.environmental_requirements


@router.get("/{env_id}", response_model=EnvironmentalRead)
def get_environmental(
    env_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnvironmentalRequirements:
    environmental = _get_environmental_or_404(db, env_id)
    _ensure_can_manage_crop(current_user, environmental.crop)
    return environmental


@router.put("/{env_id}", response_model=EnvironmentalRead)
def update_environmental(
    env_id: int,
    payload: EnvironmentalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnvironmentalRequirements:
    environmental = _get_environmental_or_404(db, env_id)
    _ensure_can_manage_crop(current_user, environmental.crop)
    _apply_environmental_update(environmental, payload)
    db.commit()
    db.refresh(environmental)
    return environmental


@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environmental(
    env_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    environmental = _get_environmental_or_404(db, env_id)
    _ensure_can_manage_crop(current_user, environmental.crop)
    db.delete(environmental)
    db.commit()
