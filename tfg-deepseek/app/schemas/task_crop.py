"""Schemas Pydantic para asociación Task-Crop."""

from datetime import datetime

from pydantic import BaseModel


class TaskCropCreate(BaseModel):
    task_id: int
    crop_id: int


class TaskCropRead(BaseModel):
    id: int
    task_id: int
    crop_id: int
    created_at: datetime

    model_config = {"from_attributes": True}