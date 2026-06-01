from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

import app.models  # noqa: F401
from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models.crop import Crop, CultivationGuide, EnvironmentalRequirements, IrrigationAttributes
from app.models.planting_calendar import PlantingCalendar
from app.models.task import Task, TaskCrop
from app.models.user import User


PLACEHOLDER_IMAGE_URL = "/uploads/crops/placeholder.png"


@dataclass
class SeedSummary:
    counts: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {"created": 0, "existing": 0}))

    def mark(self, category: str, created: bool) -> None:
        status = "created" if created else "existing"
        self.counts[category][status] += 1

    def lines(self) -> list[str]:
        return [
            f"{category}: {values['created']} created, {values['existing']} existing"
            for category, values in sorted(self.counts.items())
        ]


PUBLIC_CROPS = [
    {
        "name": "Tomate",
        "crop_type": "hortaliza",
        "description": "Cultivo demo de tomate para huerto de desarrollo.",
        "irrigation": {
            "water_needs": "medium-high",
            "frequency_days": 2,
            "notes": "Mantener humedad estable sin encharcar.",
            "watering_frequency": "Cada 2 dias",
            "water_amount": "Moderada",
            "recommendations": "Regar a primera hora y evitar mojar hojas.",
        },
        "environmental": {
            "climate": "templado",
            "soil_type": "rico y bien drenado",
            "sun_exposure": "sol directo",
            "min_temperature_c": 15,
            "max_temperature_c": 30,
            "frost_tolerance": False,
        },
        "guide": {
            "preparation": "Aportar compost maduro antes de plantar.",
            "sowing": "Sembrar en semillero protegido.",
            "care": "Entutorar y retirar brotes no deseados.",
            "harvest": "Cosechar cuando el fruto este rojo y firme.",
        },
    },
    {
        "name": "Lechuga",
        "crop_type": "hoja",
        "description": "Cultivo demo de lechuga para rotaciones rapidas.",
        "irrigation": {
            "water_needs": "medium",
            "frequency_days": 2,
            "notes": "Necesita humedad frecuente.",
            "watering_frequency": "Cada 2 dias",
            "water_amount": "Ligera",
            "recommendations": "Evitar sequias prolongadas para reducir espigado.",
        },
        "environmental": {
            "climate": "fresco",
            "soil_type": "suelto y fertil",
            "sun_exposure": "sol suave o semisombra",
            "min_temperature_c": 8,
            "max_temperature_c": 24,
            "frost_tolerance": True,
        },
        "guide": {
            "preparation": "Nivelar el terreno y mantenerlo mullido.",
            "sowing": "Sembrar escalonado para cosechas continuas.",
            "care": "Aclarar plantas si estan muy juntas.",
            "harvest": "Cortar hojas externas o pieza completa.",
        },
    },
    {
        "name": "Zanahoria",
        "crop_type": "raiz",
        "description": "Cultivo demo de zanahoria para suelo profundo.",
        "irrigation": {
            "water_needs": "medium",
            "frequency_days": 3,
            "notes": "Riego regular durante germinacion.",
            "watering_frequency": "Cada 3 dias",
            "water_amount": "Moderada",
            "recommendations": "Mantener el suelo humedo hasta emergencia.",
        },
        "environmental": {
            "climate": "templado",
            "soil_type": "arenoso y profundo",
            "sun_exposure": "sol directo",
            "min_temperature_c": 7,
            "max_temperature_c": 25,
            "frost_tolerance": True,
        },
        "guide": {
            "preparation": "Retirar piedras para evitar raices deformes.",
            "sowing": "Sembrar directo en lineas poco profundas.",
            "care": "Aclarar dejando espacio entre plantas.",
            "harvest": "Extraer cuando alcance calibre suficiente.",
        },
    },
    {
        "name": "Pimiento",
        "crop_type": "hortaliza",
        "description": "Cultivo demo de pimiento para temporada calida.",
        "irrigation": {
            "water_needs": "medium",
            "frequency_days": 3,
            "notes": "Prefiere riegos constantes.",
            "watering_frequency": "Cada 3 dias",
            "water_amount": "Moderada",
            "recommendations": "Aumentar riego en floracion y fruto.",
        },
        "environmental": {
            "climate": "calido",
            "soil_type": "fertil y drenado",
            "sun_exposure": "sol directo",
            "min_temperature_c": 16,
            "max_temperature_c": 32,
            "frost_tolerance": False,
        },
        "guide": {
            "preparation": "Incorporar materia organica antes del trasplante.",
            "sowing": "Sembrar en semillero con temperatura estable.",
            "care": "Proteger de frio y viento.",
            "harvest": "Recolectar verdes o maduros segun uso.",
        },
    },
    {
        "name": "Fresa",
        "crop_type": "fruto",
        "description": "Cultivo demo de fresa para bancal o maceta.",
        "irrigation": {
            "water_needs": "medium",
            "frequency_days": 2,
            "notes": "Evitar exceso de humedad en fruto.",
            "watering_frequency": "Cada 2 dias",
            "water_amount": "Ligera",
            "recommendations": "Usar acolchado para conservar humedad.",
        },
        "environmental": {
            "climate": "templado",
            "soil_type": "ligeramente acido y drenado",
            "sun_exposure": "sol directo",
            "min_temperature_c": 6,
            "max_temperature_c": 26,
            "frost_tolerance": True,
        },
        "guide": {
            "preparation": "Preparar caballones o macetas con buen drenaje.",
            "sowing": "Trasplantar plantones sanos.",
            "care": "Retirar hojas secas y controlar estolones.",
            "harvest": "Cosechar frutos rojos completamente maduros.",
        },
    },
]


