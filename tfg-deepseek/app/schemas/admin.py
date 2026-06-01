"""Schemas Pydantic para Panel Admin."""

from datetime import datetime
from pydantic import BaseModel


class UserAdminRead(BaseModel):
    """Schema para respuesta de usuario en admin (NUNCA incluye password/hash)."""
    id: int
    email: str
    username: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserAdminUpdate(BaseModel):
    """Schema para actualización de usuario por admin."""
    email: str | None = None
    username: str | None = None
    full_name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class AdminSummary(BaseModel):
    """Resumen global del panel admin."""
    total_users: int
    total_crops: int
    total_public_crops: int
    total_tasks: int
    tasks_pending: int
    tasks_completed: int
    total_active_calendars: int
    total_completed_calendars: int