"""
Configuración centralizada de AgroManager.
Maneja variables de entorno con valores por defecto.
"""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env del proyecto
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)


class Settings:
    """Configuración de la aplicación."""

    # Aplicación
    APP_ENV: str = os.getenv("APP_ENV", "development").strip().lower()
    DEBUG: bool = APP_ENV == "development"
    APP_NAME: str = "AgroManager"

    # Base de datos
    # PostgreSQL por defecto. SQLite como fallback si no existe DATABASE_URL
    # En tests, siempre usa SQLite
    _raw_database_url: str = os.getenv("DATABASE_URL", "").strip()

    @staticmethod
    def get_database_url() -> str:
        """
        Retorna la URL de BD.
        Precedencia:
        1. DATABASE_URL del .env (PostgreSQL recomendado)
        2. SQLite local si DATABASE_URL está vacío (fallback para dev rápido)
        En tests, siempre SQLite en memoria.
        """
        raw_url = os.getenv("DATABASE_URL", "").strip()
        if raw_url:
            return raw_url
        # Fallback a SQLite local si no hay DATABASE_URL
        db_path = BASE_DIR / "app.db"
        return f"sqlite:///{db_path}"

    DATABASE_URL: str = get_database_url()

    # JWT y autenticación
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod-12345")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # CORS
    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "").strip()

    @staticmethod
    def get_cors_origins() -> list[str]:
        """Retorna lista de orígenes CORS permitidos."""
        cors_raw = os.getenv("CORS_ORIGINS", "").strip()
        if cors_raw:
            return [origin.strip() for origin in cors_raw.split(",") if origin.strip()]

        # En desarrollo, permitir localhost
        app_env = os.getenv("APP_ENV", "development").strip().lower()
        if app_env == "development":
            return [
                "http://127.0.0.1:5173",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://localhost:3000",
            ]

        return []

    CORS_ORIGINS: list[str] = get_cors_origins()

    # Google OAuth (opcional, sin deps reales)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_OAUTH_REDIRECT: str = os.getenv(
        "GOOGLE_OAUTH_REDIRECT", "http://127.0.0.1:8000/auth/google/callback"
    )

    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")


@lru_cache()
def get_settings() -> Settings:
    """Retorna instancia única de Settings (singleton con cache)."""
    return Settings()
