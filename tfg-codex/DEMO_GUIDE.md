# Guia de demo de AgroManager

Esta guia describe un recorrido completo para demostrar AgroManager en local con backend, frontend, seed demo y panel admin.

## URLs de referencia

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`
- Docs FastAPI: `http://127.0.0.1:8000/docs`

## 1. Preparar backend

```bash
cd tfg-codex
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## 2. Ejecutar seed demo

```bash
python scripts/seed_demo.py
```

Credenciales demo:

- Usuario: `user@test.com` / `user123`
- Admin: `admin@test.com` / `admin123`

## 3. Arrancar backend

```bash
uvicorn app.main:app --reload
```

Comprobar:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## 4. Preparar frontend

Abrir otra terminal:

```bash
cd tfg-codex/frontend
npm install
```

## 5. Arrancar frontend

```bash
npm run dev
```

Abrir:

- `http://localhost:5173`

## 6. Recorrido como usuario

1. Iniciar sesion con `user@test.com` / `user123`.
2. Revisar el dashboard de usuario.
3. Abrir "Mis cultivos" y comprobar los cultivos personales creados por el seed.
4. Abrir el catalogo publico y revisar cultivos disponibles.
5. Revisar el calendario agricola y las fases de cultivo.
6. Revisar tareas pendientes y completadas.
7. Consultar informacion de riego y requisitos ambientales desde los cultivos.

## 7. Recorrido como admin

1. Cerrar sesion.
2. Iniciar sesion con `admin@test.com` / `admin123`.
3. Abrir el panel admin.
4. Revisar resumen del dashboard admin.
5. Revisar usuarios.
6. Revisar cultivos.
7. Revisar tareas.
8. Probar cambios simples de administracion si procede para la demo.

## 8. Cierre de demo

1. Mostrar `http://127.0.0.1:8000/docs` para evidenciar la API.
2. Ejecutar tests de backend si se quiere demostrar validacion automatizada.
3. Ejecutar build frontend si se quiere demostrar preparacion para distribucion.
