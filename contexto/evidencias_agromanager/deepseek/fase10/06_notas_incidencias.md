# Incidencias — DeepSeek FASE 10

## Incidencia

La suite completa fallaba con:

sqlite3.OperationalError: no such table: users

## Causa

`tests/test_api.py` y `tests/test_seed.py` definían `app.dependency_overrides[get_db]` a nivel de módulo. Durante la carga de tests, un módulo sobrescribía el override del otro.

## Solución

- Mover overrides a `setUpClass()`.
- Limpiar overrides en `tearDownClass()`.
- Usar bases de test separadas.
- Cerrar engines con `dispose()` antes de borrar archivos.

## Validación posterior

117 tests ejecutados conjuntamente con resultado OK.

## Estado

Corregida. FASE 10 cerrada.
