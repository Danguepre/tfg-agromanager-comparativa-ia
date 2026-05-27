from pydantic import BaseModel, ConfigDict


class EnvironmentalBase(BaseModel):
    sun_exposure: str | None = None
    min_temp: int | None = None
    max_temp: int | None = None
    frost_tolerance: bool | None = None


class EnvironmentalCreate(EnvironmentalBase):
    crop_id: int


class EnvironmentalUpdate(EnvironmentalBase):
    pass


class EnvironmentalRead(EnvironmentalBase):
    id: int
    crop_id: int

    model_config = ConfigDict(from_attributes=True)
