from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.auth import hash_password
from app.database import get_db
from app.dependencies import get_current_user
from app.models.crop import Crop
from app.models.cultivation_guide import CultivationGuide
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.planting_calendar import PlantingCalendar
from app.models.task_crop import TaskCrop
from app.models.user import User
from app.schemas.admin import (
    AdminCropPayload,
    AdminSummaryResponse,
    AdminUserCreate,
    AdminUserUpdate,
    PaginatedCropsResponse,
    PaginatedUsersResponse,
)
from app.schemas.crop import CropResponse
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def paginate(total: int, page: int, page_size: int) -> tuple[int, int]:
    total_pages = max((total + page_size - 1) // page_size, 1)
    current_page = min(page, total_pages)
    return current_page, total_pages


def ensure_user_exists(db: Session, user_id: int | None):
    if user_id is None:
        return
    if not db.query(User.id).filter(User.id == user_id).first():
        raise HTTPException(status_code=400, detail="User owner does not exist")


def ensure_source_crop_exists(db: Session, source_crop_id: int | None, crop_id: int | None = None):
    if source_crop_id is None:
        return
    query = db.query(Crop.id).filter(Crop.id == source_crop_id)
    if crop_id is not None:
        query = query.filter(Crop.id != crop_id)
    if not query.first():
        raise HTTPException(status_code=400, detail="Source crop does not exist")


def apply_crop_payload(db: Session, crop: Crop, payload: AdminCropPayload):
    ensure_user_exists(db, payload.user_id)
    ensure_source_crop_exists(db, payload.source_crop_id, crop.id)

    crop.name = payload.name.strip()
    crop.type = payload.type.strip()
    crop.life_cycle = payload.life_cycle.strip()
    crop.image_url = payload.image_url
    crop.user_id = payload.user_id
    crop.is_public = payload.is_public
    crop.source_crop_id = payload.source_crop_id

    if payload.irrigation:
        irrigation = crop.irrigation or IrrigationAttributes(crop_id=crop.id)
        irrigation.watering_frequency = payload.irrigation.watering_frequency
        irrigation.water_amount = payload.irrigation.water_amount
        irrigation.recommendations = payload.irrigation.recommendations
        db.add(irrigation)

    if payload.environmental:
        environmental = crop.environmental or EnvironmentalRequirements(crop_id=crop.id)
        environmental.sun_exposure = payload.environmental.sun_exposure
        environmental.min_temp = payload.environmental.min_temp
        environmental.max_temp = payload.environmental.max_temp
        environmental.frost_tolerance = payload.environmental.frost_tolerance
        db.add(environmental)

    if payload.calendar:
        calendar = crop.calendar or PlantingCalendar(crop_id=crop.id)
        calendar.planting_start = payload.calendar.planting_start
        calendar.planting_end = payload.calendar.planting_end
        calendar.transplant_start = payload.calendar.transplant_start
        calendar.transplant_end = payload.calendar.transplant_end
        calendar.harvest_start = payload.calendar.harvest_start
        calendar.harvest_end = payload.calendar.harvest_end
        calendar.is_active = payload.calendar.is_active
        calendar.current_phase_index = payload.calendar.current_phase_index
        calendar.status = payload.calendar.status
        db.add(calendar)


def delete_crop_and_related(db: Session, crop_id: int):
    db.query(Crop).filter(Crop.source_crop_id == crop_id).update(
        {Crop.source_crop_id: None},
        synchronize_session=False,
    )
    db.query(TaskCrop).filter(TaskCrop.crop_id == crop_id).delete(synchronize_session=False)
    db.query(CultivationGuide).filter(CultivationGuide.crop_id == crop_id).delete(synchronize_session=False)
    db.query(PlantingCalendar).filter(PlantingCalendar.crop_id == crop_id).delete(synchronize_session=False)
    db.query(EnvironmentalRequirements).filter(EnvironmentalRequirements.crop_id == crop_id).delete(synchronize_session=False)
    db.query(IrrigationAttributes).filter(IrrigationAttributes.crop_id == crop_id).delete(synchronize_session=False)
    db.query(Crop).filter(Crop.id == crop_id).delete(synchronize_session=False)


@router.get("/summary", response_model=AdminSummaryResponse)
def get_admin_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    return {
        "total_users": db.query(User).count(),
        "total_crops": db.query(Crop).count(),
        "catalog_crops": db.query(Crop).filter(Crop.is_public.is_(True)).count(),
        "user_crops": db.query(Crop).filter(Crop.user_id.isnot(None)).count(),
    }


@router.get("/users", response_model=PaginatedUsersResponse)
def list_admin_users(
    search: str | None = Query(None),
    role: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    query = db.query(User)

    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(User.name.ilike(term), User.email.ilike(term)))
    if role in {"user", "admin"}:
        query = query.filter(User.role == role)

    total = query.count()
    current_page, total_pages = paginate(total, page, page_size)
    users = query.order_by(User.id).offset((current_page - 1) * page_size).limit(page_size).all()

    return {"items": users, "total": total, "page": current_page, "page_size": page_size, "total_pages": total_pages}


@router.post("/users", response_model=UserResponse)
def create_admin_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(
        name=payload.name.strip(),
        email=payload.email,
        password=hash_password(payload.password),
        location=payload.location,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_admin_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    email_owner = db.query(User).filter(User.email == payload.email, User.id != user_id).first()
    if email_owner:
        raise HTTPException(status_code=400, detail="Email already exists")

    if user.role == "admin" and payload.role != "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last admin")

    user.name = payload.name.strip()
    user.email = payload.email
    user.location = payload.location
    user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
def delete_admin_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    if user_id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Admins cannot delete their own user")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "admin" and db.query(User).filter(User.role == "admin").count() <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last admin")

    db.query(Crop).filter(Crop.user_id == user_id).update({Crop.user_id: None}, synchronize_session=False)
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}


