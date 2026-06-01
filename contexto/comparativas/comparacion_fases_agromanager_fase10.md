# Comparación por fases — AgroManager

## FASE 10 — Seed/admin inicial y datos de ejemplo

**Estado del documento:** Final  
**Motivo:** Codex, DeepSeek y Claude Code están validados. Claude Code fue completado posteriormente tras una interrupción temporal por cuota/herramienta y una corrección para alinear sus criterios con Codex y DeepSeek.

---

## Objetivo de la fase

La FASE 10 tiene como objetivo preparar la aplicación para una demostración completa sin necesidad de manipular manualmente la base SQLite.

En fases anteriores, especialmente FASE 8 y FASE 9, la aplicación funcionaba correctamente, pero era necesario crear usuarios, roles admin y datos de prueba de forma manual. Esta fase corrige ese problema incorporando un seed de desarrollo/demo.

El seed debe permitir probar:

- login de usuario administrador;
- login de usuario normal;
- catálogo público;
- cultivos personales;
- calendario agrícola;
- tareas;
- riego;
- requisitos ambientales;
- panel admin;
- dashboard con datos reales;
- idempotencia del proceso.

---

## Alcance funcional esperado

### Datos mínimos esperados

- Usuario admin:
  - `admin@test.com / admin123`
- Usuario normal:
  - `user@test.com / user123`
- Al menos 5 cultivos públicos.
- Al menos 2 cultivos personales.
- Al menos 4 tareas.
- Al menos 1 calendario activo.
- Datos de riego.
- Requisitos ambientales.
- Documentación del seed.
- Tests automáticos.
- Build frontend correcto.
- Sin romper fases anteriores.

### Requisitos técnicos

- Script idempotente.
- Contraseñas hasheadas.
- No usar secretos reales.
- No depender de la base real en tests.
- Mantener `unittest`.
- Mantener `fastapi.testclient.TestClient`.
- Mantener React/Vite.
- No implementar todavía Alembic/migraciones.
- No implementar todavía tests E2E.

---

# Tabla comparativa final FASE 10

| IA | Estado | Seed | Tests | Build | Visual | Incidencias | Puntuación final |
|---|---|---|---|---|---|---|---:|
| Claude Code | Validado y cerrado tras ajuste | OK, idempotente | OK, 106 tests | OK, 569ms | OK | Primera versión funcional pero incompleta; corregida con tests y 2 cultivos personales | 94 |
| Codex | Validado y cerrado | OK, idempotente | OK, 52 tests con `discover` | OK, 90ms | OK | Ninguna bloqueante | 94 |
| DeepSeek | Validado y cerrado tras corrección | OK, idempotente | OK, 117 tests ejecución conjunta explícita | OK, 582ms | OK | Contaminación de `get_db` corregida | 95 |

---

# Codex — FASE 10

## Estado

**Validado y cerrado.**

Codex implementó correctamente un sistema de seed demo idempotente, con usuarios, cultivos, calendarios, tareas, riego, requisitos ambientales y guías. Además, los tests pasan en el comando estándar con `unittest discover`.

---

## Archivos creados

- `scripts/seed_demo.py`
- `tests/test_seed_demo.py`
- `SEED_DEMO.md`

## Archivos modificados

- `README.md`

---

## Comando de seed

```bash
cd C:\Users\danie\Desktop\tfg\tfg-codex
python scripts\seed_demo.py
```

---

## Resultado del seed validado

```text
AgroManager demo seed completed.
- calendars: 0 created, 7 existing
- crops: 0 created, 7 existing
- environmental: 0 created, 7 existing
- guides: 0 created, 7 existing
- irrigation: 0 created, 7 existing
- task_crop_links: 0 created, 4 existing
- tasks: 0 created, 4 existing
- users: 0 created, 2 existing
```

Este resultado confirma que el seed es idempotente: al volver a ejecutarlo, detecta datos existentes y no duplica registros.

---

## Credenciales demo

| Rol | Email | Contraseña |
|---|---|---|
| Admin | `admin@test.com` | `admin123` |
| Usuario normal | `user@test.com` | `user123` |

---

## Datos demo creados

| Tipo | Cantidad |
|---|---:|
| Usuarios | 2 |
| Cultivos públicos/personales totales | 7 |
| Cultivos públicos | 5 |
| Cultivos personales | 2 |
| Calendarios | 7 |
| Tareas | 4 |
| Relaciones tarea-cultivo | 4 |
| Riego | 7 |
| Requisitos ambientales | 7 |
| Guías | 7 |

---

## Idempotencia

