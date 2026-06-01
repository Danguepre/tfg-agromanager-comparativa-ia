# Contexto maestro para reconstruccion con IA

Este documento resume el estado final del proyecto `tfg-copilot` para generar prompts reproducibles y comparar el resultado de diferentes IAs. La idea es que todas reciban el mismo contexto, las mismas fases y los mismos criterios de aceptacion.

## 1. Objetivo del experimento

Comparar como distintas herramientas de IA reconstruyen una aplicacion web completa de gestion de cultivos a partir de una especificacion comun.

La comparacion debe medir:

- cumplimiento funcional;
- calidad de arquitectura;
- seguridad y control de permisos;
- calidad de frontend;
- calidad de API;
- persistencia de datos;
- tests;
- mantenibilidad;
- numero de iteraciones necesarias para llegar a una version funcional.

## 2. Proyecto final esperado

Nombre funcional: AgroManager.

Aplicacion web para gestionar cultivos personales y un catalogo de cultivos publicados. Incluye autenticacion, roles, panel de usuario, panel de administracion, calendario agricola por fases, tareas asociadas a cultivos, requisitos ambientales, informacion de riego y tests automatizados.

## 3. Stack tecnologico

Backend:

- Python.
- FastAPI.
- SQLAlchemy ORM.
- Pydantic.
- PostgreSQL en desarrollo por defecto.
- SQLite para tests.
- JWT con `python-jose`.
- Hash de passwords con `passlib[bcrypt]`.
- CORS configurable.
- Google OAuth opcional mediante `httpx`.
- Archivos estaticos para imagenes en `/uploads`.

Frontend:

- React.
- Vite.
- React Router.
- Fetch API.
- CSS e inline styles.
- Persistencia del token en `localStorage`.

Testing:

- `unittest`.
- `fastapi.testclient.TestClient`.
- E2E HTTP con la app FastAPI real.
- Lint/build del frontend con npm.

## 4. Estructura principal

```text
tfg-copilot/
  app/
    main.py
    database.py
    auth.py
    dependencies.py
    seed.py
    models/
    schemas/
    routes/
    services/
  frontend/
    src/
      api/
      components/
      context/
      pages/
      utils/
    package.json
    vite.config.js
  tests/
    test_api.py
    e2e/test_flows.py
  requirements.txt
  package.json
  TESTING.md
```

No deben incluirse en el contexto de reconstruccion archivos generados o temporales como `__pycache__`, bases de datos `test_app*.db`, `node_modules`, `.venv`, `.env`, logs o secretos.

## 5. Variables de entorno

Variables relevantes:

```env
APP_ENV=development
DATABASE_URL=postgresql://postgres:admin@localhost:5432/tfg_db
RUN_SEED=0
FRONTEND_URL=http://127.0.0.1:5173
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_OAUTH_REDIRECT=http://127.0.0.1:8000/auth/google/callback
```

En tests:

```env
APP_ENV=test
RUN_SEED=0
DATABASE_URL=sqlite:///./test_app_<pid>.db
```

## 6. Modelo de datos

### User

Campos:

- `id`
- `name`
- `email`, unico e indexado
- `password`, hasheado
- `location`
- `role`, con valores principales `user` y `admin`
- `created_at`

Relaciones:

- un usuario tiene muchos cultivos;
- un usuario tiene muchas tareas.

### Crop

Campos:

- `id`
- `name`
- `type`
- `life_cycle`
- `image_url`
- `user_id`, nullable
- `is_public`
- `source_crop_id`, nullable, para copias desde catalogo
- `created_at`

Relaciones:

- pertenece opcionalmente a un usuario;
- puede ser una copia de otro cultivo;
- tiene un calendario;
- tiene datos ambientales;
- tiene datos de riego;
- tiene pasos de guia;
- se asocia a tareas mediante tabla intermedia.

Comportamiento importante:

