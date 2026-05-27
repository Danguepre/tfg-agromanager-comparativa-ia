# Comparación por fases — AgroManager

## FASE 9 — Panel admin visual

**Estado del documento:** Provisional  
**Motivo:** Codex y DeepSeek están validados. Claude Code queda pendiente por agotamiento de cuota/herramienta y se añadirá cuando pueda completarse.

---

## Objetivo de la fase

Implementar un panel de administración visual en el frontend usando los endpoints backend ya creados en FASE 7.

La fase busca permitir que un usuario con rol `admin` pueda gestionar desde la interfaz:

1. Resumen global del sistema.
2. Usuarios.
3. Cultivos.
4. Tareas.
5. Acceso protegido por rol admin.
6. Estados de carga, error y vacío.
7. Confirmación antes de acciones destructivas.
8. Mantenimiento del frontend de usuario ya validado en FASE 8.
9. `npm run build` sin errores.
10. Tests backend sin regresiones.

---

## Alcance funcional esperado

### Acceso admin

- Ruta `/admin`.
- Rutas o secciones:
  - `/admin/dashboard`
  - `/admin/users`
  - `/admin/crops`
  - `/admin/tasks`
- Usuario sin token debe ser redirigido a login.
- Usuario normal no debe ver enlace Admin.
- Usuario normal no debe poder acceder al panel admin.
- Usuario admin debe ver enlace Admin.
- Usuario admin debe poder acceder a las secciones administrativas.
- Protección doble:
  - frontend por rol;
  - backend por endpoints `/admin/*`.

### Dashboard admin

Debe consumir `GET /admin/summary` y mostrar:

- Total de usuarios.
- Total de cultivos.
- Total de cultivos públicos.
- Total de tareas.
- Tareas pendientes.
- Tareas completadas.
- Calendarios activos.
- Calendarios completados.

### Gestión de usuarios

Endpoints esperados:

- `GET /admin/users`
- `GET /admin/users/{user_id}`
- `PATCH /admin/users/{user_id}`
- `DELETE /admin/users/{user_id}`

Requisitos:

- Listado o tabla de usuarios.
- No mostrar password ni password hash.
- Editar campos básicos si el backend lo permite.
- Activar/desactivar si existe `is_active`.
- Confirmación antes de eliminar.
- Estado vacío/error controlado.

### Gestión de cultivos

Endpoints esperados:

- `GET /admin/crops`
- `GET /admin/crops/{crop_id}`
- `PATCH /admin/crops/{crop_id}`
- `DELETE /admin/crops/{crop_id}`

Requisitos:

- Listado global de cultivos.
- Editar campos básicos como `name`, `description`, `crop_type`, `is_public`.
- Confirmación antes de eliminar.
- Normalización de respuestas de listas.

### Gestión de tareas

Endpoints esperados:

- `GET /admin/tasks`
- `GET /admin/tasks/{task_id}`
- `PATCH /admin/tasks/{task_id}`
- `DELETE /admin/tasks/{task_id}`

Requisitos:

- Listado global de tareas.
- Editar `title/name`, `description`, `status`, `due_date` si existe.
- Marcar pendiente/completada si el backend lo soporta.
- Confirmación antes de eliminar.
- Normalización de respuestas de listas.

---

# Tabla comparativa provisional FASE 9

| IA | Estado | Iteraciones | Build frontend | Backend tests | Visual admin | Admin route | Admin usuarios | Admin cultivos | Admin tareas | Observaciones | Puntuación provisional |
|---|---|---:|---|---|---|---|---|---|---|---|---:|
| Claude Code | Pendiente | — | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Bloqueado por cuota/herramienta; se añadirá después | Pendiente |
| Codex | Validado | 1 | OK, 151ms | OK, 50 tests | OK | Sí | Sí | Sí | Sí | Admin creado manualmente en SQLite | 91 |
| DeepSeek | Validado | 1 | OK, 671ms | OK, 104 tests | OK | Sí | Sí | Sí | Sí | Admin creado manualmente en SQLite | 93 |

---

# Codex — FASE 9

## Estado

**Validado y cerrado.**

Codex implementó el panel admin visual correctamente. La validación visual se realizó con un usuario convertido manualmente a rol `admin` en la base SQLite local `agromanager.db`.

---

## Validación técnica

### Build frontend

Comando ejecutado:

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
dist/assets/index-LsF5PRld.css    4.72 kB │ gzip:  1.59 kB
dist/assets/index-CsCQDoGq.js   215.93 kB │ gzip: 66.86 kB

