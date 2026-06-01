from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.crop import Crop
from app.models.task import Task, TaskCrop
from app.models.user import User
from app.schemas.crop import CropRead
from app.schemas.task import TaskAssign, TaskCreate, TaskRead, TaskStatusUpdate, TaskUpdate


router = APIRouter(prefix="/tasks", tags=["tasks"])

ALLOWED_STATUSES = {"pending", "completed"}


def _is_admin(user: User) -> bool:
    return user.role == "admin"


def _get_task_or_404(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def _get_crop_or_404(db: Session, crop_id: int) -> Crop:
    crop = db.get(Crop, crop_id)
    if crop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found")
    return crop


def _ensure_can_manage_task(user: User, task: Task) -> None:
    if not _is_admin(user) and task.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def _ensure_can_manage_crop(user: User, crop: Crop) -> None:
    if not _is_admin(user) and crop.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")


def _ensure_valid_status(status_value: str) -> None:
    if status_value not in ALLOWED_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task status")


def _crop_ids_from_assign(payload: TaskAssign) -> list[int]:
    crop_ids = list(payload.crop_ids or [])
    if payload.crop_id is not None:
        crop_ids.append(payload.crop_id)
    return list(dict.fromkeys(crop_ids))


def _replace_task_crops(db: Session, task: Task, crop_ids: list[int], current_user: User) -> None:
    crops = [_get_crop_or_404(db, crop_id) for crop_id in crop_ids]
    for crop in crops:
        _ensure_can_manage_crop(current_user, crop)

    task.crop_links.clear()
    for crop in crops:
        task.crop_links.append(TaskCrop(crop_id=crop.id))


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    _ensure_valid_status(payload.status)
    user_id = payload.user_id or current_user.id
    if not _is_admin(current_user) and user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    task = Task(
        user_id=user_id,
        name=payload.name,
        description=payload.description,
        status=payload.status,
    )
    db.add(task)
    db.flush()
    if payload.crop_ids:
        _replace_task_crops(db, task, payload.crop_ids, current_user)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=list[TaskRead])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    query = db.query(Task)
    if not _is_admin(current_user):
        query = query.filter(Task.user_id == current_user.id)
    return query.order_by(Task.id).all()


@router.get("/user/{user_id}", response_model=list[TaskRead])
def list_tasks_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    if not _is_admin(current_user) and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return db.query(Task).filter(Task.user_id == user_id).order_by(Task.id).all()


@router.get("/crop/{crop_id}", response_model=list[TaskRead])
def list_tasks_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    crop = _get_crop_or_404(db, crop_id)
    _ensure_can_manage_crop(current_user, crop)
    return (
        db.query(Task)
        .join(TaskCrop)
        .filter(TaskCrop.crop_id == crop_id)
        .order_by(Task.id)
        .all()
    )


@router.post("/assign", response_model=TaskRead)
def assign_task_to_crops(
    payload: TaskAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    task = _get_task_or_404(db, payload.task_id)
    _ensure_can_manage_task(current_user, task)
    crop_ids = _crop_ids_from_assign(payload)
    if not crop_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one crop is required")

    existing_ids = {link.crop_id for link in task.crop_links}
    for crop_id in crop_ids:
        crop = _get_crop_or_404(db, crop_id)
        _ensure_can_manage_crop(current_user, crop)
        if crop.id not in existing_ids:
            task.crop_links.append(TaskCrop(crop_id=crop.id))
            existing_ids.add(crop.id)

    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}/crops", response_model=list[CropRead])
def list_task_crops(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Crop]:
    task = _get_task_or_404(db, task_id)
    _ensure_can_manage_task(current_user, task)
    return [link.crop for link in task.crop_links]


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    task = _get_task_or_404(db, task_id)
    _ensure_can_manage_task(current_user, task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    task = _get_task_or_404(db, task_id)
    _ensure_can_manage_task(current_user, task)
    _ensure_valid_status(payload.status)
    task.status = payload.status
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    task = _get_task_or_404(db, task_id)
    _ensure_can_manage_task(current_user, task)
    update_data = payload.model_dump(exclude_unset=True)

    if "user_id" in update_data:
        if not _is_admin(current_user) and update_data["user_id"] != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        task.user_id = update_data["user_id"]
    if "status" in update_data and update_data["status"] is not None:
        _ensure_valid_status(update_data["status"])
        task.status = update_data["status"]
    if "name" in update_data and update_data["name"] is not None:
        task.name = update_data["name"]
    if "description" in update_data:
        task.description = update_data["description"]
    if "crop_ids" in update_data and update_data["crop_ids"] is not None:
        _replace_task_crops(db, task, update_data["crop_ids"], current_user)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    task = _get_task_or_404(db, task_id)
    _ensure_can_manage_task(current_user, task)
    db.delete(task)
    db.commit()
