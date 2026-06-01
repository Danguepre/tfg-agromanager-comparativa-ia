def seed_data():
    from app.database import SessionLocal
    from app.models import (
        User, Crop,
        PlantingCalendar,
        EnvironmentalRequirements,
        IrrigationAttributes,
        Task, TaskCrop
    )
    from app.auth import hash_password
    from datetime import datetime, date
    import random

    db = SessionLocal()

    names = ["Dani", "Ana", "Luis", "Marta", "Carlos", "Lucia", "Javier"]
    locations = ["Sevilla", "Madrid", "Valencia", "Granada", "Bilbao"]

    users = []

    admin_user = User(
        name="Admin",
        email="admin@test.com",
        password=hash_password("1234"),
        location="Admin",
        role="admin",
        created_at=datetime.utcnow()
    )
    users.append(admin_user)

    for i, name in enumerate(names):
        user = User(
            name=name,
            email=f"{name.lower()}@test.com",
            password=hash_password("1234"),
            location=random.choice(locations),
            created_at=datetime.utcnow()
        )
        users.append(user)

    db.add_all(users)
    db.commit()

    crop_catalog = [
        ("Tomate", "hortaliza", "anual"),
        ("Lechuga", "hoja", "anual"),
        ("Zanahoria", "raiz", "bienal"),
        ("Patata", "tuberculo", "anual"),
        ("Cebolla", "bulbo", "bienal"),
        ("Pimiento", "hortaliza", "anual"),
        ("Pepino", "hortaliza", "anual"),
        ("Calabacín", "hortaliza", "anual"),
        ("Berenjena", "hortaliza", "anual"),
        ("Espinaca", "hoja", "anual"),
        ("Ajo", "bulbo", "anual"),
        ("Maíz", "cereal", "anual"),
        ("Trigo", "cereal", "anual"),
        ("Fresa", "fruta", "perenne"),
        ("Melón", "fruta", "anual"),
        ("Sandía", "fruta", "anual"),
        ("Albahaca", "aromatica", "anual"),
        ("Perejil", "aromatica", "bienal"),
        ("Romero", "aromatica", "perenne"),
        ("Lavanda", "aromatica", "perenne"),
    ]

    crops = []
    for i in range(40):  
        name, type_, cycle = random.choice(crop_catalog)
        crop = Crop(
            name=f"{name} {i+1}",
            type=type_,
            life_cycle=cycle,
            user_id=random.choice(users).id
        )
        crops.append(crop)

    db.add_all(crops)
    db.commit()

    calendars = []
    for crop in crops[:25]:  # no todos tienen calendario
        calendars.append(
            PlantingCalendar(
                crop_id=crop.id,
                planting_start=date(2026, random.randint(1, 3), 1),
                planting_end=date(2026, random.randint(3, 5), 28),
                transplant_start=None,
                transplant_end=None,
                harvest_start=date(2026, random.randint(6, 8), 1),
                harvest_end=date(2026, random.randint(8, 10), 28),
            )
        )

    db.add_all(calendars)

    envs = []
    for crop in crops:
        envs.append(
            EnvironmentalRequirements(
                crop_id=crop.id,
                sun_exposure=random.choice(["full_sun", "partial", "shade"]),
                min_temp=random.randint(5, 15),
                max_temp=random.randint(20, 35),
                frost_tolerance=random.choice([True, False])
            )
        )

    db.add_all(envs)

    irrigations = []
    for crop in crops:
        irrigations.append(
            IrrigationAttributes(
                crop_id=crop.id,
                watering_frequency=random.choice(["daily", "2 times/week", "3 times/week"]),
                water_amount=round(random.uniform(0.5, 3.0), 2),
                recommendations="Riego moderado"
            )
        )

    db.add_all(irrigations)

    tasks = []
    for i in range(20):
        user = random.choice(users)
        task = Task(
            user_id=user.id,
            name=f"Tarea {i+1}",
            description="Tarea agrícola general",
            status=random.choice(["pending", "completed"])
        )
        tasks.append(task)

    db.add_all(tasks)
    db.commit()

    relations = []
    for task in tasks:
        for _ in range(random.randint(1, 3)):
            relations.append(
                TaskCrop(
                    task_id=task.id,
                    crop_id=random.choice(crops).id
                )
            )

    db.add_all(relations)
    db.commit()

    db.close()