- los cultivos publicados forman el catalogo;
- un usuario puede copiar un cultivo del catalogo a "Mis cultivos";
- la copia debe ser independiente del original;
- si un usuario elimina un cultivo original suyo, pasa a catalogo publico en vez de desaparecer totalmente;
- al crear un cultivo se crean datos de riego y ambientales por defecto.

### PlantingCalendar

Campos:

- `id`
- `crop_id`
- `planting_start`
- `planting_end`
- `transplant_start`
- `transplant_end`
- `harvest_start`
- `harvest_end`
- `is_active`
- `current_phase_index`
- `status`

Fases:

1. Siembra.
2. Trasplante.
3. Cosecha.

Reglas:

- un calendario solo puede activarse si tiene completas las fechas de siembra, trasplante y cosecha;
- los eventos de calendario se muestran por mes y quincena, ignorando el ano;
- al avanzar una fase se incrementa `current_phase_index`;
- al avanzar desde la ultima fase, el calendario queda `completed` e inactivo.

### IrrigationAttributes

Campos:

- `id`
- `crop_id`
- `watering_frequency`
- `water_amount`
- `recommendations`

### EnvironmentalRequirements

Campos:

- `id`
- `crop_id`
- `sun_exposure`
- `min_temp`
- `max_temp`
- `frost_tolerance`

### CultivationGuide

Campos:

- `id`
- `crop_id`
- `step_number`
- `description`

### Task

Campos:

- `id`
- `user_id`
- `name`
- `description`
- `status`
- `created_at`

Relaciones:

- pertenece a un usuario;
- se puede asociar a uno o varios cultivos mediante `TaskCrop`.

### TaskCrop

Campos:

- `id`
- `task_id`
- `crop_id`

## 7. Backend esperado

La app FastAPI debe:

- cargar variables de entorno desde `.env`;
- crear tablas automaticamente solo en entorno de desarrollo;
- montar `/uploads`;
- permitir CORS en desarrollo para Vite;
- incluir routers de usuarios, auth, cultivos, calendario, riego, ambiental, tareas, admin y dashboard;
- exponer `GET /` con un mensaje basico de salud.

### Autenticacion y permisos

Debe existir:

- registro de usuario en `POST /users/`;
- login en `POST /auth/login`;
- token JWT con `user_id` y `role`;
- dependencia `get_current_user`;
- acceso protegido con header `Authorization: Bearer <token>`;
- rol `admin` con acceso ampliado;
- Google OAuth opcional en `GET /auth/google` y callback en `GET /auth/google/callback`.

Reglas de permisos:

- un usuario normal solo ve y modifica sus propios recursos;
- un admin puede ver y gestionar recursos globales;
- un usuario normal no puede crear recursos para otro usuario;
- un usuario normal no puede publicar cultivos;
- endpoints `/admin/*` requieren rol admin.

## 8. Endpoints funcionales

### Usuarios y auth

- `POST /users/`: registrar usuario normal.
- `GET /users/`: admin ve todos, usuario normal se ve a si mismo.
- `GET /users/{user_id}`: obtener usuario si es admin o propietario.
- `DELETE /users/{user_id}`: borrar usuario si es admin o propietario.
- `POST /auth/login`: login email/password.
- `GET /auth/google`: inicia flujo OAuth Google.
- `GET /auth/google/callback`: procesa callback, crea usuario local si no existe y redirige al frontend con JWT.

### Cultivos

- `POST /crops/`: crear cultivo con `multipart/form-data`.
- `GET /crops/`: listar cultivos visibles.
- `GET /crops/my`: listar cultivos del usuario con paginacion.
- `GET /crops/published`: catalogo con filtros `name`, `type` y paginacion.
- `POST /crops/{crop_id}/add-to-my-crops`: copiar cultivo del catalogo.
- `GET /crops/{crop_id}`: obtener cultivo.
- `GET /crops/user/{user_id}`: cultivos por usuario.
- `PUT /crops/{crop_id}`: actualizar cultivo.
- `DELETE /crops/{crop_id}`: quitar/eliminar cultivo segun origen.

