# Acta de constitución de Gymratik PWA

## Identificación

- **Producto activo:** Gymratik PWA: rutinas y progreso local.
- **Usuario:** una persona.
- **Plataforma activa:** PWA servida por HTTPS y ejecutada en navegador compatible.
- **Estado:** aplicación PWA en evolución; las capacidades se declaran con evidencia por separado.

## Problema

La persona necesita abrir sus cuatro rutinas canónicas, registrar el avance desde el teléfono y conservarlo entre sesiones, incluso cuando no hay conexión después de preparar la PWA.

## Objetivos

1. Consultar las cuatro rutinas sin conexión tras completar la descarga offline.
2. Registrar y revisar sesiones localmente sin pérdida silenciosa al recargar o actualizar.
3. Permitir exportar y restaurar manualmente un respaldo compatible.
4. Comunicar con claridad el estado local, de red, actualización y respaldo.

## Alcance activo

- Portada, instalación, actualización y recursos offline de la PWA.
- Cuatro rutinas canónicas con calentamiento, series, descanso y estado local.
- Perfil, historial y estadísticas locales disponibles en modo instalado.
- Exportación e importación manual de respaldo JSON v3.
- Privacidad, seguridad, validación y operación limitadas a este origen PWA.

## Fuera del alcance actual

- Nutrición y suplementos.
- Gestión/detección de gimnasios o catálogo de equipo.
- IA y recomendaciones generadas por modelos.
- Aplicación Android nativa.
- Amazfit, Zepp, Health Connect u otras integraciones.
- Cuentas, backend, nube o sincronización de datos entre dispositivos.

Los requisitos e ideas heredados de estas áreas quedan registrados como diferidos en [DEFERRED_SCOPE.md](../01-requirements/DEFERRED_SCOPE.md). Retomarlos exige una nueva decisión de alcance, criterios verificables y revisión de arquitectura.

## Indicadores de aceptación

- Las cuatro rutinas y sus recursos declarados esenciales abren sin red tras completar preparación offline.
- Una sesión local iniciada hoy se puede continuar después de navegar, recargar o actualizar la PWA.
- El progreso semanal anterior no contamina el nuevo avance y el historial terminado permanece.
- Un respaldo v3 sintético se exporta, valida y restaura; uno inválido no modifica datos.
- La interfaz identifica el origen de almacenamiento y los formatos IndexedDB/localStorage/exportación.

## Restricciones y límites

- Cache API contiene recursos de la PWA; los datos de usuario están en IndexedDB/localStorage.
- El respaldo es un archivo manual bajo control del usuario; no hay sincronización automática.
- La PWA identifica el origen y formatos locales; el navegador/sistema operativo controla el borrado de datos del sitio y los efectos de desinstalación.
- La validación automatizada o emulada no acredita por sí sola funcionamiento físico.

## Ciclo de vida

Incrementos pequeños sobre la PWA existente. La secuencia, puertas de calidad y criterios de cierre están en [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md).