✓ built in 151ms
```

### Tests backend

Comando ejecutado:

```bash
cd C:\Users\danie\Desktop\tfg\tfg-codex
python -m unittest discover -s tests -p "test*.py" -v
```

Resultado:

```text
Ran 50 tests in 65.154s

OK
```

---

## Validación visual

### Usuario normal

- Usuario normal inicia sesión correctamente.
- Usuario normal no ve enlace Admin.
- Usuario normal no accede a funcionalidad admin.
- Frontend de usuario sigue funcionando.

### Usuario admin

Para validar el panel admin, se convirtió manualmente un usuario en admin modificando `agromanager.db`.

Resultado visual:

- Usuario admin inicia sesión correctamente.
- Aparece enlace Admin en el menú lateral.
- `/admin/dashboard` carga correctamente.
- `/admin/users` carga correctamente.
- `/admin/crops` carga correctamente.
- `/admin/tasks` carga correctamente.
- El frontend de usuario sigue funcionando.

### Dashboard admin observado

- Usuarios: 2.
- Cultivos: 0.
- Cultivos públicos: 0.
- Tareas: 0.
- Tareas pendientes: 0.
- Tareas completadas: 0.
- Calendarios activos: 0.
- Calendarios completados: 0.

---

## Fortalezas Codex

- Implementación estable en primera iteración.
- Build muy rápido.
- Panel admin funcional.
- No rompe tests backend.
- Admin visual integrado con frontend existente.
- Usuario normal no ve el enlace Admin.
- El frontend de usuario validado en FASE 8 sigue funcionando.

---

## Limitaciones Codex

| Limitación | Impacto | Estado |
|---|---|---|
| No hay seed/admin inicial | Hay que convertir admin manualmente | Pendiente FASE 10 |
| Panel visual funcional pero simple | Menor riqueza visual | Aceptable |
| Sin búsqueda/ordenación/paginación avanzada | Gestión limitada con muchos datos | Pendiente |
| Validación visual con pocos datos | No se comprueba comportamiento con muchos usuarios/cultivos/tareas | Pendiente |
| Tests backend siguen siendo lentos para 50 tests | Tiempo de validación alto | No bloqueante |

---

## Incidencias Codex

No se observaron incidencias bloqueantes en FASE 9.

La principal observación es metodológica: al no existir seed ni creación segura de admin inicial, fue necesario modificar manualmente SQLite para validar el panel admin.

---

## Puntuación provisional Codex FASE 9

```text
91/100
```

### Justificación

Codex cumple la fase correctamente, pasa build y tests, y el panel admin funciona visualmente. Se penaliza ligeramente por simplicidad visual y por la ausencia de seed/admin inicial, aunque esta última es una limitación del alcance general y queda para FASE 10.

---

# DeepSeek — FASE 9

## Estado

**Validado y cerrado.**

DeepSeek implementó el panel admin visual correctamente, con mayor cobertura backend que Codex y una estructura más completa en componentes admin.

---

## Archivos creados

DeepSeek reportó la creación de:

- `frontend/src/components/AdminRoute.jsx`
- `frontend/src/pages/admin/AdminDashboard.jsx`
- `frontend/src/pages/admin/AdminUsers.jsx`
- `frontend/src/pages/admin/AdminCrops.jsx`
- `frontend/src/pages/admin/AdminTasks.jsx`

## Archivos modificados

DeepSeek reportó modificaciones en:

- `frontend/src/api/api.js`
- `frontend/src/context/AuthContext.jsx`
- `frontend/src/components/Navbar.jsx`
- `frontend/src/App.jsx`

---

## Decisiones técnicas reportadas

- `AdminRoute` se basa en `useAuth().isAdmin`.
- `AuthContext` incluye `isAdmin`.
- Se añadió `parseJwt` para extraer `user_id` del token al login.
- `normalizeList` también soporta `data.users`.
- `apiRequest` maneja explícitamente HTTP 403 con el mensaje:
  - “No tienes permisos de administrador”.
- Las páginas admin usan patrón `loading/error/empty/success`.
- Formularios de edición inline.
- Confirmación antes de eliminar.
- Toggle de activo/completado con botón directo.

---

## Rutas frontend admin añadidas

| Ruta | Componente | Descripción |
|---|---|---|
| `/admin/dashboard` | `AdminDashboard` | Resumen global del sistema |
| `/admin/users` | `AdminUsers` | CRUD de usuarios |
| `/admin/crops` | `AdminCrops` | CRUD de cultivos |
| `/admin/tasks` | `AdminTasks` | CRUD de tareas |

---

## Endpoints admin consumidos

- `GET /admin/summary`
- `GET /admin/users`
- `PATCH /admin/users/{id}`
- `DELETE /admin/users/{id}`
- `GET /admin/crops`
- `PATCH /admin/crops/{id}`
- `DELETE /admin/crops/{id}`
- `GET /admin/tasks`
- `PATCH /admin/tasks/{id}`
- `DELETE /admin/tasks/{id}`

---

## Protección por rol admin

DeepSeek implementó protección en dos capas:

### Frontend

- `AdminRoute` redirige a login si no hay token.
- `AdminRoute` muestra mensaje de permisos si `user.role !== "admin"`.
- Navbar solo muestra “Admin ⚙️” si `isAdmin === true`.

### Backend

- Los endpoints `/admin/*` siguen protegidos y devuelven `403` si el usuario no es admin.

---

## Validación técnica

### Build frontend

Comando:

```bash
cd C:\Users\danie\Desktop\tfg\tfg-deepseek\frontend
npm run build
```

Resultado reportado:

```text
✓ built in 671ms
✓ 57 modules transformed
dist/index.html                  0.33 kB │ gzip:  0.25 kB
dist/assets/index-Byj7vGJZ.js  235.03 kB │ gzip: 68.63 kB
```

### Tests backend

Comando:

```bash
cd C:\Users\danie\Desktop\tfg\tfg-deepseek
python -m unittest discover -s tests -p "test*.py" -v
```

Resultado:

```text
Ran 104 tests in 73.391s

OK
```

---

## Validación visual

### Usuario admin

- Login admin: OK.
- Enlace Admin visible: OK.
- `/admin/dashboard`: OK.
- `/admin/users`: OK.
- `/admin/crops`: OK.
- `/admin/tasks`: OK.
- Frontend usuario sigue funcionando.

### Dashboard admin observado

- Usuarios totales: 1.
- Cultivos totales: 0.
- Cultivos públicos: 0.
- Tareas totales: 0.
- Tareas pendientes: 0.
- Tareas completadas: 0.
- Calendarios activos: 0.
- Calendarios completados: 0.

---

## Fortalezas DeepSeek

- Mayor cobertura backend: 104 tests.
- Panel admin dividido en componentes específicos.
- Protección admin explícita con `AdminRoute`.
- Manejo específico de `403`.
- Navbar condicional por `isAdmin`.
- Normalización de listas ampliada.
- Build correcto.
- Validación visual correcta en todas las rutas admin.

---

## Limitaciones DeepSeek

| Limitación | Impacto | Estado |
|---|---|---|
| No hay seed/admin inicial | Requiere modificar DB manualmente | Pendiente FASE 10 |
| Tablas sin paginación/búsqueda/ordenación avanzada | Gestión limitada con muchos datos | Pendiente |
| Dashboard sin gráficos | Visualmente simple | Aceptable |
| Validación frontend básica | Backend soporta validación principal | Aceptable |
| Toggle inmediato puede duplicar llamadas si se pulsa rápido | Riesgo menor de UX | Pendiente |

---

## Riesgos DeepSeek

- Si cambian nombres en `AdminSummary`, el frontend muestra 0 por fallback.
- Si el usuario no tiene datos en `localStorage`, `isAdmin` será false hasta login.
- Accesos directos a `/admin/*` por usuario normal dependen de frontend y backend para bloquear.
- Sin seed final, no hay forma limpia de probar admin sin manipular DB.

---

## Puntuación provisional DeepSeek FASE 9

```text
93/100
```

### Justificación

DeepSeek supera a Codex por mayor cobertura backend, mejor estructura del panel admin y protección admin más explícita. Se penaliza por simplicidad visual y ausencia de seed/admin inicial.

---

# Claude Code — FASE 9

## Estado

**Pendiente.**

Claude no se ha podido validar en FASE 9 por agotamiento de cuota/herramienta.

---

## Situación actual

- FASE 8 de Claude quedó validada.
- FASE 9 está pendiente.
- Se intentó continuar con Claude Haiku 4.5 mediante Cline, pero requiere API key de Anthropic.
- Para mantener la comparación, Claude FASE 9 queda pausado hasta:
  - renovación de cuota de GitHub Copilot Chat;
  - o uso explícito de Cline/Anthropic API, dejando registrada la diferencia metodológica.

---

## Nota metodológica

Si Claude se continúa con Cline usando `anthropic/claude-haiku-4.5`, debe registrarse en la comparación como cambio de herramienta:

```text
Claude FASE 9 continuado mediante Cline con anthropic/claude-haiku-4.5 tras agotarse la cuota mensual de GitHub Copilot Chat.
```

Esto mantiene el mismo modelo/familia aproximada, pero cambia la herramienta agente y puede afectar la comparación.

---

# Comparación provisional FASE 9

## Mejor cobertura backend

**DeepSeek**

Motivo:

- 104 tests frente a 50 de Codex.
- Mantiene cobertura amplia de fases anteriores.

## Mejor velocidad de build

**Codex**

Motivo:

- Build en 151ms frente a 671ms de DeepSeek.

## Mejor estructura admin

**DeepSeek**

Motivo:

- Componentes admin separados.
- `AdminRoute`.
- `isAdmin`.
- Manejo específico de 403.
- Normalización ampliada.

## Mejor estabilidad visual

**Empate Codex / DeepSeek**

Motivo:

- Ambos cargan correctamente dashboard, usuarios, cultivos y tareas admin.
- Ambos requieren admin manual por SQLite.

## Mejor resultado provisional

**DeepSeek**

Motivo:

- Mayor cobertura.
- Mejor estructura.
- Validación visual completa.
- Sin regresiones.

---

# Resultado provisional

| Posición provisional | IA | Puntuación | Motivo |
|---:|---|---:|---|
| 1 | DeepSeek | 93/100 | Mayor cobertura y mejor estructura admin |
| 2 | Codex | 91/100 | Funcional y estable, build muy rápido |
| — | Claude Code | Pendiente | Bloqueado por cuota/herramienta |

---

# Estado acumulado provisional tras FASE 9

| IA | Piloto 0-3 | FASE 4 | FASE 5 | FASE 6 | FASE 7 | FASE 8 | FASE 9 | Estado acumulado |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | 91 | 92 | 91 | Pendiente | Funcional hasta FASE 8; FASE 9 pendiente |
| Codex | 77 | 86 | 90 | 90 | 91 | 90 | 91 | Funcional y estable, aunque más simple |
| DeepSeek | 87 | 94 | 96 | 96 | 97 | 92 | 93 | Mejor resultado acumulado provisional |

---

# Incidencias transversales FASE 9

## Falta de seed/admin inicial

Tanto Codex como DeepSeek necesitaron un admin creado o activado manualmente en SQLite para validar el panel admin.

Esto confirma que la siguiente fase debería resolver:

- creación segura de usuario admin inicial;
- datos de ejemplo;
- cultivos públicos de prueba;
- tareas de prueba;
- calendarios de prueba.

## Validación visual con pocos datos

Los paneles se han validado principalmente con datos vacíos o mínimos.

Esto no invalida FASE 9, pero limita la comprobación de:

- tablas con muchos registros;
- paginación;
- búsqueda;
- ordenación;
- edición masiva;
- relaciones complejas.

## Sin migraciones reales

Sigue pendiente resolver el problema de bases SQLite antiguas cuando cambian los modelos.

---

# Próximo paso recomendado

La siguiente fase debería ser:

```text
FASE 10 — Seed/admin inicial y datos de ejemplo
```

## Objetivo recomendado FASE 10

Implementar mecanismos controlados para preparar el entorno de prueba y demostración:

- Crear usuario admin inicial de forma segura.
- Crear usuario normal de ejemplo.
- Crear cultivos públicos de ejemplo.
- Crear cultivos personales.
- Crear tareas de ejemplo.
- Crear calendario agrícola de ejemplo.
- Crear datos de riego.
- Crear requisitos ambientales.
- Documentar cómo ejecutar el seed.
- Evitar secretos reales.
- Mantener tests backend pasando.
- Mantener build frontend pasando.

## Motivo

FASE 10 resolvería la principal limitación detectada en FASE 8 y FASE 9: la app funciona, pero no tiene datos iniciales suficientes para una demostración completa sin manipular SQLite manualmente.

---

# Estado del documento

Este documento es provisional porque falta añadir Claude Code FASE 9.

Cuando Claude esté disponible:

1. Ejecutar prompt FASE 9 en `tfg-claude/`.
2. Validar:
   - `npm run build`;
   - tests backend;
   - usuario normal;
   - usuario admin;
   - dashboard admin;
   - usuarios/cultivos/tareas admin.
3. Añadir resultados al documento.
4. Convertir este documento de provisional a final.
