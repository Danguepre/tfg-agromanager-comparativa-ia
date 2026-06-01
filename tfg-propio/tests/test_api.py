import os
import unittest
from datetime import date
from pathlib import Path

os.environ["APP_ENV"] = "test"
os.environ["RUN_SEED"] = "0"
os.environ["DATABASE_URL"] = f"sqlite:///./test_app_{os.getpid()}.db"
os.environ["FRONTEND_URL"] = "http://127.0.0.1:5173"
os.environ["GOOGLE_CLIENT_ID"] = "test-client-id"
os.environ["GOOGLE_CLIENT_SECRET"] = "test-client-secret"
os.environ["GOOGLE_OAUTH_REDIRECT"] = "http://127.0.0.1:8000/auth/google/callback"

from fastapi.testclient import TestClient

from app.auth import hash_password
from app.database import Base, SessionLocal, engine
from app.main import app
from app.models.crop import Crop
from app.models.environmental_requirements import EnvironmentalRequirements
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.planting_calendar import PlantingCalendar
from app.models.task import Task
from app.models.task_crop import TaskCrop
from app.models.user import User


class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()
        self.seed_base_data()

    def tearDown(self):
        self.db.close()

    def seed_base_data(self):
        self.admin = User(
            name="Admin",
            email="admin@example.com",
            password=hash_password("1234"),
            location="Admin",
            role="admin",
        )
        self.user = User(
            name="User",
            email="user@example.com",
            password=hash_password("1234"),
            location="Madrid",
            role="user",
        )
        self.other_user = User(
            name="Other",
            email="other@example.com",
            password=hash_password("1234"),
            location="Sevilla",
            role="user",
        )
        self.db.add_all([self.admin, self.user, self.other_user])
        self.db.flush()

        self.catalog_tomato = self.create_crop(
            name="Tomate Roma",
            type="hortaliza",
            user_id=None,
            is_public=True,
        )
        self.catalog_lettuce = self.create_crop(
            name="Lechuga Batavia",
            type="hoja",
            user_id=None,
            is_public=True,
        )
        self.user_crop = self.create_crop(
            name="Pimiento Usuario",
            type="hortaliza",
            user_id=self.user.id,
            is_public=False,
            with_calendar=True,
        )
        self.other_crop = self.create_crop(
            name="Fresa Otro",
            type="fruta",
            user_id=self.other_user.id,
            is_public=False,
            with_calendar=True,
        )
        self.incomplete_crop = self.create_crop(
            name="Ajo Incompleto",
            type="bulbo",
            user_id=self.user.id,
            is_public=False,
            with_calendar=False,
        )
        self.db.commit()

    def create_crop(self, name, type, user_id, is_public, source_crop_id=None, with_calendar=False):
        crop = Crop(
            name=name,
            type=type,
            life_cycle="anual",
            image_url=None,
            user_id=user_id,
            is_public=is_public,
            source_crop_id=source_crop_id,
        )
        self.db.add(crop)
        self.db.flush()
        self.db.add(IrrigationAttributes(
            crop_id=crop.id,
            watering_frequency="daily",
            water_amount=1.0,
            recommendations="Riego de prueba",
        ))
        self.db.add(EnvironmentalRequirements(
            crop_id=crop.id,
            sun_exposure="full_sun",
            min_temp=10,
            max_temp=30,
            frost_tolerance=False,
        ))
        if with_calendar:
            self.db.add(PlantingCalendar(
                crop_id=crop.id,
                planting_start=date(2000, 3, 1),
                planting_end=date(2000, 3, 1),
                transplant_start=date(2000, 4, 16),
                transplant_end=date(2000, 4, 16),
                harvest_start=date(2000, 8, 1),
                harvest_end=date(2000, 8, 1),
                is_active=False,
                current_phase_index=0,
                status="draft",
            ))
        return crop

    def auth_headers(self, email, password="1234"):
        response = self.client.post("/auth/login", json={"email": email, "password": password})
        self.assertEqual(response.status_code, 200, response.text)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}


