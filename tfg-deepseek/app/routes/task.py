"""Rutas para gestión de tareas (FASE 6)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.crop import Crop
from app.models.task import Task
from app.models.task_crop import TaskCrop
from app.models.user import User
from app.schemas.crop import CropRead
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.schemas.task_crop import TaskCropCreate, TaskCropRead

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task_or_404(task_id: int, db: Session) -> Task:
    """Obtiene una tarea por ID o lanza 404."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    return task


def _verify_task_ownership(task: Task, current_user: User) -> None:
    """Verifica que el usuario sea propietario de la tarea o admin."""
    if current_user.role != "admin" and task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para gestionar esta tarea",
        )


def _verify_crop_ownership(crop: Crop, current_user: User) -> None:
    """Verifica que el usuario sea propietario del cultivo o admin."""
    if current_user.role != "admin" and crop.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para gestionar este cultivo",
        )


def _task_to_read(task: Task) -> TaskRead:
    """Convierte un modelo Task a schema de lectura."""
    return TaskRead(
        id=task.id,
        owner_id=task.owner_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        is_completed=task.is_completed,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


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


# ──────────────────────────────────────────────
# POST /tasks/ — Crear tarea
# ──────────────────────────────────────────────


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva tarea para el usuario autenticado.
    Opcionalmente puede asociarse a cultivos mediante crop_ids."""
    task = Task(
        owner_id=current_user.id,
        title=data.title,
        description=data.description,
        status=data.status,
        priority=data.priority,
        due_date=data.due_date,
    )
    # Si is_completed se envía en la creación, establecer status acorde
    if data.status == "completed":
        task.is_completed = True

    db.add(task)
    db.commit()
    db.refresh(task)

    # Si se incluyen crop_ids, asociar tarea a cultivos (solo los propios)
    if data.crop_ids:
        for crop_id in data.crop_ids:
            crop = db.query(Crop).filter(Crop.id == crop_id).first()
            if not crop:
                continue  # Ignorar cultivos inexistentes
            _verify_crop_ownership(crop, current_user)
            tc = TaskCrop(task_id=task.id, crop_id=crop_id)
            db.add(tc)
        db.commit()
        db.refresh(task)

    return _task_to_read(task)


# ──────────────────────────────────────────────
# GET /tasks/ — Listar tareas
# ──────────────────────────────────────────────


@router.get("/", response_model=list[TaskRead])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista tareas. Admin ve todas; usuario normal solo las suyas."""
    if current_user.role == "admin":
        tasks = db.query(Task).all()
    else:
        tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return [_task_to_read(t) for t in tasks]


# ──────────────────────────────────────────────
# GET /tasks/{task_id} — Obtener tarea por ID
# ──────────────────────────────────────────────


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una tarea por su ID."""
    task = _get_task_or_404(task_id, db)
    _verify_task_ownership(task, current_user)
    return _task_to_read(task)


# ──────────────────────────────────────────────
# GET /tasks/user/{user_id} — Tareas de un usuario
# ──────────────────────────────────────────────


@router.get("/user/{user_id}", response_model=list[TaskRead])
def get_user_tasks(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene las tareas de un usuario. Admin ve todos; usuario normal solo las suyas."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver las tareas de este usuario",
        )

    tasks = db.query(Task).filter(Task.owner_id == user_id).all()
    return [_task_to_read(t) for t in tasks]


# ──────────────────────────────────────────────
# GET /tasks/crop/{crop_id} — Tareas de un cultivo
# ──────────────────────────────────────────────


@router.get("/crop/{crop_id}", response_model=list[TaskRead])
def get_tasks_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene las tareas asociadas a un cultivo específico."""
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cultivo no encontrado",
        )
    _verify_crop_ownership(crop, current_user)

    # Obtener task_ids asociados a este cultivo
    tc_records = db.query(TaskCrop).filter(TaskCrop.crop_id == crop_id).all()
    task_ids = [tc.task_id for tc in tc_records]

    if not task_ids:
        return []

    tasks = db.query(Task).filter(Task.id.in_(task_ids)).all()
    return [_task_to_read(t) for t in tasks]


