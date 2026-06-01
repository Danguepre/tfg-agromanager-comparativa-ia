# AgroManager

Aplicación web para la gestión integral de cultivos agrícolas personales,
catálogo público de cultivos, calendario agrícola por fases, tareas,
riego y requisitos ambientales.

Caso práctico del **Trabajo de Fin de Grado (TFG)** sobre reconstrucción
de aplicaciones legacy usando asistentes de IA generativa.

## Stack tecnológico

| Capa      | Tecnología                                                    |
|-----------|---------------------------------------------------------------|
| Backend   | **FastAPI** + **SQLAlchemy** + **Pydantic** + **SQLite**      |
| Frontend  | **React** + **Vite** + **Fetch API**                          |
| Auth      | JWT (access token con `python-jose` + `passlib`/bcrypt)       |
| Tests     | **unittest** + `fastapi.testclient.TestClient`                |

## Funcionalidades principales

- **Registro / Login** de usuarios con JWT
- **Gestión de usuarios** con roles `user` y `admin`
- **Cultivos personales** (CRUD completo)
- **Catálogo público** de cultivos con búsqueda y paginación
- **Copiar cultivo** del catálogo a cultivos personales
- **Calendario agrícola por fases**: siembra, trasplante, cosecha
- **Tareas** (pending / completed) asociables a cultivos
- **Riego** (frecuencia, método, volumen de agua)
- **Requisitos ambientales** (temperatura, pH, suelo, horas de sol)
- **Guías de cultivo** detalladas
- **Dashboard de usuario** con resumen de cultivos, tareas, calendario, riego y ambiente
- **Panel de administración** con estadísticas globales y CRUD de usuarios/cultivos/tareas
- **Seed de desarrollo** con datos demo

## Estructura del proyecto

```
tfg-deepseek/
├── app/
│   ├── main.py                   # Punto de entrada FastAPI
│   ├── config.py                 # Configuración (pydantic-settings)
│   ├── database.py               # Conexión SQLAlchemy + sesión
│   ├── auth.py                   # JWT y hashing de contraseñas
│   ├── dependencies.py           # Dependencias (get_current_user)
│   ├── models/                   # Modelos SQLAlchemy
│   │   ├── user.py               #   Usuario
│   │   ├── crop.py               #   Cultivo
│   │   ├── planting_calendar.py  #   Calendario agrícola
│   │   ├── irrigation_attributes.py
│   │   ├── environmental_requirements.py
│   │   ├── cultivation_guide.py  #   Guía de cultivo
│   │   ├── task.py               #   Tarea
│   │   └── task_crop.py          #   Relación tarea-cultivo
│   ├── schemas/                  # Schemas Pydantic
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── crop.py
│   │   ├── planting_calendar.py
│   │   ├── irrigation_attributes.py
│   │   ├── environmental_requirements.py
│   │   ├── cultivation_guide.py
│   │   ├── task.py
│   │   ├── task_crop.py
│   │   ├── dashboard.py
│   │   └── admin.py
│   ├── routes/                   # Rutas FastAPI
│   │   ├── auth.py               #   /auth/*
│   │   ├── user.py               #   /users/*
│   │   ├── crop.py               #   /crops/*
│   │   ├── planting_calendar.py  #   /calendar/*
│   │   ├── irrigation.py         #   /irrigation/*
│   │   ├── environmental.py      #   /environmental/*
│   │   ├── task.py               #   /tasks/*
│   │   ├── dashboard.py          #   /dashboard/*
│   │   └── admin.py              #   /admin/*
│   └── services/                 # Lógica de negocio (reservado)
├── frontend/                     # Aplicación React + Vite
│   ├── src/
│   │   ├── api/                  #   Llamadas a la API
│   │   ├── components/           #   Componentes reutilizables
│   │   ├── context/              #   AuthContext (React Context)
│   │   └── pages/                #   Páginas de la aplicación
│   │       └── admin/            #   Páginas del panel admin
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── scripts/
│   └── seed_demo.py              # Script de seed de desarrollo
├── tests/
│   ├── test_api.py               # Tests de API (104 tests)
│   └── test_seed.py              # Tests del seed (13 tests)
├── uploads/                      # Archivos subidos (imágenes)
├── .env.example                  # Variables de entorno de ejemplo
├── SEED_DEMO.md                  # Documentación del seed
├── DEMO_GUIDE.md                 # Guía rápida de demostración
├── VALIDATION.md                 # Guía técnica de validación
└── README.md                     # Este archivo
```

## Requisitos previos

