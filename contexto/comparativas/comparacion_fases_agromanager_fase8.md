# Comparación por fases — AgroManager

## FASE 8 — Frontend funcional de usuario

## Objetivo de la fase

Convertir los frontends mínimos o placeholders de las tres implementaciones en una aplicación funcional para usuario normal.

La fase se centró en login, registro, guardado de `access_token`, logout, rutas protegidas, dashboard visual, Mis cultivos, Catálogo público, Calendario básico, Tareas, estados de carga/error/vacío, conexión real con API mediante Fetch, `npm run build` sin errores y tests backend sin regresiones.

No se incluía todavía el panel admin visual completo. Eso queda reservado para la FASE 9.

---

## Reglas de evaluación

### Validación técnica

```bash
npm run build
```

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Validación visual

- Home carga.
- Registro funciona.
- Login funciona.
- Se guarda sesión/token.
- Navbar/layout principal aparece.
- Dashboard carga.
- Mis cultivos carga sin romper.
- Catálogo carga sin romper.
- Calendario carga sin romper.
- Tareas carga sin romper.
- Logout disponible.
- Estados vacíos se muestran de forma controlada.
- No aparecen errores críticos que impidan usar la app.

---

# Tabla comparativa FASE 8

| IA | Iteraciones | Backend tests | Frontend build | Login/Register | Rutas protegidas | Dashboard | Cultivos | Catálogo | Calendario | Tareas | UX/errores | Puntuación /100 |
|---|---:|---|---|---|---|---|---|---|---|---|---|---:|
| Claude Code | 2 | OK, 83 tests | OK | OK | OK | OK tras reset DB | OK tras corrección | OK tras corrección | OK | OK básico | Bug de listas corregido; requiere normalización | 91 |
| Codex | 1 | OK, 50 tests | OK | OK | OK | OK | OK vacío | OK vacío | OK vacío | OK básico | Simple pero estable | 90 |
| DeepSeek | 1 | OK, 104 tests | OK | OK | OK | OK tras reset DB | OK vacío | OK vacío | OK vacío | OK básico | Simple; requiere reset DB por esquema antiguo | 92 |

---

# Resultado final FASE 8

| Posición | IA | Puntuación | Motivo principal |
|---:|---|---:|---|
| 1 | DeepSeek | 92/100 | Mejor cobertura backend y frontend funcional tras reset de base |
| 2 | Claude Code | 91/100 | Buen frontend y normalización robusta, pero necesitó segunda iteración |
| 3 | Codex | 90/100 | Estable y funcional, aunque más simple y con menor cobertura |

---

# Claude Code — FASE 8

## Estado final

**Validado.**

Claude necesitó una segunda iteración para corregir un bug en la página de cultivos, pero tras la corrección la fase queda cerrada correctamente.

## Build frontend

```bash
cd C:\Users\danie\Desktop\tfg\tfg-claude\frontend
npm run build
```

Resultado observado:

```text
vite v5.4.21 building for production...
✓ 51 modules transformed.
dist/index.html                   0.47 kB │ gzip:  0.31 kB
dist/assets/index-Dl7NhFS7.css   10.30 kB │ gzip:  2.45 kB
dist/assets/index-CED9LfOb.js   184.86 kB │ gzip: 58.44 kB
✓ built in 502ms
```

Observaciones:

- `npm install` reportó 2 vulnerabilidades moderadas.
- `npm run bui` fue un error tipográfico del comando, no una incidencia del proyecto.
- `npm run build` terminó correctamente.

## Tests backend

```bash
cd C:\Users\danie\Desktop\tfg\tfg-claude
python -m unittest discover -s tests -p "test*.py" -v
```

Resultado final tras corrección:

```text
Ran 83 tests in 55.719s

OK
```

## Funcionalidades implementadas

Claude construyó un frontend con:

