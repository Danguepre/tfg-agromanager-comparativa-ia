"""
Script de seed de desarrollo/demo para AgroManager.

Crea datos de ejemplo para poder probar la aplicación completa sin
tener que introducir datos manualmente.

Uso:
    python scripts/seed_demo.py

Requiere que las tablas existan en la base de datos (ejecutar backend al menos una vez).

¡ATENCIÓN! No uses estas credenciales en producción.
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto está en sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from datetime import date, datetime, timezone

from app.database import Base, SessionLocal, engine
from app.models.user import User
from app.models.crop import Crop
from app.models.planting_calendar import PlantingCalendar
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.cultivation_guide import CultivationGuide
from app.models.task import Task
from app.models.task_crop import TaskCrop
from app.auth import hash_password


# ─── Datos de seed ───────────────────────────────────────────────────

CATALOG_CROPS = [
    {
        "name": "Tomate",
        "scientific_name": "Solanum lycopersicum",
        "description": "El tomate es una hortaliza ampliamente cultivada en huertos. "
                       "Requiere climas cálidos y suelos bien drenados. "
                       "Ideal para ensaladas, salsas y conservas.",
        "category": "Hortalizas",
        "irrigation": {"frequency_days": 3, "water_needed_mm": 30.0, "irrigation_method": "riego por goteo"},
        "environmental": {
            "min_temperature": 15.0, "max_temperature": 35.0, "optimal_temperature": 24.0,
            "min_ph": 5.5, "max_ph": 7.5, "optimal_ph": 6.5,
            "sunlight_hours": 8, "humidity_percent": 65.0, "soil_type": "Franco arenoso",
        },
        "calendar": {
            "planting_start": date(2025, 3, 15), "planting_end": date(2025, 5, 15),
            "transplant_start": date(2025, 5, 1), "transplant_end": date(2025, 6, 15),
            "harvest_start": date(2025, 7, 1), "harvest_end": date(2025, 9, 30),
            "is_active": True, "status": "active",
        },
    },
    {
        "name": "Lechuga",
        "scientific_name": "Lactuca sativa",
        "description": "La lechuga es una hortaliza de hoja verde, ideal para "
                       "climas templados y cosecha rápida. Perfecta para jardineros principiantes.",
        "category": "Hortalizas",
        "irrigation": {"frequency_days": 2, "water_needed_mm": 20.0, "irrigation_method": "aspersión"},
        "environmental": {
            "min_temperature": 8.0, "max_temperature": 28.0, "optimal_temperature": 18.0,
            "min_ph": 6.0, "max_ph": 7.0, "optimal_ph": 6.5,
            "sunlight_hours": 5, "humidity_percent": 70.0, "soil_type": "Franco",
        },
        "calendar": None,
    },
    {
        "name": "Zanahoria",
        "scientific_name": "Daucus carota",
        "description": "La zanahoria es un cultivo de raíz que se desarrolla mejor "
                       "en suelos profundos y sueltos. Rica en betacaroteno.",
        "category": "Hortalizas",
        "irrigation": {"frequency_days": 4, "water_needed_mm": 25.0, "irrigation_method": "riego por goteo"},
        "environmental": {
            "min_temperature": 5.0, "max_temperature": 30.0, "optimal_temperature": 18.0,
            "min_ph": 5.5, "max_ph": 7.0, "optimal_ph": 6.3,
            "sunlight_hours": 6, "humidity_percent": 60.0, "soil_type": "Arenoso",
        },
        "calendar": None,
    },
    {
        "name": "Pimiento",
        "scientific_name": "Capsicum annuum",
        "description": "El pimiento es una hortaliza versátil que puede ser dulce "
                       "o picante. Requiere climas cálidos y mucho sol.",
        "category": "Hortalizas",
        "irrigation": {"frequency_days": 3, "water_needed_mm": 35.0, "irrigation_method": "riego por goteo"},
        "environmental": {
            "min_temperature": 15.0, "max_temperature": 35.0, "optimal_temperature": 25.0,
            "min_ph": 5.5, "max_ph": 7.2, "optimal_ph": 6.5,
            "sunlight_hours": 8, "humidity_percent": 60.0, "soil_type": "Franco arcilloso",
        },
        "calendar": None,
    },
    {
        "name": "Fresa",
        "scientific_name": "Fragaria × ananassa",
        "description": "La fresa es una fruta deliciosa y fácil de cultivar. "
                       "Ideal para macetas y jardines pequeños.",
        "category": "Frutas",
        "irrigation": {"frequency_days": 2, "water_needed_mm": 20.0, "irrigation_method": "riego por goteo"},
        "environmental": {
            "min_temperature": 5.0, "max_temperature": 30.0, "optimal_temperature": 20.0,
            "min_ph": 5.5, "max_ph": 7.0, "optimal_ph": 6.2,
            "sunlight_hours": 6, "humidity_percent": 70.0, "soil_type": "Franco arenoso",
        },
        "calendar": None,
    },
]

PERSONAL_CROPS = [
    {
        "name": "Mi Tomate",
        "description": "Mis tomates cherry del huerto de casa.",
        "category": "Hortalizas",
    },
    {
        "name": "Mi Lechuga",
        "description": "Lechugas variadas para ensaladas frescas.",
        "category": "Hortalizas",
    },
]

SEED_TASKS = [
    {
        "title": "Regar los tomates",
        "description": "Los tomates necesitan riego frecuente. Revisar humedad del suelo.",
        "status": "pending",
        "priority": "high",
    },
    {
        "title": "Abonar las lechugas",
        "description": "Aplicar fertilizante orgánico a las lechugas.",
        "status": "pending",
        "priority": "medium",
    },
    {
        "title": "Cosechar fresas maduras",
        "description": "Revisar las fresas y cosechar las que estén maduras.",
        "status": "completed",
        "priority": "medium",
    },
    {
        "title": "Preparar suelo para zanahorias",
        "description": "Airear la tierra y eliminar malas hierbas antes de la siembra.",
        "status": "completed",
        "priority": "low",
    },
]


def seed_demo(db):
    """Ejecuta el seed de datos demo. Devuelve un resumen."""
    summary = {
        "users_created": 0,
        "users_existing": 0,
        "crops_created": 0,
        "crops_existing": 0,
        "tasks_created": 0,
        "tasks_existing": 0,
        "calendars_created": 0,
        "calendars_existing": 0,
        "irrigation_created": 0,
        "irrigation_existing": 0,
        "environmental_created": 0,
        "environmental_existing": 0,
        "guides_created": 0,
        "guides_existing": 0,
    }

    # ─── Usuarios ───────────────────────────────────────────────────

    admin = db.query(User).filter(User.email == "admin@test.com").first()
    if not admin:
        admin = User(
            email="admin@test.com",
            username="admin",
            hashed_password=hash_password("admin123"),
            full_name="Administrador",
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.flush()
        summary["users_created"] += 1
    else:
        summary["users_existing"] += 1

    normal_user = db.query(User).filter(User.email == "user@test.com").first()
    if not normal_user:
        normal_user = User(
            email="user@test.com",
            username="user",
            hashed_password=hash_password("user123"),
            full_name="Usuario Demo",
            role="user",
            is_active=True,
        )
        db.add(normal_user)
        db.flush()
        summary["users_created"] += 1
    else:
        summary["users_existing"] += 1

    db.flush()

    # ─── Cultivos públicos del catálogo ─────────────────────────────

    for crop_data in CATALOG_CROPS:
        existing = db.query(Crop).filter(
            Crop.name == crop_data["name"],
            Crop.is_public == True,
        ).first()
        if existing:
            summary["crops_existing"] += 1
            continue

        crop = Crop(
            name=crop_data["name"],
            scientific_name=crop_data.get("scientific_name"),
            description=crop_data.get("description"),
            category=crop_data.get("category"),
            is_public=True,
            owner_id=admin.id,
            image_url="/static/placeholder-crop.png",
        )
        db.add(crop)
        db.flush()
        summary["crops_created"] += 1

        # Crear riego
        irr_data = crop_data.get("irrigation", {})
        irr = IrrigationAttributes(
            crop_id=crop.id,
            frequency_days=irr_data.get("frequency_days", 7),
            water_needed_mm=irr_data.get("water_needed_mm", 25.0),
            irrigation_method=irr_data.get("irrigation_method", "riego por goteo"),
            notes="Valores de ejemplo para demo",
        )
        db.add(irr)
        db.flush()
        summary["irrigation_created"] += 1

        # Crear ambientales
        env_data = crop_data.get("environmental", {})
        env = EnvironmentalRequirements(
            crop_id=crop.id,
            min_temperature=env_data.get("min_temperature", 10.0),
            max_temperature=env_data.get("max_temperature", 35.0),
            optimal_temperature=env_data.get("optimal_temperature"),
            min_ph=env_data.get("min_ph"),
            max_ph=env_data.get("max_ph"),
            optimal_ph=env_data.get("optimal_ph"),
            soil_type=env_data.get("soil_type"),
            sunlight_hours=env_data.get("sunlight_hours", 6),
            humidity_percent=env_data.get("humidity_percent"),
            notes="Valores de ejemplo para demo",
        )
        db.add(env)
        db.flush()
        summary["environmental_created"] += 1

        # Crear calendario si tiene datos
        cal_data = crop_data.get("calendar")
        if cal_data:
            cal = PlantingCalendar(
                crop_id=crop.id,
                planting_start=cal_data["planting_start"],
                planting_end=cal_data["planting_end"],
                transplant_start=cal_data["transplant_start"],
                transplant_end=cal_data["transplant_end"],
                harvest_start=cal_data["harvest_start"],
                harvest_end=cal_data["harvest_end"],
                is_active=cal_data.get("is_active", False),
                current_phase_index=cal_data.get("current_phase_index", 0),
                status=cal_data.get("status", "draft"),
                notes="Calendario de ejemplo para demo",
            )
            db.add(cal)
            db.flush()
            summary["calendars_created"] += 1

        # Crear guía de cultivo
        guide = CultivationGuide(
            crop_id=crop.id,
            soil_preparation=f"Preparar suelo para {crop_data['name']}: "
                             "labrar y enriquecer con compost.",
            planting_instructions=f"Plantar {crop_data['name']} a una profundidad "
                                  "adecuada según el tipo de semilla.",
            fertilization="Aplicar fertilizante orgánico cada 15 días.",
            pest_management="Vigilar plagas comunes y aplicar tratamientos "
                            "preventivos ecológicos.",
            pruning="Realizar poda de formación si es necesario.",
            harvesting_instructions="Cosechar cuando el producto esté en su punto "
                                    "óptimo de maduración.",
            storage="Almacenar en lugar fresco y seco.",
            notes=f"Guía básica de cultivo para {crop_data['name']}.",
        )
        db.add(guide)
        db.flush()
        summary["guides_created"] += 1

    # ─── Cultivos personales para user ──────────────────────────────

    for pc_data in PERSONAL_CROPS:
        existing = db.query(Crop).filter(
            Crop.name == pc_data["name"],
            Crop.owner_id == normal_user.id,
        ).first()
        if existing:
            summary["crops_existing"] += 1
            continue

        crop = Crop(
            name=pc_data["name"],
            description=pc_data.get("description"),
            category=pc_data.get("category"),
            is_public=False,
            owner_id=normal_user.id,
            image_url="/static/placeholder-crop.png",
        )
        db.add(crop)
        db.flush()
        summary["crops_created"] += 1

        # Riego por defecto
        irr = IrrigationAttributes(
            crop_id=crop.id,
            frequency_days=5,
            water_needed_mm=25.0,
            irrigation_method="riego por goteo",
            notes="Valores por defecto — ajustar según necesidad",
        )
        db.add(irr)
        db.flush()
        summary["irrigation_created"] += 1

        # Ambientales por defecto
        env = EnvironmentalRequirements(
            crop_id=crop.id,
            min_temperature=10.0,
            max_temperature=35.0,
            optimal_temperature=22.0,
            min_ph=5.5,
            max_ph=7.5,
            optimal_ph=6.5,
            sunlight_hours=6,
            humidity_percent=60.0,
            notes="Valores por defecto — ajustar según necesidad",
        )
        db.add(env)
        db.flush()
        summary["environmental_created"] += 1

    # ─── Calendarios para cultivos personales ──────────────────────

    # Buscar "Mi Tomate" para calendario activo
    mi_tomate = db.query(Crop).filter(
        Crop.name == "Mi Tomate",
        Crop.owner_id == normal_user.id,
    ).first()

    if mi_tomate:
        existing_cal = db.query(PlantingCalendar).filter(
            PlantingCalendar.crop_id == mi_tomate.id,
        ).first()
        if not existing_cal:
            cal = PlantingCalendar(
                crop_id=mi_tomate.id,
                planting_start=date(2025, 4, 1),
                planting_end=date(2025, 5, 30),
                transplant_start=date(2025, 5, 15),
                transplant_end=date(2025, 6, 30),
                harvest_start=date(2025, 7, 15),
                harvest_end=date(2025, 9, 30),
                is_active=True,
                current_phase_index=1,
                status="active",
                notes="Calendario activo para mis tomates.",
            )
            db.add(cal)
            db.flush()
            summary["calendars_created"] += 1
        else:
            summary["calendars_existing"] += 1

    # Buscar "Mi Lechuga" para calendario completado
    mi_lechuga = db.query(Crop).filter(
        Crop.name == "Mi Lechuga",
        Crop.owner_id == normal_user.id,
    ).first()

    if mi_lechuga:
        existing_cal = db.query(PlantingCalendar).filter(
            PlantingCalendar.crop_id == mi_lechuga.id,
        ).first()
        if not existing_cal:
            cal = PlantingCalendar(
                crop_id=mi_lechuga.id,
                planting_start=date(2025, 1, 15),
                planting_end=date(2025, 2, 28),
                transplant_start=date(2025, 3, 1),
                transplant_end=date(2025, 3, 31),
                harvest_start=date(2025, 4, 1),
                harvest_end=date(2025, 5, 15),
                is_active=False,
                current_phase_index=2,
                status="completed",
                notes="Calendario completado de lechugas.",
            )
            db.add(cal)
            db.flush()
            summary["calendars_created"] += 1
        else:
            summary["calendars_existing"] += 1

    # ─── Tareas ────────────────────────────────────────────────────

    for task_data in SEED_TASKS:
        existing = db.query(Task).filter(
            Task.title == task_data["title"],
            Task.owner_id == normal_user.id,
        ).first()
        if existing:
            summary["tasks_existing"] += 1
            continue

        is_completed = task_data["status"] == "completed"

        task = Task(
            owner_id=normal_user.id,
            title=task_data["title"],
            description=task_data.get("description"),
            status=task_data["status"],
            priority=task_data.get("priority", "medium"),
            is_completed=is_completed,
        )
        db.add(task)
        db.flush()
        summary["tasks_created"] += 1

        # Asignar tareas a cultivos según corresponda
        if "tomate" in task_data["title"].lower() and mi_tomate:
            existing_tc = db.query(TaskCrop).filter(
                TaskCrop.task_id == task.id,
                TaskCrop.crop_id == mi_tomate.id,
            ).first()
            if not existing_tc:
                db.add(TaskCrop(task_id=task.id, crop_id=mi_tomate.id))

        if "lechuga" in task_data["title"].lower() and mi_lechuga:
            existing_tc = db.query(TaskCrop).filter(
                TaskCrop.task_id == task.id,
                TaskCrop.crop_id == mi_lechuga.id,
            ).first()
            if not existing_tc:
                db.add(TaskCrop(task_id=task.id, crop_id=mi_lechuga.id))

    db.commit()

    # Contar riego/ambiente existentes (los que no se crearon ahora)
    existing_irr = summary["irrigation_existing"]
    if "irrigation_existing" in summary:
        summary["irrigation_existing"] = existing_irr

    return summary


def print_summary(summary):
    """Imprime un resumen formateado del seed."""
    print("=" * 60)
    print("  🌱 SEED DE DESARROLLO — RESUMEN")
    print("=" * 60)
    print(f"  Usuarios creados:    {summary['users_created']}")
    print(f"  Usuarios existentes: {summary['users_existing']}")
    print(f"  Cultivos creados:    {summary['crops_created']}")
    print(f"  Cultivos existentes: {summary['crops_existing']}")
    print(f"  Calendarios creados:    {summary['calendars_created']}")
    print(f"  Calendarios existentes: {summary['calendars_existing']}")
    print(f"  Tareas creadas:      {summary['tasks_created']}")
    print(f"  Tareas existentes:   {summary['tasks_existing']}")
    print(f"  Riego creado:        {summary['irrigation_created']}")
    print(f"  Riego existente:     {summary['irrigation_existing']}")
    print(f"  Ambiente creado:     {summary['environmental_created']}")
    print(f"  Ambiente existente:  {summary['environmental_existing']}")
    print(f"  Guías creadas:       {summary['guides_created']}")
    print(f"  Guías existentes:    {summary['guides_existing']}")
    print("=" * 60)


def main():
    """Punto de entrada del script de seed."""
    # Asegurar que las tablas existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("🌱 Ejecutando seed de desarrollo...")
        summary = seed_demo(db)
        print_summary(summary)
        print("✅ Seed completado correctamente.")
        print()
        print("📋 Credenciales DEMO:")
        print("   Admin: admin@test.com / admin123")
        print("   User:  user@test.com / user123")
        print()
        print("⚠️  No uses estas credenciales en producción.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error ejecutando seed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()