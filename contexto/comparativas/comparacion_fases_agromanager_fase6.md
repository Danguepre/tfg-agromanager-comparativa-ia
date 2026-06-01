# Comparación por fases — AgroManager

## FASE 6 — Riego, requisitos ambientales y tareas

## Objetivo de la fase

Implementar la gestión de:

1. Riego asociado a cultivos.
2. Requisitos ambientales asociados a cultivos.
3. Tareas de usuario.
4. Relación entre tareas y cultivos mediante `TaskCrop`.

La fase debe permitir crear, consultar, actualizar y eliminar recursos respetando permisos de usuario propietario y admin.

---

## Endpoints requeridos

### Riego

- `POST /irrigation/`
- `GET /irrigation/`
- `GET /irrigation/{irrigation_id}`
- `GET /irrigation/crop/{crop_id}`
- `PUT /irrigation/{irrigation_id}`
- `DELETE /irrigation/{irrigation_id}`

### Requisitos ambientales

- `POST /environmental/`
- `GET /environmental/`
- `GET /environmental/{env_id}`
- `GET /environmental/crop/{crop_id}`
- `PUT /environmental/{env_id}`
- `DELETE /environmental/{env_id}`

### Tareas

- `POST /tasks/`
- `GET /tasks/`
- `GET /tasks/{task_id}`
- `GET /tasks/user/{user_id}`
- `GET /tasks/crop/{crop_id}`
- `POST /tasks/assign`
- `PATCH /tasks/{task_id}`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `GET /tasks/{task_id}/crops`

---

## Reglas funcionales esperadas

- Usuario normal solo gestiona riego, ambiente y tareas de sus propios cultivos.
- Usuario normal solo ve sus propias tareas.
- Usuario normal no puede asociar tareas a cultivos ajenos.
- Admin puede ver y gestionar todos los recursos.
- No se deben exponer datos de otros usuarios.
- Al crear un cultivo, debe seguir existiendo creación de riego y ambiente por defecto si ya estaba implementada.
- Se puede crear una tarea sin cultivo asociado.
- Se puede asignar una tarea a un cultivo propio.
- Se puede listar tareas por cultivo.
- Se puede listar cultivos asociados a una tarea.
- Se puede actualizar parcialmente el estado de una tarea con `PATCH`.
- Estados sugeridos de tarea: `pending`, `completed`.
- Se puede completar y reabrir tarea.
- `DELETE /tasks/{task_id}` elimina la tarea y sus relaciones `TaskCrop`.
- `DELETE` de riego o ambiente debe respetar permisos y no borrar cultivos.
- Los tests existentes de auth, usuarios, cultivos y calendario deben seguir pasando.

---

## Tabla comparativa FASE 6

| IA | Iteraciones | Tests pasan | Nº tests | Riego CRUD | Ambiente CRUD | Tareas CRUD | Asignación tarea-cultivo | Permisos | Errores / desviaciones | Puntuación /100 |
|---|---:|---|---:|---|---|---|---|---|---|---:|
| Claude Code | 2 | Sí | 63 | Sí | Sí | Sí | Sí | Sí | Fallo inicial de aislamiento corregido; redirects 307; algunas respuestas 404 para ocultar recursos ajenos | 91 |
| Codex | 1 | Sí | 39 | Sí | Sí | Sí | Sí | Sí | Ejecución lenta; cobertura compacta | 90 |
| DeepSeek | 1 | Sí | 72 | Sí | Sí | Sí | Sí | Sí | Ninguna funcional observada; desviación menor en nombres internos | 96 |

---

# Resultados por IA — FASE 6

## Claude Code

### Estado

Validado tras una corrección.

### Primera implementación reportada

Claude reportó la creación/modificación de los siguientes elementos:

### Archivos creados

