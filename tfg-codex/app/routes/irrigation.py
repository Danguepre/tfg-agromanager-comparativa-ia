from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.crop import Crop, IrrigationAttributes
from app.models.user import User
from app.schemas.irrigation import IrrigationCreate, IrrigationRead, IrrigationUpdate


router = APIRouter(prefix="/irrigation", tags=["irrigation"])


def _is_admin(user: User) -> bool:
    return user.role == "admin"


def _get_crop_or_404(db: Session, crop_id: int) -> Crop:
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    return crop


def _get_irrigation_or_404(db: Session, irrigation_id: int) -> IrrigationAttributes:
    irrigation = db.get(IrrigationAttributes, irrigation_id)
    if irrigation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Irrigation not found")
    return irrigation


def _ensure_can_manage_crop(user: User, crop: Crop) -> None:
    if not _is_admin(user) and crop.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def _apply_irrigation_update(irrigation: IrrigationAttributes, payload: IrrigationUpdate) -> None:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(irrigation, field, value)


@router.post("/", response_model=IrrigationRead, status_code=status.HTTP_201_CREATED)
def create_irrigation(
    payload: IrrigationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IrrigationAttributes:
    crop = _get_crop_or_404(db, payload.crop_id)
    _ensure_can_manage_crop(current_user, crop)

    irrigation = crop.irrigation_attributes or IrrigationAttributes(crop_id=crop.id)
    _apply_irrigation_update(irrigation, IrrigationUpdate(**payload.model_dump(exclude={"crop_id"})))
    if crop.irrigation_attributes is None:
        db.add(irrigation)
    db.commit()
    db.refresh(irrigation)
    return irrigation


@router.get("/", response_model=list[IrrigationRead])
def list_irrigation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[IrrigationAttributes]:
    query = db.query(IrrigationAttributes).join(Crop)
    if not _is_admin(current_user):
        query = query.filter(Crop.owner_id == current_user.id)
    return query.order_by(IrrigationAttributes.id).all()


@router.get("/crop/{crop_id}", response_model=IrrigationRead)
def get_irrigation_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IrrigationAttributes:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)
    if crop.irrigation_attributes is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Irrigation not found")
    return crop.irrigation_attributes


@router.get("/{irrigation_id}", response_model=IrrigationRead)
def get_irrigation(
    irrigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IrrigationAttributes:
    irrigation = _get_irrigation_or_404(db, irrigation_id)
    _ensure_can_manage_crop(current_user, irrigation.crop)
    return irrigation


@router.put("/{irrigation_id}", response_model=IrrigationRead)
def update_irrigation(
    irrigation_id: int,
    payload: IrrigationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IrrigationAttributes:
    irrigation = _get_irrigation_or_404(db, irrigation_id)
    _ensure_can_manage_crop(current_user, irrigation.crop)
    _apply_irrigation_update(irrigation, payload)
    db.commit()
    db.refresh(irrigation)
    return irrigation


@router.delete("/{irrigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_irrigation(
    irrigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    irrigation = _get_irrigation_or_404(db, irrigation_id)
    _ensure_can_manage_crop(current_user, irrigation.crop)
    db.delete(irrigation)
    db.commit()
