"""
Rutas de riego: CRUD.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.irrigation import (
    IrrigationCreate,
    IrrigationUpdate,
    IrrigationResponse,
)
from app.services.irrigation_service import (
    get_irrigation_by_id,
    get_irrigation_by_crop_id,
    get_user_irrigations,
    get_all_irrigations,
    update_irrigation,
    delete_irrigation,
    check_irrigation_permission,
)

router = APIRouter(prefix="/irrigation", tags=["irrigation"])


# ============================================================================
# POST /irrigation/ - Crear riego para cultivo
# ============================================================================
@router.post("", response_model=IrrigationResponse, status_code=status.HTTP_201_CREATED)
def create_irrigation_endpoint(
    crop_id: int = Query(..., description="ID del cultivo"),
    irrigation_data: IrrigationCreate = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Crear nuevo riego para un cultivo.
    - Usuario normal solo puede crear para sus propios cultivos.
    - Admin puede crear para cualquier cultivo.
    
    Nota: El riego se crea automáticamente al crear un cultivo.
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
            detail="You can only create irrigation for your own crops",
        )

    # Verificar que no exista riego previo
    existing = get_irrigation_by_crop_id(db, crop_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Irrigation already exists for this crop",
        )

    # Crear riego
    from app.models.irrigation_attributes import IrrigationAttributes
    
    irrigation = IrrigationAttributes(
        crop_id=crop_id,
        water_frequency_days=irrigation_data.water_frequency_days if irrigation_data else None,
        water_amount_mm=irrigation_data.water_amount_mm if irrigation_data else None,
        irrigation_type=irrigation_data.irrigation_type if irrigation_data else None,
        notes=irrigation_data.notes if irrigation_data else None,
    )
    db.add(irrigation)
    db.commit()
    db.refresh(irrigation)
    return irrigation


# ============================================================================
# GET /irrigation/ - Listar riegos
# ============================================================================
@router.get("", response_model=dict)
def list_irrigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Listar riegos.
    - Usuario normal ve solo sus riegos (de sus cultivos).
    - Admin ve todos.
    """
    if current_user.role.value == "admin":
        irrigations, total = get_all_irrigations(db, skip, limit)
    else:
        irrigations, total = get_user_irrigations(db, current_user.id, skip, limit)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [IrrigationResponse.model_validate(i) for i in irrigations],
    }


# ============================================================================
# GET /irrigation/{irrigation_id} - Obtener riego por ID
# ============================================================================
@router.get("/{irrigation_id}", response_model=IrrigationResponse)
def get_irrigation_detail(
    irrigation_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener detalles de un riego.
    - Usuario normal solo accede a riegos de sus cultivos.
    - Admin accede a todos.
    """
    irrigation = check_irrigation_permission(db, irrigation_id, current_user)
    if not irrigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation not found or access denied",
        )
    return irrigation


# ============================================================================
# GET /irrigation/crop/{crop_id} - Obtener riego por cultivo
# ============================================================================
@router.get("/crop/{crop_id}", response_model=IrrigationResponse)
def get_irrigation_by_crop(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener riego de un cultivo.
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
            detail="You can only access irrigation for your own crops",
        )

    irrigation = get_irrigation_by_crop_id(db, crop_id)
    if not irrigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No irrigation found for this crop",
        )
    return irrigation


# ============================================================================
# PUT /irrigation/{irrigation_id} - Actualizar riego
# ============================================================================
@router.put("/{irrigation_id}", response_model=IrrigationResponse)
def update_irrigation_endpoint(
    irrigation_id: int,
    irrigation_data: IrrigationUpdate,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Actualizar un riego.
    - Usuario normal solo puede actualizar riegos de sus cultivos.
    - Admin puede actualizar cualquier riego.
    """
    irrigation = check_irrigation_permission(db, irrigation_id, current_user)
    if not irrigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation not found or access denied",
        )

    try:
        updated = update_irrigation(
            db=db,
            irrigation=irrigation,
            water_frequency_days=irrigation_data.water_frequency_days,
            water_amount_mm=irrigation_data.water_amount_mm,
            irrigation_type=irrigation_data.irrigation_type,
            notes=irrigation_data.notes,
        )
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# DELETE /irrigation/{irrigation_id} - Eliminar riego
# ============================================================================
@router.delete("/{irrigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_irrigation_endpoint(
    irrigation_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Eliminar un riego.
    - Usuario normal solo puede eliminar riegos de sus cultivos.
    - Admin puede eliminar cualquier riego.
    """
    irrigation = check_irrigation_permission(db, irrigation_id, current_user)
    if not irrigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Irrigation not found or access denied",
        )

    try:
        delete_irrigation(db, irrigation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
