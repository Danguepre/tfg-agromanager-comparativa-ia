from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    user = "user"
    admin = "admin"


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=80)
    role: UserRole = UserRole.user


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
