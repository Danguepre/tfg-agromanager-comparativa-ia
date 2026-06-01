# Comparación por fases — AgroManager

## FASE 9 — Panel admin visual

**Estado del documento:** Final  
**Motivo:** Codex, DeepSeek y Claude Code están validados. Claude Code fue completado posteriormente tras una interrupción temporal por cuota/herramienta y una corrección del rol admin en frontend.

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

# Tabla comparativa final FASE 9

| IA | Estado | Iteraciones | Build frontend | Backend tests | Visual admin | Admin route | Admin usuarios | Admin cultivos | Admin tareas | Observaciones | Puntuación final |
|---|---|---:|---|---|---|---|---|---|---|---|---:|
| Claude Code | Validado tras corrección | 2 | OK, 581ms | OK, 83 tests | OK | Sí | Sí | Sí | Sí | Bug inicial por `user.role` ausente en `localStorage`; corregido decodificando JWT | 92 |
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
| No hay seed/admin inicial | Hay que convertir admin manualmente | Resuelto en FASE 10 |
| Panel visual funcional pero simple | Menor riqueza visual | Aceptable |
| Sin búsqueda/ordenación/paginación avanzada | Gestión limitada con muchos datos | Pendiente |
| Validación visual con pocos datos | No se comprueba comportamiento con muchos usuarios/cultivos/tareas | Pendiente |
| Tests backend siguen siendo lentos para 50 tests | Tiempo de validación alto | No bloqueante |

---

## Incidencias Codex

No se observaron incidencias bloqueantes en FASE 9.

La principal observación es metodológica: al no existir seed ni creación segura de admin inicial, fue necesario modificar manualmente SQLite para validar el panel admin.

---

## Puntuación final Codex FASE 9

```text
91/100
```

### Justificación

Codex cumple la fase correctamente, pasa build y tests, y el panel admin funciona visualmente. Se penaliza ligeramente por simplicidad visual y por la ausencia de seed/admin inicial en ese momento, aunque esta limitación queda resuelta posteriormente en FASE 10.

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
| No hay seed/admin inicial | Requiere modificar DB manualmente | Resuelto en FASE 10 |
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

## Puntuación final DeepSeek FASE 9

```text
93/100
```

### Justificación

DeepSeek supera a Codex por mayor cobertura backend, mejor estructura del panel admin y protección admin más explícita. Se penaliza por simplicidad visual y ausencia de seed/admin inicial en ese momento, aunque esta limitación queda resuelta en FASE 10.

---

# Claude Code — FASE 9

## Estado

**Validado y cerrado tras corrección.**

Claude Code completó la FASE 9 implementando el panel admin visual en frontend. Inicialmente la fase parecía implementada, pero durante la validación visual se detectó un bug que impedía ver el enlace Admin y acceder al panel aunque el backend reconocía el rol correctamente.

---

## Archivos creados

Claude reportó la creación de:

- `frontend/src/components/ProtectedAdminRoute.jsx`
- `frontend/src/pages/AdminDashboard.jsx`
- `frontend/src/pages/AdminUsers.jsx`
- `frontend/src/pages/AdminCrops.jsx`
- `frontend/src/pages/AdminTasks.jsx`
- `frontend/src/pages/AdminPages.css`
- `scripts/make_admin.py`
- `PHASE9_IMPLEMENTATION.md`
- `QUICKSTART_PHASE9.md`

## Archivos modificados

Claude reportó modificaciones en:

- `frontend/src/App.jsx`
- `frontend/src/api/api.js`
- `frontend/src/components/Navbar.jsx`
- `README.md`

Tras la corrección del bug de rol admin también se modificaron:

- `frontend/src/api/api.js`
- `frontend/src/components/Login.jsx`
- `frontend/src/components/Register.jsx`

---

## Rutas frontend admin añadidas

| Ruta | Descripción |
|---|---|
| `/admin` | Redirección o acceso al área admin |
| `/admin/dashboard` | Dashboard admin con resumen global |
| `/admin/users` | Gestión de usuarios |
| `/admin/crops` | Gestión de cultivos |
| `/admin/tasks` | Gestión de tareas |

---

## Endpoints admin consumidos

