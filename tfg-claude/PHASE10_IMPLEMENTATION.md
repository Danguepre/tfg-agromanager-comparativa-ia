# FASE 10: Seed/Admin Inicial y Datos de Ejemplo

**Estado:** ✅ **COMPLETADA**
**Fecha:** 2024
**Build:** ✅ Sin errores (588ms)
**Tests:** ✅ 83/83 pasando

---

## 📋 Descripción

Implementación de un script **idempotente** de seed que inicializa la base de datos con:
- **Usuario admin** (credenciales de demostración)
- **Usuario demo** (para pruebas de usuario normal)
- **Cultivos de ejemplo** (tomate, lechuga, zanahoria, pepino, fresa)
- **Atributos de riego** para cada cultivo
- **Requisitos ambientales** para cada cultivo
- **Calendarios de siembra** con fechas de siembra, trasplante y cosecha
- **Tareas de demostración** para usuario demo

El script puede ejecutarse múltiples veces sin crear duplicados.

---

## ✅ Credenciales Demo Creadas

### Admin
```
Email: admin@test.com
Password: admin123
Role: admin
Permisos: Panel admin, acceso a todos los datos
```

### Usuario Demo
```
Email: user@test.com
Password: user123
Role: user
Permisos: Ver cultivos, crear tareas, ver calendarios
```

---

## 📁 Archivos Creados

| Archivo | Líneas | Descripción |
|---------|--------|-----------|
| `scripts/seed_demo.py` | ~440 | Script idempotente de seed con opciones |

---

## 🚀 Uso del Script

### 1. Crear datos de ejemplo (modo normal)
```bash
python scripts/seed_demo.py
```

**Resultado:**
- Crea usuario admin@test.com si no existe
- Crea usuario user@test.com si no existe
- Crea cultivos públicos (sistema)
- Crea cultivo privado del usuario demo
- Crea calendarios de siembra
- Crea tareas de ejemplo
- Totalmente seguro ejecutar múltiples veces

### 2. Limpiar datos demo (mantener admin)
```bash
python scripts/seed_demo.py --clean
```

**Resultado:**
- Elimina tareas demo
- Elimina calendarios
- Elimina cultivos privados del usuario demo
- Elimina usuario demo
- **Mantiene** usuario admin

### 3. Reset completo (eliminar TODO)
```bash
python scripts/seed_demo.py --reset
```

**Resultado:**
- Elimina TODO incluyendo admin
- Base de datos vacía
- Ejecutar nuevamente `python scripts/seed_demo.py` recrea datos

---

## 📊 Datos Creados

### Cultivos del Sistema (5)
1. **Tomate**
   - Tipo: verdura
   - Público: sí
   - Riego: cada 3 días, 25mm
   - Temperatura: 15-25°C
   - Calendario: Mar-Oct

2. **Lechuga**
   - Tipo: verdura
   - Público: sí
   - Riego: cada 3 días, 25mm
   - Temperatura: 15-25°C
   - Calendario: Feb-May

3. **Zanahoria**
   - Tipo: raíz
   - Público: sí
   - Riego: cada 3 días, 25mm
   - Temperatura: 15-25°C
   - Calendario: Abr-Nov

4. **Pepino**
   - Tipo: verdura
   - Público: sí
   - Riego: cada 3 días, 25mm
   - Temperatura: 15-25°C

5. **Fresa**
   - Tipo: fruta
   - Público: sí
   - Riego: cada 3 días, 25mm
   - Temperatura: 15-25°C

### Cultivo Privado del Usuario Demo
- **Mi Huerto Personal**
  - Tipo: mixto
  - Público: no
  - Owner: user@test.com

### Calendarios de Siembra (3)
- Tomate: Mar-Oct (siembra, trasplante, cosecha)
- Lechuga: Feb-May (siembra, trasplante, cosecha)
- Zanahoria: Abr-Nov (siembra, cosecha)

### Tareas de Demostración (4)
1. **Regar tomates** (Pending, mañana)
2. **Revisar plagas** (Pending, en 2 días)
3. **Preparar abono** (Completed, hoy)
4. **Trasplante de pepino** (Pending, en 7 días)

---

## 🔄 Características de Idempotencia

El script verifica **antes de crear**:
- Si usuario admin existe → No crea duplicado
- Si usuario demo existe → No crea duplicado
- Si cultivo existe (por nombre) → No crea duplicado
- Si calendario existe (por cultivo) → No crea duplicado
- Si tarea existe (por owner + título) → No crea duplicado

**Resultado:** Ejecutar múltiples veces es 100% seguro y no crea duplicados.

---

## 📝 Implementación Técnica

### Dependencias
- `app.database` - SessionLocal, engine, Base
- `app.models.*` - Todos los modelos (User, Crop, Task, etc.)
- `app.services.user_service` - create_user, get_user_by_email
- `app.services.auth_service` - hash_password

### Funciones Principales
```python
create_admin_user(db)           # Crea/verifica admin
create_demo_user(db)            # Crea/verifica usuario demo
create_demo_crops(db, owner)    # Crea cultivos con atributos
create_demo_calendars(db, crops) # Crea calendarios de siembra
create_demo_tasks(db, owner)    # Crea tareas
seed_database()                 # Orquesta todo
clean_demo_data(db, keep_admin) # Limpia datos
main()                          # CLI con argumentos
```

