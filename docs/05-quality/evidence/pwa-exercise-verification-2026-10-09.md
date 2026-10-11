# Verificación integral de ejercicios PWA — 2026-10-09

## Resultado

La corrida local terminó en `E2E_ROUTINES_OK`: 4 días, 26 ejercicios y 82 series efectivas. El E2E registró en cada serie preparación mínima, actividad, descanso, contador, clave persistida, repeticiones, carga y duración; también comprobó el indicador visual animado durante actividad y descanso.

El inventario visual encontró 12 tarjetas `STATIC_ONLY` en Días 1–2 y 14 GIF de ejercicio en Días 3–4. Se revisaron 25 parejas Inicio/Final y la guía estática de tres pasos del hip thrust. Para cada uno de los 14 GIF se comprobó pausa en `prefers-reduced-motion`, poster visible y reanudación con avance de cuadros.

## Cobertura por ejercicio

| Día | Ej. | Ejercicio | Series / claves | Medio | Verificación |
|---:|---:|---|---|---|---|
| 1 | 1 | JALÓN AL PECHO | 4 (`e1s1, e1s2, e1s3, e1s4`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 1 | 2 | REMO ALTO UNILATERAL | 4 (`e2s1, e2s2, e2s3, e2s4`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 1 | 3 | REMO HORIZONTAL EN MÁQUINA | 3 (`e3s1, e3s2, e3s3`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 1 | 4 | APERTURA INVERSA EN MÁQUINA | 3 (`e4s1, e4s2, e4s3`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 1 | 5 | CURL DE BÍCEPS EN MÁQUINA | 3 (`e5s1, e5s2, e5s3`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 1 | 6 | CURL DE BÍCEPS SENTADO EN MÁQUINA | 3 (`e6s1, e6s2, e6s3`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 2 | 1 | HACK SQUAT | 3 (`e1s1, e1s2, e1s3`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 2 | 2 | HIP THRUST | 3 (`e2s1, e2s2, e2s3`) | Guía estática 3 pasos | 82-series E2E; guía visual |
| 2 | 3 | PRENSA DE PIERNAS | 3 (`e3s1, e3s2, e3s3`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 2 | 4 | CURL FEMORAL EN MÁQUINA | 4 (`e4s1, e4s2, e4s3, e4s4`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 2 | 5 | EXTENSIÓN DE PIERNAS | 3 (`e5s1, e5s2, e5s3`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 2 | 6 | PANTORRILLAS DE PIE | 4 (`e6s1, e6s2, e6s3, e6s4`) | 2 imágenes estáticas | 82-series E2E; pareja visual |
| 3 | 1 | PRESS DE PECHO SENTADO EN MÁQUINA | 4 (`e1s1, e1s2, e1s3, e1s4`) | GIF local | 82-series E2E; poster y reanudación |
| 3 | 2 | PRESS INCLINADO CONVERGENTE EN MÁQUINA | 3 (`e2s1, e2s2, e2s3`) | GIF local | 82-series E2E; poster y reanudación |
| 3 | 3 | PEC DECK / CONTRACTOR DE PECHO | 3 (`e3s1, e3s2, e3s3`) | GIF local | 82-series E2E; poster y reanudación |
| 3 | 4 | PRESS DE HOMBRO EN MÁQUINA | 3 (`e4s1, e4s2, e4s3`) | GIF local | 82-series E2E; poster y reanudación |
| 3 | 5 | ELEVACIÓN LATERAL EN MÁQUINA | 3 (`e5s1, e5s2, e5s3`) | GIF local | 82-series E2E; poster y reanudación |
| 3 | 6 | JALÓN DE TRÍCEPS EN POLEA | 3 (`e6s1, e6s2, e6s3`) | GIF local | 82-series E2E; poster y reanudación |
| 3 | 7 | EXTENSIÓN DE TRÍCEPS SOBRE CABEZA CON CUERDA | 3 (`e7s1, e7s2, e7s3`) | GIF local | 82-series E2E; poster y reanudación |
| 4 | 1 | PRENSA UNILATERAL ALTERNA | 3 (`e1s1, e1s2, e1s3`) | GIF local | 82-series E2E; poster y reanudación |
| 4 | 2 | PESO MUERTO RUMANO CON BARRA | 3 (`e2s1, e2s2, e2s3`) | GIF local | 82-series E2E; poster y reanudación |
| 4 | 3 | CURL FEMORAL TUMBADO | 4 (`e3s1, e3s2, e3s3, e3s4`) | GIF local | 82-series E2E; poster y reanudación |
| 4 | 4 | ABDUCCIÓN DE CADERA SENTADA | 2 (`e4s1, e4s2`) | GIF local | 82-series E2E; poster y reanudación |
| 4 | 5 | ADUCCIÓN DE CADERA SENTADA | 2 (`e5s1, e5s2`) | GIF local | 82-series E2E; poster y reanudación |
| 4 | 6 | ELEVACIÓN DE PANTORRILLA SENTADA | 3 (`e6s1, e6s2, e6s3`) | GIF local | 82-series E2E; poster y reanudación |
| 4 | 7 | CRUNCH CON ELEVACIÓN DE PIERNAS SENTADA | 3 (`e7s1, e7s2, e7s3`) | GIF local | 82-series E2E; poster y reanudación |

## Evidencia y comandos

- [Registro por ejercicio y serie en JSON](pwa-exercise-verification-2026-10-09.json).
- [Mosaico de parejas Inicio/Final](routine-phase-pairs-2026-10-09.jpg).
- [Mosaico de 14 GIF, cuatro cuadros por GIF](routine-exercise-gifs-2026-10-09.jpg).

Comandos ejecutados: `python scripts/validate_repository.py`, `python scripts/validate_canonical_routines.py`, `python scripts/validate_routine_media.py`, `python -m unittest tests.routines.test_canonical_routines tests.routines.test_routine_media tests.routines.test_battery_motion tests.routines.test_day2_hip_thrust_visuals`, `python scripts/e2e_routine_activity_check.py --functional-only` y `python scripts/e2e_routine_activity_check.py --resources-only`.

La suite del repositorio ejecutó 212 pruebas con resultado `OK`; se excluyó
una prueba de inventario que queda bloqueada al crear el loop de Playwright en
Windows/Python 3.14 (`asyncio._make_self_pipe`, antes del navegador). El
recorrido de recursos E2E completó la misma inspección en Edge local.

Los cinco generadores (cuatro rutinas y Service Worker) se ejecutaron dos veces;
las salidas de las dos pasadas consecutivas fueron idénticas. La prueba nueva
de idempotencia del normalizador también pasa para los cuatro días.

## Límites

La evidencia corresponde a Edge/Playwright local con datos sintéticos. No confirma ejecución en el Realme GT 6 instalado ni en el despliegue público. La inspección visual confirma el patrón mostrado en los cuadros revisados, pero no identifica el modelo exacto del equipo físico ni valida clínicamente la prescripción.
