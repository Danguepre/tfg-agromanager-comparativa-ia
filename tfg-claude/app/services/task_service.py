"""
Servicio de tareas: CRUD, validaciones, asignaciones.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.task import Task, TaskStatus
from app.models.task_crop import TaskCrop
from app.models.crop import Crop
from app.models.user import User, UserRole


def create_task(
    db: Session,
    owner_id: int,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
) -> Task:
    """Crear nueva tarea."""
    task = Task(
        owner_id=owner_id,
        title=title,
        description=description,
        due_date=due_date,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """Obtener tarea por ID."""
    return db.query(Task).filter(Task.id == task_id).first()


def get_user_tasks(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Task], int]:
    """
    Obtener tareas del usuario.
    Retorna (tasks, total_count).
    """
    query = db.query(Task).filter(Task.owner_id == user_id)
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    return tasks, total


def get_all_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Task], int]:
    """
    Obtener todas las tareas (admin).
    Retorna (tasks, total_count).
    """
    query = db.query(Task)
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    return tasks, total


def get_tasks_by_crop(
    db: Session,
    crop_id: int,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Task], int]:
    """
    Obtener tareas asociadas a un cultivo.
    Retorna (tasks, total_count).
    """
    query = (
        db.query(Task)
        .join(TaskCrop)
        .filter(TaskCrop.crop_id == crop_id)
    )
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    return tasks, total


def get_crops_by_task(
    db: Session,
    task_id: int,
) -> list[Crop]:
    """Obtener cultivos asociados a una tarea."""
    return (
        db.query(Crop)
        .join(TaskCrop)
        .filter(TaskCrop.task_id == task_id)
        .all()
    )


def assign_task_to_crop(
    db: Session,
    task_id: int,
    crop_id: int,
) -> TaskCrop:
    """
    Asignar tarea a cultivo.
    Si ya existe la relación, no duplica.
    """
    # Validar que tarea y cultivo existen
    task = db.query(Task).filter(Task.id == task_id).first()
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    
    if not task:
        raise ValueError("Task not found")
    if not crop:
        raise ValueError("Crop not found")

    # Validar que el usuario propietario de la tarea es dueño del cultivo o es admin
    # En este punto se asume que esta validación ocurrió en la ruta
    
    # Verificar si ya existe
    existing = (
        db.query(TaskCrop)
        .filter(TaskCrop.task_id == task_id, TaskCrop.crop_id == crop_id)
        .first()
    )
    if existing:
        return existing

    task_crop = TaskCrop(task_id=task_id, crop_id=crop_id)
    db.add(task_crop)
    db.commit()
    db.refresh(task_crop)
    return task_crop


def unassign_task_from_crop(
    db: Session,
    task_id: int,
    crop_id: int,
) -> None:
    """Desasignar tarea de cultivo."""
    task_crop = (
        db.query(TaskCrop)
        .filter(TaskCrop.task_id == task_id, TaskCrop.crop_id == crop_id)
        .first()
    )
    if task_crop:
        db.delete(task_crop)
        db.commit()


def update_task(
    db: Session,
    task: Task,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    status: Optional[TaskStatus] = None,
) -> Task:
    """Actualizar tarea."""
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if due_date is not None:
        task.due_date = due_date
    if status is not None:
        task.status = status
    db.commit()
    db.refresh(task)
    return task


def update_task_status(
    db: Session,
    task: Task,
    status: TaskStatus,
) -> Task:
    """Actualizar solo el estado de una tarea (PATCH)."""
    task.status = status
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    """
    Eliminar tarea.
    Las relaciones TaskCrop se eliminan en cascada por la relación del modelo.
    """
    db.delete(task)
    db.commit()


def check_task_permission(
    db: Session,
    task_id: int,
    current_user: User,
) -> Optional[Task]:
    """
    Obtener tarea y validar permisos.
    - Usuario normal solo accede a sus tareas.
    - Admin accede a todas.
    
    Retorna task si tiene permiso, None si no existe o sin permiso.
    """
    task = get_task_by_id(db, task_id)
    if not task:
        return None

    if current_user.role == UserRole.ADMIN:
        return task
    
    if task.owner_id == current_user.id:
        return task
    
    return None


def check_crop_ownership(
    db: Session,
    crop_id: int,
    current_user: User,
) -> Optional[Crop]:
    """
    Validar que el usuario es propietario del cultivo o es admin.
    Retorna crop si tiene permiso, None si no existe o sin permiso.
    """
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        return None

    if current_user.role == UserRole.ADMIN:
        return crop
    
    if crop.owner_id == current_user.id:
        return crop
    
    return None
