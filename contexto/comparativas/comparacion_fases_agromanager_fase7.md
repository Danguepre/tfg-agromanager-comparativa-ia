# Comparación por fases — AgroManager

## FASE 7 — Dashboard de usuario y panel admin básico

## Objetivo de la fase

Implementar endpoints de dashboard para usuario autenticado y endpoints básicos de administración.

La fase debe permitir:

1. Consultar un dashboard personal agregado.
2. Obtener estadísticas de cultivos, tareas, calendario, riego y ambiente.
3. Gestionar usuarios desde panel admin.
4. Gestionar cultivos desde panel admin.
5. Gestionar tareas desde panel admin.
6. Mantener permisos estrictos entre usuario normal y admin.
7. Mantener la suite completa de fases anteriores sin regresiones.

---

## Endpoints requeridos

### Dashboard de usuario

- `GET /dashboard/summary`
- `GET /dashboard/crops`
- `GET /dashboard/tasks`
- `GET /dashboard/calendar`
- `GET /dashboard/irrigation`
- `GET /dashboard/environmental`

### Panel admin

- `GET /admin/summary`
- `GET /admin/users`
- `GET /admin/users/{user_id}`
- `PATCH /admin/users/{user_id}`
- `DELETE /admin/users/{user_id}`
- `GET /admin/crops`
- `GET /admin/crops/{crop_id}`
- `PATCH /admin/crops/{crop_id}`
- `DELETE /admin/crops/{crop_id}`
- `GET /admin/tasks`
- `GET /admin/tasks/{task_id}`
- `PATCH /admin/tasks/{task_id}`
- `DELETE /admin/tasks/{task_id}`

---

## Reglas funcionales esperadas

### Dashboard

- El dashboard debe estar protegido por token.
- Usuario sin token debe recibir `401`.
- El dashboard debe devolver información solo del usuario autenticado.
- Admin, al usar dashboard normal, debe ver su propio dashboard, no un dashboard global.
- Debe incluir total de cultivos personales.
- Debe incluir cultivos públicos/copias si aplica.
- Debe incluir tareas por estado: `pending` / `completed`.
- Debe incluir próximas tareas pendientes.
- Debe incluir próximos eventos activos del calendario.
- Debe incluir fase actual de calendarios activos.
- Debe incluir resumen de riego por cultivo.
- Debe incluir resumen ambiental por cultivo.

### Panel admin

- Solo usuarios admin pueden acceder.
- Usuario normal debe recibir `403`.
- `/admin/summary` debe incluir:
  - total de usuarios;
  - total de cultivos;
  - total de cultivos públicos;
  - total de tareas;
  - tareas pendientes;
  - tareas completadas;
  - total de calendarios activos;
  - total de calendarios completados.
- Admin puede listar/ver usuarios.
- Admin puede activar/desactivar usuario si existe campo `is_active`.
- Admin puede editar campos básicos de usuario permitidos.
- Admin no debe ver `password` ni `password_hash`.
- Admin puede listar/ver/modificar/eliminar cultivos.
- Admin puede listar/ver/modificar/eliminar tareas.
- Mantener permisos existentes del resto de rutas.

### Frontend

- No se pedía todavía un frontend funcional avanzado.
- Se permitían placeholders o páginas mínimas.
- La prioridad de la fase era backend + tests.

---

## Tabla comparativa FASE 7

| IA | Iteraciones | Tests pasan | Nº tests | Dashboard usuario | Estadísticas | Admin usuarios | Admin cultivos | Admin tareas | Permisos | Errores / desviaciones | Puntuación /100 |
|---|---:|---|---:|---|---|---|---|---|---|---|---:|
| Claude Code | 1 | Sí | 83 | Sí | Sí | Sí | Sí | Sí | Sí | Redirects 307; mantiene `/auth/register`; frontend placeholder | 92 |
| Codex | 1 | Sí | 50 | Sí | Sí | Sí | Sí | Sí | Sí | Suite lenta; cobertura más compacta; frontend no avanzado | 91 |
| DeepSeek | 1 | Sí | 104 | Sí | Sí | Sí | Sí | Sí | Sí | Ninguna funcional observada; suite más lenta pero más amplia | 97 |

---

# Resultados por IA — FASE 7

## Claude Code

### Estado

Validado.

### Comando ejecutado

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Resultado

```text
Ran 83 tests in 49.847s

OK
```

### Tests totales

83 tests.

### Tests de dashboard/admin validados

