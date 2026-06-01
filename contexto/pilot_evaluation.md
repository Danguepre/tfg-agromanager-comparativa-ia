# Evaluación piloto — Reconstrucción AgroManager

## Objetivo

Evaluar una reconstrucción piloto de AgroManager usando distintas herramientas de IA.

Esta primera prueba solo cubre:

1. FASE 0 — Plan de trabajo.
2. FASE 1 — Arquitectura base.
3. FASE 2 — Modelos y schemas.
4. FASE 3 — Autenticación, usuarios y permisos básicos.

No se evalúan todavía:

- CRUD completo de cultivos.
- Calendario agrícola funcional.
- Riego, ambiente y tareas completos.
- Dashboard.
- Panel admin completo.
- Frontend funcional completo.
- Seed completo.
- Tests E2E finales.

---

## Herramientas evaluadas

| Herramienta | Modelo usado | Carpeta de trabajo | Estado |
|---|---|---|---|
| Claude Code | Claude 4.5 | `tfg-claude/` | Backend, tests piloto y frontend mínimo validados |
| Codex | OpenAI / Codex | `tfg-codex/` | Tests piloto y frontend mínimo validados |
| DeepSeek | DeepSeek mediante Cline/VS Code | `tfg-deepseek/` | Backend, tests piloto, frontend y documentación corregida validados |
| GitHub Copilot | GPT-4.1 | `tfg-copilot-test/` | Pendiente |

---

## Criterios de aceptación del piloto

La reconstrucción piloto se considera válida si cumple:

- El backend arranca con `uvicorn`.
- `GET /` devuelve un JSON de salud.
- La estructura del proyecto es modular.
- Las tablas principales se crean correctamente.
- Existen modelos y schemas para:
  - User;
  - Crop;
  - PlantingCalendar;
  - IrrigationAttributes;
  - EnvironmentalRequirements;
  - CultivationGuide;
  - Task;
  - TaskCrop.
- Se puede registrar un usuario.
- Se puede hacer login.
- El login devuelve `access_token`.
- Una ruta protegida falla sin token.
- Un usuario normal no puede ver datos de otros usuarios.
- Un admin puede ver todos los usuarios.
- No se expone password en respuestas.
- Se respetan las restricciones principales del contexto maestro:
  - PostgreSQL por defecto en desarrollo.
  - SQLite para tests.
  - `unittest` + `fastapi.testclient.TestClient`.
  - Fetch API en frontend.
  - No secretos reales.
  - No modificar el proyecto original.

---

## Tabla de evaluación resumen

| IA | Iteraciones | Backend arranca /20 | Estructura /20 | Modelos /20 | Auth y permisos /20 | Claridad /20 | Total /100 | Errores encontrados | Prompts extra usados |
|----|-------------|---------------------|----------------|-------------|---------------------|--------------|------------|---------------------|---------------------|
| Claude Code | 7 | 15/20 provisional | Pendiente | Pendiente | 15/20 provisional | Pendiente | Pendiente | Backend arranca tras 3 correcciones. Tests piloto pasan tras corregir configuración de SQLite en tests. Frontend arranca tras corregir import relativo incorrecto en `src/App.jsx`. Desviaciones pendientes: usa `sqlite:///./app.db` en desarrollo y los tests usan `POST /auth/register` en vez de `POST /users/`. | 6 prompts de corrección. |
| Codex | 3 | Pendiente de validación manual con `uvicorn` | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Tests no ejecutaban inicialmente porque usaban `pytest`. Tras corregirlo, apareció falta de dependencia `pydantic_settings`. Después de la segunda corrección, los tests funcionan correctamente y el frontend arranca sin errores. | 2 prompts de corrección. |
| DeepSeek | 3 | 18/20 provisional | Pendiente | Pendiente | 17/20 provisional | Pendiente | Pendiente | Inicialmente `unittest` no detectaba tests: `Ran 0 tests`. Tras corrección, ejecuta 17 tests correctamente. El riesgo de crear admin desde registro público queda cubierto por `test_register_cannot_become_admin`. Backend arranca, frontend compila correctamente y README fue corregido para no documentar creación insegura de admin. | 2 prompts de corrección. |
| Copilot GPT-4.1 | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |

---

## Registro de iteraciones

### Claude Code

| Iteración | Tipo | Descripción | Resultado |
|---|---|---|---|
| 1 | Generación inicial | Se pidió implementar FASE 0, FASE 1, FASE 2 y FASE 3 dentro de `tfg-claude/`. | Claude generó estructura, backend, frontend mínimo, modelos, schemas, auth, usuarios, tests y documentación. |
| 2 | Corrección 1 | Se pidió corregir el fallo de arranque en `app/config.py`: `TypeError: 'classmethod' object is not callable`. | El error de `config.py` dejó de aparecer, pero surgió un nuevo error crítico en `app/models/base.py`. |
| 3 | Corrección 2 | Se pidió corregir el uso incorrecto de `DateTime` en `app/models/base.py` y revisar modelos relacionados. | El error de `DateTime` dejó de aparecer, pero surgió un nuevo error crítico en `app/dependencies.py`. |
| 4 | Corrección 3 | Se pidió corregir el import incorrecto `HTTPAuthCredentials` en `app/dependencies.py`. | El backend arrancó correctamente con `uvicorn app.main:app --reload`. |
| 5 | Corrección 4 | Se pidió corregir problemas de mappers/importación de modelos SQLAlchemy. | Se avanzó hasta ejecutar tests, pero aparecieron errores de base de datos de test sin tablas. |
| 6 | Corrección 5 | Se pidió corregir la configuración de SQLite en tests porque fallaban con `no such table: users`. | Los tests piloto pasan correctamente: `Ran 12 tests in 3.285s`, todos `ok`. |
| 7 | Corrección 6 | Se pidió corregir un import relativo incorrecto en el frontend: `../api/api` desde `src/App.jsx`. | El frontend arranca correctamente con `npm run dev`. |

