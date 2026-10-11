# Estrategia de pruebas de Gymratik PWA

## Objetivo

Demostrar los comportamientos del [SRS activo](../01-requirements/SRS.md), vinculando cada conclusión con una prueba y su nivel de evidencia. La estructura documental está en [TDD_SDD_SERIES.md](../00-governance/TDD_SDD_SERIES.md).

## Capas

| Capa | Ejemplos | Uso |
|---|---|---|
| Validadores | Markdown, enlaces, requisitos, rutinas, medios, contratos | Cada cambio pertinente |
| Unitarias | persistencia, esquema, estados, Service Worker | Cada cambio pertinente |
| Integración local | IndexedDB, migración y respaldo con fixtures | Cambios de datos |
| Navegador | flujo de inicio, sesión, instalación y offline | Cambios de interfaz/PWA |
| Dispositivo | PWA instalada, modo avión, permisos reales | Solo para confirmar comportamiento físico |

## Casos críticos

- **TST-PRO-006:** perfil vacío presenta el formulario inicial; guardar conserva navegación y progreso; perfil ya definido no se redirige.
- **TST-PRO-007:** mensajes de actividad se derivan de datos locales disponibles sin inventar resultados ni modificar registros.
- **TST-PRO-016:** mover un reloj de prueba al inicio de una semana local nueva; el avance anterior deja de contar, pero cada snapshot completo queda archivado; repetir apertura de portada y comprobar archivo idempotente. Una sesión fechada iniciada hoy persiste incluso con cero series.
- **TST-PRO-017:** la interfaz identifica el origen, IndexedDB v3, claves fallback/snapshots/archivo de localStorage y JSON `gymratik-backup` esquema 3.
- **TST-PRO-018:** revisar cada llamada de borrado y probar que solo se alcanza mediante reinicio confirmado o importación de reemplazo confirmada; esas acciones incluyen snapshots archivados. Actualizar/reabrir/migrar/rotar conserva snapshots e historial. Documentar que la limpieza del navegador/sistema operativo está fuera del control de la PWA.

Los casos específicos de actualización, privacidad, rutinas y medios están en [TDD-005](TDD-005-pwa-perfil-e2e.md), [TDD-002](TDD-002-integridad-rutinas-canonicas.md) y [TDD-004](TDD-004-medios-formato-y-correspondencia.md).

## Casos frontera

- Cambio de fecha local al cruzar lunes, zona horaria o horario de verano.
- Cierre/recarga durante calentamiento, descanso o sesión sin series completadas.
- Snapshot sin fecha semanal confiable.
- Migración interrumpida, store desconocido o transacción fallida.
- Archivo v3 corrupto, sobredimensionado, mal tipado o de versión incompatible.
- Cuota insuficiente o red interrumpida durante actualización de recursos.
- Movimiento reducido, almacenamiento privado o IndexedDB no disponible.

## Evidencia de entrega

- Registrar comando, salida, fecha, plataforma y limitaciones.
- Diferenciar prueba automatizada, navegador emulado, navegador publicado y dispositivo físico.
- No presentar una prueba sintética como publicación o compatibilidad física.
- Usar fixtures sintéticos; no copiar datos personales reales al repositorio.
- Ejecutar `python scripts/validate_repository.py` antes de integrar cambios.

Las pruebas de IA, Room, backend, servicios, métricas de rendimiento Android e integraciones están fuera de esta estrategia activa.