PERSONAL_CROPS = [
    {
        "name": "Mi Tomate",
        "crop_type": "hortaliza",
        "description": "Tomates cherry demo del usuario.",
        "copied_from": "Tomate",
        "calendar": {
            "planting_start": date(2026, 3, 1),
            "planting_end": date(2026, 3, 15),
            "transplant_start": date(2026, 4, 15),
            "transplant_end": date(2026, 4, 30),
            "harvest_start": date(2026, 7, 1),
            "harvest_end": date(2026, 8, 31),
            "is_active": True,
            "current_phase_index": 1,
            "status": "active",
        },
    },
    {
        "name": "Mi Lechuga",
        "crop_type": "hoja",
        "description": "Lechugas demo para consumo domestico.",
        "copied_from": "Lechuga",
        "calendar": {
            "planting_start": date(2026, 1, 15),
            "planting_end": date(2026, 1, 31),
            "transplant_start": date(2026, 2, 15),
            "transplant_end": date(2026, 2, 28),
            "harvest_start": date(2026, 4, 1),
            "harvest_end": date(2026, 4, 30),
            "is_active": False,
            "current_phase_index": 2,
            "status": "completed",
        },
    },
]


TASKS = [
    {
        "name": "Revisar humedad de Mi Tomate",
        "description": "Tarea demo pendiente asociada al cultivo personal.",
        "status": "pending",
        "crop_names": ["Mi Tomate"],
    },
    {
        "name": "Entutorar Mi Tomate",
        "description": "Tarea demo pendiente para probar tareas por cultivo.",
        "status": "pending",
        "crop_names": ["Mi Tomate"],
    },
    {
        "name": "Preparar semillero de Lechuga",
        "description": "Tarea demo completada.",
        "status": "completed",
        "crop_names": ["Mi Lechuga"],
    },
    {
        "name": "Actualizar notas de riego",
        "description": "Tarea demo completada sin riesgo productivo.",
        "status": "completed",
        "crop_names": ["Mi Tomate", "Mi Lechuga"],
    },
]


