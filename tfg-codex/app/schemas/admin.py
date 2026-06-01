from pydantic import BaseModel, EmailStr

from app.schemas.user import UserRole


class AdminSummary(BaseModel):
    total_users: int
    total_crops: int
    total_public_crops: int
    total_tasks: int
    pending_tasks: int
    completed_tasks: int
    total_active_calendars: int
    total_completed_calendars: int


class AdminUserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class AdminCropUpdate(BaseModel):
    name: str | None = None
    crop_type: str | None = None
    description: str | None = None
    image_url: str | None = None
    is_public: bool | None = None
    owner_id: int | None = None
    copied_from_crop_id: int | None = None
