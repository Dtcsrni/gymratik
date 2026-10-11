# SDD-004 — Generación, ejecución y publicación de la PWA

**Estado:** `In progress`
**Versión:** `0.3`
**Fecha:** `2026-10-09`
**TDD asociado:** [TDD-005](../05-quality/TDD-005-pwa-perfil-e2e.md)
**Decisiones:** [ADR-013](adr/ADR-013-perfil-local-y-respaldo-pwa.md), [ADR-014](adr/ADR-014-progresion-e-horarios-locales-pwa.md), [ADR-015](adr/ADR-015-base-local-v3-exclusiva.md), [ADR-016](adr/ADR-016-actualizacion-segura-pwa.md), [ADR-017](adr/ADR-017-politica-de-actualizacion-y-cache-pwa.md)

## 1. Propósito y alcance

Describe la PWA estática: portada, cuatro rutinas canónicas, progreso/perfil
local, instalación/actualización y recursos offline. No define servicios ni
integraciones externas.

El alcance verificable es `FUN-PWA-001..010`, `FUN-PRO-001..017` y
`FUN-TRN-010..012`. Los datos se guardan localmente y el único traslado manual
de datos personales es el respaldo JSON v3 confirmado por el usuario.

## 2. Componentes y responsabilidades

| Componente | Responsabilidad | Datos persistentes |
|---|---|---|
| `index.html` | Shell, splash, preferencias de red, perfil/estadísticas, navegación y avisos | No escribe directamente series |
| HTML canónicos (Días 1–4) | Prescripción, calentamiento, temporización, una acción de serie y captura de rendimiento | Progreso legado de rutina y borradores; bloqueado fuera del modo instalado |
| `progress-store.js` | API local, esquema IndexedDB v3, fallback, perfil, sesiones, actividad y respaldo | IndexedDB o fallback v3 de `localStorage` |
| `install-gate.js` | Identificar modo instalado; restringir lectura/escritura de perfil y progreso | Preferencia local de cierre de invitación |
| `sw.js` | Instalar inventario, cache-first, progreso, versión completa, actualización diferida y limpieza acotada | Cachés `entrenamiento-pwa-*`, separadas del historial |
| `scripts/build_pwa_service_worker.py` | Generar el inventario esencial reproducible | Reescribe únicamente el artefacto generado `sw.js` |

## 3. Flujos y estados

### 3.1 Inicio y red

```text
Abrir shell ─┬─ inicializar IndexedDB/fallback y renderizar estado local
             └─ consultar SW/versión ─ permiso de red ─ precache opcional
```

La lectura local no depende de la red. El splash separa ese estado del estado
de descarga, anuncia solo conteos medibles y no publica bytes de transferencia
estimados como si fueran medidos. La autorización `ask` es temporal a la
apertura; `always` y `wifi` son preferencias locales. La detección Wi‑Fi es
best-effort: si el navegador no expone el tipo, se difiere la descarga.

### 3.2 Actualización offline

```text
versión activa completa (A)
        │ instalar nueva (B) en caché aislada
        ├─ fallo/cuota/interrupción → eliminar B parcial; conservar A y datos
        └─ inventario completo → marcar B completa; esperar apertura segura
                                 → activar B y limpiar cachés Gymratik antiguas
```

Solo el worker declara completa una caché después de guardar el inventario
generado. Una instalación incompleta no sustituye la versión completa previa.
La limpieza se limita a cachés de Gymratik; las reglas de inclusión de medios
dependen del inventario actual.

### 3.3 Entrenamiento y perfil

Las cuatro fichas mantienen claves de series separadas por día. La acción única
de cada ejercicio cambia según el estado: iniciar, completar, descanso mínimo,
descanso en curso y siguiente serie. Mantener 5 s durante descanso lo omite; no
hay segundo botón de salto. El slider de repeticiones se deriva del rango
prescrito `rMin..rMax+4`; solo una serie completada puede generar registro de
rendimiento.

