# DEMO_GUIDE - Guía de Demostración AgroManager

**Objetivo:** Guía paso a paso para ejecutar y demostrar AgroManager ante tribunal/tutor.

**Tiempo estimado:** 15-20 minutos

---

## Fase 0: Preparación (5 minutos)

### 1. Verificar requisitos
```bash
# Verificar Python
python --version        # Debe ser 3.10+

# Verificar Node
node --version         # Debe ser 16+
npm --version          # Debe ser 7+

# Verificar Git (opcional)
git --version
```

### 2. Navegar al proyecto
```bash
cd tfg-claude
```

### 3. Activar virtual environment
```bash
# Windows PowerShell
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

---

## Fase 1: Inicializar Datos (2 minutos)

### Ejecutar seed de datos demo
```bash
python scripts/seed_demo.py
```

**Output esperado:**
```
[INFO] ============================================================
[INFO] Iniciando FASE 10: Seed de Datos Demo
[INFO] ============================================================
[INFO] Verificando usuario admin...
[WARN] Usuario admin ya existe (ID: 3)
[INFO] Verificando usuario demo...
[WARN] Usuario demo ya existe (ID: 4)
[INFO] Creando cultivos de ejemplo...
...
[OK] Seed completado exitosamente
[OK] ============================================================
[INFO] Admin creado/verificado: admin@test.com
[INFO] Usuario demo creado/verificado: user@test.com
[INFO] Cultivos creados/verificados: 7
[INFO] Calendarios creados/verificados: 3
[INFO] Tareas creadas/verificadas: 4

Puedes ahora:
  1. Login como admin: admin@test.com / admin123
  2. Login como user: user@test.com / user123
  3. Ver cultivos, tareas y calendarios en el frontend
```

---

## Fase 2: Ejecutar Backend (1 minuto)

```bash
python -m uvicorn app.main:app --reload
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Verificar API disponible:**
- Abrir http://localhost:8000/docs en navegador
- Ver todos los endpoints del API
- Swagger UI interactivo

---

## Fase 3: Ejecutar Frontend (1 minuto)

**Abrir nueva terminal:**

```bash
cd tfg-claude/frontend
npm run dev
```

**Output esperado:**
```
  VITE v5.4.21  ready in 234 ms

  ➜  Local:   http://127.0.0.1:5173/
  ➜  press h + enter to show help
```

**Acceder a:**
- Abrir http://localhost:5173 en navegador
- Debe mostrar página de login

---

## Fase 4: Demostración de Funcionalidades (10 minutos)

### A. Rol de Usuario Normal (user@test.com)

#### 1. Login como usuario normal
- URL: http://localhost:5173/login
- Email: `user@test.com`
- Password: `user123`
- Click en "Iniciar Sesión"
- **Resultado esperado:** Redirige a dashboard del usuario

#### 2. Ver Dashboard
- Muestra:
  - Bienvenida "Usuario Demo"
  - Navbar con link "🌱 AgroManager"
  - **NO muestra** link "🔧 Admin" (solo para admin)
- Funcionalidades accesibles:
  - Ver perfil de usuario
  - Ver cultivos (5 públicos + 2 personales)
  - Ver tareas (4 tareas demo)
  - Ver calendarios de siembra

#### 3. Ver Cultivos Disponibles
- Click en "Mis Cultivos" o similar (ver UI)
- Debe mostrar:
  - **Cultivos Personales (2):**
    - Mi Tomate
    - Mi Lechuga
  - **Cultivos Públicos (5):**
    - Tomate
    - Lechuga
    - Zanahoria
    - Pimiento
    - Fresa
- Cada cultivo muestra:
  - Nombre, tipo, descripción
  - Datos de riego (frecuencia: 3 días)
  - Requisitos ambientales (temp: 15-25°C)

#### 4. Ver Tareas
- Debe mostrar 4 tareas:
  - Regar tomates (PENDING) - mañana
  - Revisar plagas (PENDING) - +2 días
  - Preparar abono (COMPLETED) - hoy
  - Trasplante de pepino (PENDING) - +7 días
- Filtrar por estado (pending/completed)

#### 5. Ver Calendarios de Siembra
- Mostrar 3 calendarios:
  - Tomate: siembra Mar-Abr, cosecha Jul-Oct
  - Lechuga: siembra Feb-Mar, cosecha Abr-May
  - Zanahoria: siembra Abr-May, cosecha Ago-Nov
- Cada calendario con fechas de siembra, trasplante, cosecha

#### 6. Logout
- Click en perfil → Logout
- Redirige a login

### B. Rol de Administrador (admin@test.com)

#### 1. Login como admin
- URL: http://localhost:5173/login
- Email: `admin@test.com`
- Password: `admin123`
- Click en "Iniciar Sesión"
- **Resultado esperado:** Redirige a dashboard del admin

#### 2. Ver Admin Link en Navbar
- **Debe mostrar:** Link "🔧 Admin" en navbar
- Click en "🔧 Admin"
- Redirige a /admin/dashboard

#### 3. Panel Admin - Dashboard
- Muestra 8 métricas:
  - Total de usuarios: 2
  - Total de cultivos: 7
  - Cultivos públicos: 5
  - Total de tareas: 4
  - Tareas pendientes: 3
  - Tareas completadas: 1
  - Calendarios activos: 3
  - Calendarios completados: 0
- Layout limpio con cards