### Codex

| Iteración | Tipo | Descripción | Resultado |
|---|---|---|---|
| 1 | Generación inicial | Se pidió implementar el mismo piloto que a Claude dentro de `tfg-codex/`. | Codex generó el proyecto, pero los tests no ejecutaban porque dependían de `pytest`. |
| 2 | Corrección 1 | Se pidió convertir los tests de `pytest` a `unittest` y `fastapi.testclient.TestClient`, sin instalar pytest. | El error de `pytest` desapareció, pero apareció un nuevo error: faltaba `pydantic_settings`. |
| 3 | Corrección 2 | Se pidió corregir la dependencia/configuración de `pydantic-settings`. | Los tests funcionan correctamente y el frontend arranca sin errores. |

### DeepSeek

| Iteración | Tipo | Descripción | Resultado |
|---|---|---|---|
| 1 | Generación inicial | Se pidió implementar el mismo piloto dentro de `tfg-deepseek/`. | DeepSeek indicó que el proyecto estaba completo y que las pruebas funcionales pasaban, pero el comando estándar de `unittest` ejecutó 0 tests. |
| 2 | Corrección 1 | Se pidió crear tests reales con `unittest` y `fastapi.testclient.TestClient`, además de validar que un usuario no pueda registrarse como admin enviando `role: admin`. | DeepSeek añadió tests detectables por `unittest`. Resultado: `Ran 17 tests in 7.715s`, `OK`. Backend y frontend quedan validados posteriormente. |
| 3 | Corrección 2 | Se pidió corregir solo el README porque seguía documentando creación insegura de admin con `role: admin`. | El README ahora aclara que `POST /users/` crea siempre usuarios `user` y que no existe todavía un mecanismo seguro para crear el primer admin. |

### GitHub Copilot GPT-4.1

Pendiente.

---

## Incidencias Claude Code

### Incidencia 1 — Backend no arranca por error en configuración

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-claude/
```

**Comando ejecutado:**

```bash
uvicorn app.main:app --reload
```

**Resultado:**

Uvicorn inicia el proceso de recarga, pero falla al importar `app.main`.

**Error principal:**

```text
TypeError: 'classmethod' object is not callable
```

**Archivo señalado por la traza:**

```text
app/config.py
```

**Línea aproximada señalada por la traza:**

```python
DATABASE_URL: str = get_database_url()
```

**Diagnóstico:**

Claude generó una clase `Settings` donde intenta llamar a `get_database_url()` durante la definición de la propia clase, pero ese método está definido como `@classmethod`.

En Python, un `classmethod` no puede llamarse así dentro del cuerpo de la clase mientras la clase todavía se está construyendo.

**Impacto:**

Fallo crítico de arranque del backend.

**Severidad:**

Alta.

**Acción tomada:**

Se envió un prompt de corrección limitado a este problema.

**Estado:**

Corregida aparentemente. El error ya no aparece en los siguientes arranques.

---

### Incidencia 2 — Backend no arranca por error en campos DateTime

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-claude/
```

**Comando ejecutado:**

```bash
uvicorn app.main:app --reload
```

**Resultado:**

El backend sigue sin arrancar. El error anterior de `config.py` ya no aparece, pero falla al importar los modelos SQLAlchemy.

**Error principal:**

```text
TypeError: DateTime.__init__() got an unexpected keyword argument 'default'
```

**Archivo señalado por la traza:**

```text
app/models/base.py
```

**Línea aproximada señalada por la traza:**

```python
created_at = DateTime(timezone=True, default=func.now(), nullable=False)
```

**Diagnóstico:**

Claude generó campos de timestamp usando `DateTime(...)` como si fuera una columna completa de SQLAlchemy.

Los parámetros `default`, `nullable` y `onupdate` deben definirse en `Column(...)` o `mapped_column(...)`, no directamente en el tipo `DateTime(...)`.

**Impacto:**

Fallo crítico de arranque del backend. La aplicación no podía importar los modelos.

**Severidad:**

Alta.

**Acción tomada:**

Se envió un segundo prompt de corrección a Claude, limitado a arreglar la definición de timestamps y revisar modelos relacionados.

**Estado:**

Corregida aparentemente. El error ya no aparece en los siguientes arranques.

---

### Incidencia 3 — Backend no arranca por import incorrecto de FastAPI

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-claude/
```

**Comando ejecutado:**

```bash
uvicorn app.main:app --reload
```

**Resultado:**

El backend sigue sin arrancar. El error anterior de SQLAlchemy/DateTime ya no aparece, pero falla al importar las dependencias de autenticación.

**Error principal:**

```text
ImportError: cannot import name 'HTTPAuthCredentials' from 'fastapi.security'
```

**Archivo señalado por la traza:**

```text
app/dependencies.py
```

**Línea aproximada señalada por la traza:**

```python
from fastapi.security import HTTPBearer, HTTPAuthCredentials
```

**Diagnóstico:**

Claude usó un nombre de clase incorrecto en FastAPI.

El tipo `HTTPAuthCredentials` no existe en `fastapi.security`. El nombre correcto suele ser `HTTPAuthorizationCredentials`.

**Impacto:**

Fallo crítico de arranque del backend. La aplicación no podía cargar las dependencias de autenticación.

**Severidad:**

Alta.

**Acción tomada:**

Se envió un tercer prompt de corrección a Claude, limitado a corregir el import y revisar usos relacionados.

**Estado:**

Corregida. El backend arranca correctamente después de esta corrección.

---

### Incidencia 4 — Tests fallan por mappers incompletos de SQLAlchemy

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-claude/
```

**Comando ejecutado:**

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado inicial:**

Los tests se ejecutaban, pero fallaban mayoritariamente.

```text
Ran 12 tests
FAILED (errors=10)
```

**Error principal:**

