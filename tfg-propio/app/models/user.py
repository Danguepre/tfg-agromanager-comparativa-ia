from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    location = Column(String)
    role = Column(String, default="user")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    crops = relationship("Crop", back_populates="user")
    tasks = relationship("Task", back_populates="user")