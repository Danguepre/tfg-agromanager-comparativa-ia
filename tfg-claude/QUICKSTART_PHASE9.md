# QUICKSTART PHASE 9: Panel Admin Visual

**FASE 9 COMPLETADA** ✅

Guía rápida para probar el panel admin recién implementado.

---

## 1️⃣ Verificar Build (debe estar limpio)

```bash
cd frontend
npm.cmd run build
```

✅ **Esperado:**
```
✓ built in 573ms
dist/index.html                   0.47 kB
dist/assets/index-D5y9pt0e.css   12.92 kB
dist/assets/index-DqzCHHQ1.js   197.86 kB
```

---

## 2️⃣ Verificar Tests (todos deben pasar)

```bash
python -m unittest discover -s tests -p "test*.py"
```

✅ **Esperado:**
```
Ran 83 tests in 54.402s
OK
```

---

## 3️⃣ Crear Usuario Admin para Prueba

**Opción A: Script helper (recomendado)**
```bash
python scripts/make_admin.py 1
```

**Opción B: SQL directo**
```powershell
python
```
```python
from app.database import SessionLocal
from app.models.user import User, UserRole

db = SessionLocal()
user = db.query(User).filter(User.id == 1).first()
if user:
    user.role = UserRole.ADMIN
    db.commit()
    print(f"✅ {user.email} es ahora admin")
else:
    print("❌ Usuario 1 no existe")
db.close()
```

---

## 4️⃣ Iniciar Backend + Frontend

**Terminal 1: Backend**
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2: Frontend**
```bash
cd frontend
npm.cmd run dev
```

Accede a: `http://localhost:5173`

---

## 5️⃣ Pruebas Manuales

### A. Usuario Normal ❌ Sin Admin
```
1. Click Register → Crear usuario nuevo (email: user@test.com, pwd: Test123!)
2. Login con user@test.com
3. Verificar: NO ves "🔧 Admin" en navbar
4. Intentar acceso: http://localhost:5173/admin
5. Esperado: Mensaje "Acceso Denegado"
6. Verificar: Dashboard usuario sigue funcionando
```

### B. Usuario Admin ✅ Con Admin
```
1. Login con usuario admin (ID 1 convertido anteriormente)
2. Verificar: VES "🔧 Admin" en navbar
3. Click en "🔧 Admin" → va a /admin/dashboard
4. Verificar: Dashboard carga con 8 tarjetas (usuarios, cultivos, tareas, etc)
```

### C. Operaciones Admin
```
Usuarios:
  1. Click "🔧 Admin" → Users
  2. Tabla muestra todos los usuarios
  3. Click ✏️ en una fila → Campos editables (amarillo)
  4. Cambiar email → Click "Guardar"
  5. Verificar: Email actualizado en backend
  6. Click 🗑️ → Pide confirmación → Eliminar

Cultivos:
  1. Click "🔧 Admin" → Crops
  2. Tabla muestra todos los cultivos globales
  3. Click ✏️ → Editar name, tipo, visibilidad
  4. Cambios inmediatos

Tareas:
  1. Click "🔧 Admin" → Tasks
  2. Tabla muestra todas las tareas
  3. Click ✏️ → Editar titulo, status, fecha
  4. Dropdown: pending/completed
  5. Date picker para fecha vencimiento
```

### D. Verificar Usuario Normal No Afectado
```
1. Logout de admin
2. Login con usuario normal
3. Verificar:
   - Dashboard usuario funciona
   - "Mis Cultivos" funciona
   - Catálogo funciona
   - Calendario funciona
   - Tareas usuario funciona
   - No ves cambios admin realizados (o sí, si son públicos)
```

---

## 📁 Archivos Creados/Modificados

**Creados:**
- ✅ `frontend/src/components/ProtectedAdminRoute.jsx`
- ✅ `frontend/src/pages/AdminDashboard.jsx`
- ✅ `frontend/src/pages/AdminUsers.jsx`
- ✅ `frontend/src/pages/AdminCrops.jsx`
- ✅ `frontend/src/pages/AdminTasks.jsx`
- ✅ `frontend/src/pages/AdminPages.css`
- ✅ `scripts/make_admin.py`
- ✅ `PHASE9_IMPLEMENTATION.md` (documentación)

**Modificados:**
- ✅ `frontend/src/App.jsx` (5 rutas admin)
- ✅ `frontend/src/api/api.js` (12 funciones admin)
- ✅ `frontend/src/components/Navbar.jsx` (enlace admin condicional)

---

## 🔐 Protección Admin

✅ **Frontend:**
- ProtectedAdminRoute verifica `user.role === 'admin'`
- Enlace "Admin" en navbar solo visible para admins
- Sin token → Redirige a login
- Sin admin → "Acceso Denegado"

✅ **Backend:**
- Todos endpoints `/admin` usan `get_current_admin`
- Retorna 403 si no es admin
- Retorna 401 si sin token

✅ **Base de datos:**
- User model tiene campo `role` (enum: admin/user)
- Default: user
- Script make_admin.py permite conversión segura

---

## 📊 Endpoints Admin Consumidos

| GET | Dashboard | `GET /admin/summary` |
|-----|-----------|-----------------|
| GET | Usuarios | `GET /admin/users?skip=0&limit=50` |
| PATCH | Usuarios | `PATCH /admin/users/{id}` |
| DELETE | Usuarios | `DELETE /admin/users/{id}` |
| GET | Cultivos | `GET /admin/crops?skip=0&limit=50` |
| PATCH | Cultivos | `PATCH /admin/crops/{id}` |
| DELETE | Cultivos | `DELETE /admin/crops/{id}` |
| GET | Tareas | `GET /admin/tasks?skip=0&limit=50` |
| PATCH | Tareas | `PATCH /admin/tasks/{id}` |
| DELETE | Tareas | `DELETE /admin/tasks/{id}` |

---

## ❌ Troubleshooting

### "Acceso Denegado" para admin
→ User no tiene role=admin en DB
→ Ejecuta: `python scripts/make_admin.py 1`

### Admin link no aparece en navbar
→ Recarga página: Ctrl+Shift+R (hard refresh)
→ O logout/login

### Dashboard vacío / sin datos
→ Backend no está corriendo en http://127.0.0.1:8000
→ Verifica terminal backend

### Errores en consola
→ Abre DevTools (F12)
→ Tab "Console"
→ Nota el error exacto
→ Verifica logs backend

### Cambios no guardan
→ 401/403 error → Verify token válido
→ Refresca tabla manualmente

---

## ✅ Validación Final

```
✓ Build sin errores: npm run build → 573ms OK
✓ Tests sin regressions: 83/83 OK
✓ Admin routes: /admin, /admin/dashboard, /admin/users, /admin/crops, /admin/tasks
✓ Admin protection: Solo role=admin accede
✓ CRUD usuarios: ✏️ Editar, 🗑️ Eliminar
✓ CRUD cultivos: ✏️ Editar, 🗑️ Eliminar
✓ CRUD tareas: ✏️ Editar, 🗑️ Eliminar
✓ Usuario normal: No afectado, sigue funcionando
```

---

## 🚀 Próximas Fases

- **FASE 10:** Seed de datos inicial
- **FASE 11:** Migraciones Alembic
- **FASE 12:** Tests E2E
