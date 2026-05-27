# FASE 9 — Panel admin visual en frontend para Claude

Actúa como desarrollador full-stack senior especializado en React, Vite, FastAPI y control de permisos.

Vamos a continuar la reconstrucción de AgroManager dentro de `tfg-claude/`.

## Contexto

Claude Code tiene implementadas y validadas las fases 0 a 8:

- FASE 0-3: base del proyecto, modelos, schemas, autenticación, usuarios y permisos.
- FASE 4: cultivos y catálogo.
- FASE 5: calendario agrícola.
- FASE 6: riego, requisitos ambientales y tareas.
- FASE 7: dashboard backend y panel admin backend básico.
- FASE 8: frontend funcional de usuario.

Ahora toca implementar solo la **FASE 9: Panel admin visual en frontend**.

## Restricciones metodológicas

- Trabaja únicamente dentro de `tfg-claude/`.
- No leas ni copies código de `tfg-codex/`.
- No leas ni copies código de `tfg-deepseek/`.
- No leas ni copies código del proyecto original.
- No uses documentos comparativos de fases 9, 10 u 11.
- No añadas funcionalidades fuera de esta fase.
- No rompas backend.
- No rompas frontend de usuario.
- No elimines tests existentes.
- Mantén React/Vite.
- Mantén FastAPI/SQLAlchemy/unittest.
- No implementes seed demo todavía.
- No implementes cierre documental todavía.

## Objetivo

Añadir un panel visual de administración al frontend para usuarios con rol admin.

Debe permitir:

1. Ver resumen global admin.
2. Ver listado de usuarios.
3. Editar datos básicos de usuarios si el backend lo permite.
4. Eliminar/desactivar usuarios si el backend lo permite.
5. Ver listado global de cultivos.
6. Editar cultivos si el backend lo permite.
7. Eliminar cultivos si el backend lo permite.
8. Ver listado global de tareas.
9. Editar tareas si el backend lo permite.
10. Eliminar tareas si el backend lo permite.
11. Proteger rutas admin en frontend.
12. Mostrar enlace admin solo si el usuario es admin.

## Rutas frontend esperadas

Añade rutas equivalentes a:

```text
/admin/dashboard
/admin/users
/admin/crops
/admin/tasks
```

## Componentes esperados

Crea componentes/páginas similares a:

```text
src/components/AdminRoute.jsx
src/pages/admin/AdminDashboard.jsx
src/pages/admin/AdminUsers.jsx
src/pages/admin/AdminCrops.jsx
src/pages/admin/AdminTasks.jsx
```

Adapta nombres y ubicaciones al proyecto real.

## Protección por rol

- Si no hay token, redirigir a login.
- Si el usuario no es admin, mostrar acceso denegado o redirigir.
- El enlace admin en Navbar solo debe verse si `user.role === "admin"` o equivalente.
- La seguridad real debe seguir estando en backend.

## API frontend

Amplía el cliente API para consumir endpoints admin existentes.

Endpoints orientativos:

```text
GET    /admin/summary
GET    /admin/users
PATCH  /admin/users/{id}
DELETE /admin/users/{id}
GET    /admin/crops
PATCH  /admin/crops/{id}
DELETE /admin/crops/{id}
GET    /admin/tasks
PATCH  /admin/tasks/{id}
DELETE /admin/tasks/{id}
```

Adapta a los endpoints reales de `tfg-claude/`.

## Normalización de respuestas

Maneja listas de forma defensiva. El backend puede devolver arrays directos o estructuras con `items`. Evita errores `.map is not a function` y `.filter is not a function`.

## UI mínima esperada

- Estados loading.
- Mensajes de error.
- Empty states.
- Tablas o cards.
- Botones para acciones disponibles.
- Confirmación antes de eliminar.
- Navegación clara entre secciones admin.

## Validación obligatoria

Ejecuta backend tests:

```bash
cd tfg-claude
python -m unittest discover -s tests -p "test*.py" -v
```

Ejecuta build frontend:

```bash
cd frontend
npm run build
```

Si PowerShell bloquea npm:

```bash
npm.cmd run build
```

## Validación visual

Arranca:

```bash
uvicorn app.main:app --reload
cd frontend
npm run dev
```

Comprueba:

- login usuario normal;
- usuario normal NO ve enlace admin;
- usuario normal NO puede acceder a `/admin/dashboard`;
- login admin;
- admin ve enlace admin;
- admin accede a dashboard admin;
- admin ve usuarios/cultivos/tareas;
- las páginas no muestran errores de consola.

Si no existe usuario admin todavía, documenta cómo crear uno temporalmente en SQLite para validar FASE 9. No implementes seed todavía.

## Entrega final

Incluye:

1. archivos creados;
2. archivos modificados;
3. rutas admin añadidas;
4. endpoints admin consumidos;
5. protección por rol implementada;
6. resultado de tests backend;
7. resultado de build frontend;
8. validación visual realizada;
9. limitaciones pendientes;
10. riesgos detectados;
11. confirmación de si FASE 9 queda completada.
