"""
Tests para FASE 10: Seed Demo

Valida que el script de seed crea los datos correctos y es idempotente.
"""
import unittest
import sys
import os
from datetime import date, timedelta

# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.crop import Crop
from app.models.task import Task, TaskStatus
from app.models.planting_calendar import PlantingCalendar
from app.models.irrigation_attributes import IrrigationAttributes
from app.models.environmental_requirements import EnvironmentalRequirements
from app.services.auth_service import verify_password, hash_password
from app.services.user_service import create_user, get_user_by_email

# Importar funciones del seed
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
from seed_demo import (
    create_admin_user,
    create_demo_user,
    create_demo_crops,
    create_demo_calendars,
    create_demo_tasks,
)


class TestSeedDemo(unittest.TestCase):
    """Suite de tests para validar el seed de FASE 10."""

    @classmethod
    def setUpClass(cls):
        """Crear tablas antes de los tests."""
        Base.metadata.create_all(bind=engine)

    def setUp(self):
        """Limpiar BD antes de cada test."""
        self.db = SessionLocal()
        # Limpiar todas las tablas
        for table in reversed(Base.metadata.sorted_tables):
            self.db.execute(table.delete())
        self.db.commit()

    def tearDown(self):
        """Cerrar sesión después de cada test."""
        self.db.close()

    # ==================== TEST: ADMIN USER ====================

    def test_seed_creates_admin_user(self):
        """TEST: Seed crea usuario admin."""
        admin = create_admin_user(self.db)
        
        self.assertIsNotNone(admin)
        self.assertEqual(admin.email, "admin@test.com")
        self.assertEqual(admin.name, "admin")
        self.assertEqual(admin.role, UserRole.ADMIN)
        self.assertTrue(admin.is_active)

    def test_admin_password_hashed(self):
        """TEST: Contraseña admin está hasheada."""
        admin = create_admin_user(self.db)
        
        # Verificar que la contraseña NO es plaintext
        self.assertNotEqual(admin.password_hash, "admin123")
        
        # Verificar que verify_password funciona
        self.assertTrue(verify_password("admin123", admin.password_hash))
        self.assertFalse(verify_password("wrongpassword", admin.password_hash))

    def test_admin_can_login(self):
        """TEST: Admin puede login con credenciales correctas."""
        admin = create_admin_user(self.db)
        
        # Simular login
        user = self.db.query(User).filter(User.email == "admin@test.com").first()
        self.assertIsNotNone(user)
        self.assertTrue(verify_password("admin123", user.password_hash))

    # ==================== TEST: NORMAL USER ====================

    def test_seed_creates_demo_user(self):
        """TEST: Seed crea usuario demo."""
        user = create_demo_user(self.db)
        
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "user@test.com")
        self.assertEqual(user.name, "Demo User")
        self.assertEqual(user.role, UserRole.USER)
        self.assertTrue(user.is_active)

    def test_demo_user_password_hashed(self):
        """TEST: Contraseña demo user está hasheada."""
        user = create_demo_user(self.db)
        
        # Verificar que la contraseña NO es plaintext
        self.assertNotEqual(user.password_hash, "user123")
        
        # Verificar que verify_password funciona
        self.assertTrue(verify_password("user123", user.password_hash))
        self.assertFalse(verify_password("wrongpassword", user.password_hash))

    def test_demo_user_can_login(self):
        """TEST: Usuario demo puede login con credenciales correctas."""
        user = create_demo_user(self.db)
        
        # Simular login
        fetched_user = self.db.query(User).filter(User.email == "user@test.com").first()
        self.assertIsNotNone(fetched_user)
        self.assertTrue(verify_password("user123", fetched_user.password_hash))

    # ==================== TEST: PUBLIC CROPS ====================

    def test_seed_creates_5_public_crops(self):
        """TEST: Seed crea al menos 5 cultivos públicos."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        # Filtrar solo cultivos públicos
        public_crops = [c for c in crops if c.is_public]
        
        self.assertGreaterEqual(len(public_crops), 5)

    def test_public_crops_have_correct_names(self):
        """TEST: Cultivos públicos tienen nombres esperados."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        # Filtrar cultivos públicos
        public_crops = {c.name for c in crops if c.is_public}
        
        expected_names = {"Tomate", "Lechuga", "Zanahoria", "Pimiento", "Fresa"}
        self.assertEqual(public_crops, expected_names)

    def test_public_crops_have_no_owner(self):
        """TEST: Cultivos públicos no tienen dueño."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        for crop in crops:
            if crop.is_public:
                self.assertIsNone(crop.owner_id)

    def test_public_crops_have_irrigation_attributes(self):
        """TEST: Cultivos públicos tienen atributos de riego."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        public_crops = [c for c in crops if c.is_public]
        for crop in public_crops:
            irrigation = self.db.query(IrrigationAttributes).filter(
                IrrigationAttributes.crop_id == crop.id
            ).first()
            self.assertIsNotNone(irrigation)
            self.assertIsNotNone(irrigation.water_frequency_days)
            self.assertIsNotNone(irrigation.water_amount_mm)

    def test_public_crops_have_environmental_requirements(self):
        """TEST: Cultivos públicos tienen requisitos ambientales."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        public_crops = [c for c in crops if c.is_public]
        for crop in public_crops:
            env_req = self.db.query(EnvironmentalRequirements).filter(
                EnvironmentalRequirements.crop_id == crop.id
            ).first()
            self.assertIsNotNone(env_req)
            self.assertIsNotNone(env_req.min_temperature_celsius)
            self.assertIsNotNone(env_req.max_temperature_celsius)

    # ==================== TEST: PRIVATE CROPS ====================

    def test_seed_creates_2_personal_crops_for_user(self):
        """TEST: Seed crea 2 cultivos personales para usuario demo."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        # Filtrar cultivos privados del usuario
        private_crops = [c for c in crops if not c.is_public and c.owner_id == demo_user.id]
        
        self.assertEqual(len(private_crops), 2)

    def test_personal_crops_have_correct_names(self):
        """TEST: Cultivos personales se llaman Mi Tomate y Mi Lechuga."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        # Filtrar cultivos privados
        private_crops = {c.name for c in crops if not c.is_public and c.owner_id == demo_user.id}
        
        expected_names = {"Mi Tomate", "Mi Lechuga"}
        self.assertEqual(private_crops, expected_names)

    def test_personal_crops_belong_to_demo_user(self):
        """TEST: Cultivos personales pertenecen al usuario demo."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        for crop in crops:
            if not crop.is_public:
                self.assertEqual(crop.owner_id, demo_user.id)

    # ==================== TEST: CALENDARS ====================

    def test_seed_creates_calendars(self):
        """TEST: Seed crea calendarios de siembra."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        calendars = create_demo_calendars(self.db, crops)
        
        self.assertGreater(len(calendars), 0)

    def test_calendars_have_date_ranges(self):
        """TEST: Calendarios tienen rangos de fechas."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        calendars = create_demo_calendars(self.db, crops)
        
        for calendar in calendars:
            self.assertIsNotNone(calendar.planting_start)
            self.assertIsNotNone(calendar.planting_end)
            self.assertIsNotNone(calendar.harvest_start)
            self.assertIsNotNone(calendar.harvest_end)

    # ==================== TEST: TASKS ====================

    def test_seed_creates_demo_tasks(self):
        """TEST: Seed crea tareas para usuario demo."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        tasks = create_demo_tasks(self.db, demo_user)
        
        self.assertGreater(len(tasks), 0)

    def test_tasks_belong_to_demo_user(self):
        """TEST: Tareas pertenecen al usuario demo."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        tasks = create_demo_tasks(self.db, demo_user)
        
        for task in tasks:
            self.assertEqual(task.owner_id, demo_user.id)

    def test_tasks_have_pending_and_completed(self):
        """TEST: Existen tareas pending y completed."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        tasks = create_demo_tasks(self.db, demo_user)
        
        statuses = {t.status for t in tasks}
        self.assertIn(TaskStatus.PENDING, statuses)
        self.assertIn(TaskStatus.COMPLETED, statuses)

    # ==================== TEST: IDEMPOTENCY ====================

    def test_seed_is_idempotent_users(self):
        """TEST: Segunda ejecución no duplica usuarios."""
        # Primera ejecución
        admin1 = create_admin_user(self.db)
        user1 = create_demo_user(self.db)
        
        user_count_after_first = self.db.query(User).count()
        
        # Segunda ejecución
        admin2 = create_admin_user(self.db)
        user2 = create_demo_user(self.db)
        
        user_count_after_second = self.db.query(User).count()
        
        # Verificar que no se duplicaron
        self.assertEqual(user_count_after_first, user_count_after_second)
        self.assertEqual(admin1.id, admin2.id)
        self.assertEqual(user1.id, user2.id)

    def test_seed_is_idempotent_crops(self):
        """TEST: Segunda ejecución no duplica cultivos."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        
        # Primera ejecución
        crops1 = create_demo_crops(self.db, owner=demo_user)
        crop_count_after_first = self.db.query(Crop).count()
        
        # Segunda ejecución
        crops2 = create_demo_crops(self.db, owner=demo_user)
        crop_count_after_second = self.db.query(Crop).count()
        
        # Verificar que no se duplicaron
        self.assertEqual(crop_count_after_first, crop_count_after_second)
        self.assertEqual(len(crops1), len(crops2))

    def test_seed_is_idempotent_tasks(self):
        """TEST: Segunda ejecución no duplica tareas."""
        admin = create_admin_user(self.db)
        demo_user = create_demo_user(self.db)
        crops = create_demo_crops(self.db, owner=demo_user)
        
        # Primera ejecución
        tasks1 = create_demo_tasks(self.db, demo_user)
        task_count_after_first = self.db.query(Task).count()
        
        # Segunda ejecución
        tasks2 = create_demo_tasks(self.db, demo_user)
        task_count_after_second = self.db.query(Task).count()
        
        # Verificar que no se duplicaron
        self.assertEqual(task_count_after_first, task_count_after_second)
        self.assertEqual(len(tasks1), len(tasks2))

    def test_complete_idempotent_workflow(self):
        """TEST: Workflow completo es idempotente."""
        # Primera ejecución completa
        admin1 = create_admin_user(self.db)
        user1 = create_demo_user(self.db)
        crops1 = create_demo_crops(self.db, owner=user1)
        calendars1 = create_demo_calendars(self.db, crops1)
        tasks1 = create_demo_tasks(self.db, user1)
        
        counts_first = {
            'users': self.db.query(User).count(),
            'crops': self.db.query(Crop).count(),
            'calendars': self.db.query(PlantingCalendar).count(),
            'tasks': self.db.query(Task).count(),
        }
        
        # Segunda ejecución completa
        admin2 = create_admin_user(self.db)
        user2 = create_demo_user(self.db)
        crops2 = create_demo_crops(self.db, owner=user2)
        calendars2 = create_demo_calendars(self.db, crops2)
        tasks2 = create_demo_tasks(self.db, user2)
        
        counts_second = {
            'users': self.db.query(User).count(),
            'crops': self.db.query(Crop).count(),
            'calendars': self.db.query(PlantingCalendar).count(),
            'tasks': self.db.query(Task).count(),
        }
        
        # Todos los conteos deben ser iguales
        self.assertEqual(counts_first, counts_second)


if __name__ == '__main__':
    unittest.main()
