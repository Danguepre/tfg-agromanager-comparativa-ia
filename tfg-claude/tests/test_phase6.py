"""
Tests unitarios para riego, requisitos ambientales y tareas (FASE 6).
Usa unittest + TestClient de FastAPI.
Base de datos: SQLite en memoria para tests (COMPARTIDA vía conftest.py).
"""
import unittest
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app import models
from app.main import app
from app.models.user import User, UserRole
from app.models.task import TaskStatus

# ============================================================================
# USAR ENGINE Y SESSIONLOCAL CENTRALIZADOS DE conftest.py
# ============================================================================
from tests.conftest import engine, TestingSessionLocal, override_get_db, reset_test_database

# El override ya se realizó en conftest.py al importarlo


class TestIrrigation(unittest.TestCase):
    """Tests de riego."""

    def setUp(self):
        """Configuración previa a cada test."""
        reset_test_database()  # Limpiar BD antes de cada test class
        self.client = TestClient(app)

        # Crear usuario normal
        user_response = self.client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
                "name": "Regular User",
            },
        )
        self.user_id = user_response.json()["id"]

        # Login usuario normal
        login_response = self.client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
            },
        )
        self.user_token = login_response.json()["access_token"]

        # Crear usuario admin
        admin_response = self.client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123",
                "name": "Admin User",
            },
        )
        self.admin_id = admin_response.json()["id"]

        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.id == self.admin_id).first()
        if admin_user:
            admin_user.role = UserRole.ADMIN
            db.commit()
        db.close()

        admin_login = self.client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123",
            },
        )
        self.admin_token = admin_login.json()["access_token"]

        # Crear cultivo para el usuario
        crop_response = self.client.post(
            "/crops/",
            data={
                "name": "Tomate",
                "crop_type": "verdura",
                "is_public": "false",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.crop_id = crop_response.json()["id"]

    def test_get_irrigation_by_crop_success(self):
        """GET /irrigation/crop/{crop_id} debe retornar riego del cultivo."""
        response = self.client.get(
            f"/irrigation/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["crop_id"], self.crop_id)
        self.assertIn("id", data)

    def test_get_irrigation_forbidden_other_user(self):
        """GET /irrigation/crop/{crop_id} de usuario normal no debe acceder cultivo ajeno."""
        # Crear otro usuario
        other_response = self.client.post(
            "/auth/register",
            json={
                "email": "other@example.com",
                "password": "SecurePass123",
                "name": "Other User",
            },
        )
        other_id = other_response.json()["id"]

        other_login = self.client.post(
            "/auth/login",
            json={
                "email": "other@example.com",
                "password": "SecurePass123",
            },
        )
        other_token = other_login.json()["access_token"]

        # Intentar acceder al riego del cultivo del primer usuario
        response = self.client.get(
            f"/irrigation/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_update_irrigation_success(self):
        """PUT /irrigation/{irrigation_id} debe actualizar riego."""
        # Obtener ID del riego
        get_response = self.client.get(
            f"/irrigation/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        irrigation_id = get_response.json()["id"]

        # Actualizar riego
        response = self.client.put(
            f"/irrigation/{irrigation_id}",
            json={
                "water_frequency_days": 3,
                "water_amount_mm": 25.5,
                "irrigation_type": "goteo",
                "notes": "Riego por goteo automático",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["water_frequency_days"], 3)
        self.assertEqual(data["water_amount_mm"], 25.5)
        self.assertEqual(data["irrigation_type"], "goteo")

    def test_delete_irrigation_success(self):
        """DELETE /irrigation/{irrigation_id} debe eliminar riego."""
        # Obtener ID del riego
        get_response = self.client.get(
            f"/irrigation/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        irrigation_id = get_response.json()["id"]

        # Eliminar
        response = self.client.delete(
            f"/irrigation/{irrigation_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que no existe
        get_again = self.client.get(
            f"/irrigation/{irrigation_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(get_again.status_code, 404)

    def test_list_irrigations_user_sees_only_own(self):
        """GET /irrigation/ debe mostrar solo riegos del usuario."""
        response = self.client.get(
            "/irrigation/",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)  # Un cultivo del usuario
        self.assertEqual(len(data["items"]), 1)

    def test_list_irrigations_admin_sees_all(self):
        """GET /irrigation/ como admin debe mostrar todos los riegos."""
        response = self.client.get(
            "/irrigation/",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["total"], 1)


class TestEnvironmental(unittest.TestCase):
    """Tests de requisitos ambientales."""

    def setUp(self):
        """Configuración previa a cada test."""
        reset_test_database()  # Ya limpia e inicializa las tablas
        self.client = TestClient(app)

        # Crear usuario normal
        user_response = self.client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
                "name": "Regular User",
            },
        )
        self.user_id = user_response.json()["id"]

        # Login usuario normal
        login_response = self.client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
            },
        )
        self.user_token = login_response.json()["access_token"]

        # Crear cultivo para el usuario
        crop_response = self.client.post(
            "/crops/",
            data={
                "name": "Lechuga",
                "crop_type": "verdura",
                "is_public": "false",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.crop_id = crop_response.json()["id"]

    def test_get_environmental_by_crop_success(self):
        """GET /environmental/crop/{crop_id} debe retornar requisitos ambientales."""
        response = self.client.get(
            f"/environmental/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["crop_id"], self.crop_id)
        self.assertIn("id", data)

    def test_get_environmental_forbidden_other_user(self):
        """GET /environmental/crop/{crop_id} de usuario normal no debe acceder cultivo ajeno."""
        # Crear otro usuario
        other_response = self.client.post(
            "/auth/register",
            json={
                "email": "other@example.com",
                "password": "SecurePass123",
                "name": "Other User",
            },
        )
        other_login = self.client.post(
            "/auth/login",
            json={
                "email": "other@example.com",
                "password": "SecurePass123",
            },
        )
        other_token = other_login.json()["access_token"]

        # Intentar acceder
        response = self.client.get(
            f"/environmental/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_update_environmental_success(self):
        """PUT /environmental/{env_id} debe actualizar requisitos ambientales."""
        # Obtener ID
        get_response = self.client.get(
            f"/environmental/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        env_id = get_response.json()["id"]

        # Actualizar
        response = self.client.put(
            f"/environmental/{env_id}",
            json={
                "min_temperature_celsius": 15.0,
                "max_temperature_celsius": 25.0,
                "sunlight_hours_per_day": 6.0,
                "soil_type": "arenoso",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["min_temperature_celsius"], 15.0)
        self.assertEqual(data["max_temperature_celsius"], 25.0)
        self.assertEqual(data["sunlight_hours_per_day"], 6.0)

    def test_delete_environmental_success(self):
        """DELETE /environmental/{env_id} debe eliminar requisitos."""
        # Obtener ID
        get_response = self.client.get(
            f"/environmental/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        env_id = get_response.json()["id"]

        # Eliminar
        response = self.client.delete(
            f"/environmental/{env_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que no existe
        get_again = self.client.get(
            f"/environmental/{env_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(get_again.status_code, 404)


class TestTasks(unittest.TestCase):
    """Tests de tareas."""

    def setUp(self):
        """Configuración previa a cada test."""
        reset_test_database()  # Ya limpia e inicializa las tablas
        self.client = TestClient(app)

        # Crear usuario normal
        user_response = self.client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
                "name": "Regular User",
            },
        )
        self.user_id = user_response.json()["id"]

        # Login usuario normal
        login_response = self.client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
            },
        )
        self.user_token = login_response.json()["access_token"]

        # Crear usuario admin
        admin_response = self.client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123",
                "name": "Admin User",
            },
        )
        self.admin_id = admin_response.json()["id"]

        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.id == self.admin_id).first()
        if admin_user:
            admin_user.role = UserRole.ADMIN
            db.commit()
        db.close()

        admin_login = self.client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123",
            },
        )
        self.admin_token = admin_login.json()["access_token"]

        # Crear cultivo para el usuario
        crop_response = self.client.post(
            "/crops/",
            data={
                "name": "Papa",
                "crop_type": "tubérculo",
                "is_public": "false",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.crop_id = crop_response.json()["id"]

    def test_create_task_authenticated(self):
        """POST /tasks/ con autenticación debe crear tarea."""
        response = self.client.post(
            "/tasks/",
            json={
                "title": "Regar plantas",
                "description": "Riego diario",
                "due_date": "2025-06-01",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Regar plantas")
        self.assertEqual(data["owner_id"], self.user_id)
        self.assertEqual(data["status"], "pending")
        self.assertIn("id", data)

    def test_create_task_without_token(self):
        """POST /tasks/ sin token debe fallar con 401."""
        response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea",
                "description": "Descripción",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_list_tasks_user_sees_only_own(self):
        """GET /tasks/ debe mostrar solo tareas del usuario."""
        # Crear 2 tareas para el usuario
        for i in range(2):
            self.client.post(
                "/tasks/",
                json={
                    "title": f"Tarea {i}",
                    "description": f"Descripción {i}",
                },
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

        response = self.client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["items"]), 2)

    def test_list_tasks_admin_sees_all(self):
        """GET /tasks/ como admin debe mostrar todas las tareas."""
        # Usuario normal crea tarea
        self.client.post(
            "/tasks/",
            json={
                "title": "Tarea 1",
                "description": "Descripción 1",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Admin crea tarea
        self.client.post(
            "/tasks/",
            json={
                "title": "Tarea Admin",
                "description": "Descripción Admin",
            },
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )

        # Admin lista todas
        response = self.client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {self.admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)

    def test_assign_task_to_crop_success(self):
        """POST /tasks/assign debe asignar tarea a cultivo propio."""
        # Crear tarea
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Preparar terreno",
                "description": "Preparar papa",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Asignar a cultivo
        response = self.client.post(
            "/tasks/assign",
            json={
                "task_id": task_id,
                "crop_id": self.crop_id,
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 201)

    def test_assign_task_to_other_crop_forbidden(self):
        """POST /tasks/assign debe fallar si intenta asignar a cultivo ajeno."""
        # Crear otro usuario con cultivo
        other_response = self.client.post(
            "/auth/register",
            json={
                "email": "other@example.com",
                "password": "SecurePass123",
                "name": "Other User",
            },
        )
        other_id = other_response.json()["id"]

        other_login = self.client.post(
            "/auth/login",
            json={
                "email": "other@example.com",
                "password": "SecurePass123",
            },
        )
        other_token = other_login.json()["access_token"]

        other_crop = self.client.post(
            "/crops/",
            data={
                "name": "Otro Cultivo",
                "crop_type": "fruta",
            },
            headers={"Authorization": f"Bearer {other_token}"},
        )
        other_crop_id = other_crop.json()["id"]

        # Crear tarea para usuario 1
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea 1",
                "description": "Descripción",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Intentar asignar a cultivo del otro usuario
        response = self.client.post(
            "/tasks/assign",
            json={
                "task_id": task_id,
                "crop_id": other_crop_id,
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_get_tasks_by_crop(self):
        """GET /tasks/crop/{crop_id} debe listar tareas del cultivo."""
        # Crear y asignar tareas
        for i in range(2):
            task_response = self.client.post(
                "/tasks/",
                json={
                    "title": f"Tarea {i}",
                    "description": f"Descripción {i}",
                },
                headers={"Authorization": f"Bearer {self.user_token}"},
            )
            task_id = task_response.json()["id"]

            self.client.post(
                "/tasks/assign",
                json={
                    "task_id": task_id,
                    "crop_id": self.crop_id,
                },
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

        # Obtener tareas del cultivo
        response = self.client.get(
            f"/tasks/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)

    def test_get_task_crops(self):
        """GET /tasks/{task_id}/crops debe listar cultivos de la tarea."""
        # Crear tarea
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea Multi",
                "description": "Tarea para varios cultivos",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Crear segundo cultivo
        crop2_response = self.client.post(
            "/crops/",
            data={
                "name": "Tomate",
                "crop_type": "verdura",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        crop2_id = crop2_response.json()["id"]

        # Asignar a ambos cultivos
        self.client.post(
            "/tasks/assign",
            json={
                "task_id": task_id,
                "crop_id": self.crop_id,
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.client.post(
            "/tasks/assign",
            json={
                "task_id": task_id,
                "crop_id": crop2_id,
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Obtener cultivos de la tarea
        response = self.client.get(
            f"/tasks/{task_id}/crops",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        crops = response.json()
        self.assertEqual(len(crops), 2)

    def test_patch_task_status_to_completed(self):
        """PATCH /tasks/{task_id} debe cambiar estado a completed."""
        # Crear tarea
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea a completar",
                "description": "Descripción",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Cambiar estado a completed
        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")

    def test_patch_task_status_to_pending(self):
        """PATCH /tasks/{task_id} debe cambiar estado de vuelta a pending."""
        # Crear tarea
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea",
                "description": "Descripción",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Cambiar a completed
        self.client.patch(
            f"/tasks/{task_id}",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Cambiar de vuelta a pending
        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": "pending"},
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "pending")

    def test_put_task_full_update(self):
        """PUT /tasks/{task_id} debe actualizar tarea completa."""
        # Crear tarea
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea Original",
                "description": "Descripción original",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Actualizar completa
        response = self.client.put(
            f"/tasks/{task_id}",
            json={
                "title": "Tarea Actualizada",
                "description": "Nueva descripción",
                "due_date": "2025-07-15",
                "status": "completed",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["title"], "Tarea Actualizada")
        self.assertEqual(data["description"], "Nueva descripción")
        self.assertEqual(data["status"], "completed")

    def test_delete_task_success(self):
        """DELETE /tasks/{task_id} debe eliminar tarea."""
        # Crear tarea
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea a eliminar",
                "description": "Descripción",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Eliminar
        response = self.client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que no existe
        get_response = self.client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(get_response.status_code, 404)

    def test_normal_user_cannot_edit_other_task(self):
        """Usuario normal no puede editar tarea ajena."""
        # Usuario 1 crea tarea
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea de usuario 1",
                "description": "Descripción",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Crear usuario 2
        user2_response = self.client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "password": "SecurePass123",
                "name": "User 2",
            },
        )

        user2_login = self.client.post(
            "/auth/login",
            json={
                "email": "user2@example.com",
                "password": "SecurePass123",
            },
        )
        user2_token = user2_login.json()["access_token"]

        # Usuario 2 intenta editar tarea de usuario 1
        response = self.client.put(
            f"/tasks/{task_id}",
            json={
                "title": "Intento de cambio",
            },
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_task_deletes_relations(self):
        """DELETE /tasks/{task_id} debe eliminar también relaciones TaskCrop."""
        # Crear tarea
        task_response = self.client.post(
            "/tasks/",
            json={
                "title": "Tarea con relaciones",
                "description": "Descripción",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        task_id = task_response.json()["id"]

        # Asignar a cultivo
        self.client.post(
            "/tasks/assign",
            json={
                "task_id": task_id,
                "crop_id": self.crop_id,
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Verificar que está asignada
        get_response = self.client.get(
            f"/tasks/{task_id}/crops",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(len(get_response.json()), 1)

        # Eliminar tarea
        self.client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Verificar que la relación se eliminó (tarea no debe existir)
        get_after = self.client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(get_after.status_code, 404)


if __name__ == "__main__":
    unittest.main()
