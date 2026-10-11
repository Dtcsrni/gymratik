# Backlog activo de Gymratik PWA

Solo las tareas de esta lista pertenecen al backlog activo. Un estado pendiente significa que requiere evidencia, no que ya esté implementado.

## P0 — Continuidad y datos locales

- [ ] Cerrar pruebas de progreso semanal: nuevo lunes, zona horaria local, snapshot sin fecha y sesión iniciada hoy con cero series.
- [ ] Verificar migración y restauración IndexedDB con fixtures sintéticos v1/v2/v3 sin borrar stores desconocidos.
- [ ] Probar exportar/importar JSON v3; archivo inválido no debe mutar datos.
- [ ] Verificar que interfaz y mensajes expliquen que el respaldo es manual y local.

## P1 — Instalación y offline

- [ ] Verificar primera instalación, actualización pendiente y recuperación de cuota en navegador móvil.
- [ ] Comprobar visualmente portada, cuatro rutinas, iconos y medios declarados esenciales offline.
- [ ] Medir transferencia real desde el host publicado; el tamaño del inventario local es solo una estimación.
- [ ] Revisar accesibilidad, movimiento reducido y flujo móvil en un navegador objetivo.

## Diferido

Nutrición, suplementos, gimnasio/equipo, IA, Android nativo, Amazfit/Zepp, Health Connect, backend y sincronización entre dispositivos. El registro de identificadores heredados está en [DEFERRED_SCOPE.md](DEFERRED_SCOPE.md); no implica autorización o prioridad futura.
