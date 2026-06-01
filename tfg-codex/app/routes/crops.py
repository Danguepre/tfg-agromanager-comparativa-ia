from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import decode_access_token
from app.models.crop import Crop, EnvironmentalRequirements, IrrigationAttributes
from app.models.planting_calendar import PlantingCalendar
from app.models.user import User
from app.schemas.crop import CropRead


router = APIRouter(prefix="/crops", tags=["crops"])

PLACEHOLDER_IMAGE_URL = "/uploads/crops/placeholder.png"
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def _is_admin(user: User) -> bool:
    return user.role == "admin"


def _ensure_can_manage_crop(user: User, crop: Crop) -> None:
    if not _is_admin(user) and crop.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def _ensure_can_view_crop(user: User, crop: Crop) -> None:
    if crop.is_public or _is_admin(user) or crop.owner_id == user.id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def _get_crop_or_404(db: Session, crop_id: int) -> Crop:
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    return crop


def _get_user_from_optional_token(db: Session, token: str | None) -> User | None:
    if token is None:
        return None

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return db.get(User, int(user_id))


def _save_crop_image(image: UploadFile | None) -> str:
    if image is None or not image.filename:
        return PLACEHOLDER_IMAGE_URL

    upload_dir = Path(settings.upload_dir) / "crops"
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(image.filename).suffix.lower()
    filename = f"{uuid4().hex}{suffix}"
    destination = upload_dir / filename

    with destination.open("wb") as buffer:
        copyfileobj(image.file, buffer)

    return f"/uploads/crops/{filename}"


def _add_default_crop_details(crop: Crop) -> None:
    crop.planting_calendar = PlantingCalendar()
    crop.irrigation_attributes = IrrigationAttributes(
        water_needs="medium",
        frequency_days=3,
        watering_frequency="every 3 days",
        water_amount="medium",
    )
    crop.environmental_requirements = EnvironmentalRequirements(
        climate="temperate",
        soil_type="well-drained",
        sun_exposure="full sun",
        frost_tolerance=False,
    )


def _copy_crop_details(source: Crop, target: Crop) -> None:
    if source.planting_calendar:
        target.planting_calendar = PlantingCalendar(
            planting_start=source.planting_calendar.planting_start,
            planting_end=source.planting_calendar.planting_end,
            transplant_start=source.planting_calendar.transplant_start,
            transplant_end=source.planting_calendar.transplant_end,
            harvest_start=source.planting_calendar.harvest_start,
            harvest_end=source.planting_calendar.harvest_end,
            is_active=False,
            current_phase_index=0,
            status="draft",
        )
    else:
        target.planting_calendar = PlantingCalendar()

    if source.irrigation_attributes:
        target.irrigation_attributes = IrrigationAttributes(
            water_needs=source.irrigation_attributes.water_needs,
            frequency_days=source.irrigation_attributes.frequency_days,
            notes=source.irrigation_attributes.notes,
            watering_frequency=source.irrigation_attributes.watering_frequency,
            water_amount=source.irrigation_attributes.water_amount,
            recommendations=source.irrigation_attributes.recommendations,
        )
    else:
        target.irrigation_attributes = IrrigationAttributes(
            water_needs="medium",
            frequency_days=3,
            watering_frequency="every 3 days",
            water_amount="medium",
        )

    if source.environmental_requirements:
        target.environmental_requirements = EnvironmentalRequirements(
            climate=source.environmental_requirements.climate,
            soil_type=source.environmental_requirements.soil_type,
            sun_exposure=source.environmental_requirements.sun_exposure,
            min_temperature_c=source.environmental_requirements.min_temperature_c,
            max_temperature_c=source.environmental_requirements.max_temperature_c,
            frost_tolerance=source.environmental_requirements.frost_tolerance,
        )
    else:
        target.environmental_requirements = EnvironmentalRequirements(
            climate="temperate",
            soil_type="well-drained",
            sun_exposure="full sun",
            frost_tolerance=False,
        )


@router.post("/", response_model=CropRead, status_code=status.HTTP_201_CREATED)
def create_crop(
    name: str = Form(...),
    crop_type: str | None = Form(None),
    description: str | None = Form(None),
    is_public: bool = Form(False),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Crop:
    if is_public and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can publish crops")

    crop = Crop(
        name=name,
        crop_type=crop_type,
        description=description,
        image_url=_save_crop_image(image),
        is_public=is_public,
        owner_id=current_user.id,
    )
    _add_default_crop_details(crop)
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router.get("/", response_model=list[CropRead])
def list_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Crop]:
    query = db.query(Crop)
    if not _is_admin(current_user):
        query = query.filter(Crop.owner_id == current_user.id)
    return query.order_by(Crop.id).all()


@router.get("/my", response_model=list[CropRead])
def list_my_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Crop]:
    return db.query(Crop).filter(Crop.owner_id == current_user.id).order_by(Crop.id).all()


@router.get("/published", response_model=list[CropRead])
def list_published_crops(
    name: str | None = Query(None),
    crop_type: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Crop]:
    query = db.query(Crop).filter(Crop.is_public.is_(True))
    if name:
        query = query.filter(Crop.name.ilike(f"%{name}%"))
    if crop_type:
        query = query.filter(Crop.crop_type.ilike(f"%{crop_type}%"))
    return query.order_by(Crop.id).offset(skip).limit(limit).all()


@router.post("/{crop_id}/add-to-my-crops", response_model=CropRead, status_code=status.HTTP_201_CREATED)
def add_to_my_crops(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Crop:
    source = _get_crop_or_404(db, crop_id)
    if not source.is_public:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only published crops can be copied")

    crop = Crop(
        name=source.name,
        crop_type=source.crop_type,
        description=source.description,
        image_url=source.image_url,
        is_public=False,
        owner_id=current_user.id,
        copied_from_crop_id=source.id,
    )
    _copy_crop_details(source, crop)
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop


@router.get("/{crop_id}", response_model=CropRead)
def get_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    token: str | None = Depends(optional_oauth2_scheme),
) -> Crop:
    crop = _get_crop_or_404(db, crop_id)
    if crop.is_public:
        return crop
    current_user = _get_user_from_optional_token(db, token)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _ensure_can_view_crop(current_user, crop)
    return crop


@router.get("/user/{user_id}", response_model=list[CropRead])
def list_user_crops(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Crop]:
    if not _is_admin(current_user) and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return db.query(Crop).filter(Crop.owner_id == user_id).order_by(Crop.id).all()


@router.put("/{crop_id}", response_model=CropRead)
def update_crop(
    crop_id: int,
    name: str | None = Form(None),
    crop_type: str | None = Form(None),
    description: str | None = Form(None),
    is_public: bool | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Crop:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)

    if is_public is True and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can publish crops")

    if name is not None:
        crop.name = name
    if crop_type is not None:
        crop.crop_type = crop_type
    if description is not None:
        crop.description = description
    if is_public is not None:
        crop.is_public = is_public
    if image is not None:
        crop.image_url = _save_crop_image(image)

    db.commit()
    db.refresh(crop)
    return crop


@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)

    if crop.copied_from_crop_id is not None:
        db.delete(crop)
    else:
        crop.is_public = True
        crop.owner_id = None
    db.commit()
