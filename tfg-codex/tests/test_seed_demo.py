import unittest
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, engine as app_engine, get_db
from app.core.security import verify_password
from app.main import create_app
from app.models.crop import Crop
from app.models.user import User
from scripts.seed_demo import seed_demo


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app_seed_demo.db"


def login(client: TestClient, email: str, password: str):
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class SeedDemoTestCase(unittest.TestCase):
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

    def _seed(self):
        db = self.testing_session_local()
        try:
            return seed_demo(db)
        finally:
            db.close()

    def test_seed_creates_demo_data_and_is_idempotent(self):
        first_summary = self._seed()
        self.assertGreater(first_summary.counts["users"]["created"], 0)
        second_summary = self._seed()
        self.assertEqual(second_summary.counts["users"]["created"], 0)

        db = self.testing_session_local()
        try:
            admin = db.query(User).filter(User.email == "admin@test.com").one()
            user = db.query(User).filter(User.email == "user@test.com").one()
            public_crops = db.query(Crop).filter(Crop.is_public.is_(True)).all()

            self.assertEqual(admin.role, "admin")
            self.assertEqual(user.role, "user")
            self.assertGreaterEqual(len(public_crops), 5)
            self.assertEqual(db.query(User).filter(User.email == "admin@test.com").count(), 1)
            self.assertEqual(db.query(User).filter(User.email == "user@test.com").count(), 1)
            self.assertNotEqual(admin.hashed_password, "admin123")
            self.assertNotEqual(user.hashed_password, "user123")
            self.assertTrue(verify_password("admin123", admin.hashed_password))
            self.assertTrue(verify_password("user123", user.hashed_password))
        finally:
            db.close()

    def test_seeded_users_can_login_and_public_catalog_returns_data(self):
        self._seed()

        admin_login = login(self.client, "admin@test.com", "admin123")
        user_login = login(self.client, "user@test.com", "user123")

        self.assertEqual(admin_login.status_code, 200)
        self.assertEqual(user_login.status_code, 200)

        catalog = self.client.get("/crops/published")
        self.assertEqual(catalog.status_code, 200)
        self.assertGreaterEqual(len(catalog.json()), 5)

        user_token = user_login.json()["access_token"]
        my_crops = self.client.get("/crops/my", headers=auth_header(user_token))
        self.assertEqual(my_crops.status_code, 200)
        self.assertGreaterEqual(len(my_crops.json()), 2)


if __name__ == "__main__":
    unittest.main()
