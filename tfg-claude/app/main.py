"""
Punto de entrada de AgroManager API.
FastAPI + SQLAlchemy + JWT.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db, Base, engine
# Importar modelos para registrar mappers con Base
from app import models
from app.routes import auth, users, crops, planting_calendars, irrigation, environmental, tasks, dashboard, admin

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Contexto de ciclo de vida de la aplicación.
    startup: se ejecuta al iniciar
    shutdown: se ejecuta al apagar
    """
    # Startup
    logger.info(f"Starting AgroManager API in {settings.APP_ENV} environment")
    logger.info(f"Database: {settings.DATABASE_URL}")

    # Crear tablas
    try:
        init_db()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down AgroManager API")


# Crear aplicación FastAPI
app = FastAPI(
    title="AgroManager API",
    description="API para gestionar cultivos, tareas y calendarios agrícolas",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for: {settings.CORS_ORIGINS}")

# Crear carpeta de uploads si no existe
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Montar carpeta de uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Rutas de healthcheck
@app.get("/", tags=["health"])
def health_check():
    """
    Healthcheck de la API.
    Retorna estado de salud e información de la aplicación.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "app": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "version": "1.0.0",
        },
    )


@app.get("/health", tags=["health"])
def health():
    """Alias para healthcheck."""
    return {"status": "ok"}


# Incluir routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(crops.router)
app.include_router(planting_calendars.router)
app.include_router(irrigation.router)
app.include_router(environmental.router)
app.include_router(tasks.router)
app.include_router(dashboard.router)
app.include_router(admin.router)

logger.info("AgroManager API initialized successfully")
