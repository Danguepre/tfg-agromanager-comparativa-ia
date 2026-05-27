"""Rutas para gestión de cultivos y catálogo público."""

import os
import shutil
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.crop import Crop
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.user import User
from app.schemas.crop import CropRead

router = APIRouter(prefix="/crops", tags=["crops"])

UPLOADS_CROPS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "uploads",
    "crops",
)
os.makedirs(UPLOADS_CROPS_DIR, exist_ok=True)


def _save_upload(file: UploadFile | None) -> str | None:
    """Guarda una imagen y devuelve la URL relativa, o None si no hay archivo."""
    if not file or file.filename is None or file.filename == "":
        return "/static/placeholder-crop.png"

    ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOADS_CROPS_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"/uploads/crops/{unique_name}"


def _crop_to_read(crop: Crop) -> CropRead:
    """Convierte un modelo Crop a CropRead."""
    return CropRead(
        id=crop.id,
        name=crop.name,
        scientific_name=crop.scientific_name,
        description=crop.description,
        category=crop.category,
        is_public=crop.is_public,
        owner_id=crop.owner_id,
        copied_from_id=crop.copied_from_id,
        image_url=crop.image_url,
        created_at=crop.created_at,
        updated_at=crop.updated_at,
    )


def _create_default_irrigation(crop_id: int, db: Session) -> IrrigationAttributes:
    """Crea datos de riego por defecto para un cultivo."""
    irrigation = IrrigationAttributes(
        crop_id=crop_id,
        frequency_days=7,
        water_needed_mm=25.0,
        irrigation_method="riego por goteo",
        notes="Valores por defecto — ajustar según necesidad",
    )
    db.add(irrigation)
    return irrigation


def _create_default_environmental(crop_id: int, db: Session) -> EnvironmentalRequirements:
    """Crea datos ambientales por defecto para un cultivo."""
    env = EnvironmentalRequirements(
        crop_id=crop_id,
        min_temperature=10.0,
        max_temperature=35.0,
        optimal_temperature=22.0,
        min_ph=5.5,
        max_ph=7.5,
        optimal_ph=6.5,
        sunlight_hours=6,
        humidity_percent=60.0,
        notes="Valores por defecto — ajustar según necesidad",
    )
    db.add(env)
    return env


def _get_crop_or_404(crop_id: int, db: Session) -> Crop:
    """Obtiene un cultivo por ID o lanza 404."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cultivo no encontrado",
        )
    return crop


# ──────────────────────────────────────────────
# POST /crops/ — Crear cultivo (multipart)
# ──────────────────────────────────────────────


@router.post("/", response_model=CropRead, status_code=status.HTTP_201_CREATED)
def create_crop(
    name: str = Form(...),
    scientific_name: str | None = Form(None),
    description: str | None = Form(None),
    category: str | None = Form(None),
    is_public: bool = Form(False),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un nuevo cultivo. Solo admin puede crear cultivos públicos."""
    if is_public and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden crear cultivos públicos",
        )

    image_url = _save_upload(image)

    crop = Crop(
        name=name,
        scientific_name=scientific_name,
        description=description,
        category=category,
        is_public=is_public,
        owner_id=current_user.id,
        image_url=image_url,
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)

    # Crear datos por defecto de riego y ambientales
    _create_default_irrigation(crop.id, db)
    _create_default_environmental(crop.id, db)
    db.commit()
    db.refresh(crop)

    return _crop_to_read(crop)


# ──────────────────────────────────────────────
# GET /crops/ — Listar cultivos (según rol)
# ──────────────────────────────────────────────


@router.get("/", response_model=list[CropRead])
def list_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista cultivos. Admin ve todos; usuario normal ve solo los suyos."""
    if current_user.role == "admin":
        crops = db.query(Crop).all()
    else:
        crops = db.query(Crop).filter(Crop.owner_id == current_user.id).all()
    return [_crop_to_read(c) for c in crops]


# ──────────────────────────────────────────────
# GET /crops/my — Mis cultivos
# ──────────────────────────────────────────────


@router.get("/my", response_model=list[CropRead])
def my_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Devuelve los cultivos del usuario autenticado."""
    crops = (
        db.query(Crop)
        .filter(Crop.owner_id == current_user.id)
        .all()
    )
    return [_crop_to_read(c) for c in crops]


# ──────────────────────────────────────────────
# GET /crops/published — Catálogo público
# ──────────────────────────────────────────────


