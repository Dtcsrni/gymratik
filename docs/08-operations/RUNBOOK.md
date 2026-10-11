# Operación local de la PWA

## Desarrollo y validación

1. Trabajar con fixtures sintéticos; no copiar perfiles, bases ni respaldos reales al repositorio.
2. Regenerar `sw.js` con `python scripts/build_pwa_service_worker.py` si cambia un recurso precargado.
3. Ejecutar `python scripts/validate_repository.py` y las pruebas aplicables al cambio.
4. Revisar el diff y confirmar que el inventario generado corresponde a los recursos actuales.

## Uso sin conexión

- La primera preparación requiere conectividad y espacio suficiente.
- Verificar que el splash marque paquete completo antes de declarar disponibilidad offline.
- Si la descarga falla, mantener la versión completa previa y reintentar cuando haya conexión/espacio.
- El Service Worker guarda recursos estáticos; no es una copia de sesiones ni perfil.

## Exportar y restaurar

1. Exportar desde la pantalla local de perfil/datos.
2. Guardar el JSON v3 fuera del almacenamiento del sitio y, de ser necesario, fuera del dispositivo.
3. Para restaurar, seleccionar el archivo, revisar la confirmación y comprobar perfil e historial.
4. Ante un archivo inválido, conservar el estado actual; no intentar editar la base manualmente.

## Incidentes comunes

- **Datos locales no disponibles:** no borrar el sitio como primer paso. Revisar soporte de IndexedDB y el origen correcto; si existe un JSON v3 externo, restaurarlo mediante la PWA.
- **PWA abre una versión anterior:** conectarse, abrir la URL publicada y permitir que el Service Worker complete actualización; no limpiar IndexedDB como medida de caché.
- **Paquete offline incompleto:** recuperar conexión y reintentar; verificar el inventario y no afirmar disponibilidad offline completa antes del éxito.
- **Datos borrados por navegador/desinstalación:** recuperar únicamente desde un archivo exportado previamente; la PWA no puede reconstruir almacenamiento eliminado.

No hay servicios de backend, workers remotos, colas, credenciales, relojes ni procedimiento de operación de servidor en el alcance vigente.
