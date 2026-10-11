# SDD-001 — Modelo de rutina canónica y versionado

**Estado:** `Verified (local PWA)`
**Versión:** `0.2`
**Fecha de verificación:** `2026-10-09`
**TDD asociado:** [TDD-002](../05-quality/TDD-002-integridad-rutinas-canonicas.md)

## 1. Objetivo

Fijar un modelo único para que el contenido de una rutina, su HTML canónico y
el contador interactivo representen el mismo número de ejercicios y series
efectivas. El diseño evita que un encabezado o dashboard correcto oculte una
salida incompleta.

## 2. Alcance

Incluye Día 1, Día 2, Día 3 y Día 4, sus documentos de contenido, las HTML bajo
`data/rutinas_autocontenidas/canonicas/` y los builders que producen salidas
canónicas. Incluye calentamiento, series de aproximación, ejercicios,
distribución, orden y versión.

No incluye la corrección de los archivos en este SDD ni la evaluación científica
de la prescripción. La evidencia científica sigue gobernada por
`docs/09-research/EVIDENCE_BASE_AND_ROUTINE_PROTOCOL.md`.

## 3. Modelo lógico

La representación mínima que debe poder reconstruirse desde una rutina es:

```text
CanonicalRoutine
├─ routineId             # entrenamiento-day{N}-series-v{V}
├─ dayNumber
├─ routineVersion
├─ title
├─ exerciseCount
├─ effectiveSeriesTotal
├─ effectiveSeriesDistribution[]
├─ warmup                  # no forma parte del total efectivo
└─ exercises[]
   ├─ exerciseIndex        # 1..exerciseCount, sin huecos
   ├─ exerciseId/title
   ├─ equipmentDescription
   ├─ effectiveSeries
   ├─ seriesKeys[]         # e{exerciseIndex}s1..e{exerciseIndex}sN
   ├─ repetitions
   ├─ rest
   └─ technicalGuidance
```

El HTML es una proyección de este modelo. No se debe corregir el total solo en
el resumen: el contenido, las tarjetas, las claves y el dashboard deben
cambiar juntos.

## 4. Invariantes obligatorias

Para cada rutina canónica:

1. `exerciseCount = len(exercises)`.
2. Los índices de ejercicio son exactamente `1..exerciseCount`.
3. `effectiveSeriesTotal = sum(effectiveSeries por ejercicio)`.
4. Cada ejercicio tiene exactamente `effectiveSeries` claves únicas y
   contiguas: `e{index}s1` hasta `e{index}s{N}`.
5. El calentamiento y las series de aproximación no aparecen en
   `effectiveSeriesTotal` ni en las claves efectivas.
6. El título, el resumen, el dashboard, el progreso global y las tarjetas
   muestran el mismo total y distribución.
7. La última tarjeta no ofrece un índice siguiente; las anteriores apuntan a
   `exerciseIndex + 1`.
8. Una rutina no mezcla en una misma salida los identificadores de otra rutina,
   día o versión.
9. Las cuatro salidas comparten un único `main.cards`, un `data-exercise-index`
   contiguo por tarjeta y un único `sessionFooter`; las diferencias de contenido
   no deben crear una segunda variante de layout.

## 5. Fuente y flujo de construcción

```text
DIA_{N}_CONTENIDO_Y_MAQUETACION.md
             │
             ├─ prescripción y distribución
             └─ criterios de presentación
                      │
                      ▼
             builder determinista
                      │
                      ▼
             HTML canónico V{N}
                      │
             TDD-002 / TDD-005
                      ▼
              PWA y revisión visual
```

La plantilla visual del Día 1 sigue siendo la base compartida declarada en
`data/rutinas_autocontenidas/README.md`, pero debe tratarse como una plantilla
con contrato estructural, no como una copia que pueda propagar silenciosamente
tarjetas faltantes, footers alternativos o referencias obsoletas.

## 6. Versionado y compatibilidad

- Un cambio de ejercicio, orden, cantidad de series, rango o comportamiento
  incrementa `routineVersion`.
- Un cambio puramente editorial puede conservar versión solo si no modifica
  estructura, semántica ni comportamiento; debe quedar registrado en el
  changelog del documento de contenido.
- Los IDs persistidos de series deben ser estables dentro de una versión.
- Una migración entre versiones debe declarar qué series se conservan,
  sustituyen o quedan obsoletas; nunca debe reasignar silenciosamente una serie
  histórica a otro ejercicio.

Estas reglas son propuestas de diseño hasta que exista persistencia Android.
La implementación futura debe convertirlas en un contrato versionado.

## 7. Estado actual y discrepancias conocidas

La inspección del estado actual confirmó:

- Día 1 conserva seis ejercicios y la distribución `4 + 4 + 3 + 3 + 3 + 3`.
- Día 2 conserva seis ejercicios y la distribución `3 + 3 + 3 + 4 + 3 + 4`.
- Día 3 conserva siete ejercicios y la distribución `4 + 3 + 3 + 3 + 3 + 3 + 3`.
- Día 4 conserva siete ejercicios y la distribución `3 + 3 + 4 + 2 + 2 + 3 + 3`.

Las cuatro salidas canónicas superaron TDD-002 el 2026-10-09. La evidencia de
conteo, series y recorrido funcional local está enlazada desde
[`TRACEABILITY.md`](../00-governance/TRACEABILITY.md) y el
[registro por ejercicio](../05-quality/evidence/pwa-exercise-verification-2026-10-09.md).

## 8. Criterio de aceptación

La estructura, los índices, las claves, los totales y el recorrido local por
serie quedaron verificados para los cuatro días. La compatibilidad física y
publicada se mantiene como evidencia independiente de esta especificación.