### Calendario

- `POST /calendar/`: crear calendario.
- `GET /calendar/`: listar calendarios visibles.
- `GET /calendar/events`: eventos activos del usuario.
- `PUT /calendar/crop/{crop_id}`: crear o actualizar calendario de un cultivo.
- `POST /calendar/crop/{crop_id}/activate`: activar calendario si esta completo.
- `POST /calendar/crop/{crop_id}/advance`: avanzar fase.
- `GET /calendar/{calendar_id}`: obtener calendario.
- `GET /calendar/{calendar_id}/events`: eventos de calendario.
- `GET /calendar/crop/{crop_id}`: calendario por cultivo.
- `PUT /calendar/{calendar_id}`: actualizar calendario.
- `DELETE /calendar/{calendar_id}`: eliminar calendario.

### Riego y requisitos ambientales

Riego:

- `POST /irrigation/`
- `GET /irrigation/`
- `GET /irrigation/{irrigation_id}`
- `GET /irrigation/crop/{crop_id}`
- `PUT /irrigation/{irrigation_id}`
- `DELETE /irrigation/{irrigation_id}`

Ambiental:

- `POST /environmental/`
- `GET /environmental/`
- `GET /environmental/{env_id}`
- `GET /environmental/crop/{crop_id}`
- `PUT /environmental/{env_id}`
- `DELETE /environmental/{env_id}`

### Tareas

- `POST /tasks/`: crear tarea.
- `GET /tasks/`: listar tareas visibles.
- `GET /tasks/{task_id}`: obtener tarea.
- `GET /tasks/user/{user_id}`: tareas por usuario.
- `GET /tasks/crop/{crop_id}`: tareas de un cultivo.
- `POST /tasks/assign`: asociar tarea a cultivo.
- `PATCH /tasks/{task_id}`: actualizar parcialmente, sobre todo estado.
- `PUT /tasks/{task_id}`: actualizar completa.
- `DELETE /tasks/{task_id}`: borrar tarea.
- `GET /tasks/{task_id}/crops`: cultivos asociados a una tarea.

### Dashboard

- `GET /dashboard/summary`: resumen personal.

Debe devolver:

- numero de cultivos del usuario;
- calendarios activos;
- tareas pendientes;
- tareas vencidas, actualmente 0;
- cultivos con fases incompletas;
- hasta 5 tareas pendientes;
- hasta 6 calendarios activos;
- hasta 6 avisos.

### Admin

- `GET /admin/summary`.
- `GET /admin/users` con filtros `search`, `role`, `page`, `page_size`.
- `POST /admin/users`.
- `PUT /admin/users/{user_id}`.
- `DELETE /admin/users/{user_id}`.
- `GET /admin/crops` con filtros `name`, `type`, `user_id`, `kind`, `page`, `page_size`.
- `POST /admin/crops`.
- `PUT /admin/crops/{crop_id}`.
- `DELETE /admin/crops/{crop_id}`.

Reglas admin importantes:

- no se debe exponer password en respuestas;
- no se puede eliminar el propio usuario admin;
- no se puede borrar ni degradar el ultimo admin;
- al eliminar usuario, sus cultivos quedan sin propietario;
- al eliminar cultivo admin, se eliminan relaciones y datos asociados.

## 9. Frontend esperado

La primera pantalla para usuario sin token es una home publica con llamadas a login y registro.

Rutas:

- `/`: home si no hay token, redirige a dashboard si hay token.
- `/login`: login email/password y boton Google.
- `/signup`: registro y login posterior.
- `/oauth/callback`: recibe token o error de OAuth.
- `/dashboard`: panel personal.
- `/crops`: mis cultivos.
- `/published-crops`: catalogo publicado.
- `/tasks`: tareas.
- `/calendar`: calendario por meses y quincenas.
- `/admin`, `/admin/users`, `/admin/crops`: panel admin.

