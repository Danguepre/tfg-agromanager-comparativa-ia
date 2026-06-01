"""
Configuración CENTRALIZADA de base de datos para tests.
Usada por AMBOS unittest (test_api.py, test_phase6.py) y pytest.

CRÍTICO: Todos los módulos de test deben usar este engine/sessionlocal compartido.
Esto previene contaminación de datos entre tests de diferentes módulos.
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
# Importar modelos para registrar mappers con Base
from app import models
from app.main import app
from app.config import Settings

# ============================================================================
# CONFIGURACIÓN CENTRALIZADA - UN ÚNICO ENGINE PARA TODOS LOS TESTS
# ============================================================================
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Crear engine ÚNICO (no recrear en cada módulo de test)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # ✅ CRÍTICO: todas las conexiones usan la misma BD en memoria
)

# SessionLocal ÚNICO para tests (reutilizado por unittest y pytest)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas UNA SOLA VEZ en este módulo
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override centralizado de dependencia para usar BD de test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Realizar override UNA SOLA VEZ en app (antes de que se carguen los tests)
app.dependency_overrides[get_db] = override_get_db


def reset_test_database():
    """
    Limpiar y recrear todas las tablas de test.
    Llamar en setUp() de cada test class de unittest.
    IMPORTANTE: No eliminar/recrear en cada test individual, sino en setUp() de clase.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# ============================================================================
# FIXTURES PARA PYTEST (mantener compatibilidad - importar solo si pytest disponible)
# ============================================================================
try:
    import pytest

    @pytest.fixture
    def db():
        """Fixture que proporciona una sesión de BD limpia para cada test de pytest."""
        reset_test_database()
        connection = engine.connect()
        transaction = connection.begin()
        session = TestingSessionLocal(bind=connection)

        yield session

        session.close()
        transaction.rollback()
        connection.close()
        reset_test_database()

    @pytest.fixture
    def client():
        """Fixture que proporciona un cliente de test."""
        reset_test_database()
        return TestClient(app)

except ImportError:
    # pytest no está instalado, es OK para unittest
    pass
