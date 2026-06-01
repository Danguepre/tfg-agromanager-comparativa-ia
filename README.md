# TFG - Evaluación de IA en Desarrollo Software

## Descripción

El objetivo de este proyecto es desarrollar una aplicación web sencilla para la gestión de cultivos, utilizando una arquitectura basada en:

- Backend: API REST
- Base de datos relacional
- Frontend básico

Este proyecto forma parte de un estudio comparativo en el que distintas herramientas de inteligencia artificial generarán soluciones a partir de este mismo enunciado.

---

## Objetivo del sistema

Desarrollar una aplicación que permita gestionar información básica sobre cultivos, incluyendo:

- Listado de cultivos
- Información detallada de cada cultivo
- Calendario de siembra
- Guía de cultivo

---

## Requisitos funcionales

### 1. Gestión de cultivos (CRUD completo)

El sistema debe permitir:

- Crear un cultivo  
- Obtener listado de cultivos  
- Obtener un cultivo por ID  
- Actualizar un cultivo  
- Eliminar un cultivo  

Campos mínimos de un cultivo:

- id
- name
- type
- life_cycle

Endpoints esperados:

- GET /crops  
- GET /crops/{id}  
- POST /crops  
- PUT /crops/{id}  
- DELETE /crops/{id}  

---

### 2. Calendario de siembra

Para cada cultivo se debe almacenar:

- fecha inicio de siembra  
- fecha fin de siembra  
- fecha inicio de cosecha  
- fecha fin de cosecha  

Endpoint esperado:

- GET /crops/{id}/calendar  

---

### 3. Guía de cultivo

Cada cultivo debe tener una guía compuesta por pasos:

- número de paso  
- descripción  

Endpoint esperado:

- GET /crops/{id}/guide  

---

## Requisitos técnicos

### Backend

- Lenguaje: Python  
- Framework: FastAPI  
- Arquitectura basada en API REST  

---

### Base de datos

- Tipo: Relacional  
- Motor: PostgreSQL o MariaDB  

Debe incluir al menos las siguientes entidades:

- crops  
- planting_calendar  
- cultivation_guides  

---

### Frontend

- HTML  
- CSS  
- JavaScript  

Debe permitir:

- Mostrar listado de cultivos  
- Visualizar detalle de un cultivo  
- Realizar peticiones a la API  

---

## Requisitos adicionales

- Código estructurado y modular  
- Uso de buenas prácticas  
- Manejo básico de errores (404, 400, etc.)  
- Validación de datos de entrada  
- Separación clara entre capas (frontend, backend, base de datos)  

---

## Estructura esperada del proyecto

backend/  
frontend/  
database/  

---

## Criterios de evaluación

La solución será evaluada en base a:

- Correctitud del código  
- Cumplimiento de requisitos funcionales  
- Calidad y estructura del código  
- Claridad y legibilidad  
- Número de iteraciones necesarias para obtener una solución funcional  
- Manejo de errores y validaciones  

---

## Restricciones

- No es necesario implementar autenticación  
- No es necesario implementar funcionalidades avanzadas  
- No es necesario optimizar el rendimiento  

---

## Notas

- Se prioriza simplicidad y claridad sobre complejidad  
- Todas las soluciones deben partir de este mismo enunciado  
- No se deben reutilizar soluciones generadas por otras herramientas de IA  

---
## Configuración de Google OAuth

Para habilitar el inicio de sesión con Google en el backend, crea un archivo `.env` en la raíz del proyecto con estas variables:

```env
APP_ENV=development
DATABASE_URL=postgresql://postgres:admin@localhost:5432/tfg_db
GOOGLE_CLIENT_ID=tu-google-client-id
GOOGLE_CLIENT_SECRET=tu-google-client-secret
GOOGLE_OAUTH_REDIRECT=http://127.0.0.1:5173/auth/google/callback
FRONTEND_URL=http://127.0.0.1:5173
CORS_ORIGINS=http://127.0.0.1:5173
```

Luego instala las dependencias y arranca el backend. El flujo de Google iniciará en `http://127.0.0.1:5173/auth/google` y redirigirá al frontend con el token.

---