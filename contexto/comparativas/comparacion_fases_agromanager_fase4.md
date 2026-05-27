# Comparación por fases — AgroManager

## Objetivo del documento

Registrar la comparación longitudinal de distintas herramientas de IA reconstruyendo AgroManager por fases.

Este documento continúa después del cierre de la fase piloto, donde se evaluaron las fases 0, 1, 2 y 3:

- arquitectura base;
- modelos y schemas;
- autenticación;
- usuarios;
- permisos básicos;
- frontend mínimo;
- tests piloto;
- documentación inicial.

A partir de este punto, cada nueva fase debe compararse de forma independiente entre las IAs evaluadas.

---

## IAs evaluadas

| IA | Carpeta | Estado tras piloto |
|---|---|---|
| Claude Code | `tfg-claude/` | FASE 0-3 completada con desviaciones |
| Codex | `tfg-codex/` | FASE 0-3 completada con desviaciones |
| DeepSeek | `tfg-deepseek/` | FASE 0-3 completada con desviaciones |

---

## Fases del experimento

| Fase | Nombre | Estado |
|---|---|---|
| 0-3 | Piloto base/auth/usuarios | Cerrada |
| 4 | Cultivos y catálogo | Cerrada |
| 5 | Calendario agrícola | Pendiente |
| 6 | Riego, ambiente y tareas | Pendiente |
| 7 | Dashboard y admin | Pendiente |
| 8 | Frontend funcional usuario | Pendiente |
| 9 | Frontend admin | Pendiente |
| 10 | Seed, documentación y scripts | Pendiente |
| 11 | Tests finales | Pendiente |
| 12 | Hardening y revisión final | Pendiente |

---

## Metodología

Para comparar de forma justa:

1. Todas las IAs reciben el mismo prompt por fase.
2. Cada IA trabaja únicamente dentro de su propia carpeta.
3. No se enseña a una IA el código ni los errores generados por otra.
4. Cada corrección cuenta como una iteración adicional.
5. Se ejecutan los mismos comandos de validación.
6. Se registra:
   - número de tests;
   - resultado de tests;
   - endpoints implementados;
   - errores;
   - desviaciones;
   - calidad de permisos;
   - cobertura funcional;
   - puntuación provisional.

---

# FASE 4 — Cultivos y catálogo

## Objetivo de la fase

Implementar la gestión de cultivos personales y catálogo público.

### Endpoints requeridos

- `POST /crops/`
- `GET /crops/`
- `GET /crops/my`
- `GET /crops/published`
- `POST /crops/{crop_id}/add-to-my-crops`
- `GET /crops/{crop_id}`
- `GET /crops/user/{user_id}`
- `PUT /crops/{crop_id}`
- `DELETE /crops/{crop_id}`

### Requisitos funcionales

- Crear cultivo con `multipart/form-data`.
- Aceptar imagen opcional.
- Guardar imágenes en `uploads/crops` o implementar placeholder si no hay imagen.
- Crear datos de riego y datos ambientales por defecto al crear cultivo.
- Catálogo publicado con filtros por nombre y tipo.
- Catálogo publicado con paginación.
- Copiar cultivo desde catálogo a "Mis cultivos".
- La copia debe ser independiente del original.
- Usuario normal solo puede ver/modificar sus propios cultivos.
- Admin puede ver y gestionar todos.
- Usuario normal no puede crear cultivos publicados.
- Si un usuario elimina un cultivo original suyo, debe pasar a catálogo público en vez de desaparecer totalmente.
- Si elimina una copia, debe quitarse de sus cultivos.
- No exponer datos sensibles.
- Los tests existentes deben seguir pasando.

---

## Tabla comparativa FASE 4

| IA | Iteraciones | Backend arranca | Tests pasan | Nº tests | Endpoints completos | Permisos | Catálogo | Copias independientes | Errores | Puntuación /100 |
|---|---:|---|---|---:|---|---|---|---|---|---:|
| Claude Code | 1 | Sí | Sí | 25 | Sí | Sí | Sí | Sí | Redirects 307 por barra final; mantiene `/auth/register` | 90 |
| Codex | 1 | Sí | Sí | 15 | Sí | Sí | Sí | Sí | Menos cobertura de tests; login Swagger usa `username` aunque espera email | 86 |
| DeepSeek | 2 | Sí | Sí | 33 | Sí | Sí | Sí | Sí | Error inicial en `tearDownClass` corregido | 94 |

