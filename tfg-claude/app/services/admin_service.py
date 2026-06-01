"""
Servicios para panel admin.
"""
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.crop import Crop
from app.models.task import Task, TaskStatus
from app.models.planting_calendar import PlantingCalendar, CalendarStatus
from app.services.auth_service import hash_password


def get_admin_summary(db: Session) -> dict:
    """
    Obtener resumen general para el panel admin.
    Incluye totales globales de usuarios, cultivos, tareas, etc.
    """
    total_users = db.query(User).count()
    total_crops = db.query(Crop).count()
    total_public_crops = db.query(Crop).filter(Crop.is_public == True).count()  # noqa: E712
    total_tasks = db.query(Task).count()
    total_pending_tasks = db.query(Task).filter(Task.status == TaskStatus.PENDING).count()
    total_completed_tasks = db.query(Task).filter(Task.status == TaskStatus.COMPLETED).count()
    total_active_calendars = db.query(PlantingCalendar).filter(
        PlantingCalendar.status == CalendarStatus.ACTIVE
    ).count()
    total_completed_calendars = db.query(PlantingCalendar).filter(
        PlantingCalendar.status == CalendarStatus.COMPLETED
    ).count()

    return {
        "total_users": total_users,
        "total_crops": total_crops,
        "total_public_crops": total_public_crops,
        "total_tasks": total_tasks,
        "total_pending_tasks": total_pending_tasks,
        "total_completed_tasks": total_completed_tasks,
        "total_active_calendars": total_active_calendars,
        "total_completed_calendars": total_completed_calendars,
    }


# ============================================================================
# Funciones para usuarios
# ============================================================================

def get_admin_users(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[User], int]:
    """
    Obtener lista de usuarios (admin).
    Retorna (users, total_count).
    """
    query = db.query(User)
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return users, total


def get_admin_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Obtener usuario por ID (admin).
    """
    return db.query(User).filter(User.id == user_id).first()


def update_admin_user(
    db: Session,
    user: User,
    name: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    role: Optional[UserRole] = None,
) -> User:
    """
    Actualizar usuario (admin).
    No se puede actualizar password desde aquí.
    """
    if name is not None:
        user.name = name
    if email is not None:
        user.email = email
    if is_active is not None:
        user.is_active = is_active
    if role is not None:
        user.role = role

    db.commit()
    db.refresh(user)
    return user


def delete_admin_user(db: Session, user_id: int) -> bool:
    """
    Eliminar usuario (admin).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False


# ============================================================================
# Funciones para cultivos
# ============================================================================

def get_admin_crops(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Crop], int]:
    """
    Obtener lista de cultivos (admin).
    Retorna (crops, total_count).
    """
    query = db.query(Crop)
    total = query.count()
    crops = query.offset(skip).limit(limit).all()
    return crops, total


def get_admin_crop_by_id(db: Session, crop_id: int) -> Optional[Crop]:
    """
    Obtener cultivo por ID (admin).
    """
    return db.query(Crop).filter(Crop.id == crop_id).first()


def update_admin_crop(
    db: Session,
    crop: Crop,
    name: Optional[str] = None,
    description: Optional[str] = None,
    crop_type: Optional[str] = None,
    is_public: Optional[bool] = None,
) -> Crop:
    """
    Actualizar cultivo (admin).
    """
    if name is not None:
        crop.name = name
    if description is not None:
        crop.description = description
    if crop_type is not None:
        crop.crop_type = crop_type
    if is_public is not None:
        crop.is_public = is_public

    db.commit()
    db.refresh(crop)
    return crop


def delete_admin_crop(db: Session, crop_id: int) -> bool:
    """
    Eliminar cultivo (admin).
    Esto también elimina calendarios, riego, ambiente, tareas asociadas.
    """
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if crop:
        db.delete(crop)
        db.commit()
        return True
    return False


# ============================================================================
# Funciones para tareas
# ============================================================================

def get_admin_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[list[Task], int]:
    """
    Obtener lista de tareas (admin).
    Retorna (tasks, total_count).
    """
    query = db.query(Task)
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    return tasks, total


def get_admin_task_by_id(db: Session, task_id: int) -> Optional[Task]:
    """
    Obtener tarea por ID (admin).
    """
    return db.query(Task).filter(Task.id == task_id).first()


def update_admin_task(
    db: Session,
    task: Task,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    due_date: Optional[str] = None,
) -> Task:
    """
    Actualizar tarea (admin).
    """
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        task.status = status
    if due_date is not None:
        task.due_date = due_date

    db.commit()
    db.refresh(task)
    return task


def delete_admin_task(db: Session, task_id: int) -> bool:
    """
    Eliminar tarea (admin).
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return True
    return False
