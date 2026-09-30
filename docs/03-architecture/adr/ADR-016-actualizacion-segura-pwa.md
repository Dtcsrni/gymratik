# ADR-016 — Inicio informativo y actualización segura de la PWA

**Estado:** Superseded por [ADR-017](ADR-017-politica-de-actualizacion-y-cache-pwa.md)
**Fecha:** 2026-09-23

## Contexto

La PWA precargaba todos sus recursos con `cache.addAll`, llamaba `skipWaiting()` en cada instalación y activaba inmediatamente cada versión nueva. La portada ocultaba el splash al terminar de leer el estado local, sin comunicar el avance del precache. Una activación podía reclamar pestañas abiertas y la portada recargaba al detectar `controllerchange`. Además, el precache incluía animaciones GIF que no son necesarias para operar las rutinas sin conexión.

## Decisión

1. La inicialización local y la preparación de la PWA se ejecutan en paralelo. El inicio local no tiene un límite artificial y el splash dura al menos un segundo; la comprobación de versión y la descarga de recursos tienen presupuestos independientes de 20 s. Si falla la lectura local, el splash conserva el estado y ofrece reintento manual sin mutar ni eliminar datos.
2. El worker descarga y guarda secuencialmente cada recurso esencial, informa conteos verificables y escribe una marca de caché completa al terminar. La activación elimina versiones anteriores solo después de completar el nuevo inventario. La primera instalación puede tomar control; una actualización posterior queda en espera y se activa desde una apertura futura de la portada.
3. La caché esencial incluye la portada, rutinas canónicas e imágenes estáticas de sus referencias. Videos/GIF no bloquean ni forman parte del estado de versión offline completa.
4. La preferencia local de red es `ask` por defecto, `always` o `wifi`. El permiso de `ask` es de sesión de página/apertura y se muestra en el splash con controles explícitos y estimación de tamaño, sin diálogo modal nativo. Se puede continuar sin descargar; la comprobación queda pendiente. Si el navegador no identifica el tipo de conexión, `wifi` no inicia una descarga y `ask` solicita permiso. No se implementa sincronización de datos de usuario.
5. Si hay error de cuota, la instalación se reintenta una vez tras eliminar cachés Gymratik obsoletas/incompletas, preservando una caché completa previa (o una caché legacy que contenga la portada y las cuatro rutinas). La caché parcial de la instalación fallida se elimina. Si no existe una versión completa, el splash comunica la espera y reintenta cada 30 s y al recibir `online`.
6. El splash usa un sprite local con poses de prensa de piernas y press de pecho sentado. `prefers-reduced-motion` fija una pose estática.

## Consecuencias y límites

- El estado de avance se mide por recursos completados; el inventario conoce el tamaño local de los archivos, pero no garantiza el tamaño efectivo transferido (compresión/protocolo). No se presenta como bytes descargados.
- El navegador no expone universalmente si la conexión es Wi-Fi o celular. En navegadores sin Network Information API, `Solo Wi‑Fi` difiere la descarga y `Preguntar cada vez` consulta antes de iniciar.
- Un usuario puede continuar con la última caché activa durante la preparación de una actualización. Los registros de perfil, series e historial permanecen en IndexedDB/localStorage y no se alteran.
- Solo se eliminan cachés con prefijo Gymratik; siempre se preserva una caché con marca completa o, para versiones anteriores al marcador, la candidata que contiene la portada y las cuatro rutinas. Cachés sin clave Gymratik no se modifican.

## Alternativas consideradas

- Activación inmediata con `skipWaiting()`: descartada porque puede reemplazar el worker durante una sesión.
- `cache.addAll()`: descartada porque no permite comunicar avance incremental.
- Precache de GIF y videos: descartado porque aumenta el trabajo de red y no es esencial para iniciar las rutinas.
- Sincronización de datos de usuario: fuera de alcance; el acuerdo cubre únicamente el paquete estático de la PWA.

## Verificación

- `python scripts/build_pwa_service_worker.py` regenera el inventario esencial y `sw.js`.
- `python scripts/validate_repository.py` valida documentación, identificadores y enlaces.
- La activación diferida, la política de conexión y la recuperación ante cuota requieren validación en navegador Android real; no se infiere de validación estática.
