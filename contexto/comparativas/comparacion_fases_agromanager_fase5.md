# Comparación por fases — AgroManager

## FASE 5 — Calendario agrícola

## Objetivo de la fase

Implementar el calendario agrícola asociado a cultivos personales, con fases de:

1. Siembra.
2. Trasplante.
3. Cosecha.

La fase debe permitir crear, actualizar, activar, consultar eventos y avanzar fases de calendario respetando permisos de usuario propietario y admin.

---

## Endpoints requeridos

- `POST /calendar/`
- `GET /calendar/`
- `GET /calendar/events`
- `PUT /calendar/crop/{crop_id}`
- `POST /calendar/crop/{crop_id}/activate`
- `POST /calendar/crop/{crop_id}/advance`
- `GET /calendar/{calendar_id}`
- `GET /calendar/{calendar_id}/events`
- `GET /calendar/crop/{crop_id}`
- `PUT /calendar/{calendar_id}`
- `DELETE /calendar/{calendar_id}`

---

## Reglas funcionales esperadas

- Un calendario pertenece a un cultivo.
- Un usuario normal solo puede gestionar calendarios de sus propios cultivos.
- Admin puede gestionar todos.
- Un calendario solo puede activarse si tiene completas las fechas de siembra, trasplante y cosecha.
- Los eventos del calendario se calculan por mes y quincena, ignorando el año.
- `current_phase_index` marca la fase visible/actual.
- Al avanzar fase:
  - de Siembra pasa a Trasplante;
  - de Trasplante pasa a Cosecha;
  - desde Cosecha marca el calendario como `completed` e inactivo.
- `GET /calendar/events` debe devolver eventos activos del usuario autenticado.
- `GET /calendar/{calendar_id}/events` debe devolver eventos de ese calendario.
- `GET /calendar/crop/{crop_id}` debe obtener el calendario de un cultivo.
- Si el cultivo no pertenece al usuario, debe devolver `403`, salvo admin.
- No se deben exponer datos de otros usuarios.
- Los tests existentes de auth, usuarios y cultivos deben seguir pasando.

---

## Tabla comparativa FASE 5

| IA | Iteraciones | Tests pasan | Nº tests | Calendario CRUD | Activación | Eventos | Avance fase | Permisos | Errores / desviaciones | Puntuación /100 |
|---|---:|---|---:|---|---|---|---|---|---|---:|
| Claude Code | 1 | Sí | 39 | Sí | Sí, por `calendar_id` | Sí | Sí, por `calendar_id` | Sí | Redirects 307; activate/advance no siguen la ruta por `crop_id` pedida | 88 |
| Codex | 1 | Sí | 29 | Sí | Sí | Sí | Sí | Sí | Más lento; mantiene login Swagger `username` aunque espera email | 90 |
| DeepSeek | 1 | Sí | 51 | Sí | Sí | Sí | Sí | Sí | Ninguna incidencia funcional observada | 96 |

---

# Resultados por IA — FASE 5

## Claude Code

### Estado

Validado.

### Comando ejecutado

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Resultado

```text
Ran 39 tests in 17.516s

OK
```

### Tests totales

39 tests.

### Tests de calendario validados

- `test_create_calendar_authenticated`
- `test_create_calendar_without_token`
- `test_user_cannot_create_calendar_for_other_crop`
- `test_get_calendar_by_crop_id`
- `test_update_calendar_with_put_crop_endpoint`
- `test_cannot_activate_incomplete_calendar`
- `test_activate_complete_calendar`
- `test_get_user_events`
- `test_get_calendar_events`
- `test_advance_phase_from_planting_to_transplant`
- `test_advance_phase_from_transplant_to_harvest`
- `test_advance_from_harvest_completes_calendar`
- `test_admin_can_manage_other_calendars`
- `test_delete_calendar`

### Cobertura observada

- Crear calendario para cultivo propio.
- Bloqueo sin token.
- Usuario normal no puede crear calendario para cultivo ajeno.
- Obtener calendario por cultivo.
- Actualizar calendario por `PUT /calendar/crop/{crop_id}`.
- No activar calendario incompleto.
- Activar calendario completo.
- Obtener eventos activos del usuario.
- Obtener eventos de un calendario.
- Avanzar de Siembra a Trasplante.
- Avanzar de Trasplante a Cosecha.
- Avanzar desde Cosecha marca `COMPLETED`.
- Admin puede gestionar calendarios de otros usuarios.
- Eliminar calendario.
- Tests previos de auth, usuarios y cultivos siguen pasando.

### Incidencias observadas

- Se mantienen redirects `307 Temporary Redirect` por diferencias entre rutas con y sin barra final.
- Claude implementa activación y avance como:
  - `POST /calendar/{calendar_id}/activate`
  - `POST /calendar/{calendar_id}/advance`
- El prompt pedía:
  - `POST /calendar/crop/{crop_id}/activate`
  - `POST /calendar/crop/{crop_id}/advance`
