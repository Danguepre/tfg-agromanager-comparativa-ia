# FASE 5 — Calendario agrícola

Actúa como desarrollador backend senior especializado en FastAPI, SQLAlchemy, SQLite, lógica de negocio y testing con unittest.

Vamos a continuar AgroManager con la **FASE 5: Calendario agrícola**.

## Contexto

Ya están implementadas:

- base del backend;
- autenticación;
- usuarios;
- permisos básicos;
- cultivos propios;
- catálogo público;
- copia de cultivos públicos a cultivos personales.

Ahora toca añadir planificación agrícola mediante calendarios por cultivo.

## Restricciones

- Trabaja únicamente dentro de la carpeta del proyecto actual.
- No leas ni copies código de otros proyectos.
- No implementes frontend todavía.
- No implementes riego, tareas ni panel admin todavía.
- No rompas cultivos ni autenticación.
- No elimines tests existentes.
- Mantén FastAPI, SQLAlchemy, SQLite y unittest.
- Respeta la arquitectura ya existente.

## Objetivo

Implementar calendarios agrícolas asociados a cultivos.

Un calendario debe permitir representar el ciclo de vida de un cultivo mediante fases.

Fases esperadas:

```text
siembra
trasplante
cosecha
```

Estados posibles recomendados:

```text
draft
active
completed
```

Adapta nombres y enums al estilo del proyecto.

## Funcionalidad esperada

El usuario debe poder:

1. Crear un calendario para un cultivo propio.
2. Consultar sus calendarios.
3. Consultar un calendario por id.
4. Consultar calendario por cultivo.
5. Actualizar fechas/fases del calendario.
6. Activar calendario.
7. Avanzar de fase.
8. Completar calendario al terminar la fase final.
9. Consultar eventos del calendario.
10. Eliminar calendario propio.

## Reglas de negocio

- Un usuario solo puede crear calendarios para cultivos propios.
- Un usuario no puede crear calendarios para cultivos ajenos.
- Un calendario debe estar asociado a un cultivo.
- No debe haber calendarios duplicados activos para el mismo cultivo si la arquitectura no lo permite.
- Para activar un calendario debe tener la información mínima necesaria.
- El avance de fase debe seguir el orden:
  - siembra -> trasplante -> cosecha -> completado.
- Un calendario completado no debe aparecer como activo.
- Los eventos devueltos deben pertenecer al usuario autenticado.
- Si se manejan fechas, documenta claramente el formato.
- Si se decide ignorar el año para fases agrícolas recurrentes, impleméntalo de forma coherente y documentada.

## Endpoints esperados

Implementa endpoints equivalentes a:

```text
GET    /calendar/
POST   /calendar/
GET    /calendar/events
GET    /calendar/{calendar_id}
PUT    /calendar/{calendar_id}
DELETE /calendar/{calendar_id}
POST   /calendar/{calendar_id}/activate
POST   /calendar/{calendar_id}/advance
GET    /calendar/crop/{crop_id}
```

Si el proyecto usa otra convención, respétala y documenta los endpoints finales.

## Tests obligatorios

Añade tests para:

- crear calendario para cultivo propio;
- rechazar calendario sin token;
- rechazar calendario para cultivo ajeno;
- listar calendarios propios;
- obtener calendario por id;
- obtener calendario por cultivo;
- actualizar calendario propio;
- impedir actualizar calendario ajeno;
- activar calendario válido;
- rechazar activar calendario incompleto;
- avanzar de siembra a trasplante;
- avanzar de trasplante a cosecha;
- completar calendario al avanzar desde cosecha;
- consultar eventos propios;
- impedir ver eventos de otro usuario;
- 404 para calendario inexistente.

## Validación obligatoria

Ejecuta:

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

Corrige cualquier error antes de finalizar.

## Entrega final

Incluye:

1. archivos creados;
2. archivos modificados;
3. endpoints implementados;
4. modelos/schemas añadidos;
5. reglas de negocio aplicadas;
6. tests añadidos;
7. resultado exacto de los tests;
8. limitaciones pendientes;
9. confirmación de FASE 5 completada.