Componentes clave:

- `AuthProvider`: guarda token en estado y `localStorage`.
- `ProtectedRoute`: bloquea rutas privadas.
- `AdminRoute`: permite solo role admin.
- `Navbar`: navegacion principal y logout.
- `NotificationBanner`: avisa de eventos activos en la quincena actual.
- `CropTasks`: tareas asociadas dentro del detalle de cultivo.

Paginas esperadas:

- Dashboard: tarjetas de resumen, accesos rapidos, tareas pendientes, calendarios activos y avisos.
- PublishedCrops: catalogo con filtros, paginacion, indicador de cultivo ya anadido y accion para copiar a mis cultivos.
- Crops: listado paginado de cultivos personales, crear cultivo con imagen opcional, detalle, editar, eliminar/quitar, editar riego, ambiente, calendario y tareas.
- Calendar: vista de 12 meses divididos en primera y segunda quincena; muestra fase actual y permite avanzar fase.
- Tasks: listado de tareas, filtros por estado, creacion, asignacion a cultivo, completar/reabrir y eliminar.
- Admin: resumen global, gestion paginada de usuarios, gestion paginada de cultivos, filtros y formularios.

## 10. Imagenes y uploads

El backend debe soportar:

- subida manual de imagen al crear cultivo;
- almacenamiento en `uploads/crops`;
- URL servida desde `/uploads/...`;
- imagen por defecto o busqueda/descarga si no se sube imagen, siempre de forma tolerante a fallos.

Para reconstruccion, se puede implementar una version simple siempre que no bloquee la creacion de cultivos.

## 11. Seed de datos

Debe existir una funcion de seed opcional que cree:

- usuario admin `admin@test.com` con password `1234`;
- usuarios normales de prueba;
- cultivos variados;
- calendarios;
- datos ambientales;
- datos de riego;
- tareas;
- relaciones tarea-cultivo.

El seed solo debe ejecutarse si `RUN_SEED` es verdadero.

## 12. Tests esperados

Debe existir bateria de tests que cubra:

- root backend;
- existencia/configuracion basica del frontend;
- registro;
- login correcto;
- login incorrecto;
- acceso protegido sin token;
- token invalido;
- inicio de OAuth Google sin intercambio real de token;
- permisos admin prohibidos a usuarios normales;
- gestion admin de usuarios;
- no exposicion de password;
- proteccion contra borrar/degradar ultimo admin;
- gestion admin de cultivos;
- filtros y paginacion de catalogo;
- copia de cultivo desde catalogo;
- independencia original/copia;
- alcance de "Mis cultivos";
- permisos contra editar o borrar recursos ajenos;
- quitar cultivo manteniendolo en catalogo;
- rechazo de calendario incompleto;
- activacion de calendario completo;
- eventos por fase actual;
- avance de fase;
- completar ciclo;
- permisos de calendario;
- independencia del ano en los eventos;
- dashboard sin fuga de datos de otros usuarios;
- flujo E2E de usuario normal;
- flujo E2E de admin.

Comandos:

```bash
npm run test
npm run test:backend
npm run test:frontend
npm run test:e2e
npm run lint
```

## 13. Criterios de aceptacion globales

Una reconstruccion se considera valida si:

- backend arranca sin errores;
- frontend compila;
- se puede registrar y hacer login;
- el token se guarda y protege rutas;
- usuario normal solo accede a sus datos;
- admin puede gestionar usuarios y cultivos;
- catalogo publicado funciona con filtros y paginacion;
- copiar cultivo desde catalogo crea copia independiente;
- mis cultivos permite crear, editar, ver detalle y quitar;
- calendario permite configurar, activar, ver fase actual y avanzar;
- tareas se crean, asignan, completan y eliminan;
- dashboard resume datos personales;
- tests automaticos pasan;
- no se requieren secretos reales para ejecutar tests;
- no se suben archivos temporales ni credenciales.

