import unittest
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, engine as app_engine, get_db
from app.main import create_app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app_crops.db"


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
    return client.post("/crops/", data=data, headers=auth_header(token))


class CropsTestCase(unittest.TestCase):
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

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        app_engine.dispose()

    def test_authenticated_user_can_create_crop(self):
        response = create_crop(
            self.client,
            self.user_token,
            "Tomate cherry",
            crop_type="hortaliza",
            description="Cultivo de temporada",
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["name"], "Tomate cherry")
        self.assertEqual(body["crop_type"], "hortaliza")
        self.assertFalse(body["is_public"])
        self.assertIsNotNone(body["owner_id"])
        self.assertEqual(body["image_url"], "/uploads/crops/placeholder.png")
        self.assertIsNotNone(body["irrigation_attributes"])
        self.assertIsNotNone(body["environmental_requirements"])
        self.assertNotIn("hashed_password", body)

    def test_user_without_token_cannot_create_crop(self):
        response = self.client.post("/crops/", data={"name": "Lechuga"})

        self.assertEqual(response.status_code, 401)

    def test_normal_user_cannot_publish_crop(self):
        response = create_crop(self.client, self.user_token, "Albahaca", is_public="true")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_published_crop(self):
        response = create_crop(
            self.client,
            self.admin_token,
            "Zanahoria",
            crop_type="raiz",
            is_public="true",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["is_public"])

    def test_my_crops_returns_only_current_user_crops(self):
        user_crop = create_crop(self.client, self.user_token, "Pimiento").json()
        create_crop(self.client, self.other_token, "Cebolla")

        response = self.client.get("/crops/my", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        crop_ids = [crop["id"] for crop in response.json()]
        self.assertEqual(crop_ids, [user_crop["id"]])

    def test_published_crops_can_be_paginated_and_filtered(self):
        create_crop(self.client, self.admin_token, "Tomate pera", crop_type="hortaliza", is_public="true")
        create_crop(self.client, self.admin_token, "Tomate raf", crop_type="hortaliza", is_public="true")
        create_crop(self.client, self.admin_token, "Lavanda", crop_type="aromatica", is_public="true")

        response = self.client.get(
            "/crops/published?name=tomate&crop_type=hortaliza&skip=1&limit=1",
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["name"], "Tomate raf")

    def test_copy_from_catalog_creates_independent_copy(self):
        original = create_crop(
            self.client,
            self.admin_token,
            "Fresa",
            crop_type="fruta",
            description="Original",
            is_public="true",
        ).json()

        copy_response = self.client.post(
            f"/crops/{original['id']}/add-to-my-crops",
            headers=auth_header(self.user_token),
        )
        self.assertEqual(copy_response.status_code, 201)
        copied = copy_response.json()
        self.assertNotEqual(copied["id"], original["id"])
        self.assertEqual(copied["copied_from_crop_id"], original["id"])
        self.assertFalse(copied["is_public"])

        update_response = self.client.put(
            f"/crops/{copied['id']}",
            data={"name": "Fresa personalizada"},
            headers=auth_header(self.user_token),
        )
        self.assertEqual(update_response.status_code, 200)

        original_response = self.client.get(f"/crops/{original['id']}", headers=auth_header(self.user_token))
        self.assertEqual(original_response.json()["name"], "Fresa")

    def test_normal_user_cannot_edit_other_user_crop(self):
        other_crop = create_crop(self.client, self.other_token, "Melon").json()

        response = self.client.put(
            f"/crops/{other_crop['id']}",
            data={"name": "Melon robado"},
            headers=auth_header(self.user_token),
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_copy_removes_it_from_my_crops(self):
        original = create_crop(self.client, self.admin_token, "Acelga", is_public="true").json()
        copied = self.client.post(
            f"/crops/{original['id']}/add-to-my-crops",
            headers=auth_header(self.user_token),
        ).json()

        delete_response = self.client.delete(f"/crops/{copied['id']}", headers=auth_header(self.user_token))
        my_crops_response = self.client.get("/crops/my", headers=auth_header(self.user_token))

        self.assertEqual(delete_response.status_code, 204)
        self.assertNotIn(copied["id"], [crop["id"] for crop in my_crops_response.json()])

    def test_delete_original_keeps_it_as_public_catalog_crop(self):
        original = create_crop(self.client, self.user_token, "Pepino").json()

        delete_response = self.client.delete(f"/crops/{original['id']}", headers=auth_header(self.user_token))
        published_response = self.client.get("/crops/published?name=pepino", headers=auth_header(self.user_token))
        my_crops_response = self.client.get("/crops/my", headers=auth_header(self.user_token))

        self.assertEqual(delete_response.status_code, 204)
        published = published_response.json()
        self.assertEqual(len(published), 1)
        self.assertEqual(published[0]["id"], original["id"])
        self.assertTrue(published[0]["is_public"])
        self.assertIsNone(published[0]["owner_id"])
        self.assertNotIn(original["id"], [crop["id"] for crop in my_crops_response.json()])


if __name__ == "__main__":
    unittest.main()