Codex garantiza la idempotencia mediante comprobaciones previas basadas en:

- email para usuarios;
- `name + is_public` para cultivos públicos;
- `owner_id + name` para cultivos personales;
- relaciones uno-a-uno por cultivo;
- `user_id + task name` para tareas.

---

## Tests backend

Comando ejecutado:

```bash
cd C:\Users\danie\Desktop\tfg\tfg-codex
python -m unittest discover -s tests -p "test*.py" -v
```

Resultado:

```text
Ran 52 tests in 67.323s

OK
```

Tests de seed incluidos:

- `test_seed_creates_demo_data_and_is_idempotent`
- `test_seeded_users_can_login_and_public_catalog_returns_data`

---

## Build frontend

Comando ejecutado:

```bash
cd C:\Users\danie\Desktop\tfg\tfg-codex\frontend
npm.cmd run build
```

Resultado:

```text
vite v8.0.13 building client environment for production...
✓ 16 modules transformed.
computing gzip size...
dist/index.html                   0.40 kB │ gzip:  0.27 kB
dist/assets/index-LsF5PRld.css    4.72 kB │ gzip:  1.59 kB
dist/assets/index-CsCQDoGq.js   215.93 kB │ gzip: 66.86 kB

✓ built in 90ms
```

---

## Validación visual

### Admin

El dashboard admin muestra datos reales de catálogo:

- cultivos: 5;
- públicos: 5.

### Usuario normal

El dashboard de usuario muestra datos completos:

- cultivos: 2;
- tareas pendientes: 2;
- tareas completadas: 2;
- calendarios activos: 1;
- copias: 2;
- próximo evento: `Mi Tomate — Trasplante`.

---

## Fortalezas Codex

- Seed integrado con la suite estándar.
- `unittest discover` pasa completo.
- Build frontend muy rápido.
- Seed idempotente.
- Datos demo suficientes para demostrar frontend usuario y panel admin.
- No requiere modificar manualmente SQLite.
- Documentación específica `SEED_DEMO.md`.

---

## Limitaciones Codex

| Limitación | Impacto | Estado |
|---|---|---|
| No hay migraciones/Alembic | La estructura DB depende de `create_all` o base limpia | Pendiente |
| Sin tests E2E | No valida flujos completos de navegador | Pendiente |
| Compatibilidad defensiva con tabla legacy `tasks` | Puede indicar arrastre de estructura previa local | No bloqueante |
| `npm run build` bloqueado por política PowerShell | Se usa `npm.cmd run build` | Entorno local |

---

## Incidencias Codex

No se detectaron incidencias bloqueantes en FASE 10.

---

## Puntuación final Codex FASE 10

```text
94/100
```

### Justificación

Codex cumple la fase de forma estable y muy integrada. Destaca especialmente que el comando estándar `unittest discover` pasa completo junto con los tests de seed. Se penaliza ligeramente por menor cobertura específica de seed que DeepSeek y por ausencia de migraciones/E2E, aunque estas no estaban dentro del alcance obligatorio.

---

# DeepSeek — FASE 10

## Estado

**Validado y cerrado tras corrección.**

DeepSeek implementó un seed demo más amplio en cobertura de tests, con 13 tests específicos para esta fase. Inicialmente apareció una incidencia grave de aislamiento entre tests, pero fue corregida correctamente.

---

## Archivos creados

- `scripts/seed_demo.py`
- `tests/test_seed.py`
- `SEED_DEMO.md`

---

## Comando de seed

```bash
cd C:\Users\danie\Desktop\tfg\tfg-deepseek
python scripts\seed_demo.py
```

---

## Credenciales demo

| Rol | Email | Contraseña |
|---|---|---|
| Admin | `admin@test.com` | `admin123` |
| Usuario normal | `user@test.com` | `user123` |

---

## Datos demo creados

| Tipo | Cantidad | Detalles |
|---|---:|---|
| Usuarios | 2 base / 3 observados en validación visual | admin, user y usuario previo del entorno |
| Cultivos públicos | 5 | Tomate, Lechuga, Zanahoria, Pimiento, Fresa |
| Cultivos personales | 2 | Mi Tomate, Mi Lechuga |
| Cultivos totales | 7 | 5 públicos + 2 personales |
| Calendarios | 3 | 2 activos y 1 completado observados |
| Tareas | 4 | 2 pending y 2 completed |
| Riego | 7 | catálogo + personales |
| Ambiente | 7 | catálogo + personales |
| Guías de cultivo | 5 | una por cultivo del catálogo |

---

## Idempotencia