- Login.
- Registro.
- Logout.
- Guardado de token en `localStorage`.
- Rutas protegidas.
- Redirección a login sin token.
- Navbar superior.
- Dashboard.
- Mis Cultivos.
- Catálogo.
- Calendario.
- Tareas.
- Cliente API centralizado con Fetch.
- Uso de `VITE_API_URL`.
- Envío de `Authorization: Bearer <token>`.
- Manejo de errores.
- Normalización de respuestas de listas tras corrección.

## Archivos reportados

### Creados inicialmente

- `frontend/src/components/Login.jsx`
- `frontend/src/components/Register.jsx`
- `frontend/src/components/Auth.css`
- `frontend/src/components/Layout.jsx`
- `frontend/src/components/Navbar.jsx`
- `frontend/src/components/Navbar.css`
- `frontend/src/components/Layout.css`
- `frontend/src/components/ProtectedRoute.jsx`
- `frontend/src/pages/Home.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `frontend/src/pages/Crops.jsx`
- `frontend/src/pages/CropDetail.jsx`
- `frontend/src/pages/Calendar.jsx`
- `frontend/src/pages/Tasks.jsx`
- `frontend/src/pages/Pages.css`

### Modificados inicialmente

- `frontend/package.json`
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/api/api.js`
- `frontend/src/App.jsx`
- `frontend/src/main.jsx`

### Modificados en la corrección

- `frontend/src/api/normalizers.js`
- `frontend/src/api/api.js`
- `frontend/src/pages/Crops.jsx`

## Incidencia 1 — Base SQLite antigua

Error observado inicialmente:

```text
Error: Failed to fetch
```

La consola backend mostró:

```text
sqlite3.OperationalError: no such column: crops.crop_type
```

Causa:

La base local `app.db` había sido creada con un esquema antiguo. El modelo actual esperaba la columna `crops.crop_type`, pero SQLite no la tenía.

Solución aplicada:

- Borrar la base local.
- Reiniciar backend.
- Re-registrar usuario.

Clasificación:

No se considera fallo directo del frontend. Es una incidencia de migración/esquema local.

## Incidencia 2 — `published.filter is not a function`

Error observado:

```text
Crops.jsx:51 Uncaught TypeError: published.filter is not a function
```

Causa:

El backend devolvía una respuesta paginada tipo:

```json
{
  "total": 0,
  "skip": 0,
  "limit": 10,
  "items": []
}
```

El frontend esperaba un array directo y ejecutaba `.filter()` sobre un objeto.

Corrección aplicada:

- Nueva función `normalizeListResponse()`.
- Soporte para array directo, `{ items: [...] }`, `{ crops: [...] }`, `{ data: [...] }`.
- Validaciones defensivas antes de `.filter()`, `.map()` y `.length`.

Resultado:

- Mis Cultivos carga correctamente.
- Catálogo carga correctamente.
- Un cultivo creado aparece en Mis Cultivos.
- Catálogo no rompe aunque esté vacío.

## Validación visual final

- Home: OK.
- Registro: OK.
- Login: OK.
- Navbar: OK.
- Dashboard: OK.
- Mis Cultivos: OK, muestra cultivo creado.
- Catálogo: OK, no rompe aunque esté vacío.
- Calendario: OK.
- Tareas: OK básico.
- Logout: OK.

## Incidencias pendientes Claude

| Incidencia | Severidad | Estado |
|---|---|---|
| Requiere borrar DB local cuando cambia esquema | Media | Pendiente de migraciones reales |
| `npm audit` con 2 vulnerabilidades moderadas | Baja/Media | Pendiente |
| Mantiene desviaciones previas como `/auth/register` | Baja | Documentada |
| Redirects 307 en varias rutas backend | Baja | No bloqueante |
| Necesitó segunda iteración para normalizar listas | Media | Corregido |

## Puntuación Claude FASE 8

```text
91/100
```