## 14. Prompts para reconstruir el proyecto

Usar estos prompts en el mismo orden con cada IA. Para comparacion justa, no dar codigo final salvo que se indique expresamente. Dar siempre el mismo contexto inicial.

### Prompt 0: rol, restricciones y formato de trabajo

```text
Actua como un desarrollador full-stack senior. Vas a reconstruir una aplicacion web llamada AgroManager para gestion de cultivos.

Restricciones:
- Usa backend Python con FastAPI, SQLAlchemy y Pydantic.
- Usa frontend React con Vite y React Router.
- Usa PostgreSQL por defecto y SQLite para tests.
- Implementa JWT para autenticacion.
- No incluyas secretos reales.
- Mantener codigo modular y testeable.
- Entregar cambios por fases.

Necesito que implementes el proyecto completo siguiendo los requisitos que te dare por fases. En cada fase indica archivos creados/modificados, decisiones tomadas y como verificarlo.
```

### Prompt 1: arquitectura base

```text
Crea la estructura base del proyecto AgroManager.

Debe incluir:
- backend FastAPI en `app/`;
- modelos, schemas, routes y services separados;
- configuracion de base de datos con SQLAlchemy;
- lectura de variables de entorno;
- lifespan que cree tablas solo en desarrollo;
- CORS configurable;
- montaje de `/uploads`;
- frontend React/Vite en `frontend/`;
- scripts npm de test, lint y build;
- README o notas de ejecucion.

Criterios de aceptacion:
- `GET /` devuelve un JSON de salud;
- el backend puede arrancar con uvicorn;
- el frontend puede arrancar con Vite;
- no hay secretos reales hardcodeados salvo placeholders de desarrollo documentados.
```

### Prompt 2: modelos y schemas

```text
Implementa los modelos SQLAlchemy y schemas Pydantic para:
- User;
- Crop;
- PlantingCalendar;
- CultivationGuide;
- IrrigationAttributes;
- EnvironmentalRequirements;
- Task;
- TaskCrop.

Incluye relaciones entre entidades y respuestas que no expongan passwords.

Reglas clave:
- Crop puede ser publico, pertenecer a un usuario o ser copia de otro cultivo.
- PlantingCalendar tiene fases de siembra, trasplante y cosecha, estado, fase actual y activacion.
- Task se puede asociar a varios cultivos.

Criterios de aceptacion:
- las tablas se crean correctamente;
- las respuestas incluyen relaciones utiles como calendar, irrigation y environmental cuando proceda;
- no se devuelve password en ningun schema publico.
```

### Prompt 3: autenticacion y usuarios

```text
Implementa autenticacion y usuarios.

Debe incluir:
- registro `POST /users/`;
- login `POST /auth/login`;
- password hasheada;
- JWT con `user_id` y `role`;
- dependencia `get_current_user`;
- permisos de usuario normal y admin;
- rutas `GET /users/`, `GET /users/{id}`, `DELETE /users/{id}`;
- Google OAuth opcional con `GET /auth/google` y `GET /auth/google/callback`, sin requerir credenciales reales para tests.

Criterios de aceptacion:
- login correcto devuelve `access_token`;
- login incorrecto devuelve error;
- rutas protegidas fallan sin token;
- usuario normal solo ve sus propios datos;
- admin ve todos.
```

### Prompt 4: cultivos y catalogo

