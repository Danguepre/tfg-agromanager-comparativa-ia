"""
Tests para dashboard y panel admin.
Usa unittest + TestClient de FastAPI.
"""
import unittest
from fastapi.testclient import TestClient

from app.database import Base
# Importar modelos para registrar mappers con Base
from app import models
from app.main import app
from app.models.user import User, UserRole
from app.models.crop import Crop
from app.models.task import Task, TaskStatus
from app.models.planting_calendar import PlantingCalendar, CalendarStatus

# ============================================================================
# USAR ENGINE Y SESSIONLOCAL CENTRALIZADOS DE conftest.py
# ============================================================================
from tests.conftest import engine, TestingSessionLocal, override_get_db, reset_test_database

# El override ya se realizó en conftest.py al importarlo


class TestDashboard(unittest.TestCase):
    """Tests del dashboard de usuario."""

    def setUp(self):
        """Configuración previa a cada test."""
        reset_test_database()
        self.client = TestClient(app)

        # Crear usuario normal
        user_response = self.client.post(
            "/auth/register",
            json={
                "email": "normaluser@example.com",
                "password": "SecurePass123",
                "name": "Normal User",
            },
        )
        self.user_id = user_response.json()["id"]

        # Login usuario normal
        login_response = self.client.post(
            "/auth/login",
            json={
                "email": "normaluser@example.com",
                "password": "SecurePass123",
            },
        )
        self.user_token = login_response.json()["access_token"]

    def test_dashboard_summary_authenticated(self):
        """GET /dashboard/summary con autenticación debe retornar resumen."""
        response = self.client.get(
            "/dashboard/summary",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_personal_crops", data)
        self.assertIn("total_public_crops_available", data)
        self.assertIn("total_tasks_pending", data)
        self.assertIn("total_tasks_completed", data)
        self.assertIn("total_active_calendars", data)
        self.assertIn("upcoming_tasks", data)
        self.assertIn("active_calendar_phases", data)

    def test_dashboard_summary_unauthenticated(self):
        """GET /dashboard/summary sin token debe fallar con 401."""
        response = self.client.get("/dashboard/summary")
        self.assertEqual(response.status_code, 401)

    def test_dashboard_crops(self):
        """GET /dashboard/crops debe retornar cultivos del usuario."""
        # Crear un cultivo
        self.client.post(
            "/crops/",
            data={
                "name": "Tomate",
                "description": "Tomate de prueba",
                "crop_type": "verdura",
                "is_public": "false",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        response = self.client.get(
            "/dashboard/crops",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("personal_crops", data)
        self.assertIn("total_personal", data)
        self.assertEqual(data["total_personal"], 1)
        self.assertEqual(data["personal_crops"][0]["name"], "Tomate")

    def test_dashboard_crops_only_user_data(self):
        """Dashboard de cultivos solo debe incluir cultivos del usuario."""
        # Crear otro usuario
        other_response = self.client.post(
            "/auth/register",
            json={
                "email": "otheruser@example.com",
                "password": "SecurePass123",
                "name": "Other User",
            },
        )
        other_user_id = other_response.json()["id"]

        # Login otro usuario
        other_login = self.client.post(
            "/auth/login",
            json={
                "email": "otheruser@example.com",
                "password": "SecurePass123",
            },
        )
        other_token = other_login.json()["access_token"]

        # Usuario 1 crea un cultivo
        self.client.post(
            "/crops/",
            data={
                "name": "Tomate",
                "crop_type": "verdura",
                "is_public": "false",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Usuario 2 crea otro cultivo
        self.client.post(
            "/crops/",
            data={
                "name": "Lechuga",
                "crop_type": "verdura",
                "is_public": "false",
            },
            headers={"Authorization": f"Bearer {other_token}"},
        )

        # Verificar que cada usuario solo ve sus propios cultivos
        user1_response = self.client.get(
            "/dashboard/crops",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(user1_response.json()["total_personal"], 1)
        self.assertEqual(user1_response.json()["personal_crops"][0]["name"], "Tomate")

        user2_response = self.client.get(
            "/dashboard/crops",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(user2_response.json()["total_personal"], 1)
        self.assertEqual(user2_response.json()["personal_crops"][0]["name"], "Lechuga")

    def test_dashboard_tasks_pending_completed(self):
        """GET /dashboard/tasks debe separar pending y completed."""
        # Crear una tarea pending
        self.client.post(
            "/tasks/",
            json={
                "title": "Tarea 1",
                "description": "Tarea pendiente",
                "due_date": "2026-06-01",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Crear otra tarea pending
        self.client.post(
            "/tasks/",
            json={
                "title": "Tarea 2",
                "description": "Otra tarea pendiente",
                "due_date": "2026-06-02",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        response = self.client.get(
            "/dashboard/tasks",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("pending_tasks", data)
        self.assertIn("completed_tasks", data)
        self.assertIn("total_pending", data)
        self.assertIn("total_completed", data)
        self.assertEqual(data["total_pending"], 2)
        self.assertEqual(data["total_completed"], 0)

    def test_dashboard_calendar(self):
        """GET /dashboard/calendar debe retornar calendarios activos y completados."""
        response = self.client.get(
            "/dashboard/calendar",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("active_calendars", data)
        self.assertIn("completed_calendars", data)

    def test_dashboard_irrigation(self):
        """GET /dashboard/irrigation debe retornar resumen de riego."""
        # Crear un cultivo
        crop_response = self.client.post(
            "/crops/",
            data={
                "name": "Tomate",
                "crop_type": "verdura",
                "is_public": "false",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        response = self.client.get(
            "/dashboard/irrigation",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("irrigation_summaries", data)

    def test_dashboard_environmental(self):
        """GET /dashboard/environmental debe retornar requisitos ambientales."""
        response = self.client.get(
            "/dashboard/environmental",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("environmental_summaries", data)


class TestAdminPanel(unittest.TestCase):
    """Tests del panel admin."""

    def setUp(self):
        """Configuración previa a cada test."""
        reset_test_database()
        self.client = TestClient(app)

        # Obtener sesión de BD para crear admin directamente
        db = TestingSessionLocal()
        
        # Crear usuario admin directamente en BD
        from app.services.user_service import create_user
        admin_user = create_user(
            db,
            email="admin@example.com",
            password="AdminPass123",
            name="Admin User",
            role=UserRole.ADMIN,
        )
        self.admin_id = admin_user.id

        # Crear usuario normal
        normal_user = create_user(
            db,
            email="normaluser@example.com",
            password="NormalPass123",
            name="Normal User",
            role=UserRole.USER,
        )
        self.normal_user_id = normal_user.id

        db.close()

        # Login admin
        admin_login = self.client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123",
            },
        )
        self.admin_token = admin_login.json()["access_token"]

        # Login usuario normal
        normal_login = self.client.post(
            "/auth/login",
            json={
                "email": "normaluser@example.com",
                "password": "NormalPass123",
            },
        )
        self.normal_token = normal_login.json()["access_token"]

    def test_admin_summary_admin_only(self):
        """GET /admin/summary solo accesible por admin."""
        # Usuario normal no puede acceder
        response = self.client.get(
            "/admin/summary",
            headers={"Authorization": f"Bearer {self.normal_token}"},
        )
        self.assertEqual(response.status_code, 403)

        # Admin sí puede acceder
        response = self.client.get(
            "/admin/summary",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_users", data)
        self.assertIn("total_crops", data)
        self.assertIn("total_public_crops", data)
        self.assertIn("total_tasks", data)
        self.assertIn("total_pending_tasks", data)
        self.assertIn("total_completed_tasks", data)
        self.assertIn("total_active_calendars", data)
        self.assertIn("total_completed_calendars", data)

    def test_admin_list_users(self):
        """GET /admin/users solo accesible por admin."""
        # Usuario normal no puede acceder
        response = self.client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {self.normal_token}"},
        )
        self.assertEqual(response.status_code, 403)

        # Admin sí puede acceder
        response = self.client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total", data)
        self.assertIn("items", data)
        self.assertGreaterEqual(data["total"], 2)  # Admin + Normal

        # Verificar que no expone passwords
        for user in data["items"]:
            self.assertNotIn("password_hash", user)

    def test_admin_get_user_by_id(self):
        """GET /admin/users/{user_id} retorna usuario sin password."""
        response = self.client.get(
            f"/admin/users/{self.normal_user_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.normal_user_id)
        self.assertEqual(data["email"], "normaluser@example.com")
        self.assertNotIn("password_hash", data)

    def test_admin_update_user(self):
        """PATCH /admin/users/{user_id} permite actualizar usuario."""
        response = self.client.patch(
            f"/admin/users/{self.normal_user_id}",
            json={
                "name": "Updated Name",
                "is_active": False,
            },
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Name")
        self.assertEqual(data["is_active"], False)

    def test_admin_delete_user(self):
        """DELETE /admin/users/{user_id} elimina usuario."""
        response = self.client.delete(
            f"/admin/users/{self.normal_user_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que usuario fue eliminado
        get_response = self.client.get(
            f"/admin/users/{self.normal_user_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(get_response.status_code, 404)

    def test_admin_list_crops(self):
        """GET /admin/crops retorna todos los cultivos."""
        response = self.client.get(
            "/admin/crops",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total", data)
        self.assertIn("items", data)

    def test_admin_update_crop(self):
        """PATCH /admin/crops/{crop_id} permite actualizar cultivo."""
        # Crear cultivo
        db = TestingSessionLocal()
        crop = Crop(
            name="Tomate Original",
            crop_type="verdura",
            owner_id=self.normal_user_id,
            is_public=False,
        )
        db.add(crop)
        db.commit()
        crop_id = crop.id
        db.close()

        # Admin actualiza cultivo
        response = self.client.patch(
            f"/admin/crops/{crop_id}",
            json={
                "name": "Tomate Actualizado",
                "is_public": True,
            },
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Tomate Actualizado")
        self.assertEqual(data["is_public"], True)

    def test_admin_delete_crop(self):
        """DELETE /admin/crops/{crop_id} elimina cultivo."""
        # Crear cultivo
        db = TestingSessionLocal()
        crop = Crop(
            name="Tomate",
            crop_type="verdura",
            owner_id=self.normal_user_id,
            is_public=False,
        )
        db.add(crop)
        db.commit()
        crop_id = crop.id
        db.close()

        # Admin elimina cultivo
        response = self.client.delete(
            f"/admin/crops/{crop_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que cultivo fue eliminado
        get_response = self.client.get(
            f"/admin/crops/{crop_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(get_response.status_code, 404)

    def test_admin_list_tasks(self):
        """GET /admin/tasks retorna todas las tareas."""
        response = self.client.get(
            "/admin/tasks",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total", data)
        self.assertIn("items", data)

    def test_admin_update_task(self):
        """PATCH /admin/tasks/{task_id} permite actualizar tarea."""
        # Crear tarea
        db = TestingSessionLocal()
        task = Task(
            owner_id=self.normal_user_id,
            title="Tarea Original",
            status=TaskStatus.PENDING,
        )
        db.add(task)
        db.commit()
        task_id = task.id
        db.close()

        # Admin actualiza tarea
        response = self.client.patch(
            f"/admin/tasks/{task_id}",
            json={
                "title": "Tarea Actualizada",
                "status": "completed",
            },
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Tarea Actualizada")
        self.assertEqual(data["status"], "completed")

    def test_admin_delete_task(self):
        """DELETE /admin/tasks/{task_id} elimina tarea."""
        # Crear tarea
        db = TestingSessionLocal()
        task = Task(
            owner_id=self.normal_user_id,
            title="Tarea",
            status=TaskStatus.PENDING,
        )
        db.add(task)
        db.commit()
        task_id = task.id
        db.close()

        # Admin elimina tarea
        response = self.client.delete(
            f"/admin/tasks/{task_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que tarea fue eliminada
        get_response = self.client.get(
            f"/admin/tasks/{task_id}",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(get_response.status_code, 404)

    def test_normal_user_cannot_access_admin_endpoints(self):
        """Usuario normal no puede acceder a endpoints admin."""
        endpoints = [
            "/admin/summary",
            "/admin/users",
            f"/admin/users/{self.admin_id}",
            "/admin/crops",
            "/admin/tasks",
        ]

        for endpoint in endpoints:
            response = self.client.get(
                endpoint,
                headers={"Authorization": f"Bearer {self.normal_token}"},
            )
            self.assertEqual(
                response.status_code,
                403,
                f"Endpoint {endpoint} debe retornar 403 para usuario normal",
            )


if __name__ == "__main__":
    unittest.main()