```text
sqlalchemy.exc.InvalidRequestError:
One or more mappers failed to initialize.
Triggering mapper: 'Mapper[User(users)]'.
Original exception was:
When initializing mapper Mapper[User(users)], expression 'Crop' failed to locate a name ('Crop').
```

**Diagnóstico:**

SQLAlchemy no podía resolver la relación entre `User` y `Crop`. Probablemente no se estaban importando todos los modelos antes de crear tablas o ejecutar queries. Esto impedía que SQLAlchemy configurase correctamente los mappers.

**Impacto:**

Aunque el backend arrancaba, la lógica de base de datos fallaba al usar endpoints que consultaban usuarios. Registro, login y tests funcionales quedaban bloqueados.

**Severidad:**

Alta.

**Acción tomada:**

Se envió un cuarto prompt de corrección a Claude, limitado a registrar correctamente todos los modelos y corregir la configuración de SQLAlchemy/tests.

**Estado:**

Corregida parcialmente o superada. El error de mapper dejó de aparecer, pero después apareció otro problema en la base de datos de test: `no such table: users`.

---

### Incidencia 5 — Tests fallan porque no existen tablas en SQLite

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-claude/
```

**Comando ejecutado inicialmente:**

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado inicial:**

Los tests fallaban al llamar a endpoints que consultaban la base de datos.

**Error principal:**

```text
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
```

**Ruta implicada:**

```text
POST /auth/register
```

**Línea relevante:**

```python
db.query(User).filter(User.email == email).first()
```

**Diagnóstico:**

La base de datos usada por los tests no tenía las tablas creadas. Probablemente la app y los tests no compartían correctamente el mismo engine/sesión de SQLite, o faltaba crear tablas antes de cada test.

También era posible que SQLite en memoria estuviese usando conexiones separadas sin `StaticPool`.

**Impacto:**

Los tests de registro, login y permisos quedaban bloqueados.

**Severidad:**

Alta.

**Acción tomada:**

Se envió un prompt de corrección para configurar correctamente SQLite en tests, crear tablas antes de las pruebas y asegurar que `TestClient` usa la misma base de datos de test.

**Resultado tras corrección:**

```text
Ran 12 tests in 3.285s

OK
```

**Estado:**

Corregida.

---

### Incidencia 6 — Frontend no arranca por import relativo incorrecto

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-claude/frontend/
```

**Comando ejecutado:**

```bash
npm run dev
```

**Resultado inicial:**

Vite arrancaba, pero mostraba un error interno al resolver imports.

**Error principal:**

```text
Failed to resolve import "../api/api" from "src/App.jsx". Does the file exist?
```

**Archivo señalado:**

```text
frontend/src/App.jsx
```

**Línea aproximada:**

```js
import { healthCheck } from "../api/api";
```

**Diagnóstico:**

El import relativo estaba mal construido. `App.jsx` está dentro de `frontend/src/`, y si el cliente API está en `frontend/src/api/api.js`, la ruta correcta debía ser:

```js
import { healthCheck } from "./api/api";
```

**Impacto:**

El frontend no podía compilar ni mostrarse correctamente en Vite.

**Severidad:**

Media-alta.

**Acción tomada:**

Se envió un prompt de corrección a Claude para arreglar el import y revisar rutas relativas del frontend.

**Resultado tras corrección:**

El frontend arranca correctamente con:

```bash
npm run dev
```

**Estado:**

Corregida.

---

## Incidencias Codex

### Incidencia 1 — Tests dependen de pytest aunque se pidió unittest

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-codex/
```

**Comando ejecutado:**

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado:**

Los tests no llegan a ejecutarse porque falla la importación del módulo de test.

**Error principal:**

```text
ModuleNotFoundError: No module named 'pytest'
```

**Archivo señalado:**

```text
tests/test_auth_users.py
```

**Línea relevante:**

```python
import pytest
```

**Diagnóstico:**

Codex generó tests con dependencia de `pytest`, aunque el prompt pedía explícitamente `unittest` y `fastapi.testclient.TestClient`.

**Impacto:**

La batería de tests no era reproducible con el comando acordado para el experimento.

**Severidad:**

Media-alta.

**Acción tomada:**

Se envió un prompt de corrección a Codex para convertir los tests a `unittest` sin añadir `pytest`.

**Estado:**

Corregida. El error de `pytest` ya no aparece.

---

### Incidencia 2 — Falta dependencia `pydantic-settings`

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-codex/
```

**Comando ejecutado:**

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado:**

Los tests seguían sin ejecutarse. El error anterior de `pytest` ya no aparecía, pero fallaba la importación de configuración.

**Error principal:**

```text
ModuleNotFoundError: No module named 'pydantic_settings'
```

**Archivo señalado:**

```text
app/core/config.py
```

**Línea relevante:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
```

**Diagnóstico:**

Codex generó una configuración basada en `pydantic-settings`, pero la dependencia no estaba instalada o no estaba declarada correctamente en `requirements.txt`.

**Impacto:**

La app no podía importar la configuración y los tests quedaban bloqueados antes de ejecutarse.

**Severidad:**

Media-alta.

**Acción tomada:**

Se envió un prompt de corrección a Codex para declarar correctamente la dependencia o adaptar la configuración.

**Estado:**

Corregida. Tras la corrección, los tests funcionan correctamente.

---

## Incidencias DeepSeek

### Incidencia 1 — No hay tests detectables por unittest

**Fecha:** 2026-05-13 / 2026-05-18

**Carpeta evaluada:**

```text
tfg-deepseek/
```

**Comando ejecutado inicialmente:**

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado inicial:**

```text
Ran 0 tests in 0.000s

