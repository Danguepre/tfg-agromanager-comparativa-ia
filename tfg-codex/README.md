# AgroManager

AgroManager es una reconstruccion piloto de una aplicacion de gestion agricola para pequenos cultivos. El proyecto sirve como caso practico del TFG y cubre backend, frontend, datos de demostracion, panel de usuario, panel de administracion y validacion tecnica.

El objetivo no es entregar un producto listo para produccion, sino una base funcional, ejecutable y documentada que permita demostrar las decisiones tecnicas, el flujo completo de usuario y la integracion entre API y cliente web.

## Stack tecnologico

- FastAPI para la API REST.
- SQLAlchemy para modelos y acceso a datos.
- SQLite como base de datos local del piloto.
- React para la interfaz de usuario.
- Vite como servidor y herramienta de build frontend.
- Fetch API para comunicacion HTTP desde el frontend.
- unittest para pruebas automatizadas de backend.

## Funcionalidades principales

- Registro y login con JWT.
- Gestion de usuarios.
- Cultivos publicos y privados.
- Catalogo publico de cultivos.
- Seccion "Mis cultivos".
- Calendario agricola por fases.
- Gestion de tareas asociadas a cultivos.
- Informacion de riego.
- Requisitos ambientales.
- Dashboard de usuario.
- Panel admin visual.
- Seed demo idempotente con usuarios, cultivos, calendario, tareas, riego y requisitos ambientales.

## Estructura del proyecto

```text
tfg-codex/
  app/
    core/          Configuracion, base de datos, seguridad y dependencias.
    models/        Modelos SQLAlchemy.
    routes/        Endpoints FastAPI.
    schemas/       Schemas Pydantic.
    services/      Logica reutilizable de dominio.
    main.py        Creacion de la aplicacion FastAPI.
  frontend/
    src/           Aplicacion React.
    package.json   Scripts Vite.
  scripts/
    seed_demo.py   Seed de datos de demostracion.
  tests/           Tests unittest de backend.
  .env.example     Variables de entorno de ejemplo.
  DEMO_GUIDE.md    Guia paso a paso para demo.
  SEED_DEMO.md     Detalle del seed demo.
  VALIDATION.md    Guia tecnica de validacion.
```

## Requisitos previos

- Python 3.11 o superior.
- Node.js y npm.
- Windows PowerShell.

## Instalacion backend

Desde la carpeta superior del workspace:

```bash
cd tfg-codex
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Variables de entorno

El backend lee variables desde el entorno del sistema o desde un archivo `.env` local en la raiz de `tfg-codex/`. Hay valores de desarrollo por defecto, pero se recomienda copiar `.env.example` para dejar la configuracion explicita.

Variables principales:

- `APP_NAME`: nombre mostrado por FastAPI.
- `ENVIRONMENT`: entorno logico de ejecucion.
- `DATABASE_URL`: URL SQLAlchemy. Por defecto usa `sqlite:///./agromanager.db`.
- `SECRET_KEY`: clave local para firmar JWT. Debe cambiarse fuera de desarrollo.
- `ALGORITHM`: algoritmo JWT.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: duracion del token.
- `ALLOWED_ORIGINS`: origenes CORS separados por coma.
- `UPLOAD_DIR`: directorio local de archivos estaticos.
- `VITE_API_URL`: URL de la API usada por el frontend si se define en el entorno de Vite o en `frontend/.env`. Si no se define, el frontend usa `http://127.0.0.1:8000`.

No se incluyen secretos reales. Las claves de Google OAuth estan reservadas en configuracion, pero el flujo OAuth no forma parte de esta fase.

## Ejecutar backend

```bash
cd tfg-codex
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

URLs utiles:

- API: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/`
- Docs FastAPI: `http://127.0.0.1:8000/docs`

## Instalacion frontend

En otra terminal:

```bash
cd tfg-codex/frontend
npm install
```

## Ejecutar frontend

```bash
cd tfg-codex/frontend
npm run dev
```

URL del frontend:

- `http://localhost:5173`

## Ejecutar seed demo

Con el entorno virtual activo:

```bash
cd tfg-codex
python scripts/seed_demo.py
```

El seed es idempotente: puede ejecutarse varias veces y reutiliza los datos existentes cuando ya estan creados.

Credenciales demo:

- Admin: `admin@test.com` / `admin123`
- Usuario: `user@test.com` / `user123`

Mas detalle en [SEED_DEMO.md](SEED_DEMO.md).

## Ejecutar tests

```bash
cd tfg-codex
python -m unittest discover -s tests -p "test*.py" -v
```

## Ejecutar build frontend

```bash
cd tfg-codex/frontend
npm.cmd run build
```

Nota PowerShell: si `npm run build` falla por la politica local de ejecucion de `npm.ps1`, usar `npm.cmd run build`.

## Validacion visual

1. Ejecutar backend en `http://127.0.0.1:8000`.
2. Ejecutar frontend en `http://localhost:5173`.
3. Ejecutar el seed demo.
4. Entrar como `user@test.com` y revisar dashboard, catalogo, mis cultivos, calendario y tareas.
5. Entrar como `admin@test.com` y revisar dashboard admin, usuarios, cultivos y tareas.
6. Abrir `http://127.0.0.1:8000/docs` para comprobar la documentacion OpenAPI.

## Limitaciones conocidas

- No hay migraciones Alembic; las tablas se crean al arrancar y hay ajustes aditivos para compatibilidad local.
- SQLite es adecuado para el piloto, pero produccion deberia usar una base de datos como PostgreSQL.
- No hay tests E2E automatizados.
- El flujo Google OAuth esta solo preparado a nivel de configuracion.
- La gestion de subida de imagenes es basica.
- Las credenciales demo son solo para entorno local.

## Riesgos pendientes

- Endurecer seguridad antes de produccion: secretos reales, rotacion de claves, politicas CORS y HTTPS.
- Definir migraciones formales antes de evolucionar el modelo de datos.
- Ampliar validaciones de permisos en escenarios de administracion mas complejos.
- Revisar estrategia de backups y despliegue.
- Incorporar observabilidad y logging estructurado.

## Trabajo futuro

- Anadir Alembic para migraciones.
- Sustituir SQLite por PostgreSQL en despliegue real.
- Incorporar tests E2E y pruebas visuales.
- Mejorar gestion de imagenes y almacenamiento externo.
- Completar funcionalidades avanzadas de planificacion agricola.
- Preparar despliegue documentado para un entorno cloud o servidor propio.
