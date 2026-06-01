# Comparación por fases — AgroManager

## FASE 11 — Cierre técnico, limpieza y documentación final

**Estado del documento:** Final  
**Motivo:** Codex, DeepSeek y Claude Code están validados y cerrados. Claude Code fue completado posteriormente tras una interrupción temporal por cuota/herramienta.

---

## Objetivo de la fase

La FASE 11 tiene como objetivo cerrar técnicamente el proyecto y dejar cada implementación lista para:

- ejecución local;
- validación técnica;
- demostración visual;
- revisión del código;
- documentación del caso práctico;
- uso como evidencia para la memoria del TFG.

A diferencia de fases anteriores, esta fase no busca añadir nuevas funcionalidades grandes, sino consolidar lo ya desarrollado.

---

## Alcance funcional esperado

La fase debía producir o revisar:

1. README final claro y completo.
2. `.env.example` con valores seguros de ejemplo.
3. Guía de instalación.
4. Guía de ejecución backend.
5. Guía de ejecución frontend.
6. Guía de seed demo.
7. Credenciales demo.
8. Comandos de tests.
9. Comandos de build.
10. Estructura del proyecto.
11. Limitaciones conocidas.
12. Riesgos pendientes.
13. Guía rápida de demo.
14. Limpieza de archivos temporales innecesarios.
15. Validación final de backend/frontend/seed.

---

# Tabla comparativa final FASE 11

| IA | Estado | Documentación | Tests | Build | Limpieza | Observaciones | Puntuación final |
|---|---|---|---|---|---|---|---:|
| Claude Code | Validado y cerrado | README + `.env.example` + DEMO + VALIDATION + docs cierre | OK, 106 tests | OK, 513ms/569ms según validación | OK | Documentación extensa y cierre sin nuevas funcionalidades | 95 |
| Codex | Validado y cerrado | README + `.env.example` + DEMO + VALIDATION | OK, 52 tests | OK | OK | Conserva `agromanager.db` demo | 94 |
| DeepSeek | Validado y cerrado | README + DEMO + VALIDATION + `.env.example` revisado | OK, 117 tests | OK | OK | Documenta limitación de `unittest discover` en Windows | 95 |

---

# Codex — FASE 11

## Estado

**Validado y cerrado.**

Codex completó el cierre técnico de `tfg-codex/`, generando documentación final, guía de demo, guía de validación, ejemplo de entorno y limpieza de artefactos temporales.

---

## Archivos creados o modificados

| Archivo | Tipo | Descripción |
|---|---|---|
| `README.md` | Modificado | Documentación final completa del proyecto |
| `.env.example` | Creado/modificado | Variables reales del proyecto con valores seguros |
| `DEMO_GUIDE.md` | Creado | Guía paso a paso para demo de usuario y admin |
| `VALIDATION.md` | Creado | Guía técnica de validación, tests, build y checklist manual |

---

## Contenido documentado

La documentación final de Codex incluye:

- nombre del proyecto;
- descripción general;
- objetivo del caso práctico;
- stack tecnológico;
- funcionalidades principales;
- estructura del proyecto;
- instalación backend;
- instalación frontend;
- variables de entorno;
- ejecución de backend;
- ejecución de frontend;
- ejecución del seed demo;
- credenciales demo;
- comandos de tests;
- comandos de build;
- validación visual;
- limitaciones conocidas;
- riesgos pendientes;
- trabajo futuro.

---

## Validación ejecutada

Codex ejecutó:

```bash
python scripts/seed_demo.py
python -m unittest discover -s tests -p "test*.py" -v
npm.cmd run build
```

---

## Resultados

### Seed demo

```text
Seed demo OK e idempotente.
```

### Tests backend

```text
Ran 52 tests in 65.341s

OK
```

### Build frontend

```text
Frontend build OK.
Vite terminó con built.
```

---

## Limpieza realizada

Codex reportó la siguiente limpieza:

- eliminados directorios `__pycache__`;
- eliminada `.pytest_cache`;
- eliminadas bases temporales `test_app_*.db`;
- conservada `agromanager.db`, porque es la base local demo actual;
- conservados `node_modules` y `frontend/dist`, por ser artefactos locales útiles para ejecución/build y estar ignorados por `.gitignore`.

---

## Limitaciones documentadas

Entre las limitaciones y trabajo futuro documentados se incluyen:

