import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


DEFAULT_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/tfg_db"


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL).strip()


DATABASE_URL = get_database_url()

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_crop_publication_columns():
    inspector = inspect(engine)
    if "crops" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("crops")}
    statements = []

    if "is_public" not in columns:
        if engine.dialect.name == "postgresql":
            statements.append("ALTER TABLE crops ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT FALSE")
        else:
            statements.append("ALTER TABLE crops ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT 0")

    if "source_crop_id" not in columns:
        statements.append("ALTER TABLE crops ADD COLUMN source_crop_id INTEGER NULL")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def ensure_calendar_activation_column():
    inspector = inspect(engine)
    if "planting_calendar" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("planting_calendar")}
    statements = []

    if "is_active" not in columns:
        if engine.dialect.name == "postgresql":
            statements.append("ALTER TABLE planting_calendar ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT FALSE")
        else:
            statements.append("ALTER TABLE planting_calendar ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 0")

    if "current_phase_index" not in columns:
        statements.append("ALTER TABLE planting_calendar ADD COLUMN current_phase_index INTEGER NOT NULL DEFAULT 0")

    if "status" not in columns:
        statements.append("ALTER TABLE planting_calendar ADD COLUMN status VARCHAR NOT NULL DEFAULT 'draft'")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
