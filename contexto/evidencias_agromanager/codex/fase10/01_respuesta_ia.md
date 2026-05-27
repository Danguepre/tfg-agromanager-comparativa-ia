# Respuesta IA — Codex FASE 10

## Estado

FASE 10 completada y validada.

## Archivos creados

- `scripts/seed_demo.py`
- `tests/test_seed_demo.py`
- `SEED_DEMO.md`

## Archivos modificados

- `README.md`

## Comando seed

```bash
cd tfg-codex
python scripts/seed_demo.py
```

## Credenciales demo

- Admin: `admin@test.com / admin123`
- Usuario: `user@test.com / user123`

## Datos creados

- 2 usuarios demo.
- 5 cultivos públicos.
- 2 cultivos personales.
- 7 calendarios.
- 4 tareas.
- 4 relaciones tarea-cultivo.
- 7 datos de riego.
- 7 requisitos ambientales.
- 7 guías de cultivo.

## Idempotencia

El seed evita duplicados buscando por:

- email para usuarios;
- `name + is_public` para cultivos públicos;
- `owner_id + name` para cultivos personales;
- relaciones uno-a-uno por cultivo;
- `user_id + task name` para tareas.

## Estado final

Validado y cerrado.
