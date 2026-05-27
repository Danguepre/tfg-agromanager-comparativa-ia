import unittest
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, engine as app_engine, get_db
from app.main import create_app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app_agromanager.db"


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


class AuthUsersTestCase(unittest.TestCase):
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

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
        app_engine.dispose()

    def test_health_check(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_register_login_and_password_not_exposed(self):
        response = register(self.client, "user@example.com", "userone", "password123")
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["email"], "user@example.com")
        self.assertNotIn("password", body)
        self.assertNotIn("hashed_password", body)

        token = login(self.client, "user@example.com", "password123")
        self.assertTrue(token)

    def test_protected_route_fails_without_token(self):
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 401)

    def test_normal_user_cannot_read_other_user(self):
        user_response = register(self.client, "normal@example.com", "normaluser", "password123")
        other_response = register(self.client, "other@example.com", "otheruser", "password123")
        token = login(self.client, "normal@example.com", "password123")

        response = self.client.get(f"/users/{other_response.json()['id']}", headers=auth_header(token))
        self.assertEqual(user_response.status_code, 201)
        self.assertEqual(response.status_code, 403)

    def test_admin_can_list_all_users(self):
        register(self.client, "admin@example.com", "adminuser", "password123", role="admin")
        register(self.client, "regular@example.com", "regularuser", "password123")
        token = login(self.client, "admin@example.com", "password123")

        response = self.client.get("/users/", headers=auth_header(token))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)


if __name__ == "__main__":
    unittest.main()
