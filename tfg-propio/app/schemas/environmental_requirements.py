from pydantic import BaseModel

class EnvironmentalRequirementsBase(BaseModel):
    sun_exposure: str
    min_temp: float
    max_temp: float
    frost_tolerance: bool

class EnvironmentalRequirementsCreate(EnvironmentalRequirementsBase):
    crop_id: int

class EnvironmentalRequirementsResponse(EnvironmentalRequirementsBase):
    id: int
    crop_id: int

    class Config:
        from_attributes = True