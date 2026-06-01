# QUICKSTART PHASE 10: Seed y Datos Demo

**FASE 10 COMPLETADA** ✅

Guía rápida para inicializar la BD con datos de ejemplo.

---

## 🎯 Objetivo

Probar AgroManager sin crear usuarios/cultivos/tareas manualmente.

Credenciales demo:
- **Admin:** admin@test.com / admin123
- **User:** user@test.com / user123

---

## 🚀 Inicio Rápido

### 1️⃣ Crear Datos Demo
```bash
cd tfg-claude
python scripts/seed_demo.py
```

**Output esperado:**
```
✅ Iniciando FASE 10: Seed de Datos Demo
⚠️ Usuario admin ya existe (ID: 3)
⚠️ Usuario demo ya existe (ID: 4)
✅ Cultivo 'Tomate' creado (ID: 1)
✅ Cultivo 'Lechuga' creado (ID: 2)
... (más cultivos)
✅ Calendarios creados
✅ Tareas creadas
✨ Seed completado exitosamente
```

### 2️⃣ Iniciar Backend
```bash
python -m uvicorn app.main:app --reload
```

Backend en: http://localhost:8000
Docs API: http://localhost:8000/docs

### 3️⃣ Iniciar Frontend
```bash
cd frontend
npm run dev
```

Frontend en: http://localhost:5173

### 4️⃣ Login y Probar
```
Admin:
  1. http://localhost:5173/login
  2. Email: admin@test.com
  3. Password: admin123
  4. Click "Iniciar Sesión"
  5. Navbar muestra "🔧 Admin" → Click
  6. Ver dashboard admin con usuarios, cultivos, tareas

Usuario Normal:
  1. http://localhost:5173/login
  2. Email: user@test.com
  3. Password: user123
  4. Click "Iniciar Sesión"
  5. Ver dashboard de usuario
  6. Ver tareas creadas
  7. Ver calendarios
  8. No ves "🔧 Admin"
```

---

## 🧹 Limpiar Datos Demo

### Opción A: Limpiar demo (mantener admin)
```bash
python scripts/seed_demo.py --clean
```

Elimina:
- Usuario demo
- Cultivos demo
- Tareas demo
- Calendarios demo

Mantiene:
- Usuario admin

### Opción B: Reset completo
```bash
python scripts/seed_demo.py --reset
```

Elimina TODO incluyendo admin.

Luego:
```bash
python scripts/seed_demo.py
```

Recrea datos.

---

## 📊 Datos Creados

| Recurso | Cantidad | Descripción |
|---------|----------|------------|
| **Usuarios** | 2 | admin + demo |
| **Cultivos** | 6 | 5 públicos + 1 privado |
| **Calendarios** | 3 | Tomate, Lechuga, Zanahoria |
| **Tareas** | 4 | Para usuario demo |
| **Riego** | 6 | Para cada cultivo |
| **Requisitos** | 6 | Para cada cultivo |

---

## ✅ Validación

### Build
```bash
cd frontend
npm run build
```
✅ Debe ser exitoso

### Tests
```bash
python -m unittest discover -s tests -p "test*.py" -v
```
✅ Deben ser 83/83 OK

---

## 🎯 Casos de Uso

### Caso 1: Desarrollador Local
```bash
# Inicio día de trabajo
python scripts/seed_demo.py  # Asegurar datos
python -m uvicorn app.main:app --reload
cd frontend && npm run dev
# Probar funcionalidades con datos realistas
```

### Caso 2: Demo de Producto
```bash
# Reset limpio
python scripts/seed_demo.py --reset
python scripts/seed_demo.py
# Iniciar frontend
# Mostrar a stakeholders datos reales del sistema
```

### Caso 3: Limpiar entre Pruebas
```bash
# Borrar datos de prueba, mantener admin
python scripts/seed_demo.py --clean
# Ejecutar tests
python -m unittest discover -s tests -p "test*.py"
# Recrear demo si se quiere
python scripts/seed_demo.py
```

---

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con bcrypt
- ✅ Credenciales demo solo en dev
- ✅ No usar en producción
- ✅ Cambiar contraseñas en prod

---

## 📝 Notas

- Script es **idempotente:** ejecutar 10 veces = mismo resultado
- Colores en output (Windows PowerShell soportado)
- Logs de SQLAlchemy incluidos (verbose para debugging)
- SQLite local por defecto
- Sin dependencias nuevas

---

## ❓ Troubleshooting

### Error: "ModuleNotFoundError: app"
```bash
# Verificar estar en tfg-claude/
cd tfg-claude
python scripts/seed_demo.py
```

### Error: "no such table"
```bash
# BD corrupta, reset completo
python scripts/seed_demo.py --reset
python scripts/seed_demo.py
```

### Error: "user already exists"
```bash
# Normal si se ejecuta múltiples veces
# Script evita duplicados
python scripts/seed_demo.py
```

### Password incorrecto en login
```bash
# Verificar credenciales exactas:
# admin@test.com / admin123
# user@test.com / user123
```

---

## ✨ Siguiente

- Probar admin panel: /admin/dashboard
- Probar usuario normal: dashboard + cultivos + tareas
- Probar logout/login
- Leer PHASE10_IMPLEMENTATION.md para detalles técnicos
