# Incidencias — Claude FASE 10

## Ajuste solicitado

La primera versión funcionaba, pero no quedaba alineada con Codex/DeepSeek.

## Problemas detectados

- No incluía tests específicos de seed.
- Solo creaba un cultivo personal.
- Usaba Pepino en lugar de Pimiento.

## Corrección

- Añadido `tests/test_seed_demo.py` con 17 tests.
- Añadidos 2 cultivos personales: `Mi Tomate`, `Mi Lechuga`.
- Ajustados 5 cultivos públicos: Tomate, Lechuga, Zanahoria, Pimiento, Fresa.
