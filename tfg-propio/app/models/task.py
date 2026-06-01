from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    name = Column(String)
    description = Column(Text)
    status = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="tasks")
    crops = relationship("TaskCrop", back_populates="task")

    @property
    def crop_ids(self):
        return [relation.crop_id for relation in self.crops]

    @property
    def crop_id(self):
        return self.crop_ids[0] if self.crop_ids else None
