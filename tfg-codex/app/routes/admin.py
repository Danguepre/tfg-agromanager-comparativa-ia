from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.crop import Crop
from app.models.planting_calendar import PlantingCalendar
from app.models.task import Task, TaskCrop
from app.models.user import User
from app.schemas.admin import AdminCropUpdate, AdminSummary, AdminUserUpdate
from app.schemas.crop import CropRead
from app.schemas.task import TaskRead, TaskUpdate
from app.schemas.user import UserRead


router = APIRouter(prefix="/admin", tags=["admin"])

ALLOWED_TASK_STATUSES = {"pending", "completed"}


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _get_crop_or_404(db: Session, crop_id: int) -> Crop:
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    return crop


def _get_task_or_404(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _commit_or_400(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or duplicate data") from exc


def _replace_task_crops(db: Session, task: Task, crop_ids: list[int]) -> None:
    crops = [_get_crop_or_404(db, crop_id) for crop_id in crop_ids]
    task.crop_links.clear()
    for crop in crops:
        task.crop_links.append(TaskCrop(crop_id=crop.id))


@router.get("/summary", response_model=AdminSummary)
def admin_summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AdminSummary:
    return AdminSummary(
        total_users=db.query(User).count(),
        total_crops=db.query(Crop).count(),
        total_public_crops=db.query(Crop).filter(Crop.is_public.is_(True)).count(),
        total_tasks=db.query(Task).count(),
        pending_tasks=db.query(Task).filter(Task.status == "pending").count(),
        completed_tasks=db.query(Task).filter(Task.status == "completed").count(),
        total_active_calendars=db.query(PlantingCalendar).filter(PlantingCalendar.is_active.is_(True)).count(),
        total_completed_calendars=db.query(PlantingCalendar).filter(PlantingCalendar.status == "completed").count(),
    )


@router.get("/users", response_model=list[UserRead])
def admin_list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[User]:
    return db.query(User).order_by(User.id).all()


@router.get("/users/{user_id}", response_model=UserRead)
def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    return _get_user_or_404(db, user_id)


@router.patch("/users/{user_id}", response_model=UserRead)
def admin_update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> User:
    user = _get_user_or_404(db, user_id)
    update_data = payload.model_dump(exclude_unset=True)
    update_data.pop("is_active", None)
    for field, value in update_data.items():
        setattr(user, field, value)
    _commit_or_400(db)
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
) -> None:
    user = _get_user_or_404(db, user_id)
    if user.id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin cannot delete itself")
    db.delete(user)
    _commit_or_400(db)


@router.get("/crops", response_model=list[CropRead])
def admin_list_crops(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[Crop]:
    return db.query(Crop).order_by(Crop.id).all()


@router.get("/crops/{crop_id}", response_model=CropRead)
def admin_get_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Crop:
    return _get_crop_or_404(db, crop_id)


@router.patch("/crops/{crop_id}", response_model=CropRead)
def admin_update_crop(
    crop_id: int,
    payload: AdminCropUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Crop:
    crop = _get_crop_or_404(db, crop_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(crop, field, value)
    _commit_or_400(db)
    db.refresh(crop)
    return crop


@router.delete("/crops/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    crop = _get_crop_or_404(db, crop_id)
    db.delete(crop)
    _commit_or_400(db)


@router.get("/tasks", response_model=list[TaskRead])
def admin_list_tasks(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> list[Task]:
    return db.query(Task).order_by(Task.id).all()


@router.get("/tasks/{task_id}", response_model=TaskRead)
def admin_get_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Task:
    return _get_task_or_404(db, task_id)


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def admin_update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> Task:
    task = _get_task_or_404(db, task_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "user_id" in update_data and update_data["user_id"] is not None:
        _get_user_or_404(db, update_data["user_id"])
        task.user_id = update_data["user_id"]
    if "name" in update_data and update_data["name"] is not None:
        task.name = update_data["name"]
    if "description" in update_data:
        task.description = update_data["description"]
    if "status" in update_data and update_data["status"] is not None:
        if update_data["status"] not in ALLOWED_TASK_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task status")
        task.status = update_data["status"]
    if "crop_ids" in update_data and update_data["crop_ids"] is not None:
        _replace_task_crops(db, task, update_data["crop_ids"])
    _commit_or_400(db)
    db.refresh(task)
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> None:
    task = _get_task_or_404(db, task_id)
    db.delete(task)
    _commit_or_400(db)
