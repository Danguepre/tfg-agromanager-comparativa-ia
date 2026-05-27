"""
Rutas de tareas: CRUD, asignación a cultivos, filtros.
"""
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.models.task import TaskStatus
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskCropAssignRequest,
    CropBasicResponse,
)
from app.services.task_service import (
    create_task,
    get_task_by_id,
    get_user_tasks,
    get_all_tasks,
    get_tasks_by_crop,
    get_crops_by_task,
    assign_task_to_crop,
    unassign_task_from_crop,
    update_task,
    update_task_status,
    delete_task,
    check_task_permission,
    check_crop_ownership,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ============================================================================
# POST /tasks/ - Crear tarea
# ============================================================================
@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(
    task_data: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Crear nueva tarea.
    - Solo usuarios autenticados pueden crear tareas.
    - La tarea se asigna al usuario actual.
    - Se puede crear sin cultivo asociado.
    """
    try:
        task = create_task(
            db=db,
            owner_id=current_user.id,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
        )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# POST /tasks/assign - Asignar tarea a cultivo (ANTES DE /tasks/{task_id})
# ============================================================================
@router.post("/assign", status_code=status.HTTP_201_CREATED)
def assign_task_to_crop_endpoint(
    assign_data: TaskCropAssignRequest,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Asignar una tarea a un cultivo.
    - Usuario normal solo puede asignar sus tareas a sus cultivos.
    - Admin puede asignar cualquier tarea a cualquier cultivo.
    """
    from app.models.crop import Crop
    
    # Validar permisos sobre la tarea
    task = check_task_permission(db, assign_data.task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    # Validar que el cultivo existe
    crop = db.query(Crop).filter(Crop.id == assign_data.crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    # Validar permisos sobre el cultivo
    if current_user.role.value != "admin" and crop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only assign tasks to your own crops",
        )

    try:
        task_crop = assign_task_to_crop(db, assign_data.task_id, assign_data.crop_id)
        return {"message": "Task assigned successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# GET /tasks/ - Listar tareas
# ============================================================================
@router.get("", response_model=TaskListResponse)
def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Listar tareas.
    - Usuario normal ve solo sus tareas.
    - Admin ve todas.
    """
    if current_user.role.value == "admin":
        tasks, total = get_all_tasks(db, skip, limit)
    else:
        tasks, total = get_user_tasks(db, current_user.id, skip, limit)

    return TaskListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[TaskResponse.model_validate(t) for t in tasks],
    )


# ============================================================================
# GET /tasks/user/{user_id} - Listar tareas de un usuario
# ============================================================================
@router.get("/user/{user_id}", response_model=TaskListResponse)
def list_user_tasks(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Listar tareas de un usuario específico.
    - Usuario normal solo ve sus propias tareas.
    - Admin puede ver tareas de cualquier usuario.
    """
    # Validar permisos
    if current_user.role.value != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tasks",
        )

    tasks, total = get_user_tasks(db, user_id, skip, limit)
    return TaskListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[TaskResponse.model_validate(t) for t in tasks],
    )


# ============================================================================
# GET /tasks/crop/{crop_id} - Listar tareas de un cultivo
# ============================================================================
@router.get("/crop/{crop_id}", response_model=TaskListResponse)
def list_crop_tasks(
    crop_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Listar tareas asociadas a un cultivo.
    - Usuario normal solo ve tareas de sus cultivos.
    - Admin ve tareas de cualquier cultivo.
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
            detail="You can only view tasks for your own crops",
        )

    tasks, total = get_tasks_by_crop(db, crop_id, skip, limit)
    return TaskListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[TaskResponse.model_validate(t) for t in tasks],
    )


# ============================================================================
# GET /tasks/{task_id} - Obtener tarea por ID
# ============================================================================
@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task_detail(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Obtener detalles de una tarea con cultivos asociados.
    - Usuario normal solo accede a sus tareas.
    - Admin accede a todas.
    """
    task = check_task_permission(db, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    # Obtener cultivos asociados
    crops = get_crops_by_task(db, task_id)
    task_detail = TaskDetailResponse.model_validate(task)
    task_detail.crops = [CropBasicResponse.model_validate(c) for c in crops]
    return task_detail


# ============================================================================
# GET /tasks/{task_id}/crops - Obtener cultivos asociados a tarea
# ============================================================================
@router.get("/{task_id}/crops", response_model=list[CropBasicResponse])
def get_task_crops(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Listar cultivos asociados a una tarea.
    - Usuario normal solo accede a sus tareas.
    - Admin accede a todas.
    """
    task = check_task_permission(db, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    crops = get_crops_by_task(db, task_id)
    return [CropBasicResponse.model_validate(c) for c in crops]



# ============================================================================
# PATCH /tasks/{task_id} - Actualizar estado de tarea (cambio parcial)
# ============================================================================
@router.patch("/{task_id}", response_model=TaskResponse)
def patch_task_status(
    task_id: int,
    status_update: dict = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Actualizar estado de una tarea (PATCH).
    Permite cambiar el estado de pending a completed y viceversa.
    - Usuario normal solo puede actualizar sus tareas.
    - Admin puede actualizar cualquier tarea.
    """
    task = check_task_permission(db, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    # Obtener nuevo estado del body
    if not status_update or "status" not in status_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status field is required",
        )

    new_status_str = status_update.get("status")
    try:
        new_status = TaskStatus(new_status_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed: {[s.value for s in TaskStatus]}",
        )

    try:
        updated_task = update_task_status(db, task, new_status)
        return updated_task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# PUT /tasks/{task_id} - Actualizar tarea completa
# ============================================================================
@router.put("/{task_id}", response_model=TaskResponse)
def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Actualizar una tarea completa.
    - Usuario normal solo puede actualizar sus tareas.
    - Admin puede actualizar cualquier tarea.
    """
    task = check_task_permission(db, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    try:
        updated_task = update_task(
            db=db,
            task=task,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            status=task_data.status,
        )
        return updated_task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# DELETE /tasks/{task_id} - Eliminar tarea
# ============================================================================
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Eliminar una tarea.
    - Usuario normal solo puede eliminar sus tareas.
    - Admin puede eliminar cualquier tarea.
    - Elimina también las relaciones TaskCrop.
    """
    task = check_task_permission(db, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied",
        )

    try:
        delete_task(db, task)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
