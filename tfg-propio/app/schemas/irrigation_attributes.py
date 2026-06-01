from pydantic import BaseModel

class IrrigationAttributesBase(BaseModel):
    watering_frequency: str
    water_amount: float
    recommendations: str

class IrrigationAttributesCreate(IrrigationAttributesBase):
    crop_id: int

class IrrigationAttributesResponse(IrrigationAttributesBase):
    id: int
    crop_id: int

    class Config:
        from_attributes = True