"""Rutas de panel de administración (FASE 7)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.crop import Crop
from app.models.task import Task
from app.models.planting_calendar import PlantingCalendar
from app.schemas.admin import AdminSummary, UserAdminRead, UserAdminUpdate
from app.schemas.user import UserCreate, UserRead
from app.schemas.crop import CropCreate, CropRead, CropUpdate
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(current_user: User) -> None:
    """Verifica que el usuario actual sea admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a este recurso",
        )


# ──────────────────────────────────────────
#  Admin Summary
# ──────────────────────────────────────────


@router.get("/summary", response_model=AdminSummary)
def get_admin_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene resumen global del sistema. Solo admin."""
    _require_admin(current_user)

    total_users = db.query(User).count()
    total_crops = db.query(Crop).count()
    total_public_crops = db.query(Crop).filter(Crop.is_public == True).count()  # noqa: E712
    total_tasks = db.query(Task).count()
    tasks_pending = db.query(Task).filter(Task.is_completed == False).count()  # noqa: E712
    tasks_completed = db.query(Task).filter(Task.is_completed == True).count()  # noqa: E712
    total_active_calendars = db.query(PlantingCalendar).filter(
        PlantingCalendar.status == "active"
    ).count()
    total_completed_calendars = db.query(PlantingCalendar).filter(
        PlantingCalendar.status == "completed"
    ).count()

    return AdminSummary(
        total_users=total_users,
        total_crops=total_crops,
        total_public_crops=total_public_crops,
        total_tasks=total_tasks,
        tasks_pending=tasks_pending,
        tasks_completed=tasks_completed,
        total_active_calendars=total_active_calendars,
        total_completed_calendars=total_completed_calendars,
    )


# ──────────────────────────────────────────
#  Admin Users
# ──────────────────────────────────────────


@router.get("/users", response_model=list[UserAdminRead])
def admin_list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos los usuarios. Solo admin."""
    _require_admin(current_user)
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=UserAdminRead)
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un usuario por ID. Solo admin."""
    _require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user


@router.patch("/users/{user_id}", response_model=UserAdminRead)
def admin_update_user(
    user_id: int,
    user_data: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un usuario. Solo admin. No expone password."""
    _require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un usuario. Solo admin."""
    _require_admin(current_user)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    db.delete(user)
    db.commit()
    return None


# ──────────────────────────────────────────
#  Admin Crops
# ──────────────────────────────────────────


@router.get("/crops")
def admin_list_crops(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos los cultivos. Solo admin."""
    _require_admin(current_user)
    crops = db.query(Crop).all()
    return crops


@router.get("/crops/{crop_id}")
def admin_get_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene un cultivo por ID. Solo admin."""
    _require_admin(current_user)
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cultivo no encontrado",
        )
    return crop


@router.patch("/crops/{crop_id}")
def admin_update_crop(
    crop_id: int,
    crop_data: CropUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza un cultivo. Solo admin."""
    _require_admin(current_user)
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cultivo no encontrado",
        )

    update_data = crop_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(crop, field, value)

    db.commit()
    db.refresh(crop)
    return crop


@router.delete("/crops/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un cultivo definitivamente. Solo admin."""
    _require_admin(current_user)
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cultivo no encontrado",
        )

    # Eliminar registros relacionados para evitar errores de integridad
    if crop.irrigation:
        db.delete(crop.irrigation)
    if crop.environmental:
        db.delete(crop.environmental)
    if crop.planting_calendar:
        db.delete(crop.planting_calendar)
    if crop.cultivation_guide:
        db.delete(crop.cultivation_guide)
    if crop.task_crops:
        for tc in crop.task_crops:
            db.delete(tc)

    db.delete(crop)
    db.commit()
    return None


# ──────────────────────────────────────────
#  Admin Tasks
# ──────────────────────────────────────────


@router.get("/tasks")
def admin_list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas las tareas. Solo admin."""
    _require_admin(current_user)
    tasks = db.query(Task).all()
    return tasks


@router.get("/tasks/{task_id}")
def admin_get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una tarea por ID. Solo admin."""
    _require_admin(current_user)
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )
    return task


@router.patch("/tasks/{task_id}")
def admin_update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una tarea. Solo admin."""
    _require_admin(current_user)
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una tarea. Solo admin."""
    _require_admin(current_user)
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada",
        )

    db.delete(task)
    db.commit()
    return None