# Incidencias — DeepSeek FASE 8

## Incidencia — Base SQLite antigua

### Error inicial del dashboard

```text
Error: Error de red en /dashboard/summary: Failed to fetch
```

La consola backend mostraba:

```text
sqlite3.OperationalError: no such column: planting_calendars.planting_start
```

### Causa

La base local había sido creada con un esquema anterior. Los modelos actuales esperaban columnas nuevas en `planting_calendars`.

### Solución aplicada

- Borrar la base `.db` local.
- Reiniciar backend.
- Re-registrar usuario.

### Estado

Resuelto con reset de base local.

## Incidencias pendientes

| Incidencia | Severidad | Estado |
|---|---|---|
| Requiere reset DB por esquema antiguo | Media | Pendiente de migraciones |
| `npm audit` con 2 vulnerabilidades moderadas | Baja/Media | Pendiente |
| Frontend visualmente simple | Baja | Aceptable |
| No hay seed de datos | Baja | Pendiente |
| Suite backend más lenta | Baja | Aceptable por cobertura |
