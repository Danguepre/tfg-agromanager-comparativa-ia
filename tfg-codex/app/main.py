from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text

import app.models  # noqa: F401
from app.core.config import settings
from app.core.database import Base, engine
from app.routes import admin, auth, calendar, crops, dashboard, environmental, irrigation, tasks, users


def _ensure_crop_schema() -> None:
    inspector = inspect(engine)
    if "crops" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("crops")}
    additive_columns = {
        "crop_type": "ALTER TABLE crops ADD COLUMN crop_type VARCHAR(80)",
        "image_url": "ALTER TABLE crops ADD COLUMN image_url VARCHAR(255)",
    }

    with engine.begin() as connection:
        for column_name, statement in additive_columns.items():
            if column_name not in columns:
                connection.execute(text(statement))


def _ensure_calendar_schema() -> None:
    inspector = inspect(engine)
    if "planting_calendars" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("planting_calendars")}
    additive_columns = {
        "planting_start": "ALTER TABLE planting_calendars ADD COLUMN planting_start DATE",
        "planting_end": "ALTER TABLE planting_calendars ADD COLUMN planting_end DATE",
        "transplant_start": "ALTER TABLE planting_calendars ADD COLUMN transplant_start DATE",
        "transplant_end": "ALTER TABLE planting_calendars ADD COLUMN transplant_end DATE",
        "harvest_start": "ALTER TABLE planting_calendars ADD COLUMN harvest_start DATE",
        "harvest_end": "ALTER TABLE planting_calendars ADD COLUMN harvest_end DATE",
        "is_active": "ALTER TABLE planting_calendars ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 0",
        "current_phase_index": (
            "ALTER TABLE planting_calendars ADD COLUMN current_phase_index INTEGER NOT NULL DEFAULT 0"
        ),
        "status": "ALTER TABLE planting_calendars ADD COLUMN status VARCHAR(30) NOT NULL DEFAULT 'draft'",
    }

    with engine.begin() as connection:
        for column_name, statement in additive_columns.items():
            if column_name not in columns:
                connection.execute(text(statement))


def _ensure_phase6_schema() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as connection:
        if "irrigation_attributes" in table_names:
            columns = {column["name"] for column in inspector.get_columns("irrigation_attributes")}
            additive_columns = {
                "watering_frequency": "ALTER TABLE irrigation_attributes ADD COLUMN watering_frequency VARCHAR(120)",
                "water_amount": "ALTER TABLE irrigation_attributes ADD COLUMN water_amount VARCHAR(120)",
                "recommendations": "ALTER TABLE irrigation_attributes ADD COLUMN recommendations TEXT",
            }
            for column_name, statement in additive_columns.items():
                if column_name not in columns:
                    connection.execute(text(statement))

        if "environmental_requirements" in table_names:
            columns = {column["name"] for column in inspector.get_columns("environmental_requirements")}
            additive_columns = {
                "frost_tolerance": "ALTER TABLE environmental_requirements ADD COLUMN frost_tolerance BOOLEAN",
            }
            for column_name, statement in additive_columns.items():
                if column_name not in columns:
                    connection.execute(text(statement))

        if "tasks" in table_names:
            columns = {column["name"] for column in inspector.get_columns("tasks")}
            additive_columns = {
                "user_id": "ALTER TABLE tasks ADD COLUMN user_id INTEGER",
                "name": "ALTER TABLE tasks ADD COLUMN name VARCHAR(160)",
                "created_at": "ALTER TABLE tasks ADD COLUMN created_at DATETIME",
            }
            for column_name, statement in additive_columns.items():
                if column_name not in columns:
                    connection.execute(text(statement))

            refreshed_columns = columns | set(additive_columns)
            if "owner_id" in refreshed_columns:
                connection.execute(text("UPDATE tasks SET user_id = owner_id WHERE user_id IS NULL"))
            if "title" in refreshed_columns:
                connection.execute(text("UPDATE tasks SET name = title WHERE name IS NULL"))
            connection.execute(text("UPDATE tasks SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL"))


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    _ensure_crop_schema()
    _ensure_calendar_schema()
    _ensure_phase6_schema()

    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(crops.router)
    app.include_router(calendar.router)
    app.include_router(irrigation.router)
    app.include_router(environmental.router)
    app.include_router(tasks.router)
    app.include_router(dashboard.router)
    app.include_router(admin.router)

    @app.get("/")
    def health_check() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
