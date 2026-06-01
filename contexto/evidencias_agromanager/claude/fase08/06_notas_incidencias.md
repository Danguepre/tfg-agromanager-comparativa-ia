# Incidencias — Claude Code FASE 8

## Incidencia 1 — Base SQLite antigua

### Error observado

```text
Error: Failed to fetch
```

La consola backend mostró:

```text
sqlite3.OperationalError: no such column: crops.crop_type
```

### Causa

La base local `app.db` había sido creada con un esquema antiguo. El modelo actual esperaba la columna `crops.crop_type`, pero SQLite no la tenía.

### Solución aplicada

- Borrar la base local.
- Reiniciar backend.
- Re-registrar usuario.

### Clasificación

No se considera fallo directo del frontend. Es una incidencia de migración/esquema local.

## Incidencia 2 — `published.filter is not a function`

### Error observado

```text
Crops.jsx:51 Uncaught TypeError: published.filter is not a function
```

### Causa

El backend devolvía una respuesta paginada tipo `{ total, skip, limit, items }`, pero el frontend esperaba un array directo.

### Corrección aplicada

- Nueva función `normalizeListResponse()`.
- Soporte para array directo, `{ items: [...] }`, `{ crops: [...] }`, `{ data: [...] }`.
- Validaciones defensivas antes de `.filter()`, `.map()` y `.length`.

### Estado

Corregido.

## Incidencias pendientes

| Incidencia | Severidad | Estado |
|---|---|---|
| Requiere borrar DB local cuando cambia esquema | Media | Pendiente de migraciones reales |
| `npm audit` con 2 vulnerabilidades moderadas | Baja/Media | Pendiente |
| Mantiene desviaciones previas como `/auth/register` | Baja | Documentada |
| Redirects 307 en varias rutas backend | Baja | No bloqueante |
| Necesitó segunda iteración para normalizar listas | Media | Corregido |
