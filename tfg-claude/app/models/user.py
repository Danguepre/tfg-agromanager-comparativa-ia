"""
Modelo User.
"""
from enum import Enum

from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin


class UserRole(str, Enum):
    """Roles de usuario."""

    USER = "user"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    """Modelo de usuario."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)  # bcrypt hash
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relaciones (para FASE 2+)
    crops = relationship("Crop", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
