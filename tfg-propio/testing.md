# Testing

Este proyecto no tenia framework de tests configurado. La bateria actual usa las herramientas ya disponibles:

- Backend/API: `unittest` de Python + `fastapi.testclient.TestClient`.
- Frontend: `eslint` como test estatico y `vite build` como comprobacion de compilacion.
- E2E: flujos HTTP completos con `TestClient` contra la app FastAPI real.

No se ha añadido Playwright, Cypress, Vitest ni pytest para evitar dependencias nuevas innecesarias.

## Base de Datos de Test

Los tests no usan PostgreSQL ni datos reales. Cada proceso de test configura:

```text
DATABASE_URL=sqlite:///./test_app_<pid>.db
APP_ENV=test
RUN_SEED=0
```

Cada test borra y recrea las tablas con los modelos SQLAlchemy, por lo que el estado es repetible e independiente.

## Datos de Prueba

Los fixtures crean:

- 1 usuario admin.
- 2 usuarios normales.
- cultivos globales de catalogo.
- cultivos asociados a usuarios.
- cultivos con calendario completo.
- cultivos sin calendario completo.
- cultivos de distintos tipos.

Las contrasenas se guardan hasheadas con la funcion real `hash_password`.

## Comandos

Desde `tfg-copilot`:

```bash
npm run test
npm run test:backend
npm run test:frontend
npm run test:e2e
npm run lint
```

Para build de produccion del frontend:

```bash
cd frontend
npm run build
```

Nota Windows: en este entorno, Vite falla con `spawn EPERM` si el build se lanza desde un script npm situado en la carpeta padre. Ejecutar `npm run build` directamente dentro de `frontend` funciona correctamente.

## Cobertura Actual

Backend/API:

- arranque basico del backend;
- registro;
- login correcto e incorrecto;
- rutas protegidas sin token;
- token invalido;
- inicio de OAuth Google sin intercambio de red;
- permisos admin `403` para usuario normal;
- listado, creacion, edicion y eliminacion de usuarios admin;
- no exposicion de password en respuestas;
- proteccion contra borrado propio de admin;
- listado, creacion, edicion y eliminacion de cultivos admin;
- filtros y paginacion del catalogo;
- copia de cultivo desde catalogo;
- independencia entre original y copia;
- alcance de "Mis cultivos" por usuario;
- permisos contra edicion/eliminacion de cultivos ajenos;
- quitar un cultivo original de "Mis cultivos" manteniendolo en catalogo;
- validacion backend de calendario incompleto;
- activacion de calendario completo;
- fase actual unica;
- avance de fase;
- fin de ciclo en ultima fase;
- permisos de avance;
- independencia del ano en fases, usando mes y quincena.

E2E:

- flujo de usuario normal: login, catalogo, filtros, copiar cultivo, editar copia, configurar calendario, activar, ver fase y avanzar fase;
- flujo admin: login admin, bloqueo a usuario normal, resumen, crear/editar/eliminar usuario, crear/editar/eliminar cultivo.

Frontend:

- lint de React/Vite;
- build de produccion.

## Como Anadir Tests

Para backend/API, anade tests en `tests/test_api.py` o crea un nuevo `tests/test_*.py`.

Usa `ApiTestCase` si necesitas:

- base de datos limpia por test;
- usuarios admin/user ya creados;
- cultivos de catalogo y de usuario;
- helper `auth_headers(email)`.

Para flujos completos, anade tests en `tests/e2e/test_flows.py`.

## Si Falla un Test

1. Ejecuta primero el grupo concreto:
   - `npm run test:backend`
   - `npm run test:e2e`
   - `npm run test:frontend`
2. Mira el codigo HTTP esperado y el JSON devuelto.
3. Si falla por datos, revisa el fixture en `ApiTestCase.seed_base_data`.
4. Si falla el build frontend, ejecuta:
   - `cd frontend`
   - `npm run lint`
   - `npm run build`

## Limitaciones

No hay tests de navegador real porque no hay Playwright/Cypress instalado. Los flujos E2E actuales validan la API completa y la persistencia, pero no hacen clicks reales ni comprobaciones visuales. Para cubrir UI real en el futuro, se recomienda anadir Playwright con un servidor backend/frontend de test.
