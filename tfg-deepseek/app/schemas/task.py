"""Schemas Pydantic para Tarea."""

from datetime import datetime

from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: str = "pending"
    priority: str = "medium"
    due_date: datetime | None = None
    crop_ids: list[int] | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
    is_completed: bool | None = None
    crop_ids: list[int] | None = None


class TaskRead(BaseModel):
    id: int
    owner_id: int | None = None
    title: str
    description: str | None = None
    status: str
    priority: str
    due_date: datetime | None = None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}