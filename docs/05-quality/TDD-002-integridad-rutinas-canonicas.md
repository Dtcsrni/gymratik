# TDD-002 — Integridad semántica de rutinas canónicas

**Estado:** `Verified (local synthetic; physical/public pending)`
**Versión:** `0.6`
**Fecha de verificación:** `2026-10-28`
**Diseño asociado:** [SDD-001](../03-architecture/SDD-001-rutina-canonica-versionado.md)

## 1. Objetivo

Detectar automáticamente inconsistencias entre el contenido declarado y las
las HTML canónicas, especialmente las que no detectan los checks actuales del
repositorio: tarjetas ausentes, índices discontinuos, claves incompletas y
totales falsos.

## 2. Sistema bajo prueba

| Día | Archivo | Contrato declarado |
|---|---|---|
| 1 | `data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html` | 7 ejercicios; 23 series; `4 + 4 + 3 + 3 + 3 + 3 + 3` (contenido v3) |
| 2 | `data/rutinas_autocontenidas/canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html` | 7 ejercicios; 23 series; `3 + 3 + 3 + 4 + 4 + 3 + 3` (contenido v3) |
| 3 | `data/rutinas_autocontenidas/canonicas/Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html` | 7 ejercicios; 22 series; `4 + 3 + 3 + 3 + 3 + 3 + 3` (contenido v3) |
| 4 | `data/rutinas_autocontenidas/canonicas/Rutina_Dia_4_Pierna_Equilibrio_V1.html` | 7 ejercicios; 22 series; `3 + 3 + 4 + 3 + 3 + 3 + 3` (contenido v3, opcional) |

El contrato del plan v3 debe mantenerse explícito: todo cambio de distribución,
equipo o rango requiere actualizar SRS, SDD-001, salida y trazabilidad en el mismo cambio.

## 3. Casos de prueba

### TST-CAN-001 — Conteo e índices

**Preparación:** leer cada HTML sin ejecutar scripts y localizar tarjetas con
`data-exercise`.

**Comprobaciones:**

- cantidad de tarjetas igual a `exerciseCount`;
- índices únicos y exactamente contiguos;
- ningún ejercicio declarado desaparece del DOM canónico;
- cada tarjeta tiene título, métricas y tracker.

**Resultado esperado:** las cuatro salidas deben superar este caso; las
mutaciones sintéticas deben producir un fallo localizado.

### TST-CAN-002 — Suma de series efectivas

**Preparación:** extraer `data-series-keys` por tarjeta y contar las claves.

**Comprobaciones:**

- cada conjunto tiene claves `e{index}s1..e{index}sN`;
- la suma coincide con el total declarado;
- la distribución coincide con dashboard, resumen y documento del día;
- `warmupSet` no se suma como serie efectiva.

**Resultado esperado:** ningún total depende solo de texto visible; cualquier
discrepancia produce ubicación de archivo, ejercicio y valor esperado/real.

### TST-CAN-003 — Navegación sucesiva

**Preparación:** extraer cada `nextExerciseCue`, `data-next` y etiqueta visible.

**Comprobaciones:**

- tarjeta `i` apunta a `i + 1` cuando no es la última;
- la etiqueta del botón coincide con el título de la tarjeta `i + 1`;
- la última tarjeta muestra finalización y no un siguiente inexistente;
- no se permiten índices 0, repetidos o fuera del rango.

**Resultado esperado:** cualquier botón que no apunte al título siguiente se
reporta indicando el índice, etiqueta y valor esperado.

### TST-CAN-004 — Layout compartido

**Preparación:** leer cada HTML canónica sin ejecutar scripts y localizar el
contenedor de tarjetas, los índices de tarjeta y el footer de acciones.

**Comprobaciones:**

- existe exactamente un `<main class="cards">`;
- las tarjetas declaran `data-exercise-index="1..N"` sin huecos;
- existe exactamente un `<footer class="sessionFooter">`;
- no se conserva un footer alternativo de la fuente local.