- ausencia de migraciones/Alembic;
- ausencia de tests E2E;
- uso de SQLite como base local;
- entorno pensado para desarrollo/demo;
- comandos específicos para Windows PowerShell;
- uso de `npm.cmd run build` si `npm.ps1` está bloqueado por políticas locales.

---

## Fortalezas Codex FASE 11

- Cierre limpio y directo.
- Documentación final suficiente para ejecutar el proyecto.
- Seed, tests y build validados.
- Limpieza de temporales sin eliminar artefactos necesarios.
- Mantiene `unittest discover` como comando estándar de validación.
- Conserva la base demo local para facilitar demostración.

---

## Incidencias Codex FASE 11

No se detectan incidencias bloqueantes.

---

## Puntuación final Codex FASE 11

```text
94/100
```

### Justificación

Codex cumple perfectamente el objetivo de cierre técnico. La documentación deja el proyecto listo para demo y validación. Se penaliza ligeramente porque su cobertura total de tests es menor que DeepSeek y Claude.

---

# DeepSeek — FASE 11

## Estado

**Validado y cerrado.**

DeepSeek completó el cierre técnico de `tfg-deepseek/` con documentación final, guía de demo, guía de validación, revisión de `.env.example`, actualización de `.gitignore` y limpieza de artefactos temporales.

---

## Archivos creados o modificados

| Archivo | Tipo | Descripción |
|---|---|---|
| `README.md` | Modificado | README final completo |
| `DEMO_GUIDE.md` | Creado | Guía paso a paso de demostración |
| `VALIDATION.md` | Creado | Checklist técnica y visual de validación |
| `.env.example` | Revisado | Ya existía y estaba completo |
| `.gitignore` | Modificado | Añadidos patrones para bases de test |

---

## Cambios en `.gitignore`

DeepSeek añadió:

```gitignore
test_*.db
test_*.db-wal
test_*.db-shm
```

Esto evita subir bases temporales de test y sus ficheros auxiliares de SQLite.

---

## Documentación generada

### README.md

Incluye:

- stack tecnológico;
- estructura del proyecto;
- instalación;
- ejecución;
- seed demo;
- tests;
- build;
- credenciales demo;
- limitaciones;
- riesgos;
- trabajo futuro.

También documenta 13 funcionalidades principales del proyecto.

### DEMO_GUIDE.md

Incluye:

- preparación del entorno;
- instalación de dependencias;
- ejecución del seed;
- arranque de backend;
- arranque de frontend;
- recorrido como usuario normal;
- recorrido como administrador;
- pruebas de API con `curl`;
- tabla de URLs.

### VALIDATION.md

Incluye:

- comandos de seed;
- comandos de tests individuales y conjuntos;
- observación sobre `unittest discover` en Windows PowerShell;
- comando de build frontend;
- checklist visual de usuario;
- checklist visual de admin;
- pruebas API con `curl`;
- tabla resumen de comandos.

---

## Validación final ejecutada

DeepSeek ejecutó:

```bash
python scripts/seed_demo.py
python -m unittest tests.test_api tests.test_seed -v
npm.cmd run build
```

---

## Resultados

### Seed demo

```text
Seed ejecutado correctamente.
```

Datos reportados:

- 2 usuarios;
- 7 cultivos;
- 3 calendarios;
- 4 tareas;
- 7 registros de riego;
- 7 requisitos ambientales;
- 5 guías.

### Tests backend

```text
117 tests OK en 76.5s
```

### Build frontend

```text
✓ built in 600ms
dist/index.html 0.33kB
dist/assets/index-Byj7vGJZ.js 235kB
```

---

## Limpieza realizada

DeepSeek reportó:

- no se eliminó `agromanager.db`, porque contiene datos demo locales;
- eliminados 6 directorios `__pycache__`;
- eliminados 42 archivos `.pyc`;
- no se encontraron temporales como `test_result.txt` o `make_admin.py`;
- `.gitignore` ya ignoraba:
  - `__pycache__/`;
  - `*.db`;
  - `.env`;
  - `uploads/*`;
  - `node_modules/`;
  - `dist/`.

---

## Limitaciones documentadas

DeepSeek documentó 7 limitaciones principales:

1. SQLite no apto para producción multiusuario.
2. Sin sistema de migraciones Alembic.
3. Imágenes placeholder.
4. Google OAuth no implementado, aunque hay campo preparado.
5. Sin tests E2E.
6. `unittest discover` puede no detectar tests en Windows PowerShell.
7. Tests API y seed usan archivos `.db` distintos y `dependency_overrides` propios.

