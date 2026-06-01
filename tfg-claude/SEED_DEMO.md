# SEED_DEMO.md

**FASE 10: Seed/Admin Inicial y Datos de Ejemplo**

---

## 📋 Descripción General

Script idempotente que inicializa la base de datos con datos de ejemplo para testing, desarrollo y demostración.

### Característica Clave: Idempotencia
El script puede ejecutarse múltiples veces de forma segura. La segunda ejecución detecta datos existentes y no crea duplicados.

---

## 🎯 Datos Creados

### Usuarios (2)

| Email | Password | Rol | Estado |
|-------|----------|-----|--------|
| `admin@test.com` | `admin123` | ADMIN | activo |
| `user@test.com` | `user123` | USER | activo |

**Seguridad:** Las contraseñas se hashean con bcrypt.

### Cultivos Públicos (5)

Sistema de cultivos compartidos sin propietario:

| Nombre | Tipo | Descripción |
|--------|------|-----------|
| Tomate | verdura | Cultivo de tomates rojo intenso |
| Lechuga | verdura | Lechuga fresca de hoja larga |
| Zanahoria | raíz | Zanahoria naranja dulce |
| Pimiento | verdura | Pimiento colorido para ensaladas |
| Fresa | fruta | Fresas dulces para postre |

### Cultivos Personales (2)

Cultivos privados del usuario demo:

| Nombre | Tipo | Propietario | Privado |
|--------|------|-------------|---------|
| Mi Tomate | verdura | user@test.com | sí |
| Mi Lechuga | verdura | user@test.com | sí |

### Atributos de Riego (7)

Cada cultivo (público y privado) incluye:
- Frecuencia de riego: 3 días
- Cantidad de agua: 25mm
- Tipo: Riego por goteo
- Notas: "Aumentar en verano"

### Requisitos Ambientales (7)

Cada cultivo (público y privado) incluye:
- **Temperatura:** 15-25°C
- **Humedad:** 50-80%
- **Luz solar:** 6 horas/día
- **Suelo:** Fértil bien drenado
- **pH:** 6.0-7.0

### Calendarios de Siembra (3)

| Cultivo | Siembra | Trasplante | Cosecha |
|---------|---------|------------|---------|
| Tomate | Mar 1-Abr 15 | Abr 20-May 10 | Jul 1-Oct 31 |
| Lechuga | Feb 1-Mar 31 | Mar 15-Abr 15 | Abr 1-May 31 |
| Zanahoria | Abr 1-May 31 | — | Ago 1-Nov 30 |

### Tareas para Usuario Demo (4)

| Título | Estado | Descripción | Vencimiento |
|--------|--------|-----------|-----------|
| Regar tomates | PENDING | Riego matutino de 5 litros | Mañana |
| Revisar plagas | PENDING | Inspeccionar hojas de lechuga | +2 días |
| Preparar abono | COMPLETED | Preparar mezcla de abono | Hoy |
| Trasplante de pepino | PENDING | Trasplantar al huerto principal | +7 días |

---

## 🚀 Cómo Usar

### Crear/Actualizar Datos Demo
```bash
cd tfg-claude
python scripts/seed_demo.py
```

**Output esperado:**
```
ℹ️  Iniciando FASE 10: Seed de Datos Demo
⚠️  Usuario admin ya existe (ID: 3)
⚠️  Usuario demo ya existe (ID: 4)
✅ Cultivo 'Tomate' creado (ID: 1)
✅ Cultivo 'Lechuga' creado (ID: 2)
✅ Cultivo 'Zanahoria' creado (ID: 3)
✅ Cultivo 'Pimiento' creado (ID: 4)
✅ Cultivo 'Fresa' creado (ID: 5)
✅ Cultivo 'Mi Tomate' creado (ID: 6)
✅ Cultivo 'Mi Lechuga' creado (ID: 7)
✅ Calendario para 'Tomate' creado (ID: 1)
✅ Calendario para 'Lechuga' creado (ID: 2)
✅ Calendario para 'Zanahoria' creado (ID: 3)
✅ Tarea 'Regar tomates' creada (ID: 1)
✅ Tarea 'Revisar plagas' creada (ID: 2)
✅ Tarea 'Preparar abono' creada (ID: 3)
✅ Tarea 'Trasplante de pepino' creada (ID: 4)
✨ Seed completado exitosamente
```

### Limpiar Datos Demo (Mantener Admin)
```bash
python scripts/seed_demo.py --clean
```

Elimina:
- Usuario demo (user@test.com)
- Cultivos privados (Mi Tomate, Mi Lechuga)
- Calendarios
- Tareas

Mantiene:
- Usuario admin (admin@test.com)

### Reset Completo
```bash
python scripts/seed_demo.py --reset
```

Elimina TODO incluyendo admin. Luego ejecuta nuevamente para recrear desde cero.

---

## 🧪 Testing

### Suite de Tests: `tests/test_seed_demo.py`

Casos de test incluidos:

✅ **Usuario Admin**
- Seed crea usuario admin
- Contraseña hasheada correctamente
- Admin puede login con credenciales

✅ **Usuario Demo**
- Seed crea usuario demo
- Contraseña hasheada correctamente
- Usuario demo puede login con credenciales