Claude reportó el consumo de 13 endpoints del backend de FASE 7:

- `GET /admin/summary`
- `GET /admin/users?skip=0&limit=50`
- `GET /admin/users/{id}`
- `PATCH /admin/users/{id}`
- `DELETE /admin/users/{id}`
- `GET /admin/crops?skip=0&limit=50`
- `GET /admin/crops/{id}`
- `PATCH /admin/crops/{id}`
- `DELETE /admin/crops/{id}`
- `GET /admin/tasks?skip=0&limit=50`
- `GET /admin/tasks/{id}`
- `PATCH /admin/tasks/{id}`
- `DELETE /admin/tasks/{id}`

---

## Decisiones técnicas reportadas

- Protección en dos capas:
  - frontend mediante `ProtectedAdminRoute`;
  - backend mediante dependencias de admin en endpoints `/admin`.
- Edición inline en tablas.
- API client basado en Fetch API.
- Normalización de respuestas paginadas.
- Estados `loading`, `error` y vacío en cada componente.
- Navbar con enlace Admin condicional por rol.

---

## Validación técnica inicial

### Build frontend inicial

```text
vite v5.4.21 building for production...
✓ 58 modules transformed.
dist/index.html                   0.47 kB
dist/assets/index-D5y9pt0e.css   12.92 kB
dist/assets/index-DqzCHHQ1.js   197.86 kB
✓ built in 573ms
```

### Tests backend iniciales

```text
Ran 83 tests in 54.402s

OK
```

---

## Incidencia detectada — rol admin no disponible en frontend

### Síntoma

El backend reconocía correctamente al usuario como admin, pero el frontend no mostraba el enlace Admin y `/admin/dashboard` mostraba “Acceso denegado”.

### Causa

El JWT contenía el rol:

```json
{
  "role": "admin"
}
```

pero el backend devolvía solo:

```json
{
  "access_token": "...",
  "token_type": "...",
  "expires_in": "..."
}
```

El frontend buscaba `response.user`, que no existía, y terminaba guardando un usuario simplificado:

```json
{
  "email": "admin@test.com"
}
```

Por tanto:

```text
user.role === undefined
```

y `ProtectedAdminRoute` evaluaba:

```text
undefined !== "admin"
```

mostrando acceso denegado.

---

## Corrección aplicada

Claude añadió un helper `parseJwt()` en `frontend/src/api/api.js`:

```javascript
export function parseJwt(token) {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const decoded = JSON.parse(atob(parts[1]))
    return decoded
  } catch (error) {
    console.error('Error parsing JWT:', error)
    return null
  }
}
```

Después modificó `Login.jsx` y `Register.jsx` para decodificar el token y construir un objeto de usuario con:

- `id`;
- `email`;
- `role`;
- `name`.

Ejemplo de usuario final guardado:

```json
{
  "id": 1,
  "email": "admin@test.com",
  "role": "admin",
  "name": "admin"
}
```

---

## Validación técnica tras corrección

### Build frontend

```text
vite v5.4.21 building for production...
✓ 58 modules transformed.
dist/index.html                   0.47 kB │ gzip:  0.31 kB
dist/assets/index-AXNBHVE3.js   198.27 kB │ gzip: 60.35 kB
dist/assets/index-D5y9pt0e.css   12.92 kB │ gzip:  2.90 kB
✓ built in 581ms
```

### Tests backend

```text
Ran 83 tests in 51.210s

OK
```

---

## Validación visual final

### Admin

- Login como admin: OK.
- `localStorage` contiene usuario con `role: "admin"`.
- Navbar muestra enlace “Admin”.
- `/admin/dashboard` carga correctamente.
- `/admin/users` accesible.
- `/admin/crops` accesible.
- `/admin/tasks` accesible.

### Usuario normal

- Usuario normal no ve enlace Admin.
- Usuario normal no accede a rutas admin.
- Resto del frontend de usuario sigue funcionando.

---

## Fortalezas Claude FASE 9

- Panel admin visual completo.
- Buena documentación de implementación.
- Protección por rol en frontend.
- Consumo amplio de endpoints admin.
- Corrección razonada del bug de `user.role`.
- Validación visual final correcta.
- Sin regresiones backend.

---

