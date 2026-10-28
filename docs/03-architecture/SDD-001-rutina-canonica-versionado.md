# SDD-001 — Modelo de rutina canónica y versionado

**Estado:** `Routine v2 functional E2E verified (local synthetic)`
**Versión:** `0.4`
**Fecha de verificación:** `2026-10-27`
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
11. El contenido v3 mantiene el `routineId` y las claves previas estables; los
    ejercicios nuevos ocupan índices vacantes, sin reasignar registros anteriores.
12. Los días base suman 21–24 series y el cuarto día es opcional. Cada rutina
    tiene hasta siete ejercicios, al menos 3 series por ejercicio y prescribe
    8–12 repeticiones. Se priorizan máquinas; la bisagra usa Smith. El tiempo
    de sesión incluye calentamiento y es una estimación de programación.
8. Una rutina no mezcla en una misma salida los identificadores de otra rutina,
   día o versión.
9. Las cuatro salidas comparten un único `main.cards`, un `data-exercise-index`
   contiguo por tarjeta y un único `sessionFooter`; las diferencias de contenido
   no deben crear una segunda variante de layout.
10. El contexto del día (objetivo y anatomía) se mantiene disponible en un
    desplegable nativo cerrado por defecto. En móvil, las métricas y controles
    de registro preceden a las referencias visuales; en escritorio, el orden de
    la ficha no cambia y el contexto expandido presenta sus dos paneles en
    columnas.

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

El atributo `data-routine-content-version="3"` identifica la prescripción v3;
`routineId=dayN` y los índices/claves previos se conservan por compatibilidad con
el progreso local. Los ejercicios nuevos se agregan en índices vacantes. El
cuarto día no participa en la rotación base, pero una sesión opcional iniciada
hoy conserva el flujo de continuación.
Las cargas base son orientativas y no representan topes físicos verificados sin
marca/modelo de la máquina y sus incrementos.

## 7. Estado actual y discrepancias conocidas

El contenido v3 declara 7/23, 7/23, 7/22 y 7/22 ejercicios/series,
respectivamente. Los tres días base suman 68 series; el opcional eleva el máximo
semanal a 90. El validador ejecutable constituye la fuente del resultado;
los E2E previos de 2026-10-09 se conservan como evidencia histórica y no
validan esta nueva distribución.

Las cuatro salidas canónicas superaron TDD-002 el 2026-10-09. El cambio de
jerarquía móvil se validó estáticamente y mediante capturas sintéticas el
2026-10-26; su recorrido interactivo responsive queda pendiente del arranque
del driver Playwright. La evidencia de conteo, series y recorrido funcional local está enlazada desde
[`TRACEABILITY.md`](../00-governance/TRACEABILITY.md) y el
[registro por ejercicio](../05-quality/evidence/pwa-exercise-verification-2026-10-09.md).
Las capturas nuevas están en la [auditoría móvil](../05-quality/evidence/ux-audit-2026-10-26/README.md).

## 8. Criterio de aceptación

La estructura, los índices, las claves, los totales y el recorrido local por
serie quedaron verificados para los cuatro días. La compatibilidad física y
publicada se mantiene como evidencia independiente de esta especificación.
