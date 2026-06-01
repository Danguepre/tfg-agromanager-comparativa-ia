"""
Schemas de tarea.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.task import TaskStatus


class TaskBase(BaseModel):
    """Base para tarea."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    due_date: Optional[str] = None


class TaskCreate(TaskBase):
    """Creación de tarea."""

    pass


class TaskUpdate(BaseModel):
    """Actualización parcial de tarea."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    due_date: Optional[str] = None
    status: Optional[TaskStatus] = None


class TaskResponse(TaskBase):
    """Respuesta de tarea."""

    id: int
    owner_id: int
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskCropAssignRequest(BaseModel):
    """Request para asignar tarea a cultivo."""

    task_id: int
    crop_id: int


class CropBasicResponse(BaseModel):
    """Respuesta básica de cultivo para tareas."""

    id: int
    name: str
    crop_type: Optional[str] = None
    owner_id: Optional[int] = None

    model_config = {"from_attributes": True}


class TaskDetailResponse(TaskResponse):
    """Respuesta detallada de tarea con cultivos asociados."""

    crops: Optional[list[CropBasicResponse]] = []

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    """Paginación de tareas."""

    total: int
    skip: int
    limit: int
    items: list[TaskResponse]
