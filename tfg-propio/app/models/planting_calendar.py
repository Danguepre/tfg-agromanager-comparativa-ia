from sqlalchemy import Boolean, Column, Integer, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base

class PlantingCalendar(Base):
    __tablename__ = "planting_calendar"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"))

    planting_start = Column(Date)
    planting_end = Column(Date)
    transplant_start = Column(Date)
    transplant_end = Column(Date)
    harvest_start = Column(Date)
    harvest_end = Column(Date)
    is_active = Column(Boolean, default=False, nullable=False)
    current_phase_index = Column(Integer, default=0, nullable=False)
    status = Column(String, default="draft", nullable=False)

    crop = relationship("Crop", back_populates="calendar")
