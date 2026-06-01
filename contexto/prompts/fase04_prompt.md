# FASE 4 — Gestión de cultivos y catálogo

Actúa como desarrollador backend senior especializado en FastAPI, SQLAlchemy, SQLite y testing con unittest.

Vamos a continuar el desarrollo incremental de AgroManager.

## Contexto

El proyecto ya tiene implementadas las fases iniciales:

- estructura base del backend;
- configuración de FastAPI;
- conexión a SQLite mediante SQLAlchemy;
- modelos y schemas iniciales;
- autenticación;
- registro/login;
- usuarios;
- control básico de permisos mediante usuario autenticado.

Ahora toca implementar la **FASE 4: Gestión de cultivos y catálogo público**.

## Restricciones

- Trabaja únicamente dentro de la carpeta del proyecto actual.
- No leas ni copies código de otros proyectos.
- No cambies la arquitectura principal si no es necesario.
- No elimines tests existentes.
- No rompas autenticación ni usuarios.
- Mantén FastAPI, SQLAlchemy, SQLite y unittest.
- No implementes frontend todavía.
- No implementes calendario todavía.
- No implementes riego, tareas ni panel admin todavía.
- No uses datos reales ni secretos reales.

## Objetivo de la fase

Implementar la funcionalidad backend para gestionar cultivos y catálogo público.

El sistema debe permitir:

1. Crear cultivos propios.
2. Consultar cultivos propios.
3. Consultar detalle de un cultivo.
4. Actualizar cultivos propios.
5. Eliminar cultivos propios.
6. Publicar cultivos en catálogo público si el usuario tiene permisos.
7. Consultar catálogo público.
8. Copiar un cultivo público a la lista personal del usuario.

## Modelo de cultivo

Revisa los modelos existentes antes de modificar nada. Si no existe un modelo adecuado para cultivos, créalo.

Un cultivo debe contemplar, como mínimo:

- id;
- name;
- description;
- crop_type o categoría equivalente si encaja con el modelo;
- owner_id;
- is_public;
- timestamps si el proyecto ya los usa.

Adapta los nombres reales a la arquitectura existente.

## Endpoints esperados

Implementa endpoints equivalentes a:

```text
GET    /crops/my
GET    /crops/published
GET    /crops/{crop_id}
POST   /crops/
PUT    /crops/{crop_id}
DELETE /crops/{crop_id}
POST   /crops/{crop_id}/add-to-my-crops
```

Si el proyecto ya usa otro prefijo o naming, respétalo y documenta la decisión.

## Reglas de negocio

- Un usuario autenticado puede crear cultivos propios.
- Un usuario normal solo puede consultar, actualizar o eliminar sus propios cultivos.
- Los cultivos públicos pueden consultarse desde el catálogo.
- Al copiar un cultivo público, debe crearse una copia independiente para el usuario.
- La copia no debe modificar el cultivo público original.
- Un usuario no debe poder modificar cultivos de otro usuario.
- Un usuario no autenticado no debe poder crear, actualizar ni eliminar cultivos.
- Si ya existe control de rol admin, solo admin debería poder crear/publicar cultivos públicos directamente.
- Si todavía no existe rol admin completo, deja la implementación preparada de forma coherente con la autenticación actual.

## Schemas

Crea o actualiza schemas para:

- creación de cultivo;
- actualización de cultivo;
- respuesta de cultivo;
- listado paginado si el proyecto ya usa paginación.

## Tests obligatorios

Añade o actualiza tests con unittest y FastAPI TestClient.

Casos mínimos:

- crear cultivo autenticado;
- rechazar creación sin token;
- listar cultivos propios;
- obtener detalle de cultivo propio;
- impedir acceder/modificar cultivo ajeno;
- actualizar cultivo propio;
- eliminar cultivo propio;
- listar catálogo público;
- copiar cultivo público a mis cultivos;
- verificar que la copia no modifica el original;
- 404 para cultivo inexistente.

## Validación obligatoria

Ejecuta:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

Si el comando falla, corrige el problema antes de terminar.

## Entrega final

Al terminar, responde con:

1. archivos creados;
2. archivos modificados;
3. endpoints añadidos;
4. modelos/schemas añadidos;
5. tests añadidos;
6. resultado exacto de los tests;
7. limitaciones pendientes;
8. riesgos detectados;
9. confirmación de si FASE 4 queda completada.
