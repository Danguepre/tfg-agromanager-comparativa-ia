from functools import lru_cache
import os
from pathlib import Path

from pydantic import BaseModel


def _load_dotenv(path: str = ".env") -> dict[str, str]:
    env_path = Path(path)
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _get_env(name: str, default: str, dotenv_values: dict[str, str]) -> str:
    return os.getenv(name, dotenv_values.get(name, default))


class Settings(BaseModel):
    app_name: str = "AgroManager Pilot"
    environment: str = "development"
    database_url: str = "sqlite:///./agromanager.db"
    secret_key: str = "dev-only-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    allowed_origins_raw: str = "http://localhost:5173"
    upload_dir: str = "uploads"
    google_client_id: str | None = None
    google_client_secret: str | None = None

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    dotenv_values = _load_dotenv()
    return Settings(
        app_name=_get_env("APP_NAME", "AgroManager Pilot", dotenv_values),
        environment=_get_env("ENVIRONMENT", "development", dotenv_values),
        database_url=_get_env("DATABASE_URL", "sqlite:///./agromanager.db", dotenv_values),
        secret_key=_get_env("SECRET_KEY", "dev-only-change-me", dotenv_values),
        algorithm=_get_env("ALGORITHM", "HS256", dotenv_values),
        access_token_expire_minutes=int(
            _get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "60", dotenv_values)
        ),
        allowed_origins_raw=_get_env("ALLOWED_ORIGINS", "http://localhost:5173", dotenv_values),
        upload_dir=_get_env("UPLOAD_DIR", "uploads", dotenv_values),
        google_client_id=_get_env("GOOGLE_CLIENT_ID", "", dotenv_values) or None,
        google_client_secret=_get_env("GOOGLE_CLIENT_SECRET", "", dotenv_values) or None,
    )


settings = get_settings()