---

# Resultados por IA — FASE 4

## Claude Code

### Estado

Validado.

### Comando ejecutado

```bash
python -m unittest tests.test_api -v
```

### Resultado

```text
Ran 25 tests in 10.733s

OK
```

### Tests totales

25 tests.

### Tests de cultivos validados

- `test_create_crop_authenticated`
- `test_create_crop_without_token`
- `test_create_crop_normal_user_cannot_publish`
- `test_get_my_crops`
- `test_get_crop_detail`
- `test_update_crop_own`
- `test_delete_crop_own`
- `test_copy_crop_from_catalog`
- `test_copy_is_independent`
- `test_normal_user_cannot_edit_other_crop`
- `test_delete_copy_removes_from_my_crops`
- `test_delete_original_public_preserves_as_catalog`
- `test_get_published_crops_pagination_and_filters`

### Cobertura observada

- Crear cultivo autenticado.
- Bloqueo sin token.
- Usuario normal no puede publicar.
- Mis cultivos solo devuelve cultivos del usuario.
- Detalle de cultivo.
- Actualizar cultivo propio.
- Eliminar cultivo propio.
- Copiar cultivo desde catálogo.
- Copia independiente del original.
- Usuario normal no puede editar cultivo ajeno.
- Eliminar copia la quita de “Mis cultivos”.
- Eliminar original público lo conserva en catálogo.
- Catálogo publicado con paginación y filtros.
- Tests previos de auth/usuarios siguen pasando.

### Incidencias observadas

- Varias llamadas a `POST /crops/` devuelven `307 Temporary Redirect` y después `201 Created` en `/crops`. No rompe los tests, pero indica diferencia entre rutas con y sin barra final.
- Se mantiene la desviación previa de Claude: autenticación mediante `/auth/register` en vez de `POST /users/`.

### Conclusión

Claude completa FASE 4 correctamente y mantiene todos los tests previos. La implementación de cultivos queda validada por 25 tests pasando.

### Puntuación provisional FASE 4

```text
90/100
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
Ran 15 tests in 15.804s

OK
```

### Tests totales

15 tests.

### Tests de cultivos validados

- `test_admin_can_create_published_crop`
- `test_authenticated_user_can_create_crop`
- `test_copy_from_catalog_creates_independent_copy`
- `test_delete_copy_removes_it_from_my_crops`
- `test_delete_original_keeps_it_as_public_catalog_crop`
- `test_my_crops_returns_only_current_user_crops`
- `test_normal_user_cannot_edit_other_user_crop`
- `test_normal_user_cannot_publish_crop`
- `test_published_crops_can_be_paginated_and_filtered`
- `test_user_without_token_cannot_create_crop`

### Cobertura observada

- Crear cultivo autenticado.
- Usuario sin token no puede crear cultivo.
- Admin puede crear cultivo publicado.
- Usuario normal no puede publicar cultivo.
- `GET /crops/my` devuelve solo cultivos del usuario.
- Catálogo publicado con paginación y filtros.
- Copiar cultivo desde catálogo crea copia independiente.
- Usuario normal no puede editar cultivo ajeno.
- Eliminar copia la quita de mis cultivos.
- Eliminar cultivo original lo conserva como público.
- Tests previos de auth/usuarios siguen pasando.

### Incidencias observadas

- Menor número de tests que Claude y DeepSeek.
- No se observa en la salida un test específico de detalle `GET /crops/{crop_id}` ni actualización de cultivo propio, aunque podrían estar cubiertos indirectamente o implementados en API.
- Se mantiene la observación previa de Codex: el login en Swagger muestra `username`, pero realmente usa email.

### Conclusión

Codex completa FASE 4 correctamente y mantiene todos los tests previos. La implementación de cultivos queda validada por 15 tests pasando.

