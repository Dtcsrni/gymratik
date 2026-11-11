# Changelog

Los cambios notables se documentarán siguiendo Keep a Changelog y versionado semántico una vez exista software distribuible.

## [0.7.7] - 2026-11-10

### Fixed

- La portada, los hitos y las cuatro rutinas recargan la versión activa cuando el Service Worker aplica una actualización, manteniendo un único paquete coherente de pantallas y recursos.

## [0.7.6] - 2026-11-10

### Fixed

- Se elimina la duplicación de funciones en las rutinas que impedía analizar y ejecutar su JavaScript; vuelve a responder el calentamiento y se aplica la mascota elegida en el perfil.
- La regeneración del contrato de cuatro días deja de acumular declaraciones y código repetido.

## [0.7.5] - 2026-11-10

### Changed

- El progreso se identifica como guardado automático; completar la última serie cierra la rutina sin pulsar un botón adicional.
- El cierre manual temprano se presenta como opcional y omitir el último ejercicio registra automáticamente una sesión parcial.

## [0.7.4] - 2026-11-10

### Added

- El cierre del día celebra sesiones completas y parciales con resumen de series, ejercicios, repeticiones y duración, más datos curiosos basados en series confirmadas.
- Se aclara que las aproximaciones no cuentan como trabajo efectivo y se permite reintentar el guardado cuando falla.

## [0.7.3] - 2026-11-09

### Added

- Se comparan la sesión reciente con la anterior, la semana en curso y el mes en curso contra tramos equivalentes previos.
- Se agregan gráficos de actividad diaria, semanal y mensual con deltas y animaciones que respetan movimiento reducido.

## [0.7.2] - 2026-11-09

### Changed

- El panel completo de control de series también queda resaltado en amarillo y difuminado cuando la máquina está ocupada; solo el control para liberarla permanece activo y nítido.

## [0.7.1] - 2026-11-09

### Changed

- Se separan visualmente las secciones de prescripción, cargas, series, referencias y técnica en las cuatro rutinas.
- El peso de aproximación usa un campo y un borrador propios; el peso normal conserva su última carga registrada y se muestra aparte.
- La PWA deja explícito que la carga de aproximación no se mezcla con las series normales.

## [0.7.0] - 2026-11-09

### Changed

- Se diferencian mejor las tarjetas de ejercicios y se anima el ejercicio en foco en la barra flotante, también cuando está plegada.
- Marcar una máquina ocupada resalta y difumina su tarjeta y bloquea sus controles hasta liberar la máquina.
- Se mejora la presentación de frases motivacionales y se desactiva el zoom de página en dispositivos móviles.
- Se mantiene la carga de calentamiento en el registro separado de las series normales.

## [Unreleased]

### Added

- Base de gobierno, requisitos, arquitectura, calidad, seguridad, MLOps y operación.
