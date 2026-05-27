"""
Tests para el script de seed de desarrollo/demo de AgroManager.

Verifica que seed_demo:
- Crea usuarios admin y normal
- Crea cultivos públicos de catálogo
- Es idempotente (no duplica datos al ejecutarse dos veces)
- Las contraseñas quedan hasheadas
- Los usuarios pueden iniciar sesión tras el seed
- El catálogo público devuelve datos tras seed

Ejecutar con: python -m unittest discover -s tests -p "test*.py" -v
"""

import sys
import os

# Asegurar que el directorio raíz del proyecto está en sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.auth import hash_password, verify_password
from app.models.user import User
from app.models.crop import Crop
from app.models.task import Task
from app.models.planting_calendar import PlantingCalendar

# Usar base de datos en memoria para aislamiento
TEST_DATABASE_URL = "sqlite:///./test_seed_agromanager.db"
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


class TestSeedDemo(unittest.TestCase):
    """Tests para el script de seed de desarrollo."""

    @classmethod
    def setUpClass(cls):
        """Crea las tablas e instala dependency_overrides una vez antes de todos los tests."""
        Base.metadata.create_all(bind=test_engine)
        app.dependency_overrides[get_db] = override_get_db

    @classmethod
    def tearDownClass(cls):
        """Limpia dependency_overrides, elimina tablas y archivo de BD de test."""
        # Limpiar dependency_overrides para no contaminar otros tests
        if get_db in app.dependency_overrides:
            del app.dependency_overrides[get_db]
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()
        db_path = os.path.join(PROJECT_ROOT, "test_seed_agromanager.db")
        for suffix in ("", "-wal", "-shm"):
            path = db_path + suffix
            try:
                if os.path.exists(path):
                    os.remove(path)
            except PermissionError:
                pass

    def setUp(self):
        """Limpia los datos antes de cada test."""
        Base.metadata.drop_all(bind=test_engine)
        Base.metadata.create_all(bind=test_engine)
        self.client = TestClient(app)
        # Importar seed_demo
        from scripts.seed_demo import seed_demo as run_seed
        self.run_seed = run_seed

    def _get_db_session(self):
        """Obtiene una sesión de BD de test."""
        return TestSessionLocal()

    def test_seed_creates_admin(self):
        """seed_demo crea usuario admin."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
            admin = db.query(User).filter(User.email == "admin@test.com").first()
            self.assertIsNotNone(admin)
            self.assertEqual(admin.username, "admin")
            self.assertEqual(admin.role, "admin")
            self.assertTrue(admin.is_active)
        finally:
            db.close()

    def test_seed_creates_normal_user(self):
        """seed_demo crea usuario normal."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
            user = db.query(User).filter(User.email == "user@test.com").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "user")
            self.assertEqual(user.role, "user")
            self.assertTrue(user.is_active)
        finally:
            db.close()

    def test_seed_creates_public_crops(self):
        """seed_demo crea al menos 5 cultivos públicos."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
            public_crops = db.query(Crop).filter(Crop.is_public == True).all()
            self.assertGreaterEqual(len(public_crops), 5)
            names = [c.name for c in public_crops]
            for expected in ("Tomate", "Lechuga", "Zanahoria", "Pimiento", "Fresa"):
                self.assertIn(expected, names)
        finally:
            db.close()

    def test_seed_is_idempotent(self):
        """Ejecutar seed dos veces no duplica usuarios ni cultivos."""
        db = self._get_db_session()
        try:
            # Primera ejecución
            summary1 = self.run_seed(db)
            # Segunda ejecución
            summary2 = self.run_seed(db)

            # Usuarios: la segunda vez deben ser "existentes", no "creados"
            self.assertEqual(summary2["users_created"], 0,
                             "No deberían crearse nuevos usuarios en segunda ejecución")
            self.assertGreater(summary2["users_existing"], 0)

            # Cultivos: no deben duplicarse
            self.assertEqual(summary2["crops_created"], 0,
                             "No deberían crearse nuevos cultivos en segunda ejecución")

            # Tareas: no deben duplicarse
            self.assertEqual(summary2["tasks_created"], 0,
                             "No deberían crearse nuevas tareas en segunda ejecución")

            # Verificar que solo hay 1 admin y 1 user
            admins = db.query(User).filter(User.email == "admin@test.com").count()
            self.assertEqual(admins, 1)
            users = db.query(User).filter(User.email == "user@test.com").count()
            self.assertEqual(users, 1)

            # Verificar que los cultivos públicos no se duplicaron
            tomates = db.query(Crop).filter(
                Crop.name == "Tomate", Crop.is_public == True
            ).count()
            self.assertEqual(tomates, 1)
        finally:
            db.close()

    def test_passwords_are_hashed(self):
        """Las contraseñas guardadas deben ser hashes bcrypt."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
            admin = db.query(User).filter(User.email == "admin@test.com").first()
            self.assertIsNotNone(admin)
            # Verificar que es un hash bcrypt (empieza con $2b$ o $2a$)
            self.assertTrue(
                admin.hashed_password.startswith("$2"),
                f"El hash debería empezar con $2 pero es: {admin.hashed_password[:10]}..."
            )
            # Verificar que verify_password funciona
            self.assertTrue(
                verify_password("admin123", admin.hashed_password)
            )
        finally:
            db.close()

    def test_admin_can_login_after_seed(self):
        """El admin puede iniciar sesión tras ejecutar seed."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
        finally:
            db.close()

        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

    def test_normal_user_can_login_after_seed(self):
        """El usuario normal puede iniciar sesión tras ejecutar seed."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
        finally:
            db.close()

        response = self.client.post(
            "/auth/login",
            json={"username": "user", "password": "user123"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

    def test_public_catalog_returns_data_after_seed(self):
        """El endpoint de catálogo público devuelve datos tras seed."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
        finally:
            db.close()

        response = self.client.get("/crops/published")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertGreaterEqual(data["total"], 5)

    def test_seed_does_not_duplicate_on_second_run(self):
        """Verificación extra: segunda ejecución via API no rompe nada."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
        finally:
            db.close()

        # Login como admin
        login_resp = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"},
        )
        token = login_resp.json()["access_token"]

        # Verificar que el catálogo público funciona
        response = self.client.get("/crops/published")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["total"], 5)

        # Ver dashboard de user (no admin, para evitar filtro owner_id)
        login_user = self.client.post(
            "/auth/login",
            json={"username": "user", "password": "user123"},
        )
        user_token = login_user.json()["access_token"]
        response = self.client.get(
            "/dashboard/summary",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # user tiene cultivos personales
        self.assertGreaterEqual(data["total_personal_crops"], 2)
        # user tiene tareas
        self.assertGreaterEqual(data["tasks_pending"], 2)
        self.assertGreaterEqual(data["tasks_completed"], 2)

    def test_seed_creates_personal_crops(self):
        """seed_demo crea cultivos personales para user."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
            user = db.query(User).filter(User.email == "user@test.com").first()
            personal_crops = db.query(Crop).filter(
                Crop.owner_id == user.id,
                Crop.is_public == False,
            ).all()
            self.assertGreaterEqual(len(personal_crops), 2)
            names = [c.name for c in personal_crops]
            self.assertIn("Mi Tomate", names)
            self.assertIn("Mi Lechuga", names)
        finally:
            db.close()

    def test_seed_creates_tasks(self):
        """seed_demo crea al menos 4 tareas."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
            user = db.query(User).filter(User.email == "user@test.com").first()
            tasks = db.query(Task).filter(Task.owner_id == user.id).all()
            self.assertGreaterEqual(len(tasks), 4)
        finally:
            db.close()

    def test_seed_has_pending_and_completed_tasks(self):
        """Las tareas del seed incluyen pending y completed."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
            user = db.query(User).filter(User.email == "user@test.com").first()
            pending = db.query(Task).filter(
                Task.owner_id == user.id, Task.status == "pending"
            ).count()
            completed = db.query(Task).filter(
                Task.owner_id == user.id, Task.status == "completed"
            ).count()
            self.assertGreaterEqual(pending, 2)
            self.assertGreaterEqual(completed, 2)
        finally:
            db.close()

    def test_wrong_password_after_seed(self):
        """Contraseña incorrecta debe fallar tras seed."""
        db = self._get_db_session()
        try:
            self.run_seed(db)
        finally:
            db.close()

        response = self.client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrongpass"},
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()