NO TESTS RAN
```

**Diagnóstico:**

La reconstrucción de DeepSeek no contenía tests detectables por `unittest` en la carpeta `tests/`, o los tests no estaban nombrados/estructurados de forma compatible con el comando acordado.

**Impacto:**

No se podía validar automáticamente registro, login, permisos, rutas protegidas ni ausencia de exposición de password mediante la batería de tests exigida en el piloto.

**Severidad:**

Alta.

**Observación:**

DeepSeek afirmó que las pruebas funcionales pasaban, pero el comando estándar del experimento no ejecutaba ningún test.

**Acción tomada:**

Se envió un prompt de corrección para crear tests reales con `unittest` y `fastapi.testclient.TestClient`.

**Resultado tras corrección:**

```text
Ran 17 tests in 7.715s

OK
```

**Estado:**

Corregida.

---

### Incidencia 2 — Posible fallo grave: registro permite crear usuarios admin

**Fecha:** 2026-05-13 / 2026-05-18

**Carpeta evaluada:**

```text
tfg-deepseek/
```

**Descripción inicial:**

DeepSeek indicó que para crear un usuario administrador se debía llamar a `POST /users/` enviando `"role": "admin"`.

Ejemplo indicado por DeepSeek:

```json
{
  "email": "admin@agro.com",
  "username": "admin",
  "password": "admin123",
  "role": "admin"
}
```

**Diagnóstico inicial:**

Si el endpoint público `POST /users/` permite elegir `role: admin`, cualquier usuario podría registrarse como administrador.

**Impacto potencial:**

Posible fallo grave de seguridad en el control de roles y permisos.

**Severidad inicial:**

Alta.

**Criterio esperado:**

El registro público debe crear siempre usuarios normales con rol `user`.

La creación de administradores debería hacerse mediante:

- seed controlado;
- script interno;
- usuario inicial configurado de forma segura;
- endpoint protegido accesible solo por admin.

**Validación realizada:**

La batería de tests incluye:

```text
test_register_cannot_become_admin
```

Además, en validación manual, el usuario con username `admin` aparece con:

```json
{
  "username": "admin",
  "role": "user"
}
```

**Estado:**

Corregida aparentemente. El registro público no crea admins.

---

### Incidencia 3 — README documentaba creación insegura de admin

**Fecha:** 2026-05-18

**Carpeta evaluada:**

```text
tfg-deepseek/
```

**Archivo revisado:**

```text
README.md
```

**Estado anterior:**

El README indicaba crear un administrador llamando a `POST /users/` con `"role":"admin"`.

**Problema:**

Aunque la validación posterior mostraba que el backend no parecía crear admins desde el registro público, la documentación seguía recomendando un flujo inseguro o incorrecto.

**Impacto:**

Podía confundir a futuros usuarios o evaluadores. Además contradecía el criterio de seguridad del piloto: el registro público no debe permitir autoproclamarse admin.

**Corrección aplicada:**

El README ahora aclara que:

- `POST /users/` crea siempre usuarios con rol `user`;
- no es posible autoproclamarse admin durante el registro;
- no existe todavía un mecanismo seguro para crear el primer administrador;
- esa falta queda documentada como limitación pendiente;
- se eliminó la recomendación de crear admins enviando `role: admin`.

**Estado:**

Corregida.

---

## Validación de arranque backend — Claude Code

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-claude/
```

**Comando ejecutado:**

```bash
uvicorn app.main:app --reload
```

**Resultado:**

El backend arranca correctamente.

**Evidencia del log:**

```text
INFO:app.main:AgroManager API initialized successfully
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:app.main:Starting AgroManager API in development environment
INFO:app.main:Database: sqlite:///./app.db
INFO:app.main:Database tables initialized
INFO:     Application startup complete.
```

**Conclusión:**

El criterio “backend arranca con uvicorn” queda validado, pero solo después de 3 prompts de corrección.

**Observación importante:**

El log muestra:

```text
Database: sqlite:///./app.db
```

Esto es una desviación respecto al contexto maestro, que pedía PostgreSQL por defecto en desarrollo y SQLite para tests.

---

## Validación de tests piloto — Claude Code

**Fecha:** 2026-05-13

**Comando ejecutado:**

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado:**

```text
Ran 12 tests in 3.285s

OK
```

**Tests ejecutados correctamente:**

- `test_login_invalid_email`
- `test_login_invalid_password`
- `test_login_success`
- `test_register_duplicate_email`
- `test_register_short_password`
- `test_register_success`
- `test_health_check_health_endpoint`
- `test_health_check_root`
- `test_delete_own_user`
- `test_get_other_user_forbidden`
- `test_get_own_user`
- `test_get_own_user_with_token`

**Cobertura funcional observada:**

- Login con email inválido.
- Login con contraseña inválida.
- Login correcto.
- Registro correcto.
- Registro con email duplicado.
- Registro con contraseña corta.
- Health check en `/`.
- Health check en `/health`.
- Obtener usuario propio con token.
- Bloqueo al obtener otro usuario.
- Bloqueo de ruta protegida sin token.
- Eliminación del propio usuario.

**Conclusión:**

La batería piloto de backend pasa correctamente después de las correcciones.

**Observación importante:**

Los tests usan `POST /auth/register`, pero el contexto maestro pedía `POST /users/` para registrar usuarios. Esto queda como desviación pendiente de revisar en `/docs`.

---

## Validación de frontend piloto — Claude Code

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-claude/frontend/
```

**Comando ejecutado:**

```bash
npm run dev
```

**Resultado inicial:**

Vite arrancaba, pero fallaba por un import relativo incorrecto:

```text
Failed to resolve import "../api/api" from "src/App.jsx"
```

**Resultado tras corrección:**

El frontend arranca correctamente.

**Conclusión:**

El frontend mínimo queda validado para la fase piloto.

**Pendiente:**

Ejecutar también:

```bash
npm run build
```

para confirmar que el frontend compila en modo producción.

---

## Validación de tests piloto — Codex

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-codex/
```

**Comando ejecutado:**

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado inicial:**

Los tests fallaban por dependencia de `pytest`.

```text
ModuleNotFoundError: No module named 'pytest'
```

**Resultado intermedio:**

Tras corregir el uso de `pytest`, los tests seguían fallando por falta de `pydantic_settings`.

