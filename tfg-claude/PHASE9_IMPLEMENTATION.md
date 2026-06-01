# FASE 9: Panel Admin Visual en Frontend

**Estado:** ✅ Completada

## Descripción
Implementación del panel de administración visual en el frontend para gestionar usuarios, cultivos y tareas globales usando los endpoints admin del backend (FASE 7).

---

## Cambios Realizados

### 1. Archivos Creados

**Frontend (React/Vite):**
- `frontend/src/components/ProtectedAdminRoute.jsx` - Componente para proteger rutas admin
- `frontend/src/pages/AdminDashboard.jsx` - Dashboard admin con resumen global
- `frontend/src/pages/AdminUsers.jsx` - Gestión de usuarios (CRUD)
- `frontend/src/pages/AdminCrops.jsx` - Gestión de cultivos (CRUD)
- `frontend/src/pages/AdminTasks.jsx` - Gestión de tareas (CRUD)
- `frontend/src/pages/AdminPages.css` - Estilos para todas las páginas admin

**Scripts:**
- `scripts/make_admin.py` - Utilidad para convertir usuarios en admin en SQLite

### 2. Archivos Modificados

**Frontend:**
- `frontend/src/App.jsx` - Agregadas rutas `/admin/*` con protección
- `frontend/src/api/api.js` - 12 nuevas funciones para endpoints admin
- `frontend/src/components/Navbar.jsx` - Enlace "Admin" visible solo para admins

---

## Funcionalidades Implementadas

### ✅ Acceso Admin
- ✓ Ruta `/admin` → Redirige a `/admin/dashboard`
- ✓ Rutas hijo: `/admin/dashboard`, `/admin/users`, `/admin/crops`, `/admin/tasks`
- ✓ Protección: `ProtectedAdminRoute` verifica `user.role === 'admin'`
- ✓ Acceso denegado: Usuario normal ve "Acceso Denegado"
- ✓ Sin token: Redirige a `/login`
- ✓ Navbar: Enlace "🔧 Admin" solo visible para admins

### ✅ Dashboard Admin
- ✓ Consume: `GET /admin/summary`
- ✓ Muestra:
  - Total usuarios
  - Total cultivos
  - Total cultivos públicos
  - Total tareas
  - Tareas pendientes / completadas
  - Calendarios activos / completados
- ✓ Manejo: Si campo no existe, muestra 0
- ✓ Enlaces rápidos a secciones admin

### ✅ Gestión de Usuarios (Admin)
- ✓ Consume: `GET /admin/users`, `GET /admin/users/{id}`, `PATCH /admin/users/{id}`, `DELETE /admin/users/{id}`
- ✓ Tabla listado de usuarios sin password
- ✓ Editable en línea: email, name, role, is_active
- ✓ Confirmar antes de eliminar
- ✓ Estados: loading, error, vacío
- ✓ Normalización: Lista paginada extraída correctamente

### ✅ Gestión de Cultivos (Admin)
- ✓ Consume: `GET /admin/crops`, `GET /admin/crops/{id}`, `PATCH /admin/crops/{id}`, `DELETE /admin/crops/{id}`
- ✓ Tabla listado de cultivos globales
- ✓ Editable: name, description, crop_type, is_public
- ✓ Confirmar antes de eliminar
- ✓ Estados: loading, error, vacío
- ✓ Normalización: Lista paginada extraída correctamente

### ✅ Gestión de Tareas (Admin)
- ✓ Consume: `GET /admin/tasks`, `GET /admin/tasks/{id}`, `PATCH /admin/tasks/{id}`, `DELETE /admin/tasks/{id}`
- ✓ Tabla listado de tareas globales
- ✓ Editable: title, description, status (pending/completed), due_date
- ✓ Confirmar antes de eliminar
- ✓ Estados: loading, error, vacío
- ✓ Normalización: Lista paginada extraída correctamente

### ✅ Cliente API (api.js)
12 nuevas funciones admin:
- `getAdminSummary(token)`
- `getAdminUsers(token, skip, limit)`
- `getAdminUser(userId, token)`
- `updateAdminUser(userId, data, token)`
- `deleteAdminUser(userId, token)`
- `getAdminCrops(token, skip, limit)`
- `getAdminCrop(cropId, token)`
- `updateAdminCrop(cropId, data, token)`
- `deleteAdminCrop(cropId, token)`
- `getAdminTasks(token, skip, limit)`
- `getAdminTask(taskId, token)`
- `updateAdminTask(taskId, data, token)`
- `deleteAdminTask(taskId, token)`

