# FASE 8 — Frontend funcional de usuario

Actúa como desarrollador frontend/full-stack senior especializado en React, Vite y conexión con APIs FastAPI.

Vamos a continuar AgroManager con la **FASE 8: Frontend funcional de usuario**.

## Contexto

Ya existe un backend funcional con:

- autenticación;
- usuarios;
- cultivos;
- catálogo;
- calendario;
- tareas;
- riego;
- requisitos ambientales;
- dashboard backend;
- endpoints admin backend.

Ahora toca construir un frontend funcional para usuario normal.

## Restricciones

- Trabaja únicamente dentro de la carpeta del proyecto actual.
- No leas ni copies código de otros proyectos.
- No implementes todavía panel admin visual.
- No cambies innecesariamente el backend.
- No rompas tests backend.
- Mantén React y Vite.
- Usa Fetch API nativo salvo que el proyecto ya use otra cosa.
- No añadas librerías pesadas si no son necesarias.
- No uses datos mock si ya existen endpoints reales.
- No implementes diseño avanzado; prioriza funcionalidad, claridad y validación.

## Objetivo

Crear frontend de usuario que permita:

1. Página inicial.
2. Registro.
3. Login.
4. Logout.
5. Rutas protegidas.
6. Layout con navegación.
7. Dashboard de usuario.
8. Mis cultivos.
9. Catálogo público.
10. Detalle de cultivo si procede.
11. Calendario.
12. Tareas.
13. Sesión/perfil básico.

## Páginas esperadas

Crea o actualiza páginas equivalentes a:

```text
/
/login
/register
/dashboard
/crops
/catalog
/crops/:id
/calendar
/tasks
/session
```

Adapta a la arquitectura existente.

## Componentes esperados

- AuthContext o equivalente.
- ProtectedRoute.
- Layout.
- Navbar.
- Cliente API centralizado.
- Formularios login/register.
- Cards/listados básicos.

## Cliente API

Debe centralizar llamadas al backend.

Debe gestionar:

- base URL;
- token en Authorization;
- errores HTTP;
- 401;
- 403;
- respuestas JSON;
- listas directas o respuestas paginadas.

Muy importante: si el backend devuelve listas como `{ total, skip, limit, items }`, el frontend debe normalizar para que los componentes trabajen con arrays seguros. Evita errores `.filter is not a function` o `.map is not a function`.

## Reglas de UI

- Si no hay datos, mostrar mensaje claro.
- Si hay error, mostrar mensaje legible.
- Si está cargando, mostrar estado loading.
- Si no hay token, redirigir a login.
- Si login funciona, redirigir a dashboard.
- Logout debe limpiar sesión.
- No mostrar rutas privadas a usuarios no autenticados.

## Validación frontend

Ejecuta:

```bash
cd frontend
npm install
npm run build
```

Si PowerShell bloquea `npm.ps1`, usar:

```bash
npm.cmd run build
```

## Validación backend

Ejecuta desde la raíz:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

## Validación manual recomendada

Arranca backend y frontend:

```bash
uvicorn app.main:app --reload
cd frontend
npm run dev
```

Comprueba:

- registro;
- login;
- dashboard;
- mis cultivos;
- catálogo;
- tareas;
- calendario;
- logout.

## Entrega final

Incluye:

1. archivos creados;
2. archivos modificados;
3. rutas frontend implementadas;
4. endpoints consumidos;
5. decisiones técnicas;
6. resultado de `npm run build`;
7. resultado de tests backend;
8. limitaciones pendientes;
9. riesgos;
10. confirmación de FASE 8 completada.
