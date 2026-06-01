from datetime import date

from pydantic import BaseModel, ConfigDict


class PlantingCalendarBase(BaseModel):
    planting_start: date | None = None
    planting_end: date | None = None
    transplant_start: date | None = None
    transplant_end: date | None = None
    harvest_start: date | None = None
    harvest_end: date | None = None
    is_active: bool = False
    current_phase_index: int = 0
    status: str = "draft"


class PlantingCalendarRead(PlantingCalendarBase):
    id: int
    crop_id: int

    model_config = ConfigDict(from_attributes=True)


class IrrigationAttributesBase(BaseModel):
    water_needs: str | None = None
    frequency_days: int | None = None
    notes: str | None = None


class IrrigationAttributesRead(IrrigationAttributesBase):
    id: int
    crop_id: int

    model_config = ConfigDict(from_attributes=True)


class EnvironmentalRequirementsBase(BaseModel):
    climate: str | None = None
    soil_type: str | None = None
    sun_exposure: str | None = None
    min_temperature_c: int | None = None
    max_temperature_c: int | None = None


class EnvironmentalRequirementsRead(EnvironmentalRequirementsBase):
    id: int
    crop_id: int

    model_config = ConfigDict(from_attributes=True)


class CultivationGuideBase(BaseModel):
    preparation: str | None = None
    sowing: str | None = None
    care: str | None = None
    harvest: str | None = None


class CultivationGuideRead(CultivationGuideBase):
    id: int
    crop_id: int

    model_config = ConfigDict(from_attributes=True)


class CropBase(BaseModel):
    name: str
    crop_type: str | None = None
    description: str | None = None
    image_url: str | None = None
    is_public: bool = False
    owner_id: int | None = None
    copied_from_crop_id: int | None = None


class CropCreate(CropBase):
    planting_calendar: PlantingCalendarBase | None = None
    irrigation_attributes: IrrigationAttributesBase | None = None
    environmental_requirements: EnvironmentalRequirementsBase | None = None
    cultivation_guide: CultivationGuideBase | None = None


class CropRead(CropBase):
    id: int
    planting_calendar: PlantingCalendarRead | None = None
    irrigation_attributes: IrrigationAttributesRead | None = None
    environmental_requirements: EnvironmentalRequirementsRead | None = None
    cultivation_guide: CultivationGuideRead | None = None

    model_config = ConfigDict(from_attributes=True)