```text
ModuleNotFoundError: No module named 'pydantic_settings'
```

**Resultado final tras corrección:**

Los tests funcionan correctamente.

**Conclusión:**

La batería piloto de tests de Codex queda validada tras 2 correcciones.

**Pendiente:**

Registrar el número exacto de tests ejecutados y el tiempo total si se quiere comparar con más precisión.

---

## Validación de frontend piloto — Codex

**Fecha:** 2026-05-13

**Carpeta evaluada:**

```text
tfg-codex/frontend/
```

**Comando ejecutado:**

```bash
npm run dev
```

**Resultado:**

El frontend arranca y no muestra errores.

**Conclusión:**

El frontend mínimo de Codex queda validado en modo desarrollo.

**Pendiente:**

Ejecutar también:

```bash
npm run build
```

para confirmar que el frontend compila en modo producción.

---

## Validación de backend manual — DeepSeek

**Fecha:** 2026-05-18

**Carpeta evaluada:**

```text
tfg-deepseek/
```

**Comando ejecutado:**

```bash
uvicorn app.main:app --reload
```

**Resultado:**

El backend arranca correctamente.

**Conclusión:**

El backend de DeepSeek queda validado manualmente para la fase piloto.

**Estado:**

Validado.

---

## Validación de tests piloto — DeepSeek

**Fecha:** 2026-05-18

**Carpeta evaluada:**

```text
tfg-deepseek/
```

**Comando ejecutado:**

```bash
python -m unittest discover -s tfg-deepseek\tests -p "test*.py" -v
```

**Resultado inicial antes de la corrección:**

```text
Ran 0 tests in 0.000s

NO TESTS RAN
```

**Resultado tras corrección:**

```text
Ran 17 tests in 7.715s

OK
```

**Tests ejecutados correctamente:**

- `test_admin_can_see_all_users`
- `test_delete_user_by_admin`
- `test_delete_user_forbidden_for_normal_user`
- `test_get_nonexistent_user`
- `test_get_user_by_id`
- `test_health_check`
- `test_login_nonexistent_user`
- `test_login_success`
- `test_login_wrong_password`
- `test_protected_route_with_invalid_token`
- `test_protected_route_without_token`
- `test_register_cannot_become_admin`
- `test_register_duplicate_email`
- `test_register_duplicate_username`
- `test_register_user`
- `test_user_cannot_access_other_user_by_id`
- `test_user_cannot_see_other_users`

**Cobertura funcional observada:**

- Health check.
- Registro de usuario normal.
- Bloqueo de email duplicado.
- Bloqueo de username duplicado.
- Login correcto.
- Login con usuario inexistente.
- Login con contraseña incorrecta.
- Ruta protegida sin token.
- Ruta protegida con token inválido.
- Usuario normal solo ve su propio perfil.
- Usuario normal no accede a otros usuarios por ID.
- Admin puede ver todos los usuarios.
- Admin puede eliminar usuarios.
- Usuario normal no puede eliminar a otro usuario.
- Usuario no puede registrarse como admin enviando `role: admin`.
- No se expone password en las respuestas comprobadas por los tests.

**Conclusión:**

La batería piloto de DeepSeek queda validada tras una corrección. Destaca positivamente que cubre explícitamente el caso de seguridad `test_register_cannot_become_admin`.

**Estado:**

Validado.

---

## Validación de seguridad de rol — DeepSeek

**Fecha:** 2026-05-18

**Prueba realizada:**

Se inició sesión con el usuario `admin` y se llamó a:

```text
GET /users/
```

**Resultado:**

La API respondió `200 OK` y devolvió el usuario con:

```json
{
  "username": "admin",
  "role": "user"
}
```

**Conclusión:**

Aunque el usuario se llama `admin`, su rol real es `user`. La prueba indica que el registro público no está creando un administrador automáticamente.

**Estado:**

Riesgo de autoproclamarse admin mitigado aparentemente. Además existe test automático específico: `test_register_cannot_become_admin`.

---

## Validación de configuración — DeepSeek

**Fecha:** 2026-05-18

### `.env`

Contenido revisado:

```env
DATABASE_URL=sqlite:///./agromanager.db 
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173
GOOGLE_CLIENT_ID=
```

**Conclusión:**

No se observan secretos reales. `SECRET_KEY` es un placeholder.

**Desviación:**

La base de datos por defecto usa SQLite:

```text
sqlite:///./agromanager.db
```

El contexto maestro pedía PostgreSQL por defecto en desarrollo y SQLite para tests.

### `.gitignore`

Se confirma que ignora:

```text
.env
*.db
node_modules/
dist/
```

**Conclusión:**

Correcto. Evita subir secretos, bases locales y archivos generados.

### Frontend

Archivo revisado:

```text
frontend/src/App.jsx
```

El frontend es una pantalla mínima estática que enlaza a `/docs`.

**Conclusión:**

El frontend mínimo compila y funciona, pero no se observa consumo de API con Fetch en `App.jsx`. Tampoco se observa uso de Axios.

**Estado:**

Validado parcialmente.

---

## Validación de README — DeepSeek

**Fecha:** 2026-05-18

**Archivo revisado:**

```text
tfg-deepseek/README.md
```

**Estado anterior:**

El README recomendaba crear un administrador mediante `POST /users/` enviando `"role":"admin"`.

**Estado tras corrección:**

El README ahora incluye una sección “Nota sobre roles de usuario” e indica que:

- el registro público `POST /users/` crea siempre usuarios con rol `user`;
- no es posible autoproclamarse administrador durante el registro;
- actualmente no existe un mecanismo seguro para crear el primer administrador;
- la creación del primer administrador queda como limitación pendiente;
- una solución futura podría ser un script de seed protegido o una ruta administrativa restringida.

**Conclusión:**

La documentación insegura fue corregida.

**Estado:**

Validado.

---

## Validación de build frontend — DeepSeek

