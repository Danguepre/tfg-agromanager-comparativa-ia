# 🌱 Seed de Desarrollo / Demo — AgroManager

Este script inicializa la base de datos de desarrollo con datos de ejemplo
para poder probar todas las funcionalidades de AgroManager sin tener que
introducir datos manualmente.

## ¿Para qué sirve?

- Crear un usuario **admin** y un **usuario normal** de prueba.
- Poblar el **catálogo público** con 5 cultivos de ejemplo.
- Crear **cultivos personales** para el usuario normal.
- Crear **calendarios agrícolas** (activo y completado).
- Crear **tareas** (pending y completed).
- Crear **datos de riego** y **requisitos ambientales**.
- Crear **guías de cultivo** para los cultivos del catálogo.

## Requisitos

- El backend debe haberse ejecutado al menos una vez para que existan las tablas.
- Tener las dependencias instaladas (`pip install -r requirements.txt`).

## Cómo ejecutar

Desde el directorio raíz del proyecto (`tfg-deepseek/`):

```bash
python scripts/seed_demo.py
```

## Credenciales DEMO

| Rol    | Email            | Contraseña |
|--------|------------------|------------|
| Admin  | admin@test.com   | admin123   |
| User   | user@test.com    | user123    |

## ¿Qué datos crea?

### Usuarios
- **admin** (rol admin, activo)
- **user** (rol user, activo)

### Cultivos públicos de catálogo (5)
1. **Tomate** — Hortaliza, con datos de riego, ambiente, calendario activo y guía.
2. **Lechuga** — Hortaliza, con datos de riego, ambiente y guía.
3. **Zanahoria** — Hortaliza, con datos de riego, ambiente y guía.
4. **Pimiento** — Hortaliza, con datos de riego, ambiente y guía.
5. **Fresa** — Fruta, con datos de riego, ambiente y guía.

### Cultivos personales (2 para user)
1. **Mi Tomate** — Con calendario activo (fase: trasplante).
2. **Mi Lechuga** — Con calendario completado.

### Tareas (4 para user)
- 2 **pending**: "Regar los tomates", "Abonar las lechugas"
- 2 **completed**: "Cosechar fresas maduras", "Preparar suelo para zanahorias"
- Las tareas relacionadas con tomate/lechuga se asignan automáticamente a los cultivos correspondientes.

### Riego y ambiente
- Cada cultivo (catálogo y personal) tiene sus propios atributos de riego y requisitos ambientales.
- Los cultivos del catálogo tienen datos específicos (frecuencia, método, temperaturas, pH, etc.).
- Los cultivos personales tienen valores por defecto.

## Idempotencia

El script es **idempotente**: puedes ejecutarlo varias veces sin duplicar datos.
- Los usuarios se identifican por **email**.
- Los cultivos públicos se identifican por **name** + **is_public=True**.
- Los cultivos personales se identifican por **name** + **owner_id**.
- Las tareas se identifican por **title** + **owner_id**.
- Los calendarios se identifican por **crop_id**.

## Advertencia

⚠️ **NO uses estas credenciales en producción.**
Este seed es exclusivamente para desarrollo y pruebas locales.
Las contraseñas son débiles y públicas.

## Cómo resetear la base de datos en desarrollo

Si necesitas empezar de cero:

### Opción 1: Eliminar el archivo SQLite
```bash
# Desde tfg-deepseek/
del agromanager.db
```
Luego reinicia el backend (se crearán las tablas vacías) y ejecuta el seed.

### Opción 2: Si usas otro motor de BD
Conéctate a tu BD y ejecuta:
```sql
DROP TABLE IF EXISTS task_crops;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS cultivation_guides;
DROP TABLE IF EXISTS planting_calendars;
DROP TABLE IF EXISTS environmental_requirements;
DROP TABLE IF EXISTS irrigation_attributes;
DROP TABLE IF EXISTS crops;
DROP TABLE IF EXISTS users;
```
Luego reinicia el backend y ejecuta el seed.

## Tests

```bash
python -m unittest discover -s tests -p "test*.py" -v
```

Los tests del seed verifican:
- Creación de admin y usuario normal.
- Creación de 5+ cultivos públicos.
- Idempotencia (no duplicación en 2ª ejecución).
- Contraseñas hasheadas con bcrypt.
- Login exitoso con ambas cuentas.
- Catálogo público con datos.
- Creación de cultivos personales.
- Creación de 4+ tareas con estados pending/completed.