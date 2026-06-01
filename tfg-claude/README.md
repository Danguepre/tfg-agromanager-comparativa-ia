# AgroManager - Implementación Completa

**Aplicación web full-stack** para gestión de cultivos personales, catálogo público de cultivos, tareas agrícolas y calendarios de siembra.

**Estado:** ✅ **FASE 11 - CIERRE TÉCNICO COMPLETADO**

**Stack Tecnológico:**
- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React 18 + Vite 5
- **Autenticación:** JWT + bcrypt
- **Testing:** Python unittest + React testing

---

## 🚀 Inicio Rápido

### Requisitos
- Python 3.10+
- Node.js 16+
- npm 7+

### Setup Local (5 minutos)

```bash
# 1. Clonar y entrar al proyecto
cd tfg-claude

# 2. Backend - crear venv e instalar
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Backend - inicializar BD con datos demo
python scripts/seed_demo.py

# 4. Backend - ejecutar
python -m uvicorn app.main:app --reload
# Accesible en http://localhost:8000
# API docs en http://localhost:8000/docs

# 5. Frontend - instalar (otra terminal)
cd frontend
npm install

# 6. Frontend - ejecutar
npm run dev
# Accesible en http://localhost:5173

# 7. Credenciales demo
# Admin: admin@test.com / admin123
# User: user@test.com / user123
```

### Ejecutar Tests
```bash
python -m unittest discover -s tests -p "test*.py" -v
# Resultado: 106 tests OK
```

### Build Frontend
```bash
cd frontend
npm run build
# Resultado: dist/ generado sin errores
```

---

## 📖 Documentación Completa

- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Guía paso a paso para demostración
- **[VALIDATION.md](VALIDATION.md)** - Validación técnica completa
- **[SEED_DEMO.md](SEED_DEMO.md)** - Documentación del seed de datos
- **[ENTREGA_FASE10.md](ENTREGA_FASE10.md)** - Cierre de FASE 10

---

## Estructura del Proyecto

```
tfg-claude/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada FastAPI
│   ├── config.py            # Configuración centralizada
│   ├── database.py          # SQLAlchemy setup
│   ├── dependencies.py      # Dependencias (get_current_user, etc.)
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── base.py          # Mixin TimestampMixin
│   │   ├── user.py
│   │   ├── crop.py
│   │   ├── planting_calendar.py
│   │   ├── irrigation_attributes.py
│   │   ├── environmental_requirements.py
│   │   ├── cultivation_guide.py
│   │   ├── task.py
│   │   └── task_crop.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── crop.py
│   │   └── task.py
│   ├── routes/              # FastAPI routers
│   │   ├── auth.py          # Login, registro
│   │   └── users.py         # CRUD usuarios
│   └── services/            # Lógica de negocio
│       ├── auth_service.py  # JWT, hashing
│       └── user_service.py  # Operaciones usuario
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   └── api.js       # Cliente HTTP Fetch API
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   └── components/
│   │       └── Navbar.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── tests/
│   ├── conftest.py          # Configuración pytest (no es pytest, pero compatible)
│   └── test_api.py          # Tests con unittest + TestClient
├── uploads/                 # Directorio para archivos subidos
├── .env                     # Variables de entorno (local)
├── .env.example             # Plantilla de variables
├── requirements.txt         # Dependencias Python
└── README.md                # Este archivo
```

---

## Fases Implementadas

### ✅ FASE 1: Arquitectura Base
- Backend FastAPI con estructura modular
- SQLAlchemy ORM
- Pydantic para validación
- Lectura de .env con config centralizada
- CORS configurable
- Montaje de `/uploads`
- GET `/` con JSON de salud
- Logging

### ✅ FASE 2: Modelos y Schemas
- **Modelos SQLAlchemy:** User, Crop, PlantingCalendar, IrrigationAttributes, EnvironmentalRequirements, CultivationGuide, Task, TaskCrop
- **Schemas Pydantic:** Validación separada por dominio (auth, user, crop, task)
- **Reglas:** Password no se expone, User tiene role user/admin, Crop puede ser público/privado/copia, Task asociado a varios cultivos

### ✅ FASE 3: Autenticación y Usuarios
- POST `/auth/register` - Registro de usuario
- POST `/auth/login` - Login con JWT
- Password hasheada con bcrypt
- Dependencia `get_current_user` para proteger rutas
- GET `/users/` - Listar usuarios (solo admin)
- GET `/users/{user_id}` - Ver datos usuario (usuario normal solo puede ver sí mismo, admin puede ver todos)
- DELETE `/users/{user_id}` - Eliminar usuario (usuario normal solo puede eliminar su cuenta, admin puede eliminar cualquiera)
- Rutas protegidas fallan sin token (401)
- Permisos verificados correctamente (403 si no autorizado)
- Google OAuth preparado (sin credenciales reales)

