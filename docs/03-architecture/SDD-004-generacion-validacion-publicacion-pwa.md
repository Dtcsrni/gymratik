# SDD-004 — Generación, ejecución y publicación de la PWA

**Estado:** `In progress`
**Versión:** `0.1`
**Fecha:** `2026-09-24`
**TDD asociado:** [TDD-005](../05-quality/TDD-005-pwa-perfil-e2e.md)
**Decisiones:** [ADR-013](adr/ADR-013-perfil-local-y-respaldo-pwa.md), [ADR-014](adr/ADR-014-progresion-e-horarios-locales-pwa.md), [ADR-015](adr/ADR-015-base-local-v3-exclusiva.md), [ADR-016](adr/ADR-016-actualizacion-segura-pwa.md), [ADR-017](adr/ADR-017-politica-de-actualizacion-y-cache-pwa.md)

## 1. Propósito y alcance

Describe la PWA web estática: su shell, las cuatro rutinas canónicas, el
progreso/perfil local, el ciclo de instalación/actualización y la preparación
offline. No sustituye el SRS ni declara implementadas las funciones Android,
Tezkatli, nutrición, IA, Zepp o Health Connect.

El alcance verificable es `FUN-PWA-001..010`, `FUN-PRO-001..014` y las partes
de `FUN-TRN-*` que la PWA efectivamente ofrece: calentamiento, series, descanso,
deshacer y captura de repeticiones/carga. Los contratos Android más amplios se
mantienen fuera de esta especificación.

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

Solo el worker puede declarar completa una caché después de terminar todo el
inventario esencial. Nunca se borra el historial al actualizar recursos y nunca
se limpian cachés de otros orígenes/aplicaciones. Los videos/GIF son opcionales.

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
   datos. Importaciones v1/v2 y esquemas inválidos no mutan el estado.
6. Los avisos de entrenamiento son de primer plano; no se promete entrega con
   la PWA cerrada.
7. No se persisten fotografías de usuario en esta PWA ni se sincroniza perfil,
   historial o series entre dispositivos.

## 5. NFR aplicables y evidencia real

Se automatizan disponibilidad offline del shell/recursos, no pérdida/duplicado
de datos, esquema, gates de instalación, privacidad estática, labels/estados,
reduced motion y presupuestos funcionales del worker. Los umbrales de
persistencia `<100 ms` y TTFD `<500 ms` en **Realme GT 6** requieren medición en
ese dispositivo; desktop/viewport emulado no los cierra. Compatibilidad
instalada/offline/ahorro de batería, comportamiento de cuota real y lectores de
pantalla necesitan validación en navegador/dispositivo correspondiente.

## 6. Criterios de cierre

El diseño solo se cierra cuando TDD-005 trace todos los requisitos incluidos,
la suite automatizada pase, E2E de navegador cubra cuatro rutinas y shell, y los
gates de Android real queden medidos o explícitamente pendientes. El estado
`Verified` se asigna solo al alcance y tipo de evidencia que efectivamente se
ejecutó.