#### 4. Panel Admin - Gestión de Usuarios
- Acceder a /admin/users
- Ver tabla de usuarios:
  - admin@test.com (ADMIN, activo)
  - user@test.com (USER, activo)
- Funcionalidades:
  - Click en "Editar" → Editar email, nombre, rol, estado
  - Click en "Eliminar" → Confirmar eliminación
  - Cambiar email de un usuario
  - **Verificación:** Los cambios persisten en BD

#### 5. Panel Admin - Gestión de Cultivos
- Acceder a /admin/crops
- Ver tabla de 7 cultivos:
  - Los 5 públicos (Tomate, Lechuga, Zanahoria, Pimiento, Fresa)
  - Los 2 personales (Mi Tomate, Mi Lechuga)
- Funcionalidades:
  - Editar nombre, tipo, descripción, estado público/privado
  - Eliminar cultivo
  - **Verificación:** Cambios se reflejan inmediatamente

#### 6. Panel Admin - Gestión de Tareas
- Acceder a /admin/tasks
- Ver tabla de 4 tareas:
  - Todas las tareas del usuario demo
- Funcionalidades:
  - Editar título, descripción, estado (dropdown: pending/completed)
  - Editar fecha de vencimiento (input date)
  - Eliminar tarea
  - **Verificación:** Cambios se reflejan en dashboard de usuario

#### 7. Logout
- Click en perfil → Logout
- Redirige a login

---

## Fase 5: Validación Técnica (2 minutos)

### Backend Tests
```bash
# En terminal con backend detenido
python -m unittest discover -s tests -p "test*.py" -v
```

**Output esperado:**
```
Ran 106 tests in 60.570s
OK
```

- ✅ 83 tests originales
- ✅ 17 tests de seed
- ✅ 6 tests adicionales
- ✅ 0 fallos

### Frontend Build
```bash
cd frontend
npm run build
```

**Output esperado:**
```
vite v5.4.21 building for production...
✓ 58 modules transformed.
✓ built in 569ms
```

- ✅ 0 errores
- ✅ Build time: <1s
- ✅ Directorio `dist/` generado

---

## Casos de Uso Clave para Demostración

### 1. Flow de Login y Autenticación
- ✅ Registro de nuevo usuario
- ✅ Login exitoso
- ✅ Token JWT en localStorage
- ✅ Logout borra token
- ✅ Acceso a ruta protegida sin token → Error

### 2. Control de Roles (RBAC)
- ✅ Usuario normal NO ve panel admin
- ✅ Admin VE panel admin
- ✅ Usuario normal solo puede eliminar su cuenta
- ✅ Admin puede gestionar usuarios de otros

### 3. Gestión de Cultivos
- ✅ Usuario ve sus cultivos personales
- ✅ Usuario ve catálogo público
- ✅ Admin puede editar cualquier cultivo
- ✅ Cada cultivo tiene datos de riego y ambientales
- ✅ Cultivos públicos vs privados funcionan correctamente

### 4. Tareas y Calendarios
- ✅ Usuario ve sus tareas
- ✅ Tareas con estados (pending/completed)
- ✅ Calendarios de siembra con fechas realistas
- ✅ Admin puede editar tareas de cualquier usuario

### 5. Idempotencia del Seed
- ✅ Ejecutar `seed_demo.py` dos veces
- ✅ Verificar que NO hay duplicados
- ✅ Conteos de usuarios, cultivos, tareas permanecen igual

---

## Troubleshooting

### Backend no inicia
```bash
# Verificar venv está activado
which python    # Debe mostrar ruta con venv

# Reinstalar dependencias
pip install -r requirements.txt

# Borrar BD corrupta
rm app.db

# Reintentar seed
python scripts/seed_demo.py

# Ejecutar backend nuevamente
python -m uvicorn app.main:app --reload
```

### Frontend no carga
```bash
# Limpiar cache y reinstalar
cd frontend
rm -rf node_modules package-lock.json
npm install

# Build fallido
npm run build

# Verificar http://localhost:5173 está accesible
```

### Credenciales no funcionan
```bash
# Verificar BD tiene datos
python scripts/seed_demo.py --reset
python scripts/seed_demo.py

# Verificar backend está corriendo
curl http://localhost:8000/docs

# Verificar frontend conecta a backend
# Abrir DevTools (F12) → Network → Verificar requests a /auth/login
```

### Admin role no se detecta
- Verificar en DevTools → Application → LocalStorage
- Debe estar `user` con `role: "admin"`
- Si no está, hacer login de nuevo

---

## Puntos Clave para Presentar

1. **Arquitectura moderna:** FastAPI + React + SQLAlchemy
2. **Seguridad:** JWT + bcrypt + RBAC
3. **Testing robustez:** 106 tests pasando
4. **Datos realistas:** Seed idempotente con cultivos agrícolas
5. **Interfaz intuitiva:** Admin panel funcional
6. **Buenas prácticas:** Separación de capas, validación, documentación

---

## Notas Finales

- ✅ Proyecto está en **estado de producción local**
- ✅ Base de datos SQLite para desarrollo
- ✅ API totalmente funcional y documentada
- ✅ Frontend responsivo y moderno
- ✅ Listo para demostración ante tribunal/tutor
- ✅ Preparado para migración a PostgreSQL en producción

**Duración total demo:** 15-20 minutos  
**Requerimientos:** Solo navegador, Python, Node.js  
**Complejidad:** Baja (todo es automático después del setup)
