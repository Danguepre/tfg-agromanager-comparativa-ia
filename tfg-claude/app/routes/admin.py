"""
Rutas de administración: gestión global de usuarios, cultivos y tareas.
Solo accesibles por usuarios admin.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.admin import (
    AdminSummary,
    AdminUserResponse,
    AdminUserUpdate,
    AdminCropResponse,
    AdminCropUpdate,
    AdminTaskResponse,
    AdminTaskUpdate,
)
from app.services.admin_service import (
    get_admin_summary,
    get_admin_users,
    get_admin_user_by_id,
    update_admin_user,
    delete_admin_user,
    get_admin_crops,
    get_admin_crop_by_id,
    update_admin_crop,
    delete_admin_crop,
    get_admin_tasks,
    get_admin_task_by_id,
    update_admin_task,
    delete_admin_task,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================================
# GET /admin/summary
# ============================================================================

@router.get("/summary", response_model=AdminSummary)
def get_admin_summary_endpoint(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /admin/summary
    Obtiene resumen general del panel admin.
    Solo accesible por admin.
    Retorna totales globales de usuarios, cultivos, tareas, calendarios.
    """
    summary_data = get_admin_summary(db)
    return AdminSummary(**summary_data)


# ============================================================================
# Endpoints de usuarios
# ============================================================================

@router.get("/users", response_model=dict)
def list_admin_users(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """
    GET /admin/users
    Lista todos los usuarios (admin).
    Retorna lista paginada sin exponer passwords.
    """
    users, total = get_admin_users(db, skip, limit)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            AdminUserResponse.model_validate(user) for user in users
        ],
    }


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_admin_user_endpoint(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /admin/users/{user_id}
    Obtiene datos de un usuario específico (admin).
    No expone password.
    """
    user = get_admin_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return AdminUserResponse.model_validate(user)


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_admin_user_endpoint(
    user_id: int,
    user_update: AdminUserUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    PATCH /admin/users/{user_id}
    Actualiza datos de un usuario (admin).
    Permite actualizar name, email, is_active, role.
    No permite cambiar password desde aquí.
    """
    user = get_admin_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    updated_user = update_admin_user(
        db,
        user,
        name=user_update.name,
        email=user_update.email,
        is_active=user_update.is_active,
        role=user_update.role,
    )
    return AdminUserResponse.model_validate(updated_user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_user_endpoint(
    user_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    DELETE /admin/users/{user_id}
    Elimina un usuario (admin).
    Esto también elimina sus cultivos, tareas y calendarios.
    """
    user = get_admin_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    delete_admin_user(db, user_id)
    return None


# ============================================================================
# Endpoints de cultivos
# ============================================================================

@router.get("/crops", response_model=dict)
def list_admin_crops(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """
    GET /admin/crops
    Lista todos los cultivos (admin).
    Retorna lista paginada.
    """
    crops, total = get_admin_crops(db, skip, limit)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            AdminCropResponse.model_validate(crop) for crop in crops
        ],
    }


@router.get("/crops/{crop_id}", response_model=AdminCropResponse)
def get_admin_crop_endpoint(
    crop_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /admin/crops/{crop_id}
    Obtiene datos de un cultivo específico (admin).
    """
    crop = get_admin_crop_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )
    return AdminCropResponse.model_validate(crop)


@router.patch("/crops/{crop_id}", response_model=AdminCropResponse)
def update_admin_crop_endpoint(
    crop_id: int,
    crop_update: AdminCropUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    PATCH /admin/crops/{crop_id}
    Actualiza datos de un cultivo (admin).
    """
    crop = get_admin_crop_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    updated_crop = update_admin_crop(
        db,
        crop,
        name=crop_update.name,
        description=crop_update.description,
        crop_type=crop_update.crop_type,
        is_public=crop_update.is_public,
    )
    return AdminCropResponse.model_validate(updated_crop)


@router.delete("/crops/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_crop_endpoint(
    crop_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    DELETE /admin/crops/{crop_id}
    Elimina un cultivo (admin).
    Esto también elimina sus calendarios, riego, ambiente, tareas asociadas.
    """
    crop = get_admin_crop_by_id(db, crop_id)
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    delete_admin_crop(db, crop_id)
    return None


# ============================================================================
# Endpoints de tareas
# ============================================================================

@router.get("/tasks", response_model=dict)
def list_admin_tasks(
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """
    GET /admin/tasks
    Lista todas las tareas (admin).
    Retorna lista paginada.
    """
    tasks, total = get_admin_tasks(db, skip, limit)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            AdminTaskResponse.model_validate(task) for task in tasks
        ],
    }


@router.get("/tasks/{task_id}", response_model=AdminTaskResponse)
def get_admin_task_endpoint(
    task_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    GET /admin/tasks/{task_id}
    Obtiene datos de una tarea específica (admin).
    """
    task = get_admin_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return AdminTaskResponse.model_validate(task)


@router.patch("/tasks/{task_id}", response_model=AdminTaskResponse)
def update_admin_task_endpoint(
    task_id: int,
    task_update: AdminTaskUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    PATCH /admin/tasks/{task_id}
    Actualiza datos de una tarea (admin).
    """
    task = get_admin_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    updated_task = update_admin_task(
        db,
        task,
        title=task_update.title,
        description=task_update.description,
        status=task_update.status,
        due_date=task_update.due_date,
    )
    return AdminTaskResponse.model_validate(updated_task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_task_endpoint(
    task_id: int,
    current_admin: Annotated[User, Depends(get_current_admin)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    DELETE /admin/tasks/{task_id}
    Elimina una tarea (admin).
    """
    task = get_admin_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    delete_admin_task(db, task_id)
    return None
