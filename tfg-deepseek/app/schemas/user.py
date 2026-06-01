"""Schemas Pydantic para Usuario."""

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Schema para creación de usuario."""
    email: str
    username: str
    password: str
    full_name: str | None = None
    role: str = "user"


class UserUpdate(BaseModel):
    """Schema para actualización de usuario."""
    email: str | None = None
    username: str | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserRead(BaseModel):
    """Schema para respuesta de usuario (NUNCA incluye password)."""
    id: int
    email: str
    username: str
    full_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}