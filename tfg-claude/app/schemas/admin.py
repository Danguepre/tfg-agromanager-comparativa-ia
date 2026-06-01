"""
Schemas para panel admin.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole
from app.models.task import TaskStatus


class AdminUserResponse(BaseModel):
    """Respuesta de usuario para admin (sin password)."""

    id: int
    email: EmailStr
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUserUpdate(BaseModel):
    """Actualización de usuario por admin."""

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class AdminCropResponse(BaseModel):
    """Respuesta de cultivo para admin."""

    id: int
    name: str
    description: Optional[str] = None
    crop_type: Optional[str] = None
    owner_id: Optional[int] = None
    is_public: bool
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminCropUpdate(BaseModel):
    """Actualización de cultivo por admin."""

    name: Optional[str] = None
    description: Optional[str] = None
    crop_type: Optional[str] = None
    is_public: Optional[bool] = None


class AdminTaskResponse(BaseModel):
    """Respuesta de tarea para admin."""

    id: int
    owner_id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    due_date: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminTaskUpdate(BaseModel):
    """Actualización de tarea por admin."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[str] = None


class AdminListResponse(BaseModel):
    """Respuesta genérica para listados de admin."""

    total: int
    skip: int
    limit: int
    items: list


class AdminSummary(BaseModel):
    """Resumen general del panel admin."""

    total_users: int
    total_crops: int
    total_public_crops: int
    total_tasks: int
    total_pending_tasks: int
    total_completed_tasks: int
    total_active_calendars: int
    total_completed_calendars: int
