from tests.test_api import ApiTestCase


class UserFlowE2ETests(ApiTestCase):
    def test_normal_user_catalog_copy_calendar_and_logout_equivalent_flow(self):
        headers = self.auth_headers("user@example.com")

        catalog = self.client.get("/crops/published?name=Tomate&type=hortaliza&page=1&page_size=12", headers=headers)
        self.assertEqual(catalog.status_code, 200)
        self.assertEqual(catalog.json()["total"], 1)

        copied = self.client.post(f"/crops/{self.catalog_tomato.id}/add-to-my-crops", headers=headers)
        self.assertEqual(copied.status_code, 200)
        copy_id = copied.json()["id"]

        edited = self.client.put(f"/crops/{copy_id}", headers=headers, json={
            "name": "Tomate E2E",
            "type": "hortaliza",
            "life_cycle": "anual",
            "image_url": None,
            "user_id": self.user.id,
            "is_public": False,
            "source_crop_id": self.catalog_tomato.id,
        })
        self.assertEqual(edited.status_code, 200)

        calendar = self.client.put(f"/calendar/crop/{copy_id}", headers=headers, json={
            "crop_id": copy_id,
            "planting_start": "2000-02-01",
            "planting_end": "2000-02-01",
            "transplant_start": "2000-03-16",
            "transplant_end": "2000-03-16",
            "harvest_start": "2000-07-01",
            "harvest_end": "2000-07-01",
        })
        self.assertEqual(calendar.status_code, 200)

        activated = self.client.post(f"/calendar/crop/{copy_id}/activate", headers=headers)
        self.assertEqual(activated.status_code, 200)
        self.assertEqual(activated.json()["current_phase_index"], 0)

        events = self.client.get("/calendar/events", headers=headers)
        self.assertTrue(any(event["crop_id"] == copy_id and event["phase"] == "Siembra" for event in events.json()))

        advanced = self.client.post(f"/calendar/crop/{copy_id}/advance", headers=headers)
        self.assertEqual(advanced.status_code, 200)
        self.assertEqual(advanced.json()["current_phase_index"], 1)

        advanced_events = self.client.get("/calendar/events", headers=headers)
        self.assertTrue(any(event["crop_id"] == copy_id and event["phase"] == "Trasplante" for event in advanced_events.json()))


class AdminFlowE2ETests(ApiTestCase):
    def test_admin_user_and_crop_management_flow(self):
        admin_headers = self.auth_headers("admin@example.com")
        normal_headers = self.auth_headers("user@example.com")

        forbidden = self.client.get("/admin/summary", headers=normal_headers)
        self.assertEqual(forbidden.status_code, 403)

        summary = self.client.get("/admin/summary", headers=admin_headers)
        self.assertEqual(summary.status_code, 200)

        user = self.client.post("/admin/users", headers=admin_headers, json={
            "name": "E2E User",
            "email": "e2e-user@example.com",
            "location": "Test",
            "role": "user",
            "password": "1234",
        })
        self.assertEqual(user.status_code, 200)
        user_id = user.json()["id"]

        promoted = self.client.put(f"/admin/users/{user_id}", headers=admin_headers, json={
            "name": "E2E User",
            "email": "e2e-user@example.com",
            "location": "Test",
            "role": "admin",
        })
        self.assertEqual(promoted.status_code, 200)
        self.assertEqual(promoted.json()["role"], "admin")

        crop_payload = {
            "name": "E2E Cultivo",
            "type": "test",
            "life_cycle": "anual",
            "image_url": None,
            "user_id": user_id,
            "is_public": True,
            "source_crop_id": None,
            "irrigation": {"watering_frequency": "weekly", "water_amount": 2, "recommendations": "E2E"},
            "environmental": {"sun_exposure": "partial", "min_temp": 8, "max_temp": 24, "frost_tolerance": False},
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
        crop = self.client.post("/admin/crops", headers=admin_headers, json=crop_payload)
        self.assertEqual(crop.status_code, 200)
        crop_id = crop.json()["id"]

        crop_payload["name"] = "E2E Cultivo Editado"
        edited = self.client.put(f"/admin/crops/{crop_id}", headers=admin_headers, json=crop_payload)
        self.assertEqual(edited.status_code, 200)
        self.assertEqual(edited.json()["name"], "E2E Cultivo Editado")

        deleted_crop = self.client.delete(f"/admin/crops/{crop_id}", headers=admin_headers)
        self.assertEqual(deleted_crop.status_code, 200)

        deleted_user = self.client.delete(f"/admin/users/{user_id}", headers=admin_headers)
        self.assertEqual(deleted_user.status_code, 200)
