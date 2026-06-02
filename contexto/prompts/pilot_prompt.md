Actúa como desarrollador full-stack senior.

Vamos a hacer una reconstrucción piloto de AgroManager.

Contexto resumido:
AgroManager es una aplicación web para gestionar cultivos personales y un catálogo público de cultivos. El proyecto final tendrá backend FastAPI, frontend React/Vite, autenticación JWT, roles user/admin, cultivos, calendario agrícola, tareas, dashboard, admin y tests.

En esta primera prueba NO quiero el proyecto completo.

Implementa solo estas fases:

FASE 0: Plan de trabajo
- Explica cómo vas a organizar el proyecto.
- Indica decisiones técnicas.
- No escribas código todavía salvo estructura propuesta.

FASE 1: Arquitectura base
- Backend FastAPI en app/.
- SQLAlchemy.
- Pydantic.
- Lectura de variables de entorno.
- CORS configurable.
- Montaje de /uploads.
- GET / con JSON de salud.
- Estructura modular con models, schemas, routes y services.
- Frontend React/Vite mínimo en frontend/.
- Scripts básicos.
- README inicial.

FASE 2: Modelos y schemas
Implementa modelos y schemas para:
- User.
- Crop.
- PlantingCalendar.
- IrrigationAttributes.
- EnvironmentalRequirements.
- CultivationGuide.
- Task.
- TaskCrop.

Reglas:
- No exponer password en respuestas.
- User tiene role user/admin.
- Crop puede ser público, tener propietario o ser copia de otro cultivo.
- Task puede asociarse a varios cultivos.
- PlantingCalendar tiene fases siembra, trasplante y cosecha.

FASE 3: Autenticación y usuarios
Implementa:
- POST /users/ para registro.
- POST /auth/login para login.
- Password hasheada.
- JWT con user_id y role.
- Dependencia get_current_user.
- GET /users/.
- GET /users/{user_id}.
- DELETE /users/{user_id}.
- Permisos: usuario normal solo accede a sí mismo; admin puede ver todos.
- Rutas protegidas deben fallar sin token.
- No usar secretos reales.
- Google OAuth puede quedar preparado de forma opcional, sin depender de credenciales reales.

Criterios de aceptación de esta prueba:
- Backend arranca con uvicorn.
- GET / devuelve salud.
- Las tablas se crean correctamente.
- Se puede registrar usuario.
- Se puede hacer login.
- Login devuelve access_token.
- Una ruta protegida falla sin token.
- Usuario normal no puede ver datos de otros usuarios.
- Admin puede ver todos los usuarios.
- No se expone password en respuestas.

Al terminar, entrega:
1. archivos creados/modificados;
2. decisiones técnicas;
3. comandos para ejecutar;
4. comandos para probar;
5. riesgos o limitaciones;
6. qué queda pendiente para las siguientes fases.