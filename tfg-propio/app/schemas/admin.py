from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.crop import CropResponse
from app.schemas.user import UserResponse


class PaginatedUsersResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedCropsResponse(BaseModel):
    items: list[CropResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    types: list[str]


class AdminSummaryResponse(BaseModel):
    total_users: int
    total_crops: int
    catalog_crops: int
    user_crops: int


class AdminUserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    location: str = ""
    role: Literal["user", "admin"] = "user"
    password: str = Field(min_length=4)


class AdminUserUpdate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    location: str = ""
    role: Literal["user", "admin"] = "user"


class AdminIrrigationPayload(BaseModel):
    watering_frequency: str = "daily"
    water_amount: float = 1.0
    recommendations: str = ""


class AdminEnvironmentalPayload(BaseModel):
    sun_exposure: str = "full_sun"
    min_temp: float = 15.0
    max_temp: float = 30.0
    frost_tolerance: bool = False


class AdminCalendarPayload(BaseModel):
    planting_start: date | None = None
    planting_end: date | None = None
    transplant_start: date | None = None
    transplant_end: date | None = None
    harvest_start: date | None = None
    harvest_end: date | None = None
    is_active: bool = False
    current_phase_index: int = 0
    status: str = "draft"


class AdminCropPayload(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    life_cycle: str = Field(min_length=1)
    image_url: str | None = None
    user_id: int | None = None
    is_public: bool = False
    source_crop_id: int | None = None
    irrigation: AdminIrrigationPayload | None = None
    environmental: AdminEnvironmentalPayload | None = None
    calendar: AdminCalendarPayload | None = None