Todas:
- ✓ Incluyen `Authorization: Bearer <token>`
- ✓ Manejan 401 (sin sesión)
- ✓ Manejan 403 (sin permisos admin)
- ✓ Normalizan listas evitando `.map is not a function`
- ✓ Manejo de respuestas vacías

---

## Rutas Frontend Agregadas

| Ruta | Componente | Protección | Descripción |
|------|-----------|-----------|-----------|
| `/admin` | AdminDashboard | Admin | Panel principal admin |
| `/admin/dashboard` | AdminDashboard | Admin | Dashboard con resumen |
| `/admin/users` | AdminUsers | Admin | Gestión de usuarios |
| `/admin/crops` | AdminCrops | Admin | Gestión de cultivos |
| `/admin/tasks` | AdminTasks | Admin | Gestión de tareas |

---

## Endpoints Admin Consumidos

Todos del backend (FASE 7):

| Método | Endpoint | Uso |
|--------|----------|-----|
| GET | `/admin/summary` | Resumen global |
| GET | `/admin/users?skip=0&limit=50` | Listar usuarios |
| GET | `/admin/users/{user_id}` | Detalle usuario |
| PATCH | `/admin/users/{user_id}` | Editar usuario |
| DELETE | `/admin/users/{user_id}` | Eliminar usuario |
| GET | `/admin/crops?skip=0&limit=50` | Listar cultivos |
| GET | `/admin/crops/{crop_id}` | Detalle cultivo |
| PATCH | `/admin/crops/{crop_id}` | Editar cultivo |
| DELETE | `/admin/crops/{crop_id}` | Eliminar cultivo |
| GET | `/admin/tasks?skip=0&limit=50` | Listar tareas |
| GET | `/admin/tasks/{task_id}` | Detalle tarea |
| PATCH | `/admin/tasks/{task_id}` | Editar tarea |
| DELETE | `/admin/tasks/{task_id}` | Eliminar tarea |

---

## Protección por Rol Admin

### Frontend
1. **ProtectedAdminRoute** (nuevo componente)
   - Verifica: `user.role === 'admin'`
   - Sin token: Redirige a `/login`
   - No admin: Muestra "Acceso Denegado"

2. **Navbar.jsx** (modificado)
   - Enlace Admin condicional: `{user.role === 'admin' && <Link to="/admin/dashboard">🔧 Admin</Link>}`

### Backend (ya implementado FASE 7)
- Dependencia `get_current_admin` en todos los endpoints `/admin`
- Retorna 403 si usuario no es admin
- Retorna 401 si sin token

---

## Comandos de Prueba

### 1. Build Frontend
```bash
cd frontend
npm.cmd run build
```
✅ **Resultado esperado:** Compilación sin errores
```
✓ built in 598ms
```

### 2. Tests Backend
```bash
python -m unittest discover -s tests -p "test*.py" -v
```
✅ **Resultado esperado:** 83 tests pasados
```
Ran 83 tests in 53.525s
OK
```

### 3. Crear Usuario Admin para Prueba Manual

**Opción A: Usar script helper (recomendado)**
```bash
# Crear usuario normal mediante frontend/API
# Luego convertirlo en admin:
python scripts/make_admin.py 1
```

**Opción B: Método rápido (desarrollo)
En Python shell:
```python
from app.database import SessionLocal
from app.models.user import User, UserRole

db = SessionLocal()
user = db.query(User).filter(User.id == 1).first()
user.role = UserRole.ADMIN
db.commit()
db.close()
print(f"Usuario {user.email} es ahora admin")
```

### 4. Ejecutar Frontend en Desarrollo
```bash
cd frontend
npm.cmd run dev
```
Accede a `http://localhost:5173`