def _get_or_create_user(db: Session, summary: SeedSummary, *, email: str, username: str, password: str, role: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        summary.mark("users", False)
        return user

    user = User(email=email, username=username, hashed_password=get_password_hash(password), role=role)
    db.add(user)
    db.flush()
    summary.mark("users", True)
    return user


def _get_public_crop(db: Session, name: str) -> Crop | None:
    return db.query(Crop).filter(Crop.name == name, Crop.is_public.is_(True)).first()


def _get_personal_crop(db: Session, owner_id: int, name: str) -> Crop | None:
    return db.query(Crop).filter(Crop.name == name, Crop.owner_id == owner_id, Crop.is_public.is_(False)).first()


def _ensure_irrigation(db: Session, summary: SeedSummary, crop: Crop, payload: dict[str, object]) -> None:
    if crop.irrigation_attributes:
        summary.mark("irrigation", False)
        return
    crop.irrigation_attributes = IrrigationAttributes(crop_id=crop.id, **payload)
    summary.mark("irrigation", True)


def _ensure_environmental(db: Session, summary: SeedSummary, crop: Crop, payload: dict[str, object]) -> None:
    if crop.environmental_requirements:
        summary.mark("environmental", False)
        return
    crop.environmental_requirements = EnvironmentalRequirements(crop_id=crop.id, **payload)
    summary.mark("environmental", True)


def _ensure_guide(db: Session, summary: SeedSummary, crop: Crop, payload: dict[str, object]) -> None:
    if crop.cultivation_guide:
        summary.mark("guides", False)
        return
    crop.cultivation_guide = CultivationGuide(crop_id=crop.id, **payload)
    summary.mark("guides", True)


def _ensure_calendar(db: Session, summary: SeedSummary, crop: Crop, payload: dict[str, object]) -> None:
    if crop.planting_calendar:
        summary.mark("calendars", False)
        return
    crop.planting_calendar = PlantingCalendar(crop_id=crop.id, **payload)
    summary.mark("calendars", True)


def _create_public_crops(db: Session, summary: SeedSummary, admin: User) -> dict[str, Crop]:
    crops: dict[str, Crop] = {}
    for payload in PUBLIC_CROPS:
        crop = _get_public_crop(db, payload["name"])
        if crop:
            summary.mark("crops", False)
        else:
            crop = Crop(
                name=payload["name"],
                crop_type=payload["crop_type"],
                description=payload["description"],
                image_url=PLACEHOLDER_IMAGE_URL,
                is_public=True,
                owner_id=admin.id,
            )
            db.add(crop)
            db.flush()
            summary.mark("crops", True)

        _ensure_irrigation(db, summary, crop, payload["irrigation"])
        _ensure_environmental(db, summary, crop, payload["environmental"])
        _ensure_guide(db, summary, crop, payload["guide"])
        _ensure_calendar(
            db,
            summary,
            crop,
            {
                "planting_start": date(2026, 3, 1),
                "planting_end": date(2026, 3, 31),
                "transplant_start": date(2026, 4, 15),
                "transplant_end": date(2026, 4, 30),
                "harvest_start": date(2026, 7, 1),
                "harvest_end": date(2026, 8, 31),
                "is_active": False,
                "current_phase_index": 0,
                "status": "draft",
            },
        )
        crops[crop.name] = crop
    return crops


def _copy_crop_details(db: Session, summary: SeedSummary, source: Crop, target: Crop) -> None:
    if source.irrigation_attributes:
        _ensure_irrigation(
            db,
            summary,
            target,
            {
                "water_needs": source.irrigation_attributes.water_needs,
                "frequency_days": source.irrigation_attributes.frequency_days,
                "notes": source.irrigation_attributes.notes,
                "watering_frequency": source.irrigation_attributes.watering_frequency,
                "water_amount": source.irrigation_attributes.water_amount,
                "recommendations": source.irrigation_attributes.recommendations,
            },
        )
    if source.environmental_requirements:
        _ensure_environmental(
            db,
            summary,
            target,
            {
                "climate": source.environmental_requirements.climate,
                "soil_type": source.environmental_requirements.soil_type,
                "sun_exposure": source.environmental_requirements.sun_exposure,
                "min_temperature_c": source.environmental_requirements.min_temperature_c,
                "max_temperature_c": source.environmental_requirements.max_temperature_c,
                "frost_tolerance": source.environmental_requirements.frost_tolerance,
            },
        )
    if source.cultivation_guide:
        _ensure_guide(
            db,
            summary,
            target,
            {
                "preparation": source.cultivation_guide.preparation,
                "sowing": source.cultivation_guide.sowing,
                "care": source.cultivation_guide.care,
                "harvest": source.cultivation_guide.harvest,
            },
        )


def _create_personal_crops(
    db: Session,
    summary: SeedSummary,
    user: User,
    public_crops: dict[str, Crop],
) -> dict[str, Crop]:
    crops: dict[str, Crop] = {}
    for payload in PERSONAL_CROPS:
        crop = _get_personal_crop(db, user.id, payload["name"])
        source = public_crops[payload["copied_from"]]
        if crop:
            summary.mark("crops", False)
        else:
            crop = Crop(
                name=payload["name"],
                crop_type=payload["crop_type"],
                description=payload["description"],
                image_url=source.image_url or PLACEHOLDER_IMAGE_URL,
                is_public=False,
                owner_id=user.id,
                copied_from_crop_id=source.id,
            )
            db.add(crop)
            db.flush()
            summary.mark("crops", True)

        _copy_crop_details(db, summary, source, crop)
        _ensure_calendar(db, summary, crop, payload["calendar"])
        crops[crop.name] = crop
    return crops


def _ensure_task_crops(task: Task, crops: list[Crop], summary: SeedSummary) -> None:
    existing_ids = {link.crop_id for link in task.crop_links}
    created_any = False
    for crop in crops:
        if crop.id not in existing_ids:
            task.crop_links.append(TaskCrop(crop_id=crop.id))
            existing_ids.add(crop.id)
            created_any = True
    summary.mark("task_crop_links", created_any)


def _task_table_columns(db: Session) -> set[str]:
    bind = db.get_bind()
    return {column["name"] for column in inspect(bind).get_columns("tasks")}


def _create_task(db: Session, payload: dict[str, object], user: User) -> Task:
    columns = _task_table_columns(db)
    if not {"title", "owner_id"} & columns:
        task = Task(
            user_id=user.id,
            name=payload["name"],
            description=payload["description"],
            status=payload["status"],
        )
        db.add(task)
        db.flush()
        return task

    values = {
        "user_id": user.id,
        "name": payload["name"],
        "description": payload["description"],
        "status": payload["status"],
        "created_at": datetime.now(UTC),
    }
    if "title" in columns:
        values["title"] = payload["name"]
    if "owner_id" in columns:
        values["owner_id"] = user.id

    column_names = ", ".join(values)
    parameter_names = ", ".join(f":{name}" for name in values)
    db.execute(text(f"INSERT INTO tasks ({column_names}) VALUES ({parameter_names})"), values)
    db.flush()
    return db.query(Task).filter(Task.user_id == user.id, Task.name == payload["name"]).one()


def _create_tasks(db: Session, summary: SeedSummary, user: User, personal_crops: dict[str, Crop]) -> None:
    for payload in TASKS:
        task = db.query(Task).filter(Task.user_id == user.id, Task.name == payload["name"]).first()
        if task:
            summary.mark("tasks", False)
        else:
            task = _create_task(db, payload, user)
            summary.mark("tasks", True)
        _ensure_task_crops(task, [personal_crops[name] for name in payload["crop_names"]], summary)


def seed_demo(db: Session) -> SeedSummary:
    summary = SeedSummary()
    admin = _get_or_create_user(
        db,
        summary,
        email="admin@test.com",
        username="admin",
        password="admin123",
        role="admin",
    )
    user = _get_or_create_user(
        db,
        summary,
        email="user@test.com",
        username="user",
        password="user123",
        role="user",
    )

    public_crops = _create_public_crops(db, summary, admin)
    personal_crops = _create_personal_crops(db, summary, user, public_crops)
    _create_tasks(db, summary, user, personal_crops)

    db.commit()
    return summary


def main() -> None:
    from app.main import create_app

    create_app()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        summary = seed_demo(db)
    finally:
        db.close()

    print("AgroManager demo seed completed.")
    for line in summary.lines():
        print(f"- {line}")


if __name__ == "__main__":
    main()
