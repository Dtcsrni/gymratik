# ADR-018 — Retención manual de datos y archivo semanal

**Estado:** Accepted
**Fecha:** 2026-10-09

## Contexto

El código separa recursos de Cache API de los registros en IndexedDB/localStorage, pero el texto de perfil recomendaba exportar antes de desinstalar y el rollover semanal vaciaba el snapshot operativo. Además, el archivo anterior guardaba una sola captura por rutina, con riesgo de reemplazar evidencia local en un rollover posterior.

## Decisión

1. La aplicación no elimina datos de usuario durante instalación, inicio, actualización de recursos, migración o renovación semanal.
2. La renovación semanal puede cambiar la vista operativa, pero primero agrega el snapshot completo a `gymratik-legacy-progress-archive-v1`. El archivo conserva múltiples capturas por rutina y evita repetir la misma captura en aperturas sucesivas.
3. Reiniciar registros o importar un respaldo para reemplazar datos son acciones manuales. La interfaz requiere confirmación; esos actos incluyen snapshots y archivos semanales locales.
4. La interfaz identifica dónde residen los datos y sus formatos: IndexedDB `entrenamiento-progress` v3; fallback `entrenamiento-progress-fallback-v3`; snapshots `fitlovers-dayN-series-v1`; archivo `gymratik-legacy-progress-archive-v1`; exportación JSON `gymratik-backup` esquema 3.
5. La PWA no puede controlar la limpieza manual del origen, cambios de perfil/origen, navegación privada ni todos los efectos de desinstalación del navegador/sistema operativo. `navigator.storage.persist()` expresa una solicitud al navegador, no una garantía universal.

## Consecuencias

- Los datos disponibles en el mismo origen sobreviven a las operaciones de ciclo de vida que controla la aplicación.
- Los snapshots anteriores siguen recuperables localmente y pueden ocupar más almacenamiento con el tiempo; no se les aplica purga automática.
- La importación confirmada puede reemplazar registros y el reinicio confirmado puede borrarlos; ambos actos son visibles y manuales.
- El comportamiento externo de instalación/desinstalación depende del navegador y sistema operativo, por lo que no se promete retención universal tras desinstalar.

## Verificación

- Pruebas runtime: snapshot fuera de semana archivado íntegro, archivos sucesivos sin pérdida y deduplicación al reabrir.
- Pruebas de migración: stores previos, fallback y snapshots conocidos permanecen disponibles.
- Prueba de interfaz: ubicación y formatos identificados; borrado/importación reemplazante requieren confirmación.
