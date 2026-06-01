"""
Modelo base con campos comunes (created_at, updated_at).
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class TimestampMixin:
    """Mixin que añade campos de timestamp a los modelos."""

    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
