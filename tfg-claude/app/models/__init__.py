"""Modelos SQLAlchemy - Importación centralizada."""
# Importar todos los modelos para registrar los mappers con Base
from app.models.user import User, UserRole
from app.models.crop import Crop
from app.models.planting_calendar import PlantingCalendar
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.cultivation_guide import CultivationGuide
from app.models.task import Task, TaskStatus
from app.models.task_crop import TaskCrop

__all__ = [
    "User",
    "UserRole",
    "Crop",
    "PlantingCalendar",
    "IrrigationAttributes",
    "EnvironmentalRequirements",
    "CultivationGuide",
    "Task",
    "TaskStatus",
    "TaskCrop",
]
