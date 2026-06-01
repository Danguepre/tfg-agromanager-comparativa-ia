from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    name: str
    description: str | None = None
    status: str = "pending"


class TaskCreate(TaskBase):
    user_id: int | None = None
    crop_ids: list[int] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    user_id: int | None = None
    name: str | None = None
    description: str | None = None
    status: str | None = None
    crop_ids: list[int] | None = None


class TaskStatusUpdate(BaseModel):
    status: str


class TaskAssign(BaseModel):
    task_id: int
    crop_id: int | None = None
    crop_ids: list[int] | None = None


class TaskCropRead(BaseModel):
    task_id: int
    crop_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskRead(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    crop_links: list[TaskCropRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
