# ADR-020 — Estabilización y rollback seguro de actualizaciones PWA

**Estado:** Accepted
**Fecha:** 2026-11-24
**Supersede:** ADR-019, solo en la política de confirmación y recuperación de versiones.

## Contexto

Una instalación precargada se verificaba antes de activarse, pero la caché
completa anterior se eliminaba al activar la nueva. Un fallo de arranque o de
escritura local podía dejar una sesión sin controles funcionales; recargar solo
repetía el fallo. Los datos personales viven en IndexedDB/localStorage y deben
permanecer fuera de la caché de recursos.

## Decisión

1. El worker conserva la versión activa anterior si está marcada completa y
   elimina cachés Gymratik más antiguas/incompletas. Descargas no verificadas
   siguen sin activarse.
2. La versión activa entra en una ventana de estabilización de 24 horas. La
   portada y las rutinas instaladas notifican inicio correcto solo después de
   comprobar escritura y lectura de un registro temporal aislado en el almacén
   `meta` de IndexedDB v3 y leer perfil e historial. La comprobación elimina su
   propio registro temporal y no toca stores de progreso, sesión o actividad.
3. Un fallo de inicio, una excepción no controlada durante el arranque o un
   `training-storage-error` sin respaldo local funcional solicita rollback. El
   worker solo lo acepta durante la ventana y si existe una caché anterior
   completa. Los fallos recuperables cubiertos por el fallback local no disparan
   rollback.
4. El worker conserva el marcador de rollback en la caché candidata y sirve
   todos los recursos de la versión estable. La portada estable muestra un
   aviso fijo de rollback con una acción explícita para reintentar la candidata;
   no hay reintento automático en bucle. Si no existe versión estable completa,
   se muestra reintentar y se informa que no fue posible volver atrás.
5. No se migran, eliminan ni reemplazan datos de entrenamiento al activar,
   revertir o reintentar. Cambios futuros al esquema local requieren su propia
   migración y pruebas de actualización/restauración.

## Consecuencias y riesgos

- Se ocupa espacio de caché para una versión previa completa hasta una nueva
  actualización. Ante cuota, la instalación conserva la versión activa y puede
  cancelar el paquete candidato.
- El rollback cubre fallos observables por el cliente y la comprobación de
  almacenamiento; no puede detectar una corrupción silenciosa no observable ni
  garantizar el comportamiento físico de un dispositivo.
- La ventana de 24 horas limita regresiones tardías; después, la app no cambia
  automáticamente de versión por errores de almacenamiento.
- El usuario puede reintentar deliberadamente una versión candidata; si vuelve
  a fallar durante la ventana, el worker la revierte de nuevo sin ciclo
  automático.

## Alternativas

- Confirmar la versión solo tras una evaluación del usuario: descartada porque
  añade una acción en el flujo de entrenamiento y permite posponer
  indefinidamente la protección.
- Confiar en recargar la pantalla: descartada porque no cambia la versión que
  controla las respuestas offline.
- Restaurar o migrar datos desde la caché: descartada porque la caché no es
  autoridad de datos personales.

## Verificación

- `TST-PWA-035` prueba conservación de caché, rollback, aislamiento de la
  comprobación IndexedDB, opción de reintento y límite temporal.
- `python scripts/validate_repository.py` comprueba requisitos y artefactos.
- Prueba en Chrome Android y Realme GT 6 sigue siendo evidencia humana necesaria
  para validar la interacción real del Service Worker y almacenamiento local.
