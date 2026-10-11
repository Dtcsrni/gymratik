# Día 3 · Pecho + hombro + tríceps · contenido y maquetación

## Estado y objetivo

La rutina canónica se genera en `canonicas/Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html` desde la plantilla visual del Día 1. Presenta una sesión de tren superior con prioridad en pecho, trabajo específico de hombro y dos posiciones de trabajo para tríceps.

La prescripción vigente es de `7` ejercicios y `22` series efectivas: `4 + 3 + 3 + 3 + 3 + 3 + 3`. Las series de aproximación no se contabilizan.

## Prescripción

| # | Ejercicio | Series | Repeticiones | Descanso |
|---:|---|---:|---:|---:|
| 1 | Press de pecho sentado en máquina | 4 | 6–10 | 2–3 min |
| 2 | Press inclinado convergente en máquina | 3 | 8–12 | 2–3 min |
| 3 | Pec deck / contractor de pecho | 3 | 10–15 | 90–120 s |
| 4 | Press de hombro en máquina | 3 | 8–12 | 2 min |
| 5 | Elevación lateral en máquina | 3 | 10–15 | 60–90 s |
| 6 | Jalón de tríceps en polea | 3 | 8–12 | 75–90 s |
| 7 | Extensión de tríceps sobre cabeza con cuerda | 3 | 10–15 | 75–90 s |

La suma es `4 + 3 + 3 + 3 + 3 + 3 + 3 = 22` series efectivas. Se mantiene RIR `1–2` como objetivo operativo y se reduce la carga si se pierde apoyo, alineación o control.

## Preparación y duración

- Cardio moderado: `16 min`, con intensidad conversacional.
- Movilidad y activación de hombros: `2 min`.
- Series de aproximación del primer press: `2` progresivas; no son series efectivas.
- Duración estimada: `83–98 min`; es una estimación operativa, no una medición individual.

## Medios y límites de evidencia

Los siete ejercicios usan recursos locales del inventario `evidencia/dia3_media_manifest.json`. Cada tarjeta separa cuatro roles visuales: vista aislada de la máquina, imagen estática inicial, imagen estática final y GIF del recorrido completo. La clave del press de hombro se corrigió a `2318-dNFYIU1`; las demás son `0577-T0yTjgW`, `1299-jHAnWmT`, `0596-v3xmPAR`, `0584-dRTfGZT`, `0200-dU605di` y `0194-2IxROQ1`.

Las vistas aisladas de máquina (`*-machine-only.webp`) son ediciones visuales basadas en la referencia local: eliminan a la persona del recuadro de máquina y conservan la geometría visible como apoyo, pero no prueban por sí solas la identidad exacta del equipo instalado. Los recursos de movimiento se muestran como demostraciones visuales del patrón y tampoco prueban por sí solos la prescripción ni la superioridad de una máquina. La ficha conserva imágenes estáticas de inicio/final para reducción de movimiento o fallo de carga.

El 2026-10-09 se revisaron los siete pares Inicio/Final y se muestrearon cuatro cuadros de cada uno de los siete GIF. En la PWA local, las siete animaciones también se pausaron con su poster bajo `prefers-reduced-motion` y reanudaron con avance de cuadros. Véanse el [registro por ejercicio](../../docs/05-quality/evidence/pwa-exercise-verification-2026-10-09.md) y los mosaicos de evidencia vinculados allí. Esto no confirma la máquina física ni el despliegue publicado.

## Criterios de aceptación

- El encabezado, resumen, dashboard y progreso reportan `22` series efectivas.
- Existen exactamente `7` tarjetas, con series `4, 3, 3, 3, 3, 3, 3`.
- Cada tarjeta conserva ajuste, ejecución, ritmo, advertencia, contador de series y pareja estática Inicio/Final.
- El recuadro de máquina muestra exclusivamente la máquina, sin persona, y está etiquetado como ilustración de apoyo; no se presenta como confirmación del equipo real.
- Las siete vistas GIF apuntan a los GIF locales verificados y tienen texto alternativo específico.
- El template conserva `warmupTracker`, `sessionGamification` y `resetSession`.
- La rutina no declara identidad exacta del equipo del gimnasio.
- Se ejecutan `python scripts/build_day3_canonical.py`, `python scripts/validate_repository.py`, `python -m py_compile scripts/build_day3_canonical.py` y revisión visual de escritorio/móvil.
