"""
Rutas de cultivos: CRUD, catálogo, copias.
"""
import os
from pathlib import Path
from typing import Annotated, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    Query,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User, UserRole
from app.models.crop import Crop
from app.schemas.crop import (
    CropCreate,
    CropResponse,
    CropDetailResponse,
    CropListResponse,
    CropUpdate,
)
from app.services.crop_service import (
    create_crop,
    get_crop_by_id,
    get_user_crops_paginated,
    get_published_crops,
    get_user_crops,
    update_crop,
    copy_crop_to_user,
    delete_crop,
    get_all_crops_paginated,
    get_crops_by_user_id,
)

router = APIRouter(prefix="/crops", tags=["crops"])

# Directorio para guardar imágenes
UPLOAD_DIR = Path("uploads/crops")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def ensure_upload_dir():
    """Crear directorio de uploads si no existe."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("", response_model=CropDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_crop_endpoint(
    name: Annotated[str, Form()],
    description: Annotated[Optional[str], Form()] = None,
    crop_type: Annotated[Optional[str], Form()] = None,
    is_public: Annotated[bool, Form()] = False,
    image: Annotated[Optional[UploadFile], File()] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Crear nuevo cultivo.
    - Multipart/form-data con imagen opcional.
    - Solo admin puede crear cultivos públicos.
    """
    ensure_upload_dir()

    # Validar que user es admin si quiere crear público
    if is_public and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create public crops",
        )

    # Procesar imagen si se proporciona
    image_path = None
    if image:
        # Validar extensión
        file_ext = Path(image.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Validar tamaño
        contents = await image.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {MAX_FILE_SIZE // 1024 // 1024}MB",
            )

        # Guardar archivo
        filename = f"{uuid4()}{file_ext}"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as f:
            f.write(contents)

        image_path = f"crops/{filename}"

    # Crear cultivo
    try:
        crop = create_crop(
            db=db,
            name=name,
            description=description,
            crop_type=crop_type,
            owner_id=current_user.id,
            is_public=is_public,
            image_path=image_path,
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Refresh para obtener relaciones completas
    db.refresh(crop)
    crop.owner = db.query(User).filter(User.id == crop.owner_id).first()
    return crop


@router.get("", response_model=CropListResponse)
def list_crops(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    name: Optional[str] = Query(None),
    crop_type: Optional[str] = Query(None),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Listar cultivos.
    - Usuario normal ve: sus cultivos + catálogo público
    - Admin ve: todos los cultivos
    """
    if current_user.role == UserRole.ADMIN:
        # Admin ve todos
        crops, total = get_all_crops_paginated(db, skip, limit)
    else:
        # User ve sus cultivos
        user_crops, user_total = get_user_crops_paginated(db, current_user.id, skip, limit)
        # Y catálogo público (con filtros si se proporcionan)
        published, published_total = get_published_crops(
            db,
            name_filter=name,
            crop_type_filter=crop_type,
            skip=0,
            limit=limit,
        )
        # Combinar (en una aplicación real, esto sería más complejo)
        crops = user_crops + published
        total = user_total + published_total

    return CropListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[CropResponse.model_validate(c) for c in crops],
    )


@router.get("/my", response_model=CropListResponse)
def list_my_crops(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener "Mis cultivos" del usuario actual.
    Incluye cultivos personales y copias del catálogo.
    """
    crops, total = get_user_crops_paginated(db, current_user.id, skip, limit)
    return CropListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[CropResponse.model_validate(c) for c in crops],
    )


@router.get("/published", response_model=CropListResponse)
def list_published_crops(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    name: Optional[str] = Query(None),
    crop_type: Optional[str] = Query(None),
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener catálogo público de cultivos.
    Con filtros opcionales por nombre y tipo.
    Paginado.
    """
    crops, total = get_published_crops(
        db,
        name_filter=name,
        crop_type_filter=crop_type,
        skip=skip,
        limit=limit,
    )
    return CropListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[CropResponse.model_validate(c) for c in crops],
    )


@router.post("/{crop_id}/add-to-my-crops", response_model=CropDetailResponse, status_code=status.HTTP_201_CREATED)
def add_crop_to_my_crops(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Copiar cultivo del catálogo a "Mis cultivos".
    Crea una copia independiente vinculada al usuario.
    """
    source_crop = get_crop_by_id(db, crop_id)
    if not source_crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    # Verificar que sea público (catálogo)
    if not source_crop.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot copy a private crop",
        )

    try:
        new_crop = copy_crop_to_user(db, crop_id, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Refresh para obtener relaciones completas
    db.refresh(new_crop)
    new_crop.owner = db.query(User).filter(User.id == new_crop.owner_id).first()
    return new_crop


@router.get("/{crop_id}", response_model=CropDetailResponse)
def get_crop_detail(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener detalles de un cultivo.
    - Usuario normal solo puede ver: sus cultivos + catálogo público
    - Admin puede ver cualquier cultivo
    """
    crop = get_crop_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    # Verificar permisos
    if crop.owner_id != current_user.id and current_user.role != UserRole.ADMIN and not crop.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this crop",
        )

    # Refresh para obtener relaciones completas
    db.refresh(crop)
    crop.owner = db.query(User).filter(User.id == crop.owner_id).first() if crop.owner_id else None
    return crop


@router.get("/user/{user_id}", response_model=CropListResponse)
def get_user_crops_endpoint(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener cultivos públicos de un usuario.
    Solo se devuelven cultivos públicos (catálogo).
    """
    crops, total = get_crops_by_user_id(db, user_id, skip, limit)
    return CropListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[CropResponse.model_validate(c) for c in crops],
    )


@router.put("/{crop_id}", response_model=CropDetailResponse)
async def update_crop_endpoint(
    crop_id: int,
    name: Annotated[Optional[str], Form()] = None,
    description: Annotated[Optional[str], Form()] = None,
    crop_type: Annotated[Optional[str], Form()] = None,
    image: Annotated[Optional[UploadFile], File()] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Actualizar cultivo.
    - Usuario normal solo puede editar sus propios cultivos
    - Admin puede editar cualquier cultivo
    - Imagen opcional
    """
    ensure_upload_dir()

    crop = get_crop_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    # Verificar permisos
    if crop.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this crop",
        )

    # Procesar imagen si se proporciona
    image_path = crop.image_path
    if image:
        # Validar extensión
        file_ext = Path(image.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Validar tamaño
        contents = await image.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {MAX_FILE_SIZE // 1024 // 1024}MB",
            )

        # Eliminar imagen anterior si existe
        if crop.image_path:
            old_path = UPLOAD_DIR / Path(crop.image_path).name
            if old_path.exists():
                old_path.unlink()

        # Guardar nueva imagen
        filename = f"{uuid4()}{file_ext}"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as f:
            f.write(contents)

        image_path = f"crops/{filename}"

    # Actualizar cultivo
    crop = update_crop(
        db=db,
        crop=crop,
        name=name,
        description=description,
        crop_type=crop_type,
        image_path=image_path,
    )

    # Refresh para obtener relaciones completas
    db.refresh(crop)
    crop.owner = db.query(User).filter(User.id == crop.owner_id).first() if crop.owner_id else None
    return crop


@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crop_endpoint(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Eliminar cultivo.
    - Usuario normal solo puede eliminar sus propios cultivos
    - Admin puede eliminar cualquier cultivo
    - Lógica especial:
      * Si es copia: eliminar normalmente
      * Si es original público: desvincular usuario (pasar a catálogo anónimo)
      * Si es original privado: eliminar completamente
    """
    crop = get_crop_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    # Verificar permisos
    if crop.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this crop",
        )

    # Eliminar imagen si existe
    if crop.image_path:
        image_path = UPLOAD_DIR / Path(crop.image_path).name
        if image_path.exists():
            image_path.unlink()

    # Eliminar cultivo (con lógica especial)
    delete_crop(db, crop, current_user)
