from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.crop import Crop
from app.schemas.environmental_requirements import (
    EnvironmentalRequirementsCreate,
    EnvironmentalRequirementsResponse
)

router = APIRouter(prefix="/environmental", tags=["Environmental"])


@router.post("/", response_model=EnvironmentalRequirementsResponse)
def create_environmental(
    data: EnvironmentalRequirementsCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user_role != "admin" and crop.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add environmental data to this crop")

    existing = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.crop_id == data.crop_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Environmental data already exists for this crop")

    env = EnvironmentalRequirements(**data.dict())

    db.add(env)
    db.commit()
    db.refresh(env)

    return env


@router.get("/", response_model=list[EnvironmentalRequirementsResponse])
def get_environmentals(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] == "admin":
        return db.query(EnvironmentalRequirements).all()
    return db.query(EnvironmentalRequirements).join(Crop).filter(Crop.user_id == current_user["user_id"]).all()


@router.get("/{env_id}", response_model=EnvironmentalRequirementsResponse)
def get_environmental(
    env_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] == "admin":
        env = db.query(EnvironmentalRequirements).filter(EnvironmentalRequirements.id == env_id).first()
    else:
        env = db.query(EnvironmentalRequirements).join(Crop).filter(
            EnvironmentalRequirements.id == env_id,
            Crop.user_id == current_user["user_id"]
        ).first()

    if not env:
        raise HTTPException(status_code=404, detail="Environmental data not found")

    return env


@router.get("/crop/{crop_id}", response_model=EnvironmentalRequirementsResponse)
def get_environmental_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view environmental data for this crop")

    env = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.crop_id == crop_id
    ).first()

    if not env:
        raise HTTPException(status_code=404, detail="Environmental data not found for this crop")

    return env


@router.put("/{env_id}", response_model=EnvironmentalRequirementsResponse)
def update_environmental(
    env_id: int,
    data: EnvironmentalRequirementsCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    env = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.id == env_id
    ).first()

    if not env:
        raise HTTPException(status_code=404, detail="Environmental data not found")

    crop = db.query(Crop).filter(Crop.id == env.crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user_role != "admin" and crop.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this environmental data")

    if current_user_role != "admin":
        new_crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
        if not new_crop or new_crop.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to assign this environmental data to another user's crop")

    env.sun_exposure = data.sun_exposure
    env.min_temp = data.min_temp
    env.max_temp = data.max_temp
    env.frost_tolerance = data.frost_tolerance
    env.crop_id = data.crop_id

    db.commit()
    db.refresh(env)

    return env


@router.delete("/{env_id}")
def delete_environmental(
    env_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    env = db.query(EnvironmentalRequirements).filter(
        EnvironmentalRequirements.id == env_id
    ).first()

    if not env:
        raise HTTPException(status_code=404, detail="Environmental data not found")

    crop = db.query(Crop).filter(Crop.id == env.crop_id).first()
    if not crop or (current_user_role != "admin" and crop.user_id != current_user_id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this environmental data")

    db.delete(env)
    db.commit()

    return {"message": "Environmental data deleted"}
