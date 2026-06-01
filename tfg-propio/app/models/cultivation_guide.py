from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CultivationGuide(Base):
    __tablename__ = "cultivation_guides"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"))

    step_number = Column(Integer)
    description = Column(Text)

    crop = relationship("Crop", back_populates="guides")