**Resultado esperado:** las cuatro salidas tienen la misma estructura de página y
solo difieren en prescripción, contenido visual y contrato específico del día.

### TST-CAN-006 — Prescripción y equipo

**Preparación:** validar cada tarjeta de las cuatro salidas canónicas v3.

**Comprobaciones:** días 1–3 suman 21–24 series (68 total); día 4 opcional suma 22 (90 si se realizan los cuatro); ninguna rutina supera 7 ejercicios; cada ejercicio tiene al menos 3 series y declara 8–12 repeticiones; Día 4 usa peso muerto rumano en Smith; el HTML declara `data-routine-content-version="3"`. La portada rota solo por los tres días base y permite continuar una sesión activa del opcional. El E2E funcional ejecuta cada serie efectiva. Las cargas del selector son orientativas hasta identificar el modelo físico exacto.

### TST-CAN-007 — Contador de ejercicios en estado de sesión

**Preparación:** abrir cada rutina canónica en un contexto de navegador limpio.

**Comprobaciones:** el contador flotante inicia en `0/7 ejercicios`, muestra el
total de series del día y permanece sincronizado con las siete tarjetas. El E2E
rechaza el texto inicial `0/6 ejercicios` o cualquier denominador distinto del
número de ejercicios activo.

**Evidencia 2026-10-28:** el comando
`python scripts/e2e_routine_activity_check.py --functional-only` terminó con
`E2E_ROUTINES_OK`: cuatro días, siete ejercicios por día y 90/90 series
efectivas completadas. Se verificaron formato uniforme, carga manual/Enter y
celebración de sesión. El resumen está en
[routine-v3-e2e-2026-10-28.json](evidence/routine-v3-e2e-2026-10-28.json).

### TST-CAN-005 — Contexto y prioridad de registro en móvil

**Preparación:** abrir las cuatro salidas canónicas en un viewport móvil y
examinar una tarjeta por ejercicio.

**Comprobaciones:**

- cada salida contiene exactamente un desplegable nativo de contexto, cerrado
  por defecto, que contiene objetivo y grupos musculares;
- cada tarjeta conserva título, métricas, contador, referencias visuales y
  técnica; en móvil los controles preceden a las referencias sin cambiar el
  diseño de escritorio;
- el resumen del desplegable mantiene foco visible y activación por teclado;
- no hay desbordamiento horizontal a 320, 360, 390 o 412 px.

**Resultado esperado:** todas las salidas cumplen el mismo contrato de
presentación y mantienen sus series, selectores y estados persistidos.

## 4. Casos negativos y de frontera

- HTML sin tarjetas.
- Dos tarjetas con el mismo `data-exercise`.
- Salto de índice, por ejemplo 2 → 4.
- `data-series-keys` vacío, duplicado o con `s0`.
- Total declarado distinto de la suma.
- Calentamiento contado como serie efectiva.
- Última tarjeta con `data-next`.
- Texto del dashboard con total correcto pero trackers incompletos.
- Atributo presente en una tarjeta y ausente en otra.

## 5. Implementación

El validador de solo lectura es
`scripts/validate_canonical_routines.py` y usa el parser HTML de la biblioteca
estándar o una estrategia equivalente estable. Debe:

1. recibir rutas explícitas o usar las cuatro canónicas por defecto;
2. emitir errores estructurados con archivo, ejercicio, atributo, esperado y
   observado;
3. devolver código distinto de cero ante cualquier discrepancia;
4. no modificar HTML, documentos, manifiestos ni artefactos;
5. poder ejecutarse desde PowerShell y desde una prueba Python; y
6. evitar volcar imágenes embebidas o contenido base64 en la salida.

Comando de ejecución sobre las cuatro salidas:

```powershell
python scripts/validate_canonical_routines.py
```

