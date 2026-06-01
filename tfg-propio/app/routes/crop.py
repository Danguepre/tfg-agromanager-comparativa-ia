from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.cultivation_guide import CultivationGuide
from app.models.crop import Crop
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.planting_calendar import PlantingCalendar
from app.models.task_crop import TaskCrop
from app.models.user import User
from app.schemas.crop import CropCatalogResponse, CropCreate, CropResponse
from app.services.image_search import fetch_and_store_crop_image, save_uploaded_crop_image

router = APIRouter(prefix="/crops", tags=["Crops"])


def get_catalog_source_id(crop: Crop) -> int:
    return crop.source_crop_id or crop.id


def get_user_catalog_source_ids(db: Session, user_id: int) -> set[int]:
    user_crops = db.query(Crop).filter(Crop.user_id == user_id).all()
    return {get_catalog_source_id(crop) for crop in user_crops}


@router.post("/", response_model=CropResponse)
def create_crop(
    name: str = Form(...),
    type: str = Form(...),
    life_cycle: str = Form(...),
    user_id: int = Form(...),
    is_public: bool = Form(False),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    if current_user_role != "admin" and user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot create crop for another user")
    if current_user_role != "admin" and is_public:
        raise HTTPException(status_code=403, detail="Only admins can publish crops")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        if image:
            image_url = save_uploaded_crop_image(image)
        else:
            image_url = fetch_and_store_crop_image(name, type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    new_crop = Crop(
        name=name,
        type=type,
        life_cycle=life_cycle,
        image_url=image_url,
        user_id=user_id,
        is_public=is_public,
    )

    db.add(new_crop)
    db.commit()
    db.refresh(new_crop)

    irrigation = IrrigationAttributes(
        crop_id=new_crop.id,
        watering_frequency="daily",
        water_amount=1.0,
        recommendations="Riego diario moderado"
    )
    db.add(irrigation)

    environmental = EnvironmentalRequirements(
        crop_id=new_crop.id,
        sun_exposure="full_sun",
        min_temp=15.0,
        max_temp=30.0,
        frost_tolerance=False
    )
    db.add(environmental)

    db.commit()
    db.refresh(new_crop)
    return new_crop


@router.get("/published", response_model=CropCatalogResponse)
def get_published_crops(
    name: str | None = Query(None, min_length=1),
    type: str | None = Query(None, min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_source_ids = get_user_catalog_source_ids(db, current_user["user_id"])

    available_types = [
        row[0]
        for row in db.query(Crop.type)
        .filter(Crop.type.isnot(None), Crop.type != "")
        .distinct()
        .order_by(Crop.type)
        .all()
    ]

    query = db.query(Crop)

    if name:
        query = query.filter(Crop.name.ilike(f"%{name.strip()}%"))

    if type:
        query = query.filter(Crop.type == type.strip())

    total = query.count()
    total_pages = max((total + page_size - 1) // page_size, 1)
    current_page = min(page, total_pages)

    crops = query.options(
        joinedload(Crop.irrigation),
        joinedload(Crop.environmental),
        joinedload(Crop.calendar),
    ).order_by(Crop.name, Crop.id).offset((current_page - 1) * page_size).limit(page_size).all()

    for crop in crops:
        crop.added_to_my_crops = get_catalog_source_id(crop) in user_source_ids

    return {
        "items": crops,
        "total": total,
        "page": current_page,
        "page_size": page_size,
        "total_pages": total_pages,
        "types": available_types,
    }


@router.get("/my", response_model=CropCatalogResponse)
def get_my_crops(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]

    query = db.query(Crop).options(
        joinedload(Crop.irrigation),
        joinedload(Crop.environmental),
        joinedload(Crop.calendar),
    ).filter(Crop.user_id == current_user_id)

    total = query.count()
    total_pages = max((total + page_size - 1) // page_size, 1)
    current_page = min(page, total_pages)

    crops = query.order_by(Crop.id.desc()).offset((current_page - 1) * page_size).limit(page_size).all()

    return {
        "items": crops,
        "total": total,
        "page": current_page,
        "page_size": page_size,
        "total_pages": total_pages,
        "types": [],
    }


@router.post("/{crop_id}/add-to-my-crops", response_model=CropResponse)
def add_published_crop_to_my_crops(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]

    source_crop = db.query(Crop).options(
        joinedload(Crop.irrigation),
        joinedload(Crop.environmental),
        joinedload(Crop.calendar),
        joinedload(Crop.guides),
    ).filter(Crop.id == crop_id).first()

    if not source_crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    source_id = get_catalog_source_id(source_crop)
    already_added = db.query(Crop).filter(
        Crop.user_id == current_user_id,
        or_(
            Crop.id == source_id,
            Crop.source_crop_id == source_id,
        ),
    ).first()

    if already_added:
        raise HTTPException(status_code=400, detail="Este cultivo ya esta en tus cultivos")

    new_crop = Crop(
        name=source_crop.name,
        type=source_crop.type,
        life_cycle=source_crop.life_cycle,
        image_url=source_crop.image_url,
        user_id=current_user_id,
        is_public=False,
        source_crop_id=source_id,
    )
    db.add(new_crop)
    db.flush()

    if source_crop.irrigation:
        db.add(IrrigationAttributes(
            crop_id=new_crop.id,
            watering_frequency=source_crop.irrigation.watering_frequency,
            water_amount=source_crop.irrigation.water_amount,
            recommendations=source_crop.irrigation.recommendations,
        ))

    if source_crop.environmental:
        db.add(EnvironmentalRequirements(
            crop_id=new_crop.id,
            sun_exposure=source_crop.environmental.sun_exposure,
            min_temp=source_crop.environmental.min_temp,
            max_temp=source_crop.environmental.max_temp,
            frost_tolerance=source_crop.environmental.frost_tolerance,
        ))

    if source_crop.calendar:
        db.add(PlantingCalendar(
            crop_id=new_crop.id,
            planting_start=source_crop.calendar.planting_start,
            planting_end=source_crop.calendar.planting_end,
            transplant_start=source_crop.calendar.transplant_start,
            transplant_end=source_crop.calendar.transplant_end,
            harvest_start=source_crop.calendar.harvest_start,
            harvest_end=source_crop.calendar.harvest_end,
        ))

    for guide in source_crop.guides:
        db.add(CultivationGuide(
            crop_id=new_crop.id,
            step_number=guide.step_number,
            description=guide.description,
        ))

    db.commit()
    db.refresh(new_crop)
    return new_crop


@router.get("/", response_model=list[CropResponse])
def get_crops(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    query = db.query(Crop).options(
        joinedload(Crop.irrigation),
        joinedload(Crop.environmental),
        joinedload(Crop.calendar),
    )

    if current_user_role == "admin":
        return query.all()

    return query.filter(Crop.user_id == current_user_id).all()


@router.get("/{crop_id}", response_model=CropResponse)
def get_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    crop = db.query(Crop).options(
        joinedload(Crop.irrigation),
        joinedload(Crop.environmental),
        joinedload(Crop.calendar),
    ).filter(Crop.id == crop_id).first()

    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user_role != "admin" and crop.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this crop")

    return crop


@router.get("/user/{user_id}", response_model=list[CropResponse])
def get_crops_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    if current_user_role != "admin" and user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view crops for this user")

    return db.query(Crop).options(
        joinedload(Crop.irrigation),
        joinedload(Crop.environmental),
        joinedload(Crop.calendar),
    ).filter(Crop.user_id == user_id).all()


@router.put("/{crop_id}", response_model=CropResponse)
def update_crop(
    crop_id: int,
    updated_crop: CropCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    crop = db.query(Crop).filter(Crop.id == crop_id).first()

    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user_role != "admin" and crop.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this crop")
    if current_user_role != "admin" and updated_crop.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Cannot reassign crop to another user")

    crop.name = updated_crop.name
    crop.type = updated_crop.type
    crop.life_cycle = updated_crop.life_cycle
    crop.image_url = updated_crop.image_url
    crop.user_id = updated_crop.user_id
    if current_user_role == "admin":
        crop.is_public = updated_crop.is_public
        crop.source_crop_id = updated_crop.source_crop_id

    db.commit()
    db.refresh(crop)

    return crop


@router.delete("/{crop_id}")
def delete_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]
    current_user_role = current_user["role"]

    crop = db.query(Crop).filter(Crop.id == crop_id).first()

    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    if current_user_role != "admin" and crop.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this crop")

    if crop.source_crop_id is None:
        crop.user_id = None
        crop.is_public = True
        db.query(TaskCrop).filter(TaskCrop.crop_id == crop_id).delete(synchronize_session=False)
        db.commit()
        return {"message": "Crop removed from my crops"}

    db.query(Crop).filter(Crop.source_crop_id == crop_id).update(
        {Crop.source_crop_id: None},
        synchronize_session=False,
    )
    db.query(TaskCrop).filter(TaskCrop.crop_id == crop_id).delete(synchronize_session=False)
    db.query(CultivationGuide).filter(CultivationGuide.crop_id == crop_id).delete(synchronize_session=False)
    db.query(PlantingCalendar).filter(PlantingCalendar.crop_id == crop_id).delete(synchronize_session=False)
    db.query(EnvironmentalRequirements).filter(EnvironmentalRequirements.crop_id == crop_id).delete(synchronize_session=False)
    db.query(IrrigationAttributes).filter(IrrigationAttributes.crop_id == crop_id).delete(synchronize_session=False)

    db.delete(crop)
    db.commit()

    return {"message": "Crop deleted"}
