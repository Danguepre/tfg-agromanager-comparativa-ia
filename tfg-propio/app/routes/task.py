from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.task import Task
from app.models.user import User
from app.models.crop import Crop
from app.models.task_crop import TaskCrop
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.schemas.task_crop import TaskCropCreate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "admin" and task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Cannot create a task for another user")

    user = db.query(User).filter(User.id == task.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_task = Task(**task.dict())

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.post("/assign")
def assign_task_to_crop(
    data: TaskCropCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    task = db.query(Task).filter(Task.id == data.task_id).first()
    crop = db.query(Crop).filter(Crop.id == data.crop_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    if current_user["role"] != "admin" and (task.user_id != current_user["user_id"] or crop.user_id != current_user["user_id"]):
        raise HTTPException(status_code=403, detail="Not authorized to assign this task to this crop")

    relation = TaskCrop(**data.dict())

    db.add(relation)
    db.commit()

    return {"message": "Task assigned to crop"}


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] == "admin":
        return db.query(Task).all()
    return db.query(Task).filter(Task.user_id == current_user["user_id"]).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user["role"] != "admin" and task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this task")

    return task


@router.get("/user/{user_id}", response_model=list[TaskResponse])
def get_tasks_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin" and user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view tasks for this user")
    return db.query(Task).filter(Task.user_id == user_id).all()


@router.get("/crop/{crop_id}", response_model=list[TaskResponse])
def get_tasks_by_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    
    if current_user["role"] != "admin" and crop.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view tasks for this crop")
    
    task_crops = db.query(TaskCrop).filter(TaskCrop.crop_id == crop_id).all()
    tasks = [task_crop.task for task_crop in task_crops]
    
    return tasks


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user["role"] != "admin" and task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    db.query(TaskCrop).filter(TaskCrop.task_id == task_id).delete()
    
    db.delete(task)
    db.commit()
    
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if current_user["role"] != "admin" and task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task


@router.get("/{task_id}/crops")
def get_crops_for_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user["role"] != "admin" and task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view crops for this task")

    relations = db.query(TaskCrop).filter(TaskCrop.task_id == task_id).all()

    crop_ids = [r.crop_id for r in relations]

    crops = db.query(Crop).filter(Crop.id.in_(crop_ids)).all()

    return crops


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    updated_task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user["role"] != "admin" and task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this task")
    if current_user["role"] != "admin" and updated_task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Cannot reassign task to another user")

    task.name = updated_task.name
    task.description = updated_task.description
    task.status = updated_task.status
    task.user_id = updated_task.user_id

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if current_user["role"] != "admin" and task.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}