### Puntuación provisional FASE 4

```text
86/100
```

---

## DeepSeek

### Estado

Validado tras una corrección.

### Comando ejecutado

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

### Primera ejecución

La primera ejecución mostró que todos los tests funcionales aparecían como `ok`, pero la batería falló al final por un error de limpieza de SQLite en Windows:

```text
Ran 33 tests in 20.641s

FAILED (errors=1)
```

Error principal:

```text
PermissionError: [WinError 32] El proceso no tiene acceso al archivo porque está siendo utilizado por otro proceso:
test_agromanager.db
```

Diagnóstico:

- La funcionalidad de cultivos parecía correcta.
- El error ocurría en `tearDownClass`.
- La base SQLite seguía bloqueada al intentar eliminar el archivo de test.
- Se pidió una corrección limitada a cerrar conexiones/sesiones o limpiar la base sin borrar un archivo bloqueado.

### Segunda ejecución tras corrección

```text
Ran 33 tests in 20.158s
```

En la salida final no aparece `FAILED` ni errores, y todos los tests listados aparecen como `ok`.

### Tests totales

33 tests.

### Tests de cultivos validados

- `test_add_to_my_crops_creates_independent_copy`
- `test_admin_can_create_public_crop`
- `test_admin_can_see_all_crops`
- `test_create_crop_authenticated`
- `test_create_crop_without_token_fails`
- `test_delete_copy_removes_it`
- `test_delete_original_conserves_as_public`
- `test_edit_copy_does_not_modify_original`
- `test_get_user_crops_other_forbidden`
- `test_get_user_crops_own`
- `test_my_crops_returns_only_user_crops`
- `test_normal_user_cannot_create_public_crop`
- `test_normal_user_cannot_edit_other_crop`
- `test_normal_user_crop_list_only_own`
- `test_published_crops_pagination_and_filters`
- `test_user_cannot_add_non_public_crop`

### Cobertura observada

- Crear cultivo autenticado.
- Usuario sin token no puede crear cultivo.
- Admin puede crear cultivo publicado.
- Admin puede ver todos los cultivos.
- Usuario normal no puede crear cultivo público.
- Usuario normal solo ve sus propios cultivos.
- Usuario normal no puede ver cultivos de otro usuario.
- Usuario normal no puede editar cultivo ajeno.
- Catálogo publicado con filtros y paginación.
- Copia independiente desde catálogo.
- Editar copia no modifica original.
- Eliminar copia la quita de mis cultivos.
- Eliminar cultivo original lo conserva como público.
- No se puede añadir un cultivo no publicado a mis cultivos.
- Tests anteriores de usuarios/auth siguen pasando.

### Incidencias observadas

- En una ejecución anterior falló `tearDownClass` al intentar eliminar `test_agromanager.db` porque SQLite seguía bloqueada en Windows.
- En la ejecución corregida ya no aparece el fallo.
- No se observa en la salida final una línea explícita `OK`, pero tampoco aparece `FAILED` ni errores.

### Conclusión

DeepSeek completa FASE 4 correctamente y mantiene todos los tests previos. La implementación de cultivos queda validada por 33 tests ejecutados correctamente, después de corregir el problema de limpieza de SQLite en Windows.

### Puntuación provisional FASE 4

```text
94/100
```

---

# Incidencias FASE 4

| IA | Incidencia | Severidad | Corrección necesaria | Estado |
|---|---|---|---|---|
| Claude Code | Redirects 307 por diferencia entre `/crops/` y `/crops` | Baja | Unificar rutas con o sin barra final si se quiere evitar ruido en tests/logs | No bloqueante |
| Claude Code | Mantiene desviación previa: registro en `/auth/register` | Media | Adaptar a `POST /users/` en una fase de hardening | Pendiente |
| Codex | Menor cobertura de tests que Claude y DeepSeek | Media | Añadir tests de detalle y actualización propia si se quiere igualar cobertura | No bloqueante |
| Codex | Login Swagger usa `username`, pero espera email | Baja | Documentar o ajustar esquema de login | No bloqueante |
| DeepSeek | Primer intento falló en `tearDownClass` por SQLite bloqueada en Windows | Media | Cerrar sesiones/conexiones o limpiar tablas sin borrar archivo bloqueado | Corregida |
| DeepSeek | No aparece línea final explícita `OK` en la salida copiada | Baja | Repetir ejecución si se desea confirmar visualmente `OK` | No bloqueante |