Claude termina con un frontend funcional y una solución robusta para listas paginadas, pero necesitó una segunda iteración por un bug que rompía Mis Cultivos/Catálogo.

---

# Codex — FASE 8

## Estado final

**Validado.**

Codex fue el más estable en primera pasada. Su frontend es más simple, pero no rompió visualmente y manejó bien los estados vacíos.

## Build frontend

```bash
cd C:\Users\danie\Desktop\tfg\tfg-codex\frontend
npm run build
```

Resultado:

```text
vite v8.0.13 building client environment for production...
✓ 16 modules transformed.
computing gzip size...
dist/index.html                   0.40 kB │ gzip:  0.27 kB
dist/assets/index-b4LNGS_f.css    3.93 kB │ gzip:  1.38 kB
dist/assets/index-BedyJEXX.js   207.18 kB │ gzip: 64.72 kB

✓ built in 105ms
```

## Tests backend

```bash
cd C:\Users\danie\Desktop\tfg\tfg-codex
python -m unittest discover -s tests -p "test*.py" -v
```

Resultado:

```text
Ran 50 tests in 66.797s

OK
```

## Validación visual

- Login: OK.
- Registro: OK.
- Dashboard: OK.
- Mis Cultivos: OK, estado vacío sin error.
- Catálogo: OK, estado vacío sin error.
- Calendario: OK, estado vacío sin error.
- Tareas: OK, formulario visible y listado vacío sin error.
- Sesión: OK.
- Logout: visible.
- Las rutas principales responden correctamente desde backend.

## Endpoints observados funcionando

- `POST /users/`
- `POST /auth/login`
- `GET /users/`
- `GET /dashboard/summary`
- `GET /crops/my`
- `GET /crops/published`
- `GET /calendar/`
- `GET /calendar/events`
- `GET /tasks/`

## Observaciones Codex

| Aspecto | Observación |
|---|---|
| Frontend | Funcional, pero visualmente simple |
| Build | Muy rápido |
| Tests backend | Pasan, pero tardan bastante para 50 tests |
| Datos seed | No hay datos, por eso las pantallas aparecen vacías |
| Tareas | No se validó exhaustivamente crear/completar/eliminar en visual |
| Login | Mantiene desviación previa: Swagger usa `username`, aunque el uso real parece email |

## Incidencias pendientes Codex

| Incidencia | Severidad | Estado |
|---|---|---|
| Frontend simple | Baja | Aceptable |
| Suite lenta para 50 tests | Baja | Pendiente |
| Sin seed de datos | Baja | Pendiente |
| Validación visual de CRUD completo de tareas no exhaustiva | Baja | Pendiente |
| Build usa Vite v8, distinto a otros proyectos | Baja | No bloqueante |

## Puntuación Codex FASE 8

```text
90/100
```

Codex fue funcional y estable en primera pasada. No tuvo bugs críticos visuales, pero su implementación es más básica y su cobertura backend es menor que la de DeepSeek y Claude.

---

# DeepSeek — FASE 8

## Estado final

**Validado.**

DeepSeek tuvo la mejor cobertura backend y un frontend funcional, aunque visualmente sencillo. Requirió reset de la base local para que el dashboard funcionara por un problema de esquema SQLite antiguo.

## Build frontend

```bash
cd C:\Users\danie\Desktop\tfg\tfg-deepseek\frontend
npm run build
```

Resultado:

```text
vite v5.4.21 building for production...
✓ 52 modules transformed.
dist/index.html                  0.33 kB │ gzip:  0.25 kB
dist/assets/index-BNooW832.js  213.47 kB │ gzip: 65.42 kB
✓ built in 528ms
```

Observaciones:

- `npm install` reportó 2 vulnerabilidades moderadas.
- Build correcto.

## Tests backend

```bash
cd C:\Users\danie\Desktop\tfg\tfg-deepseek
python -m unittest discover -s tests -p "test*.py" -v
```

Resultado:

```text
Ran 104 tests in 71.954s

OK
```

## Validación visual inicial

Antes de resetear la base:

- Home: OK.
- Registro: OK.
- Login: OK.
- Navbar: OK.
- Mis Cultivos: OK, estado vacío.
- Catálogo: OK, estado vacío.
- Calendario: OK, estado vacío.
- Tareas: OK, estado vacío con botón “Nueva tarea”.
- Dashboard: fallaba.

Error inicial del dashboard:

```text
Error: Error de red en /dashboard/summary: Failed to fetch
```

La consola backend mostraba:

```text
sqlite3.OperationalError: no such column: planting_calendars.planting_start
```

## Incidencia — Base SQLite antigua

Causa:

La base local había sido creada con un esquema anterior. Los modelos actuales esperaban columnas nuevas en `planting_calendars`, como:

- `planting_start`
- `planting_end`
- `transplant_start`
- `transplant_end`
- `harvest_start`
- `harvest_end`

SQLite no añade columnas nuevas automáticamente con `create_all()`.

Solución aplicada:

- Borrar la base `.db` local.
- Reiniciar backend.
- Re-registrar usuario.

## Validación visual final

Después de borrar/recrear la base, el dashboard carga correctamente.

Resultado observado:

- Dashboard: OK.
- Cultivos propios: 0.
- Catálogo público: 0.
- Tareas pendientes: 0.
- Tareas completadas: 0.
- Calendarios activos: 0.
- Calendarios completados: 0.
- Mis Cultivos: OK, estado vacío.
- Catálogo: OK, estado vacío.
- Calendario: OK, estado vacío.
- Tareas: OK, estado vacío.
- Logout: OK visualmente.

## Incidencias pendientes DeepSeek

| Incidencia | Severidad | Estado |
|---|---|---|
| Requiere reset DB por esquema antiguo | Media | Pendiente de migraciones |
| `npm audit` con 2 vulnerabilidades moderadas | Baja/Media | Pendiente |
| Frontend visualmente simple | Baja | Aceptable |
| No hay seed de datos | Baja | Pendiente |
| Suite backend más lenta | Baja | Aceptable por cobertura |

## Puntuación DeepSeek FASE 8

```text
92/100
```

DeepSeek consigue el mejor balance entre cobertura backend y frontend funcional. Aunque requirió reset de base para el dashboard, no tuvo un bug de renderizado como Claude y conserva la suite backend más amplia.

---

# Comparación de incidencias

| IA | Incidencia principal | Impacto | Estado |
|---|---|---|---|
| Claude Code | `published.filter is not a function` | Rompía Mis Cultivos/Catálogo | Corregido |
| Claude Code | SQLite local antigua: `crops.crop_type` | Rompía llamadas backend | Resuelto con reset DB |
| Codex | Frontend simple | Menor riqueza visual | Aceptable |
| Codex | Suite lenta para 50 tests | Tiempo alto | No bloqueante |
| DeepSeek | SQLite local antigua: `planting_calendars.planting_start` | Rompía Dashboard | Resuelto con reset DB |
| DeepSeek | Frontend simple | Menor riqueza visual | Aceptable |

---

# Comparación cualitativa

## Mejor cobertura backend

**DeepSeek**

Motivo:

- 104 tests.
- Mantiene cobertura amplia de auth, usuarios, cultivos, calendario, riego, ambiente, tareas, dashboard y admin.

## Mejor estabilidad visual en primera pasada

**Codex**

Motivo:

- No rompió visualmente en Dashboard, Cultivos, Catálogo, Calendario o Tareas.
- Mostró estados vacíos sin errores.

## Mejor corrección posterior

**Claude Code**

Motivo:

- Identificó correctamente el problema de `CropListResponse`.
- Añadió un normalizador robusto.
- El resultado final maneja mejor respuestas paginadas o no homogéneas.

## Mejor resultado global

