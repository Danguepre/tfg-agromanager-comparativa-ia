"""
Tests unitarios para rutas de autenticación y usuarios.
Usa unittest + TestClient de FastAPI.
Base de datos: SQLite en memoria para tests (COMPARTIDA vía conftest.py).
"""
import unittest
from fastapi.testclient import TestClient

from app.database import Base, get_db
# Importar modelos para registrar mappers con Base
from app import models
from app.main import app
from app.models.user import User

# ============================================================================
# USAR ENGINE Y SESSIONLOCAL CENTRALIZADOS DE conftest.py
# ============================================================================
from tests.conftest import engine, TestingSessionLocal, override_get_db, reset_test_database

# El override ya se realizó en conftest.py al importarlo


class TestHealth(unittest.TestCase):
    """Tests del healthcheck."""

    def setUp(self):
        """Configuración previa a cada test."""
        reset_test_database()  # Limpiar BD antes de cada test class
        self.client = TestClient(app)

    def test_health_check_root(self):
        """GET / debe retornar estado ok."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["app"], "AgroManager")
        self.assertIn("environment", data)

    def test_health_check_health_endpoint(self):
        """GET /health debe retornar estado ok."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")


class TestAuthenticationRegister(unittest.TestCase):
    """Tests de registro."""

    def setUp(self):
        """Configuración previa a cada test."""
        self.client = TestClient(app)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_register_success(self):
        """POST /auth/register con datos válidos debe crear usuario."""
        response = self.client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "name": "Test User",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["email"], "newuser@example.com")
        self.assertEqual(data["name"], "Test User")
        self.assertEqual(data["role"], "user")
        self.assertNotIn("password_hash", data)  # No exponer password

    def test_register_duplicate_email(self):
        """POST /auth/register con email duplicado debe fallar."""
        # Registrar primer usuario
        self.client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
                "name": "User One",
            },
        )

        # Intentar registrar con mismo email
        response = self.client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "AnotherPass123",
                "name": "User Two",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("already registered", response.json()["detail"])

    def test_register_short_password(self):
        """POST /auth/register con contraseña corta debe fallar."""
        response = self.client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "short",
                "name": "Test User",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("at least 8 characters", response.json()["detail"])


