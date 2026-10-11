# Modelo de amenazas de la PWA

## Activos

- Progreso, sesiones, perfil y archivo de respaldo.
- Integridad de rutinas, portada, manifiesto y Service Worker.
- Disponibilidad de la versión offline completa.

## Límites de confianza

1. Usuario ↔ interfaz PWA.
2. Origen PWA ↔ navegador y almacenamiento local.
3. Archivo JSON elegido ↔ validador de importación.
4. Recursos publicados ↔ Service Worker/Cache API.

No existe flujo de datos hacia Android nativo, Tezkatli, un proveedor de IA ni servicios de integración en el alcance actual.

## Amenazas y controles

| Amenaza | Ejemplo | Control PWA |
|---|---|---|
| Suplantación de contenido | sitio/origen incorrecto | servir mediante HTTPS; validar origen y manifest en entrega |
| Manipulación | JSON alterado | validar versión, tamaño y esquema; confirmar reemplazo |
| Divulgación | XSS lee perfil local | insertar usuario como texto, evitar HTML inseguro y revisar dependencias |
| Pérdida | limpieza del navegador/sistema operativo o desinstalación elimina almacenamiento del origen | no borrar desde el ciclo de vida de la PWA; identificar el origen y formatos; describir el límite de control externo |
| Indisponibilidad | actualización incompleta/cuota | conservar paquete completo anterior y no activar parcial |
| Contenido malicioso | texto o archivo importado | validar y limitar entradas antes de usarlas |

## Verificación

- Pruebas sintéticas de importación válida/inválida y persistencia.
- Revisión del código que representa texto de usuario y procesa archivos.
- Prueba de actualización/recuperación en navegador compatible.
- Validación de recursos y enlaces del repositorio.

Estas comprobaciones no prueban la seguridad integral del navegador o del dispositivo. No se declara certificación ni cumplimiento de un estándar móvil para esta PWA.