**Fecha:** 2026-05-18

**Carpeta evaluada:**

```text
tfg-deepseek/frontend/
```

**Comando ejecutado:**

```bash
npm run build
```

**Resultado:**

```text
vite v5.4.21 building for production...
✓ 30 modules transformed.
dist/index.html                  0.33 kB │ gzip:  0.25 kB
dist/assets/index-D8BmuV2y.js  143.02 kB │ gzip: 45.98 kB
✓ built in 368ms
```

**Conclusión:**

El frontend de DeepSeek compila correctamente en modo producción.

**Estado:**

Validado.

---

## Desviaciones detectadas hasta ahora

| IA | Desviación | Descripción | Estado |
|---|---|---|---|
| Claude Code | Base de datos por defecto | El backend arranca con `sqlite:///./app.db` en desarrollo, pero el contexto maestro pedía PostgreSQL por defecto y SQLite para tests. | Confirmada por log de arranque. |
| Claude Code | Endpoint de registro | Los tests usan `POST /auth/register`, pero el contexto maestro pedía `POST /users/`. | Confirmada en tests. Pendiente de revisar en `/docs` si también existe `POST /users/`. |
| Claude Code | Archivo `.env` creado | Claude creó `.env`; debe comprobarse que no contiene secretos reales y que está ignorado por Git. | Pendiente de revisar. |
| Claude Code | Tests | Claude usa `unittest` y `TestClient`, pero también creó estructura tipo `conftest.py`, que es más habitual de pytest. | Pendiente de revisar si es necesario o residual. |
| Claude Code | Frontend | El frontend falló inicialmente por import relativo incorrecto. | Corregida. |
| Claude Code | Build frontend | Se validó `npm run dev`, pero falta confirmar `npm run build`. | Pendiente. |
| Claude Code | Admin | Los tests piloto no verifican todavía que un admin pueda listar todos los usuarios. | Pendiente. |
| Codex | Tests | Codex generó tests con `pytest`, aunque se pidió `unittest`. | Corregida tras prompt adicional. |
| Codex | Dependencias | Codex usó `pydantic-settings` sin tenerlo disponible/declarado correctamente. | Corregida tras prompt adicional. |
| Codex | Build frontend | Se validó `npm run dev`, pero falta confirmar `npm run build`. | Pendiente. |
| Codex | Backend manual | Los tests funcionan, pero falta registrar validación manual de `uvicorn app.main:app --reload`, si no se ha ejecutado aún. | Pendiente. |
| DeepSeek | Tests | `unittest` no detectaba ningún test: `Ran 0 tests`. | Corregida. Ahora ejecuta 17 tests correctamente. |
| DeepSeek | Seguridad / roles | DeepSeek indicó inicialmente que `POST /users/` podía crear admin enviando `role: admin`, pero los tests ahora incluyen `test_register_cannot_become_admin` y la validación manual muestra `role: user`. | Corregida aparentemente. |
| DeepSeek | README admin | El README seguía recomendando crear un administrador desde `POST /users/` enviando `"role":"admin"`. | Corregida. Ahora indica que el registro público crea siempre usuarios `user` y que falta un mecanismo seguro para crear el primer admin. |
| DeepSeek | Admin inicial | No existe mecanismo seguro para crear el primer administrador. | Pendiente, documentado correctamente como limitación. |
| DeepSeek | Base de datos por defecto | README y `.env` usan SQLite como base de datos principal (`sqlite:///./agromanager.db`), pero el contexto maestro pedía PostgreSQL por defecto en desarrollo y SQLite para tests. | Confirmada. |
| DeepSeek | `.env` | No contiene secretos reales; `SECRET_KEY` es placeholder. | Validado. |
| DeepSeek | `.gitignore` | Ignora `.env`, bases `.db`, `node_modules/` y `dist/`. | Validado. |
| DeepSeek | Frontend API | El frontend es una pantalla estática mínima y no se observa cliente Fetch API en `App.jsx`. No usa Axios. | Validado parcialmente. |
| DeepSeek | Build frontend | Frontend compilado correctamente con `npm run build`. | Validado. |
| DeepSeek | Backend manual | Backend arrancado correctamente con `uvicorn`. | Validado. |

---

## Comandos de validación usados

### Backend — Claude Code

```bash
cd tfg-claude
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

**Resultado actual:**

El backend arranca correctamente tras 3 correcciones.

Última evidencia:

```text
Application startup complete.
```

### Tests backend — Claude Code

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado actual:**

```text
Ran 12 tests in 3.285s

OK
```

**Estado:**

Validado.

### Frontend — Claude Code

```bash
cd tfg-claude/frontend
npm run dev
```

**Resultado inicial:**

Falló por import relativo incorrecto:

```text
Failed to resolve import "../api/api" from "src/App.jsx"
```

**Resultado tras corrección:**

El frontend arranca correctamente.

**Estado:**

Validado parcialmente.

**Pendiente:**

```bash
npm run build
```

### Tests backend — Codex

```bash
cd tfg-codex
python -m unittest discover -s tests -p "test*.py" -v
```

**Resultado inicial:**

```text
FAILED (errors=1)
```

**Primer error principal:**

```text
ModuleNotFoundError: No module named 'pytest'
```

**Segundo error principal tras primera corrección:**

```text
ModuleNotFoundError: No module named 'pydantic_settings'
```

**Resultado tras segunda corrección:**

Los tests funcionan correctamente.

**Estado:**

Validado.

**Pendiente:**

Registrar número exacto de tests y tiempo total.

### Frontend — Codex

```bash
cd tfg-codex/frontend
npm run dev
```

**Resultado:**

El frontend arranca y no muestra errores.

**Estado:**

Validado parcialmente.

**Pendiente:**

```bash
npm run build
```

### Backend manual — Codex

Pendiente de registrar, si no se ha ejecutado todavía.

Comando previsto:

```bash
cd tfg-codex
uvicorn app.main:app --reload
```

### Backend — DeepSeek

```bash
cd tfg-deepseek
uvicorn app.main:app --reload
```

**Resultado actual:**

El backend arranca correctamente.

**Estado:**

Validado.

### Tests backend — DeepSeek

```bash
cd tfg
python -m unittest discover -s tfg-deepseek\tests -p "test*.py" -v
```

**Resultado inicial:**

```text
Ran 0 tests in 0.000s