- `app/schemas/irrigation.py`
- `app/schemas/environmental.py`
- `app/services/irrigation_service.py`
- `app/services/environmental_service.py`
- `app/services/task_service.py`
- `app/routes/irrigation.py`
- `app/routes/environmental.py`
- `app/routes/tasks.py`
- `tests/test_phase6.py`

### Archivos modificados

- `app/schemas/task.py`
- `app/main.py`

### Endpoints reportados

#### Riego

- `POST /irrigation/`
- `GET /irrigation/`
- `GET /irrigation/{irrigation_id}`
- `GET /irrigation/crop/{crop_id}`
- `PUT /irrigation/{irrigation_id}`
- `DELETE /irrigation/{irrigation_id}`

#### Requisitos ambientales

- `POST /environmental/`
- `GET /environmental/`
- `GET /environmental/{env_id}`
- `GET /environmental/crop/{crop_id}`
- `PUT /environmental/{env_id}`
- `DELETE /environmental/{env_id}`

#### Tareas

- `POST /tasks/`
- `GET /tasks/`
- `GET /tasks/user/{user_id}`
- `GET /tasks/crop/{crop_id}`
- `GET /tasks/{task_id}`
- `GET /tasks/{task_id}/crops`
- `POST /tasks/assign`
- `PATCH /tasks/{task_id}`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

---

## Claude Code — Primera validación parcial

### Comando ejecutado

```bash
python -m unittest tests.test_phase6 -v
```

### Resultado

```text
Ran 24 tests in 19.924s

OK
```

### Cobertura validada en tests aislados

#### Riego

- Obtener riego por cultivo.
- Bloquear acceso a riego de cultivo ajeno.
- Actualizar riego.
- Eliminar riego.
- Usuario normal ve solo sus riegos.
- Admin ve todos los riegos.

#### Requisitos ambientales

- Obtener requisitos ambientales por cultivo.
- Bloquear acceso a requisitos de cultivo ajeno.
- Actualizar requisitos ambientales.
- Eliminar requisitos ambientales.

#### Tareas

- Crear tarea autenticada.
- Bloquear creación sin token.
- Listar solo tareas del usuario.
- Admin ve todas las tareas.
- Asignar tarea a cultivo propio.
- Bloquear asignación a cultivo ajeno.
- Listar tareas por cultivo.
- Listar cultivos asociados a tarea.
- Completar tarea con `PATCH`.
- Reabrir tarea con `PATCH`.
- Actualizar tarea completa con `PUT`.
- Bloquear edición de tarea ajena.
- Eliminar tarea.
- Eliminar tarea elimina relaciones `TaskCrop`.

### Resultado de la suite completa antes de corregir

### Comando ejecutado

```bash
python -m unittest tests.test_api tests.test_phase6 -v
```

### Resultado

```text
Ran 63 tests in 22.057s

FAILED (failures=1, errors=30)
```

### Diagnóstico

Los tests de FASE 6 pasaban de forma aislada, pero la suite completa fallaba al ejecutar `test_api.py` junto con `test_phase6.py`.

El patrón principal de errores era:

- `POST /auth/register` devolvía `400 Bad Request`.
- Los tests esperaban una respuesta con `id`.
- Al recibir un error en vez de un usuario, aparecía `KeyError: 'id'`.
- También apareció un fallo donde se esperaba el mensaje `"at least 8 characters"`, pero la respuesta era `"Email already registered"`.

### Causa

Falta de aislamiento entre tests.

`test_api.py` y `test_phase6.py` estaban usando configuraciones de base de datos de test independientes o no centralizadas, lo que permitía contaminación de datos entre módulos.

---

## Claude Code — Corrección aplicada

### Archivos modificados

- `tests/conftest.py`
- `tests/test_api.py`
- `tests/test_phase6.py`

### Archivo creado

- `TEST_ISOLATION_FIX.md`

### Cambios reportados

