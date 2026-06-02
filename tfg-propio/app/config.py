import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
LOCAL_SECRET_KEY = "change-me-only-for-local-development"

load_dotenv(dotenv_path=ENV_PATH)


def get_app_env() -> str:
    return os.getenv("APP_ENV", "development").strip().lower()


def get_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY", "").strip()
    if secret_key:
        return secret_key

    if get_app_env() in {"development", "test"}:
        return LOCAL_SECRET_KEY

    raise RuntimeError("SECRET_KEY must be configured outside development and test environments")


def get_pexels_api_key() -> str | None:
    return os.getenv("PEXELS_API_KEY")