---

## Riesgos pendientes

DeepSeek no reporta riesgos nuevos. Los puntos pendientes quedan recogidos como limitaciones y trabajo futuro.

---

## Fortalezas DeepSeek FASE 11

- Documentación muy completa.
- Checklist técnica y visual detallada.
- Mayor cobertura de tests: 117 tests.
- Actualización útil de `.gitignore`.
- Limpieza cuantificada: 6 directorios y 42 `.pyc`.
- Documentación explícita de la limitación de `unittest discover`.
- Deja trazabilidad clara de seed, build y demo.

---

## Incidencias DeepSeek FASE 11

No se detectan incidencias bloqueantes en esta fase.

La única observación es que se mantiene la particularidad metodológica de usar:

```bash
python -m unittest tests.test_api tests.test_seed -v
```

en lugar del comando estándar con `discover`, debido a problemas documentados en Windows PowerShell.

---

## Puntuación final DeepSeek FASE 11

```text
95/100
```

### Justificación

DeepSeek destaca por una documentación muy completa, una validación técnica amplia y una limpieza detallada. Se penaliza ligeramente porque conserva la observación del comando `discover`, aunque la ejecución conjunta explícita de 117 tests está validada.

---

# Claude Code — FASE 11

## Estado

**Validado y cerrado.**

Claude Code completó la FASE 11 como cierre técnico, limpieza y documentación final. La fase respetó el alcance definido: no se añadieron nuevas funcionalidades, no se implementó Alembic, no se añadieron migraciones y no se añadieron tests E2E.

---

## Deliverables requeridos

| Archivo | Estado | Detalles |
|---|---|---|
| `README.md` | Actualizado | Quick start, stack claro y enlaces a documentación |
| `.env.example` | Actualizado | Comentarios detallados y valores seguros |
| `DEMO_GUIDE.md` | Creado | Guía de demostración paso a paso |
| `VALIDATION.md` | Creado | Validación técnica exhaustiva |

---

## Documentación complementaria creada

- `FASE11_CIERRE.md`
- `FASE11_DELIVERABLES.md`

---

## Validación técnica ejecutada

Claude reportó:

```text
Tests Backend:     106/106 OK
Frontend Build:    569ms sin errores
Seed Demo:         Idempotente
API Endpoints:     Todos funcionales
Admin RBAC:        Funcional
```

Además, la validación final de terminal mostró:

### Tests backend

```text
Ran 106 tests in 60.980s

OK
```

### Build frontend

```text
vite v5.4.21 building for production...
✓ 58 modules transformed.
dist/index.html                   0.47 kB │ gzip:  0.31 kB
dist/assets/index-D5y9pt0e.css   12.92 kB │ gzip:  2.90 kB
dist/assets/index-AXNBHVE3.js   198.27 kB │ gzip: 60.35 kB
✓ built in 513ms
```

---

## Contenido documentado

La documentación final de Claude incluye:

- quick start;
- stack tecnológico;
- instalación backend;
- instalación frontend;
- ejecución del seed demo;
- credenciales demo;
- ejecución de tests;
- build frontend;
- validación técnica;
- validación visual;
- demo de usuario;
- demo de administrador;
- limitaciones conocidas;
- riesgos pendientes;
- cierre técnico.

---

## Fortalezas Claude FASE 11

- Documentación final extensa.
- Guía de demo completa.
- Checklist de validación técnica.
- `.env.example` actualizado con valores seguros.
- 106 tests OK.
- Build frontend OK.
- Seed demo idempotente.
- RBAC admin funcional.
- Respeta el alcance: sin Alembic, sin migraciones, sin E2E y sin nuevas funcionalidades.

---

## Limitaciones Claude FASE 11

| Limitación | Impacto | Estado |
|---|---|---|
| Menos tests que DeepSeek | Menor cobertura total | Aceptable |
| Documentación muy extensa | Puede requerir organización | Aceptable |
| Sin migraciones/Alembic | Pendiente para producción | Pendiente |
| Sin tests E2E | Validación visual manual | Pendiente |
| SQLite local | No apto para producción multiusuario | Pendiente |

---

## Incidencias Claude FASE 11

No se detectan incidencias bloqueantes.