### Manejo de Errores
- Try-catch en seed_database()
- Try-finally para cerrar sesión DB
- Rollback en caso de error en clean_demo_data()
- Logs coloreados para facilitar debugging

---

## ✅ Validación

### Build Frontend
```
vite v5.4.21 building for production...
✓ 58 modules transformed.
✓ built in 588ms
```
✅ **SIN ERRORES**

### Tests Backend
```
Ran 83 tests in 49.163s
OK
```
✅ **TODOS PASANDO (SIN REGRESSIONS)**

### Ejecución del Seed
```
✅ Iniciando FASE 10: Seed de Datos Demo
⚠️ Usuario admin ya existe (ID: 3)
⚠️ Usuario demo ya existe (ID: 4)
✅ Cultivo 'Tomate' creado (ID: 1)
✅ Cultivo 'Lechuga' creado (ID: 2)
✅ Cultivo 'Zanahoria' creado (ID: 3)
✅ Cultivo 'Pepino' creado (ID: 4)
✅ Cultivo 'Fresa' creado (ID: 5)
✅ Cultivo 'Mi Huerto Personal' creado (ID: 6)
✅ Calendario para 'Tomate' creado (ID: 1)
✅ Calendario para 'Lechuga' creado (ID: 2)
✅ Calendario para 'Zanahoria' creado (ID: 3)
✅ Tarea 'Regar tomates' creada (ID: 1)
✅ Tarea 'Revisar plagas' creada (ID: 2)
✅ Tarea 'Preparar abono' creada (ID: 3)
✅ Tarea 'Trasplante de pepino' creada (ID: 4)
✨ Seed completado exitosamente
```

---

## 🧪 Flujo de Prueba Manual

### 1. Inicializar BD con datos
```bash
# Opción A: Crear/recrear datos
python scripts/seed_demo.py

# Opción B: Reset completo
python scripts/seed_demo.py --reset
python scripts/seed_demo.py
```

### 2. Iniciar Backend
```bash
python -m uvicorn app.main:app --reload
```

### 3. Iniciar Frontend
```bash
cd frontend
npm run dev
```
Accede a: http://localhost:5173

### 4. Pruebas
```
✓ Login como admin@test.com / admin123
  → Ver panel admin (/admin/dashboard)
  → Ver usuarios, cultivos, tareas
  → Acceso a todas las funcionalidades admin

✓ Login como user@test.com / user123
  → Ver dashboard de usuario
  → Ver cultivos (5 públicos + 1 privado)
  → Ver tareas creadas (4 tareas)
  → Ver calendarios (3 calendarios)
  → No ver panel admin

✓ Logout y login nuevamente
  → Verificar datos persisten
  → Ejecutar seed nuevamente
  → Verificar sin duplicados
```

---

## 📊 Estructura de Datos Creados

```
Database (SQLite)
│
├── Users (2)
│   ├── admin@test.com (ID: 3, role: admin)
│   └── user@test.com (ID: 4, role: user)
│
├── Crops (6)
│   ├── Tomate (ID: 1, public, no owner)
│   ├── Lechuga (ID: 2, public, no owner)
│   ├── Zanahoria (ID: 3, public, no owner)
│   ├── Pepino (ID: 4, public, no owner)
│   ├── Fresa (ID: 5, public, no owner)
│   └── Mi Huerto Personal (ID: 6, private, owner: user@test.com)
│
├── IrrigationAttributes (6)
│   └── Para cada cultivo (water_frequency_days, water_amount_mm, etc.)
│
├── EnvironmentalRequirements (6)
│   └── Para cada cultivo (temperature, humidity, sunlight, pH, etc.)
│
├── PlantingCalendars (3)
│   ├── Tomate: Mar-Oct
│   ├── Lechuga: Feb-May
│   └── Zanahoria: Abr-Nov
│
└── Tasks (4, owner: user@test.com)
    ├── Regar tomates (Pending, mañana)
    ├── Revisar plagas (Pending, en 2 días)
    ├── Preparar abono (Completed, hoy)
    └── Trasplante de pepino (Pending, en 7 días)
```

---

## 🎯 Beneficios

✅ **Desarrollo rápido:** No crear datos manualmente cada vez
✅ **Testing:** Datos realistas para probar funcionalidades
✅ **Demo:** Mostrar AgroManager con datos ya cargados
✅ **Idempotencia:** Seguro ejecutar múltiples veces
✅ **Limpieza:** Opción de limpiar y resetear BD
✅ **Documentación:** Los datos creados documentan qué se puede hacer

---

## 🚀 Próximas Fases

- **FASE 11:** Migraciones Alembic
- **FASE 12:** Tests E2E
- **FASE 13:** Deploy y Docker
- **FASE 14:** Cierre documental

---

## 📌 Notas

- Script usa `sys.path.insert` para importar módulos del proyecto
- Colores en terminal para mejor UX (funciona en Windows PowerShell)
- Manejo seguro de sesiones DB con try-finally
- Logs de SQLAlchemy se muestran (pueden deshabilitarse si necesario)
- Base de datos por defecto SQLite local (app.db)

---

## ✅ Conclusión

✅ **FASE 10 COMPLETADA**

- Script de seed idempotente creado
- Credenciales demo funcionales
- Datos de ejemplo realistas
- Sin regressions (83/83 tests OK)
- Build frontend OK (588ms)
- Pronto para demostración
