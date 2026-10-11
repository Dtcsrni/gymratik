# Identificadores heredados fuera del alcance activo

Este registro conserva referencias encontradas en documentos históricos, ADR y notas de diseño. Los elementos aquí listados están **diferidos**, no son requisitos del SRS vigente, no forman parte del backlog de la PWA y no autorizan implementación. Si se retoman, requieren una decisión de alcance y requisitos nuevos o reactivados con criterios verificables.

## Investigaciones heredadas

- **SPIKE-001:** viabilidad del Amazfit Active.
- **SPIKE-002:** acceso privado a Tezkatli desde una red móvil.
- **SPIKE-003:** capacidad de inferencia del equipo Tezkatli.
- **SPIKE-004:** error de estimación de porciones.
- **SPIKE-005:** persistencia Room/outbox tras cierre de proceso.
- **SPIKE-006:** utilidad y batería de la detección de gimnasio.

## Entrenamiento genérico y edición de rutinas

- **FUN-TRN-001 · P0:** sesiones genéricas con pausa, reanudación y cierre propios de la app Android.
- **FUN-TRN-002 · P0:** fases de cardio y fuerza configurables para el sistema Android.
- **FUN-TRN-003 · P0:** registro genérico de series con RIR/RPE, tipo y marca temporal.
- **FUN-TRN-004 · P0:** objetivos y valores anteriores según variante/equipo.
- **FUN-TRN-005 · P0:** auditoría de correcciones de series.
- **FUN-TRN-006 · P0:** temporizador configurable por ejercicio/serie y ciclo de vida Android.
- **FUN-TRN-007 · P1:** soporte genérico de calentamiento, drop set, fallo y asistencia.
- **FUN-TRN-008 · P1:** cálculo general de discos y calentamientos.
- **FUN-TRN-009 · P1:** detección general de récords con fórmula versionada.
- **FUN-ROU-001 · P0:** CRUD, clonación y versionado de rutinas personalizadas.
- **FUN-ROU-002 · P1:** recomendación de rutinas por objetivo, tiempo, historial y equipo.
- **FUN-ROU-003 · P1:** explicación y alternativas de rutinas recomendadas.
- **FUN-ROU-004 · P1:** preferencias y exclusiones configurables de ejercicios.

## Gimnasio, nutrición y suplementos

- **FUN-GYM-001 · P1:** detección de llegada al gimnasio.
- **FUN-GYM-002 · P0:** catálogo versionado de máquinas y verificación de equipo.
- **FUN-GYM-003 · P1:** disponibilidad temporal de máquinas.
- **FUN-NUT-001 · P0:** diario de alimentos con texto, códigos, OCR o fotografía.
- **FUN-NUT-002 · P0:** borradores de alimento inferido con confirmación humana.
- **FUN-NUT-003 · P0:** procedencia de mediciones y estimaciones de alimento.
- **FUN-NUT-004 · P0:** trazabilidad de catálogos de alimentos.
- **FUN-NUT-005 · P0:** edición de componentes antes de confirmar comidas.
- **FUN-NUT-006 · P1:** recetas, rendimiento y porciones.
- **FUN-NUT-007 · P1:** reutilización de comidas y porciones personales.
- **FUN-NUT-008 · P1:** captura de alimento con varias vistas o referencia geométrica.
- **FUN-NUT-009 · P1:** detección de posibles ingredientes ocultos.
- **FUN-SUP-001 · P0:** registro de producto, dosis y hora de suplemento.
- **FUN-SUP-002 · P0:** confirmación y corrección de ingestas.
- **FUN-SUP-003 · P1:** inventario y reposición de suplementos.
- **FUN-SUP-004 · P1:** captura de etiqueta de suplemento.
- **FUN-SUP-005 · P0:** salvaguarda contra prescripción automática de suplementos.

## IA e integraciones

- **FUN-AI-001 · P0:** inferencia en teléfono o Tezkatli.
- **FUN-AI-002 · P0:** procedencia reproducible de trabajos de inferencia.
- **FUN-AI-003 · P0:** validación de salidas de IA contra esquema.
- **FUN-AI-004 · P0:** cola de inferencia y entrada manual si falta Tezkatli.
- **FUN-AI-005 · P1:** reutilización de correcciones personales.
- **FUN-AI-006 · P1:** evaluación y aprobación de modelos.
- **FUN-WEA-001 · P1:** interfaz del reloj para ejercicio/serie.
- **FUN-WEA-002 · P1:** persistencia de eventos hasta ACK del reloj.
- **FUN-WEA-003 · P1:** identidad, secuencia y procedencia de eventos del reloj.
- **FUN-WEA-004 · P0:** límites de precisión de repeticiones automáticas del reloj.
- **FUN-HC-001 · P1:** importación desde Health Connect.
- **FUN-HC-002 · P1:** exportación de sesiones a Health Connect.

## Sincronización y respaldo de servicio

- **FUN-SYN-001 · P0:** operación offline de Android y sincronización posterior de varios dominios.
- **FUN-SYN-002 · P0:** sincronización idempotente tolerante a duplicación y reordenamiento.
- **FUN-SYN-003 · P0:** outbox y visualización de trabajos remotos pendientes.
- **FUN-SYN-004 · P1:** tombstones para borrados sincronizados.
- **FUN-EXP-001 · P0:** respaldo general de datos/servicios fuera del archivo local v3 de la PWA.
- **FUN-EXP-002 · P0:** restauración de servicios y bases externas.

## Requisitos no funcionales heredados

- **NFR-PER-001 · P0:** latencia objetivo para persistencia en Realme GT 6.
- **NFR-PER-002 · P0:** objetivo de TTFD para sesión Android.
- **NFR-PER-003 · P1:** no bloquear UI durante IA/sincronización Android.
- **NFR-EFF-001 · P1:** consumo de batería de ubicación y sincronización Android.
- **NFR-SEC-001 · P0:** exposición de Tezkatli a Internet.
- **NFR-MAI-001 · P0:** ciclos entre módulos Gradle Android.
- **NFR-AI-001 · P0:** límites de escritura de IA sobre datos confirmados.
- **NFR-AI-002 · P0:** reporte de métricas/datasets de IA.
- **NFR-AI-003 · P1:** presentación de incertidumbre de IA.
