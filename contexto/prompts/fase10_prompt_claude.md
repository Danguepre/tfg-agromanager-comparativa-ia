# FASE 10 — Seed/admin inicial y datos de ejemplo para Claude

Actúa como desarrollador full-stack senior especializado en FastAPI, SQLAlchemy, SQLite, scripts de inicialización y testing.

Vamos a continuar AgroManager dentro de `tfg-claude/`.

## Contexto

Claude Code tiene implementadas las fases 0 a 9:

- backend base;
- autenticación;
- usuarios;
- cultivos;
- catálogo;
- calendario agrícola;
- riego;
- requisitos ambientales;
- tareas;
- dashboard backend;
- endpoints admin backend;
- frontend de usuario;
- panel admin visual.

Ahora toca implementar solo la **FASE 10: Seed/admin inicial y datos de ejemplo**.

## Restricciones metodológicas

- Trabaja únicamente dentro de `tfg-claude/`.
- No leas ni copies código de `tfg-codex/`.
- No leas ni copies código de `tfg-deepseek/`.
- No leas ni copies código del proyecto original.
- No uses documentos comparativos de fases 10 u 11.
- No implementes funcionalidades grandes nuevas.
- No cambies arquitectura principal.
- No rompas backend.
- No rompas frontend.
- No elimines tests existentes.
- Mantén unittest.
- Mantén FastAPI/SQLAlchemy/SQLite.
- No uses secretos reales.

## Objetivo

Crear un script de seed demo idempotente que inicialice datos de demostración para AgroManager.

Debe permitir probar la aplicación sin manipular manualmente la base SQLite.

## Credenciales demo obligatorias

```text
Admin:
email: admin@test.com
password: admin123
role: admin

Usuario normal:
email: user@test.com
password: user123
role: user
```

Adapta campos como username/full_name según el modelo real.

## Datos demo esperados

El seed debe crear, como mínimo:

- 1 usuario admin;
- 1 usuario normal;
- 5 cultivos públicos;
- 2 cultivos personales para el usuario normal;
- calendarios asociados;
- tareas pendientes y completadas;
- información de riego;
- requisitos ambientales;
- guías o información adicional si el modelo ya existe.

Cultivos públicos sugeridos:

```text
Tomate
Lechuga
Zanahoria
Pimiento
Fresa
```

Cultivos personales sugeridos:

```text
Mi Tomate
Mi Lechuga
```

## Idempotencia obligatoria

El script debe poder ejecutarse múltiples veces sin duplicar datos de forma descontrolada.

Usa comprobaciones por:

- email para usuarios;
- nombre + is_public para cultivos públicos;
- owner_id + name para cultivos personales;
- crop_id para relaciones uno-a-uno;
- user_id + título/name para tareas.

Adapta a modelos reales.

## Ubicación recomendada

Crea:

```text
scripts/seed_demo.py
```

Si la carpeta `scripts/` no existe, créala.

## Documentación

Crea o actualiza:

```text
SEED_DEMO.md
```

Debe incluir objetivo del seed, comando de ejecución, credenciales demo, datos creados, explicación de idempotencia y validación manual recomendada.

## Tests obligatorios

Crea tests para el seed.

Archivo sugerido:

```text
tests/test_seed_demo.py
```

Casos mínimos:

- seed crea admin;
- seed crea usuario normal;
- passwords están hasheadas;
- admin puede hacer login;
- usuario normal puede hacer login;
- contraseña incorrecta falla;
- seed crea cultivos públicos;
- seed crea cultivos personales;
- seed crea tareas;
- hay tareas pendientes y completadas;
- seed es idempotente;
- segunda ejecución no duplica usuarios;
- catálogo público devuelve datos tras seed.

Muy importante: si usas `app.dependency_overrides[get_db]`, instálalo y límpialo dentro del ciclo de vida correcto para no contaminar otros tests.

## Validación obligatoria

Ejecuta:

```bash
cd tfg-claude
python scripts/seed_demo.py
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

Arranca backend y frontend:

```bash
uvicorn app.main:app --reload
cd frontend
npm run dev
```

Valida usuario normal y admin con credenciales demo, dashboard, cultivos, catálogo, calendario, tareas y panel admin.

## Entrega final

Incluye:

1. archivos creados;
2. archivos modificados;
3. comando exacto para seed;
4. credenciales demo;
5. datos demo creados;
6. estrategia de idempotencia;
7. tests añadidos;
8. resultado exacto de tests;
9. resultado exacto de build;
10. validación visual realizada;
11. limitaciones pendientes;
12. riesgos;
13. confirmación de si FASE 10 queda completada.
