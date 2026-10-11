# SDD-003 — Medios, fallback y procedencia técnica

**Estado:** `PWA runtime verified; media provenance pending`
**Versión:** `0.1`  
**Fecha:** `2026-09-17`  
**TDD asociado:** [TDD-004](../05-quality/TDD-004-medios-formato-y-correspondencia.md)

## 1. Objetivo

Garantizar que cada tarjeta de rutina tenga los recursos visuales que su
formato promete y que cada recurso pueda relacionarse con el ejercicio,
posición y versión correctos. La existencia física del archivo y su
correspondencia visual son controles distintos.

## 2. Roles visuales

Cada ejercicio puede declarar los siguientes roles, según el formato del día:

| Rol | Obligación | Fallback |
|---|---|---|
| `machine_reference` | Vista de apoyo de la máquina o configuración. | Texto de identificación técnica. |
| `start_frame` | Posición inicial del movimiento. | Panel estático explícito. |
| `end_frame` | Posición final o contracción controlada. | Panel estático explícito. |
| `motion_gif` | Recorrido completo cuando la tarjeta lo promete. | `static_fallback` del mismo movimiento. |
| `static_fallback` | Recurso estático legible para carga fallida o reduced motion. | Mensaje visible de recurso ausente. |

El fallback no puede sustituir silenciosamente un recurso obligatorio sin dejar
el estado observable para diagnóstico.

## 3. Contrato mínimo de manifiesto

Cada elemento de medio debe poder expresar, como mínimo:

```text
MediaItem
├─ routineId
├─ exerciseIndex?
├─ role
├─ assetId
├─ path
├─ fallbackPath?
├─ source
├─ sourceVersion?
├─ sha256
├─ dimensions
├─ frameCount?
├─ alt
├─ reviewStatus
└─ reviewNotes?
```

Estados técnicos propuestos:

- `PENDING_IDENTITY_REVIEW`
- `VERIFIED_VISUAL_MATCH`
- `REJECTED_SEMANTIC_MISMATCH`
- `MISSING_ASSET`
- `STATIC_ONLY`

La estructura debe ser homogénea entre Día 1, Día 2 y Día 3. Un arreglo con
campos distintos por día no es un contrato suficiente para automatizar la
revisión.

## 4. Reglas para imágenes y GIF

1. Toda ruta local de `src`, `data-static-src` o manifiesto debe existir dentro
   del árbol permitido.
2. Toda tarjeta debe declarar sus roles visuales requeridos; no basta con que
   exista una imagen cualquiera en el mismo HTML.
3. Un `.gif` debe ser realmente un recurso animado verificable; una miniatura o
   un archivo marcador no cuenta como GIF de técnica.
4. Toda animación debe tener `static_fallback`, `alt` descriptivo y soporte de
   `prefers-reduced-motion`.
5. Los recursos decorativos deben usar `alt=""` y `aria-hidden="true"`; los
   recursos de contenido deben tener texto alternativo específico.
6. El nombre, hash y tamaño prueban integridad e identidad técnica del archivo,
   pero no prueban que el movimiento representado sea el ejercicio correcto.
7. La correspondencia visual se revisa por ejercicio: patrón, trayectoria,
   máquina/configuración, posición inicial, posición final y ausencia de
   elementos que contradigan el título.
8. Si la revisión visual no puede confirmar la correspondencia, el estado es
   `REJECTED_SEMANTIC_MISMATCH` o `PENDING_IDENTITY_REVIEW`, nunca confirmado.

## 5. Flujo de validación

```text
HTML + manifest
      │
      ├─ presencia y rutas ──► A
      ├─ hash/dimensiones ───► A
      ├─ alt/fallback/CSS ────► A + V
      ├─ mapeo por ID/rol ────► A
      └─ patrón y máquina ────► V/H
```

La validación automatizada debe producir un inventario compacto, sin imprimir
base64 ni imágenes embebidas. La revisión visual debe guardar capturas o una
acta con el recurso revisado, el ejercicio, el rol, el resultado y la
limitación observada.

## 6. Estado actual — 2026-10-09

- Las cuatro HTML canónicas exponen 26 tarjetas con `data-media-mode`:
  12 `STATIC_ONLY` (Días 1–2) y 14 `GIF` (Días 3–4).
- El recorrido de recursos validó 25 parejas estáticas y la guía hip thrust de
  tres pasos. Las 14 animaciones pausaron con poster bajo movimiento reducido
  y reanudaron con avance de cuadros.
- El inventario y la prueba visual por ejercicio están enlazados en
  [TDD-004](../05-quality/TDD-004-medios-formato-y-correspondencia.md) y el
  [registro PWA](../05-quality/evidence/pwa-exercise-verification-2026-10-09.md).
- Los catálogos de procedencia históricos no tienen todavía un esquema
  uniforme conciliado con las salidas activas; la licencia y redistribución de
  los medios tampoco se declara cerrada. No se presentan como verificadas.

## 7. Criterio de aceptación

El comportamiento de medios en la PWA local quedó verificado. La procedencia,
el hash y la conciliación uniforme de catálogos siguen siendo criterios abiertos
para cerrar la especificación completa; la revisión local no demuestra la
identidad del equipo físico ni derechos de redistribución.