---

# Comparación FASE 4

## Mejor cobertura de tests

**DeepSeek**.

Motivo:

- 33 tests totales.
- Cubre permisos, catálogo, copias, edición de copias, visibilidad por usuario, admin, token inválido y casos negativos adicionales.

## Mejor primera ejecución sin corrección

**Claude Code y Codex**.

Motivo:

- Ambos pasaron los tests de FASE 4 sin error final de limpieza.
- DeepSeek necesitó una corrección por el problema de SQLite bloqueada en Windows.

## Mejor implementación validada por cobertura

**DeepSeek**.

Motivo:

- Mayor número de tests.
- Mayor cobertura explícita de permisos.
- Incluye caso adicional: no se puede añadir a mis cultivos un cultivo no publicado.
- Mantiene los tests previos de auth/usuarios.

## Implementación más equilibrada

**Claude Code**.

Motivo:

- 25 tests.
- Buena cobertura de detalle, actualización, permisos, catálogo y copias.
- Puntuación alta, aunque conserva desviaciones previas y redirects 307.

## Implementación más ligera

**Codex**.

Motivo:

- 15 tests totales.
- Cumple los requisitos principales, pero con menor cobertura de casos que Claude y DeepSeek.

---

# Resultado comparativo FASE 4

| Posición | IA | Puntuación | Motivo principal |
|---:|---|---:|---|
| 1 | DeepSeek | 94/100 | Mejor cobertura de tests y permisos, aunque necesitó corregir limpieza de SQLite |
| 2 | Claude Code | 90/100 | Muy buena cobertura y validación, pero mantiene desviación `/auth/register` y redirects 307 |
| 3 | Codex | 86/100 | Funcional y válido, pero con menor cobertura de tests |

---

# Estado acumulado tras FASE 4

| IA | Piloto 0-3 | FASE 4 | Estado acumulado |
|---|---:|---:|---|
| Claude Code | 75/100 | 90/100 | Funcional, con desviaciones persistentes |
| Codex | 77/100 | 86/100 | Funcional, mejora en FASE 4, cobertura más ligera |
| DeepSeek | 87/100 | 94/100 | Mejor resultado acumulado provisional |

---

# Conclusión acumulada provisional

DeepSeek mantiene la mejor posición global tras la FASE 4, principalmente por su mayor cobertura de tests y por prestar más atención a permisos y casos negativos.

Claude Code mejora mucho en FASE 4, con una implementación sólida y bastante cubierta, aunque arrastra desviaciones del piloto como `/auth/register` en lugar de `POST /users/`.

Codex se mantiene funcional y correcto, pero su implementación es más ligera y con menos tests, por lo que resulta menos fuerte para comparar robustez.

---

# Próximo paso

La siguiente fase del experimento será:

```text
FASE 5 — Calendario agrícola
```

Debe implementarse con el mismo método:

1. Mismo prompt para Claude, Codex y DeepSeek.
2. Cada IA trabaja solo en su carpeta.
3. No se comparten errores ni soluciones entre IAs.
4. Se ejecutan los mismos comandos de validación.
5. Se registran iteraciones, tests, incidencias y puntuación.
6. No se pasa a FASE 6 hasta cerrar FASE 5 en las tres IAs.

---

## Prompt pendiente para FASE 5

Debe prepararse un prompt común para implementar calendario agrícola con:

- creación/actualización de calendario por cultivo;
- activación solo si fechas completas;
- eventos por mes y quincena ignorando año;
- fase actual visible;
- avance de fase;
- finalización de ciclo;
- permisos por propietario/admin;
- tests para calendario incompleto, completo, eventos, avance, finalización, permisos e independencia del año.
