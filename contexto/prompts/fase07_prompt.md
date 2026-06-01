# FASE 7 — Dashboard backend y administración backend

Actúa como desarrollador backend senior especializado en FastAPI, SQLAlchemy, permisos por rol y testing.

Vamos a continuar AgroManager con la **FASE 7: Dashboard backend y panel admin backend básico**.

## Contexto

Ya están implementadas:

- autenticación;
- usuarios;
- roles o base para roles;
- cultivos y catálogo;
- calendario agrícola;
- riego;
- requisitos ambientales;
- tareas.

Ahora toca añadir endpoints de resumen para usuario y endpoints administrativos protegidos.

## Restricciones

- Trabaja únicamente dentro de la carpeta del proyecto actual.
- No leas ni copies código de otros proyectos.
- No implementes frontend todavía.
- No implementes panel admin visual todavía.
- No rompas endpoints existentes.
- No elimines tests.
- Mantén FastAPI, SQLAlchemy, SQLite y unittest.
- No expongas contraseñas ni hashes en respuestas de usuarios.

## Objetivos

Implementar:

1. Dashboard backend para usuario normal.
2. Dashboard backend global para admin.
3. Endpoints admin para usuarios.
4. Endpoints admin para cultivos.
5. Endpoints admin para tareas.
6. Protección por rol admin.

## Dashboard usuario

Endpoints orientativos:

```text
GET /dashboard/summary
GET /dashboard/crops
GET /dashboard/tasks
GET /dashboard/calendar
GET /dashboard/irrigation
GET /dashboard/environmental
```

El dashboard debe devolver información del usuario autenticado:

- número de cultivos;
- tareas pendientes;
- tareas completadas;
- calendarios activos;
- calendarios completados;
- eventos próximos;
- resumen de riego;
- requisitos ambientales.

## Admin backend

Endpoints orientativos:

```text
GET    /admin/summary

GET    /admin/users
GET    /admin/users/{id}
PATCH  /admin/users/{id}
DELETE /admin/users/{id}

GET    /admin/crops
GET    /admin/crops/{id}
PATCH  /admin/crops/{id}
DELETE /admin/crops/{id}

GET    /admin/tasks
GET    /admin/tasks/{id}
PATCH  /admin/tasks/{id}
DELETE /admin/tasks/{id}
```

Adapta a la arquitectura existente.

## Reglas de negocio

- Solo usuarios con rol admin pueden acceder a `/admin/*`.
- Usuario normal debe recibir 403 en endpoints admin.
- Usuario sin token debe recibir 401.
- El registro público no debe crear admins.
- No exponer password_hash.
- Admin puede listar usuarios.
- Admin puede actualizar datos básicos de usuarios.
- Admin puede activar/desactivar usuarios si el modelo lo permite.
- Admin puede consultar y gestionar cultivos globales.
- Admin puede consultar y gestionar tareas globales.
- Dashboard usuario solo debe incluir datos del usuario autenticado.
- Dashboard admin debe incluir datos globales.

## Tests obligatorios

Tests dashboard usuario:

- summary autenticado;
- rechazar summary sin token;
- contar cultivos propios;
- contar tareas pendientes/completadas;
- contar calendarios activos/completados;
- no mezclar datos de otros usuarios.

Tests admin:

- admin accede a summary global;
- usuario normal recibe 403;
- sin token recibe 401;
- admin lista usuarios;
- respuesta de usuarios no incluye hash de contraseña;
- admin actualiza usuario;
- admin elimina/desactiva usuario;
- admin lista cultivos;
- admin consulta cultivo;
- admin actualiza cultivo;
- admin elimina cultivo;
- admin lista tareas;
- admin consulta tarea;
- admin actualiza tarea;
- admin elimina tarea;
- 404 para recursos inexistentes.

## Validación obligatoria

Ejecuta:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

Corrige cualquier fallo.

## Entrega final

Incluye:

1. archivos creados;
2. archivos modificados;
3. endpoints dashboard;
4. endpoints admin;
5. protección por rol;
6. tests añadidos;
7. resultado exacto de tests;
8. limitaciones;
9. confirmación de FASE 7 completada.
