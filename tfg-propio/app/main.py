import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

logger = logging.getLogger("uvicorn.error")
google_client_id = os.getenv("GOOGLE_CLIENT_ID")
google_client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
logger.info("Loaded .env from %s: %s", ENV_PATH, ENV_PATH.exists())
logger.info("GOOGLE_CLIENT_ID loaded: %s", bool(google_client_id))
logger.info("GOOGLE_CLIENT_SECRET exists: %s", bool(google_client_secret))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine, ensure_calendar_activation_column, ensure_crop_publication_columns
from app.models import *
from app.routes import admin, auth, crop, dashboard, environmental, irrigation, planting_calendar, task, user
from app.seed import seed_data
from app.services.image_search import ensure_crop_uploads_dir


def is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def get_app_env() -> str:
    return (os.getenv("APP_ENV", "development")).strip().lower()


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    if origins:
        return origins

    if get_app_env() == "development":
        return [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]

    return []


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_env = get_app_env()

    ensure_crop_uploads_dir()

    if app_env == "development":
        Base.metadata.create_all(bind=engine)
        ensure_crop_publication_columns()
        ensure_calendar_activation_column()

    if is_truthy(os.getenv("RUN_SEED")):
        seed_data()

    yield


app = FastAPI(
    title="AgroManager API",
    lifespan=lifespan,
)

cors_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path("uploads").mkdir(exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(user.router)
app.include_router(crop.router)
app.include_router(planting_calendar.router)
app.include_router(irrigation.router)
app.include_router(environmental.router)
app.include_router(task.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "API funcionando con PostgreSQL 🚀"}
