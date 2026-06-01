from pydantic import BaseModel

class TaskCropCreate(BaseModel):
    task_id: int
    crop_id: int

class TaskCropResponse(BaseModel):
    id: int
    task_id: int
    crop_id: int

    class Config:
        from_attributes = True