✅ **Cultivos Públicos**
- Seed crea 5 cultivos públicos
- Nombres correctos (Tomate, Lechuga, Zanahoria, Pimiento, Fresa)
- Sin propietario
- Con atributos de riego
- Con requisitos ambientales

✅ **Cultivos Personales**
- Seed crea 2 cultivos personales
- Nombres correctos (Mi Tomate, Mi Lechuga)
- Pertenecen a usuario demo
- Con atributos de riego y ambientales

✅ **Calendarios**
- Seed crea calendarios
- Tienen rangos de fechas válidos

✅ **Tareas**
- Seed crea tareas para usuario demo
- Tareas tienen estados pending/completed

✅ **Idempotencia**
- Segunda ejecución no duplica usuarios
- Segunda ejecución no duplica cultivos
- Segunda ejecución no duplica tareas
- Workflow completo es idempotente

### Ejecutar Tests
```bash
python -m unittest discover -s tests -p "test*.py" -v
```

Resultado esperado: **83 tests OK** (incluidos test_seed_demo.py)

---

## 🔐 Seguridad

| Aspecto | Detalle |
|--------|--------|
| **Contraseñas** | Hasheadas con bcrypt |
| **Uso** | Solo desarrollo/testing, NO producción |
| **Credenciales demo** | Documentadas en código, cambiar en prod |
| **Sin secretos** | No contiene API keys, tokens, o datos sensibles |

---

## 📁 Archivos

| Archivo | Descripción |
|---------|-----------|
| `scripts/seed_demo.py` | Script principal del seed (440 líneas) |
| `tests/test_seed_demo.py` | Suite de tests (360+ líneas, 17 casos) |
| `SEED_DEMO.md` | Este archivo (documentación) |

---

## 🔄 Idempotencia: Cómo Funciona

Cada función verifica **antes de crear**:

```python
# Ejemplo: crear usuario
existing = get_user_by_email(db, "admin@test.com")
if existing:
    log_warning(f"Usuario admin ya existe (ID: {existing.id})")
    return existing

# Crear solo si no existe
user = create_user(db, ...)
```

**Resultado:** Ejecutar 10 veces = mismo estado final. No hay duplicados.

---

## 📊 Ejemplo de Flujo Completo

### Paso 1: Primer Seed
```bash
python scripts/seed_demo.py
# Crea:
# - 2 usuarios
# - 7 cultivos (5 público + 2 personal)
# - 3 calendarios
# - 4 tareas
# - Riego + requisitos para todos
```

### Paso 2: Verificar en DB
```bash
# Usuarios: 2
# Cultivos: 7
# Calendarios: 3
# Tareas: 4
```

### Paso 3: Ejecutar Seed Nuevamente
```bash
python scripts/seed_demo.py
# Detecta datos existentes, no crea duplicados
```

### Paso 4: Verificar en DB
```bash
# Usuarios: 2 (SIN CAMBIOS)
# Cultivos: 7 (SIN CAMBIOS)
# Calendarios: 3 (SIN CAMBIOS)
# Tareas: 4 (SIN CAMBIOS)
```

---

## 🧪 Workflow de Testing Local

```bash
# 1. Inicializar datos
python scripts/seed_demo.py

# 2. Ejecutar tests backend
python -m unittest discover -s tests -p "test*.py" -v

# 3. Iniciar backend
python -m uvicorn app.main:app --reload

# 4. Iniciar frontend (otra terminal)
cd frontend
npm run dev

# 5. Acceder a http://localhost:5173
# - Login: admin@test.com / admin123
# - Ver panel admin
# - Ver cultivos, tareas, calendarios

# 6. Limpiar entre pruebas
python scripts/seed_demo.py --clean

# 7. Recrear datos
python scripts/seed_demo.py
```

---

## 📋 Validación de FASE 10

| Criterio | Estado | Detalles |
|----------|--------|---------|
| **Script crea admin** | ✅ | admin@test.com con role ADMIN |
| **Script crea usuario** | ✅ | user@test.com con role USER |
| **Admin puede login** | ✅ | Contraseña verificada con bcrypt |
| **Usuario puede login** | ✅ | Contraseña verificada con bcrypt |
| **Passwords hasheadas** | ✅ | Usando bcrypt (no plaintext) |
| **5 cultivos públicos** | ✅ | Tomate, Lechuga, Zanahoria, Pimiento, Fresa |
| **2 cultivos personales** | ✅ | Mi Tomate, Mi Lechuga para user@test.com |
| **Calendarios** | ✅ | 3 calendarios con fechas |
| **Tareas pending/completed** | ✅ | Mix de estados |
| **Idempotente** | ✅ | Sin duplicados en múltiples ejecuciones |
| **Tests creados** | ✅ | 17 casos de test en test_seed_demo.py |
| **83 tests pasando** | ✅ | Sin regressions |
| **Build OK** | ✅ | npm run build sin errores |

---

## 🎉 Conclusión

FASE 10 proporciona un seed robusto, idempotente y bien probado que:
- ✅ Inicializa BD con datos realistas
- ✅ Facilita desarrollo y testing
- ✅ Soporta demostración del sistema
- ✅ Nunca crea duplicados
- ✅ Documentado y testeable

**Próxima fase:** FASE 11 (Migraciones Alembic)