- Centralización de la configuración de test en `tests/conftest.py`.
- Uso de un único engine SQLite in-memory para todos los tests.
- Creación de `reset_test_database()`.
- Uso compartido de:
  - `engine`;
  - `TestingSessionLocal`;
  - `override_get_db`;
  - `reset_test_database`.
- Adaptación de `test_api.py` y `test_phase6.py` para usar la configuración centralizada.
- Eliminación de engines independientes.
- Import de `pytest` hecho opcional, para no depender de pytest en unittest.

---

## Claude Code — Validación final

### Comando ejecutado

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Resultado

```text
Ran 63 tests in 36.899s

OK
```

### Tests totales

63 tests.

### Cobertura observada

- Auth y usuarios siguen pasando.
- Cultivos y catálogo siguen pasando.
- Calendario agrícola sigue pasando.
- Riego funciona.
- Requisitos ambientales funcionan.
- Tareas funcionan.
- Asignación tarea-cultivo funciona.
- Permisos por propietario/admin funcionan.
- La contaminación de BD entre módulos queda corregida.

### Incidencias observadas

- Claude necesitó una segunda iteración para corregir aislamiento de tests.
- Se mantienen redirects `307 Temporary Redirect` por rutas con/sin barra final.
- En `test_normal_user_cannot_edit_other_task`, la API devuelve `404 Not Found` para una tarea ajena. No rompe el test, y puede interpretarse como ocultación del recurso, pero conviene registrarlo como decisión/desviación frente a un `403 Forbidden`.
- Claude intentó ejecutar comandos con `pytest` durante su proceso, aunque finalmente la validación válida se realizó con `unittest`.

### Conclusión

Claude completa FASE 6 correctamente tras corregir aislamiento de tests. La suite completa queda validada con 63 tests pasando.

### Puntuación provisional FASE 6

```text
91/100
```

---

# Codex

## Estado

Validado.

## Implementación reportada

### Archivos creados

- `app/routes/irrigation.py`
- `app/routes/environmental.py`
- `app/routes/tasks.py`
- `app/schemas/irrigation.py`
- `app/schemas/environmental.py`
- `tests/test_phase6_irrigation_environmental_tasks.py`

### Archivos modificados

- `app/models/crop.py`
- `app/models/task.py`
- `app/models/user.py`
- `app/routes/crops.py`
- `app/schemas/task.py`
- `app/main.py`

### Decisiones técnicas reportadas

- Reutilización de modelos existentes:
  - `IrrigationAttributes`;
  - `EnvironmentalRequirements`;
  - `Task`;
  - `TaskCrop`.
- `POST /irrigation/` y `POST /environmental/` funcionan como creación/actualización sobre el detalle por defecto creado con el cultivo.
- Añadidas migraciones aditivas simples en `create_app()` para SQLite y bases ya existentes.
- Usuario normal solo actúa sobre cultivos/tareas propios.
- Admin puede gestionar todo.
- Tareas pueden crearse sin cultivo y asociarse luego a uno o varios cultivos.

### Endpoints reportados

#### Riego

- `/irrigation/`
- `/irrigation/{irrigation_id}`
- `/irrigation/crop/{crop_id}`

#### Requisitos ambientales

- `/environmental/`
- `/environmental/{env_id}`
- `/environmental/crop/{crop_id}`

#### Tareas

- `/tasks/`
- `/tasks/{task_id}`
- `/tasks/user/{user_id}`
- `/tasks/crop/{crop_id}`
- `/tasks/assign`
- `/tasks/{task_id}/crops`

---

## Codex — Validación final

### Comando ejecutado

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Resultado

```text
Ran 39 tests in 49.465s

OK
```

### Tests totales

39 tests.

### Tests de FASE 6 validados

