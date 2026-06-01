from pydantic import BaseModel

class CultivationGuideBase(BaseModel):
    step_number: int
    description: str

class CultivationGuideCreate(CultivationGuideBase):
    crop_id: int

class CultivationGuideResponse(CultivationGuideBase):
    id: int
    crop_id: int

    class Config:
        from_attributes = True