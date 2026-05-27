"""Configuración de SQLAlchemy y sesión de base de datos."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Clase base para modelos SQLAlchemy."""
    pass


def get_db():
    """Dependencia FastAPI para obtener la sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()