### ✅ FASE 4: Cultivos y Catálogo (NUEVO)
- **CRUD de Cultivos:**
  - POST `/crops/` - Crear cultivo (multipart/form-data con imagen opcional)
  - GET `/crops/my` - Listar cultivos del usuario
  - GET `/crops/` - Listar cultivos (user: sus + públicos; admin: todos)
  - GET `/crops/{crop_id}` - Ver detalles de cultivo
  - PUT `/crops/{crop_id}` - Actualizar cultivo (multipart/form-data)
  - DELETE `/crops/{crop_id}` - Eliminar cultivo
- **Catálogo Público:**
  - GET `/crops/published` - Listar catálogo (paginación, filtros por nombre/tipo)
  - POST `/crops/{crop_id}/add-to-my-crops` - Copiar cultivo del catálogo
  - GET `/crops/user/{user_id}` - Ver cultivos públicos de usuario
- **Características:**
  - Imágenes guardadas en `uploads/crops/` con UUID
  - Datos de riego y ambientales creados por defecto
  - Copias independientes del original (cambios no se replican)
  - Cultivos originales públicos se conservan en catálogo al eliminar (propietario se desvincula)
  - Permisos: user solo ve/edita sus cultivos, admin ve/edita todos
  - User normal no puede crear cultivos públicos (solo admin)
  - Paginación y filtros en catálogo
- **Tests:** 13 nuevos tests para cultivos (25 tests totales, 100% passing)

### ⏳ FASE 5+: Próximas Implementaciones
- Calendario de siembra
- Tareas agrícolas
- Dashboard de usuario
- Panel de administración
- Búsqueda avanzada
- Recomendaciones por región
- Rutas protegidas fallan sin token (401)
- Permisos verificados correctamente (403 si no autorizado)
- Google OAuth preparado (sin credenciales reales)

---

## Instalación

### Backend

#### 1. Crear entorno virtual

```bash
# En la carpeta tfg-claude
python -m venv venv

# Activar (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activar (Linux/Mac)
source venv/bin/activate
```

#### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 3. Configurar .env

El archivo `.env` ya está creado con SQLite local como BD:

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=dev-secret-key-change-in-prod-12345
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_ENV=development
DEBUG=True
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

Si quieres usar **PostgreSQL** en lugar de SQLite:

```env
DATABASE_URL=postgresql://postgres:admin@localhost:5432/tfg_db
```

(Asegúrate de que PostgreSQL esté corriendo y la BD exista)

### Frontend

#### 1. Instalar dependencias

```bash
cd frontend
npm install
```

---

## Ejecución

### Backend

```bash
# Asegúrate de estar en tfg-claude/ con venv activado
uvicorn app.main:app --reload --port 8000
```

El backend estará disponible en:
- **API:** http://localhost:8000
- **Docs interactivos:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Frontend

```bash
# En otra terminal, en tfg-claude/frontend
npm run dev
```

El frontend estará disponible en:
- **App:** http://localhost:5173

---

## Pruebas

### Tests Automatizados

```bash
# En tfg-claude/ con venv activado
python -m unittest tests.test_api -v
```

O para test específico:

```bash
python -m unittest tests.test_api.TestHealth.test_health_check_root -v
```

### Pruebas Manuales con cURL/Postman

#### 1. Health Check

```bash
curl -X GET http://localhost:8000/
```

**Esperado:**
```json
{
  "status": "ok",
  "app": "AgroManager",
  "environment": "development",
  "version": "1.0.0"
}
```

#### 2. Registro

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "name": "Test User"
  }'
```

**Esperado:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "Test User",
  "role": "user",
  "is_active": true,
  "created_at": "2024-05-12T10:00:00+00:00",
  "updated_at": "2024-05-12T10:00:00+00:00"
}
```

#### 3. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

**Esperado:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 4. Ruta Protegida sin Token

```bash
curl -X GET http://localhost:8000/users/1
```

**Esperado:** 401 Unauthorized

#### 5. Ruta Protegida con Token

```bash
curl -X GET http://localhost:8000/users/1 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Esperado:** Datos del usuario (sin password)

#### 6. Usuario Normal Intenta Acceder a Otros

```bash
# Registrar segundo usuario
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "other@example.com",
    "password": "OtherPass123",
    "name": "Other User"
  }'

# Intentar acceder como primer usuario
curl -X GET http://localhost:8000/users/2 \
  -H "Authorization: Bearer {token_de_usuario_1}"