- `test_assign_task_to_own_crop_and_list_relationships`
- `test_create_get_update_environmental_for_own_crop`
- `test_create_get_update_irrigation_for_own_crop`
- `test_delete_task_removes_task_crop_relationships`
- `test_normal_user_cannot_access_or_modify_environmental_of_other_crop`
- `test_normal_user_cannot_access_or_modify_irrigation_of_other_crop`
- `test_normal_user_cannot_assign_task_to_other_user_crop`
- `test_normal_user_cannot_edit_other_user_task`
- `test_patch_task_status_complete_and_reopen`
- `test_task_auth_listing_and_admin_visibility`

### Cobertura observada

- Crear, obtener y actualizar riego de cultivo propio.
- Bloquear acceso/modificación de riego de cultivo ajeno.
- Crear, obtener y actualizar requisitos ambientales de cultivo propio.
- Bloquear acceso/modificación de requisitos ambientales de cultivo ajeno.
- Crear tarea autenticada.
- Listar tareas del usuario.
- Admin puede ver tareas.
- Asignar tarea a cultivo propio.
- Bloquear asignación de tarea a cultivo ajeno.
- Listar relaciones tarea-cultivo.
- Completar y reabrir tarea con `PATCH`.
- Bloquear edición de tarea ajena.
- Eliminar tarea elimina relaciones `TaskCrop`.
- Tests previos de auth, usuarios, cultivos y calendario siguen pasando.

### Incidencias observadas

- Ejecución lenta: 49.465s para 39 tests.
- Cobertura de FASE 6 más compacta que Claude y DeepSeek.
- Codex modificó modelos existentes y añadió migraciones simples/aditivas para SQLite, lo que conviene vigilar en fases futuras.

### Conclusión

Codex completa FASE 6 correctamente. La suite completa pasa con 39 tests, sin regresiones observadas.

### Puntuación provisional FASE 6

```text
90/100
```

---

# DeepSeek

## Estado

Validado.

## Implementación reportada

### Archivos creados

- `app/routes/irrigation.py`
- `app/routes/environmental.py`
- `app/routes/task.py`

### Archivos modificados

- `app/main.py`
- `tests/test_api.py`

### Decisiones técnicas reportadas

- Los routers siguen el patrón existente de la aplicación.
- Permisos por propietario/admin.
- Admin tiene visibilidad total.
- Las tareas se implementan usando el modelo `Task` y la relación N:M `TaskCrop`.
- `PATCH /tasks/{task_id}` permite actualización parcial.
- `PUT /tasks/{task_id}` se comporta como actualización completa.
- `DELETE /tasks/{task_id}` elimina primero las relaciones `TaskCrop` y después la tarea.
- Riego y ambiente respetan la creación automática al crear cultivo.
- Los `POST` permiten crear nuevos registros si se eliminan los valores por defecto.

### Endpoints reportados

#### Riego

- `POST /irrigation/`
- `GET /irrigation/`
- `GET /irrigation/{irrigation_id}`
- `GET /irrigation/crop/{crop_id}`
- `PUT /irrigation/{irrigation_id}`
- `DELETE /irrigation/{irrigation_id}`

#### Requisitos ambientales

- `POST /environmental/`
- `GET /environmental/`
- `GET /environmental/{env_id}`
- `GET /environmental/crop/{crop_id}`
- `PUT /environmental/{env_id}`
- `DELETE /environmental/{env_id}`

#### Tareas

- `POST /tasks/`
- `GET /tasks/`
- `GET /tasks/{task_id}`
- `GET /tasks/user/{user_id}`
- `GET /tasks/crop/{crop_id}`
- `POST /tasks/assign`
- `PATCH /tasks/{task_id}`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `GET /tasks/{task_id}/crops`

---

## DeepSeek — Validación final

### Comando ejecutado

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Resultado

```text
Ran 72 tests in 48.183s

OK
```

### Tests totales

72 tests.

### Tests de FASE 6 validados

