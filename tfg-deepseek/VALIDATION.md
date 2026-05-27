# ✅ Guía Técnica de Validación — AgroManager

Checklist para validar que la aplicación funciona correctamente
tras la instalación y configuración.

## 1. Seed de datos demo

```bash
cd tfg-deepseek
python scripts/seed_demo.py
```

**Resultado esperado**: Resumen con datos creados (usuarios, cultivos, tareas, etc.)
y sin errores.

## 2. Tests

### 2.1 Comando recomendado

```bash
cd tfg-deepseek
python -m unittest tests.test_api tests.test_seed -v
```

**Resultado esperado**:

```
Ran 117 tests ... OK
```

### 2.2 Tests individuales

```bash
# Solo tests de API (104 tests)
python -m unittest tests.test_api -v

# Solo tests del seed (13 tests)
python -m unittest tests.test_seed -v
```

### 2.3 Observación sobre `unittest discover`

En Windows PowerShell, el comando:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

puede no detectar tests debido a problemas de pattern matching del shell.
La forma recomendada y verificada es la invocación explícita de módulos
(sección 2.1).

## 3. Build frontend

```bash
cd tfg-deepseek/frontend

# Si PowerShell bloquea npm.ps1, usar:
npm.cmd run build
# o:
npm run build
```

**Resultado esperado**:

```
vite v5.x.x building for production...
✓ 57 modules transformed.
dist/index.html                  0.33 kB
dist/assets/index-Byj7vGJZ.js  235.03 kB
✓ built in Xms
```

## 4. Validación manual

### 4.1 Requisitos previos

1. Seed ejecutado
2. Backend corriendo: `python -m uvicorn app.main:app --reload`
3. Frontend corriendo: `npm run dev` (en `frontend/`)

### 4.2 Checklist usuario normal

| # | Acción | Resultado esperado |
|---|--------|--------------------|
| 1 | Ir a `http://localhost:5173` | Ver página de login |
| 2 | Login: user@test.com / user123 | Dashboard con datos |
| 3 | Dashboard | Ver contadores: cultivos, tareas, calendario |
| 4 | Dashboard | Ver secciones: irrigación, ambiente |
| 5 | Mis Cultivos | Ver "Mi Tomate" y "Mi Lechuga" |
| 6 | Detalle cultivo | Ver riego, ambiente, calendario |
| 7 | Catálogo | Ver 5 cultivos públicos |
| 8 | Catálogo | Probar filtros de búsqueda |
| 9 | Catálogo | Copiar un cultivo a "Mis cultivos" |
| 10 | Calendario | Ver eventos del calendario activo |
| 11 | Tareas | Ver 2 pending + 2 completed |
| 12 | Tareas | Crear nueva tarea |
| 13 | Tareas | Marcar tarea como completada |
| 14 | Cerrar sesión | Volver a login |

### 4.3 Checklist administrador

| # | Acción | Resultado esperado |
|---|--------|--------------------|
| 1 | Login: admin@test.com / admin123 | Admin dashboard con estadísticas |
| 2 | Admin Dashboard | Ver total_users, total_crops, total_tasks |
| 3 | Admin Users | Ver lista de usuarios (sin contraseñas visibles) |
| 4 | Admin Users | Editar/desactivar un usuario |
| 5 | Admin Crops | Ver todos los cultivos |
| 6 | Admin Crops | Editar un cultivo |
| 7 | Admin Tasks | Ver todas las tareas |
| 8 | Admin Tasks | Editar/eliminar una tarea |

### 4.4 Checklist API (opcional)

```bash
# Health check
curl http://127.0.0.1:8000/
# → {"status":"ok","version":"0.1.0","message":"AgroManager API funcionando correctamente"}

# Catálogo público
curl http://127.0.0.1:8000/crops/published
# → {"items": [...], "total": 5, ...}

# Login admin
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
# → {"access_token": "eyJ...", "token_type": "bearer"}

# Swagger docs
# Abrir http://127.0.0.1:8000/docs en el navegador
```

## 5. Resumen de comandos

| Acción | Comando |
|--------|---------|
| Seed | `python scripts/seed_demo.py` |
| Tests | `python -m unittest tests.test_api tests.test_seed -v` |
| Backend | `python -m uvicorn app.main:app --reload` |
| Frontend dev | `cd frontend && npm run dev` |
| Frontend build | `cd frontend && npm run build` |
| Dependencias backend | `pip install -r requirements.txt` |
| Dependencias frontend | `cd frontend && npm install` |