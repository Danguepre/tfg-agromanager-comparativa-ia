#!/usr/bin/env python3
"""
FASE 10: Script de Seed/Demo - Inicializa BD con datos de ejemplo.

Crea usuarios, cultivos, tareas, calendarios y riego.
Totalmente idempotente: ejecutar múltiples veces es seguro.

Credenciales Demo:
  Admin:
    email: admin@test.com
    password: admin123
    role: admin

  User Demo:
    email: user@test.com
    password: user123
    role: user

Uso:
  python scripts/seed_demo.py          # Crear datos de ejemplo
  python scripts/seed_demo.py --clean  # Borrar TODO (solo admin se mantiene)
  python scripts/seed_demo.py --reset  # Borrar TODO incluyendo admin, recrear desde cero
"""
import sys
import os
from datetime import date, datetime, timedelta
from typing import Optional

# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.crop import Crop
from app.models.task import Task, TaskStatus
from app.models.planting_calendar import PlantingCalendar, CalendarStatus
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.cultivation_guide import CultivationGuide
from app.services.user_service import create_user, get_user_by_email
from app.services.auth_service import hash_password

# Colorize output (with fallback for Windows)
def log_info(msg: str):
    print(f"[INFO] {msg}")

def log_success(msg: str):
    print(f"[OK] {msg}")

def log_warning(msg: str):
    print(f"[WARN] {msg}")

def log_error(msg: str):
    print(f"[ERROR] {msg}")


def create_admin_user(db):
    """Crea usuario admin si no existe."""
    log_info("Verificando usuario admin...")
    
    admin = get_user_by_email(db, "admin@test.com")
    if admin:
        log_warning(f"Usuario admin ya existe (ID: {admin.id})")
        return admin
    
    log_info("Creando usuario admin@test.com...")
    admin = create_user(
        db,
        email="admin@test.com",
        password="admin123",
        name="admin",
        role=UserRole.ADMIN
    )
    log_success(f"Usuario admin creado (ID: {admin.id})")
    return admin


def create_demo_user(db):
    """Crea usuario demo si no existe."""
    log_info("Verificando usuario demo...")
    
    user = get_user_by_email(db, "user@test.com")
    if user:
        log_warning(f"Usuario demo ya existe (ID: {user.id})")
        return user
    
    log_info("Creando usuario user@test.com...")
    user = create_user(
        db,
        email="user@test.com",
        password="user123",
        name="Demo User",
        role=UserRole.USER
    )
    log_success(f"Usuario demo creado (ID: {user.id})")
    return user


def create_demo_crops(db, owner: Optional[User] = None):
    """Crea cultivos de ejemplo."""
    log_info("Creando cultivos de ejemplo...")
    
    crops_data = [
        {
            "name": "Tomate",
            "description": "Cultivo de tomates rojo intenso, ideal para huerto urbano",
            "crop_type": "verdura",
            "is_public": True,
            "owner_id": None,  # Público del sistema
        },
        {
            "name": "Lechuga",
            "description": "Lechuga fresca de hoja larga, cosecha rápida",
            "crop_type": "verdura",
            "is_public": True,
            "owner_id": None,
        },
        {
            "name": "Zanahoria",
            "description": "Zanahoria naranja dulce para invierno",
            "crop_type": "raíz",
            "is_public": True,
            "owner_id": None,
        },
        {
            "name": "Pimiento",
            "description": "Pimiento colorido para ensaladas y cocina",
            "crop_type": "verdura",
            "is_public": True,
            "owner_id": None,
        },
        {
            "name": "Fresa",
            "description": "Fresas dulces para postre",
            "crop_type": "fruta",
            "is_public": True,
            "owner_id": None,
        },
    ]
    
    if owner:
        crops_data.extend([
            {
                "name": "Mi Tomate",
                "description": "Cultivo privado de tomate del usuario",
                "crop_type": "verdura",
                "is_public": False,
                "owner_id": owner.id,
            },
            {
                "name": "Mi Lechuga",
                "description": "Cultivo privado de lechuga del usuario",
                "crop_type": "verdura",
                "is_public": False,
                "owner_id": owner.id,
            },
        ])
    
    created_crops = []
    for crop_data in crops_data:
        existing = db.query(Crop).filter(Crop.name == crop_data["name"]).first()
        if existing:
            log_warning(f"Cultivo '{crop_data['name']}' ya existe (ID: {existing.id})")
            created_crops.append(existing)
            continue
        
        crop = Crop(**crop_data)
        db.add(crop)
        db.flush()
        
        # Crear riego y requisitos ambientales por defecto
        if not crop.irrigation:
            irrigation = IrrigationAttributes(
                crop_id=crop.id,
                water_frequency_days=3,
                water_amount_mm=25,
                irrigation_type="riego por goteo",
                notes="Aumentar en verano"
            )
            db.add(irrigation)
        
        if not crop.environmental:
            environmental = EnvironmentalRequirements(
                crop_id=crop.id,
                min_temperature_celsius=15,
                max_temperature_celsius=25,
                min_humidity_percent=50,
                max_humidity_percent=80,
                sunlight_hours_per_day=6,
                soil_type="Fértil bien drenado",
                soil_ph_min=6.0,
                soil_ph_max=7.0
            )
            db.add(environmental)
        
        db.commit()
        db.refresh(crop)
        log_success(f"Cultivo '{crop.name}' creado (ID: {crop.id})")
        created_crops.append(crop)
    
    return created_crops


