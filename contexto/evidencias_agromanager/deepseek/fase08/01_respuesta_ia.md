# Respuesta IA — DeepSeek FASE 8

## Estado final

FASE 8 validada.

DeepSeek tuvo la mejor cobertura backend y un frontend funcional, aunque visualmente sencillo. Requirió reset de la base local para que el dashboard funcionara por un problema de esquema SQLite antiguo.

## Objetivo de la fase

Implementar un frontend funcional de usuario conectado con el backend de AgroManager.

## Resultado observado

DeepSeek implementó un frontend funcional con:

- Home.
- Registro.
- Login.
- Navbar.
- Dashboard.
- Mis Cultivos.
- Catálogo.
- Calendario.
- Tareas.
- Logout.
- Estados vacíos controlados.

## Incidencia principal

Antes de resetear la base, el dashboard fallaba con:

```text
Error: Error de red en /dashboard/summary: Failed to fetch
```

La consola backend mostraba:

```text
sqlite3.OperationalError: no such column: planting_calendars.planting_start
```

## Causa

La base local había sido creada con un esquema anterior. Los modelos actuales esperaban columnas nuevas en `planting_calendars`, como:

- `planting_start`
- `planting_end`
- `transplant_start`
- `transplant_end`
- `harvest_start`
- `harvest_end`

SQLite no añade columnas nuevas automáticamente con `create_all()`.

## Solución aplicada

- Borrar la base `.db` local.
- Reiniciar backend.
- Re-registrar usuario.

## Puntuación

```text
92/100
```

DeepSeek consiguió el mejor balance entre cobertura backend y frontend funcional. Aunque requirió reset de base para el dashboard, no tuvo un bug de renderizado como Claude y conservó la suite backend más amplia.
