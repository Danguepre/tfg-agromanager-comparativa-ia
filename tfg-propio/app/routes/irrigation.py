from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.crop import Crop
from app.schemas.irrigation_attributes import (
    IrrigationAttributesCreate,
    IrrigationAttributesResponse
)

router = APIRouter(prefix="/irrigation", tags=["Irrigation"])


@router.post("/", response_model=IrrigationAttributesResponse)
def create_irrigation(
    data: IrrigationAttributesCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user_role != "admin" and crop.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add irrigation to this crop")

    existing = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.crop_id == data.crop_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Irrigation already exists for this crop")

    irrigation = IrrigationAttributes(**data.dict())

    db.add(irrigation)
    db.commit()
    db.refresh(irrigation)

    return irrigation


@router.get("/", response_model=list[IrrigationAttributesResponse])
def get_irrigations(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] == "admin":
        return db.query(IrrigationAttributes).all()
    return db.query(IrrigationAttributes).join(Crop).filter(Crop.user_id == current_user["user_id"]).all()


@router.get("/{irrigation_id}", response_model=IrrigationAttributesResponse)
def get_irrigation(
    irrigation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] == "admin":
        irrigation = db.query(IrrigationAttributes).filter(IrrigationAttributes.id == irrigation_id).first()
    else:
        irrigation = db.query(IrrigationAttributes).join(Crop).filter(
            IrrigationAttributes.id == irrigation_id,
            Crop.user_id == current_user["user_id"]
        ).first()

    if not irrigation:
        raise HTTPException(status_code=404, detail="Irrigation not found")

    return irrigation


@router.get("/crop/{crop_id}", response_model=IrrigationAttributesResponse)
def get_irrigation_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view irrigation for this crop")

    irrigation = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.crop_id == crop_id
    ).first()

    if not irrigation:
        raise HTTPException(status_code=404, detail="Irrigation not found for this crop")

    return irrigation


@router.put("/{irrigation_id}", response_model=IrrigationAttributesResponse)
def update_irrigation(
    irrigation_id: int,
    data: IrrigationAttributesCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    irrigation = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.id == irrigation_id
    ).first()

    if not irrigation:
        raise HTTPException(status_code=404, detail="Irrigation not found")

    crop = db.query(Crop).filter(Crop.id == irrigation.crop_id).first()
    if not crop or (current_user_role != "admin" and crop.user_id != current_user_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this irrigation")

    if current_user_role != "admin":
        new_crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
        if not new_crop or new_crop.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to assign this irrigation to another user's crop")

    irrigation.watering_frequency = data.watering_frequency
    irrigation.water_amount = data.water_amount
    irrigation.recommendations = data.recommendations
    irrigation.crop_id = data.crop_id

    db.commit()
    db.refresh(irrigation)

    return irrigation


@router.delete("/{irrigation_id}")
def delete_irrigation(
    irrigation_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    irrigation = db.query(IrrigationAttributes).filter(
        IrrigationAttributes.id == irrigation_id
    ).first()

    if not irrigation:
        raise HTTPException(status_code=404, detail="Irrigation not found")

    crop = db.query(Crop).filter(Crop.id == irrigation.crop_id).first()
    if not crop or (current_user["role"] != "admin" and crop.user_id != current_user["user_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to delete this irrigation")

    db.delete(irrigation)
    db.commit()

    return {"message": "Irrigation deleted"}