DeepSeek garantiza la idempotencia mediante comprobaciones basadas en:

- email para usuarios;
- `name + is_public=True` para cultivos públicos;
- `name + owner_id` para cultivos personales;
- `title + owner_id` para tareas;
- `crop_id` para calendarios.

---

## Tests añadidos

DeepSeek añadió 13 tests específicos en `tests/test_seed.py`:

- `test_seed_creates_admin`
- `test_seed_creates_normal_user`
- `test_seed_creates_public_crops`
- `test_seed_is_idempotent`
- `test_passwords_are_hashed`
- `test_admin_can_login_after_seed`
- `test_normal_user_can_login_after_seed`
- `test_public_catalog_returns_data_after_seed`
- `test_seed_does_not_duplicate_on_second_run`
- `test_seed_creates_personal_crops`
- `test_seed_creates_tasks`
- `test_seed_has_pending_and_completed_tasks`
- `test_wrong_password_after_seed`

---

## Incidencia detectada

### Problema inicial

Al ejecutar la suite completa, aparecieron 98 errores con:

```text
sqlite3.OperationalError: no such table: users
```

### Causa

`tests/test_api.py` y `tests/test_seed.py` definían `app.dependency_overrides[get_db]` a nivel de módulo. Al cargar ambos módulos, un override sobrescribía al otro. Esto provocaba que:

- un test preparase tablas en una base;
- las rutas FastAPI apuntasen a otra;
- algunos tests ejecutasen consultas contra una base sin tablas.

### Corrección

DeepSeek movió los overrides a `setUpClass()` y limpió los overrides en `tearDownClass()`.

Archivos corregidos:

- `tests/test_api.py`
- `tests/test_seed.py`

### Resultado de la corrección

- Cada clase instala su propio override durante su ciclo.
- Cada clase elimina el override al terminar.
- Cada engine se cierra con `dispose()`.
- Se evita contaminación entre bases de datos de test.

---

## Tests backend

Comando validado:

```bash
cd C:\Users\danie\Desktop\tfg\tfg-deepseek
python -m unittest tests.test_api tests.test_seed -v
```

Resultado:

```text
Ran 117 tests in 75.840s

OK
```

Observación metodológica:

- DeepSeek indicó problemas con `unittest discover` en Windows/PowerShell.
- Se validó la ejecución conjunta explícita de los módulos afectados.
- La ejecución conjunta incluye los 104 tests API y los 13 tests seed, totalizando 117 tests.

---

## Build frontend

Resultado reportado tras corrección:

```text
✓ built in 582ms
dist/index.html                  0.33 kB
dist/assets/index-Byj7vGJZ.js  235.03 kB
✓ built successfully
```

---

## Validación visual

### Admin

Dashboard admin observado:

- usuarios totales: 3;
- cultivos totales: 7;
- cultivos públicos: 5;
- tareas totales: 4;
- tareas pendientes: 2;
- tareas completadas: 2;
- calendarios activos: 2;
- calendarios completados: 1.

### Usuario normal

Dashboard usuario observado:

- cultivos propios: 2;
- catálogo público: 5;
- tareas pendientes: 2;
- tareas completadas: 2;
- calendarios activos: 1;
- calendarios completados: 1.

El dashboard de usuario también muestra:

- próximas tareas;
- eventos de calendario activos;
- resumen de riego;
- requisitos ambientales.

---

## Fortalezas DeepSeek

- Mayor cobertura de tests: 117 tests tras corrección.
- 13 tests específicos de seed.
- Verifica que las contraseñas están hasheadas.
- Verifica login correcto de admin y user tras seed.
- Verifica contraseña incorrecta.
- Verifica catálogo público tras seed.
- Seed completo con cultivos, tareas, calendarios, riego, ambiente y guías.
- Dashboard visual más rico con tareas, riego y ambiente visibles.

---

## Limitaciones DeepSeek

| Limitación | Impacto | Estado |
|---|---|---|
| Incidencia inicial de contaminación de `get_db` | Rompía 98 tests al ejecutar juntos | Corregida |
| `discover` no queda validado como comando estándar | Se usa ejecución explícita conjunta | Observación metodológica |
| Sin migraciones/Alembic | Pendiente para cierre técnico futuro | Pendiente |
| Sin tests E2E | No valida flujos reales de navegador automáticamente | Pendiente |
| UI no modificada en FASE 10 | Depende de UI previa | Aceptable |

---

## Puntuación final DeepSeek FASE 10

```text
95/100
```

### Justificación

