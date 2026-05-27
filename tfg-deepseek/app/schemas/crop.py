"""Schemas Pydantic para Cultivo."""

from datetime import datetime

from pydantic import BaseModel


class CropCreate(BaseModel):
    """Schema para creación de cultivo."""
    name: str
    scientific_name: str | None = None
    description: str | None = None
    category: str | None = None
    is_public: bool = False
    image_url: str | None = None


class CropUpdate(BaseModel):
    """Schema para actualización de cultivo."""
    name: str | None = None
    scientific_name: str | None = None
    description: str | None = None
    category: str | None = None
    is_public: bool | None = None
    image_url: str | None = None


class CropRead(BaseModel):
    """Schema para respuesta de cultivo."""
    id: int
    name: str
    scientific_name: str | None = None
    description: str | None = None
    category: str | None = None
    is_public: bool
    owner_id: int | None = None
    copied_from_id: int | None = None
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}