- `test_dashboard_summary_authenticated`
- `test_dashboard_summary_unauthenticated`
- `test_dashboard_crops`
- `test_dashboard_crops_only_user_data`
- `test_dashboard_tasks_pending_completed`
- `test_dashboard_calendar`
- `test_dashboard_irrigation`
- `test_dashboard_environmental`
- `test_admin_summary_admin_only`
- `test_admin_list_users`
- `test_admin_get_user_by_id`
- `test_admin_update_user`
- `test_admin_delete_user`
- `test_admin_list_crops`
- `test_admin_update_crop`
- `test_admin_delete_crop`
- `test_admin_list_tasks`
- `test_admin_update_task`
- `test_admin_delete_task`
- `test_normal_user_cannot_access_admin_endpoints`

### Cobertura observada

- Dashboard accesible con token.
- Dashboard bloqueado sin token.
- Dashboard de cultivos solo muestra datos del usuario.
- Dashboard separa tareas `pending` y `completed`.
- Dashboard incluye calendario.
- Dashboard incluye riego.
- Dashboard incluye requisitos ambientales.
- Admin puede acceder a resumen global.
- Usuario normal no puede acceder a admin.
- Admin puede listar/ver/actualizar/eliminar usuarios.
- Admin puede listar/actualizar/eliminar cultivos.
- Admin puede listar/actualizar/eliminar tareas.
- No se observan regresiones en fases anteriores.

### Frontend observado

El frontend de Claude sigue siendo una pantalla mínima de estado del backend:

- Muestra título de AgroManager.
- Muestra estado del backend.
- Muestra lista de features de próximas fases.
- No implementa dashboard visual.
- No implementa panel admin visual.

Esto no se considera error bloqueante porque FASE 7 priorizaba endpoints backend y tests, y el prompt indicaba no implementar frontend avanzado completo.

### Incidencias observadas

- Se mantienen redirects `307 Temporary Redirect` en varias rutas con/sin barra final.
- Claude sigue usando `/auth/register` en la base de auth.
- No se ve en la salida un test específico de lectura individual de:
  - `GET /admin/crops/{crop_id}`;
  - `GET /admin/tasks/{task_id}`;
  aunque sí se usan indirectamente tras borrar para comprobar `404`.
- Suite cercana a 50 segundos.
- Frontend permanece como placeholder, aceptable según alcance de FASE 7.

### Conclusión

Claude completa FASE 7 correctamente. La suite completa queda validada con 83 tests pasando.

### Puntuación provisional FASE 7

```text
92/100
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
Ran 50 tests in 66.297s

OK
```

### Tests totales

50 tests.

### Tests de dashboard/admin validados

- `test_admin_crop_endpoints_can_list_get_update_delete`
- `test_admin_summary_allowed_and_normal_user_forbidden`
- `test_admin_task_endpoints_can_list_get_update_delete`
- `test_admin_user_endpoints_do_not_expose_password_and_can_update_delete`
- `test_admin_uses_own_normal_dashboard`
- `test_authenticated_user_can_read_dashboard_summary_and_counts`
- `test_dashboard_only_includes_current_user_data`
- `test_dashboard_requires_token`
- `test_normal_user_cannot_use_admin_crop_endpoints`
- `test_normal_user_cannot_use_admin_task_endpoints`
- `test_normal_user_cannot_use_admin_user_endpoints`

### Cobertura observada

- Dashboard requiere token.
- Usuario autenticado puede consultar resumen.
- Dashboard solo incluye datos del usuario actual.
- Admin usando dashboard normal ve su propio dashboard, no un dashboard global.
- Admin puede acceder a `/admin/summary`.
- Usuario normal no puede acceder a `/admin/summary`.
- Admin puede listar/ver/actualizar/eliminar usuarios sin exponer password.
- Admin puede listar/ver/actualizar/eliminar cultivos.
- Admin puede listar/ver/actualizar/eliminar tareas.
- Usuario normal no puede usar endpoints admin de usuarios.
- Usuario normal no puede usar endpoints admin de cultivos.
- Usuario normal no puede usar endpoints admin de tareas.
- Tests previos de auth, usuarios, cultivos, calendario, riego, ambiente y tareas siguen pasando.

### Incidencias observadas

- Ejecución lenta: 66.297s para 50 tests.
- Menor cobertura total que Claude y DeepSeek.
- Los casos de FASE 7 son bastante completos, pero agrupados en menos tests.
- Mantiene la desviación previa de Codex: login Swagger usa `username`, aunque espera email.
- No se observa frontend funcional avanzado, aceptable según alcance de FASE 7.

