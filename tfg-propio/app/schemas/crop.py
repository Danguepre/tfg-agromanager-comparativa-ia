from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.irrigation_attributes import IrrigationAttributesResponse
from app.schemas.environmental_requirements import EnvironmentalRequirementsResponse
from app.schemas.planting_calendar import PlantingCalendarResponse

class CropBase(BaseModel):
    name: str
    type: str
    life_cycle: str
    image_url: str | None = None
    user_id: int | None = None
    is_public: bool = False
    source_crop_id: int | None = None

class CropCreate(CropBase):
    pass

class CropResponse(CropBase):
    id: int
    user_id: int | None = None
    created_at: datetime
    irrigation: Optional[IrrigationAttributesResponse] = None
    environmental: Optional[EnvironmentalRequirementsResponse] = None
    calendar: Optional[PlantingCalendarResponse] = None
    added_to_my_crops: bool = False

    class Config:
        from_attributes = True


class CropCatalogResponse(BaseModel):
    items: list[CropResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    types: list[str]