- **Python 3.10+**
- **Node.js 18+**
- **npm** (incluido con Node.js)

## Instalación

### Backend

```bash
# Desde el directorio raíz del proyecto (tfg-deepseek/)
python -m venv venv

# Activar el entorno virtual:
#   Windows (PowerShell): venv\Scripts\Activate.ps1
#   Windows (cmd):        venv\Scripts\activate.bat
#   Linux/macOS:          source venv/bin/activate

pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
cd ..
```

## Variables de entorno

El proyecto se configura mediante variables de entorno (archivo `.env`):

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./agromanager.db` | URL de conexión a la BD |
| `SECRET_KEY` | `change-me-in-production` | Clave secreta para firmar JWT |
| `ALGORITHM` | `HS256` | Algoritmo de firma JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Minutos de validez del token |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes permitidos (CORS) |
| `GOOGLE_CLIENT_ID` | (opcional) | ID de cliente OAuth de Google |

Copia `.env.example` a `.env` y ajusta si es necesario:

```bash
cp .env.example .env
```

> **Nota**: Actualmente la configuración con variables de entorno está implementada.
> Los valores del `.env.example` son seguros para desarrollo.

## Ejecución

### Backend

```bash
cd tfg-deepseek
python -m uvicorn app.main:app --reload
```

Servidor en: `http://127.0.0.1:8000`

Documentación interactiva (OpenAPI/Swagger): `http://127.0.0.1:8000/docs`

### Frontend (en otra terminal)

```bash
cd tfg-deepseek/frontend
npm run dev
```

Frontend en: `http://localhost:5173`

### Seed de datos demo

Inicializa la base de datos con datos de ejemplo:

```bash
cd tfg-deepseek
python scripts/seed_demo.py
```

Ver documentación completa en [SEED_DEMO.md](SEED_DEMO.md).

## Credenciales demo (tras ejecutar seed)

| Rol    | Email            | Contraseña |
|--------|------------------|------------|
| Admin  | admin@test.com   | admin123   |
| User   | user@test.com    | user123    |

> ⚠️ Estas credenciales son exclusivamente para desarrollo local.
> No deben usarse en ningún entorno de producción.

## Tests

```bash
# Ejecutar todos los tests (117 tests)
cd tfg-deepseek
python -m unittest tests.test_api tests.test_seed -v

# Ejecutar solo tests de API
python -m unittest tests.test_api -v

# Ejecutar solo tests del seed
python -m unittest tests.test_seed -v
```

> **Observación**: En Windows PowerShell, `unittest discover` con patrón puede no
> encontrar tests. Usa la invocación explícita de módulos (recomendada arriba).

## Build frontend (producción)

```bash
cd tfg-deepseek/frontend
npm run build
```

El build genera los archivos estáticos en `frontend/dist/`.

## Validación visual

Tras ejecutar seed, iniciar backend y frontend:

1. **Login como user**: user@test.com / user123
   - Dashboard con contadores de cultivos y tareas
   - Mis cultivos: "Mi Tomate" y "Mi Lechuga"
   - Catálogo público: 5 cultivos
   - Calendario: eventos de "Mi Tomate"
   - Tareas: 2 pending + 2 completed

2. **Login como admin**: admin@test.com / admin123
   - Admin Dashboard con estadísticas globales
   - Admin Users: lista de usuarios registrados
   - Admin Crops: todos los cultivos
   - Admin Tasks: todas las tareas

## Limitaciones conocidas

1. **Base de datos**: SQLite (no apto para producción multiusuario).
2. **Migraciones**: No hay sistema de migraciones (Alembic) implementado.
3. **Imágenes**: Las imágenes de cultivos son placeholders.
4. **Autenticación social**: Google OAuth no está implementado (campo preparado).
5. **Tests E2E**: No hay pruebas de extremo a extremo.
6. **`unittest discover`**: En Windows PowerShell, usar `discover -s tests -p "test*.py"`
   puede no detectar tests. La invocación explícita de módulos es la vía recomendada.
7. **Separación tests**: Los tests de API y seed usan archivos `.db` distintos y
   `dependency_overrides` propios, por lo que deben ejecutarse juntos explícitamente
   (no con `discover` en PowerShell).

## Trabajo futuro

- Migrar a PostgreSQL y usar Alembic para migraciones.
- Implementar autenticación OAuth (Google, GitHub).
- Añadir tests E2E con Playwright o Cypress.
- Sistema de notificaciones (riego, tareas próximas).
- Internacionalización (i18n).
- Despliegue con Docker y CI/CD.
- Módulo de analytics y gráficos.