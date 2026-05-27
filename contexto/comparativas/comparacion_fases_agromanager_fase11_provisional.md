# Comparación por fases — AgroManager

## FASE 11 — Cierre técnico, limpieza y documentación final

**Estado del documento:** Provisional  
**Motivo:** Codex y DeepSeek están validados y cerrados. Claude Code queda pendiente por agotamiento de cuota/herramienta y se añadirá cuando pueda completarse.

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

# Tabla comparativa provisional FASE 11

| IA | Estado | Documentación | Tests | Build | Limpieza | Observaciones | Puntuación provisional |
|---|---|---|---|---|---|---|---:|
| Claude Code | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente | Bloqueado por cuota/herramienta | Pendiente |
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

## Puntuación provisional Codex FASE 11

```text
94/100
```

### Justificación

Codex cumple perfectamente el objetivo de cierre técnico. La documentación deja el proyecto listo para demo y validación. Se penaliza ligeramente porque su cobertura total de tests es menor que DeepSeek y porque no añade mejoras de producción como migraciones o E2E, aunque no eran obligatorias.

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

## Puntuación provisional DeepSeek FASE 11

```text
95/100
```

### Justificación

DeepSeek destaca por una documentación muy completa, una validación técnica amplia y una limpieza detallada. Se penaliza ligeramente porque conserva la observación del comando `discover`, aunque la ejecución conjunta explícita de 117 tests está validada.

---

# Claude Code — FASE 11

## Estado

**Pendiente.**

Claude Code no se ha podido validar en FASE 11 por agotamiento de cuota/herramienta.

---

## Situación actual

- Claude quedó validado hasta FASE 8.
- Claude FASE 9 está pendiente.
- Claude FASE 10 está pendiente.
- Claude FASE 11 también queda pendiente.
- Se retomará cuando vuelva la cuota o si se decide usar una herramienta alternativa.

---

## Nota metodológica

Si Claude se continúa mediante Cline/API externa, debe registrarse como cambio de herramienta en la comparación.

Ejemplo:

```text
Claude FASE 9-11 continuado mediante Cline con anthropic/claude-haiku-4.5 tras agotarse la cuota mensual de GitHub Copilot Chat.
```

Esto mantiene el mismo modelo/familia aproximada, pero cambia la herramienta agente y puede afectar la comparación.

---

# Comparación provisional FASE 11

## Mejor cobertura técnica

**DeepSeek**

Motivo:

- 117 tests validados frente a 52 de Codex.
- Documentación de validación más extensa.

## Mejor integración con comando estándar

**Codex**

Motivo:

- Mantiene `python -m unittest discover -s tests -p "test*.py" -v` como comando de referencia.
- No arrastra la particularidad de invocación explícita de módulos.

## Mejor limpieza

**DeepSeek**

Motivo:

- Limpieza cuantificada.
- Actualización de `.gitignore`.
- Eliminación explícita de `__pycache__` y `.pyc`.

## Mejor cierre para demo

**Empate Codex / DeepSeek**

Motivo:

- Ambos tienen README final.
- Ambos tienen guía de demo.
- Ambos tienen guía de validación.
- Ambos conservan `agromanager.db` demo local.
- Ambos documentan credenciales demo.

## Mejor resultado provisional

**DeepSeek por margen pequeño**

Motivo:

- Mayor cobertura técnica.
- Más documentación de validación.
- Mejor trazabilidad de limpieza.
- Codex gana en simplicidad e integración estándar.

---

# Resultado provisional

| Posición provisional | IA | Puntuación | Motivo |
|---:|---|---:|---|
| 1 | DeepSeek | 95/100 | Mayor cobertura y documentación más extensa |
| 2 | Codex | 94/100 | Muy estable, simple e integrado con comando estándar |
| — | Claude Code | Pendiente | Bloqueado por cuota/herramienta |

---

# Estado acumulado provisional tras FASE 11

| IA | Piloto 0-3 | FASE 4 | FASE 5 | FASE 6 | FASE 7 | FASE 8 | FASE 9 | FASE 10 | FASE 11 | Estado acumulado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Claude Code | 75 | 90 | 88 | 91 | 92 | 91 | Pendiente | Pendiente | Pendiente | Funcional hasta FASE 8; fases 9-11 pendientes |
| Codex | 77 | 86 | 90 | 90 | 91 | 90 | 91 | 94 | 94 | Funcional, estable, integrado y listo para demo |
| DeepSeek | 87 | 94 | 96 | 96 | 97 | 92 | 93 | 95 | 95 | Mejor resultado acumulado provisional |

---

# Incidencias transversales FASE 11

## 1. Claude pendiente

Claude queda pendiente por límite de herramienta/cuota. Esto debe registrarse claramente en la memoria como una limitación metodológica temporal.

## 2. Diferencia en ejecución de tests

Codex mantiene el comando estándar con `discover`.

DeepSeek usa ejecución explícita:

```bash
python -m unittest tests.test_api tests.test_seed -v
```

Esto no invalida sus resultados, pero debe anotarse como diferencia metodológica.

## 3. Ausencia de migraciones

Ni Codex ni DeepSeek implementan Alembic. Esto queda como trabajo futuro.

## 4. Ausencia de E2E

La validación visual sigue siendo manual. No hay Playwright/Cypress.

## 5. SQLite como entorno demo

SQLite es suficiente para desarrollo y validación local, pero no para producción multiusuario.

---

# Conclusión provisional FASE 11

FASE 11 cierra técnicamente el caso práctico para Codex y DeepSeek.

Ambas implementaciones quedan listas para:

- ejecución local;
- demostración;
- validación;
- revisión;
- documentación;
- uso como evidencia en la memoria del TFG.

La diferencia principal es:

- **Codex** ofrece un cierre más simple, estable e integrado con el comando estándar.
- **DeepSeek** ofrece un cierre más amplio, documentado y con más cobertura, aunque mantiene una particularidad en la ejecución de tests.

---

# Próximo paso recomendado

Con FASE 11 cerrada para Codex y DeepSeek, el siguiente paso debería ser iniciar la memoria del TFG.

## Propuesta

Crear un documento base:

```text
memoria_tfg_agromanager_borrador.md
```

Con una estructura inicial:

1. Introducción.
2. Objetivos.
3. Contexto y estado del arte.
4. Metodología.
5. Herramientas evaluadas.
6. Descripción del caso práctico AgroManager.
7. Diseño y arquitectura.
8. Desarrollo por fases.
9. Resultados comparativos.
10. Discusión.
11. Problemas encontrados.
12. Conclusiones.
13. Trabajo futuro.
14. Anexos.

---

# Estado del documento

Este documento es provisional porque falta añadir Claude Code FASE 9, FASE 10 y FASE 11.

Cuando Claude esté disponible:

1. Ejecutar FASE 9.
2. Ejecutar FASE 10.
3. Ejecutar FASE 11.
4. Validar build.
5. Validar tests.
6. Validar seed.
7. Validar documentación.
8. Añadir resultados al documento.
9. Convertir este documento de provisional a final.