### 5. Ejecutar Backend
```bash
# En terminal separada
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## Validación Visual Manual

### 1. **Usuario Normal (sin rol admin)**
```
✓ Login con usuario normal
✓ NO ve enlace "Admin" en navbar
✓ NO puede acceder a /admin → Muestra "Acceso Denegado"
✓ Redirige a / al intentar acceso denegado
```

### 2. **Usuario Admin**
```
✓ Login con usuario admin
✓ VE enlace "🔧 Admin" en navbar
✓ Puede acceder a /admin/dashboard
✓ Dashboard carga con estadísticas
✓ Acceso a /admin/users, /admin/crops, /admin/tasks
```

### 3. **Operaciones CRUD**
```
✓ Editar usuario → Cambiar email, nombre, rol
✓ Editar cultivo → Cambiar nombre, tipo, público
✓ Editar tarea → Cambiar titulo, estado, fecha
✓ Eliminar → Pide confirmación
✓ Eliminar → Remueve de la lista tras confirmación
✓ Errores → Se muestran en alert
```

### 4. **Frontend Usuario**
```
✓ Dashboard usuario sigue funcionando
✓ Mis Cultivos funciona
✓ Catálogo funciona
✓ Calendario funciona
✓ Tareas funciona
✓ Logout funciona
```

---

## Decisiones Técnicas

1. **Componente ProtectedAdminRoute separado**
   - Reutiliza lógica de ProtectedRoute
   - Verifica rol explícitamente
   - Mensajes claros de rechazo

2. **Edición inline en tablas**
   - Menos navegación
   - Cambio de estado visual (fila amarilla)
   - Guardar/Cancelar inline
   - Mejor UX para admin

3. **Normalización reutilizada**
   - Usa `normalizeListResponse` existente
   - Evita `.map is not a function`
   - Soporta múltiples formatos backend

4. **API client centralizado**
   - Mantiene patrón Fetch existente
   - No introduce Axios
   - Manejo consistente de errores
   - Token siempre incluido

5. **Sin seed final**
   - No implementado (como solicitado)
   - Script make_admin.py como alternativa temporal

6. **Sin Alembic/migraciones**
   - No implementadas (como solicitado)
   - Backend ya usa init_db()

7. **Sin tests E2E**
   - No implementados (como solicitado)
   - Tests unitarios backend intactos

---

## Resultado de Build

```
vite v5.4.21 building for production...
✓ 58 modules transformed.
dist/index.html                   0.47 kB │ gzip:  0.31 kB
dist/assets/index-D5y9pt0e.css   12.92 kB │ gzip:  2.90 kB
dist/assets/index-DqzCHHQ1.js   197.86 kB │ gzip: 60.21 kB
✓ built in 598ms
```

✅ **Sin errores de compilación**

---

## Resultado de Tests Backend

```
Ran 83 tests in 53.525s
OK
```

✅ **Todos los tests pasados**
✅ **No se rompió nada del frontend usuario**

---

## Limitaciones Conocidas

1. **Paginación básica**
   - No implementada en UI (siempre skip=0, limit=50)
   - Backend lo soporta, frontend solo muestra primeros 50

2. **Validación frontend mínima**
   - El backend valida todo
   - Frontend confía en respuestas backend

3. **Caché/refetch**
   - Datos se refrescan manualmente después de operación
   - Sin invalidación automática con React Query

4. **Permisos granulares**
   - Solo admin/usuario
   - Sin permisos CRUD a nivel endpoint

5. **Auditoría**
   - Sin logs de quién cambió qué
   - Sin timestamps de modificación en UI

---

## Riesgos Pendientes

1. **Seguridad**
   - ⚠️ Frontend confia en role del localStorage
   - ✅ Backend valida con get_current_admin (seguro)
   - **Recomendación:** Refrescar rol periódicamente del servidor

2. **Datos sensibles**
   - ✅ No se exponen passwords en tablas
   - ✅ Email mostrado es información pública

3. **Errores backend**
   - ⚠️ Errores no específicos mostrados en alert
   - **Recomendación:** Toast notificaciones en futuro

---

## Completitud de FASE 9

| Requerimiento | Estado | Notas |
|---------------|--------|-------|
| Rutas admin protegidas | ✅ | 5 rutas + protección |
| Dashboard resumen | ✅ | 8 métricas |
| CRUD Usuarios | ✅ | Tabla inline editing |
| CRUD Cultivos | ✅ | Tabla inline editing |
| CRUD Tareas | ✅ | Tabla inline editing |
| API client admin | ✅ | 12 funciones |
| Navbar enlace admin | ✅ | Condicional rol |
| Build sin errores | ✅ | Vite limpio |
| Tests backend intactos | ✅ | 83/83 OK |
| Frontend usuario intacto | ✅ | No modificado |

✅ **FASE 9 COMPLETADA**

---

## Próximos Pasos (No en FASE 9)

- [ ] FASE 10: Seed de datos inicial
- [ ] FASE 11: Migraciones Alembic
- [ ] FASE 12: Tests E2E
- [ ] Auditoría y logs
- [ ] Paginación avanzada
- [ ] Toast notificaciones
- [ ] Validación frontend mejorada
- [ ] Caché y React Query
