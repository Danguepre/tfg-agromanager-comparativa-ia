"""Tests de API usando unittest y TestClient.

Ejecutar con: python -m unittest discover -s tests -p "test*.py" -v
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto está en sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


# Base de datos SQLite en archivo para tests
TEST_DATABASE_URL = "sqlite:///./test_agromanager.db"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Sobrescribe la dependencia get_db para usar BD de test."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestAgroManagerAPI(unittest.TestCase):
    """Suite de tests para la API de AgroManager."""

    @classmethod
    def setUpClass(cls):
        """Crea las tablas e instala dependency_overrides una vez antes de todos los tests."""
        Base.metadata.create_all(bind=test_engine)
        app.dependency_overrides[get_db] = override_get_db

    @classmethod
    def tearDownClass(cls):
        """Limpia dependency_overrides, elimina tablas y cierra conexiones."""
        # Limpiar dependency_overrides para no contaminar otros tests
        if get_db in app.dependency_overrides:
            del app.dependency_overrides[get_db]
        Base.metadata.drop_all(bind=test_engine)
        # Dispose del engine para liberar todas las conexiones SQLite
        test_engine.dispose()
        # Limpiar el archivo de base de datos de test
        db_path = os.path.join(PROJECT_ROOT, "test_agromanager.db")
        for suffix in ("", "-wal", "-shm"):
            path = db_path + suffix
            try:
                if os.path.exists(path):
                    os.remove(path)
            except PermissionError:
                pass  # Ignorar si Windows aún tiene el archivo bloqueado

    def setUp(self):
        """Limpia los datos antes de cada test."""
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)
        self.client = TestClient(app)

    def _create_user(self, username="testuser", password="secure123"):
        """Helper para crear un usuario normal y devolver su token."""
        self.client.post(
            "/users/",
            json={
                "email": f"{username}@test.com",
                "username": username,
                "password": password,
                "full_name": f"{username} User",
            },
        )
        login_resp = self.client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        return login_resp.json()["access_token"]

    def _create_admin(self, username="admin", password="adminpass"):
        """Helper para crear un admin y devolver su token."""
        db = TestSessionLocal()
        from app.auth import hash_password
        from app.models.user import User
        admin_user = User(
            email=f"{username}@test.com",
            username=username,
            hashed_password=hash_password(password),
            role="admin",
        )
        db.add(admin_user)
        db.commit()
        db.close()

        login_resp = self.client.post(
            "/auth/login",
            json={"username": username, "password": password},
        )
        return login_resp.json()["access_token"]

    # =====================================================================
    # Tests existentes (fase piloto)
    # =====================================================================

    def test_health_check(self):
        """GET / debe devolver status ok."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("message", data)
        self.assertIn("version", data)

    def test_register_user(self):
        """POST /users/ debe registrar un usuario normal."""
        response = self.client.post(
            "/users/",
            json={
                "email": "user@test.com",
                "username": "testuser",
                "password": "secure123",
                "full_name": "Test User",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["email"], "user@test.com")
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["role"], "user")
        self.assertTrue(data["is_active"])
        self.assertIn("id", data)
        # No se expone password ni hashed_password
        self.assertNotIn("password", data)
        self.assertNotIn("hashed_password", response.text)

    def test_register_duplicate_email(self):
        """POST /users/ con email duplicado debe fallar."""
        self.client.post(
            "/users/",
            json={
                "email": "dup@test.com",
                "username": "user1",
                "password": "pass123",
            },
        )
        response = self.client.post(
            "/users/",
            json={
                "email": "dup@test.com",
                "username": "user2",
                "password": "pass456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json()["detail"].lower())

    def test_register_duplicate_username(self):
        """POST /users/ con username duplicado debe fallar."""
        self.client.post(
            "/users/",
            json={
                "email": "a@test.com",
                "username": "sameuser",
                "password": "pass123",
            },
        )
        response = self.client.post(
            "/users/",
            json={
                "email": "b@test.com",
                "username": "sameuser",
                "password": "pass456",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("usuario", response.json()["detail"].lower())

    def test_register_cannot_become_admin(self):
        """El registro público no debe permitir crear usuarios admin."""
        response = self.client.post(
            "/users/",
            json={
                "email": "hacker@test.com",
                "username": "hacker",
                "password": "pass123",
                "role": "admin",
            },
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        # Aunque envíe role=admin, debe crearse como user
        self.assertEqual(data["role"], "user")

    def test_login_success(self):
        """POST /auth/login con credenciales válidas devuelve access_token."""
        # Registrar usuario
        self.client.post(
            "/users/",
            json={
                "email": "logintest@test.com",
                "username": "logintest",
                "password": "mypassword",
            },
        )
        # Login
        response = self.client.post(
            "/auth/login",
            json={"username": "logintest", "password": "mypassword"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        # El token debe ser un string no vacío
        self.assertTrue(len(data["access_token"]) > 0)

    def test_login_wrong_password(self):
        """POST /auth/login con password incorrecta debe fallar."""
        self.client.post(
            "/users/",
            json={
                "email": "wrongpw@test.com",
                "username": "wrongpw",
                "password": "correctpass",
            },
        )
        response = self.client.post(
            "/auth/login",
            json={"username": "wrongpw", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 401)

    def test_login_nonexistent_user(self):
        """POST /auth/login con usuario inexistente debe fallar."""
        response = self.client.post(
            "/auth/login",
            json={"username": "noexists", "password": "anypass"},
        )
        self.assertEqual(response.status_code, 401)

    def test_protected_route_without_token(self):
        """GET /users/ sin token debe devolver 401."""
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, 401)

    def test_protected_route_with_invalid_token(self):
        """GET /users/ con token inválido debe devolver 401."""
        response = self.client.get(
            "/users/",
            headers={"Authorization": "Bearer invalid_token_123"},
        )
        self.assertEqual(response.status_code, 401)

    def test_user_cannot_see_other_users(self):
        """Usuario normal solo debe ver su propio perfil en GET /users/."""
        # Registrar usuario 1
        self.client.post(
            "/users/",
            json={
                "email": "user1@test.com",
                "username": "user1",
                "password": "pass1",
            },
        )
        # Registrar usuario 2
        self.client.post(
            "/users/",
            json={
                "email": "user2@test.com",
                "username": "user2",
                "password": "pass2",
            },
        )
        # Login como user1
        login_resp = self.client.post(
            "/auth/login",
            json={"username": "user1", "password": "pass1"},
        )
        token = login_resp.json()["access_token"]

        # Obtener lista de usuarios como user1
        response = self.client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        users = response.json()
        # Solo debe ver su propio perfil
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["username"], "user1")

    def test_user_cannot_access_other_user_by_id(self):
        """Usuario normal no puede ver datos de otro usuario por ID."""
        self.client.post(
            "/users/",
            json={
                "email": "alice@test.com",
                "username": "alice",
                "password": "pass1",
            },
        )
        self.client.post(
            "/users/",
            json={
                "email": "bob@test.com",
                "username": "bob",
                "password": "pass2",
            },
        )
        login_resp = self.client.post(
            "/auth/login",
            json={"username": "alice", "password": "pass1"},
        )
        token = login_resp.json()["access_token"]

        # Alice intenta ver a Bob (id=2)
        response = self.client.get(
            "/users/2",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_see_all_users(self):
        """Admin puede ver todos los usuarios en GET /users/."""
        # Crear usuarios normales
        self.client.post(
            "/users/",
            json={
                "email": "nobody@test.com",
                "username": "nobody",
                "password": "pass",
            },
        )
        # Crear admin (simulando endpoint protegido, insertamos directamente en BD)
        db = TestSessionLocal()
        from app.auth import hash_password
        from app.models.user import User
        admin_user = User(
            email="admin@test.com",
            username="admin",
            hashed_password=hash_password("adminpass"),
            role="admin",
        )
        db.add(admin_user)
        db.commit()
        db.close()

        # Login como admin
        login_resp = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "adminpass"},
        )
        token = login_resp.json()["access_token"]

        # Admin ve todos
        response = self.client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertGreaterEqual(len(users), 2)

    def test_get_user_by_id(self):
        """GET /users/{user_id} devuelve el usuario correcto."""
        self.client.post(
            "/users/",
            json={
                "email": "target@test.com",
                "username": "target",
                "password": "pass",
            },
        )
        login_resp = self.client.post(
            "/auth/login",
            json={"username": "target", "password": "pass"},
        )
        token = login_resp.json()["access_token"]

        response = self.client.get(
            "/users/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "target")

    def test_get_nonexistent_user(self):
        """GET /users/{user_id} con ID inexistente debe dar 404."""
        self.client.post(
            "/users/",
            json={
                "email": "exists@test.com",
                "username": "exists",
                "password": "pass",
            },
        )
        login_resp = self.client.post(
            "/auth/login",
            json={"username": "exists", "password": "pass"},
        )
        token = login_resp.json()["access_token"]

        response = self.client.get(
            "/users/999",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_user_by_admin(self):
        """DELETE /users/{user_id} funcionando para admin."""
        self.client.post(
            "/users/",
            json={
                "email": "todelete@test.com",
                "username": "todelete",
                "password": "pass",
            },
        )
        # Crear admin directamente
        db = TestSessionLocal()
        from app.auth import hash_password
        from app.models.user import User
        admin_user = User(
            email="admin2@test.com",
            username="admin2",
            hashed_password=hash_password("adminpass"),
            role="admin",
        )
        db.add(admin_user)
        db.commit()
        db.close()

        login_resp = self.client.post(
            "/auth/login",
            json={"username": "admin2", "password": "adminpass"},
        )
        token = login_resp.json()["access_token"]

        response = self.client.delete(
            "/users/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_user_forbidden_for_normal_user(self):
        """Un usuario normal no puede eliminar a otro."""
        self.client.post(
            "/users/",
            json={
                "email": "victim@test.com",
                "username": "victim",
                "password": "pass",
            },
        )
        self.client.post(
            "/users/",
            json={
                "email": "attacker@test.com",
                "username": "attacker",
                "password": "pass",
            },
        )
        login_resp = self.client.post(
            "/auth/login",
            json={"username": "attacker", "password": "pass"},
        )
        token = login_resp.json()["access_token"]

        response = self.client.delete(
            "/users/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)

    # =====================================================================
    # Tests FASE 4: Cultivos y catálogo
    # =====================================================================

    def test_create_crop_authenticated(self):
        """Usuario autenticado puede crear un cultivo."""
        token = self._create_user()
        response = self.client.post(
            "/crops/",
            data={"name": "Tomate", "category": "Hortalizas"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Tomate")
        self.assertEqual(data["category"], "Hortalizas")
        self.assertFalse(data["is_public"])
        self.assertIsNotNone(data["owner_id"])
        self.assertIsNotNone(data["image_url"])

    def test_create_crop_without_token_fails(self):
        """Usuario sin token no puede crear cultivo."""
        response = self.client.post(
            "/crops/",
            data={"name": "Tomate"},
        )
        self.assertEqual(response.status_code, 401)

    def test_normal_user_cannot_create_public_crop(self):
        """Usuario normal no puede crear cultivo público."""
        token = self._create_user()
        response = self.client.post(
            "/crops/",
            data={"name": "Tomate", "is_public": "true"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("administradores", response.json()["detail"].lower())

    def test_admin_can_create_public_crop(self):
        """Admin puede crear cultivo publicado."""
        token = self._create_admin()
        response = self.client.post(
            "/crops/",
            data={"name": "Tomate Público", "is_public": "true", "category": "Hortalizas"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["is_public"])

    def test_my_crops_returns_only_user_crops(self):
        """GET /crops/my devuelve solo cultivos del usuario."""
        token1 = self._create_user("user_a")
        token2 = self._create_user("user_b")

        # user_a crea un cultivo
        self.client.post(
            "/crops/",
            data={"name": "Cultivo de A"},
            headers={"Authorization": f"Bearer {token1}"},
        )
        # user_b crea un cultivo
        self.client.post(
            "/crops/",
            data={"name": "Cultivo de B"},
            headers={"Authorization": f"Bearer {token2}"},
        )

        # user_a ve sus cultivos
        response = self.client.get(
            "/crops/my",
            headers={"Authorization": f"Bearer {token1}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Cultivo de A")

    def test_published_crops_pagination_and_filters(self):
        """GET /crops/published pagina y filtra."""
        admin_token = self._create_admin()

        # Crear varios cultivos públicos
        for i in range(5):
            self.client.post(
                "/crops/",
                data={
                    "name": f"Público {i}",
                    "is_public": "true",
                    "category": "Frutas" if i % 2 == 0 else "Verduras",
                },
                headers={"Authorization": f"Bearer {admin_token}"},
            )

        # Sin filtro — página 1 con 3 items
        response = self.client.get("/crops/published?page=1&page_size=3")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["items"]), 3)
        self.assertEqual(body["total"], 5)
        self.assertEqual(body["total_pages"], 2)

        # Filtrar por nombre
        response = self.client.get("/crops/published?name=Público 1")
        body = response.json()
        self.assertEqual(body["total"], 1)

        # Filtrar por categoría
        response = self.client.get("/crops/published?category=Frutas")
        body = response.json()
        self.assertGreaterEqual(body["total"], 2)

    def test_add_to_my_crops_creates_independent_copy(self):
        """Copiar cultivo del catálogo crea copia independiente."""
        admin_token = self._create_admin()

        # Admin crea cultivo público
        resp = self.client.post(
            "/crops/",
            data={"name": "Tomate Original", "is_public": "true"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        original_id = resp.json()["id"]

        # Usuario normal copia
        user_token = self._create_user("farmer")
        resp = self.client.post(
            f"/crops/{original_id}/add-to-my-crops",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        self.assertEqual(resp.status_code, 201)
        copy = resp.json()
        self.assertEqual(copy["name"], "Tomate Original")
        self.assertEqual(copy["copied_from_id"], original_id)
        self.assertFalse(copy["is_public"])
        self.assertIsNotNone(copy["owner_id"])

    def test_edit_copy_does_not_modify_original(self):
        """Editar copia no modifica el original."""
        admin_token = self._create_admin()

        resp = self.client.post(
            "/crops/",
            data={"name": "Original", "is_public": "true"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        original_id = resp.json()["id"]

        user_token = self._create_user("farmer2")
        resp = self.client.post(
            f"/crops/{original_id}/add-to-my-crops",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        copy_id = resp.json()["id"]

        # Editar copia
        self.client.put(
            f"/crops/{copy_id}",
            data={"name": "Copia Modificada"},
            headers={"Authorization": f"Bearer {user_token}"},
        )

        # Verificar original no cambió
        response = self.client.get(
            f"/crops/{original_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.json()["name"], "Original")

    def test_normal_user_cannot_edit_other_crop(self):
        """Usuario normal no puede editar cultivo ajeno."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")

        # owner_a crea cultivo
        resp = self.client.post(
            "/crops/",
            data={"name": "Cultivo de A"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        crop_id = resp.json()["id"]

        # attacker_b intenta editarlo
        response = self.client.put(
            f"/crops/{crop_id}",
            data={"name": "Robado"},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_copy_removes_it(self):
        """Eliminar copia la quita de mis cultivos."""
        admin_token = self._create_admin()

        resp = self.client.post(
            "/crops/",
            data={"name": "Público para copiar", "is_public": "true"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        original_id = resp.json()["id"]

        user_token = self._create_user("copier")
        resp = self.client.post(
            f"/crops/{original_id}/add-to-my-crops",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        copy_id = resp.json()["id"]

        # Eliminar copia
        response = self.client.delete(
            f"/crops/{copy_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que ya no está en mis cultivos
        response = self.client.get(
            "/crops/my",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        ids = [c["id"] for c in response.json()]
        self.assertNotIn(copy_id, ids)

    def test_delete_original_conserves_as_public(self):
        """Eliminar cultivo original lo conserva como público."""
        token = self._create_user("gardener")

        resp = self.client.post(
            "/crops/",
            data={"name": "Mi cultivo original"},
            headers={"Authorization": f"Bearer {token}"},
        )
        crop_id = resp.json()["id"]

        # Eliminar original
        response = self.client.delete(
            f"/crops/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Ahora debe aparecer en catálogo público
        response = self.client.get("/crops/published")
        body = response.json()
        ids = [c["id"] for c in body["items"]]
        self.assertIn(crop_id, ids)

        # Ya no tiene owner
        crop_in_catalog = next(c for c in body["items"] if c["id"] == crop_id)
        self.assertIsNone(crop_in_catalog["owner_id"])
        self.assertTrue(crop_in_catalog["is_public"])

    def test_admin_can_see_all_crops(self):
        """GET /crops/ con admin ve todos los cultivos."""
        token_a = self._create_user("user_x")
        token_b = self._create_user("user_y")

        self.client.post(
            "/crops/", data={"name": "Cultivo X"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.client.post(
            "/crops/", data={"name": "Cultivo Y"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        admin_token = self._create_admin("superadmin")
        response = self.client.get(
            "/crops/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_user_cannot_add_non_public_crop(self):
        """No se puede añadir un cultivo no publicado a mis cultivos."""
        token = self._create_user("owner")
        resp = self.client.post(
            "/crops/",
            data={"name": "Privado"},
            headers={"Authorization": f"Bearer {token}"},
        )
        crop_id = resp.json()["id"]

        other_token = self._create_user("other")
        response = self.client.post(
            f"/crops/{crop_id}/add-to-my-crops",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_get_user_crops_own(self):
        """GET /crops/user/{user_id} propio funciona."""
        token = self._create_user("myuser")
        self.client.post(
            "/crops/", data={"name": "Mi cultivo"},
            headers={"Authorization": f"Bearer {token}"},
        )
        response = self.client.get(
            "/crops/user/1",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_get_user_crops_other_forbidden(self):
        """Usuario normal no puede ver cultivos de otro usuario."""
        token_a = self._create_user("user_a")
        token_b = self._create_user("user_b")

        self.client.post(
            "/crops/", data={"name": "De A"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        response = self.client.get(
            "/crops/user/1",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_normal_user_crop_list_only_own(self):
        """GET /crops/ para usuario normal devuelve solo los suyos."""
        token_a = self._create_user("alice")
        token_b = self._create_user("bob")

        self.client.post(
            "/crops/", data={"name": "Alice crop"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.client.post(
            "/crops/", data={"name": "Bob crop"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        response = self.client.get(
            "/crops/",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Alice crop")


    # =====================================================================
    # Tests FASE 5: Calendario Agrícola por Fases
    # =====================================================================

    def _create_crop_for_user(self, token, name="Mi cultivo"):
        """Helper para crear un cultivo y devolver su ID."""
        resp = self.client.post(
            "/crops/",
            data={"name": name},
            headers={"Authorization": f"Bearer {token}"},
        )
        return resp.json()["id"]

    def _create_calendar(self, token, crop_id, **kwargs):
        """Helper para crear un calendario con fechas opcionales."""
        data = {"crop_id": crop_id}
        data.update(kwargs)
        return self.client.post(
            "/calendar/",
            json=data,
            headers={"Authorization": f"Bearer {token}"},
        )

    def _fill_dates(self, token, crop_id):
        """Rellena todas las fechas del calendario de un cultivo."""
        return self.client.put(
            f"/calendar/crop/{crop_id}",
            json={
                "planting_start": "2025-03-01",
                "planting_end": "2025-04-15",
                "transplant_start": "2025-04-16",
                "transplant_end": "2025-05-15",
                "harvest_start": "2025-06-01",
                "harvest_end": "2025-08-30",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    def test_create_calendar_for_own_crop(self):
        """Crear calendario para cultivo propio."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        response = self._create_calendar(token, crop_id)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["crop_id"], crop_id)
        self.assertEqual(data["status"], "draft")
        self.assertFalse(data["is_active"])
        self.assertEqual(data["current_phase_index"], 0)

    def test_create_calendar_without_token_fails(self):
        """Usuario sin token no puede crear calendario."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        response = self.client.post(
            "/calendar/",
            json={"crop_id": crop_id},
        )
        self.assertEqual(response.status_code, 401)

    def test_normal_user_cannot_create_calendar_for_other_crop(self):
        """Usuario normal no puede crear calendario para cultivo ajeno."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")
        crop_id = self._create_crop_for_user(token_a)
        response = self._create_calendar(token_b, crop_id)
        self.assertEqual(response.status_code, 403)

    def test_get_calendar_by_crop(self):
        """Obtener calendario por ID de cultivo."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)
        response = self.client.get(
            f"/calendar/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["crop_id"], crop_id)

    def test_update_calendar_by_crop(self):
        """Actualizar calendario con PUT /calendar/crop/{crop_id}."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)
        response = self._fill_dates(token, crop_id)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["planting_start"])
        self.assertIsNotNone(data["harvest_end"])

    def test_cannot_activate_incomplete_calendar(self):
        """No activar calendario incompleto."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)
        response = self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("faltan fechas", response.json()["detail"].lower())

    def test_activate_complete_calendar(self):
        """Activar calendario completo."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)
        self._fill_dates(token, crop_id)
        response = self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_active"])
        self.assertEqual(data["status"], "active")
        self.assertEqual(data["current_phase_index"], 0)

    def test_user_events_only_own(self):
        """GET /calendar/events devuelve solo eventos del usuario."""
        token_a = self._create_user("user_a")
        token_b = self._create_user("user_b")

        # Crear cultivos y calendarios completos para ambos
        crop_a = self._create_crop_for_user(token_a)
        self._create_calendar(token_a, crop_a)
        self._fill_dates(token_a, crop_a)
        self.client.post(
            f"/calendar/crop/{crop_a}/activate",
            headers={"Authorization": f"Bearer {token_a}"},
        )

        crop_b = self._create_crop_for_user(token_b)
        self._create_calendar(token_b, crop_b)
        self._fill_dates(token_b, crop_b)
        self.client.post(
            f"/calendar/crop/{crop_b}/activate",
            headers={"Authorization": f"Bearer {token_b}"},
        )

        # User A events
        response = self.client.get(
            "/calendar/events",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(response.status_code, 200)
        # Debe tener eventos (al menos algunos meses con quincenas)
        self.assertGreater(len(response.json()), 0)

        # Verificar que user_b no tiene eventos de user_a (son independientes)
        response_b = self.client.get(
            "/calendar/events",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertGreater(len(response_b.json()), 0)

    def test_calendar_events_returns_current_phase(self):
        """GET /calendar/{calendar_id}/events devuelve la fase actual."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)
        self._fill_dates(token, crop_id)
        self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Obtener el calendar_id
        cal_resp = self.client.get(
            f"/calendar/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        cal_id = cal_resp.json()["id"]

        response = self.client.get(
            f"/calendar/{cal_id}/events",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        events = response.json()
        self.assertGreater(len(events), 0)
        # Debe incluir eventos de siembra (phase_index=0) que es la fase actual
        self.assertTrue(any(e["phase_index"] == 0 for e in events))

    def test_events_ignore_year_by_month_fortnight(self):
        """Eventos ignoran el año y funcionan por mes/quincena."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)

        # Fechas que cruzan año: nov 2025 → feb 2026
        self.client.put(
            f"/calendar/crop/{crop_id}",
            json={
                "planting_start": "2025-11-01",
                "planting_end": "2026-02-15",
                "transplant_start": "2026-03-01",
                "transplant_end": "2026-04-30",
                "harvest_start": "2026-06-01",
                "harvest_end": "2026-09-15",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # Obtener calendar_id
        cal_resp = self.client.get(
            f"/calendar/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        cal_id = cal_resp.json()["id"]

        response = self.client.get(
            f"/calendar/{cal_id}/events",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        events = response.json()
        # Debe haber eventos de noviembre (mes 11), diciembre (12), enero (1), febrero (2)
        months = {e["month"] for e in events if e["phase_index"] == 0}
        # Al menos nov, dic, ene, feb deben estar representados
        self.assertTrue(
            {11, 12, 1, 2}.issubset(months),
            f"Esperaba meses 11,12,1,2 pero obtuve {months}",
        )

    def test_advance_from_planting_to_transplant(self):
        """Avanzar de Siembra a Trasplante."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)
        self._fill_dates(token, crop_id)
        self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.post(
            f"/calendar/crop/{crop_id}/advance",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_phase_index"], 1)

    def test_advance_from_transplant_to_harvest(self):
        """Avanzar de Trasplante a Cosecha."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)
        self._fill_dates(token, crop_id)
        self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Avanzar a Trasplante
        self.client.post(
            f"/calendar/crop/{crop_id}/advance",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Avanzar a Cosecha
        response = self.client.post(
            f"/calendar/crop/{crop_id}/advance",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["current_phase_index"], 2)

    def test_advance_from_harvest_completes_and_deactivates(self):
        """Avanzar desde Cosecha completa el calendario y lo desactiva."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)
        self._fill_dates(token, crop_id)
        self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Avanzar a Trasplante
        self.client.post(
            f"/calendar/crop/{crop_id}/advance",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Avanzar a Cosecha
        self.client.post(
            f"/calendar/crop/{crop_id}/advance",
            headers={"Authorization": f"Bearer {token}"},
        )
        # Avanzar desde Cosecha → completado
        response = self.client.post(
            f"/calendar/crop/{crop_id}/advance",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")
        self.assertFalse(data["is_active"])
        self.assertEqual(data["current_phase_index"], 2)

    def test_admin_can_manage_other_user_calendar(self):
        """Admin puede gestionar calendarios de otros usuarios."""
        user_token = self._create_user("regular_user")
        crop_id = self._create_crop_for_user(user_token)
        self._create_calendar(user_token, crop_id)

        admin_token = self._create_admin("super_admin")
        # Admin puede obtener calendario de otro usuario
        response = self.client.get(
            f"/calendar/crop/{crop_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)

        # Admin puede actualizar
        response = self._fill_dates(admin_token, crop_id)
        self.assertEqual(response.status_code, 200)

        # Admin puede activar
        response = self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_active"])

    def test_normal_user_cannot_edit_other_user_calendar(self):
        """Usuario normal no puede editar calendario de cultivo ajeno."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")
        crop_id = self._create_crop_for_user(token_a)
        self._create_calendar(token_a, crop_id)

        # Intentar editar como otro usuario
        response = self.client.put(
            f"/calendar/crop/{crop_id}",
            json={"planting_start": "2025-03-01"},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_calendar(self):
        """Eliminar calendario."""
        token = self._create_user()
        crop_id = self._create_crop_for_user(token)
        self._create_calendar(token, crop_id)

        # Obtener calendar_id
        cal_resp = self.client.get(
            f"/calendar/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        cal_id = cal_resp.json()["id"]

        response = self.client.delete(
            f"/calendar/{cal_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que ya no existe
        response = self.client.get(
            f"/calendar/{cal_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_list_calendars_admin_sees_all(self):
        """Admin ve todos los calendarios en GET /calendar/."""
        token_a = self._create_user("user_x")
        token_b = self._create_user("user_y")
        crop_a = self._create_crop_for_user(token_a)
        crop_b = self._create_crop_for_user(token_b)
        self._create_calendar(token_a, crop_a)
        self._create_calendar(token_b, crop_b)

        admin_token = self._create_admin("admin_see_all")
        response = self.client.get(
            "/calendar/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_list_calendars_user_sees_only_own(self):
        """Usuario normal ve solo sus calendarios en GET /calendar/."""
        token_a = self._create_user("user_x")
        token_b = self._create_user("user_y")
        crop_a = self._create_crop_for_user(token_a)
        crop_b = self._create_crop_for_user(token_b)
        self._create_calendar(token_a, crop_a)
        self._create_calendar(token_b, crop_b)

        response = self.client.get(
            "/calendar/",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    # =====================================================================
    # Tests FASE 6: Riego, Requisitos Ambientales y Tareas
    # =====================================================================

    def _create_crop_for_user_with_token(self, token, name="Test Crop"):
        """Helper que crea un cultivo y devuelve (token, crop_id)."""
        resp = self.client.post(
            "/crops/",
            data={"name": name},
            headers={"Authorization": f"Bearer {token}"},
        )
        return resp.json()["id"]

    # ─────────── Riego ───────────

    def test_create_irrigation_for_own_crop(self):
        """Crear riego para cultivo propio."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)
        # Eliminar el riego por defecto creado al crear el cultivo
        self.client.delete(f"/irrigation/1", headers={"Authorization": f"Bearer {token}"})
        response = self.client.post(
            "/irrigation/",
            json={
                "crop_id": crop_id,
                "frequency_days": 5,
                "water_needed_mm": 30.0,
                "irrigation_method": "aspersión",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["crop_id"], crop_id)
        self.assertEqual(data["frequency_days"], 5)
        self.assertEqual(data["water_needed_mm"], 30.0)
        self.assertEqual(data["irrigation_method"], "aspersión")

    def test_get_irrigation_by_crop(self):
        """Obtener riego por ID de cultivo."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)
        # El riego por defecto ya existe (id=1)
        response = self.client.get(
            f"/irrigation/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["crop_id"], crop_id)

    def test_normal_user_cannot_access_other_irrigation(self):
        """Usuario normal no puede acceder a riego de cultivo ajeno."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")
        crop_a = self._create_crop_for_user_with_token(token_a)

        # attacker_b intenta obtener riego del cultivo de owner_a
        response = self.client.get(
            f"/irrigation/crop/{crop_a}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_update_irrigation(self):
        """Actualizar riego."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)
        # Obtener ID del riego por defecto
        resp = self.client.get(
            f"/irrigation/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        irr_id = resp.json()["id"]

        response = self.client.put(
            f"/irrigation/{irr_id}",
            json={"frequency_days": 10, "water_needed_mm": 50.0},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["frequency_days"], 10)
        self.assertEqual(data["water_needed_mm"], 50.0)

    def test_normal_user_cannot_modify_other_irrigation(self):
        """Usuario normal no puede modificar riego de cultivo ajeno."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")
        crop_a = self._create_crop_for_user_with_token(token_a)

        response = self.client.put(
            f"/irrigation/1",
            json={"frequency_days": 99},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    # ─────────── Requisitos Ambientales ───────────

    def test_create_environmental_for_own_crop(self):
        """Crear requisitos ambientales para cultivo propio."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)
        # Eliminar el environmental por defecto
        self.client.delete(f"/environmental/1", headers={"Authorization": f"Bearer {token}"})
        response = self.client.post(
            "/environmental/",
            json={
                "crop_id": crop_id,
                "min_temperature": 5.0,
                "max_temperature": 40.0,
                "sunlight_hours": 8,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["crop_id"], crop_id)
        self.assertEqual(data["min_temperature"], 5.0)
        self.assertEqual(data["max_temperature"], 40.0)

    def test_get_environmental_by_crop(self):
        """Obtener ambiente por cultivo."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)
        response = self.client.get(
            f"/environmental/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["crop_id"], crop_id)

    def test_normal_user_cannot_access_other_environmental(self):
        """Usuario normal no puede acceder a ambiente de cultivo ajeno."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")
        crop_a = self._create_crop_for_user_with_token(token_a)

        response = self.client.get(
            f"/environmental/crop/{crop_a}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_update_environmental(self):
        """Actualizar requisitos ambientales."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)
        resp = self.client.get(
            f"/environmental/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        env_id = resp.json()["id"]

        response = self.client.put(
            f"/environmental/{env_id}",
            json={"min_temperature": 0.0, "max_temperature": 45.0},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["min_temperature"], 0.0)
        self.assertEqual(data["max_temperature"], 45.0)

    def test_normal_user_cannot_modify_other_environmental(self):
        """Usuario normal no puede modificar ambiente de cultivo ajeno."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")
        _ = self._create_crop_for_user_with_token(token_a)

        response = self.client.put(
            f"/environmental/1",
            json={"min_temperature": -10.0},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    # ─────────── Tareas ───────────

    def test_create_task_authenticated(self):
        """Crear tarea autenticado."""
        token = self._create_user()
        response = self.client.post(
            "/tasks/",
            json={"title": "Regar las plantas", "description": "Mañana temprano"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], "Regar las plantas")
        self.assertEqual(data["owner_id"], 1)
        self.assertEqual(data["status"], "pending")
        self.assertFalse(data["is_completed"])

    def test_create_task_without_token_fails(self):
        """Usuario sin token no puede crear tarea."""
        response = self.client.post(
            "/tasks/",
            json={"title": "Tarea maliciosa"},
        )
        self.assertEqual(response.status_code, 401)

    def test_list_tasks_returns_only_own(self):
        """GET /tasks/ devuelve solo tareas del usuario."""
        token_a = self._create_user("user_a")
        token_b = self._create_user("user_b")

        self.client.post(
            "/tasks/", json={"title": "Tarea de A"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.client.post(
            "/tasks/", json={"title": "Tarea de B"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        response = self.client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(response.status_code, 200)
        tasks = response.json()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Tarea de A")

    def test_admin_can_see_all_tasks(self):
        """Admin puede ver todas las tareas."""
        token_a = self._create_user("user_a")
        token_b = self._create_user("user_b")

        self.client.post(
            "/tasks/", json={"title": "Tarea de A"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.client.post(
            "/tasks/", json={"title": "Tarea de B"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        admin_token = self._create_admin("super_admin")
        response = self.client.get(
            "/tasks/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json()), 2)

    def test_assign_task_to_own_crop(self):
        """Asignar tarea a cultivo propio."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)

        # Crear tarea
        resp = self.client.post(
            "/tasks/", json={"title": "Mi tarea"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]

        # Asignar a cultivo
        response = self.client.post(
            "/tasks/assign",
            json={"task_id": task_id, "crop_id": crop_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["task_id"], task_id)
        self.assertEqual(data["crop_id"], crop_id)

    def test_normal_user_cannot_assign_task_to_other_crop(self):
        """Usuario normal no puede asignar tarea a cultivo ajeno."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")
        crop_a = self._create_crop_for_user_with_token(token_a)

        # attacker_b crea tarea
        resp = self.client.post(
            "/tasks/", json={"title": "Tarea ajena"},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        task_id = resp.json()["id"]

        # Intentar asignar a cultivo de owner_a
        response = self.client.post(
            "/tasks/assign",
            json={"task_id": task_id, "crop_id": crop_a},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_get_tasks_by_crop(self):
        """GET /tasks/crop/{crop_id} lista tareas del cultivo."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)

        # Crear tarea y asignarla
        resp = self.client.post(
            "/tasks/", json={"title": "Tarea del cultivo"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]

        self.client.post(
            "/tasks/assign",
            json={"task_id": task_id, "crop_id": crop_id},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.get(
            f"/tasks/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        tasks = response.json()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Tarea del cultivo")

    def test_get_task_crops(self):
        """GET /tasks/{task_id}/crops lista cultivos asociados."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)

        resp = self.client.post(
            "/tasks/", json={"title": "Tarea con cultivo"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]

        self.client.post(
            "/tasks/assign",
            json={"task_id": task_id, "crop_id": crop_id},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.get(
            f"/tasks/{task_id}/crops",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        crops = response.json()
        self.assertEqual(len(crops), 1)
        self.assertEqual(crops[0]["id"], crop_id)

    def test_patch_task_complete_and_reopen(self):
        """PATCH /tasks/{task_id} permite completar y reabrir tarea."""
        token = self._create_user()
        resp = self.client.post(
            "/tasks/", json={"title": "Tarea completable"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]
        self.assertFalse(resp.json()["is_completed"])

        # Completar
        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["is_completed"])
        self.assertEqual(response.json()["status"], "completed")

        # Reabrir
        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"status": "pending"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_completed"])
        self.assertEqual(response.json()["status"], "pending")

    def test_normal_user_cannot_edit_other_task(self):
        """Usuario normal no puede editar tarea ajena."""
        token_a = self._create_user("owner_a")
        token_b = self._create_user("attacker_b")

        resp = self.client.post(
            "/tasks/", json={"title": "Tarea de A"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        task_id = resp.json()["id"]

        # attacker_b intenta editar
        response = self.client.patch(
            f"/tasks/{task_id}",
            json={"title": "Hackeado"},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_task_removes_relations(self):
        """Eliminar tarea elimina relaciones TaskCrop."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)

        resp = self.client.post(
            "/tasks/", json={"title": "Tarea a eliminar"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]

        # Asignar a cultivo
        self.client.post(
            "/tasks/assign",
            json={"task_id": task_id, "crop_id": crop_id},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Eliminar tarea
        response = self.client.delete(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 204)

        # Verificar que la tarea ya no existe
        response = self.client.get(
            f"/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)

        # Verificar que las relaciones también se eliminaron
        tc_response = self.client.get(
            f"/tasks/crop/{crop_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(tc_response.status_code, 200)
        self.assertEqual(len(tc_response.json()), 0)


    # =====================================================================
    # Tests FASE 7: Dashboard y Panel Admin
    # =====================================================================

    def test_dashboard_summary_authenticated_user(self):
        """Usuario autenticado puede ver /dashboard/summary."""
        token = self._create_user()
        response = self.client.get(
            "/dashboard/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_personal_crops", data)
        self.assertIn("total_public_crops", data)
        self.assertIn("tasks_pending", data)
        self.assertIn("tasks_completed", data)
        self.assertIn("upcoming_tasks", data)
        self.assertIn("upcoming_calendar_events", data)
        self.assertIn("active_calendars", data)
        self.assertIn("completed_calendars", data)
        self.assertIn("irrigation_summary", data)
        self.assertIn("environmental_summary", data)

    def test_dashboard_summary_only_own_data(self):
        """Dashboard solo incluye datos del usuario autenticado."""
        token_a = self._create_user("user_a")
        token_b = self._create_user("user_b")

        # user_a crea cultivo y tarea
        resp = self.client.post(
            "/crops/", data={"name": "Crop A"},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        crop_a_id = resp.json()["id"]
        self.client.post(
            "/tasks/", json={"title": "Task A"},
            headers={"Authorization": f"Bearer {token_a}"},
        )

        # user_b crea cultivo y tarea
        resp = self.client.post(
            "/crops/", data={"name": "Crop B"},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        self.client.post(
            "/tasks/", json={"title": "Task B"},
            headers={"Authorization": f"Bearer {token_b}"},
        )

        # Dashboard de user_a
        response = self.client.get(
            "/dashboard/summary",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_personal_crops"], 1)
        self.assertEqual(data["tasks_pending"], 1)

        # Dashboard de user_b
        response = self.client.get(
            "/dashboard/summary",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        data = response.json()
        self.assertEqual(data["total_personal_crops"], 1)
        self.assertEqual(data["tasks_pending"], 1)

    def test_dashboard_summary_tasks_counts(self):
        """Dashboard cuenta tareas pending/completed correctamente."""
        token = self._create_user()

        # Crear 2 tareas pending, 1 completed
        self.client.post(
            "/tasks/", json={"title": "Pending 1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.client.post(
            "/tasks/", json={"title": "Pending 2"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = self.client.post(
            "/tasks/", json={"title": "Completable"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]
        self.client.patch(
            f"/tasks/{task_id}",
            json={"status": "completed"},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.get(
            "/dashboard/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()
        self.assertEqual(data["tasks_pending"], 2)
        self.assertEqual(data["tasks_completed"], 1)

    def test_dashboard_summary_calendar_and_phase(self):
        """Dashboard incluye calendarios activos y fase actual."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)

        # Crear calendario completo
        self.client.post(
            "/calendar/", json={"crop_id": crop_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.client.put(
            f"/calendar/crop/{crop_id}",
            json={
                "planting_start": "2025-03-01",
                "planting_end": "2025-04-15",
                "transplant_start": "2025-04-16",
                "transplant_end": "2025-05-15",
                "harvest_start": "2025-06-01",
                "harvest_end": "2025-08-30",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.get(
            "/dashboard/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()
        self.assertEqual(data["active_calendars"], 1)
        self.assertEqual(data["completed_calendars"], 0)
        self.assertGreater(len(data["upcoming_calendar_events"]), 0)
        event = data["upcoming_calendar_events"][0]
        self.assertIn("phase_index", event)
        self.assertIn("phase_name", event)
        self.assertIn("crop_name", event)

    def test_dashboard_summary_irrigation_and_environmental(self):
        """Dashboard incluye resumen de riego y ambiente."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)

        response = self.client.get(
            "/dashboard/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = response.json()
        # Al crear cultivo se crean automáticamente riego y ambiente por defecto
        self.assertGreaterEqual(len(data["irrigation_summary"]), 1)
        self.assertGreaterEqual(len(data["environmental_summary"]), 1)
        irr = data["irrigation_summary"][0]
        self.assertIn("crop_id", irr)
        self.assertIn("crop_name", irr)
        env = data["environmental_summary"][0]
        self.assertIn("crop_id", env)
        self.assertIn("crop_name", env)

    def test_dashboard_without_token_fails(self):
        """Usuario sin token no puede acceder a dashboard."""
        response = self.client.get("/dashboard/summary")
        self.assertEqual(response.status_code, 401)
        response = self.client.get("/dashboard/crops")
        self.assertEqual(response.status_code, 401)

    def test_dashboard_crops_endpoint(self):
        """GET /dashboard/crops devuelve cultivos del usuario."""
        token = self._create_user()
        self._create_crop_for_user_with_token(token, "My Crop")

        response = self.client.get(
            "/dashboard/crops",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        crops = response.json()
        self.assertEqual(len(crops), 1)
        self.assertEqual(crops[0]["name"], "My Crop")

    def test_dashboard_tasks_endpoint(self):
        """GET /dashboard/tasks devuelve tareas del usuario."""
        token = self._create_user()
        self.client.post(
            "/tasks/", json={"title": "Dashboard Task"},
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.get(
            "/dashboard/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        tasks = response.json()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Dashboard Task")

    def test_dashboard_calendar_endpoint(self):
        """GET /dashboard/calendar devuelve eventos."""
        token = self._create_user()
        crop_id = self._create_crop_for_user_with_token(token)
        self.client.post(
            "/calendar/", json={"crop_id": crop_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.client.put(
            f"/calendar/crop/{crop_id}",
            json={
                "planting_start": "2025-03-01",
                "planting_end": "2025-04-15",
                "transplant_start": "2025-04-16",
                "transplant_end": "2025-05-15",
                "harvest_start": "2025-06-01",
                "harvest_end": "2025-08-30",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        self.client.post(
            f"/calendar/crop/{crop_id}/activate",
            headers={"Authorization": f"Bearer {token}"},
        )

        response = self.client.get(
            "/dashboard/calendar",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        events = response.json()
        self.assertGreater(len(events), 0)

    def test_dashboard_irrigation_endpoint(self):
        """GET /dashboard/irrigation devuelve resumen de riego."""
        token = self._create_user()
        self._create_crop_for_user_with_token(token)

        response = self.client.get(
            "/dashboard/irrigation",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)

    def test_dashboard_environmental_endpoint(self):
        """GET /dashboard/environmental devuelve resumen ambiental."""
        token = self._create_user()
        self._create_crop_for_user_with_token(token)

        response = self.client.get(
            "/dashboard/environmental",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)

    # ───── Admin Summary ─────

    def test_admin_can_access_admin_summary(self):
        """Admin puede acceder a /admin/summary."""
        token = self._create_admin()
        response = self.client.get(
            "/admin/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_users", data)
        self.assertIn("total_crops", data)
        self.assertIn("total_public_crops", data)
        self.assertIn("total_tasks", data)
        self.assertIn("tasks_pending", data)
        self.assertIn("tasks_completed", data)
        self.assertIn("total_active_calendars", data)
        self.assertIn("total_completed_calendars", data)

    def test_normal_user_cannot_access_admin_summary(self):
        """Usuario normal no puede acceder a /admin/summary."""
        token = self._create_user()
        response = self.client.get(
            "/admin/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 403)

    # ───── Admin Users ─────

    def test_admin_list_users_no_password(self):
        """Admin puede listar usuarios sin password/hash."""
        self.client.post(
            "/users/",
            json={
                "email": "user1@test.com",
                "username": "user1",
                "password": "pass123",
            },
        )
        admin_token = self._create_admin()
        response = self.client.get(
            "/admin/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertGreaterEqual(len(users), 1)
        for user in users:
            self.assertNotIn("password", user)
            self.assertNotIn("hashed_password", user)
            self.assertIn("id", user)
            self.assertIn("email", user)
            self.assertIn("username", user)

    def test_admin_get_user_by_id_no_password(self):
        """Admin puede ver usuario por id sin password/hash."""
        self.client.post(
            "/users/",
            json={
                "email": "target@test.com",
                "username": "target",
                "password": "pass123",
            },
        )
        admin_token = self._create_admin()
        response = self.client.get(
            "/admin/users/1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        user = response.json()
        self.assertEqual(user["username"], "target")
        self.assertNotIn("password", user)
        self.assertNotIn("hashed_password", user)

    def test_admin_update_user(self):
        """Admin puede actualizar usuario."""
        self.client.post(
            "/users/",
            json={
                "email": "update@test.com",
                "username": "update_me",
                "password": "pass123",
            },
        )
        admin_token = self._create_admin()
        response = self.client.patch(
            "/admin/users/1",
            json={"full_name": "Updated Name", "role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        user = response.json()
        self.assertEqual(user["full_name"], "Updated Name")
        self.assertEqual(user["role"], "admin")
        self.assertNotIn("password", user)
        self.assertNotIn("hashed_password", user)

    def test_admin_update_user_deactivate(self):
        """Admin puede desactivar usuario via is_active."""
        self.client.post(
            "/users/",
            json={
                "email": "deact@test.com",
                "username": "deactivate_me",
                "password": "pass123",
            },
        )
        admin_token = self._create_admin()
        response = self.client.patch(
            "/admin/users/1",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["is_active"])

    def test_admin_delete_user(self):
        """Admin puede eliminar usuario."""
        self.client.post(
            "/users/",
            json={
                "email": "delete_me@test.com",
                "username": "delete_me",
                "password": "pass123",
            },
        )
        admin_token = self._create_admin()
        response = self.client.delete(
            "/admin/users/1",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 204)

    def test_normal_user_cannot_admin_users(self):
        """Usuario normal no puede usar endpoints admin de usuarios."""
        user_token = self._create_user()
        endpoints = [
            ("GET", "/admin/users"),
            ("GET", "/admin/users/1"),
            ("PATCH", "/admin/users/1"),
            ("DELETE", "/admin/users/1"),
        ]
        for method, path in endpoints:
            if method == "GET":
                response = self.client.get(
                    path, headers={"Authorization": f"Bearer {user_token}"},
                )
            elif method == "PATCH":
                response = self.client.patch(
                    path, json={"full_name": "x"},
                    headers={"Authorization": f"Bearer {user_token}"},
                )
            elif method == "DELETE":
                response = self.client.delete(
                    path, headers={"Authorization": f"Bearer {user_token}"},
                )
            self.assertEqual(response.status_code, 403, f"{method} {path} should return 403")

    # ───── Admin Crops ─────

    def test_admin_list_crops(self):
        """Admin puede listar cultivos."""
        token = self._create_user()
        self.client.post(
            "/crops/", data={"name": "Test Crop"},
            headers={"Authorization": f"Bearer {token}"},
        )
        admin_token = self._create_admin()
        response = self.client.get(
            "/admin/crops",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        crops = response.json()
        self.assertGreaterEqual(len(crops), 1)

    def test_admin_get_crop_by_id(self):
        """Admin puede ver cultivo por id."""
        token = self._create_user()
        resp = self.client.post(
            "/crops/", data={"name": "Specific Crop"},
            headers={"Authorization": f"Bearer {token}"},
        )
        crop_id = resp.json()["id"]
        admin_token = self._create_admin()
        response = self.client.get(
            f"/admin/crops/{crop_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Specific Crop")

    def test_admin_update_crop(self):
        """Admin puede actualizar cultivo."""
        token = self._create_user()
        resp = self.client.post(
            "/crops/", data={"name": "Original Name"},
            headers={"Authorization": f"Bearer {token}"},
        )
        crop_id = resp.json()["id"]
        admin_token = self._create_admin()
        response = self.client.patch(
            f"/admin/crops/{crop_id}",
            json={"name": "Updated by Admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Updated by Admin")

    def test_admin_delete_crop(self):
        """Admin puede eliminar cultivo."""
        token = self._create_user()
        resp = self.client.post(
            "/crops/", data={"name": "Delete Me"},
            headers={"Authorization": f"Bearer {token}"},
        )
        crop_id = resp.json()["id"]
        admin_token = self._create_admin()
        response = self.client.delete(
            f"/admin/crops/{crop_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 204)

    def test_normal_user_cannot_admin_crops(self):
        """Usuario normal no puede usar endpoints admin de cultivos."""
        user_token = self._create_user()
        for method, path in [
            ("GET", "/admin/crops"),
            ("GET", "/admin/crops/1"),
            ("PATCH", "/admin/crops/1"),
            ("DELETE", "/admin/crops/1"),
        ]:
            if method == "GET":
                response = self.client.get(
                    path, headers={"Authorization": f"Bearer {user_token}"},
                )
            elif method == "PATCH":
                response = self.client.patch(
                    path, json={"name": "x"},
                    headers={"Authorization": f"Bearer {user_token}"},
                )
            elif method == "DELETE":
                response = self.client.delete(
                    path, headers={"Authorization": f"Bearer {user_token}"},
                )
            self.assertEqual(response.status_code, 403, f"{method} {path} should return 403")

    # ───── Admin Tasks ─────

    def test_admin_list_tasks(self):
        """Admin puede listar tareas."""
        token = self._create_user()
        self.client.post(
            "/tasks/", json={"title": "Admin Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        admin_token = self._create_admin()
        response = self.client.get(
            "/admin/tasks",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        tasks = response.json()
        self.assertGreaterEqual(len(tasks), 1)

    def test_admin_get_task_by_id(self):
        """Admin puede ver tarea por id."""
        token = self._create_user()
        resp = self.client.post(
            "/tasks/", json={"title": "Specific Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]
        admin_token = self._create_admin()
        response = self.client.get(
            f"/admin/tasks/{task_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Specific Task")

    def test_admin_update_task(self):
        """Admin puede actualizar tarea."""
        token = self._create_user()
        resp = self.client.post(
            "/tasks/", json={"title": "Old Title"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]
        admin_token = self._create_admin()
        response = self.client.patch(
            f"/admin/tasks/{task_id}",
            json={"title": "Updated by Admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Updated by Admin")

    def test_admin_delete_task(self):
        """Admin puede eliminar tarea."""
        token = self._create_user()
        resp = self.client.post(
            "/tasks/", json={"title": "Delete Task"},
            headers={"Authorization": f"Bearer {token}"},
        )
        task_id = resp.json()["id"]
        admin_token = self._create_admin()
        response = self.client.delete(
            f"/admin/tasks/{task_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 204)

    def test_admin_get_nonexistent_task_404(self):
        """GET /admin/tasks/{id} con ID inexistente da 404."""
        admin_token = self._create_admin()
        response = self.client.get(
            "/admin/tasks/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_admin_get_nonexistent_user_404(self):
        """GET /admin/users/{id} con ID inexistente da 404."""
        admin_token = self._create_admin()
        response = self.client.get(
            "/admin/users/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_admin_get_nonexistent_crop_404(self):
        """GET /admin/crops/{id} con ID inexistente da 404."""
        admin_token = self._create_admin()
        response = self.client.get(
            "/admin/crops/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_normal_user_cannot_admin_tasks(self):
        """Usuario normal no puede usar endpoints admin de tareas."""
        user_token = self._create_user()
        for method, path in [
            ("GET", "/admin/tasks"),
            ("GET", "/admin/tasks/1"),
            ("PATCH", "/admin/tasks/1"),
            ("DELETE", "/admin/tasks/1"),
        ]:
            if method == "GET":
                response = self.client.get(
                    path, headers={"Authorization": f"Bearer {user_token}"},
                )
            elif method == "PATCH":
                response = self.client.patch(
                    path, json={"title": "x"},
                    headers={"Authorization": f"Bearer {user_token}"},
                )
            elif method == "DELETE":
                response = self.client.delete(
                    path, headers={"Authorization": f"Bearer {user_token}"},
                )
            self.assertEqual(response.status_code, 403, f"{method} {path} should return 403")


if __name__ == "__main__":
    unittest.main()
