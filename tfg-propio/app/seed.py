from datetime import date, datetime
from pathlib import Path


def seed_data():
    from app.auth import hash_password
    from app.database import SessionLocal
    from app.models import (
        Crop,
        EnvironmentalRequirements,
        IrrigationAttributes,
        PlantingCalendar,
        Task,
        TaskCrop,
        User,
    )
    db = SessionLocal()
    if db.query(User).filter(User.email == "admin@test.com").first():
        print("Seed omitido: los datos de ejemplo ya existen")
        db.close()
        return

    names = ["Dani", "Ana", "Luis", "Marta", "Carlos", "Lucia", "Javier"]
    locations = ["Sevilla", "Madrid", "Valencia", "Granada", "Bilbao"]

    users = [
        User(
            name="Admin",
            email="admin@test.com",
            password=hash_password("admin123"),
            location="Admin",
            role="admin",
            created_at=datetime.utcnow(),
        )
    ]

    for index, name in enumerate(names):
        users.append(
            User(
                name=name,
                email=f"{name.lower()}@test.com",
                password=hash_password(f"{name.lower()}123"),
                location=locations[index % len(locations)],
                created_at=datetime.utcnow(),
            )
        )

    db.add_all(users)
    db.commit()

    crop_catalog = [
        {"name": "Tomate", "type": "hortaliza", "life_cycle": "anual"},
        {"name": "Lechuga", "type": "hoja", "life_cycle": "anual"},
        {"name": "Zanahoria", "type": "raiz", "life_cycle": "bienal"},
        {"name": "Patata", "type": "tuberculo", "life_cycle": "anual"},
        {"name": "Cebolla", "type": "bulbo", "life_cycle": "bienal"},
        {"name": "Pimiento", "type": "hortaliza", "life_cycle": "anual"},
        {"name": "Pepino", "type": "hortaliza", "life_cycle": "anual"},
        {"name": "Calabacin", "type": "hortaliza", "life_cycle": "anual"},
        {"name": "Berenjena", "type": "hortaliza", "life_cycle": "anual"},
        {"name": "Espinaca", "type": "hoja", "life_cycle": "anual"},
        {"name": "Ajo", "type": "bulbo", "life_cycle": "anual"},
        {"name": "Maiz", "type": "cereal", "life_cycle": "anual"},
        {"name": "Trigo", "type": "cereal", "life_cycle": "anual"},
        {"name": "Fresa", "type": "fruta", "life_cycle": "perenne"},
        {"name": "Melon", "type": "fruta", "life_cycle": "anual"},
        {"name": "Sandia", "type": "fruta", "life_cycle": "anual"},
        {"name": "Albahaca", "type": "aromatica", "life_cycle": "anual"},
        {"name": "Perejil", "type": "aromatica", "life_cycle": "bienal"},
        {"name": "Romero", "type": "aromatica", "life_cycle": "perenne"},
        {"name": "Lavanda", "type": "aromatica", "life_cycle": "perenne"},
    ]

    crops = []
    for crop_data in crop_catalog:
        crops.append(
            Crop(
                name=crop_data["name"],
                type=crop_data["type"],
                life_cycle=crop_data["life_cycle"],
                image_url=get_seed_crop_image_url(crop_data["name"]),
                user_id=None,
                is_public=True,
            )
        )

    db.add_all(crops)
    db.commit()

    calendars = []
    for index, crop in enumerate(crops):
        planting_month = (index % 3) + 1
        harvest_month = ((index + 5) % 5) + 6
        calendars.append(
            PlantingCalendar(
                crop_id=crop.id,
                planting_start=date(2026, planting_month, 1),
                planting_end=date(2026, planting_month + 2, 28),
                transplant_start=None,
                transplant_end=None,
                harvest_start=date(2026, harvest_month, 1),
                harvest_end=date(2026, min(harvest_month + 2, 12), 28),
            )
        )

    db.add_all(calendars)

    envs = []
    for index, crop in enumerate(crops):
        envs.append(
            EnvironmentalRequirements(
                crop_id=crop.id,
                sun_exposure=["full_sun", "partial", "shade"][index % 3],
                min_temp=6 + (index % 8),
                max_temp=22 + (index % 12),
                frost_tolerance=index % 4 == 0,
            )
        )

    db.add_all(envs)

    irrigations = []
    watering_options = ["daily", "2 times/week", "3 times/week"]
    for index, crop in enumerate(crops):
        irrigations.append(
            IrrigationAttributes(
                crop_id=crop.id,
                watering_frequency=watering_options[index % len(watering_options)],
                water_amount=round(0.8 + (index % 7) * 0.35, 2),
                recommendations="Riego moderado segun humedad del suelo",
            )
        )

    db.add_all(irrigations)
    db.commit()

    crop_by_name = {crop.name: crop for crop in crops}
    regular_users = [user for user in users if user.role != "admin"]
    task_seed_data = [
        {
            "user_index": 0,
            "crop": "Tomate",
            "name": "Revisar tomate",
            "description": "Comprobar que las plantas estan bien sujetas y retirar brotes laterales excesivos.",
            "status": "pending",
        },
        {
            "user_index": 1,
            "crop": "Lechuga",
            "name": "Riego ligero de lechuga",
            "description": "Mantener humedad constante sin encharcar la zona de raices.",
            "status": "in_progress",
        },
        {
            "user_index": 2,
            "crop": "Patata",
            "name": "Aporcar patatas",
            "description": "Cubrir la base de las plantas para proteger tuberculos y mejorar el desarrollo.",
            "status": "pending",
        },
        {
            "user_index": 3,
            "crop": "Pimiento",
            "name": "Revisar pulgon en pimiento",
            "description": "Inspeccionar el enves de las hojas y registrar si hace falta tratamiento.",
            "status": "pending",
        },
        {
            "user_index": 4,
            "crop": "Fresa",
            "name": "Retirar hojas secas de fresa",
            "description": "Eliminar hojas danadas para mejorar ventilacion y reducir enfermedades.",
            "status": "completed",
        },
        {
            "user_index": 5,
            "crop": "Maiz",
            "name": "Comprobar humedad del maiz",
            "description": "Revisar humedad del suelo antes de programar el siguiente riego.",
            "status": "in_progress",
        },
        {
            "user_index": 6,
            "crop": "Albahaca",
            "name": "Pinzar albahaca",
            "description": "Cortar puntas de crecimiento para favorecer una planta mas frondosa.",
            "status": "pending",
        },
        {
            "user_index": 0,
            "crop": "Lavanda",
            "name": "Poda suave de lavanda",
            "description": "Recortar flores secas y mantener forma compacta sin cortar madera vieja.",
            "status": "completed",
        },
    ]

    user_crop_by_key = {}
    for task_data in task_seed_data:
        user = regular_users[task_data["user_index"] % len(regular_users)]
        source_crop = crop_by_name[task_data["crop"]]
        key = (user.id, source_crop.name)

        if key in user_crop_by_key:
            continue

        user_crop = Crop(
            name=source_crop.name,
            type=source_crop.type,
            life_cycle=source_crop.life_cycle,
            image_url=source_crop.image_url,
            user_id=user.id,
            is_public=False,
            source_crop_id=source_crop.id,
        )
        db.add(user_crop)
        db.flush()

        if source_crop.calendar:
            is_dani_demo_crop = user.email == "dani@test.com"
            db.add(
                PlantingCalendar(
                    crop_id=user_crop.id,
                    planting_start=source_crop.calendar.planting_start,
                    planting_end=source_crop.calendar.planting_end,
                    transplant_start=date(2026, 4, 1) if is_dani_demo_crop else source_crop.calendar.transplant_start,
                    transplant_end=date(2026, 4, 16) if is_dani_demo_crop else source_crop.calendar.transplant_end,
                    harvest_start=source_crop.calendar.harvest_start,
                    harvest_end=source_crop.calendar.harvest_end,
                    is_active=True if is_dani_demo_crop else source_crop.calendar.is_active,
                    current_phase_index=0 if is_dani_demo_crop else source_crop.calendar.current_phase_index,
                    status="active" if is_dani_demo_crop else source_crop.calendar.status,
                )
            )

        if source_crop.environmental:
            db.add(
                EnvironmentalRequirements(
                    crop_id=user_crop.id,
                    sun_exposure=source_crop.environmental.sun_exposure,
                    min_temp=source_crop.environmental.min_temp,
                    max_temp=source_crop.environmental.max_temp,
                    frost_tolerance=source_crop.environmental.frost_tolerance,
                )
            )

        if source_crop.irrigation:
            db.add(
                IrrigationAttributes(
                    crop_id=user_crop.id,
                    watering_frequency=source_crop.irrigation.watering_frequency,
                    water_amount=source_crop.irrigation.water_amount,
                    recommendations=source_crop.irrigation.recommendations,
                )
            )

        user_crop_by_key[key] = user_crop

    db.commit()

    tasks = []
    for task_data in task_seed_data:
        user = regular_users[task_data["user_index"] % len(regular_users)]
        tasks.append(
            Task(
                user_id=user.id,
                name=task_data["name"],
                description=task_data["description"],
                status=task_data["status"],
            )
        )

    db.add_all(tasks)
    db.commit()

    relations = []
    for task, task_data in zip(tasks, task_seed_data, strict=True):
        user = regular_users[task_data["user_index"] % len(regular_users)]
        task_crop = user_crop_by_key[(user.id, task_data["crop"])]
        relations.append(TaskCrop(task_id=task.id, crop_id=task_crop.id))

    db.add_all(relations)
    db.commit()
    db.close()


def get_seed_crop_image_url(crop_name: str) -> str | None:
    uploads_dir = Path("uploads") / "crops"
    slug = normalize_crop_image_name(crop_name)

    for extension in (".jpg", ".jpeg", ".png", ".webp"):
        image_path = uploads_dir / f"{slug}{extension}"
        if image_path.exists():
            return f"/uploads/crops/{slug}{extension}"

    return None


def normalize_crop_image_name(crop_name: str) -> str:
    replacements = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
    }
    normalized = crop_name.strip().lower()
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized.replace(" ", "-")
