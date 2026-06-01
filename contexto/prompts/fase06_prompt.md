# FASE 6 — Riego, requisitos ambientales y tareas

Actúa como desarrollador backend senior especializado en FastAPI, SQLAlchemy, SQLite y testing.

Vamos a continuar AgroManager con la **FASE 6: Riego, requisitos ambientales y tareas**.

## Contexto

Ya están implementadas:

- autenticación;
- usuarios;
- cultivos;
- catálogo público;
- calendarios agrícolas.

Ahora toca ampliar el dominio agrícola con:

1. Información de riego.
2. Requisitos ambientales.
3. Gestión de tareas.

## Restricciones

- Trabaja únicamente dentro de la carpeta del proyecto actual.
- No leas ni copies código de otros proyectos.
- No implementes frontend todavía.
- No implementes panel admin visual todavía.
- No rompas fases anteriores.
- No elimines tests existentes.
- Mantén FastAPI, SQLAlchemy, SQLite y unittest.
- Respeta nombres, arquitectura y convenciones existentes.

## Objetivo

Implementar backend para:

- necesidades de riego asociadas a cultivos;
- requisitos ambientales asociados a cultivos;
- tareas del usuario, opcionalmente asociadas a cultivos.

## Riego

Debe poder almacenarse información como:

- frecuencia;
- cantidad;
- unidad;
- notas;
- cultivo asociado.

Adapta los campos al modelo real.

Endpoints orientativos:

```text
POST   /irrigation/
GET    /irrigation/
GET    /irrigation/{id}
GET    /irrigation/crop/{crop_id}
PUT    /irrigation/{id}
DELETE /irrigation/{id}
```

## Requisitos ambientales

Debe poder almacenarse información como:

- temperatura mínima;
- temperatura máxima;
- humedad;
- exposición solar;
- tipo de suelo;
- notas;
- cultivo asociado.

Endpoints orientativos:

```text
POST   /environmental/
GET    /environmental/
GET    /environmental/{id}
GET    /environmental/crop/{crop_id}
PUT    /environmental/{id}
DELETE /environmental/{id}
```

## Tareas

Las tareas deben permitir organizar acciones del usuario.

Campos recomendados:

- id;
- title o name;
- description;
- status o completed;
- due_date si procede;
- owner_id;
- relación con cultivo si procede.

Endpoints orientativos:

```text
POST   /tasks/
GET    /tasks/
GET    /tasks/{task_id}
PATCH  /tasks/{task_id}
PUT    /tasks/{task_id}
DELETE /tasks/{task_id}
```

## Reglas de negocio

- Un usuario solo puede gestionar riego/ambiente de cultivos propios.
- Un usuario no puede modificar riego/ambiente de cultivos ajenos.
- Un usuario solo ve sus propias tareas.
- Un usuario no puede modificar tareas ajenas.
- Las tareas pueden marcarse como pendientes o completadas.
- Si una tarea se asocia a un cultivo, el cultivo debe pertenecer al usuario.
- Los endpoints deben devolver 404 o 403 según el patrón usado en el proyecto.
- La información de catálogo público debe mantenerse coherente.

## Tests obligatorios

Añade tests para riego:

- crear riego para cultivo propio;
- rechazar riego sin token;
- rechazar riego para cultivo ajeno;
- consultar riego por cultivo;
- actualizar riego propio;
- eliminar riego propio;
- 404 para riego inexistente.

Añade tests para requisitos ambientales:

- crear requisitos para cultivo propio;
- rechazar creación sin token;
- rechazar creación para cultivo ajeno;
- consultar requisitos por cultivo;
- actualizar requisitos propios;
- eliminar requisitos propios;
- 404 para recurso inexistente.

Añade tests para tareas:

- crear tarea autenticada;
- rechazar tarea sin token;
- listar tareas propias;
- obtener tarea propia;
- impedir ver tarea ajena;
- actualizar tarea;
- marcar tarea completada;
- marcar tarea pendiente;
- eliminar tarea;
- asociar tarea a cultivo propio;
- rechazar asociar tarea a cultivo ajeno.

## Validación obligatoria

Ejecuta:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

Corrige cualquier fallo.

## Entrega final

Indica:

1. archivos creados;
2. archivos modificados;
3. endpoints añadidos;
4. modelos/schemas nuevos;
5. tests añadidos;
6. resultado exacto de tests;
7. decisiones técnicas;
8. limitaciones pendientes;
9. confirmación de FASE 6 completada.