@router.get("/crops", response_model=PaginatedCropsResponse)
def list_admin_crops(
    name: str | None = Query(None),
    type: str | None = Query(None),
    user_id: int | None = Query(None),
    kind: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    available_types = [
        row[0]
        for row in db.query(Crop.type)
        .filter(Crop.type.isnot(None), Crop.type != "")
        .distinct()
        .order_by(Crop.type)
        .all()
    ]

    query = db.query(Crop).options(
        joinedload(Crop.irrigation),
        joinedload(Crop.environmental),
        joinedload(Crop.calendar),
    )

    if name:
        query = query.filter(Crop.name.ilike(f"%{name.strip()}%"))
    if type:
        query = query.filter(Crop.type == type.strip())
    if user_id is not None:
        query = query.filter(Crop.user_id == user_id)
    if kind == "catalog":
        query = query.filter(Crop.is_public.is_(True))
    elif kind == "user":
        query = query.filter(Crop.user_id.isnot(None), Crop.source_crop_id.is_(None))
    elif kind == "copy":
        query = query.filter(Crop.source_crop_id.isnot(None))
    elif kind == "global":
        query = query.filter(Crop.user_id.is_(None), Crop.source_crop_id.is_(None))

    total = query.count()
    current_page, total_pages = paginate(total, page, page_size)
    crops = query.order_by(Crop.id.desc()).offset((current_page - 1) * page_size).limit(page_size).all()

    return {
        "items": crops,
        "total": total,
        "page": current_page,
        "page_size": page_size,
        "total_pages": total_pages,
        "types": available_types,
    }


@router.post("/crops", response_model=CropResponse)
def create_admin_crop(
    payload: AdminCropPayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    ensure_user_exists(db, payload.user_id)
    ensure_source_crop_exists(db, payload.source_crop_id)

    crop = Crop(
        name=payload.name.strip(),
        type=payload.type.strip(),
        life_cycle=payload.life_cycle.strip(),
        image_url=payload.image_url,
        user_id=payload.user_id,
        is_public=payload.is_public,
        source_crop_id=payload.source_crop_id,
    )
    db.add(crop)
    db.flush()
    apply_crop_payload(db, crop, payload)
    db.commit()
    db.refresh(crop)
    return crop


@router.put("/crops/{crop_id}", response_model=CropResponse)
def update_admin_crop(
    crop_id: int,
    payload: AdminCropPayload,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    crop = db.query(Crop).options(
        joinedload(Crop.irrigation),
        joinedload(Crop.environmental),
        joinedload(Crop.calendar),
    ).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    apply_crop_payload(db, crop, payload)
    db.commit()
    db.refresh(crop)
    return crop


@router.delete("/crops/{crop_id}")
def delete_admin_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    delete_crop_and_related(db, crop_id)
    db.commit()
    return {"message": "Crop deleted"}