@router.get("/published")
def published_crops(
    page: int = 1,
    page_size: int = 10,
    name: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """Catálogo público de cultivos publicado, con filtros y paginación."""
    query = db.query(Crop).filter(Crop.is_public == True)

    if name:
        query = query.filter(Crop.name.ilike(f"%{name}%"))
    if category:
        query = query.filter(Crop.category.ilike(f"%{category}%"))

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages)) if total > 0 else 1

    crops = (
        query.order_by(Crop.name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "items": [_crop_to_read(c) for c in crops],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


# ──────────────────────────────────────────────
# POST /crops/{crop_id}/add-to-my-crops — Copiar
# ──────────────────────────────────────────────


@router.post("/{crop_id}/add-to-my-crops", response_model=CropRead, status_code=status.HTTP_201_CREATED)
def add_to_my_crops(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Copia un cultivo del catálogo público a 'Mis cultivos'."""
    original = _get_crop_or_404(crop_id, db)

    if not original.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes añadir un cultivo no publicado",
        )

    # Crear copia independiente
    copy = Crop(
        name=original.name,
        scientific_name=original.scientific_name,
        description=original.description,
        category=original.category,
        is_public=False,
        owner_id=current_user.id,
        copied_from_id=original.id,
        image_url=original.image_url,
    )
    db.add(copy)
    db.commit()
    db.refresh(copy)

    # Copiar también riego y ambientales por defecto (valores del original)
    if original.irrigation:
        irr = IrrigationAttributes(
            crop_id=copy.id,
            frequency_days=original.irrigation.frequency_days,
            water_needed_mm=original.irrigation.water_needed_mm,
            irrigation_method=original.irrigation.irrigation_method,
            notes=original.irrigation.notes,
        )
        db.add(irr)
    else:
        _create_default_irrigation(copy.id, db)

    if original.environmental:
        env = EnvironmentalRequirements(
            crop_id=copy.id,
            min_temperature=original.environmental.min_temperature,
            max_temperature=original.environmental.max_temperature,
            optimal_temperature=original.environmental.optimal_temperature,
            min_ph=original.environmental.min_ph,
            max_ph=original.environmental.max_ph,
            optimal_ph=original.environmental.optimal_ph,
            soil_type=original.environmental.soil_type,
            sunlight_hours=original.environmental.sunlight_hours,
            humidity_percent=original.environmental.humidity_percent,
            hardiness_zone=original.environmental.hardiness_zone,
            notes=original.environmental.notes,
        )
        db.add(env)
    else:
        _create_default_environmental(copy.id, db)

    db.commit()
    db.refresh(copy)

    return _crop_to_read(copy)


# ──────────────────────────────────────────────
# GET /crops/{crop_id} — Obtener un cultivo
# ──────────────────────────────────────────────


@router.get("/{crop_id}", response_model=CropRead)
def get_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un cultivo por ID. Usuario normal solo puede ver el suyo o públicos."""
    crop = _get_crop_or_404(crop_id, db)

    if current_user.role != "admin" and crop.owner_id != current_user.id and not crop.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este cultivo",
        )

    return _crop_to_read(crop)


# ──────────────────────────────────────────────
# GET /crops/user/{user_id} — Cultivos por usuario
# ──────────────────────────────────────────────


@router.get("/user/{user_id}", response_model=list[CropRead])
def get_user_crops(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene los cultivos de un usuario. Admin ve todos; usuario normal solo los suyos."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los cultivos de este usuario",
        )

    crops = db.query(Crop).filter(Crop.owner_id == user_id).all()
    return [_crop_to_read(c) for c in crops]


# ──────────────────────────────────────────────
# PUT /crops/{crop_id} — Actualizar cultivo
# ──────────────────────────────────────────────


@router.put("/{crop_id}", response_model=CropRead)
def update_crop(
    crop_id: int,
    name: str | None = Form(None),
    scientific_name: str | None = Form(None),
    description: str | None = Form(None),
    category: str | None = Form(None),
    is_public: bool | None = Form(None),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un cultivo. Usuario normal solo puede modificar sus propios cultivos."""
    crop = _get_crop_or_404(crop_id, db)

    if current_user.role != "admin" and crop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este cultivo",
        )

    # Solo admin puede cambiar is_public a True
    if is_public is True and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden publicar cultivos",
        )

    if name is not None:
        crop.name = name
    if scientific_name is not None:
        crop.scientific_name = scientific_name
    if description is not None:
        crop.description = description
    if category is not None:
        crop.category = category
    if is_public is not None:
        crop.is_public = is_public

    if image and image.filename and image.filename != "":
        crop.image_url = _save_upload(image)

    db.commit()
    db.refresh(crop)
    return _crop_to_read(crop)


# ──────────────────────────────────────────────
# DELETE /crops/{crop_id} — Eliminar cultivo
# ──────────────────────────────────────────────


@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un cultivo.

    - Si es un cultivo original del usuario (sin copied_from_id): pasa a catálogo público.
    - Si es una copia (con copied_from_id): se elimina definitivamente.
    - Admin puede forzar la eliminación definitiva.
    """
    crop = _get_crop_or_404(crop_id, db)

    is_owner = crop.owner_id == current_user.id
    is_admin = current_user.role == "admin"

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este cultivo",
        )

    # Explicitly delete related irrigation and environmental records first
    if crop.irrigation:
        db.delete(crop.irrigation)
    if crop.environmental:
        db.delete(crop.environmental)

    # Admin force-delete: siempre elimina definitivamente
    if is_admin:
        db.delete(crop)
        db.commit()
        return None

    # Usuario propietario
    if crop.copied_from_id is not None:
        # Es una copia → eliminar definitivamente
        db.delete(crop)
        db.commit()
        return None
    else:
        # Es original → mover a catálogo público
        crop.is_public = True
        crop.owner_id = None
        db.commit()
        return None