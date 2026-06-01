"""Punto de entrada de la aplicación FastAPI."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.models import *  # noqa: F401, F403 — Importa todos los modelos para crear tablas
from app.routes import auth, crop, dashboard, admin, environmental, irrigation, planting_calendar, task, user

# Crear directorio de uploads si no existe
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = FastAPI(
    title="AgroManager API",
    description="API para gestión de cultivos agrícolas",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos (uploads)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Crear tablas en la base de datos
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(auth.router)
app.include_router(crop.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(environmental.router)
app.include_router(irrigation.router)
app.include_router(planting_calendar.router)
app.include_router(task.router)
app.include_router(user.router)


@app.get("/")
def health_check():
    """Endpoint de salud del sistema."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "message": "AgroManager API funcionando correctamente",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)