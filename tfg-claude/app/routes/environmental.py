"""
Rutas de requisitos ambientales: CRUD.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.environmental import (
    EnvironmentalCreate,
    EnvironmentalUpdate,
    EnvironmentalResponse,
)
from app.services.environmental_service import (
    get_environmental_by_id,
    get_environmental_by_crop_id,
    get_user_environmentals,
    get_all_environmentals,
    update_environmental,
    delete_environmental,
    check_environmental_permission,
)

router = APIRouter(prefix="/environmental", tags=["environmental"])


# ============================================================================
# POST /environmental/ - Crear requisitos ambientales para cultivo
# ============================================================================
@router.post("", response_model=EnvironmentalResponse, status_code=status.HTTP_201_CREATED)
def create_environmental_endpoint(
    crop_id: int = Query(..., description="ID del cultivo"),
    env_data: EnvironmentalCreate = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Crear nuevos requisitos ambientales para un cultivo.
    - Usuario normal solo puede crear para sus propios cultivos.
    - Admin puede crear para cualquier cultivo.
    
    Nota: Los requisitos se crean automáticamente al crear un cultivo.
    Este endpoint es para actualizar/recrear si es necesario.
    """
    # Validar que el cultivo existe y que el usuario tiene permiso
    from app.models.crop import Crop
    
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    # Validar permisos
    if current_user.role.value != "admin" and crop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create environmental requirements for your own crops",
        )

    # Verificar que no exista requisito previo
    existing = get_environmental_by_crop_id(db, crop_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Environmental requirements already exist for this crop",
        )

    # Crear requisitos ambientales
    from app.models.environmental_requirements import EnvironmentalRequirements
    
    environmental = EnvironmentalRequirements(
        crop_id=crop_id,
        min_temperature_celsius=env_data.min_temperature_celsius if env_data else None,
        max_temperature_celsius=env_data.max_temperature_celsius if env_data else None,
        min_humidity_percent=env_data.min_humidity_percent if env_data else None,
        max_humidity_percent=env_data.max_humidity_percent if env_data else None,
        sunlight_hours_per_day=env_data.sunlight_hours_per_day if env_data else None,
        soil_type=env_data.soil_type if env_data else None,
        soil_ph_min=env_data.soil_ph_min if env_data else None,
        soil_ph_max=env_data.soil_ph_max if env_data else None,
    )
    db.add(environmental)
    db.commit()
    db.refresh(environmental)
    return environmental


# ============================================================================
# GET /environmental/ - Listar requisitos ambientales
# ============================================================================
@router.get("", response_model=dict)
def list_environmentals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Listar requisitos ambientales.
    - Usuario normal ve solo los de sus cultivos.
    - Admin ve todos.
    """
    if current_user.role.value == "admin":
        environmentals, total = get_all_environmentals(db, skip, limit)
    else:
        environmentals, total = get_user_environmentals(db, current_user.id, skip, limit)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [EnvironmentalResponse.model_validate(e) for e in environmentals],
    }


# ============================================================================
# GET /environmental/{env_id} - Obtener requisitos ambientales por ID
# ============================================================================
@router.get("/{env_id}", response_model=EnvironmentalResponse)
def get_environmental_detail(
    env_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener detalles de requisitos ambientales.
    - Usuario normal solo accede a los de sus cultivos.
    - Admin accede a todos.
    """
    environmental = check_environmental_permission(db, env_id, current_user)
    if not environmental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environmental requirements not found or access denied",
        )
    return environmental


# ============================================================================
# GET /environmental/crop/{crop_id} - Obtener requisitos ambientales por cultivo
# ============================================================================
@router.get("/crop/{crop_id}", response_model=EnvironmentalResponse)
def get_environmental_by_crop(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener requisitos ambientales de un cultivo.
    - Usuario normal solo accede a sus cultivos.
    - Admin accede a todos.
    """
    # Validar que el cultivo existe y permisos
    from app.models.crop import Crop
    
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    if current_user.role.value != "admin" and crop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access environmental requirements for your own crops",
        )

    environmental = get_environmental_by_crop_id(db, crop_id)
    if not environmental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No environmental requirements found for this crop",
        )
    return environmental


# ============================================================================
# PUT /environmental/{env_id} - Actualizar requisitos ambientales
# ============================================================================
@router.put("/{env_id}", response_model=EnvironmentalResponse)
def update_environmental_endpoint(
    env_id: int,
    env_data: EnvironmentalUpdate,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Actualizar requisitos ambientales.
    - Usuario normal solo puede actualizar los de sus cultivos.
    - Admin puede actualizar cualquiera.
    """
    environmental = check_environmental_permission(db, env_id, current_user)
    if not environmental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environmental requirements not found or access denied",
        )

    try:
        updated = update_environmental(
            db=db,
            environmental=environmental,
            min_temperature_celsius=env_data.min_temperature_celsius,
            max_temperature_celsius=env_data.max_temperature_celsius,
            min_humidity_percent=env_data.min_humidity_percent,
            max_humidity_percent=env_data.max_humidity_percent,
            sunlight_hours_per_day=env_data.sunlight_hours_per_day,
            soil_type=env_data.soil_type,
            soil_ph_min=env_data.soil_ph_min,
            soil_ph_max=env_data.soil_ph_max,
        )
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# DELETE /environmental/{env_id} - Eliminar requisitos ambientales
# ============================================================================
@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_environmental_endpoint(
    env_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Eliminar requisitos ambientales.
    - Usuario normal solo puede eliminar los de sus cultivos.
    - Admin puede eliminar cualquiera.
    """
    environmental = check_environmental_permission(db, env_id, current_user)
    if not environmental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environmental requirements not found or access denied",
        )

    try:
        delete_environmental(db, environmental)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