class SmokeAndAuthTests(ApiTestCase):
    def test_backend_root_and_frontend_build_artifact_are_available(self):
        root = self.client.get("/")
        self.assertEqual(root.status_code, 200)
        self.assertIn("message", root.json())
        self.assertTrue(Path("frontend/package.json").exists())

    def test_register_login_invalid_login_and_protected_access(self):
        register = self.client.post("/users/", json={
            "name": "Nuevo",
            "email": "nuevo@example.com",
            "password": "1234",
            "location": "Valencia",
        })
        self.assertEqual(register.status_code, 200, register.text)
        self.assertNotIn("password", register.json())

        login = self.client.post("/auth/login", json={"email": "nuevo@example.com", "password": "1234"})
        self.assertEqual(login.status_code, 200)
        self.assertIn("access_token", login.json())

        bad_login = self.client.post("/auth/login", json={"email": "nuevo@example.com", "password": "bad"})
        self.assertEqual(bad_login.status_code, 400)

        no_token = self.client.get("/crops/")
        self.assertEqual(no_token.status_code, 401)

        bad_token = self.client.get("/crops/", headers={"Authorization": "Bearer invalid.token.value"})
        self.assertEqual(bad_token.status_code, 401)

        with_token = self.client.get("/crops/", headers=self.auth_headers("nuevo@example.com"))
        self.assertEqual(with_token.status_code, 200)

    def test_google_login_starts_oauth_without_exchanging_network_token(self):
        response = self.client.get("/auth/google", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.google.com", response.headers["location"])


class DashboardTests(ApiTestCase):
    def test_dashboard_summary_is_personal_and_does_not_leak_other_user_data(self):
        task = Task(
            user_id=self.user.id,
            name="Regar tomates",
            description="Pendiente del usuario",
            status="pending",
        )
        other_task = Task(
            user_id=self.other_user.id,
            name="Tarea ajena",
            description="No debe aparecer",
            status="pending",
        )
        self.db.add_all([task, other_task])
        self.db.flush()
        self.db.add(TaskCrop(task_id=task.id, crop_id=self.user_crop.id))
        self.db.commit()

        headers = self.auth_headers("user@example.com")
        activate = self.client.post(f"/calendar/crop/{self.user_crop.id}/activate", headers=headers)
        self.assertEqual(activate.status_code, 200)

        summary = self.client.get("/dashboard/summary", headers=headers)
        self.assertEqual(summary.status_code, 200)
        data = summary.json()

        self.assertEqual(data["crops_count"], 2)
        self.assertEqual(data["active_calendar_count"], 1)
        self.assertEqual(data["pending_tasks_count"], 1)
        self.assertEqual(data["overdue_tasks_count"], 0)
        self.assertEqual(data["incomplete_phase_crops_count"], 1)
        self.assertEqual(data["pending_tasks"][0]["name"], "Regar tomates")
        self.assertNotIn("Tarea ajena", str(data))
        self.assertTrue(all(item["crop_id"] != self.other_crop.id for item in data["active_calendars"]))


class AdminTests(ApiTestCase):
    def test_admin_endpoints_are_forbidden_to_normal_users(self):
        user_headers = self.auth_headers("user@example.com")
        for path in ["/admin/summary", "/admin/users", "/admin/crops"]:
            response = self.client.get(path, headers=user_headers)
            self.assertEqual(response.status_code, 403, path)

    def test_admin_can_manage_users_without_exposing_passwords_or_losing_last_admin(self):
        admin_headers = self.auth_headers("admin@example.com")

        users = self.client.get("/admin/users", headers=admin_headers)
        self.assertEqual(users.status_code, 200)
        self.assertGreaterEqual(users.json()["total"], 3)
        self.assertNotIn("password", users.json()["items"][0])

        created = self.client.post("/admin/users", headers=admin_headers, json={
            "name": "Temporal",
            "email": "temporal@example.com",
            "location": "Test",
            "role": "user",
            "password": "1234",
        })
        self.assertEqual(created.status_code, 200, created.text)
        user_id = created.json()["id"]

        updated = self.client.put(f"/admin/users/{user_id}", headers=admin_headers, json={
            "name": "Temporal Admin",
            "email": "temporal@example.com",
            "location": "Test",
            "role": "admin",
        })
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["role"], "admin")

        delete_self = self.client.delete(f"/admin/users/{self.admin.id}", headers=admin_headers)
        self.assertEqual(delete_self.status_code, 400)

        deleted = self.client.delete(f"/admin/users/{user_id}", headers=admin_headers)
        self.assertEqual(deleted.status_code, 200)

    def test_admin_can_manage_crops(self):
        admin_headers = self.auth_headers("admin@example.com")
        payload = self.admin_crop_payload(name="Admin Calabacin", user_id=self.user.id, is_public=True)

        created = self.client.post("/admin/crops", headers=admin_headers, json=payload)
        self.assertEqual(created.status_code, 200, created.text)
        crop_id = created.json()["id"]

        payload["name"] = "Admin Calabacin Editado"
        payload["calendar"]["transplant_start"] = "2000-05-16"
        updated = self.client.put(f"/admin/crops/{crop_id}", headers=admin_headers, json=payload)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["name"], "Admin Calabacin Editado")
        self.assertEqual(updated.json()["calendar"]["transplant_start"], "2000-05-16")

        listed = self.client.get("/admin/crops?name=Calabacin&page=1&page_size=25", headers=admin_headers)
        self.assertEqual(listed.status_code, 200)
        self.assertLessEqual(len(listed.json()["items"]), 25)

        deleted = self.client.delete(f"/admin/crops/{crop_id}", headers=admin_headers)
        self.assertEqual(deleted.status_code, 200)

    def admin_crop_payload(self, name, user_id, is_public):
        return {
            "name": name,
            "type": "hortaliza",
            "life_cycle": "anual",
            "image_url": None,
            "user_id": user_id,
            "is_public": is_public,
            "source_crop_id": None,
            "irrigation": {
                "watering_frequency": "weekly",
                "water_amount": 2.5,
                "recommendations": "Riego semanal",
            },
            "environmental": {
                "sun_exposure": "partial",
                "min_temp": 8,
                "max_temp": 25,
                "frost_tolerance": False,
            },
            "calendar": {
                "planting_start": "2000-03-01",
                "planting_end": "2000-03-01",
                "transplant_start": "2000-04-16",
                "transplant_end": "2000-04-16",
                "harvest_start": "2000-08-01",
                "harvest_end": "2000-08-01",
                "is_active": False,
                "current_phase_index": 0,
                "status": "draft",
            },
        }


