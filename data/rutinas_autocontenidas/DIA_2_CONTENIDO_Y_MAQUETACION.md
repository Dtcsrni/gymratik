# Día 2 · Pierna + Glúteo · contenido y maquetación

## Estado y objetivo

La versión canónica es `canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html`. Su objetivo es presentar una sesión de tren inferior para un adulto sano con prioridad práctica en máquinas, 20 series efectivas, instrucciones visuales y progresión reproducible.

La prioridad de máquinas es una restricción y preferencia de diseño: favorece estabilidad, disponibilidad y registro de carga. El hip thrust se presenta en máquina, de acuerdo con la referencia de equipo y la secuencia de fases de la fuente local. No se presenta la selección como superioridad fisiológica universal frente al peso libre.

La maquetación hereda directamente la plantilla canónica vigente del Día 1: cabecera de sesión, guía rápida, calentamiento visual, seguimiento del calentamiento, resumen de sesión, progreso de las 20 series, tarjetas de ejercicio, reglas de ejecución y reinicio de sesión. El builder toma el HTML del Día 1 como `TEMPLATE` para evitar una segunda plantilla divergente.

## Prescripción aprobada

| # | Ejercicio | Series | Repeticiones | Descanso | Función principal |
|---:|---|---:|---:|---:|---|
| 1 | Hack squat | 3 | 6–8 | 3 min | Sentadilla guiada; cuádriceps y glúteo |
| 2 | Hip thrust en máquina | 3 | 6–10 | 2.5–3 min | Extensión de cadera; glúteo mayor |
| 3 | Prensa de piernas | 3 | 8–12 | 2–3 min | Extensión de rodilla y cadera |
| 4 | Curl femoral en máquina | 4 | 8–12 | 2 min | Flexión de rodilla; isquiosurales |
| 5 | Extensión de piernas | 3 | 10–15 | 90–120 s | Extensión de rodilla; cuádriceps |
| 6 | Pantorrillas de pie | 4 | 8–12 | 90–120 s | Flexión plantar; gastrocnemio y sóleo |

La suma es `3 + 3 + 3 + 4 + 3 + 4 = 20` series efectivas. Las series de aproximación no se contabilizan. El cuarto set se asigna al curl femoral para mejorar la cobertura directa de isquiosurales sin añadir otra serie pesada a hack squat o prensa.

## Criterio científico aplicado

- La revisión de posición de **ACSM 2026** sintetiza 137 revisiones y respalda que el entrenamiento de resistencia mejora la hipertrofia; el volumen mayor suele ayudar con rendimientos decrecientes, el rango completo es útil y no hay un efecto consistente del tipo de equipo sobre la hipertrofia.
- La metarregresión de **Pelland et al. 2026** respalda una relación positiva entre volumen y masa muscular, con rendimientos decrecientes; las series indirectas deben contarse con cautela.
- La revisión de **Robinson et al. 2024** indica que la hipertrofia tiende a aumentar al terminar más cerca del fallo, pero no convierte el fallo momentáneo en requisito. Por eso se usa RIR 2–3 al inicio y RIR 1–2 al final o en aislamientos.
- La revisión de **Singer et al. 2024** sugiere una pequeña ventaja de descansos mayores de 60 s y no detecta una ventaja apreciable al superar aproximadamente 90 s de forma general; los compuestos pesados conservan descansos más largos para proteger el rendimiento.
- La revisión de **Nunes et al. 2021** no encontró diferencia consistente de hipertrofia por orden, pero el ejercicio prioritario se coloca primero para proteger el rendimiento agudo.

Fuentes primarias de síntesis: [ACSM 2026](https://pubmed.ncbi.nlm.nih.gov/41843416/), [Pelland et al. 2026](https://pubmed.ncbi.nlm.nih.gov/41343037/), [Robinson et al. 2024](https://pubmed.ncbi.nlm.nih.gov/38970765/), [Singer et al. 2024](https://pubmed.ncbi.nlm.nih.gov/39205815/) y [Nunes et al. 2021](https://pubmed.ncbi.nlm.nih.gov/32077380/).

## Calentamiento y duración

- Cardio suave: `5–8 min`, intensidad conversacional.
- Movilidad dinámica: `3–5 min`, cadera, rodilla y tobillo, sin dolor ni rebotes.
- Aproximación: `2–3 series` progresivas antes del primer ejercicio pesado; no son series efectivas.
- Duración operativa: `65–85 min` como estimación, calculada a partir de 8–13 min de preparación, aproximadamente 49–59 min de trabajo y descansos, y 8–13 min de transiciones/ajustes. Es una estimación, no una medición individual.

## Reglas de progresión y seguridad

Completa el extremo alto del rango en todas las series con técnica estable y RIR objetivo; después aumenta ligeramente la carga y vuelve al extremo bajo. Si el apoyo, la alineación o el control pélvico se deterioran, reduce la carga o aumenta el descanso. Dolor agudo, síntomas neurológicos, respiratorios o cardiovasculares, o pérdida clara de función requieren detener la sesión y buscar valoración apropiada.

## Medios y límites de evidencia

La salida canónica actual ofrece cinco parejas estáticas Inicio/Final y una guía estática de tres pasos para el hip thrust. Las seis tarjetas declaran `data-media-mode="STATIC_ONLY"`; no integran los GIF candidatos de ejercicio que aparecen en el manifiesto histórico. El hip thrust conserva una referencia visual de máquina y una liga opcional a la demostración oficial `CORRECT FORM`; la tarjeta no promete un GIF local. La guía indica apoyo de espalda y cabeza, pies firmes, ajuste del rodillo y flexión/extensión controlada. No se muestra el panel `INCORRECT FORM`.

Los GIFs de ejercicio registrados en `evidencia/dia2_media_manifest.json` son candidatos históricos y no forman parte del render canónico. El calentamiento tiene su propio visor GIF, separado de las tarjetas. La auditoría visual del 9 de octubre verificó las cinco parejas y la guía de hip thrust; la secuencia está en [la evidencia visual](../../docs/05-quality/evidence/routine-phase-pairs-2026-10-09.jpg).

El visor de calentamiento conserva sus GIF y miniaturas estáticas. La E2E valida la preferencia de movimiento reducido para todos los GIF de técnica existentes en los Días 3 y 4, además de las pausas y reanudaciones del visor de calentamiento. La procedencia individual de algunas imágenes embebidas permanece pendiente.

## Criterios de aceptación

- El encabezado y dashboard muestran exactamente `20 series efectivas`.
- Las métricas de tarjetas muestran `3, 3, 3, 4, 3, 4` series.
- La cabecera, guía rápida, calentamiento, resumen, tarjetas y cierre siguen la jerarquía del Día 1.
- El seguimiento del calentamiento y el progreso de sesión están presentes y conservan los identificadores funcionales del template (`warmupTracker`, `sessionGamification`, `resetSession`).
- El hip thrust se identifica como ejercicio en máquina; su referencia de equipo y guía no mezclan imágenes de barra.
- Las seis tarjetas declaran `STATIC_ONLY`, tienen cinco parejas Inicio/Final y un caso `hipThrustGuide` de tres pasos.
- Ningún GIF de ejercicio se carga desde estas tarjetas; los GIF del calentamiento se documentan y validan por separado.
- La ficha conserva alternativas, RIR, progresión, señales de detención y límites de evidencia.
- Se ejecuta `python scripts/validate_repository.py` y se revisa el render en escritorio y móvil.