`progress-store.js` es la única frontera para perfil/historial/respaldos. Los
recursos del Service Worker nunca actúan como copia de historial. Esquema y
respaldo aceptados: v3. La pestaña no instalada puede consultar rutinas, pero no
leer ni escribir el perfil o progreso.

### 3.4 Renovación semanal y continuidad de sesión

La semana operativa empieza el lunes según la fecha y zona horaria local del
dispositivo. `progress-store.js` deriva la semana de la fecha original de inicio
de sesión (no de una lectura o recaptura posterior). Todo snapshot con progreso
que salga de la semana actual, incluidos los que carecen de fecha, se agrega a
`gymratik-legacy-progress-archive-v1` antes de renovar la vista operativa. Cada
captura se conserva; repetir la lectura no duplica la misma captura. El archivo
no se confunde con el historial de sesiones completadas.

La portada ejecuta la renovación antes de construir sus tarjetas y cada HTML
canónico la ejecuta antes de publicar o migrar su snapshot. La operación es
idempotente. Si una sesión comenzó hoy, su snapshot fechado prevalece sobre una
clave semanal ausente y no se limpia al volver a portada, actualizar o reabrir.
El CTA detecta `sessionStartedAt` de hoy aun cuando `doneSeries=0`, enlaza a esa
rutina y usa la acción “Continuar”. Los registros terminados de semanas
anteriores quedan consultables en historial/estadísticas; no incrementan el
progreso operativo semanal.

Instalar, actualizar y migrar no llama a las rutas manuales de borrado. IndexedDB
reside bajo el origen y perfil del navegador; el fallback y los snapshots están
en localStorage. La PWA no controla la limpieza manual del sitio, el cambio de
origen/perfil ni todas las políticas de desinstalación del navegador o sistema
operativo. `navigator.storage.persist()` es una solicitud al navegador, no una
garantía de retención. El archivo transferible es JSON `gymratik-backup`, esquema
3.

## 4. Invariantes y límites

1. Las cuatro rutinas, la portada y todos los recursos estáticos esenciales
   aparecen en el inventario generado; la falta de un recurso impide marcar la
   versión como completa.
2. `completedSeries` no aumenta por ajustar el slider, abrir una ficha o
   iniciar calentamiento; solo una transición válida de serie confirmada lo
   cambia.
3. Repeticiones aceptadas por ejercicio pertenecen al intervalo inclusivo
   `[mínimo prescrito, máximo prescrito + 4]`; carga puede omitirse y conserva
   unidad declarada cuando existe.
4. La clave de progreso/identificador de rutina distingue Días 1–4; el retry de
   lectura o persistencia no duplica registros.
5. Importación de respaldo valida formato y esquema v3 antes de reemplazar
   datos. Importaciones v1/v2 y esquemas inválidos no mutan el estado. Una
   actualización de la PWA no borra stores ni snapshots locales preexistentes.
6. Los avisos de entrenamiento son de primer plano; no se promete entrega con
   la PWA cerrada.
7. No se persisten fotografías de usuario en esta PWA ni se sincroniza perfil,
   historial o series entre dispositivos.

## 5. Seguridad y evidencia

La PWA no tiene autenticación ni transmite datos de usuario a servicios remotos.
La validación estática y automatizada cubre contratos, inventario, importación,
persistencia y comportamiento del worker dentro de sus fixtures. Instalación,
offline, cuota, accesibilidad visual y actualización en dispositivo requieren
evidencia de navegador/dispositivo; no se infieren de pruebas sintéticas.

## 6. Criterios de cierre

El diseño solo se cierra cuando TDD-005 trace los requisitos incluidos, las
pruebas automatizadas aplicables pasen y la matriz reporte por separado la
evidencia de navegador y dispositivo. El estado `Verified` se asigna solo al
alcance y tipo de evidencia que efectivamente se ejecutó.