class CatalogAndMyCropsTests(ApiTestCase):
    def test_catalog_filters_and_pagination(self):
        headers = self.auth_headers("user@example.com")
        by_name = self.client.get("/crops/published?name=Tomate&page=1&page_size=1", headers=headers)
        self.assertEqual(by_name.status_code, 200)
        self.assertEqual(by_name.json()["total"], 1)
        self.assertEqual(by_name.json()["items"][0]["name"], "Tomate Roma")

        by_type = self.client.get("/crops/published?type=hoja", headers=headers)
        self.assertEqual(by_type.status_code, 200)
        self.assertEqual(by_type.json()["items"][0]["type"], "hoja")

        combined = self.client.get("/crops/published?name=Tomate&type=hortaliza", headers=headers)
        self.assertEqual(combined.status_code, 200)
        self.assertEqual(combined.json()["total"], 1)

        page_two = self.client.get("/crops/published?page=2&page_size=1&type=hortaliza", headers=headers)
        self.assertEqual(page_two.status_code, 200)
        self.assertEqual(page_two.json()["page"], 2)

    def test_user_can_copy_catalog_crop_and_copy_is_independent(self):
        headers = self.auth_headers("user@example.com")
        copied = self.client.post(f"/crops/{self.catalog_tomato.id}/add-to-my-crops", headers=headers)
        self.assertEqual(copied.status_code, 200, copied.text)
        copy_id = copied.json()["id"]
        self.assertEqual(copied.json()["source_crop_id"], self.catalog_tomato.id)

        update = self.client.put(f"/crops/{copy_id}", headers=headers, json={
            "name": "Tomate Copia Usuario",
            "type": "hortaliza editada",
            "life_cycle": "anual",
            "image_url": None,
            "user_id": self.user.id,
            "is_public": False,
            "source_crop_id": self.catalog_tomato.id,
        })
        self.assertEqual(update.status_code, 200)

        original = self.client.get(f"/crops/{self.catalog_tomato.id}", headers=self.auth_headers("admin@example.com"))
        self.assertEqual(original.status_code, 200)
        self.assertEqual(original.json()["name"], "Tomate Roma")

    def test_my_crops_are_user_scoped_and_permissions_are_enforced(self):
        user_headers = self.auth_headers("user@example.com")
        other_headers = self.auth_headers("other@example.com")

        mine = self.client.get("/crops/my?page=1&page_size=25", headers=user_headers)
        self.assertEqual(mine.status_code, 200)
        self.assertTrue(all(crop["user_id"] == self.user.id for crop in mine.json()["items"]))

        edit_other = self.client.put(f"/crops/{self.other_crop.id}", headers=user_headers, json={
            "name": "Hack",
            "type": "fruta",
            "life_cycle": "anual",
            "image_url": None,
            "user_id": self.other_user.id,
            "is_public": False,
            "source_crop_id": None,
        })
        self.assertEqual(edit_other.status_code, 403)

        delete_other = self.client.delete(f"/crops/{self.user_crop.id}", headers=other_headers)
        self.assertEqual(delete_other.status_code, 403)

    def test_removing_original_from_my_crops_keeps_it_in_catalog(self):
        headers = self.auth_headers("user@example.com")
        remove = self.client.delete(f"/crops/{self.user_crop.id}", headers=headers)
        self.assertEqual(remove.status_code, 200)

        admin_headers = self.auth_headers("admin@example.com")
        crop = self.client.get(f"/crops/{self.user_crop.id}", headers=admin_headers)
        self.assertEqual(crop.status_code, 200)
        self.assertIsNone(crop.json()["user_id"])
        self.assertTrue(crop.json()["is_public"])