```text
Implementa gestion de cultivos.

Endpoints:
- `POST /crops/`;
- `GET /crops/`;
- `GET /crops/my`;
- `GET /crops/published`;
- `POST /crops/{crop_id}/add-to-my-crops`;
- `GET /crops/{crop_id}`;
- `GET /crops/user/{user_id}`;
- `PUT /crops/{crop_id}`;
- `DELETE /crops/{crop_id}`.

Requisitos:
- crear cultivo con multipart/form-data;
- aceptar imagen opcional;
- crear riego y datos ambientales por defecto;
- catalogo con filtros por nombre/tipo y paginacion;
- copia desde catalogo independiente del original;
- permisos por propietario;
- solo admin puede publicar;
- eliminar/quitar cultivo debe respetar la logica de catalogo.

Criterios de aceptacion:
- usuario normal no puede modificar cultivos ajenos;
- usuario normal no puede publicar;
- catalogo pagina y filtra;
- copia conserva datos relacionados pero puede editarse sin cambiar el original.
```

### Prompt 5: calendario agricola

```text
Implementa calendario de cultivo por fases.

Endpoints:
- `POST /calendar/`;
- `GET /calendar/`;
- `GET /calendar/events`;
- `PUT /calendar/crop/{crop_id}`;
- `POST /calendar/crop/{crop_id}/activate`;
- `POST /calendar/crop/{crop_id}/advance`;
- `GET /calendar/{calendar_id}`;
- `GET /calendar/{calendar_id}/events`;
- `GET /calendar/crop/{crop_id}`;
- `PUT /calendar/{calendar_id}`;
- `DELETE /calendar/{calendar_id}`.

Reglas:
- fases: Siembra, Trasplante, Cosecha;
- activar solo si todas las fechas estan completas;
- eventos se calculan por mes y quincena, ignorando el ano;
- `current_phase_index` marca la fase visible;
- avanzar en ultima fase completa el calendario y lo desactiva;
- aplicar permisos por propietario/admin.

Criterios de aceptacion:
- calendario incompleto no se activa;
- calendario completo produce evento de fase actual;
- avance de fase cambia evento;
- ultima fase marca `completed`.
```

### Prompt 6: riego, ambiente y tareas

```text
Implementa rutas CRUD para riego, requisitos ambientales y tareas.

Riego:
- crear, listar, obtener, obtener por cultivo, actualizar y borrar.

Ambiental:
- crear, listar, obtener, obtener por cultivo, actualizar y borrar.

Tareas:
- crear tarea;
- listar tareas visibles;
- obtener tarea;
- listar por usuario;
- listar por cultivo;
- asociar tarea a cultivo;
- actualizar parcialmente estado;
- actualizar completa;
- borrar;
- listar cultivos de una tarea.

Criterios de aceptacion:
- usuario normal solo gestiona recursos propios;
- admin gestiona todos;
- se puede crear tarea y asignarla a cultivo;
- se puede completar/reabrir tarea.
```

### Prompt 7: dashboard y admin

