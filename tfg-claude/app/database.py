"""
Configuración de la base de datos.
Soporta PostgreSQL (recomendado) y SQLite (fallback/tests).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

settings = get_settings()

# Crear motor de BD según DATABASE_URL
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG, **engine_kwargs)

# Sesiones
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

# Base para declarar modelos
Base = declarative_base()


def get_db():
    """Dependencia para obtener sesión de BD en rutas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    Base.metadata.create_all(bind=engine)
