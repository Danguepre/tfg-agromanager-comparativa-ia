# Incidencias — Claude FASE 9

## Bug detectado

Backend reconocía al usuario como admin, pero el frontend no mostraba enlace Admin ni permitía `/admin/dashboard`.

## Causa

El JWT contenía `role: admin`, pero el objeto `user` en `localStorage` solo contenía email.

## Solución

Se añadió `parseJwt()` en `api.js` y se modificaron `Login.jsx` y `Register.jsx` para guardar el rol.
