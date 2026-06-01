# Comandos Rápidos para AgroManager Pilot

Este archivo contiene todos los comandos necesarios para instalar, ejecutar y probar AgroManager.

## 1. Instalación Backend

```bash
# Navegar a tfg-claude
cd c:\Users\danie\Desktop\tfg\tfg-claude

# Crear entorno virtual
python -m venv venv

# Activar (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activar (Windows CMD)
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt
```

## 2. Instalación Frontend

```bash
# En otra terminal, navegar a frontend
cd c:\Users\danie\Desktop\tfg\tfg-claude\frontend

# Instalar dependencias npm
npm install
```

## 3. Ejecutar Backend

```bash
# Desde tfg-claude/ con venv activado
uvicorn app.main:app --reload --port 8000
```

Backend estará en: http://localhost:8000
Docs: http://localhost:8000/docs

## 4. Ejecutar Frontend

```bash
# Desde tfg-claude/frontend
npm run dev
```

Frontend estará en: http://localhost:5173

## 5. Correr Tests

```bash
# Desde tfg-claude/ con venv activado
python -m unittest tests.test_api -v
```

O test específico:

```bash
python -m unittest tests.test_api.TestHealth -v
python -m unittest tests.test_api.TestAuthenticationRegister -v
python -m unittest tests.test_api.TestAuthenticationLogin -v
python -m unittest tests.test_api.TestUserManagement -v
```

## 6. Pruebas Manuales (cURL/Postman)

### Health Check
```bash
curl -X GET http://localhost:8000/
```

### Registrar Usuario
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123",
    "name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123"
  }'
```

Copia el `access_token` de la respuesta.

### Obtener Datos de Usuario (con token)
```bash
curl -X GET http://localhost:8000/users/1 \
  -H "Authorization: Bearer {access_token}"
```

### Sin Token (debe fallar 401)
```bash
curl -X GET http://localhost:8000/users/1
```

### Intentar Acceder a Otro Usuario (debe fallar 403)
```bash
# Registrar segundo usuario, obtener su token
# Intentar acceder como primer usuario
curl -X GET http://localhost:8000/users/2 \
  -H "Authorization: Bearer {token_user_1}"
```

## 7. Cambiar BD a PostgreSQL (Opcional)

Si quieres usar PostgreSQL en lugar de SQLite:

### Instalar PostgreSQL
- Descargar desde https://www.postgresql.org/download/
- Crear BD: `tfg_db`
- Usuario: `postgres`
- Contraseña: `admin`

### Actualizar .env
```env
DATABASE_URL=postgresql://postgres:admin@localhost:5432/tfg_db
```

### Reiniciar Backend
```bash
uvicorn app.main:app --reload
```

## 8. Variables de Entorno Disponibles

Ver `.env.example` para todas las opciones:

- `DATABASE_URL` - Conexión a BD (PostgreSQL o SQLite)
- `SECRET_KEY` - Clave secreta JWT
- `ALGORITHM` - Algoritmo JWT (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Expiración token (30 min)
- `APP_ENV` - Entorno (development/production)
- `DEBUG` - Debug mode (True/False)
- `CORS_ORIGINS` - Orígenes CORS permitidos
- `GOOGLE_CLIENT_ID` - Google OAuth (opcional)
- `GOOGLE_CLIENT_SECRET` - Google OAuth (opcional)
- `FRONTEND_URL` - URL del frontend

## 9. Estructura de Carpetas

```
tfg-claude/
├── app/                 # Backend FastAPI
├── frontend/            # Frontend React/Vite
├── tests/               # Tests
├── uploads/             # Archivos subidos
├── requirements.txt     # Dependencias Python
├── .env                 # Variables (local, no pushear)
├── .env.example         # Plantilla
└── README.md            # Documentación
```

## 10. Troubleshooting

### Error: "No module named 'app'"
- Asegurar estar en la carpeta `tfg-claude/`
- Venv activado

### Error: "Address already in use :8000"
- Backend ya está corriendo
- Usar otro puerto: `uvicorn app.main:app --reload --port 8001`

### Error: "Cannot connect to database"
- Verificar DATABASE_URL en .env
- Si usa PostgreSQL, verificar que PostgreSQL esté corriendo
- Si usa SQLite, verificar permisos en la carpeta

### Error: "CORS error"
- Verificar CORS_ORIGINS en .env
- Incluir http://localhost:5173 si frontend está en local

## 11. Estructura de Código

### Modelos (SQLAlchemy)
- `app/models/user.py` - User, UserRole
- `app/models/crop.py` - Crop
- `app/models/task.py` - Task, TaskStatus
- Más en `app/models/`

### Schemas (Pydantic)
- `app/schemas/auth.py` - AuthRegisterRequest, AuthLoginRequest, TokenResponse
- `app/schemas/user.py` - UserResponse
- `app/schemas/crop.py` - CropResponse
- Más en `app/schemas/`

### Rutas (FastAPI)
- `app/routes/auth.py` - /auth/register, /auth/login
- `app/routes/users.py` - /users/, /users/{id}, DELETE /users/{id}

### Servicios
- `app/services/auth_service.py` - hash_password, verify_password, create_access_token, decode_token
- `app/services/user_service.py` - create_user, authenticate_user, etc.

### Dependencias
- `app/dependencies.py` - get_current_user, get_current_admin

## 12. Criterios de Aceptación (✅ Completados)

- ✅ Backend arranca con uvicorn
- ✅ GET / devuelve salud
- ✅ Tablas se crean correctamente
- ✅ Se puede registrar usuario
- ✅ Se puede hacer login
- ✅ Login devuelve access_token
- ✅ Ruta protegida falla sin token (401)
- ✅ Usuario normal no puede ver datos de otros usuarios (403)
- ✅ Admin puede ver todos los usuarios
- ✅ Password no se expone en respuestas

## 13. Próximas Fases

- FASE 4: CRUD Cultivos
- FASE 5: Rutas modelos asociados
- FASE 6: Dashboard y Admin
- FASE 7: Frontend funcional
- FASE 8: Google OAuth
- FASE 9: Testing
- FASE 10: Deploy

---

**Reconstrucción Piloto AgroManager | v1.0.0 | 2024**
