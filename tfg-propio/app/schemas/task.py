from pydantic import BaseModel, Field
from datetime import datetime

class TaskBase(BaseModel):
    name: str
    description: str
    status: str

class TaskCreate(TaskBase):
    user_id: int

class TaskUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None

class TaskResponse(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    crop_id: int | None = None
    crop_ids: list[int] = Field(default_factory=list)

    class Config:
        from_attributes = True