- Por tanto, hay desviación de endpoint si no existen también las rutas por `crop_id`.
- Los tests validan avance y activación por `calendar_id`, no por `crop_id`.

### Conclusión

Claude completa FASE 5 correctamente y mantiene todos los tests previos. La implementación de calendario queda validada por 39 tests pasando, aunque con desviación de rutas en `activate` y `advance` respecto al prompt.

### Puntuación provisional FASE 5

```text
88/100
```

---

## Codex

### Estado

Validado.

### Comando ejecutado

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Resultado

```text
Ran 29 tests in 35.104s

OK
```

### Tests totales

29 tests.

### Tests de calendario validados

- `test_activate_complete_calendar`
- `test_admin_can_manage_other_user_calendar`
- `test_advance_from_harvest_completes_and_deactivates_calendar`
- `test_advance_from_planting_to_transplant`
- `test_advance_from_transplant_to_harvest`
- `test_calendar_events_return_current_phase`
- `test_cannot_activate_incomplete_calendar`
- `test_create_calendar_for_own_crop`
- `test_events_ignore_year_and_use_month_and_fortnight`
- `test_get_calendar_by_crop`
- `test_global_events_return_only_authenticated_user_events`
- `test_normal_user_cannot_create_or_edit_calendar_for_other_user_crop`
- `test_update_calendar_by_crop`
- `test_user_without_token_cannot_create_calendar`

### Cobertura observada

- Crear calendario para cultivo propio.
- Usuario sin token no puede crear calendario.
- Usuario normal no puede crear/editar calendario de cultivo ajeno.
- Obtener calendario por cultivo.
- Actualizar calendario por cultivo.
- No activar calendario incompleto.
- Activar calendario completo.
- Eventos globales solo devuelven eventos del usuario autenticado.
- Eventos de calendario devuelven la fase actual.
- Eventos ignoran el año y usan mes/quincena.
- Avanzar de Siembra a Trasplante.
- Avanzar de Trasplante a Cosecha.
- Avanzar desde Cosecha completa y desactiva el calendario.
- Admin puede gestionar calendario de otro usuario.
- Tests previos de auth, usuarios y cultivos siguen pasando.

### Incidencias observadas

- La ejecución es bastante más lenta que Claude: 35.104s frente a 17.516s.
- Menor número total de tests que Claude, pero la cobertura específica de calendario es muy completa.
- Mantiene la desviación previa de Codex: login Swagger muestra `username`, aunque espera email.

### Conclusión

Codex completa FASE 5 correctamente. La implementación de calendario queda validada por 29 tests pasando, con buena cobertura específica de reglas de calendario.

### Puntuación provisional FASE 5

```text
90/100
```

---

## DeepSeek

### Estado

Validado.

### Comando ejecutado

```bash
python -m unittest tests.test_api -v
```

### Resultado

```text
Ran 51 tests in 32.796s

OK
```

### Tests totales

51 tests.

### Tests de calendario validados

- `test_activate_complete_calendar`
- `test_admin_can_manage_other_user_calendar`
- `test_advance_from_harvest_completes_and_deactivates`
- `test_advance_from_planting_to_transplant`
- `test_advance_from_transplant_to_harvest`
- `test_calendar_events_returns_current_phase`
- `test_cannot_activate_incomplete_calendar`
- `test_create_calendar_for_own_crop`
- `test_create_calendar_without_token_fails`
- `test_delete_calendar`
- `test_events_ignore_year_by_month_fortnight`
- `test_get_calendar_by_crop`
- `test_list_calendars_admin_sees_all`
- `test_list_calendars_user_sees_only_own`
- `test_normal_user_cannot_create_calendar_for_other_crop`
- `test_normal_user_cannot_edit_other_user_calendar`
- `test_update_calendar_by_crop`
- `test_user_events_only_own`

### Cobertura observada

- Crear calendario para cultivo propio.
- Usuario sin token no puede crear calendario.
- Usuario normal no puede crear calendario para cultivo ajeno.
- Usuario normal no puede editar calendario de cultivo ajeno.
- Obtener calendario por cultivo.
- Actualizar calendario por `PUT /calendar/crop/{crop_id}`.
- No activar calendario incompleto.
- Activar calendario completo.
- Obtener eventos de un calendario con fase actual.
- Obtener eventos activos solo del usuario autenticado.
- Eventos ignoran el año y funcionan por mes/quincena.
- Avanzar de Siembra a Trasplante.
- Avanzar de Trasplante a Cosecha.
- Avanzar desde Cosecha completa y desactiva el calendario.
- Admin puede gestionar calendarios de otros usuarios.
- Admin ve todos los calendarios.
- Usuario normal solo ve sus propios calendarios.
- Eliminar calendario.
- Tests previos de auth, usuarios y cultivos siguen pasando.

### Incidencias observadas

