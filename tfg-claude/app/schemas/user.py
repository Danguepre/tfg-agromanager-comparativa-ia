"""
Schemas de usuario.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base para usuario (campos comunes)."""

    email: EmailStr
    name: str


class UserCreate(UserBase):
    """Creación de usuario."""

    password: str


class UserResponse(UserBase):
    """Respuesta de usuario (sin password)."""

    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserDetailResponse(UserResponse):
    """Respuesta detallada de usuario."""

    pass