La principal observación metodológica es que Claude había quedado interrumpido temporalmente por cuota en fases anteriores, pero posteriormente se retomó y completó FASE 9, FASE 10 y FASE 11.

---

## Puntuación final Claude FASE 11

```text
95/100
```

### Justificación

Claude completa un cierre técnico muy sólido, con documentación amplia, seed idempotente, tests OK, build OK y RBAC funcional. Se sitúa al nivel de DeepSeek en cierre documental, aunque con menor número total de tests.

---

# Comparación final FASE 11

## Mejor cobertura técnica

**DeepSeek**

Motivo:

- 117 tests validados frente a 106 de Claude y 52 de Codex.
- Documentación de validación extensa.

## Mejor integración con comando estándar

**Codex / Claude Code**

Motivo:

- Mantienen `python -m unittest discover -s tests -p "test*.py" -v` como comando de referencia.
- DeepSeek conserva la particularidad de invocación explícita de módulos.

## Mejor limpieza

**DeepSeek**

Motivo:

- Limpieza cuantificada.
- Actualización de `.gitignore`.
- Eliminación explícita de `__pycache__` y `.pyc`.

## Mejor cierre documental

**Claude Code / DeepSeek**

Motivo:

- Claude genera documentos de cierre adicionales.
- DeepSeek genera documentación técnica muy detallada y checklist completo.

## Mejor cierre para demo

**Empate Codex / DeepSeek / Claude Code**

Motivo:

- Las tres implementaciones tienen README final.
- Las tres tienen guía de demo o documentación equivalente.
- Las tres tienen guía de validación.
- Las tres documentan credenciales demo.
- Las tres tienen seed, tests y build validados.

---

# Resultado final

| Posición | IA | Puntuación | Motivo |
|---:|---|---:|---|
| 1 | DeepSeek | 95/100 | Mayor cobertura y documentación técnica muy amplia |
| 1 | Claude Code | 95/100 | Cierre documental sólido, 106 tests OK y build final OK |
| 3 | Codex | 94/100 | Muy estable, simple e integrado con comando estándar |

---

# Estado acumulado tras FASE 11

| IA | Piloto 0-3 | FASE 4 | FASE 5 | FASE 6 | FASE 7 | FASE 8 | FASE 9 | FASE 10 | FASE 11 | Estado acumulado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | 91 | 92 | 91 | 92 | 94 | 95 | Funcional y completo tras correcciones |
| Codex | 77 | 86 | 90 | 90 | 91 | 90 | 91 | 94 | 94 | Funcional, estable, integrado y listo para demo |
| DeepSeek | 87 | 94 | 96 | 96 | 97 | 92 | 93 | 95 | 95 | Mejor resultado acumulado global |

---

# Incidencias transversales FASE 11

## 1. Claude completado tras interrupción temporal

Claude había quedado temporalmente pendiente por límite de herramienta/cuota. Finalmente se retomó y se completaron las fases 9, 10 y 11.

Esto debe registrarse en la memoria como una limitación metodológica temporal, no como una fase no completada.

## 2. Diferencia en ejecución de tests

Codex y Claude mantienen el comando estándar con `discover`.

DeepSeek usa ejecución explícita:

```bash
python -m unittest tests.test_api tests.test_seed -v
```

Esto no invalida sus resultados, pero debe anotarse como diferencia metodológica.

## 3. Ausencia de migraciones

Ninguna implementación incorpora Alembic. Esto queda como trabajo futuro.

## 4. Ausencia de E2E

La validación visual sigue siendo manual. No hay Playwright/Cypress.

## 5. SQLite como entorno demo

SQLite es suficiente para desarrollo y validación local, pero no para producción multiusuario.

---

# Conclusión FASE 11

FASE 11 cierra técnicamente el caso práctico para Codex, DeepSeek y Claude Code.

Las tres implementaciones quedan listas para:

- ejecución local;
- demostración;
- validación;
- revisión;
- documentación;
- uso como evidencia en la memoria del TFG.

La diferencia principal es:

- **Codex** ofrece un cierre más simple, estable e integrado con el comando estándar.
- **DeepSeek** ofrece un cierre más amplio, documentado y con más cobertura, aunque mantiene una particularidad en la ejecución de tests.
- **Claude Code** ofrece un cierre documental muy sólido, completa las fases pendientes y confirma seed, tests, build y RBAC funcional.

Con esta fase, el desarrollo comparativo queda cerrado y puede utilizarse como base final para la memoria del TFG.
