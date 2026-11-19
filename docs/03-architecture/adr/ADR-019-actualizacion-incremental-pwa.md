# ADR-019 — Versionado explícito y actualización incremental verificable de la PWA

**Estado:** Accepted
**Fecha:** 2026-11-19
**Supersede:** ADR-017 (las decisiones de retención de datos de ADR-018 siguen vigentes)

## Contexto

El Service Worker identificaba la versión mediante un prefijo del hash de su inventario. La interfaz mostraba ese hash como si fuera una versión de producto. Cada instalación nueva volvía a descargar el inventario completo aunque la caché activa ya tuviera la mayoría de los recursos sin cambios. La política de red también había sido forzada temporalmente a descarga automática en cualquier conexión.

## Decisión

1. `app-version.json` será la fuente de la versión semántica visible. El generador sincroniza la marca de portada, el Service Worker y `release-manifest.json`. El manifiesto lista cada recurso precacheado (excepto a sí mismo) con URL, tamaño y SHA-256, además del SHA-256 del generador; su `buildId` se deriva de la versión, del generador y de esas entradas, por lo que el manifiesto no crea una referencia hash circular.
2. Antes de descargar recursos, el worker verifica que el manifiesto servido coincide con sus constantes embebidas. Examina recursos de la última caché marcada completa, reutiliza los bytes cuyo tamaño y SHA-256 coinciden y descarga solo los que falten o difieran. Verifica las respuestas antes de guardarlas y escribe la marca de caché completa únicamente al final. Se mantienen hasta seis descargas concurrentes y un reintento de cuota.
3. Se conserva una caché completa previa durante la preparación. Al completarse la instalación, la aplicación autoriza la activación inmediatamente; `controllerchange` recarga la página. Si la nueva versión falla antes de terminar el inicio, la página ofrece recargar para reintentar. No hay rollback automático.
4. `Preguntar cada vez` es el valor predeterminado. En una red móvil o de tipo desconocido, la aplicación no inicia por sí misma `registration.update()`; la interfaz ofrece un botón que expresa la autorización para comprobar y descargar. `Solo Wi-Fi` se comporta como antes, y `Permitir siempre` conserva descargas automáticas.
   La preferencia se guarda con una nueva clave local; se ignora la clave de la versión anterior porque esa versión la sobrescribía forzosamente con `always` y ya no permite distinguir la selección original del usuario.
5. La preferencia solo regula acciones iniciadas por la aplicación. El navegador puede comprobar el script del Service Worker o iniciar una instalación según su propia política; la PWA no puede garantizar tráfico celular cero. Las versiones semánticas y el manifiesto son metadatos de integridad, no firmas criptográficas de autoría.
6. El progreso informa conteos del inventario. Los bytes totales representan los tamaños de recursos que la instalación determinó que necesita descargar, no el tráfico de red exacto (que depende de compresión y protocolo).

## Consecuencias y riesgos

- Las instalaciones con recursos compartidos pueden transferir bastante menos. El worker aún lee y calcula SHA-256 de recursos de la caché previa, lo que añade trabajo de CPU y lectura local en cada actualización; no se afirma un ahorro medido hasta probarlo en los navegadores objetivo.
- Si un recurso cambió pero se sirve con contenido distinto al manifiesto, la instalación se cancela y conserva la versión activa. Una nueva versión que sí se activó pero falla al arrancar permanece activa hasta que el usuario reintente o publique otra versión; no existe recuperación automática de caché anterior.
- La app puede pedir aprobación antes de sus propias comprobaciones, pero no controlar solicitudes internas del navegador. Un Service Worker previamente instalado puede también detectar versiones conforme al ciclo de vida y la política del navegador.
- `release-manifest.json` se publica como un archivo adicional dentro del paquete offline. Despliegues parciales donde `sw.js` y el manifiesto no correspondan fallan cerrados durante la instalación.

## Alternativas consideradas

- Mostrar el hash de caché como versión de producto: descartado porque no es legible ni semánticamente controlado.
- Descargar de nuevo el paquete completo: descartado por transferencia redundante; se mantiene como comportamiento natural de primera instalación o de una caché anterior no verificable.
- Rollback automático tras un fallo de inicio: pospuesto porque requiere definir una señal de salud de arranque fiable para todas las pantallas y una política para cachés antiguas; la decisión explícita es conservar y permitir reintento.
- Delegar todas las actualizaciones al navegador: descartado porque no ofrece a Gymratik control sobre inventario, progreso, verificación y preferencias.

## Verificación

- `python scripts/build_pwa_service_worker.py` genera portada, manifiesto y Service Worker coherentes.
- `python -m pytest tests/test_service_worker.py tests/test_homepage.py -q` verifica contratos de versión, integridad, reutilización y preferencias.
- `python scripts/validate_repository.py` comprueba la consistencia del repositorio antes de integración.
- La verificación del tráfico y del tiempo de hashing en datos móviles y Android físico requiere medición en dispositivos y host publicado.