NO TESTS RAN
```

**Resultado tras corrección:**

```text
Ran 17 tests in 7.715s

OK
```

**Estado:**

Validado.

### Frontend build — DeepSeek

```bash
cd tfg-deepseek/frontend
npm run build
```

**Resultado:**

```text
vite v5.4.21 building for production...
✓ 30 modules transformed.
dist/index.html                  0.33 kB │ gzip:  0.25 kB
dist/assets/index-D8BmuV2y.js  143.02 kB │ gzip: 45.98 kB
✓ built in 368ms
```

**Estado:**

Validado.

---

## Notas de evaluación provisional — Claude Code

### Puntos positivos observados

- Confirmó que trabajaría dentro de `tfg-claude/`.
- Generó una estructura aparentemente modular.
- Separó backend, frontend, tests y documentación.
- Declaró uso de `unittest` y `TestClient`.
- Declaró uso de Fetch API.
- Identificó riesgos y pendientes.
- Corrigió sucesivamente los errores reportados.
- El backend finalmente arranca con `uvicorn`.
- Los tests piloto de backend pasan correctamente.
- El frontend mínimo arranca correctamente tras corrección.
- Se validan flujos básicos de registro, login, error de login, token y permisos de usuario.

### Puntos negativos observados

- El backend no arrancó en la primera prueba.
- Necesitó 3 correcciones para arrancar.
- Necesitó 6 prompts de corrección en total hasta validar backend, tests y frontend mínimo.
- Primer fallo crítico: error en `app/config.py`.
- Segundo fallo crítico: uso incorrecto de `DateTime` en SQLAlchemy.
- Tercer fallo crítico: import incorrecto desde `fastapi.security`.
- Cuarto fallo: problemas de registro/importación de modelos SQLAlchemy.
- Quinto fallo: base de datos de tests sin tablas.
- Sexto fallo: import relativo incorrecto en frontend.
- Usa SQLite en desarrollo aunque el contexto maestro pedía PostgreSQL por defecto.
- Usa `POST /auth/register` en tests aunque el contexto maestro pedía `POST /users/`.
- Posible uso de estructura de tests mezclada con pytest.
- Creó `.env`, que debe revisarse para evitar secretos o contaminación.
- Falta comprobar build frontend.
- Falta verificar en Swagger si existe `POST /users/`.

---

## Notas de evaluación provisional — Codex

### Puntos positivos observados

- Generó una estructura de proyecto suficiente como para ejecutar tests tras correcciones.
- Tras corregir los problemas iniciales, los tests funcionan correctamente.
- El frontend arranca sin mostrar errores.
- La primera desviación de tests fue corregible sin instalar pytest.
- La dependencia/configuración de `pydantic-settings` fue corregida.

### Puntos negativos observados

- Incumplió una restricción explícita del piloto: usó `pytest` aunque se pidió `unittest`.
- No declaró o no resolvió correctamente `pydantic-settings` al principio.
- Los tests no se ejecutaron correctamente en la primera validación.
- Todavía falta registrar validación manual de backend con `uvicorn`, si no se ha ejecutado.
- Falta comprobar build frontend.
- Falta revisar rutas reales en Swagger y endpoint exacto de registro.
- Falta revisar si respeta PostgreSQL por defecto en desarrollo y SQLite para tests.

### Estado actual

```text
Codex: tests piloto y frontend mínimo funcionando; pendiente de validación manual de backend, rutas, build y desviaciones.
```

---

## Notas de evaluación provisional — DeepSeek

### Puntos positivos observados

- DeepSeek generó una reconstrucción piloto dentro de `tfg-deepseek/`.
- Backend validado manualmente con `uvicorn`.
- Tras una corrección, creó tests reales detectables por `unittest`.
- Ejecuta 17 tests correctamente.
- Incluye test específico de seguridad: `test_register_cannot_become_admin`.
- La validación manual muestra que el usuario `admin` tiene rol `user`, no `admin`.
- Corrigió el README para eliminar la recomendación insegura de crear admin con `role: admin`.
- Frontend compila correctamente en modo producción con `npm run build`.
- `.env` no contiene secretos reales.
- `.gitignore` ignora `.env`, `.db`, `node_modules/` y `dist/`.
- Los tests cubren registro, login, permisos, token inválido, token ausente, duplicados, acceso de admin y eliminación.

### Puntos negativos observados

- Inicialmente no había tests detectables: `Ran 0 tests`.
- Inicialmente afirmó que las pruebas funcionales pasaban, pero el comando estándar no ejecutaba ninguna.
- Inicialmente propuso crear un admin manualmente desde `POST /users/` con `role: admin`, lo que era una señal de riesgo de seguridad.
- No existe mecanismo seguro para crear el primer administrador.
- Usa SQLite por defecto en desarrollo, aunque el contexto maestro pedía PostgreSQL por defecto.
- El frontend es mínimo y estático; no se observa consumo de API con Fetch en `App.jsx`.
- Falta revisar rutas reales en Swagger y estructura completa de modelos.

### Estado actual

```text
DeepSeek: backend, tests piloto, frontend build y README corregido funcionando; pendiente de revisión de rutas, configuración final y estructura.
```

---

## Puntuación provisional — Claude Code

No se asigna puntuación final completa porque faltan validaciones de:

- endpoint raíz manual;
- rutas en Swagger;
- existencia o ausencia de `POST /users/`;
- revisión real de estructura;
- revisión de modelos y relaciones;
- admin ve todos los usuarios;
- build frontend;
- revisión de `.env`;
- revisión de si usa Fetch API o Axios.

Puntuación provisional parcial:

| Criterio | Puntuación provisional | Motivo |
|---|---:|---|
| Backend arranca /20 | 15/20 | Arranca, pero necesitó 3 correcciones y usa SQLite en desarrollo. |
| Estructura /20 | Pendiente | Falta revisar estructura real de archivos. |
| Modelos /20 | Pendiente | Falta revisar que existan todos los modelos y relaciones. |
| Auth y permisos /20 | 15/20 | Tests piloto de auth y permisos pasan, pero usa `POST /auth/register` en vez de `POST /users/` y falta validar admin. |
| Claridad /20 | Pendiente | Falta valorar documentación y explicación final. |

Estado actual:

```text
Claude Code: backend, tests piloto y frontend mínimo funcionando; pendiente de revisión de rutas, build frontend y desviaciones.
```

---

## Puntuación provisional — Codex

No se asigna puntuación final completa porque faltan validaciones de:

- backend manual con `uvicorn`;
- endpoint raíz manual;
- rutas en Swagger;
- revisión real de estructura;
- revisión de modelos y relaciones;
- admin ve todos los usuarios;
- build frontend;
- revisión de `.env`;
- revisión de si usa Fetch API o Axios;
- revisión de configuración PostgreSQL/SQLite.

Puntuación provisional parcial:

| Criterio | Puntuación provisional | Motivo |
|---|---:|---|
| Backend arranca /20 | Pendiente | Tests pasan, pero falta registrar validación manual con `uvicorn`. |
| Estructura /20 | Pendiente | Falta revisar estructura real de archivos. |
| Modelos /20 | Pendiente | Falta revisar que existan todos los modelos y relaciones. |
| Auth y permisos /20 | Pendiente | Tests pasan, pero falta registrar qué cubren exactamente. |
| Claridad /20 | Pendiente | Falta valorar documentación y explicación final. |

Estado actual:

```text
Codex: tests piloto y frontend mínimo funcionando; pendiente de revisión de backend manual, rutas, build y desviaciones.
```

---

## Puntuación provisional — DeepSeek

No se asigna puntuación final completa porque faltan validaciones de:

- rutas en Swagger;
- revisión real de estructura;
- revisión de modelos y relaciones;
- revisión de si usa Fetch API o Axios en un cliente API centralizado;
- revisión completa de configuración PostgreSQL/SQLite.

Puntuación provisional parcial:

| Criterio | Puntuación provisional | Motivo |
|---|---:|---|
| Backend arranca /20 | 18/20 | Arranca correctamente. Falta revisar configuración exacta de base de datos, ya que usa SQLite por defecto. |
| Estructura /20 | Pendiente | Falta revisar estructura real de archivos. |
| Modelos /20 | Pendiente | Falta revisar que existan todos los modelos y relaciones. |
| Auth y permisos /20 | 17/20 | Tests cubren login, permisos, bloqueo de creación de admin, tokens inválidos y acceso entre usuarios. Falta revisar implementación manualmente. |
| Claridad /20 | 16/20 provisional | README fue corregido y documenta la limitación del primer admin, aunque sigue pendiente mecanismo seguro de creación de admin inicial y usa SQLite como valor por defecto. |

Estado actual:

```text
DeepSeek: backend, tests piloto, frontend build y README corregido funcionando; buen avance tras dos correcciones, pendiente de revisión de rutas y estructura.
```

---

## Próximos pasos

### Claude Code

1. Abrir documentación Swagger:

```text
http://127.0.0.1:8000/docs
```

2. Verificar rutas esperadas:

   - `POST /users/`
   - `POST /auth/login`
   - `GET /users/`
   - `GET /users/{user_id}`
   - `DELETE /users/{user_id}`

3. Confirmar si existe `POST /auth/register`, `POST /users/` o ambos.
4. Revisar `.env` y confirmar que no contiene secretos reales.
5. Revisar `.gitignore` y confirmar que `.env` está ignorado.
6. Revisar `frontend/src/api/api.js` y confirmar que usa Fetch API, no Axios.
7. Ejecutar build frontend:

```bash
cd tfg-claude/frontend
npm run build
```

8. Asignar puntuación provisional completa a Claude.

### Codex

1. Registrar salida exacta de tests:

```bash
cd tfg-codex
python -m unittest discover -s tests -p "test*.py" -v
```

2. Validar backend manual:

```bash
uvicorn app.main:app --reload
```

3. Abrir documentación Swagger:

```text
http://127.0.0.1:8000/docs
```

4. Verificar rutas esperadas:

   - `POST /users/`
   - `POST /auth/login`
   - `GET /users/`
   - `GET /users/{user_id}`
   - `DELETE /users/{user_id}`

5. Confirmar si existe `POST /auth/register`, `POST /users/` o ambos.
6. Revisar `.env` y confirmar que no contiene secretos reales.
7. Revisar `.gitignore` y confirmar que `.env` está ignorado.
8. Revisar `frontend/src/api/api.js` y confirmar que usa Fetch API, no Axios.
9. Ejecutar build frontend:

```bash
cd frontend
npm run build
```

10. Asignar puntuación provisional completa a Codex.

### DeepSeek

1. Abrir Swagger:

```text
http://127.0.0.1:8000/docs
```

2. Verificar rutas esperadas:

   - `POST /users/`
   - `POST /auth/login`
   - `GET /users/`
   - `GET /users/{user_id}`
   - `DELETE /users/{user_id}`

3. Revisar si existe un cliente API centralizado en frontend.
4. Revisar configuración de base de datos:
   - PostgreSQL por defecto en desarrollo.
   - SQLite para tests.
5. Revisar estructura real de modelos y schemas.
6. Asignar puntuación provisional completa a DeepSeek.

### GitHub Copilot GPT-4.1

Pendiente de empezar cuando Claude, Codex y DeepSeek tengan una primera validación comparable.