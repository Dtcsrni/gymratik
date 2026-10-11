# Día 4 · Pierna equilibrada · contenido y maquetación

## Estado y objetivo

La salida canónica es `canonicas/Rutina_Dia_4_Pierna_Equilibrio_V1.html` y se
genera con `scripts/build_day4_canonical.py` desde la plantilla compartida del
Día 1. Presenta una sesión de tren inferior con prioridad práctica en máquinas,
20 series efectivas y siete patrones diferenciados: rodilla unilateral, bisagra
de cadera, flexión de rodilla, abductores, aductores, pantorrilla y core.

La prioridad de máquinas es una preferencia de estabilidad, ajuste y registro;
no es una afirmación de superioridad fisiológica universal. La disponibilidad y
la identidad de cada estación deben confirmarse en el gimnasio antes de usarla.

## Prescripción

| # | Ejercicio | Series | Repeticiones | Descanso | Función principal |
|---:|---|---:|---:|---:|---|
| 1 | Prensa unilateral alterna | 3 | 8–12 por lado | 2–3 min | Extensión de rodilla y cadera; cuádriceps |
| 2 | Peso muerto rumano con barra | 3 | 8–12 | 2–3 min | Bisagra de cadera; glúteos e isquiosurales |
| 3 | Curl femoral tumbado | 4 | 8–12 | 90–120 s | Flexión de rodilla; isquiosurales |
| 4 | Abducción de cadera sentada | 2 | 12–20 | 60–90 s | Abductores y glúteo medio |
| 5 | Aducción de cadera sentada | 2 | 12–20 | 60–90 s | Aductores |
| 6 | Elevación de pantorrilla sentada | 3 | 10–15 | 60–90 s | Flexión plantar; tríceps sural |
| 7 | Crunch con elevación de piernas sentada | 3 | 10–15 | 60–90 s | Flexión controlada del tronco; abdominales |

La suma es `3 + 3 + 4 + 2 + 2 + 3 + 3 = 20` series efectivas. Las series de
aproximación y el calentamiento no forman parte del total ni de las claves
persistidas.

## Criterio científico aplicado

- La posición de ACSM 2026 sintetiza 137 revisiones y más de 30,000
  participantes. Reporta beneficios de la progresión, mayor hipertrofia con
  volúmenes mayores y ausencia de un efecto consistente del tipo de equipo; por
  eso aquí se prioriza la reproducibilidad práctica, no una superioridad de la
  máquina.
- Pelland et al. 2026 encontró una relación positiva entre volumen y tamaño
  muscular con rendimientos decrecientes; la frecuencia mostró efectos menos
  consistentes para hipertrofia. La rutina mantiene un volumen fijo y deja la
  frecuencia para la programación semanal completa.
- Una revisión y metaanálisis de glúteo mayor respalda que distintos ejercicios
  de extensión de cadera pueden producir hipertrofia; no demuestra que este
  orden ni una máquina concreta sea universalmente superior.
- En un ensayo de 12 semanas, el curl sentado produjo más crecimiento de
  isquiosurales que el tumbado. El Día 4 conserva el curl tumbado por
  disponibilidad y continuidad con el inventario visual; la sustitución por
  curl sentado es una alternativa razonable si existe y se ajusta bien.

Fuentes primarias de síntesis y estudios pertinentes: [ACSM 2026](https://pubmed.ncbi.nlm.nih.gov/41843416/), [Pelland et al. 2026](https://pubmed.ncbi.nlm.nih.gov/41343037/), [Krause Neto et al. 2025](https://pubmed.ncbi.nlm.nih.gov/40276368/) y [Ma et al. 2021](https://pubmed.ncbi.nlm.nih.gov/33009197/).

## Preparación, progresión y duración

- Cardio suave: `5–8 min`, intensidad conversacional.
- Movilidad dinámica: `3–5 min`, cadera, rodilla y tobillo, sin dolor ni rebotes.
- Aproximación: `2–3` series progresivas antes del primer ejercicio pesado; no
  son series efectivas.
- RIR operativo: `2–3` al inicio de la sesión y `1–2` en las últimas series si
  la técnica permanece estable; no se exige fallo momentáneo.
- Duración estimada: `75–90 min`, calculada desde la preparación, 20 series,
  descansos y ajustes. Es una estimación, no una medición individual.

Completa el extremo alto del rango en todas las series con técnica y rango
estables; después aumenta ligeramente la carga y vuelve al extremo bajo. Si la
pelvis, la alineación de rodilla, el apoyo o el control del tronco se deterioran,
reduce carga o aumenta el descanso. Dolor agudo, síntomas neurológicos,
respiratorios o cardiovasculares requieren detener la sesión y buscar valoración
apropiada.

## Medios y límites de evidencia

Cada tarjeta separa referencia visual del patrón, posición inicial, posición
final y GIF local. Los siete GIFs corresponden nominalmente al ejercicio elegido
en el repositorio local `ejercicios-compartido`; sus dimensiones, hashes, cuadros
y rutas publicadas están en `evidencia/dia4_media_manifest.json`. La revisión
visual registrada es `LOOP_AND_FRAME_REVIEWED_LOCAL`: se verificaron los siete
bucles y sus cuadros inicial/final contra el patrón mostrado. No es una
certificación clínica ni una prueba de que exista la máquina exacta en el
gimnasio.

La revisión integral del 9 de octubre de 2026 confirmó los siete pares Inicio/Final,
los siete GIF y los cambios visibles entre fotogramas. El caso por ejercicio está
en [la evidencia visual](../../docs/05-quality/evidence/routine-phase-pairs-2026-10-09.jpg)
y [la secuencia GIF](../../docs/05-quality/evidence/routine-exercise-gifs-2026-10-09.jpg).
Los cuadros de inicio sirven como póster estático cuando se prefiere movimiento
reducido o falla el GIF; la E2E comprueba pausa, póster y reanudación por tarjeta.
Los medios conservan estado `CANDIDATES_PENDING_LICENSE_REVIEW`; no se presenta
ninguna licencia ni permiso de redistribución como confirmado.

## Criterios de aceptación

- Encabezado, resumen, dashboard, progreso y tarjetas reportan `20` series.
- Existen exactamente `7` tarjetas con distribución `3, 3, 4, 2, 2, 3, 3`.
- Cada tarjeta conserva ajuste, ejecución, ritmo, advertencia, contador,
  pareja Inicio/Final, GIF, fallback y texto alternativo específico.
- El calentamiento es visible y debe finalizarse antes de registrar las series.
- La salida no declara identidad exacta del equipo del gimnasio ni aprobación de
  derechos de los medios.
- Se ejecutan el builder, `python scripts/validate_repository.py`, los
  validadores canónicos/media, pruebas automatizadas y revisión visual de
  escritorio y móvil.
