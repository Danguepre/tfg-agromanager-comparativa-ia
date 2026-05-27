"""Configuración de la aplicación mediante variables de entorno."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    DATABASE_URL: str = "sqlite:///./agromanager.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: str = "http://localhost:5173"
    GOOGLE_CLIENT_ID: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        """Convierte CORS_ORIGINS en lista."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()