También acepta rutas explícitas para aislar un día durante el diagnóstico.

La prueba se mantiene separada del validador general; las mutaciones negativas
siguen siendo evidencia explícita y no se ocultan cambiando el esperado.

## 6. Evidencia requerida

- salida del validador con versión de Python y rutas revisadas;
- prueba de que el caso falla ante una mutación sintética de cada invariante;
- salida posterior sin discrepancias tras corregir el contenido;
- `python scripts/validate_repository.py` y `git diff --check`;
- revisión visual independiente para confirmar que el DOM corregido se ve y
  navega correctamente.

La prueba automatizada demuestra estructura y aritmética; no demuestra por sí
sola técnica de ejercicio, exactitud del equipo, experiencia de usuario ni
validez científica de la prescripción.

### Resultado ejecutado — 2026-10-09

- `validate_canonical_routines.py`: `CANONICAL_ROUTINES_OK routines=4`.
- Contratos: Día 1 `6/20 (4+4+3+3+3+3)`; Día 2 `6/20
  (3+3+3+4+3+4)`; Día 3 `7/22 (4+3+3+3+3+3+3)`; Día 4 `7/20
  (3+3+4+2+2+3+3)`.
- Pruebas de corrupción e invariantes: batería focalizada aprobada.
- Recorrido E2E local: 26 ejercicios y 82/82 series completadas con
  persistencia de clave, repeticiones, carga y duración; véase el
  [registro por ejercicio y serie](evidence/pwa-exercise-verification-2026-10-09.json).
- La ejecución es navegador local sintético; no certifica el Realme GT 6 ni
  el despliegue público.

### Resultado de UX compartida — 2026-10-26

- `validate_canonical_routines.py`: `CANONICAL_ROUTINES_OK routines=4`.
- `validate_routine_media.py`: `ROUTINE_MEDIA_OK routines=4`.
- `validate_repository.py`: `VALIDATION_OK markdown=84`.
- Contrato estático TST-CAN-005: desplegable/contexto y orden móvil comunes a
  los cuatro días; capturas sintéticas de cabecera, tarjeta y cierre para cada
  día en [auditoría de UX](evidence/ux-audit-2026-10-26/README.md).
- Pruebas unitarias focalizadas: 3 aprobadas.
- El E2E interactivo responsive no se registra como aprobado: el proceso se
  detiene en `sync_playwright().start()` antes de iniciar Edge o recorrer los
  días. El caso de interacción por teclado y matriz de anchuras queda pendiente
  de repetirse cuando el driver Playwright responda.

### Resultado ejecutado — 2026-10-27

- `python -m unittest tests.test_homepage tests.test_service_worker tests.routines.test_canonical_routines -q`: 127 pruebas aprobadas.
- `python scripts/validate_canonical_routines.py`: `CANONICAL_ROUTINES_OK routines=4`.
- `python scripts/validate_routine_media.py`: `ROUTINE_MEDIA_OK routines=4`.
- `python scripts/e2e_routine_activity_check.py --functional-only`: `E2E_ROUTINES_OK`, cuatro días, 35 ejercicios y 112/112 series efectivas. Se verificaron formato, carga/repeticiones, Enter, aproximación, descanso, omisión/deshacer, celebración, persistencia semanal y pausado/reanudación de GIF.
- Resumen ligero por día en [evidencia E2E v2](evidence/routine-v2-e2e-2026-10-27.json); no se guardaron capturas.
- Ejecución sintética aislada en Edge headless; el dispositivo físico, despliegue público, matriz responsive completa y offline profundo siguen fuera de esta comprobación. La duración 95–115 min es estimada, no medida.

## 7. Criterio de cierre

El criterio funcional v2 queda satisfecho con el E2E sintético de los cuatro días y todas sus series efectivas. La validación en el dispositivo instalado y en el despliegue público pertenece a TDD-005 y sigue separada de esta evidencia.
