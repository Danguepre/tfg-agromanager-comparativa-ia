# 🎬 Guía de Demostración — AgroManager

Guía paso a paso para demostrar la aplicación completa.

## Requisitos

- Python 3.10+
- Node.js 18+
- Git (opcional)

## 1. Preparación del entorno

```bash
# Clonar o situarse en el directorio del proyecto
cd tfg-deepseek

# Crear y activar entorno virtual Python
python -m venv venv

# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows cmd:
venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Instalar dependencias backend
pip install -r requirements.txt

# Variable de entorno (opcional, hay valores por defecto)
cp .env.example .env
```

## 2. Seed de datos demo

```bash
cd tfg-deepseek
python scripts/seed_demo.py
```

Deberías ver un resumen como:

```
🌱 SEED DE DESARROLLO — RESUMEN
  Usuarios creados:    2
  Cultivos creados:    7
  Calendarios creados: 3
  Tareas creadas:      4
  ...
```

## 3. Iniciar backend

```bash
cd tfg-deepseek
python -m uvicorn app.main:app --reload
```

- API: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

## 4. Iniciar frontend (otra terminal)

```bash
cd tfg-deepseek/frontend
npm install   # solo la primera vez
npm run dev
```

- Frontend: `http://localhost:5173`

## 5. Demo como usuario normal

Abrir `http://localhost:5173` en el navegador.

### 5.1 Login
- Email: `user@test.com`
- Contraseña: `user123`

### 5.2 Dashboard
- Ver contadores: cultivos personales, tareas pendientes/completadas
- Ver secciones: irrigación, ambiente, calendario

### 5.3 Mis Cultivos
- Ver "Mi Tomate" y "Mi Lechuga"
- Hacer clic en un cultivo para ver detalle
- En detalle: riego, ambiente, calendario

### 5.4 Catálogo
- Ver 5 cultivos públicos: Tomate, Lechuga, Zanahoria, Pimiento, Fresa
- Usar filtros de búsqueda y categoría
- Copiar un cultivo a "Mis cultivos"

### 5.5 Calendario
- Ver eventos del calendario activo de "Mi Tomate"
- Navegar por meses

### 5.6 Tareas
- Ver 4 tareas: 2 pending, 2 completed
- Marcar/desmarcar tareas como completadas
- Crear nueva tarea

## 6. Demo como administrador

Cerrar sesión (botón en navbar).

### 6.1 Login
- Email: `admin@test.com`
- Contraseña: `admin123`

### 6.2 Admin Dashboard
- Estadísticas globales: usuarios, cultivos, tareas, calendarios

### 6.3 Admin Users
- Lista de usuarios registrados
- Ver editar/desactivar usuarios

### 6.4 Admin Crops
- Todos los cultivos (públicos y personales)

### 6.5 Admin Tasks
- Todas las tareas de todos los usuarios

## 7. Probar la API directamente

Con el backend corriendo, puedes probar endpoints con curl o desde Swagger:

```bash
# Health check
curl http://127.0.0.1:8000/

# Login como admin
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# Catálogo público (sin autenticación)
curl http://127.0.0.1:8000/crops/published
```

Desde Swagger: `http://127.0.0.1:8000/docs`

## Resumen de URLs

| Recurso                | URL                                          |
|------------------------|----------------------------------------------|
| Frontend               | `http://localhost:5173`                      |
| Backend API            | `http://127.0.0.1:8000`                      |
| Swagger Docs           | `http://127.0.0.1:8000/docs`                 |
| Health Check           | `http://127.0.0.1:8000/`                     |
| Catálogo público       | `http://127.0.0.1:8000/crops/published`      |
| Login (API)            | `POST http://127.0.0.1:8000/auth/login`      |
| Registro (API)         | `POST http://127.0.0.1:8000/users/`          |
| Dashboard (API)        | `GET http://127.0.0.1:8000/dashboard/summary` |
| Admin Summary (API)    | `GET http://127.0.0.1:8000/admin/summary`    |