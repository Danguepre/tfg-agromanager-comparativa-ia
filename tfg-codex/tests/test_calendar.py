import unittest
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, engine as app_engine, get_db
from app.main import create_app


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_app_calendar.db"


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
    return client.post("/crops/", data={"name": name}, headers=auth_header(token))


def complete_calendar_payload(crop_id: int) -> dict[str, str | int]:
    return {
        "crop_id": crop_id,
        "planting_start": "2026-03-01",
        "planting_end": "2026-03-20",
        "transplant_start": "2031-04-02",
        "transplant_end": "2031-04-18",
        "harvest_start": "2040-07-10",
        "harvest_end": "2040-07-25",
    }


class CalendarTestCase(unittest.TestCase):
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

    def test_create_calendar_for_own_crop(self):
        crop = create_crop(self.client, self.user_token, "Tomate").json()

        response = self.client.post(
            "/calendar/",
            json=complete_calendar_payload(crop["id"]),
            headers=auth_header(self.user_token),
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["crop_id"], crop["id"])
        self.assertEqual(body["planting_start"], "2026-03-01")
        self.assertFalse(body["is_active"])
        self.assertEqual(body["current_phase_index"], 0)
        self.assertEqual(body["status"], "draft")

    def test_user_without_token_cannot_create_calendar(self):
        response = self.client.post("/calendar/", json={"crop_id": 1})

        self.assertEqual(response.status_code, 401)

    def test_normal_user_cannot_create_or_edit_calendar_for_other_user_crop(self):
        other_crop = create_crop(self.client, self.other_token, "Cebolla").json()

        create_response = self.client.post(
            "/calendar/",
            json=complete_calendar_payload(other_crop["id"]),
            headers=auth_header(self.user_token),
        )
        update_response = self.client.put(
            f"/calendar/crop/{other_crop['id']}",
            json={"planting_start": "2026-02-01"},
            headers=auth_header(self.user_token),
        )

        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(update_response.status_code, 403)

    def test_get_calendar_by_crop(self):
        crop = create_crop(self.client, self.user_token, "Lechuga").json()
        self.client.post("/calendar/", json=complete_calendar_payload(crop["id"]), headers=auth_header(self.user_token))

        response = self.client.get(f"/calendar/crop/{crop['id']}", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["crop_id"], crop["id"])

    def test_update_calendar_by_crop(self):
        crop = create_crop(self.client, self.user_token, "Pimiento").json()

        response = self.client.put(
            f"/calendar/crop/{crop['id']}",
            json={"planting_start": "2027-05-16", "planting_end": "2027-05-30"},
            headers=auth_header(self.user_token),
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["planting_start"], "2027-05-16")
        self.assertEqual(body["planting_end"], "2027-05-30")

    def test_cannot_activate_incomplete_calendar(self):
        crop = create_crop(self.client, self.user_token, "Acelga").json()
        self.client.put(
            f"/calendar/crop/{crop['id']}",
            json={"planting_start": "2026-01-01", "planting_end": "2026-01-15"},
            headers=auth_header(self.user_token),
        )

        response = self.client.post(f"/calendar/crop/{crop['id']}/activate", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 400)

    def test_activate_complete_calendar(self):
        crop = create_crop(self.client, self.user_token, "Zanahoria").json()
        self.client.post("/calendar/", json=complete_calendar_payload(crop["id"]), headers=auth_header(self.user_token))

        response = self.client.post(f"/calendar/crop/{crop['id']}/activate", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["is_active"])
        self.assertEqual(body["current_phase_index"], 0)
        self.assertEqual(body["status"], "active")

    def test_global_events_return_only_authenticated_user_events(self):
        user_crop = create_crop(self.client, self.user_token, "Calabacin").json()
        other_crop = create_crop(self.client, self.other_token, "Melon").json()
        self.client.post("/calendar/", json=complete_calendar_payload(user_crop["id"]), headers=auth_header(self.user_token))
        self.client.post(
            "/calendar/",
            json=complete_calendar_payload(other_crop["id"]),
            headers=auth_header(self.other_token),
        )
        self.client.post(f"/calendar/crop/{user_crop['id']}/activate", headers=auth_header(self.user_token))
        self.client.post(f"/calendar/crop/{other_crop['id']}/activate", headers=auth_header(self.other_token))

        response = self.client.get("/calendar/events", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        events = response.json()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["crop_id"], user_crop["id"])

    def test_calendar_events_return_current_phase(self):
        crop = create_crop(self.client, self.user_token, "Brocoli").json()
        calendar = self.client.post(
            "/calendar/",
            json=complete_calendar_payload(crop["id"]),
            headers=auth_header(self.user_token),
        ).json()
        self.client.post(f"/calendar/crop/{crop['id']}/activate", headers=auth_header(self.user_token))

        response = self.client.get(f"/calendar/{calendar['id']}/events", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        events = response.json()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["phase_index"], 0)
        self.assertEqual(events[0]["phase"], "Siembra")

    def test_events_ignore_year_and_use_month_and_fortnight(self):
        crop = create_crop(self.client, self.user_token, "Fresa").json()
        calendar = self.client.post(
            "/calendar/",
            json=complete_calendar_payload(crop["id"]),
            headers=auth_header(self.user_token),
        ).json()

        response = self.client.get(f"/calendar/{calendar['id']}/events", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        event = response.json()[0]
        self.assertEqual(event["start_month"], 3)
        self.assertEqual(event["start_fortnight"], 1)
        self.assertEqual(event["end_month"], 3)
        self.assertEqual(event["end_fortnight"], 2)
        self.assertNotIn("year", event)

    def test_advance_from_planting_to_transplant(self):
        crop = create_crop(self.client, self.user_token, "Col").json()
        self.client.post("/calendar/", json=complete_calendar_payload(crop["id"]), headers=auth_header(self.user_token))
        self.client.post(f"/calendar/crop/{crop['id']}/activate", headers=auth_header(self.user_token))

        response = self.client.post(f"/calendar/crop/{crop['id']}/advance", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["current_phase_index"], 1)

    def test_advance_from_transplant_to_harvest(self):
        crop = create_crop(self.client, self.user_token, "Apio").json()
        self.client.post("/calendar/", json=complete_calendar_payload(crop["id"]), headers=auth_header(self.user_token))
        self.client.post(f"/calendar/crop/{crop['id']}/activate", headers=auth_header(self.user_token))
        self.client.post(f"/calendar/crop/{crop['id']}/advance", headers=auth_header(self.user_token))

        response = self.client.post(f"/calendar/crop/{crop['id']}/advance", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["current_phase_index"], 2)

    def test_advance_from_harvest_completes_and_deactivates_calendar(self):
        crop = create_crop(self.client, self.user_token, "Berenjena").json()
        self.client.post("/calendar/", json=complete_calendar_payload(crop["id"]), headers=auth_header(self.user_token))
        self.client.post(f"/calendar/crop/{crop['id']}/activate", headers=auth_header(self.user_token))
        self.client.post(f"/calendar/crop/{crop['id']}/advance", headers=auth_header(self.user_token))
        self.client.post(f"/calendar/crop/{crop['id']}/advance", headers=auth_header(self.user_token))

        response = self.client.post(f"/calendar/crop/{crop['id']}/advance", headers=auth_header(self.user_token))

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["current_phase_index"], 2)
        self.assertEqual(body["status"], "completed")
        self.assertFalse(body["is_active"])

    def test_admin_can_manage_other_user_calendar(self):
        user_crop = create_crop(self.client, self.user_token, "Pepino").json()

        create_response = self.client.post(
            "/calendar/",
            json=complete_calendar_payload(user_crop["id"]),
            headers=auth_header(self.admin_token),
        )
        activate_response = self.client.post(
            f"/calendar/crop/{user_crop['id']}/activate",
            headers=auth_header(self.admin_token),
        )

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(activate_response.status_code, 200)
        self.assertTrue(activate_response.json()["is_active"])


if __name__ == "__main__":
    unittest.main()