### Conclusión

Codex completa FASE 7 correctamente. La suite completa queda validada con 50 tests pasando, sin regresiones observadas.

### Puntuación provisional FASE 7

```text
91/100
```

---

## DeepSeek

### Estado

Validado.

### Comando ejecutado

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Resultado

```text
Ran 104 tests in 69.273s

OK
```

### Tests totales

104 tests.

### Tests de dashboard/admin validados

- `test_admin_can_access_admin_summary`
- `test_admin_delete_crop`
- `test_admin_delete_task`
- `test_admin_delete_user`
- `test_admin_get_crop_by_id`
- `test_admin_get_nonexistent_crop_404`
- `test_admin_get_nonexistent_task_404`
- `test_admin_get_nonexistent_user_404`
- `test_admin_get_task_by_id`
- `test_admin_get_user_by_id_no_password`
- `test_admin_list_crops`
- `test_admin_list_tasks`
- `test_admin_list_users_no_password`
- `test_admin_update_crop`
- `test_admin_update_task`
- `test_admin_update_user`
- `test_admin_update_user_deactivate`
- `test_dashboard_calendar_endpoint`
- `test_dashboard_crops_endpoint`
- `test_dashboard_environmental_endpoint`
- `test_dashboard_irrigation_endpoint`
- `test_dashboard_summary_authenticated_user`
- `test_dashboard_summary_calendar_and_phase`
- `test_dashboard_summary_irrigation_and_environmental`
- `test_dashboard_summary_only_own_data`
- `test_dashboard_summary_tasks_counts`
- `test_dashboard_tasks_endpoint`
- `test_dashboard_without_token_fails`
- `test_normal_user_cannot_access_admin_summary`
- `test_normal_user_cannot_admin_crops`
- `test_normal_user_cannot_admin_tasks`
- `test_normal_user_cannot_admin_users`

### Cobertura observada

- Dashboard requiere token.
- Usuario autenticado puede ver resumen.
- Dashboard solo incluye datos del usuario autenticado.
- Dashboard cuenta tareas `pending/completed`.
- Dashboard incluye calendarios activos y fase actual.
- Dashboard incluye resumen de riego y ambiente.
- Dashboard tiene endpoints separados para cultivos, tareas, calendario, riego y ambiente.
- Admin puede consultar resumen global.
- Usuario normal no puede acceder al resumen admin.
- Admin puede listar/ver/actualizar/eliminar usuarios.
- Admin puede desactivar usuario con `is_active`.
- Admin puede listar/ver/actualizar/eliminar cultivos.
- Admin puede listar/ver/actualizar/eliminar tareas.
- Usuario normal no puede usar endpoints admin de usuarios, cultivos ni tareas.
- Endpoints admin devuelven `404` en recursos inexistentes.
- No se observan regresiones en fases anteriores.

### Incidencias observadas

- Ejecución más larga: 69.273s.
- Se mantienen desviaciones internas previas de DeepSeek:
  - algunos nombres internos de campos/modelos no coinciden exactamente con el prompt;
  - router de tareas llamado `task.py` en vez de `tasks.py`.
- No se observa frontend funcional avanzado, aceptable según alcance de FASE 7.

### Conclusión

DeepSeek completa FASE 7 correctamente. La suite completa queda validada con 104 tests pasando, con la cobertura más amplia de la fase.

### Puntuación provisional FASE 7

```text
97/100
```

---

# Incidencias FASE 7

| IA | Incidencia | Severidad | Corrección necesaria | Estado |
|---|---|---|---|---|
| Claude Code | Redirects 307 por rutas con/sin barra final | Baja | Unificar rutas si se quiere reducir ruido en logs/tests | No bloqueante |
| Claude Code | Mantiene `/auth/register` en vez de `POST /users/` | Media | Corregir en fase de hardening si se busca homogeneidad | Pendiente |
| Claude Code | Frontend sigue como placeholder | Baja | Resolver en FASE 8/9 | Aceptable |
| Claude Code | No se observa test explícito de lectura individual de admin crop/task | Baja | Añadir tests si se quiere igualar cobertura DeepSeek | No bloqueante |
| Codex | Suite lenta para 50 tests | Baja | Revisar setup/teardown si el tiempo sigue creciendo | No bloqueante |
| Codex | Cobertura más compacta que Claude y DeepSeek | Media | Añadir más casos admin/dashboard si se quiere igualar robustez | No bloqueante |
| Codex | Mantiene login Swagger `username` aunque espera email | Baja | Ajustar schema/documentación | No bloqueante |
| Codex | Frontend no avanzado | Baja | Resolver en FASE 8/9 | Aceptable |
| DeepSeek | Suite más lenta, aunque con más tests | Baja | Vigilar tiempo de ejecución en fases siguientes | No bloqueante |
| DeepSeek | Desviaciones internas previas de nombres/modelos | Baja | Homogeneizar en hardening si se busca consistencia | No bloqueante |
| DeepSeek | Frontend no avanzado | Baja | Resolver en FASE 8/9 | Aceptable |

