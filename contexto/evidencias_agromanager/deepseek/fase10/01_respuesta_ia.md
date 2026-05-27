# Respuesta IA — DeepSeek FASE 10

## Estado

FASE 10 completada, corregida y validada.

## Archivos creados

- `scripts/seed_demo.py`
- `tests/test_seed.py`
- `SEED_DEMO.md`

## Credenciales demo

- Admin: `admin@test.com / admin123`
- User: `user@test.com / user123`

## Datos creados

- 2 usuarios base.
- 5 cultivos públicos.
- 2 cultivos personales.
- 3 calendarios.
- 4 tareas.
- 7 registros de riego.
- 7 registros ambientales.
- 5 guías de cultivo.

## Tests añadidos

13 tests específicos de seed.

## Incidencia corregida

Se corrigió contaminación de `app.dependency_overrides[get_db]` entre `tests/test_api.py` y `tests/test_seed.py`.

## Estado final

Validado y cerrado.