DeepSeek obtiene la puntuación más alta por cobertura, amplitud del seed y riqueza de validación. Se penaliza ligeramente por la incidencia inicial grave de aislamiento de tests y por no dejar validado el comando estándar `discover`, aunque la ejecución conjunta explícita de los 117 tests pasa correctamente.

---

# Claude Code — FASE 10

## Estado

**Validado y cerrado tras ajuste.**

Claude Code implementó el seed demo de FASE 10. La primera versión era funcional, pero no quedaba completamente alineada con los criterios usados en Codex y DeepSeek. Tras solicitar una corrección, Claude añadió tests específicos de seed, ajustó los datos demo y dejó la fase validada con 106 tests totales.

---

## Archivos creados

- `tests/test_seed_demo.py`
- `SEED_DEMO.md`
- `ENTREGA_FASE10.md`
- `FASE10_CIERRE_DEFINITIVO.md`

## Archivos modificados

- `scripts/seed_demo.py`
- `README.md`

---

## Comando de seed

```bash
cd C:\Users\danie\Desktop\tfg\tfg-claude
python scripts\seed_demo.py
```

---

## Credenciales demo

| Rol | Email | Contraseña |
|---|---|---|
| Admin | `admin@test.com` | `admin123` |
| Usuario normal | `user@test.com` | `user123` |

---

## Datos demo finales

| Tipo | Cantidad | Detalles |
|---|---:|---|
| Usuarios | 2 | admin y user |
| Cultivos públicos | 5 | Tomate, Lechuga, Zanahoria, Pimiento, Fresa |
| Cultivos personales | 2 | Mi Tomate, Mi Lechuga |
| Cultivos totales | 7 | 5 públicos + 2 personales |
| Calendarios | 3 | calendarios demo |
| Tareas | 4 | combinación de pendientes y completadas |
| Riego | según modelos existentes | datos asociados a cultivos |
| Requisitos ambientales | según modelos existentes | datos asociados a cultivos |

---

## Ajuste solicitado

La primera versión de FASE 10 funcionaba, pero presentaba tres diferencias respecto a los criterios comparativos:

1. No incluía tests específicos de seed.
2. Solo creaba un cultivo personal.
3. Usaba `Pepino` en lugar de `Pimiento`.

Tras la corrección:

- se añadió `tests/test_seed_demo.py`;
- se añadieron 17 tests específicos;
- se ajustaron los 5 cultivos públicos;
- se añadieron 2 cultivos personales;
- se validó la idempotencia del seed.

---

## Tests añadidos

Claude añadió 17 tests específicos de seed que validan:

- creación de admin;
- creación de usuario normal;
- contraseñas hasheadas;
- login admin;
- login user;
- creación de 5 cultivos públicos;
- creación de 2 cultivos personales;
- creación de calendarios;
- tareas pendientes y completadas;
- idempotencia;
- ausencia de duplicados al ejecutar el seed varias veces.

---

## Tests backend

Comando ejecutado:

```bash
cd C:\Users\danie\Desktop\tfg\tfg-claude
python -m unittest discover -s tests -p "test*.py"
```

Resultado:

```text
Ran 106 tests in 60.570s

OK
```

---

## Build frontend

Comando ejecutado:

```bash
cd C:\Users\danie\Desktop\tfg\tfg-claude\frontend
npm run build
```

Resultado:

```text
vite v5.4.21 building for production...
✓ 58 modules transformed.
✓ built in 569ms
```

---

## Validación visual

### Usuario normal

- Login con `user@test.com / user123`.
- Dashboard con datos.
- Mis cultivos con `Mi Tomate` y `Mi Lechuga`.
- Catálogo con 5 cultivos públicos.
- Calendario con eventos o calendarios demo.
- Tareas con estados pendientes y completadas.
- No aparece enlace Admin.

### Admin

- Login con `admin@test.com / admin123`.
- Enlace Admin visible.
- `/admin/dashboard` muestra datos globales.
- `/admin/users` muestra usuarios.
- `/admin/crops` muestra cultivos.
- `/admin/tasks` muestra tareas.

---

## Fortalezas Claude FASE 10

- 17 tests específicos de seed.
- Seed demo ajustado a los criterios comparativos.
- 106 tests totales OK.
- Build frontend correcto.
- Documentación específica de entrega y cierre.
- Idempotencia validada.
- Corrige las diferencias detectadas en la primera versión.

---

## Limitaciones Claude FASE 10