- Ninguna incidencia funcional observada en la ejecución.
- Es la batería más amplia de FASE 5.
- En comparación con Claude y Codex, DeepSeek mantiene más tests acumulados.

### Conclusión

DeepSeek completa FASE 5 correctamente. La implementación de calendario queda validada por 51 tests pasando, con la cobertura más amplia de la fase.

### Puntuación provisional FASE 5

```text
96/100
```

---

# Incidencias FASE 5

| IA | Incidencia | Severidad | Corrección necesaria | Estado |
|---|---|---|---|---|
| Claude Code | Redirects 307 por diferencias entre rutas con y sin barra final | Baja | Unificar rutas si se quiere reducir ruido en logs/tests | No bloqueante |
| Claude Code | Activate/advance implementados por `calendar_id` en vez de por `crop_id` como pedía el prompt | Media | Añadir alias o endpoints `POST /calendar/crop/{crop_id}/activate` y `POST /calendar/crop/{crop_id}/advance` | Pendiente |
| Claude Code | Mantiene desviación previa: registro en `/auth/register` | Media | Adaptar a `POST /users/` en hardening | Pendiente |
| Codex | Ejecución más lenta que Claude y DeepSeek en proporción al número de tests | Baja | Revisar setup/teardown de tests si el tiempo crece demasiado | No bloqueante |
| Codex | Login Swagger usa `username`, pero espera email | Baja | Documentar o ajustar esquema de login | No bloqueante |
| DeepSeek | Ninguna incidencia funcional observada | — | — | Validado |

---

# Comparación FASE 5

## Mejor cobertura de tests

**DeepSeek**.

Motivo:

- 51 tests totales.
- Cubre listado de calendarios para usuario y admin.
- Cubre bloqueo de edición de calendario ajeno.
- Cubre eventos por usuario, eventos por calendario, fases, avance, completado, activación y eliminación.

## Mejor cumplimiento global de reglas de calendario

**DeepSeek**.

Motivo:

- Cubre más casos de permisos.
- Cubre más endpoints de calendario.
- Mantiene más tests acumulados.
- No presenta desviaciones funcionales observadas en la salida de tests.

## Mejor implementación sin incidencias funcionales observadas

**DeepSeek y Codex**.

Motivo:

- Ambos pasan tests sin errores funcionales.
- Codex tiene menos tests totales, pero su cobertura específica de calendario es buena.
- DeepSeek tiene mayor cobertura general.

## Implementación más amplia pero con desviación de rutas

**Claude Code**.

Motivo:

- 39 tests pasando.
- Buena cobertura general.
- Sin embargo, usa activate/advance por `calendar_id`, mientras el prompt pedía rutas por `crop_id`.

## Resultado comparativo FASE 5

| Posición | IA | Puntuación | Motivo principal |
|---:|---|---:|---|
| 1 | DeepSeek | 96/100 | Mayor cobertura, permisos más completos y sin incidencias funcionales observadas |
| 2 | Codex | 90/100 | Cumple bien la fase, con buena cobertura específica de calendario |
| 3 | Claude Code | 88/100 | Funciona y pasa tests, pero tiene desviación de rutas en activate/advance |

---

# Estado acumulado tras FASE 5

| IA | Piloto 0-3 | FASE 4 | FASE 5 | Estado acumulado |
|---|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | Funcional, pero arrastra desviaciones de rutas |
| Codex | 77 | 86 | 90 | Funcional y estable, cobertura media |
| DeepSeek | 87 | 94 | 96 | Mejor resultado acumulado provisional |

---

# Conclusión acumulada provisional

DeepSeek mantiene la mejor posición global tras la FASE 5, principalmente por su mayor cobertura de tests y por implementar más casos negativos y de permisos.

Codex mejora respecto a FASE 4 y queda en segunda posición en calendario, con una implementación funcional y buena cobertura específica.

Claude Code sigue siendo funcional y pasa todos los tests, pero acumula desviaciones de rutas: primero `/auth/register` en fases previas y ahora `activate/advance` por `calendar_id` en lugar de por `crop_id`.

---

# Próximo paso

La siguiente fase del experimento será:

```text
FASE 6 — Riego, ambiente y tareas
```

Debe implementarse con el mismo método:

1. Mismo prompt para Claude, Codex y DeepSeek.
2. Cada IA trabaja solo en su carpeta.
3. No se comparten errores ni soluciones entre IAs.
4. Se ejecutan los mismos comandos de validación.
5. Se registran iteraciones, tests, incidencias y puntuación.
6. No se pasa a FASE 7 hasta cerrar FASE 6 en las tres IAs.

---

## Prompt pendiente para FASE 6

Debe prepararse un prompt común para implementar:

- rutas CRUD de riego;
- rutas CRUD de requisitos ambientales;
- tareas;
- asignación de tareas a cultivos;
- actualización parcial de estado de tareas;
- permisos por propietario/admin;
- tests para riego, ambiente, tareas, asociación tarea-cultivo, permisos y regresiones de fases anteriores.