- `test_create_irrigation_for_own_crop`
- `test_get_irrigation_by_crop`
- `test_update_irrigation`
- `test_normal_user_cannot_access_other_irrigation`
- `test_normal_user_cannot_modify_other_irrigation`
- `test_create_environmental_for_own_crop`
- `test_get_environmental_by_crop`
- `test_update_environmental`
- `test_normal_user_cannot_access_other_environmental`
- `test_normal_user_cannot_modify_other_environmental`
- `test_create_task_authenticated`
- `test_create_task_without_token_fails`
- `test_list_tasks_returns_only_own`
- `test_admin_can_see_all_tasks`
- `test_assign_task_to_own_crop`
- `test_normal_user_cannot_assign_task_to_other_crop`
- `test_get_tasks_by_crop`
- `test_get_task_crops`
- `test_patch_task_complete_and_reopen`
- `test_normal_user_cannot_edit_other_task`
- `test_delete_task_removes_relations`

### Cobertura observada

- Crear riego para cultivo propio.
- Obtener riego por cultivo.
- Actualizar riego.
- Bloquear acceso a riego de cultivo ajeno.
- Bloquear modificación de riego de cultivo ajeno.
- Crear requisitos ambientales para cultivo propio.
- Obtener ambiente por cultivo.
- Actualizar requisitos ambientales.
- Bloquear acceso a ambiente de cultivo ajeno.
- Bloquear modificación de ambiente de cultivo ajeno.
- Crear tarea autenticada.
- Bloquear creación de tarea sin token.
- `GET /tasks/` devuelve solo tareas del usuario.
- Admin puede ver todas las tareas.
- Asignar tarea a cultivo propio.
- Bloquear asignación de tarea a cultivo ajeno.
- Listar tareas por cultivo.
- Listar cultivos asociados a una tarea.
- Completar y reabrir tarea con `PATCH`.
- Bloquear edición de tarea ajena.
- Eliminar tarea elimina relaciones `TaskCrop`.
- Tests previos de auth, usuarios, cultivos y calendario siguen pasando.

### Incidencias observadas

- Ninguna incidencia funcional observada en la ejecución.
- Se mantiene como observación que DeepSeek usa nombres de campos/modelos algo distintos a los pedidos originalmente:
  - riego usa `frequency_days`, `water_needed_ml`, `irrigation_method`, `notes`;
  - tareas usan `title` en vez de `name`.
- El router de tareas se llama `task.py` en vez de `tasks.py`.
- Aunque hay desviación de nombres internos, la API pasa toda la suite funcional.

### Conclusión

DeepSeek completa FASE 6 correctamente. La suite completa pasa con 72 tests, siendo la cobertura más amplia de la fase.

### Puntuación provisional FASE 6

```text
96/100
```

---

# Incidencias FASE 6

| IA | Incidencia | Severidad | Corrección necesaria | Estado |
|---|---|---|---|---|
| Claude Code | Primera suite completa falló por contaminación de BD entre `test_api.py` y `test_phase6.py` | Alta | Centralizar engine/sesión/override/reset en tests | Corregida |
| Claude Code | Redirects 307 por diferencias entre rutas con y sin barra final | Baja | Unificar rutas si se quiere reducir ruido en logs/tests | No bloqueante |
| Claude Code | Algunas operaciones sobre recursos ajenos devuelven 404 en vez de 403 | Baja | Decidir si se prefiere ocultar recurso o devolver forbidden | No bloqueante |
| Claude Code | Intentó usar pytest durante el proceso | Baja | Mantener unittest como validación oficial | No bloqueante |
| Codex | Ejecución lenta para 39 tests | Baja | Revisar setup/teardown si el tiempo sigue creciendo | No bloqueante |
| Codex | Cobertura de FASE 6 más compacta | Media | Añadir más tests si se quiere igualar a DeepSeek | No bloqueante |
| Codex | Migraciones aditivas simples en `create_app()` | Media | Vigilar en fases futuras; sustituir por Alembic si el proyecto crece | Pendiente |
| DeepSeek | Nombres internos de riego/tareas no coinciden exactamente con el prompt | Baja | Alinear nombres si se busca máxima homogeneidad | No bloqueante |
| DeepSeek | Router de tareas llamado `task.py` en vez de `tasks.py` | Baja | Renombrar si se quiere consistencia | No bloqueante |