| Limitación | Impacto | Estado |
|---|---|---|
| Primera versión no estaba alineada con criterios comunes | Comparación incompleta | Corregida |
| No implementa migraciones/Alembic | Igual que el resto de herramientas | Pendiente |
| No implementa E2E | Validación visual manual | Pendiente |
| Documentación adicional extensa | Puede generar ruido si no se organiza | Aceptable |

---

## Puntuación final Claude FASE 10

```text
94/100
```

### Justificación

Claude alcanza una solución final sólida, con tests específicos, seed idempotente y build correcto. Se penaliza ligeramente porque la primera versión requirió una corrección para alinearse con los criterios de comparación.

---

# Comparación final FASE 10

## Mejor integración con comando estándar

**Codex / Claude Code**

Motivo:

- Ambos validan la suite final con `unittest discover`.
- DeepSeek queda validado mediante ejecución conjunta explícita.

## Mayor cobertura de tests

**DeepSeek**

Motivo:

- 117 tests en ejecución conjunta explícita.
- Claude queda cerca con 106 tests.
- Codex mantiene 52 tests.

## Mejor build

**Codex**

Motivo:

- 90ms frente a 569ms de Claude y 582ms de DeepSeek.

## Mejor seed funcional

**Empate DeepSeek / Claude Code / Codex**

Motivo:

- Las tres implementaciones crean admin, usuario normal, cultivos, tareas y datos demo.
- DeepSeek destaca por cobertura.
- Claude destaca por tests específicos tras corrección.
- Codex destaca por integración y estabilidad.

## Mejor resultado final

**DeepSeek por margen pequeño**

Motivo:

- Mayor cobertura y validación más profunda.
- La incidencia inicial fue grave, pero quedó corregida.
- Codex y Claude quedan muy cerca por estabilidad e integración.

---

# Resultado final

| Posición | IA | Puntuación | Motivo |
|---:|---|---:|---|
| 1 | DeepSeek | 95/100 | Mayor cobertura y seed más validado |
| 2 | Codex | 94/100 | Muy estable, rápido e integrado |
| 2 | Claude Code | 94/100 | Seed completo tras ajuste y 106 tests OK |

---

# Estado acumulado tras FASE 10

| IA | Piloto 0-3 | FASE 4 | FASE 5 | FASE 6 | FASE 7 | FASE 8 | FASE 9 | FASE 10 | Estado acumulado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | 91 | 92 | 91 | 92 | 94 | Funcional y completo tras correcciones |
| Codex | 77 | 86 | 90 | 90 | 91 | 90 | 91 | 94 | Funcional, estable y bien integrado |
| DeepSeek | 87 | 94 | 96 | 96 | 97 | 92 | 93 | 95 | Mejor resultado acumulado provisional |

---

# Incidencias transversales FASE 10

## 1. Necesidad de seed demo

FASE 10 confirma que la aplicación necesitaba datos iniciales para ser demostrable.

Hasta FASE 9, había que manipular SQLite manualmente para crear admins o datos.

## 2. Aislamiento de tests

DeepSeek sufrió una incidencia importante de contaminación de `app.dependency_overrides[get_db]`, que rompió la suite conjunta con 98 errores.

Esta incidencia es relevante para el TFG porque muestra una diferencia real entre generar código que funciona de forma aislada y generar código que mantiene una suite completa ejecutable.

## 3. Alineación de criterios de seed

Claude mostró una incidencia metodológica distinta: la primera versión era funcional, pero no cumplía exactamente los criterios comunes de comparación. Esto obligó a solicitar una corrección para añadir tests específicos, dos cultivos personales y los cultivos públicos esperados.

## 4. Falta de migraciones

Ninguna herramienta implementa Alembic o migraciones reales.

Esto no era requisito de FASE 10, pero queda como limitación técnica para un despliegue más profesional.

## 5. Falta de tests E2E

No hay tests automáticos de navegador.

La validación visual se ha realizado manualmente.

---

# Conclusión FASE 10

FASE 10 cierra la parte funcional principal del caso práctico en las tres implementaciones.

Los tres proyectos ya cuentan con:

- backend funcional;
- frontend usuario;
- panel admin;
- seed demo;
- credenciales de prueba;
- datos de catálogo;
- datos personales;
- tareas;
- calendarios;
- riego;
- ambiente;
- tests backend;
- build frontend.

La diferencia principal entre herramientas es:

- **Codex** entrega una solución más compacta, rápida e integrada con el comando estándar.
- **DeepSeek** entrega una solución más amplia y mejor cubierta por tests, pero necesitó una corrección importante de aislamiento.
- **Claude Code** entrega una solución sólida tras ajuste, con buena documentación y 106 tests totales OK.