def create_demo_calendars(db, crops: list):
    """Crea calendarios de siembra para cultivos."""
    log_info("Creando calendarios de siembra...")
    
    calendars_data = [
        {
            "crop_index": 0,  # Tomate
            "planting_start": date(2024, 3, 1),
            "planting_end": date(2024, 4, 15),
            "transplant_start": date(2024, 4, 20),
            "transplant_end": date(2024, 5, 10),
            "harvest_start": date(2024, 7, 1),
            "harvest_end": date(2024, 10, 31),
        },
        {
            "crop_index": 1,  # Lechuga
            "planting_start": date(2024, 2, 1),
            "planting_end": date(2024, 3, 31),
            "transplant_start": date(2024, 3, 15),
            "transplant_end": date(2024, 4, 15),
            "harvest_start": date(2024, 4, 1),
            "harvest_end": date(2024, 5, 31),
        },
        {
            "crop_index": 2,  # Zanahoria
            "planting_start": date(2024, 4, 1),
            "planting_end": date(2024, 5, 31),
            "transplant_start": None,
            "transplant_end": None,
            "harvest_start": date(2024, 8, 1),
            "harvest_end": date(2024, 11, 30),
        },
    ]
    
    created_calendars = []
    for cal_data in calendars_data:
        crop_idx = cal_data.pop("crop_index")
        if crop_idx >= len(crops):
            continue
        
        crop = crops[crop_idx]
        
        existing = db.query(PlantingCalendar).filter(PlantingCalendar.crop_id == crop.id).first()
        if existing:
            log_warning(f"Calendario para '{crop.name}' ya existe (ID: {existing.id})")
            created_calendars.append(existing)
            continue
        
        calendar = PlantingCalendar(crop_id=crop.id, **cal_data)
        db.add(calendar)
        db.commit()
        db.refresh(calendar)
        log_success(f"Calendario para '{crop.name}' creado (ID: {calendar.id})")
        created_calendars.append(calendar)
    
    return created_calendars


def create_demo_tasks(db, owner: User):
    """Crea tareas de ejemplo para el usuario."""
    log_info("Creando tareas de ejemplo...")
    
    today = date.today()
    tasks_data = [
        {
            "title": "Regar tomates",
            "description": "Riego matutino de 5 litros",
            "status": TaskStatus.PENDING,
            "due_date": (today + timedelta(days=1)).isoformat(),
        },
        {
            "title": "Revisar plagas",
            "description": "Inspeccionar hojas de lechuga",
            "status": TaskStatus.PENDING,
            "due_date": (today + timedelta(days=2)).isoformat(),
        },
        {
            "title": "Preparar abono",
            "description": "Preparar mezcla de abono para aplicar",
            "status": TaskStatus.COMPLETED,
            "due_date": today.isoformat(),
        },
        {
            "title": "Trasplante de pepino",
            "description": "Trasplantar al huerto principal",
            "status": TaskStatus.PENDING,
            "due_date": (today + timedelta(days=7)).isoformat(),
        },
    ]
    
    created_tasks = []
    for idx, task_data in enumerate(tasks_data):
        existing = db.query(Task).filter(
            Task.owner_id == owner.id,
            Task.title == task_data["title"]
        ).first()
        
        if existing:
            log_warning(f"Tarea '{task_data['title']}' ya existe (ID: {existing.id})")
            created_tasks.append(existing)
            continue
        
        task = Task(owner_id=owner.id, **task_data)
        db.add(task)
        db.commit()
        db.refresh(task)
        log_success(f"Tarea '{task.title}' creada (ID: {task.id})")
        created_tasks.append(task)
    
    return created_tasks