---

# Comparación FASE 7

## Mejor cobertura de tests

**DeepSeek**.

Motivo:

- 104 tests totales.
- Cubre dashboard, admin, usuarios, cultivos, tareas y casos 404.
- Mantiene toda la suite previa pasando.

## Mejor cobertura admin

**DeepSeek**.

Motivo:

- Incluye endpoints individuales de usuarios, cultivos y tareas.
- Incluye actualización y eliminación.
- Incluye desactivación de usuario con `is_active`.
- Incluye casos de recurso inexistente con `404`.

## Mejor dashboard validado por tests

**DeepSeek**.

Motivo:

- Cubre resumen, cultivos, tareas, calendario, riego y ambiente.
- Verifica datos propios del usuario.
- Verifica tareas `pending/completed`.
- Verifica calendario y fase actual.
- Verifica riego y ambiente.

## Implementación más equilibrada

**Claude Code**.

Motivo:

- 83 tests.
- Buena cobertura de dashboard y admin.
- Suite completa estable.
- Sin embargo, mantiene desviaciones persistentes y frontend placeholder.

## Implementación más compacta

**Codex**.

Motivo:

- 50 tests.
- Cumple requisitos principales.
- Cobertura más resumida.
- Ejecución lenta en proporción al número de tests.

---

# Resultado comparativo FASE 7

| Posición | IA | Puntuación | Motivo principal |
|---:|---|---:|---|
| 1 | DeepSeek | 97/100 | Mayor cobertura, mejor panel admin y más casos negativos |
| 2 | Claude Code | 92/100 | Buena cobertura y suite estable, aunque con desviaciones persistentes |
| 3 | Codex | 91/100 | Cumple bien la fase, pero con cobertura más compacta y ejecución lenta |

---

# Estado acumulado tras FASE 7

| IA | Piloto 0-3 | FASE 4 | FASE 5 | FASE 6 | FASE 7 | Estado acumulado |
|---|---:|---:|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | 91 | 92 | Funcional, buena cobertura, pero con desviaciones persistentes |
| Codex | 77 | 86 | 90 | 90 | 91 | Funcional y estable, cobertura media |
| DeepSeek | 87 | 94 | 96 | 96 | 97 | Mejor resultado acumulado provisional |

---

# Conclusión acumulada provisional

DeepSeek mantiene la mejor posición global tras la FASE 7. Destaca por la cobertura más amplia, mejor panel admin y más casos negativos.

Claude Code mantiene una implementación sólida y con bastante cobertura, pero arrastra desviaciones persistentes desde fases anteriores, como `/auth/register`, redirects `307` y frontend placeholder.

Codex sigue siendo funcional y estable, pero con una cobertura más compacta. Su suite de tests también se está volviendo lenta en proporción al número de casos.

---

# Próximo paso

La siguiente fase del experimento será:

```text
FASE 8 — Frontend funcional de usuario
```

Debe implementarse con el mismo método:

1. Mismo prompt para Claude, Codex y DeepSeek.
2. Cada IA trabaja solo en su carpeta.
3. No se comparten errores ni soluciones entre IAs.
4. Se ejecutan los mismos comandos de validación.
5. Se registra:
   - build frontend;
   - tests backend;
   - incidencias visuales;
   - rutas frontend;
   - conexión con API;
   - puntuación.
6. No se pasa a FASE 9 hasta cerrar FASE 8 en las tres IAs.

---

## Prompt pendiente para FASE 8

Debe prepararse un prompt común para implementar frontend funcional de usuario con:

- login;
- registro;
- almacenamiento de token;
- logout;
- dashboard visual de usuario;
- listado de cultivos personales;
- catálogo público;
- detalle de cultivo;
- calendario visual básico;
- tareas del usuario;
- estados de carga/error;
- protección de rutas;
- uso de Fetch API;
- `npm run build` sin errores;
- backend tests siguen pasando.