**DeepSeek**

Motivo:

- Mayor cobertura backend.
- Frontend funcional.
- Dashboard funcional tras reset DB.
- Menos iteraciones que Claude.
- Mejor puntuación total.

---

# Estado acumulado tras FASE 8

| IA | Piloto 0-3 | FASE 4 | FASE 5 | FASE 6 | FASE 7 | FASE 8 | Estado acumulado |
|---|---:|---:|---:|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | 91 | 92 | 91 | Funcional, buena cobertura, pero con desviaciones persistentes y necesidad de correcciones |
| Codex | 77 | 86 | 90 | 90 | 91 | 90 | Funcional y estable, pero más simple y con cobertura media |
| DeepSeek | 87 | 94 | 96 | 96 | 97 | 92 | Mejor resultado acumulado provisional |

---

# Conclusión FASE 8

La FASE 8 queda cerrada con las tres implementaciones funcionales.

- **DeepSeek** gana la fase por cobertura backend y frontend funcional.
- **Claude Code** queda muy cerca tras corregir el bug de listas y termina con una solución más robusta frente a respuestas paginadas.
- **Codex** es el más simple, pero también fue el más estable en primera pasada.

La fase evidencia que los problemas más frecuentes fueron de integración:

1. respuestas paginadas tratadas como arrays;
2. bases SQLite locales antiguas sin migraciones;
3. estados vacíos por falta de seed;
4. diferencias de rutas y contratos entre backend y frontend.

---

# Próximo paso

La siguiente fase propuesta es:

```text
FASE 9 — Panel admin visual
```

## Objetivo recomendado FASE 9

Implementar el frontend de administración usando los endpoints backend creados en FASE 7.

Debe incluir:

- Ruta `/admin`.
- Protección por rol admin.
- Dashboard admin visual.
- Listado de usuarios.
- Ver usuario.
- Activar/desactivar usuario si existe `is_active`.
- Editar usuario.
- Eliminar usuario.
- Listado de cultivos global.
- Editar/eliminar cultivos.
- Listado de tareas global.
- Editar/eliminar tareas.
- Estados de carga/error.
- Confirmación antes de eliminar.
- `npm run build` sin errores.
- Backend tests siguen pasando.
- No implementar seed final todavía.

---

# Comandos útiles

## Claude

```bash
cd C:\Users\danie\Desktop\tfg\tfg-claude\frontend
npm run build
```

```bash
cd C:\Users\danie\Desktop\tfg\tfg-claude
python -m unittest discover -s tests -p "test*.py" -v
```

## Codex

```bash
cd C:\Users\danie\Desktop\tfg\tfg-codex\frontend
npm run build
```

```bash
cd C:\Users\danie\Desktop\tfg\tfg-codex
python -m unittest discover -s tests -p "test*.py" -v
```

## DeepSeek

```bash
cd C:\Users\danie\Desktop\tfg\tfg-deepseek\frontend
npm run build
```

```bash
cd C:\Users\danie\Desktop\tfg\tfg-deepseek
python -m unittest discover -s tests -p "test*.py" -v
```

---

# Notas finales

## Sobre migraciones

Claude y DeepSeek han mostrado el mismo problema estructural: las bases SQLite locales pueden quedarse desactualizadas cuando los modelos cambian.

En desarrollo se puede resolver borrando la `.db`, pero para una aplicación más madura se debería implementar:

- Alembic;
- migraciones manuales controladas;
- script de reset/seed documentado.

## Sobre seed

La falta de datos seed hace que las pantallas funcionen pero aparezcan vacías. Esto no bloquea FASE 8, pero dificulta validar visualmente catálogo, calendarios y relaciones complejas.

Queda recomendado para una fase posterior:

- seed de cultivos públicos;
- usuario admin inicial seguro;
- cultivos personales de prueba;
- tareas de ejemplo;
- calendarios de ejemplo.