class CalendarTests(ApiTestCase):
    def test_backend_rejects_incomplete_calendar_activation(self):
        headers = self.auth_headers("user@example.com")
        activate = self.client.post(f"/calendar/crop/{self.incomplete_crop.id}/activate", headers=headers)
        self.assertEqual(activate.status_code, 400)

    def test_complete_calendar_activates_shows_current_phase_and_advances(self):
        headers = self.auth_headers("user@example.com")
        activate = self.client.post(f"/calendar/crop/{self.user_crop.id}/activate", headers=headers)
        self.assertEqual(activate.status_code, 200)
        self.assertTrue(activate.json()["is_active"])
        self.assertEqual(activate.json()["current_phase_index"], 0)

        events = self.client.get("/calendar/events", headers=headers)
        self.assertEqual(events.status_code, 200)
        self.assertEqual(len(events.json()), 1)
        self.assertEqual(events.json()[0]["phase"], "Siembra")
        self.assertEqual(events.json()[0]["month"], 3)
        self.assertEqual(events.json()[0]["half"], 1)

        advance = self.client.post(f"/calendar/crop/{self.user_crop.id}/advance", headers=headers)
        self.assertEqual(advance.status_code, 200)
        self.assertEqual(advance.json()["current_phase_index"], 1)

        advanced_events = self.client.get("/calendar/events", headers=headers)
        self.assertEqual(len(advanced_events.json()), 1)
        self.assertEqual(advanced_events.json()[0]["phase"], "Trasplante")
        self.assertEqual(advanced_events.json()[0]["month"], 4)
        self.assertEqual(advanced_events.json()[0]["half"], 2)

        self.client.post(f"/calendar/crop/{self.user_crop.id}/advance", headers=headers)
        completed = self.client.post(f"/calendar/crop/{self.user_crop.id}/advance", headers=headers)
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.json()["status"], "completed")
        self.assertFalse(completed.json()["is_active"])

    def test_calendar_permissions_and_year_independence(self):
        user_headers = self.auth_headers("user@example.com")
        other_headers = self.auth_headers("other@example.com")

        forbidden = self.client.post(f"/calendar/crop/{self.other_crop.id}/advance", headers=user_headers)
        self.assertEqual(forbidden.status_code, 403)

        update = self.client.put(f"/calendar/crop/{self.user_crop.id}", headers=user_headers, json={
            "crop_id": self.user_crop.id,
            "planting_start": "2024-03-16",
            "planting_end": "2024-03-16",
            "transplant_start": "2030-04-01",
            "transplant_end": "2030-04-01",
            "harvest_start": "1999-09-16",
            "harvest_end": "1999-09-16",
        })
        self.assertEqual(update.status_code, 200)
        self.client.post(f"/calendar/crop/{self.user_crop.id}/activate", headers=user_headers)
        events = self.client.get("/calendar/events", headers=user_headers)
        self.assertEqual(events.json()[0]["month"], 3)
        self.assertEqual(events.json()[0]["half"], 2)

        other_events = self.client.get("/calendar/events", headers=other_headers)
        self.assertEqual(other_events.status_code, 200)


if __name__ == "__main__":
    unittest.main()