# ──────────────────────────────────────────────
# POST /tasks/assign — Asignar tarea a cultivo
# ──────────────────────────────────────────────


@router.post("/assign", response_model=TaskCropRead, status_code=status.HTTP_201_CREATED)
def assign_task_to_crop(
    data: TaskCropCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Asigna una tarea existente a un cultivo.
    Usuario normal solo puede asignar tareas propias a cultivos propios."""
    task = _get_task_or_404(data.task_id, db)
    _verify_task_ownership(task, current_user)

    crop = db.query(Crop).filter(Crop.id == data.crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cultivo no encontrado",
        )
    _verify_crop_ownership(crop, current_user)

    # Verificar que no exista ya la asignación
    existing = db.query(TaskCrop).filter(
        TaskCrop.task_id == data.task_id,
        TaskCrop.crop_id == data.crop_id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La tarea ya está asignada a este cultivo",
        )

    tc = TaskCrop(task_id=data.task_id, crop_id=data.crop_id)
    db.add(tc)
    db.commit()
    db.refresh(tc)

    return TaskCropRead(
        id=tc.id,
        task_id=tc.task_id,
        crop_id=tc.crop_id,
        created_at=tc.created_at,
    )


# ──────────────────────────────────────────────
# PATCH /tasks/{task_id} — Actualización parcial (estado)
# ──────────────────────────────────────────────


@router.patch("/{task_id}", response_model=TaskRead)
def patch_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza parcialmente una tarea. Usuario normal solo puede editar sus propias tareas.
    Permite cambiar estado a completed/pending y reabrir tareas completadas."""
    task = _get_task_or_404(task_id, db)
    _verify_task_ownership(task, current_user)

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status
        task.is_completed = data.status == "completed"
    if data.priority is not None:
        task.priority = data.priority
    if data.due_date is not None:
        task.due_date = data.due_date
    if data.is_completed is not None:
        task.is_completed = data.is_completed
        task.status = "completed" if data.is_completed else "pending"

    db.commit()
    db.refresh(task)
    return _task_to_read(task)


# ──────────────────────────────────────────────
# PUT /tasks/{task_id} — Actualización completa
# ──────────────────────────────────────────────


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una tarea. Usuario normal solo puede editar sus propias tareas."""
    task = _get_task_or_404(task_id, db)
    _verify_task_ownership(task, current_user)

    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status
        task.is_completed = data.status == "completed"
    if data.priority is not None:
        task.priority = data.priority
    if data.due_date is not None:
        task.due_date = data.due_date
    if data.is_completed is not None:
        task.is_completed = data.is_completed
        task.status = "completed" if data.is_completed else "pending"

    db.commit()
    db.refresh(task)
    return _task_to_read(task)


# ──────────────────────────────────────────────
# DELETE /tasks/{task_id} — Eliminar tarea (y sus relaciones)
# ──────────────────────────────────────────────


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una tarea y sus relaciones TaskCrop.
    Usuario normal solo puede eliminar sus propias tareas."""
    task = _get_task_or_404(task_id, db)
    _verify_task_ownership(task, current_user)

    # Eliminar relaciones TaskCrop primero
    db.query(TaskCrop).filter(TaskCrop.task_id == task_id).delete()
    db.delete(task)
    db.commit()
    return None


# ──────────────────────────────────────────────
# GET /tasks/{task_id}/crops — Cultivos asociados a una tarea
# ──────────────────────────────────────────────


@router.get("/{task_id}/crops", response_model=list[CropRead])
def get_task_crops(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene los cultivos asociados a una tarea."""
    task = _get_task_or_404(task_id, db)
    _verify_task_ownership(task, current_user)

    tc_records = db.query(TaskCrop).filter(TaskCrop.task_id == task_id).all()
    crop_ids = [tc.crop_id for tc in tc_records]

    if not crop_ids:
        return []

    crops = db.query(Crop).filter(Crop.id.in_(crop_ids)).all()
    return [_crop_to_read(c) for c in crops]