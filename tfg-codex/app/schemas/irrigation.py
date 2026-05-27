from pydantic import BaseModel, ConfigDict


class IrrigationBase(BaseModel):
    watering_frequency: str | None = None
    water_amount: str | None = None
    recommendations: str | None = None


class IrrigationCreate(IrrigationBase):
    crop_id: int


class IrrigationUpdate(IrrigationBase):
    pass


class IrrigationRead(IrrigationBase):
    id: int
    crop_id: int

    model_config = ConfigDict(from_attributes=True)