## Limitaciones Claude FASE 9

| Limitación | Impacto | Estado |
|---|---|---|
| Bug inicial con rol admin en frontend | Bloqueaba acceso admin visual | Corregido |
| Rol derivado de `localStorage` en frontend | Riesgo si se manipula cliente | Mitigado por backend |
| Paginación frontend limitada | Gestión básica | Pendiente |
| Sin toasts ni feedback avanzado | UX simple | Aceptable |
| Sin seed inicial en esta fase | Admin se prepara con script/manual | Resuelto en FASE 10 |

---

## Puntuación final Claude FASE 9

```text
92/100
```

### Justificación

Claude entrega un panel admin completo y documentado, con consumo amplio de endpoints y buena corrección posterior del problema de rol. Se penaliza por haber necesitado una segunda iteración para solucionar un bug que bloqueaba el acceso visual al panel admin.

---

# Comparación final FASE 9

## Mejor cobertura backend

**DeepSeek**

Motivo:

- 104 tests frente a 83 de Claude y 50 de Codex.
- Mantiene cobertura amplia de fases anteriores.

## Mejor velocidad de build

**Codex**

Motivo:

- Build en 151ms frente a 581ms de Claude y 671ms de DeepSeek.

## Mejor estructura admin

**Empate DeepSeek / Claude Code**

Motivo:

- DeepSeek divide bien el panel admin en componentes específicos y usa `AdminRoute`.
- Claude implementa rutas admin protegidas, componentes específicos y consume 13 endpoints admin.

## Mejor corrección posterior

**Claude Code**

Motivo:

- Identificó y corrigió la causa real del bug de rol admin.
- La solución decodifica JWT y conserva coherencia entre token, usuario local y rutas protegidas.

## Mejor estabilidad en primera pasada

**Codex / DeepSeek**

Motivo:

- No requirieron una segunda iteración para hacer visible el panel admin.
- Claude necesitó corrección para que el admin pudiera acceder visualmente.

## Mejor resultado final

**DeepSeek por margen pequeño**

Motivo:

- Mayor cobertura backend.
- Buena estructura admin.
- Menos iteraciones que Claude.
- Codex fue muy estable, pero más simple.

---

# Resultado final

| Posición | IA | Puntuación | Motivo |
|---:|---|---:|---|
| 1 | DeepSeek | 93/100 | Mayor cobertura y buena estructura admin |
| 2 | Claude Code | 92/100 | Panel completo y gran corrección del bug de rol |
| 3 | Codex | 91/100 | Funcional, estable y rápido, aunque más simple |

---

# Estado acumulado tras FASE 9

| IA | Piloto 0-3 | FASE 4 | FASE 5 | FASE 6 | FASE 7 | FASE 8 | FASE 9 | Estado acumulado |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | 91 | 92 | 91 | 92 | Funcional y completo, con corrección relevante en admin |
| Codex | 77 | 86 | 90 | 90 | 91 | 90 | 91 | Funcional y estable, aunque más simple |
| DeepSeek | 87 | 94 | 96 | 96 | 97 | 92 | 93 | Mejor resultado acumulado provisional |

---

# Incidencias transversales FASE 9

## Falta de seed/admin inicial

Codex y DeepSeek necesitaron un admin creado o activado manualmente en SQLite para validar el panel admin. Claude incluyó un script auxiliar `make_admin.py`.

Esto confirma que la siguiente fase debía resolver:

- creación segura de usuario admin inicial;
- datos de ejemplo;
- cultivos públicos de prueba;
- tareas de prueba;
- calendarios de prueba.

## Validación visual con pocos datos

Los paneles se validaron principalmente con datos vacíos o mínimos.

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

# Conclusión FASE 9

FASE 9 queda cerrada con las tres implementaciones validadas.

- **DeepSeek** obtiene la mejor puntuación por cobertura backend y buena estructura admin.
- **Claude Code** queda muy cerca tras corregir el bug del rol admin y finalizar con un panel completo.
- **Codex** ofrece una solución estable, rápida y funcional, aunque más sencilla.

La fase confirma que el panel admin visual es una funcionalidad crítica para comprobar la coherencia entre backend, frontend, autenticación, roles y estado local del navegador.