```

**Esperado:** 403 Forbidden

#### 7. Listar Usuarios (Admin)

```bash
# Crear usuario admin (manualmente en BD o con SQL)
curl -X GET http://localhost:8000/users/ \
  -H "Authorization: Bearer {token_de_admin}"
```

**Esperado:** Lista de todos los usuarios

---

## Decisiones Técnicas

| Decisión | Justificación |
|----------|---------------|
| **BD por defecto SQLite local** | Desarrollo rápido sin PostgreSQL instalado. PostgreSQL soportado vía DATABASE_URL |
| **JWT sin refresh tokens** | Simplificación fase piloto; agregar en fase siguiente |
| **Unittest + TestClient** | Conforme a contexto maestro; BD SQLite en memoria para tests |
| **Fetch API vs Axios** | Reducción de dependencias; API nativa suficiente |
| **Modelos con TimestampMixin** | Auditoría y consistencia |
| **Schemas separados por dominio** | Validación clara y evitar exposición de campos internos |
| **Password nunca en responses** | Seguridad |
| **Role enum** | Type-safe y queryable |
| **Google OAuth preparado sin deps** | Preparación para fase siguiente sin bloquear desarrollo |

---

## Limitaciones (Fase Piloto)

1. **Sin refresh tokens** - Token expira después de 30 min sin renovación
2. **Sin rate limiting** - Vulnerable a fuerza bruta en login
3. **Sin validación SMTP** - Email no se valida contra servidor real
4. **Sin logging centralizado** - Solo logging básico
5. **BD SQLite en dev** - No escalable a producción
6. **Sin HTTPS** - Solo HTTP local
7. **Sin CSRF protection** - Agregar en producción
8. **Sin validación avanzada de password** - Mínimo 8 caracteres, sin complejidad

---

## Qué Queda Pendiente

### FASE 4: CRUD Cultivos
- POST /crops - Crear cultivo
- GET /crops - Listar cultivos (públicos + propios del usuario)
- GET /crops/{id} - Obtener detalle cultivo
- PUT /crops/{id} - Editar cultivo
- DELETE /crops/{id} - Eliminar cultivo
- Lógica: público, privado, copiar cultivo

### FASE 5: Rutas de Modelos Asociados
- PlantingCalendar CRUD
- IrrigationAttributes CRUD
- EnvironmentalRequirements CRUD
- CultivationGuide CRUD
- Task CRUD
- TaskCrop CRUD

### FASE 6: Dashboard y Admin
- GET /dashboard - Estadísticas de usuario
- Admin panel: listado de usuarios, cultivos, etc.

### FASE 7: Frontend Funcional
- Componentes UI para login/registro
- Dashboard usuarios
- Gestión de cultivos
- Integración con API

### FASE 8: Google OAuth
- Integración real con Google
- Callback handling
- User creation automático

### ✅ FASE 9: Panel Admin Visual en Frontend
- **Dashboard admin** con 8 métricas (usuarios, cultivos, tareas, etc.)
- **CRUD Usuarios:** Editar email/nombre/rol/estado, eliminar con confirmación
- **CRUD Cultivos:** Editar nombre/tipo/descripción/público, eliminar
- **CRUD Tareas:** Editar título/descripción/estado/fecha, eliminar
- **Rutas protegidas:** `/admin`, `/admin/dashboard`, `/admin/users`, `/admin/crops`, `/admin/tasks`
- **ProtectedAdminRoute:** Componente que verifica `user.role === 'admin'`
- **Navbar actualizado:** Enlace "Admin" solo visible para admins
- **12 funciones API:** getAdminSummary, getAdminUsers/Crops/Tasks + CRUD
- **Script helper:** `make_admin.py` para convertir usuarios a admin
- **Edición inline:** Cambios en vivo en tablas con Guardar/Cancelar
- **Estados de carga:** Loading, error, vacío en cada página
- **Build verificado:** npm run build sin errores
- **Tests intactos:** 83/83 tests pasando

### ✅ FASE 10: Seed/Admin Inicial y Datos de Ejemplo
- **Script seed idempotente:** `scripts/seed_demo.py`
- **Usuario admin demo:** admin@test.com / admin123
- **Usuario demo:** user@test.com / user123
- **Cultivos de ejemplo:** 5 públicos (Tomate, Lechuga, Zanahoria, Pepino, Fresa) + 1 privado
- **Atributos de riego:** Para cada cultivo (frecuencia, cantidad, tipo)
- **Requisitos ambientales:** Temperatura, humedad, luz, pH, tipo suelo
- **Calendarios de siembra:** Tomate, Lechuga, Zanahoria con fases
- **Tareas de ejemplo:** 4 tareas para usuario demo
- **Opciones de limpieza:** `--clean` para limpiar demo, `--reset` para reset total
- **Totalmente idempotente:** Seguro ejecutar múltiples veces

### FASE 11: Migraciones Alembic
- Versionado de esquema BD
- Rollback automático
- Historial de cambios

---

## Archivos Creados/Modificados

### Backend (app/)
- ✅ `__init__.py` - Módulo
- ✅ `config.py` - Configuración centralizada
- ✅ `database.py` - SQLAlchemy setup
- ✅ `dependencies.py` - Dependencias JWT
- ✅ `main.py` - Punto de entrada FastAPI
- ✅ `models/base.py` - Mixin TimestampMixin
- ✅ `models/user.py` - Modelo User
- ✅ `models/crop.py` - Modelo Crop
- ✅ `models/planting_calendar.py` - Modelo PlantingCalendar
- ✅ `models/irrigation_attributes.py` - Modelo IrrigationAttributes
- ✅ `models/environmental_requirements.py` - Modelo EnvironmentalRequirements
- ✅ `models/cultivation_guide.py` - Modelo CultivationGuide
- ✅ `models/task.py` - Modelo Task
- ✅ `models/task_crop.py` - Modelo TaskCrop
- ✅ `schemas/auth.py` - Schemas de autenticación
- ✅ `schemas/user.py` - Schemas de usuario
- ✅ `schemas/crop.py` - Schemas de cultivo
- ✅ `schemas/task.py` - Schemas de tarea
- ✅ `services/auth_service.py` - Hashing, JWT
- ✅ `services/user_service.py` - Operaciones usuario
- ✅ `routes/auth.py` - Rutas login, registro
- ✅ `routes/users.py` - Rutas usuario CRUD

### Frontend (frontend/)
- ✅ `package.json` - Dependencias npm
- ✅ `vite.config.js` - Configuración Vite
- ✅ `index.html` - HTML base
- ✅ `src/main.jsx` - Punto de entrada React
- ✅ `src/App.jsx` - Componente principal + rutas admin (FASE 9)
- ✅ `src/index.css` - Estilos base
- ✅ `src/api/api.js` - Cliente HTTP Fetch API + funciones admin (FASE 9)
- ✅ `src/context/AuthContext.jsx` - Contexto autenticación
- ✅ `src/components/Navbar.jsx` - Navbar + enlace admin (FASE 9)
- ✅ `src/components/ProtectedAdminRoute.jsx` - Componente protección admin (FASE 9)
- ✅ `src/pages/AdminDashboard.jsx` - Dashboard admin (FASE 9)
- ✅ `src/pages/AdminUsers.jsx` - Gestión usuarios admin (FASE 9)
- ✅ `src/pages/AdminCrops.jsx` - Gestión cultivos admin (FASE 9)
- ✅ `src/pages/AdminTasks.jsx` - Gestión tareas admin (FASE 9)
- ✅ `src/pages/AdminPages.css` - Estilos admin (FASE 9)
- ✅ `README.md` - Documentación frontend

### Tests (tests/)
- ✅ `conftest.py` - Configuración tests
- ✅ `test_api.py` - Tests unitarios (unittest + TestClient)

### Scripts (scripts/)
- ✅ `make_admin.py` - Utilidad para convertir usuarios en admin (FASE 9)
- ✅ `seed_demo.py` - Script idempotente para seed de datos demo (FASE 10)

### Configuración Proyecto
- ✅ `requirements.txt` - Dependencias Python
- ✅ `.env` - Variables de entorno (dev)
- ✅ `.env.example` - Plantilla de variables
- ✅ `README.md` - Documentación proyecto
- ✅ `PHASE9_IMPLEMENTATION.md` - Documentación FASE 9 (FASE 9)
- ✅ `QUICKSTART_PHASE9.md` - Guía rápida FASE 9 (FASE 9)
- ✅ `PHASE10_IMPLEMENTATION.md` - Documentación FASE 10 (FASE 10)
- ✅ `QUICKSTART_PHASE10.md` - Guía rápida FASE 10 (FASE 10)

---

## Próximos Pasos

1. **Verificar instalación:**
   ```bash
   pip install -r requirements.txt
   python -m unittest tests.test_api -v
   ```

2. **Arrancar backend:**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Arrancar frontend:**
   ```bash
   cd frontend && npm install && npm run dev
   ```

4. **Probar endpoints con Postman o cURL**

5. **Implementar FASE 4** cuando esta esté validada

---

## Contacto

Reconstrucción piloto de AgroManager | Versión 1.0.0 | Desarrollo | 2024
