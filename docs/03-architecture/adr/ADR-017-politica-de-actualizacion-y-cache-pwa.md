# ADR-017 — Política de actualización, red y caché acotada de la PWA

**Estado:** Accepted
**Fecha:** 2026-09-28
**Supersede:** ADR-016

## Contexto

La revisión del código frente a ADR-016 encontró tres divergencias: el worker ejecutaba `skipWaiting()` también en actualizaciones; `Preguntar cada vez` autorizaba actualizaciones con tipo de red desconocido; y el manejador `fetch` guardaba cualquier GET del mismo origen, incluyendo variantes de URL con parámetros. El inventario generado al 2026-09-28 contiene 147 recursos precacheados que suman 43 926 118 bytes (41,89 MiB) medidos en disco; junto con `sw.js` (143 839 bytes), el tamaño estimado del paquete es 44 069 957 bytes (42,03 MiB). Incluye GIF y animaciones locales que se conservan porque el uso offline de la guía visual es parte de la experiencia existente.

## Decisión

1. La primera instalación puede tomar control únicamente después de descargar y marcar completo todo el inventario. Una actualización posterior permanece en `waiting`; la portada la activa automáticamente al abrir Gymratik cuando la política de red lo permite. Una actualización descubierta durante esa apertura queda lista y se aplica en la apertura siguiente; una solicitud manual de actualización puede activarla al terminar la descarga actual. No se solicita intervención para una actualización autorizada y no se interrumpe una sesión con cambio de controlador a mitad del flujo.
2. Las descargas gestionadas por la aplicación se permiten en Wi‑Fi identificada, con `Permitir siempre` o mediante una acción manual en una apertura ya instalada. Con `Preguntar cada vez` o `Solo Wi‑Fi`, un tipo de conexión ausente/ambiguo no autoriza descarga automática. El aviso expone la razón y el gesto/botón de actualización manual.
3. La PWA no puede garantizar tráfico celular cero: el navegador puede comprobar o instalar actualizaciones del Service Worker por su cuenta. La política controla las llamadas y activaciones solicitadas por la aplicación, no el comportamiento interno de Chrome.
4. Las respuestas de recursos estáticos se revalidan (`no-cache`) para permitir validación HTTP condicional. El runtime solo guarda URLs del inventario precacheado; las búsquedas de caché ignoran parámetros, pero las respuestas con query no crean entradas adicionales. Las solicitudes externas al scope del registro no se interceptan.
5. Los datos del usuario continúan en IndexedDB/localStorage, separados de Cache API. Un cambio de versión, limpieza de cachés o migración de la base no debe eliminar el perfil, el historial ni el estado de rutina.

## Consecuencias

- La actualización protege el controlador anterior hasta que el paquete nuevo esté completo y difiere el cambio de controlador a la próxima apertura cuando el paquete se descubre durante el inicio actual.
- La revalidación puede reducir la transferencia cuando el host ofrece ETag/Last-Modified y respeta la revalidación; esa reducción no se da por medida ni garantizada hasta probar los encabezados del host publicado.
- El paquete offline completo permanece relativamente grande: 41,89 MiB de precache, más 143 839 bytes de `sw.js` en la transferencia inicial. Reducirlo o convertirlo en paquetes descargables por rutina requiere una decisión aparte porque cambia qué técnicas quedan disponibles sin conexión. La prueba de estimación hace fallar cambios futuros si el tamaño anunciado queda desfasado del inventario generado.
- La preferencia de red es local a este dispositivo y no sincroniza datos de entrenamiento.

## Alternativas consideradas

- Activar con `skipWaiting()` en cada instalación: descartado para actualizaciones porque la nueva versión puede reemplazar el controlador de una página que aún usa la anterior.
- Autorizar `Preguntar cada vez` cuando no se conoce el tipo de red: descartado por consumir datos sin una decisión explícita.
- Guardar toda respuesta GET del origen: descartado por crecimiento no acotado de caché y duplicación de variantes de consulta.
- Retirar GIF o animaciones del paquete: pospuesto hasta acordar el compromiso entre transferencia y guía visual offline.

## Verificación

- `python -m pytest tests/test_homepage.py tests/test_service_worker.py -q` verifica los contratos de red, activación y caché acotada.
- `python scripts/build_pwa_service_worker.py` regenera el Service Worker y su fingerprint.
- E2E sintético verifica actualización, paquete offline y rutas profundas; E2E físico Android verifica que el navegador instalado aplique el worker completo y preserve IndexedDB.
- La eficiencia de revalidación y el tráfico real en datos móviles quedan sujetos a medición sobre el host publicado y las versiones de Chrome objetivo.
