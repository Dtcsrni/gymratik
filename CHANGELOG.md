# Changelog

Los cambios notables se documentarán siguiendo Keep a Changelog y versionado semántico una vez exista software distribuible.

## [0.7.20] - 2026-11-12

### Fixed

- El contador animado del resumen se mantiene dentro de su función y no bloquea los controles de las rutinas.

## [0.7.19] - 2026-11-11

### Changed

- Las métricas del resumen final cuentan sus valores, también en progreso muscular, con movimiento reducido y valores accesibles.

## [0.7.18] - 2026-11-11

### Changed

- La barra flotante queda centrada en móvil y destaca más la mascota animada seleccionada.
- El resumen final muestra poses animadas más grandes de la mascota configurada, sin círculo ni manzana.

## [0.7.17] - 2026-11-11

### Changed

- El panel muscular elimina leyendas redundantes y refuerza el pulso visual rojo con un ciclo más marcado, manteniendo el ajuste de movimiento reducido.

## [0.7.16] - 2026-11-11

### Changed

- El resumen de sesión usa ilustraciones musculares anatómicas locales, anterior y posterior, del segmento con mayor trabajo registrado.
- Cada barra muestra series confirmadas frente a las prescritas para el grupo y llega al 100 % al completar su volumen previsto.

## [0.7.15] - 2026-11-10

### Changed

- El cierre de sesión presenta un anillo de progreso, barras por zona y un mapa muscular animado con datos de series confirmadas; el pulso se identifica como decorativo y respeta movimiento reducido.
- El resumen móvil amplía las métricas y conserva la variante de mascota configurada.

## [0.7.14] - 2026-11-10

### Changed

- El cierre de sesión usa un diseño móvil compacto, con métricas y mensaje a ancho completo, mascota local cuando no hay retrato, fruta decorativa animada y adornos que respetan movimiento reducido.

## [0.7.13] - 2026-11-10

### Changed

- En móvil, las imágenes de movimiento aparecen inmediatamente después del nombre de cada ejercicio y antes de la prescripción y los controles.

## [0.7.12] - 2026-11-10

### Fixed

- En móvil, las etiquetas de ejercicio se consolidan en una sola zona legible y dejan de mostrar fichas vacías o repetidas.
- El contenido de las rutinas reserva el alto real de la barra flotante, incluso cuando esta se expande, para permitir desplazar los controles que quedan detrás.

## [0.7.11] - 2026-11-10

### Fixed

- La vista «Posición y recorrido» se apila en móvil con imágenes y textos a ancho completo; la flecha queda entre Inicio y Final.

## [0.7.10] - 2026-11-10

### Fixed

- Se elimina el bloque duplicado de peso de aproximación; el único selector de carga adopta ese modo solo mientras la aproximación está pendiente.

## [0.7.9] - 2026-11-10

### Fixed

- El selector de carga cambia a una aproximación independiente para el primer ejercicio pendiente, guarda su valor por ejercicio y vuelve a la carga normal al terminar.
- La aproximación no hereda la carga normal cuando todavía no tiene un valor propio, y sus indicadores desaparecen al registrarla.

## [0.7.8] - 2026-11-10

### Changed

- La barra flotante móvil ocupa menos alto, conserva el estado y el ejercicio en foco sin duplicar su nombre, y usa fondos ligeramente translúcidos con contraste de texto suficiente.
- Se refuerza el diseño adaptable de las posiciones y el recorrido para evitar columnas angostas y texto fragmentado en pantallas móviles.

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