def seed_database():
    """Ejecuta el seed completo."""
    log_info("=" * 60)
    log_info("Iniciando FASE 10: Seed de Datos Demo")
    log_info("=" * 60)
    
    db = SessionLocal()
    try:
        # 1. Crear usuario admin
        admin = create_admin_user(db)
        
        # 2. Crear usuario demo
        demo_user = create_demo_user(db)
        
        # 3. Crear cultivos públicos (sin owner) y privados (con owner)
        crops = create_demo_crops(db, owner=demo_user)
        
        # 4. Crear calendarios de siembra
        calendars = create_demo_calendars(db, crops)
        
        # 5. Crear tareas para el usuario demo
        tasks = create_demo_tasks(db, demo_user)
        
        log_success("=" * 60)
        log_success("Seed completado exitosamente")
        log_success("=" * 60)
        log_info(f"Admin creado/verificado: {admin.email}")
        log_info(f"Usuario demo creado/verificado: {demo_user.email}")
        log_info(f"Cultivos creados/verificados: {len(crops)}")
        log_info(f"Calendarios creados/verificados: {len(calendars)}")
        log_info(f"Tareas creadas/verificadas: {len(tasks)}")
        log_info("")
        log_info("Puedes ahora:")
        log_info(f"  1. Login como admin: admin@test.com / admin123")
        log_info(f"  2. Login como user: user@test.com / user123")
        log_info(f"  3. Ver cultivos, tareas y calendarios en el frontend")
        
    except Exception as e:
        log_error(f"Error durante seed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


def clean_demo_data(db, keep_admin: bool = True):
    """Limpia datos de demostración (mantiene o no admin según keep_admin)."""
    log_info("Limpiando datos de demostración...")
    
    try:
        # Eliminar tareas de demo_user
        demo_user = get_user_by_email(db, "user@test.com")
        if demo_user:
            db.query(Task).filter(Task.owner_id == demo_user.id).delete()
            log_success("Tareas demo eliminadas")
        
        # Eliminar calendarios
        db.query(PlantingCalendar).delete()
        log_success("Calendarios eliminados")
        
        # Eliminar cultivos privados del demo_user
        if demo_user:
            db.query(Crop).filter(Crop.owner_id == demo_user.id).delete()
            log_success("Cultivos privados demo eliminados")
        
        # Eliminar cultivos públicos
        db.query(Crop).delete()
        log_success("Cultivos públicos eliminados")
        
        # Eliminar usuario demo
        if demo_user:
            db.delete(demo_user)
            log_success("Usuario demo eliminado")
        
        # Opcionalmente eliminar admin
        if not keep_admin:
            admin = get_user_by_email(db, "admin@test.com")
            if admin:
                db.delete(admin)
                log_success("Usuario admin eliminado")
        
        db.commit()
        log_success("Limpieza completada")
        
    except Exception as e:
        log_error(f"Error durante limpieza: {e}")
        db.rollback()
        raise


def main():
    """Punto de entrada principal."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--clean":
            log_info("Modo: Limpiar demo data (mantener admin)")
            db = SessionLocal()
            try:
                clean_demo_data(db, keep_admin=True)
            finally:
                db.close()
            return
        
        elif sys.argv[1] == "--reset":
            log_info("Modo: Reset completo (eliminar TODO incluyendo admin)")
            db = SessionLocal()
            try:
                clean_demo_data(db, keep_admin=False)
            finally:
                db.close()
            log_info("Ahora ejecuta nuevamente: python scripts/seed_demo.py")
            return
        
        else:
            print("Opciones válidas:")
            print("  python scripts/seed_demo.py          # Crear datos demo")
            print("  python scripts/seed_demo.py --clean  # Limpiar demo (mantener admin)")
            print("  python scripts/seed_demo.py --reset  # Reset completo (admin + todo)")
            sys.exit(1)
    
    # Modo normal: seed
    seed_database()


if __name__ == "__main__":
    main()
