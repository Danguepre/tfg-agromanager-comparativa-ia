import unittest
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, engine as app_engine, get_db
from app.main import create_app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app_phase6.db"


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


def create_crop(client: TestClient, token: str, name: str):
    response = client.post("/crops/", data={"name": name}, headers=auth_header(token))
    assert response.status_code == 201
    return response.json()


def create_task(client: TestClient, token: str, name: str, **overrides):
    payload = {"name": name, "description": "Tarea de prueba"}
    payload.update(overrides)
    return client.post("/tasks/", json=payload, headers=auth_header(token))


class Phase6TestCase(unittest.TestCase):
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

        register(self.client, "user@example.com", "userone", "password123")
        register(self.client, "other@example.com", "othertwo", "password123")
        register(self.client, "admin@example.com", "adminone", "password123", role="admin")
        self.user_token = login(self.client, "user@example.com", "password123")
        self.other_token = login(self.client, "other@example.com", "password123")
        self.admin_token = login(self.client, "admin@example.com", "password123")
        self.user_crop = create_crop(self.client, self.user_token, "Tomate")
        self.other_crop = create_crop(self.client, self.other_token, "Lechuga")

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        app_engine.dispose()

    def test_create_get_update_irrigation_for_own_crop(self):
        create_response = self.client.post(
            "/irrigation/",
            json={
                "crop_id": self.user_crop["id"],
                "watering_frequency": "daily",
                "water_amount": "500ml",
                "recommendations": "Regar al amanecer",
            },
            headers=auth_header(self.user_token),
        )
        self.assertEqual(create_response.status_code, 201)
        irrigation = create_response.json()
        self.assertEqual(irrigation["crop_id"], self.user_crop["id"])

        by_crop_response = self.client.get(
            f"/irrigation/crop/{self.user_crop['id']}",
            headers=auth_header(self.user_token),
        )
        self.assertEqual(by_crop_response.status_code, 200)
        self.assertEqual(by_crop_response.json()["watering_frequency"], "daily")

        update_response = self.client.put(
            f"/irrigation/{irrigation['id']}",
            json={"water_amount": "750ml"},
            headers=auth_header(self.user_token),
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["water_amount"], "750ml")

    def test_normal_user_cannot_access_or_modify_irrigation_of_other_crop(self):
        other_irrigation = self.client.get(
            f"/irrigation/crop/{self.other_crop['id']}",
            headers=auth_header(self.other_token),
        ).json()

        get_response = self.client.get(
            f"/irrigation/crop/{self.other_crop['id']}",
            headers=auth_header(self.user_token),
        )
        update_response = self.client.put(
            f"/irrigation/{other_irrigation['id']}",
            json={"water_amount": "robado"},
            headers=auth_header(self.user_token),
        )

        self.assertEqual(get_response.status_code, 403)
        self.assertEqual(update_response.status_code, 403)

    def test_create_get_update_environmental_for_own_crop(self):
        create_response = self.client.post(
            "/environmental/",
            json={
                "crop_id": self.user_crop["id"],
                "sun_exposure": "partial shade",
                "min_temp": 8,
                "max_temp": 28,
                "frost_tolerance": True,
            },
            headers=auth_header(self.user_token),
        )
        self.assertEqual(create_response.status_code, 201)
        environmental = create_response.json()
        self.assertEqual(environmental["crop_id"], self.user_crop["id"])

        by_crop_response = self.client.get(
            f"/environmental/crop/{self.user_crop['id']}",
            headers=auth_header(self.user_token),
        )
        self.assertEqual(by_crop_response.status_code, 200)
        self.assertEqual(by_crop_response.json()["min_temp"], 8)

        update_response = self.client.put(
            f"/environmental/{environmental['id']}",
            json={"max_temp": 30},
            headers=auth_header(self.user_token),
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["max_temp"], 30)

    def test_normal_user_cannot_access_or_modify_environmental_of_other_crop(self):
        other_environmental = self.client.get(
            f"/environmental/crop/{self.other_crop['id']}",
            headers=auth_header(self.other_token),
        ).json()

        get_response = self.client.get(
            f"/environmental/crop/{self.other_crop['id']}",
            headers=auth_header(self.user_token),
        )
        update_response = self.client.put(
            f"/environmental/{other_environmental['id']}",
            json={"sun_exposure": "robado"},
            headers=auth_header(self.user_token),
        )

        self.assertEqual(get_response.status_code, 403)
        self.assertEqual(update_response.status_code, 403)

    def test_task_auth_listing_and_admin_visibility(self):
        self.assertEqual(self.client.post("/tasks/", json={"name": "Sin token"}).status_code, 401)
        user_task = create_task(self.client, self.user_token, "Podar").json()
        other_task = create_task(self.client, self.other_token, "Abonar").json()

        user_list = self.client.get("/tasks/", headers=auth_header(self.user_token))
        admin_list = self.client.get("/tasks/", headers=auth_header(self.admin_token))

        self.assertEqual(user_list.status_code, 200)
        self.assertEqual([task["id"] for task in user_list.json()], [user_task["id"]])
        self.assertEqual(admin_list.status_code, 200)
        self.assertEqual({task["id"] for task in admin_list.json()}, {user_task["id"], other_task["id"]})

    def test_assign_task_to_own_crop_and_list_relationships(self):
        task = create_task(self.client, self.user_token, "Revisar humedad").json()

        assign_response = self.client.post(
            "/tasks/assign",
            json={"task_id": task["id"], "crop_id": self.user_crop["id"]},
            headers=auth_header(self.user_token),
        )
        by_crop_response = self.client.get(
            f"/tasks/crop/{self.user_crop['id']}",
            headers=auth_header(self.user_token),
        )
        task_crops_response = self.client.get(
            f"/tasks/{task['id']}/crops",
            headers=auth_header(self.user_token),
        )

        self.assertEqual(assign_response.status_code, 200)
        self.assertEqual(by_crop_response.status_code, 200)
        self.assertEqual([item["id"] for item in by_crop_response.json()], [task["id"]])
        self.assertEqual(task_crops_response.status_code, 200)
        self.assertEqual([crop["id"] for crop in task_crops_response.json()], [self.user_crop["id"]])

    def test_normal_user_cannot_assign_task_to_other_user_crop(self):
        task = create_task(self.client, self.user_token, "Intento invalido").json()

        response = self.client.post(
            "/tasks/assign",
            json={"task_id": task["id"], "crop_id": self.other_crop["id"]},
            headers=auth_header(self.user_token),
        )

        self.assertEqual(response.status_code, 403)

    def test_patch_task_status_complete_and_reopen(self):
        task = create_task(self.client, self.user_token, "Cosechar").json()

        complete_response = self.client.patch(
            f"/tasks/{task['id']}",
            json={"status": "completed"},
            headers=auth_header(self.user_token),
        )
        reopen_response = self.client.patch(
            f"/tasks/{task['id']}",
            json={"status": "pending"},
            headers=auth_header(self.user_token),
        )

        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(complete_response.json()["status"], "completed")
        self.assertEqual(reopen_response.status_code, 200)
        self.assertEqual(reopen_response.json()["status"], "pending")

    def test_normal_user_cannot_edit_other_user_task(self):
        other_task = create_task(self.client, self.other_token, "Tarea ajena").json()

        response = self.client.put(
            f"/tasks/{other_task['id']}",
            json={"name": "Editada"},
            headers=auth_header(self.user_token),
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_task_removes_task_crop_relationships(self):
        task = create_task(self.client, self.user_token, "Eliminar", crop_ids=[self.user_crop["id"]]).json()

        delete_response = self.client.delete(f"/tasks/{task['id']}", headers=auth_header(self.user_token))
        by_crop_response = self.client.get(
            f"/tasks/crop/{self.user_crop['id']}",
            headers=auth_header(self.user_token),
        )

        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(by_crop_response.status_code, 200)
        self.assertEqual(by_crop_response.json(), [])


if __name__ == "__main__":
    unittest.main()
