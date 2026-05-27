# Seed demo de AgroManager

Este seed carga datos de desarrollo para probar AgroManager sin editar SQLite manualmente. No usa secretos reales y sus credenciales son solo para entorno local/demo.

## Ejecutar

Desde la raiz del proyecto:

```bash
python scripts/seed_demo.py
```

El script crea las tablas si faltan, usa los modelos SQLAlchemy reales y hashea las contrasenas con la misma funcion que el login de la app.

## Credenciales de desarrollo

- Admin: `admin@test.com` / `admin123`
- Usuario: `user@test.com` / `user123`

No uses estas credenciales en produccion.

## Datos creados

- 1 usuario admin: `admin@test.com`, username `admin`, role `admin`.
- 1 usuario normal: `user@test.com`, username `user`, role `user`.
- 5 cultivos publicos de catalogo: Tomate, Lechuga, Zanahoria, Pimiento y Fresa.
- 2 cultivos personales para `user@test.com`: Mi Tomate y Mi Lechuga.
- Calendarios demo para cultivos publicos y personales, incluyendo uno activo y uno completado.
- 4 tareas demo para el usuario normal: 2 pendientes y 2 completadas.
- Datos de riego, requisitos ambientales y guias de cultivo para los cultivos demo.

## Idempotencia

Puedes ejecutar el seed varias veces. Reutiliza usuarios por `email`, cultivos publicos por `name + is_public`, cultivos personales por `owner_id + name`, calendarios/riego/ambiente/guias por la relacion uno-a-uno del cultivo, y tareas por `user_id + name`.

Al terminar imprime un resumen de elementos creados y existentes.

## Reset en desarrollo

Si necesitas partir de cero con SQLite local, para el entorno de desarrollo puedes parar el backend y borrar la base local:

```bash
Remove-Item -LiteralPath .\agromanager.db -Force
python scripts/seed_demo.py
```

No borres bases compartidas o de produccion.