---

# Comparación FASE 6

## Mejor cobertura de tests

**DeepSeek**.

Motivo:

- 72 tests totales.
- Cubre toda la suite previa.
- Añade una batería amplia de riego, ambiente y tareas.
- No presenta incidencias funcionales observadas en ejecución.

## Mejor suite completa sin corrección adicional

**DeepSeek y Codex**.

Motivo:

- Ambos pasan la suite completa en la primera validación local.
- Claude necesitó una corrección adicional por contaminación de BD entre módulos.

## Mejor estabilidad funcional

**DeepSeek**.

Motivo:

- Mayor cantidad de tests.
- Suite completa validada.
- No requiere corrección.
- Cobertura amplia de permisos.

## Implementación más compacta

**Codex**.

Motivo:

- 39 tests.
- Cumple requisitos principales.
- Menor cobertura que DeepSeek y Claude tras corrección.
- Tiempo de ejecución elevado para el número de tests.

## Implementación recuperada tras incidencia

**Claude Code**.

Motivo:

- Falló inicialmente la suite completa.
- Corrigió correctamente el aislamiento.
- Finalmente queda validado con 63 tests.

---

# Resultado comparativo FASE 6

| Posición | IA | Puntuación | Motivo principal |
|---:|---|---:|---|
| 1 | DeepSeek | 96/100 | Mayor cobertura, suite completa estable y sin incidencias funcionales |
| 2 | Claude Code | 91/100 | Buena cobertura tras corrección, aunque necesitó una iteración extra |
| 3 | Codex | 90/100 | Funcional y estable, pero con menor cobertura y ejecución lenta |

---

# Estado acumulado tras FASE 6

| IA | Piloto 0-3 | FASE 4 | FASE 5 | FASE 6 | Estado acumulado |
|---|---:|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | 91 | Funcional, buena cobertura, pero varias correcciones necesarias |
| Codex | 77 | 86 | 90 | 90 | Funcional y estable, cobertura media |
| DeepSeek | 87 | 94 | 96 | 96 | Mejor resultado acumulado provisional |

---

# Conclusión acumulada provisional

DeepSeek mantiene la mejor posición global tras la FASE 6. Sigue destacando por la mayor cobertura de tests, estabilidad y amplitud de permisos.

Claude Code queda en segunda posición en FASE 6 gracias a una cobertura fuerte tras corregir el problema de aislamiento. Aun así, acumula más iteraciones de corrección que las otras IAs.

Codex mantiene una implementación funcional y estable, pero más compacta. Su principal debilidad en esta fase es la menor cobertura y el tiempo de ejecución relativamente alto.

---

# Próximo paso

La siguiente fase del experimento será:

```text
FASE 7 — Dashboard y panel admin
```

Debe implementarse con el mismo método:

1. Mismo prompt para Claude, Codex y DeepSeek.
2. Cada IA trabaja solo en su carpeta.
3. No se comparten errores ni soluciones entre IAs.
4. Se ejecutan los mismos comandos de validación.
5. Se registran iteraciones, tests, incidencias y puntuación.
6. No se pasa a FASE 8 hasta cerrar FASE 7 en las tres IAs.

---

## Prompt pendiente para FASE 7

Debe prepararse un prompt común para implementar:

- dashboard de usuario;
- estadísticas de cultivos personales;
- estadísticas de tareas por estado;
- próximos eventos del calendario;
- resumen de riego y ambiente;
- panel admin básico;
- endpoints admin para usuarios;
- endpoints admin para cultivos;
- endpoints admin para tareas;
- tests de permisos admin/user;
- tests de agregación de datos;
- tests de regresión de fases anteriores.
