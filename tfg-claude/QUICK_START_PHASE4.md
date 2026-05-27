## FASE 4: Cultivos y Catálogo - Guía Rápida de Uso

### Arrancar el Servidor

```bash
cd c:\Users\danie\Desktop\tfg\tfg-claude

# Instalar dependencias (si es necesario)
pip install -r requirements.txt

# Iniciar servidor
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API disponible en: `http://127.0.0.1:8000`  
Documentación: `http://127.0.0.1:8000/docs`

---

### Ejecutar Tests

```bash
# Todos los tests
python -m unittest tests.test_api -v

# Solo tests de cultivos (13 nuevos tests)
python -m unittest tests.test_api.TestCropManagement -v

# Test específico
python -m unittest tests.test_api.TestCropManagement.test_copy_crop_from_catalog -v
```

**Resultado esperado:** 25 tests, OK (0 fallos)

---

### Flujo de Usuario - Ejemplo con curl

#### 1. Registrar usuario
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123","name":"Juan"}'
```

#### 2. Login
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'
# Obtener: access_token
```

#### 3. Crear cultivo personal
```bash
curl -X POST "http://127.0.0.1:8000/crops/" \
  -H "Authorization: Bearer {access_token}" \
  -F "name=Tomate" \
  -F "crop_type=verdura" \
  -F "description=Tomate casero" \
  -F "image=@/path/to/image.jpg"
```

#### 4. Ver mis cultivos
```bash
curl "http://127.0.0.1:8000/crops/my" \
  -H "Authorization: Bearer {access_token}"
```

#### 5. Ver catálogo público (sin autenticación)
```bash
curl "http://127.0.0.1:8000/crops/published"
curl "http://127.0.0.1:8000/crops/published?name=Tomate"
curl "http://127.0.0.1:8000/crops/published?crop_type=verdura"
```

#### 6. Copiar cultivo del catálogo
```bash
curl -X POST "http://127.0.0.1:8000/crops/{crop_id}/add-to-my-crops" \
  -H "Authorization: Bearer {access_token}"
```

#### 7. Actualizar cultivo
```bash
curl -X PUT "http://127.0.0.1:8000/crops/{crop_id}" \
  -H "Authorization: Bearer {access_token}" \
  -F "name=Tomate Modificado"
```

#### 8. Eliminar cultivo
```bash
curl -X DELETE "http://127.0.0.1:8000/crops/{crop_id}" \
  -H "Authorization: Bearer {access_token}"
```

---

### Variables de Entorno (.env)

```env
APP_ENV=development
DATABASE_URL=sqlite:///./agro.db
# O PostgreSQL: postgresql+psycopg2://user:password@localhost/agro

JWT_SECRET_KEY=tu-clave-super-secreta-aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

CORS_ORIGINS=["http://127.0.0.1:5173","http://localhost:5173"]

GOOGLE_CLIENT_ID=xxx (no es necesario para local)
GOOGLE_CLIENT_SECRET=xxx
```

---

### Estructura de Respuesta - Ejemplo

#### POST /crops/
```json
{
  "id": 1,
  "name": "Tomate",
  "description": "Tomate casero",
  "crop_type": "verdura",
  "owner_id": 1,
  "is_public": false,
  "source_crop_id": null,
  "image_path": "crops/a1b2c3d4.jpg",
  "created_at": "2026-05-20T10:30:00",
  "updated_at": "2026-05-20T10:30:00",
  "owner": {
    "id": 1,
    "email": "user@example.com",
    "name": "Juan"
  },
  "irrigation": {
    "id": 1,
    "water_frequency_days": null,
    "water_amount_mm": null,
    "irrigation_type": null,
    "notes": null
  },
  "environmental": {
    "id": 1,
    "min_temperature_celsius": null,
    "max_temperature_celsius": null,
    "min_humidity_percent": null,
    "max_humidity_percent": null,
    "sunlight_hours_per_day": null,
    "soil_type": null,
    "soil_ph_min": null,
    "soil_ph_max": null
  }
}
```

#### GET /crops/my (paginado)
```json
{
  "total": 3,
  "skip": 0,
  "limit": 50,
  "items": [
    {
      "id": 1,
      "name": "Tomate",
      "crop_type": "verdura",
      ...
    }
  ]
}
```

---

### Comportamiento de Copias

#### Copiar cultivo del catálogo
```bash
# Admin crea cultivo público
curl -X POST "http://127.0.0.1:8000/crops/" \
  -H "Authorization: Bearer {admin_token}" \
  -F "name=Maíz" \
  -F "is_public=true"
# Resultado: id=2 (cultivo público)

# Usuario copia
curl -X POST "http://127.0.0.1:8000/crops/2/add-to-my-crops" \
  -H "Authorization: Bearer {user_token}"
# Resultado: Nuevo cultivo id=3
#   - owner_id = usuario_id
#   - source_crop_id = 2 (original)
#   - is_public = false (siempre privado)
```

#### Independencia de copias
```bash
# Editar copia (id=3) NO afecta original (id=2)
curl -X PUT "http://127.0.0.1:8000/crops/3" \
  -H "Authorization: Bearer {user_token}" \
  -F "name=Maíz Modificado"

# Original sigue siendo "Maíz"
curl "http://127.0.0.1:8000/crops/2"
# name: "Maíz"  <- no cambió
```

#### Eliminar cultivos
```bash
# Eliminar copia: se quita de BD
DELETE /crops/3

# Eliminar original privado: se quita de BD
DELETE /crops/1

# Eliminar original público: se conserva pero sin owner
DELETE /crops/2
# Resultado: Cultivo 2 sigue en /crops/published
#   - owner_id = null
#   - is_public = true
```

---

### Validaciones y Errores

#### 401 Unauthorized
```json
{
  "detail": "Missing authentication credentials"
}
```
**Causa:** Sin token en header `Authorization: Bearer {token}`

#### 403 Forbidden
```json
{
  "detail": "Only admin can create public crops"
}
```
**Causa:** Usuario normal intenta crear cultivo `is_public=true`

#### 403 Forbidden - Permisos
```json
{
  "detail": "You don't have permission to edit this crop"
}
```
**Causa:** Intentar editar cultivo de otro usuario sin ser admin

#### 404 Not Found
```json
{
  "detail": "Crop not found"
}
```
**Causa:** ID de cultivo no existe

#### 413 Request Entity Too Large
```json
{
  "detail": "File too large. Max size: 5MB"
}
```
**Causa:** Imagen mayor a 5MB

#### 400 Bad Request
```json
{
  "detail": "Invalid file type. Allowed: .jpg, .jpeg, .png, .gif, .webp"
}
```
**Causa:** Extensión de archivo no permitida

---

### Próximos Pasos

1. **Frontend:** Implementar componentes React para CRUD de cultivos
2. **Búsqueda:** Agregar búsqueda full-text avanzada en catálogo
3. **Recomendaciones:** Sistema de recomendaciones por región/clima
4. **Imágenes:** Compresión, thumbnails, caché
5. **Análisis:** Dashboard con estadísticas de cultivos

---

### Soporte

- **Documentación API:** `http://127.0.0.1:8000/docs` (Swagger UI)
- **Tests:** `python -m unittest tests.test_api -v`
- **Logs:** Consola durante ejecución
- **DB:** SQLite local o PostgreSQL según `DATABASE_URL`

---

**Versión:** 1.0.0  
**Estado:** Producción-listo (FASE 4 completado)  
**Última actualización:** 2026-05-20
