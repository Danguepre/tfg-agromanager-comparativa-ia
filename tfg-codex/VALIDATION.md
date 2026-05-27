# Validacion tecnica de AgroManager

Esta guia recoge los comandos de cierre tecnico para validar seed, backend, tests y build frontend.

## Seed demo

```bash
cd tfg-codex
python scripts/seed_demo.py
```

Resultado esperado:

- El comando termina sin excepciones.
- Imprime `AgroManager demo seed completed.`
- Muestra resumen de entidades creadas o existentes.

## Tests backend

```bash
cd tfg-codex
python -m unittest discover -s tests -p "test*.py" -v
```

Resultado esperado:

- Todos los tests terminan en `OK`.
- Validacion final confirmada: `Ran 52 tests` y resultado `OK`.

## Build frontend

```bash
cd tfg-codex/frontend
npm.cmd run build
```

Resultado esperado:

- El comando termina sin errores.
- Validacion final confirmada: Vite termina con `built`.

Nota PowerShell:

- Si `npm run build` falla por la politica local con `npm.ps1`, usar `npm.cmd run build`.

## Checklist manual

- Login admin.
- Login user.
- Dashboard usuario.
- Catalogo.
- Mis cultivos.
- Calendario.
- Tareas.
- Admin dashboard.
- Admin users.
- Admin crops.
- Admin tasks.

## Comprobaciones de URLs

- Backend: `http://127.0.0.1:8000`
- Docs FastAPI: `http://127.0.0.1:8000/docs`
- Frontend: `http://localhost:5173`