```text
Implementa dashboard personal y panel de administracion.

Dashboard:
- `GET /dashboard/summary`;
- contar cultivos del usuario;
- contar calendarios activos;
- contar tareas pendientes;
- listar hasta 5 tareas pendientes;
- listar hasta 6 calendarios activos;
- listar avisos por cultivos sin calendario, fases incompletas o ultima fase.

Admin:
- `GET /admin/summary`;
- CRUD paginado de usuarios con filtros;
- CRUD paginado de cultivos con filtros;
- validaciones: no exponer passwords, no borrar usuario admin propio, no eliminar/degradar ultimo admin.

Criterios de aceptacion:
- dashboard no filtra datos de otros usuarios;
- usuario normal recibe 403 en `/admin/*`;
- admin puede crear, editar y borrar usuarios y cultivos con datos relacionados.
```

### Prompt 8: frontend base y autenticacion

```text
Implementa frontend React/Vite.

Debe incluir:
- AuthProvider con token en localStorage;
- cliente API centralizado;
- rutas con React Router;
- ProtectedRoute;
- AdminRoute;
- Home publica;
- Login;
- SignUp;
- OAuthCallback;
- Navbar;
- NotificationBanner.

Rutas:
- `/`;
- `/login`;
- `/signup`;
- `/oauth/callback`;
- `/dashboard`;
- `/crops`;
- `/published-crops`;
- `/tasks`;
- `/calendar`;
- `/admin`, `/admin/users`, `/admin/crops`.

Criterios de aceptacion:
- usuario sin token solo entra en home/login/signup/oauth callback;
- login guarda token y redirige a dashboard;
- logout limpia token;
- admin ve enlace/pagina admin;
- usuario normal no entra a admin.
```

### Prompt 9: frontend funcional de usuario

```text
Implementa las paginas de usuario:
- Dashboard;
- PublishedCrops;
- Crops;
- Calendar;
- Tasks.

Requisitos:
- dashboard con tarjetas y listas de resumen;
- catalogo con filtros, paginacion y boton de anadir a mis cultivos;
- mis cultivos con listado, detalle, crear con imagen opcional, editar, quitar, riego, ambiente, calendario y tareas;
- calendario anual dividido por meses y quincenas, mostrando fase actual y boton para avanzar;
- tareas con filtros por estado, crear, asignar a cultivo, completar/reabrir y eliminar;
- estados de carga, error y exito.

Criterios de aceptacion:
- todos los flujos principales pueden hacerse desde la UI;
- las llamadas usan el token;
- errores de API se muestran de forma comprensible;
- la UI no rompe si faltan datos opcionales.
```

### Prompt 10: frontend admin

```text
Implementa panel admin en React.

Debe incluir:
- resumen global;
- gestion de usuarios con busqueda, filtro por rol, paginacion, crear, editar y borrar;
- gestion de cultivos con filtros por nombre, tipo, usuario y tipo de origen/catalogo, paginacion, crear, editar y borrar;
- formularios para datos de cultivo, riego, ambiente y calendario;
- mensajes de exito/error;
- proteccion de ruta admin.

Criterios de aceptacion:
- usuario normal no accede;
- admin puede completar el flujo de gestion de usuarios;
- admin puede completar el flujo de gestion de cultivos;
- paginacion y filtros funcionan.
```

### Prompt 11: seed, documentacion y scripts

```text
Completa seed, documentacion y scripts.

Debe incluir:
- seed opcional con admin, usuarios, cultivos, calendarios, riego, ambiente, tareas y asociaciones;
- documentacion de variables de entorno;
- documentacion de ejecucion local;
- documentacion de tests;
- scripts npm desde raiz para backend tests, frontend lint/build y e2e.

Criterios de aceptacion:
- seed no se ejecuta salvo `RUN_SEED`;
- una persona puede arrancar backend y frontend siguiendo README;
- comandos de test estan documentados.
```

### Prompt 12: tests

```text
Implementa tests automaticos con `unittest` y `fastapi.testclient.TestClient`.

Cobertura minima:
- root backend;
- registro/login;
- rutas protegidas sin token;
- token invalido;
- OAuth Google inicia redirect sin llamada real a token;
- permisos admin;
- CRUD admin usuarios y cultivos;
- no exposicion de password;
- filtros y paginacion de catalogo;
- copia de cultivo e independencia;
- permisos de cultivos;
- logica de eliminar/quitar cultivo;
- calendario incompleto/completo/avance/completado;
- dashboard personal sin fuga de datos;
- E2E usuario normal;
- E2E admin.

Usa SQLite temporal por proceso de test y recrea tablas antes de cada test.

Criterios de aceptacion:
- tests pasan de forma repetible;
- no dependen de PostgreSQL;
- no dependen de red ni credenciales reales.
```

### Prompt 13: hardening y revision final

```text
Revisa el proyecto completo.

Busca:
- fugas de datos entre usuarios;
- passwords expuestos;
- endpoints sin permisos;
- errores de orden de rutas;
- bugs de calendario;
- duplicacion accidental de rutas;
- inconsistencias frontend/backend;
- fallos de build/lint;
- tests faltantes.

Entrega:
- lista de problemas encontrados;
- cambios aplicados;
- comandos ejecutados;
- resultado de tests;
- riesgos residuales.
```

## 15. Rubrica de comparacion

Puntuacion sugerida: 100 puntos.

### Funcionalidad backend, 20 puntos

- CRUD y endpoints principales completos: 5.
- Autenticacion y permisos correctos: 5.
- Catalogo y copias independientes: 4.
- Calendario por fases correcto: 4.
- Dashboard/admin/tareas/datos relacionados: 2.

### Frontend, 15 puntos

- Rutas y autenticacion cliente: 3.
- Flujos de usuario completos: 5.
- Flujos admin completos: 3.
- Estados de carga/error/exito: 2.
- Usabilidad y claridad visual: 2.

### Persistencia y modelo de datos, 10 puntos

- Relaciones correctas: 3.
- Integridad al borrar/copiar: 3.
- Configuracion PostgreSQL/SQLite: 2.
- Seed util y controlado: 2.

### Seguridad y aislamiento, 15 puntos

- JWT y password hashing: 3.
- No exposicion de passwords: 3.
- Control de propietario/admin: 5.
- Sin secretos reales: 2.
- OAuth tolerante a configuracion/test: 2.

### Tests, 15 puntos

- Tests backend unitarios/API: 5.
- Flujos E2E HTTP: 4.
- Tests de permisos y fugas de datos: 3.
- Tests de calendario/catalogo: 2.
- Repetibilidad sin servicios externos: 1.

### Calidad de codigo, 10 puntos

- Modularidad: 3.
- Claridad y legibilidad: 2.
- Manejo de errores: 2.
- Mantenibilidad: 2.
- Consistencia de estilo: 1.

### Documentacion y ejecucion, 8 puntos

- README claro: 2.
- variables de entorno documentadas: 2.
- comandos de test/build: 2.
- notas de limitaciones: 2.

### Autonomia de la IA, 7 puntos

- Entrega funcional en pocas iteraciones: 2.
- Buenas decisiones no especificadas: 2.
- Capacidad de depurar fallos: 2.
- Explicacion clara de cambios: 1.

## 16. Tabla de evaluacion sugerida

```md
| IA | Iteraciones | Backend /20 | Frontend /15 | Datos /10 | Seguridad /15 | Tests /15 | Codigo /10 | Docs /8 | Autonomia /7 | Total /100 | Fortalezas | Debilidades |
|----|-------------|-------------|--------------|-----------|---------------|-----------|------------|---------|--------------|------------|------------|-------------|
| IA A | | | | | | | | | | | |
| IA B | | | | | | | | | | | |
| IA C | | | | | | | | | | | |
```

## 17. Recomendaciones para una comparacion justa

- Usar exactamente los mismos prompts y en el mismo orden.
- No mostrar a una IA el codigo generado por otra.
- Fijar un limite de iteraciones por fase.
- Ejecutar los mismos tests al final.
- Registrar los errores y los prompts de correccion necesarios.
- Evaluar tanto el resultado final como el proceso.
- Separar dos experimentos si se desea:
  - reconstruccion guiada con este documento;
  - reconstruccion desde especificacion funcional sin detalles internos del proyecto final.

## 18. Prompt para pedir a ChatGPT que genere una bateria alternativa

```text
Te paso un contexto maestro de un proyecto final llamado AgroManager. Quiero que generes una bateria de prompts para reconstruirlo desde cero con distintas IAs.

Objetivo:
- que los prompts sean comparables;
- que esten divididos por fases;
- que no revelen codigo final literalmente;
- que incluyan criterios de aceptacion;
- que permitan medir puntos fuertes y debiles de cada IA.

Genera:
1. prompts por fase;
2. una version resumida para IAs con poco contexto;
3. una version detallada para IAs con mucho contexto;
4. una rubrica de evaluacion;
5. una tabla para comparar resultados;
6. recomendaciones para controlar sesgos del experimento.
```

