# FASE 11 — Cierre técnico, limpieza y documentación final para Claude

Actúa como desarrollador full-stack senior y responsable de cierre técnico de proyecto.

Vamos a continuar AgroManager dentro de `tfg-claude/`.

## Contexto

Claude Code tiene implementadas las fases 0 a 10:

- base del proyecto;
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
- panel admin visual;
- seed demo con datos iniciales.

Ahora toca implementar solo la **FASE 11: cierre técnico, limpieza y documentación final**.

## Restricciones metodológicas

- Trabaja únicamente dentro de `tfg-claude/`.
- No leas ni copies código de `tfg-codex/`.
- No leas ni copies código de `tfg-deepseek/`.
- No leas ni copies código del proyecto original.
- No uses documentos comparativos de fases 11.
- No añadas funcionalidades grandes nuevas.
- No implementes Alembic/migraciones todavía.
- No implementes tests E2E.
- No cambies arquitectura principal.
- No rompas backend.
- No rompas frontend.
- No rompas seed.
- No rompas panel admin.
- No elimines tests existentes.
- No uses secretos reales.
- Mantén unittest.
- Mantén React/Vite.
- Mantén FastAPI/SQLAlchemy.

## Objetivo

Dejar `tfg-claude/` listo para ejecución local, validación técnica, demostración, revisión y memoria del TFG.

## Documentos esperados

Crear o actualizar:

```text
README.md
.env.example
DEMO_GUIDE.md
VALIDATION.md
```

Si `.env.example` ya existe y está completo, revísalo y documenta que no fue necesario cambiarlo.

## README.md

Debe incluir nombre del proyecto, descripción, objetivo, stack, funcionalidades, estructura, requisitos, instalación, variables, ejecución backend/frontend, seed, credenciales demo, tests, build, validación visual, limitaciones y trabajo futuro.

## .env.example

Debe contener valores seguros de ejemplo si aplican:

```text
DATABASE_URL=sqlite:///./agromanager.db
SECRET_KEY=change-me-in-development
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

No inventes variables que el proyecto no usa.

## DEMO_GUIDE.md

Debe explicar paso a paso:

1. Crear entorno virtual.
2. Instalar dependencias backend.
3. Ejecutar seed.
4. Arrancar backend.
5. Instalar dependencias frontend.
6. Arrancar frontend.
7. Login como user.
8. Probar dashboard usuario.
9. Probar mis cultivos.
10. Probar catálogo.
11. Probar calendario.
12. Probar tareas.
13. Login como admin.
14. Probar panel admin.
15. Probar usuarios/cultivos/tareas admin.

URLs:

```text
Backend: http://127.0.0.1:8000
Frontend: http://localhost:5173
Docs FastAPI: http://127.0.0.1:8000/docs
```

## VALIDATION.md

Debe incluir comando seed, comando tests, comando build frontend, nota PowerShell para `npm.cmd run build`, resultado esperado, checklist manual usuario, checklist manual admin y limitaciones conocidas.

## Limpieza

Eliminar solo archivos temporales claramente innecesarios:

- `__pycache__`;
- `.pytest_cache`;
- `.pyc`;
- `test_result.txt`;
- logs temporales;
- scripts temporales de depuración;
- bases temporales de test si no son necesarias.

No eliminar tests, seed, documentación útil ni `agromanager.db` si contiene demo local.

## Validación final obligatoria

Ejecuta:

```bash
cd tfg-claude
python scripts/seed_demo.py
python -m unittest discover -s tests -p "test*.py" -v
cd frontend
npm run build
```

Si PowerShell bloquea npm:

```bash
npm.cmd run build
```

Comprueba que el seed sigue siendo idempotente.

## No implementar

No implementes nuevas pantallas grandes, gráficos, OAuth, Docker completo, Alembic, Playwright/Cypress, subida de imágenes ni permisos avanzados nuevos.

Esta fase es cierre técnico, no ampliación funcional.

## Entrega final

Indica:

1. archivos creados;
2. archivos modificados;
3. archivos eliminados;
4. documentación añadida;
5. cambios en README;
6. contenido de `.env.example`, si se creó;
7. comando exacto para seed;
8. comando exacto para backend;
9. comando exacto para frontend;
10. comando exacto para tests;
11. resultado de tests;
12. comando exacto para build;
13. resultado de build;
14. checklist de validación visual;
15. limitaciones conocidas documentadas;
16. riesgos pendientes;
17. si FASE 11 queda cerrada o queda algo pendiente.
