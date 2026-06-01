import unittest
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, engine as app_engine, get_db
from app.main import create_app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app_phase7.db"


def register(client: TestClient, email: str, username: str, password: str, role: str = "user"):
    return client.post(
        "/users/",
        json={"email": email, "username": username, "password": password, "role": role},
    )


def login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_crop(client: TestClient, token: str, name: str, **overrides):
    data = {"name": name}
    data.update(overrides)
    response = client.post("/crops/", data=data, headers=auth_header(token))
    assert response.status_code == 201
    return response.json()


def create_task(client: TestClient, token: str, name: str, **overrides):
    payload = {"name": name, "description": "Tarea de fase 7"}
    payload.update(overrides)
    response = client.post("/tasks/", json=payload, headers=auth_header(token))
    assert response.status_code == 201
    return response.json()


def complete_calendar_payload(crop_id: int) -> dict[str, str | int]:
    return {
        "crop_id": crop_id,
        "planting_start": "2026-03-01",
        "planting_end": "2026-03-20",
        "transplant_start": "2026-04-02",
        "transplant_end": "2026-04-18",
        "harvest_start": "2026-07-10",
        "harvest_end": "2026-07-25",
    }


class Phase7DashboardAdminTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        self.testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        def override_get_db() -> Generator[Session, None, None]:
            db = self.testing_session_local()
            try:
                yield db
            finally:
                db.close()

        self.app = create_app()
        self.app.dependency_overrides[get_db] = override_get_db
        self.client_context = TestClient(self.app)
        self.client = self.client_context.__enter__()

        self.user = register(self.client, "user@example.com", "userone", "password123").json()
        self.other = register(self.client, "other@example.com", "othertwo", "password123").json()
        self.admin = register(self.client, "admin@example.com", "adminone", "password123", role="admin").json()
        self.user_token = login(self.client, "user@example.com", "password123")
        self.other_token = login(self.client, "other@example.com", "password123")
        self.admin_token = login(self.client, "admin@example.com", "password123")

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        app_engine.dispose()

    def seed_dashboard_data(self):
        user_crop = create_crop(self.client, self.user_token, "Tomate")
        other_crop = create_crop(self.client, self.other_token, "Lechuga")

        self.client.put(
            f"/calendar/crop/{user_crop['id']}",
            json=complete_calendar_payload(user_crop["id"]),
            headers=auth_header(self.user_token),
        )
        self.client.post(f"/calendar/crop/{user_crop['id']}/activate", headers=auth_header(self.user_token))
        self.client.post(
            "/irrigation/",
            json={"crop_id": user_crop["id"], "watering_frequency": "daily", "water_amount": "500ml"},
            headers=auth_header(self.user_token),
        )
        self.client.post(
            "/environmental/",
            json={"crop_id": user_crop["id"], "sun_exposure": "full sun", "min_temp": 10, "max_temp": 28},
            headers=auth_header(self.user_token),
        )
        create_task(self.client, self.user_token, "Regar", crop_ids=[user_crop["id"]])
        create_task(self.client, self.user_token, "Podar", status="completed", crop_ids=[user_crop["id"]])
        create_task(self.client, self.other_token, "Tarea ajena", crop_ids=[other_crop["id"]])
        return user_crop, other_crop

    def test_authenticated_user_can_read_dashboard_summary_and_counts(self):
        self.seed_dashboard_data()

        response = self.client.get("/dashboard/summary", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total_personal_crops"], 1)
        self.assertEqual(body["tasks_by_status"]["pending"], 1)
        self.assertEqual(body["tasks_by_status"]["completed"], 1)
        self.assertEqual(body["active_calendars_total"], 1)
        self.assertEqual(body["current_calendar_phases"][0]["phase"], "Siembra")
        self.assertEqual(body["irrigation_summary"][0]["water_amount"], "500ml")
        self.assertEqual(body["environmental_summary"][0]["sun_exposure"], "full sun")

    def test_dashboard_only_includes_current_user_data(self):
        user_crop, other_crop = self.seed_dashboard_data()

        response = self.client.get("/dashboard/summary", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        crop_ids = {item["crop_id"] for item in body["irrigation_summary"]}
        task_names = {item["name"] for item in body["upcoming_pending_tasks"]}
        self.assertIn(user_crop["id"], crop_ids)
        self.assertNotIn(other_crop["id"], crop_ids)
        self.assertEqual(task_names, {"Regar"})

    def test_dashboard_requires_token(self):
        response = self.client.get("/dashboard/summary")

        self.assertEqual(response.status_code, 401)

    def test_admin_uses_own_normal_dashboard(self):
        create_crop(self.client, self.admin_token, "Cultivo admin")
        create_crop(self.client, self.user_token, "Cultivo usuario")

        response = self.client.get("/dashboard/summary", headers=auth_header(self.admin_token))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_personal_crops"], 1)

    def test_admin_summary_allowed_and_normal_user_forbidden(self):
        self.seed_dashboard_data()

        admin_response = self.client.get("/admin/summary", headers=auth_header(self.admin_token))
        user_response = self.client.get("/admin/summary", headers=auth_header(self.user_token))

        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(admin_response.json()["total_users"], 3)
        self.assertEqual(admin_response.json()["total_tasks"], 3)
        self.assertEqual(admin_response.json()["pending_tasks"], 2)
        self.assertEqual(admin_response.json()["completed_tasks"], 1)
        self.assertEqual(admin_response.json()["total_active_calendars"], 1)
        self.assertEqual(user_response.status_code, 403)

    def test_admin_user_endpoints_do_not_expose_password_and_can_update_delete(self):
        list_response = self.client.get("/admin/users", headers=auth_header(self.admin_token))
        get_response = self.client.get(f"/admin/users/{self.user['id']}", headers=auth_header(self.admin_token))
        update_response = self.client.patch(
            f"/admin/users/{self.user['id']}",
            json={"username": "updateduser"},
            headers=auth_header(self.admin_token),
        )
        delete_target = register(self.client, "delete@example.com", "deleteuser", "password123").json()
        delete_response = self.client.delete(
            f"/admin/users/{delete_target['id']}",
            headers=auth_header(self.admin_token),
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertNotIn("password", list_response.json()[0])
        self.assertNotIn("hashed_password", list_response.json()[0])
        self.assertEqual(get_response.status_code, 200)
        self.assertNotIn("hashed_password", get_response.json())
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["username"], "updateduser")
        self.assertEqual(delete_response.status_code, 204)

    def test_normal_user_cannot_use_admin_user_endpoints(self):
        response = self.client.get("/admin/users", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 403)

    def test_admin_crop_endpoints_can_list_get_update_delete(self):
        crop = create_crop(self.client, self.user_token, "Borraja")

        list_response = self.client.get("/admin/crops", headers=auth_header(self.admin_token))
        get_response = self.client.get(f"/admin/crops/{crop['id']}", headers=auth_header(self.admin_token))
        update_response = self.client.patch(
            f"/admin/crops/{crop['id']}",
            json={"name": "Borraja editada", "is_public": True},
            headers=auth_header(self.admin_token),
        )
        delete_response = self.client.delete(f"/admin/crops/{crop['id']}", headers=auth_header(self.admin_token))

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["name"], "Borraja editada")
        self.assertTrue(update_response.json()["is_public"])
        self.assertEqual(delete_response.status_code, 204)

    def test_normal_user_cannot_use_admin_crop_endpoints(self):
        response = self.client.get("/admin/crops", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 403)

    def test_admin_task_endpoints_can_list_get_update_delete(self):
        task = create_task(self.client, self.user_token, "Abonar")

        list_response = self.client.get("/admin/tasks", headers=auth_header(self.admin_token))
        get_response = self.client.get(f"/admin/tasks/{task['id']}", headers=auth_header(self.admin_token))
        update_response = self.client.patch(
            f"/admin/tasks/{task['id']}",
            json={"name": "Abonar editada", "status": "completed"},
            headers=auth_header(self.admin_token),
        )
        delete_response = self.client.delete(f"/admin/tasks/{task['id']}", headers=auth_header(self.admin_token))

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["status"], "completed")
        self.assertEqual(delete_response.status_code, 204)

    def test_normal_user_cannot_use_admin_task_endpoints(self):
        response = self.client.get("/admin/tasks", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