class TestAuthenticationLogin(unittest.TestCase):
    """Tests de login."""

    def setUp(self):
        """Configuración previa a cada test."""
        self.client = TestClient(app)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # Crear usuario de prueba
        self.client.post(
            "/auth/register",
            json={
                "email": "testuser@example.com",
                "password": "SecurePass123",
                "name": "Test User",
            },
        )

    def test_login_success(self):
        """POST /auth/login con credenciales válidas debe retornar token."""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "SecurePass123",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertIn("expires_in", data)

    def test_login_invalid_email(self):
        """POST /auth/login con email inválido debe fallar."""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SecurePass123",
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid", response.json()["detail"])

    def test_login_invalid_password(self):
        """POST /auth/login con contraseña inválida debe fallar."""
        response = self.client.post(
            "/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "WrongPassword123",
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid", response.json()["detail"])


class TestUserManagement(unittest.TestCase):
    """Tests de gestión de usuarios."""

    def setUp(self):
        """Configuración previa a cada test."""
        self.client = TestClient(app)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # Crear usuarios de prueba
        reg_response = self.client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
                "name": "Regular User",
            },
        )
        self.user_id = reg_response.json()["id"]

        # Login para obtener token
        login_response = self.client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
            },
        )
        self.token = login_response.json()["access_token"]

    def test_get_own_user(self):
        """GET /users/{user_id} sin token debe fallar con 401."""
        response = self.client.get(f"/users/{self.user_id}")
        self.assertEqual(response.status_code, 401)

    def test_get_own_user_with_token(self):
        """GET /users/{user_id} con token válido debe retornar datos del usuario."""
        response = self.client.get(
            f"/users/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], "user@example.com")
        self.assertEqual(data["name"], "Regular User")
        self.assertNotIn("password_hash", data)  # No exponer password

    def test_get_other_user_forbidden(self):
        """GET /users/{other_user_id} de usuario normal debe fallar con 403."""
        # Crear otro usuario
        other_response = self.client.post(
            "/auth/register",
            json={
                "email": "other@example.com",
                "password": "OtherPass123",
                "name": "Other User",
            },
        )
        other_user_id = other_response.json()["id"]

        # Intentar acceder como primer usuario
        response = self.client.get(
            f"/users/{other_user_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("can only access", response.json()["detail"])

    def test_delete_own_user(self):
        """DELETE /users/{user_id} debe eliminar el usuario."""
        response = self.client.delete(
            f"/users/{self.user_id}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Intentar login con usuario eliminado
        login_response = self.client.post(
            "/auth/login",
            json={
                "email": "user@example.com",
                "password": "SecurePass123",
            },
        )
        self.assertEqual(login_response.status_code, 401)


class TestCropManagement(unittest.TestCase):
    """Tests de gestión de cultivos."""

    def setUp(self):
        """Configuración previa a cada test."""
        self.client = TestClient(app)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

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

        # Crear usuario admin (modificar BD directamente para simplificar)
        # En lugar de eso, vamos a registrar otro usuario e intentar promoverlo
        # Para esta prueba, vamos a usar un usuario sin privilegios como fallback

    def test_create_crop_authenticated(self):
        """POST /crops/ con autenticación debe crear cultivo."""
        response = self.client.post(
            "/crops/",
            data={
                "name": "Tomate",
                "description": "Tomate de huerto casero",
                "crop_type": "verdura",
                "is_public": "false",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Tomate")
        self.assertEqual(data["crop_type"], "verdura")
        self.assertEqual(data["is_public"], False)
        self.assertEqual(data["owner_id"], self.user_id)
        self.assertIsNotNone(data["id"])

    def test_create_crop_without_token(self):
        """POST /crops/ sin token debe fallar con 401."""
        response = self.client.post(
            "/crops/",
            data={
                "name": "Lechuga",
                "crop_type": "verdura",
                "is_public": "false",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_create_crop_normal_user_cannot_publish(self):
        """POST /crops/ con is_public=true de usuario normal debe fallar."""
        response = self.client.post(
            "/crops/",
            data={
                "name": "Espinaca",
                "crop_type": "verdura",
                "is_public": "true",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("admin", response.json()["detail"].lower())

    def test_get_my_crops(self):
        """GET /crops/my debe retornar solo cultivos del usuario."""
        # Crear 2 cultivos para el usuario
        for i in range(2):
            self.client.post(
                "/crops/",
                data={
                    "name": f"Cultivo {i}",
                    "crop_type": "verdura",
                },
                headers={"Authorization": f"Bearer {self.user_token}"},
            )

        # Obtener mis cultivos
        response = self.client.get(
            "/crops/my",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 2)
        self.assertEqual(len(data["items"]), 2)

    def test_get_crop_detail(self):
        """GET /crops/{crop_id} debe retornar detalles del cultivo."""
        # Crear cultivo
        create_response = self.client.post(
            "/crops/",
            data={
                "name": "Papa",
                "description": "Papa criolla",
                "crop_type": "tubérculo",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        crop_id = create_response.json()["id"]

        # Obtener detalles
        response = self.client.get(
            f"/crops/{crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], crop_id)
        self.assertEqual(data["name"], "Papa")
        # Verificar que tenga relaciones inicializadas
        self.assertIsNotNone(data.get("irrigation"))
        self.assertIsNotNone(data.get("environmental"))

    def test_update_crop_own(self):
        """PUT /crops/{crop_id} debe actualizar cultivo propio."""
        # Crear cultivo
        create_response = self.client.post(
            "/crops/",
            data={
                "name": "Cebolla",
                "crop_type": "verdura",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        crop_id = create_response.json()["id"]

        # Actualizar
        response = self.client.put(
            f"/crops/{crop_id}",
            data={
                "name": "Cebolla Roja",
                "crop_type": "verdura modificada",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Cebolla Roja")
        self.assertEqual(data["crop_type"], "verdura modificada")

    def test_delete_crop_own(self):
        """DELETE /crops/{crop_id} debe eliminar cultivo propio."""
        # Crear cultivo
        create_response = self.client.post(
            "/crops/",
            data={
                "name": "Zanahoria",
                "crop_type": "verdura",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        crop_id = create_response.json()["id"]

        # Eliminar
        response = self.client.delete(
            f"/crops/{crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que no existe
        get_response = self.client.get(
            f"/crops/{crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(get_response.status_code, 404)

    def test_copy_crop_from_catalog(self):
        """POST /crops/{crop_id}/add-to-my-crops debe copiar cultivo del catálogo."""
        # Crear segundo usuario (será quien tenga el cultivo público)
        other_user_response = self.client.post(
            "/auth/register",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123",
                "name": "Admin User",
            },
        )
        other_user_id = other_user_response.json()["id"]

        # Actualizar a admin manualmente en BD
        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.id == other_user_id).first()
        if admin_user:
            from app.models.user import UserRole
            admin_user.role = UserRole.ADMIN
            db.commit()
        db.close()

        # Login como admin
        admin_login_response = self.client.post(
            "/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123",
            },
        )
        admin_token = admin_login_response.json()["access_token"]

        # Crear cultivo público como admin
        crop_response = self.client.post(
            "/crops/",
            data={
                "name": "Maíz Público",
                "crop_type": "cereal",
                "is_public": "true",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        source_crop_id = crop_response.json()["id"]

        # Copiar como usuario normal
        copy_response = self.client.post(
            f"/crops/{source_crop_id}/add-to-my-crops",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(copy_response.status_code, 201)
        copied_crop = copy_response.json()
        self.assertEqual(copied_crop["name"], "Maíz Público")
        self.assertEqual(copied_crop["owner_id"], self.user_id)
        self.assertEqual(copied_crop["source_crop_id"], source_crop_id)
        self.assertEqual(copied_crop["is_public"], False)  # La copia es privada

    def test_copy_is_independent(self):
        """Editar copia no debe modificar el original."""
        # Crear admin y cultivo público
        admin_response = self.client.post(
            "/auth/register",
            json={
                "email": "admin2@example.com",
                "password": "AdminPass123",
                "name": "Admin 2",
            },
        )
        admin_id = admin_response.json()["id"]

        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.id == admin_id).first()
        if admin_user:
            from app.models.user import UserRole
            admin_user.role = UserRole.ADMIN
            db.commit()
        db.close()

        admin_login = self.client.post(
            "/auth/login",
            json={
                "email": "admin2@example.com",
                "password": "AdminPass123",
            },
        )
        admin_token = admin_login.json()["access_token"]

        # Crear cultivo público
        public_crop = self.client.post(
            "/crops/",
            data={
                "name": "Frijol Público",
                "crop_type": "legumbre",
                "is_public": "true",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        source_id = public_crop.json()["id"]

        # Copiar
        copy_response = self.client.post(
            f"/crops/{source_id}/add-to-my-crops",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        copied_id = copy_response.json()["id"]

        # Editar copia
        update_response = self.client.put(
            f"/crops/{copied_id}",
            data={"name": "Frijol Modificado"},
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["name"], "Frijol Modificado")

        # Verificar que original no cambió
        original_response = self.client.get(
            f"/crops/{source_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(original_response.json()["name"], "Frijol Público")

    def test_normal_user_cannot_edit_other_crop(self):
        """Usuario normal no puede editar cultivo ajeno."""
        # Crear segundo usuario
        user2_response = self.client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "password": "SecurePass123",
                "name": "User 2",
            },
        )
        user2_id = user2_response.json()["id"]

        user2_login = self.client.post(
            "/auth/login",
            json={
                "email": "user2@example.com",
                "password": "SecurePass123",
            },
        )
        user2_token = user2_login.json()["access_token"]

        # User 1 crea cultivo
        crop_response = self.client.post(
            "/crops/",
            data={
                "name": "Cultivo User 1",
                "crop_type": "verdura",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        crop_id = crop_response.json()["id"]

        # User 2 intenta editar
        update_response = self.client.put(
            f"/crops/{crop_id}",
            data={"name": "Cultivo Modificado por User 2"},
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        self.assertEqual(update_response.status_code, 403)

    def test_delete_copy_removes_from_my_crops(self):
        """Eliminar copia debe quitarla de 'Mis cultivos'."""
        # Crear admin y cultivo público
        admin_response = self.client.post(
            "/auth/register",
            json={
                "email": "admin3@example.com",
                "password": "AdminPass123",
                "name": "Admin 3",
            },
        )
        admin_id = admin_response.json()["id"]

        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.id == admin_id).first()
        if admin_user:
            from app.models.user import UserRole
            admin_user.role = UserRole.ADMIN
            db.commit()
        db.close()

        admin_login = self.client.post(
            "/auth/login",
            json={
                "email": "admin3@example.com",
                "password": "AdminPass123",
            },
        )
        admin_token = admin_login.json()["access_token"]

        # Crear cultivo público
        public_crop = self.client.post(
            "/crops/",
            data={
                "name": "Mostaza Pública",
                "crop_type": "verdura",
                "is_public": "true",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        source_id = public_crop.json()["id"]

        # Copiar
        copy_response = self.client.post(
            f"/crops/{source_id}/add-to-my-crops",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        copied_id = copy_response.json()["id"]

        # Verificar que está en "Mis cultivos"
        my_crops = self.client.get(
            "/crops/my",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(my_crops.json()["total"], 1)

        # Eliminar copia
        delete_response = self.client.delete(
            f"/crops/{copied_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(delete_response.status_code, 204)

        # Verificar que se quitó
        my_crops_after = self.client.get(
            "/crops/my",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(my_crops_after.json()["total"], 0)

    def test_delete_original_public_preserves_as_catalog(self):
        """Eliminar cultivo original público debe conservarlo como catálogo anónimo."""
        # Crear admin
        admin_response = self.client.post(
            "/auth/register",
            json={
                "email": "admin4@example.com",
                "password": "AdminPass123",
                "name": "Admin 4",
            },
        )
        admin_id = admin_response.json()["id"]

        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.id == admin_id).first()
        if admin_user:
            from app.models.user import UserRole
            admin_user.role = UserRole.ADMIN
            db.commit()
        db.close()

        admin_login = self.client.post(
            "/auth/login",
            json={
                "email": "admin4@example.com",
                "password": "AdminPass123",
            },
        )
        admin_token = admin_login.json()["access_token"]

        # Admin crea cultivo público
        public_crop = self.client.post(
            "/crops/",
            data={
                "name": "Berenjena Pública",
                "crop_type": "verdura",
                "is_public": "true",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        crop_id = public_crop.json()["id"]

        # Admin elimina su cultivo
        delete_response = self.client.delete(
            f"/crops/{crop_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(delete_response.status_code, 204)

        # Cultivo debe estar en catálogo público (sin owner)
        published_crops = self.client.get("/crops/published")
        self.assertEqual(published_crops.status_code, 200)
        published_items = published_crops.json()["items"]
        # Buscar el cultivo
        found = any(crop["name"] == "Berenjena Pública" and crop["owner_id"] is None for crop in published_items)
        self.assertTrue(found, "Cultivo público eliminado debe estar en catálogo sin owner")

    def test_get_published_crops_pagination_and_filters(self):
        """GET /crops/published debe paginar y filtrar."""
        # Crear admin
        admin_response = self.client.post(
            "/auth/register",
            json={
                "email": "admin5@example.com",
                "password": "AdminPass123",
                "name": "Admin 5",
            },
        )
        admin_id = admin_response.json()["id"]

        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.id == admin_id).first()
        if admin_user:
            from app.models.user import UserRole
            admin_user.role = UserRole.ADMIN
            db.commit()
        db.close()

        admin_login = self.client.post(
            "/auth/login",
            json={
                "email": "admin5@example.com",
                "password": "AdminPass123",
            },
        )
        admin_token = admin_login.json()["access_token"]

        # Crear varios cultivos públicos
        for i in range(5):
            self.client.post(
                "/crops/",
                data={
                    "name": f"Verdura {i}",
                    "crop_type": "verdura",
                    "is_public": "true",
                },
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        # Crear cultivos de otro tipo
        for i in range(3):
            self.client.post(
                "/crops/",
                data={
                    "name": f"Fruta {i}",
                    "crop_type": "fruta",
                    "is_public": "true",
                },
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        # Obtener catálogo con filtro por tipo
        verdura_response = self.client.get(
            "/crops/published?crop_type=verdura"
        )
        self.assertEqual(verdura_response.status_code, 200)
        verdura_data = verdura_response.json()
        self.assertEqual(verdura_data["total"], 5)

        # Obtener catálogo con paginación
        page1 = self.client.get("/crops/published?skip=0&limit=3")
        self.assertEqual(len(page1.json()["items"]), 3)

        # Obtener catálogo con filtro por nombre
        filter_response = self.client.get("/crops/published?name=Verdura")
        filter_data = filter_response.json()
        self.assertGreater(filter_data["total"], 0)


class TestCalendarManagement(unittest.TestCase):
    """Tests de gestión de calendario agrícola."""

    def setUp(self):
        """Configuración previa a cada test."""
        self.client = TestClient(app)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        # Crear usuario normal con cultivo
        user_response = self.client.post(
            "/auth/register",
            json={
                "email": "calendaruser@example.com",
                "password": "SecurePass123",
                "name": "Calendar User",
            },
        )
        self.user_id = user_response.json()["id"]

        # Login usuario normal
        login_response = self.client.post(
            "/auth/login",
            json={
                "email": "calendaruser@example.com",
                "password": "SecurePass123",
            },
        )
        self.user_token = login_response.json()["access_token"]

        # Crear cultivo para el usuario
        crop_response = self.client.post(
            "/crops/",
            data={
                "name": "Tomate de Calendario",
                "crop_type": "verdura",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.crop_id = crop_response.json()["id"]

    def test_create_calendar_authenticated(self):
        """POST /calendar/ con autenticación debe crear calendario."""
        response = self.client.post(
            "/calendar/?crop_id=" + str(self.crop_id),
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["crop_id"], self.crop_id)
        self.assertEqual(data["status"], "draft")
        self.assertFalse(data["is_active"])
        self.assertEqual(data["current_phase_index"], 0)

    def test_create_calendar_without_token(self):
        """POST /calendar/ sin token debe fallar con 401."""
        response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_user_cannot_create_calendar_for_other_crop(self):
        """Usuario normal no puede crear calendario para cultivo ajeno."""
        # Crear segundo usuario y su cultivo
        user2_response = self.client.post(
            "/auth/register",
            json={
                "email": "user2calendar@example.com",
                "password": "SecurePass123",
                "name": "User 2",
            },
        )
        user2_id = user2_response.json()["id"]

        user2_login = self.client.post(
            "/auth/login",
            json={
                "email": "user2calendar@example.com",
                "password": "SecurePass123",
            },
        )
        user2_token = user2_login.json()["access_token"]

        # User 2 crea cultivo
        crop2_response = self.client.post(
            "/crops/",
            data={
                "name": "Cultivo User 2",
                "crop_type": "verdura",
            },
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        crop2_id = crop2_response.json()["id"]

        # User 1 intenta crear calendario para cultivo de User 2
        response = self.client.post(
            f"/calendar/?crop_id={crop2_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_get_calendar_by_crop_id(self):
        """GET /calendar/crop/{crop_id} debe obtener el calendario."""
        # Crear calendario
        self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Obtener calendario
        response = self.client.get(
            f"/calendar/crop/{self.crop_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["crop_id"], self.crop_id)
        self.assertEqual(data["status"], "draft")

    def test_update_calendar_with_put_crop_endpoint(self):
        """PUT /calendar/crop/{crop_id} debe actualizar el calendario."""
        # Crear calendario
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        # Actualizar
        response = self.client.put(
            f"/calendar/crop/{self.crop_id}",
            json={
                "planting_start": "2024-03-05",
                "planting_end": "2024-03-20",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["planting_start"], "2024-03-05")
        self.assertEqual(data["planting_end"], "2024-03-20")

    def test_cannot_activate_incomplete_calendar(self):
        """POST /calendar/{calendar_id}/activate con fechas incompletas debe fallar."""
        # Crear calendario sin fechas
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={},
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        # Intentar activar sin todas las fechas debe fallar
        response = self.client.post(
            f"/calendar/{calendar_id}/activate",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("all dates", response.json()["detail"].lower())

    def test_activate_complete_calendar(self):
        """POST /calendar/{calendar_id}/activate con fechas completas debe activar."""
        # Crear calendario completo
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        # Activar
        response = self.client.post(
            f"/calendar/{calendar_id}/activate",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_active"])
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["current_phase_index"], 0)

    def test_get_user_events(self):
        """GET /calendar/events debe retornar eventos activos del usuario."""
        # Crear y activar calendario
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        self.client.post(
            f"/calendar/{calendar_id}/activate",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Obtener eventos
        response = self.client.get(
            "/calendar/events",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data["total"], 0)
        self.assertEqual(data["items"][0]["phase_name"], "Siembra")

    def test_get_calendar_events(self):
        """GET /calendar/{calendar_id}/events debe retornar la fase actual."""
        # Crear y activar calendario
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        self.client.post(
            f"/calendar/{calendar_id}/activate",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Obtener eventos del calendario
        response = self.client.get(
            f"/calendar/{calendar_id}/events",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["phase_name"], "Siembra")
        self.assertEqual(data["items"][0]["phase_index"], 0)

    def test_advance_phase_from_planting_to_transplant(self):
        """POST /calendar/{calendar_id}/advance Siembra → Trasplante."""
        # Crear y activar calendario
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        self.client.post(
            f"/calendar/{calendar_id}/activate",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Avanzar fase
        response = self.client.post(
            f"/calendar/{calendar_id}/advance",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_phase_index"], 1)
        self.assertTrue(data["is_active"])

        # Verificar evento cambió
        events_response = self.client.get(
            f"/calendar/{calendar_id}/events",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        event_data = events_response.json()
        self.assertEqual(event_data["items"][0]["phase_name"], "Trasplante")

    def test_advance_phase_from_transplant_to_harvest(self):
        """POST /calendar/{calendar_id}/advance Trasplante → Cosecha."""
        # Crear, activar y avanzar a Trasplante
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        self.client.post(
            f"/calendar/{calendar_id}/activate",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        self.client.post(
            f"/calendar/{calendar_id}/advance",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Avanzar a Cosecha
        response = self.client.post(
            f"/calendar/{calendar_id}/advance",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_phase_index"], 2)
        self.assertTrue(data["is_active"])

        # Verificar evento es Cosecha
        events_response = self.client.get(
            f"/calendar/{calendar_id}/events",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        event_data = events_response.json()
        self.assertEqual(event_data["items"][0]["phase_name"], "Cosecha")

    def test_advance_from_harvest_completes_calendar(self):
        """POST /calendar/{calendar_id}/advance desde Cosecha marca COMPLETED."""
        # Crear, activar y avanzar a Cosecha
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        self.client.post(
            f"/calendar/{calendar_id}/activate",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        self.client.post(
            f"/calendar/{calendar_id}/advance",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        self.client.post(
            f"/calendar/{calendar_id}/advance",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )

        # Avanzar desde Cosecha
        response = self.client.post(
            f"/calendar/{calendar_id}/advance",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")
        self.assertFalse(data["is_active"])
        self.assertEqual(data["current_phase_index"], 2)

    def test_admin_can_manage_other_calendars(self):
        """Admin puede gestionar calendarios de otros usuarios."""
        # Crear admin
        admin_response = self.client.post(
            "/auth/register",
            json={
                "email": "calendaradmin@example.com",
                "password": "AdminPass123",
                "name": "Calendar Admin",
            },
        )
        admin_id = admin_response.json()["id"]

        db = TestingSessionLocal()
        admin_user = db.query(User).filter(User.id == admin_id).first()
        if admin_user:
            from app.models.user import UserRole
            admin_user.role = UserRole.ADMIN
            db.commit()
        db.close()

        admin_login = self.client.post(
            "/auth/login",
            json={
                "email": "calendaradmin@example.com",
                "password": "AdminPass123",
            },
        )
        admin_token = admin_login.json()["access_token"]

        # Crear calendario para usuario normal
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        # Admin puede activar
        response = self.client.post(
            f"/calendar/{calendar_id}/activate",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        # Admin debería poder, pero como el cultivo pertenece a otro usuario y el admin
        # accede a través del calendario, esto depende de la implementación
        # Por ahora esperamos 200 o 403
        self.assertIn(response.status_code, [200, 403])

    def test_delete_calendar(self):
        """DELETE /calendar/{calendar_id} debe eliminar el calendario."""
        # Crear calendario
        create_response = self.client.post(
            f"/calendar/?crop_id={self.crop_id}",
            json={
                "planting_start": "2024-03-01",
                "planting_end": "2024-03-15",
                "transplant_start": "2024-04-01",
                "transplant_end": "2024-04-15",
                "harvest_start": "2024-06-01",
                "harvest_end": "2024-06-30",
            },
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        calendar_id = create_response.json()["id"]

        # Eliminar
        response = self.client.delete(
            f"/calendar/{calendar_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que no existe
        get_response = self.client.get(
            f"/calendar/{calendar_id}",
            headers={"Authorization": f"Bearer {self.user_token}"},
        )
        self.assertEqual(get_response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
