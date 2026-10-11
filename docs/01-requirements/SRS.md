# Requisitos de software de Gymratik PWA

## 1. Propósito y alcance

Este SRS define el producto activo: una PWA instalable para consultar cuatro rutinas canónicas, registrar y revisar el progreso en el dispositivo, y preparar/actualizar recursos para uso sin conexión. `PWA` significa aplicación web progresiva: una aplicación web que puede instalarse desde un navegador y usar un Service Worker para recursos offline.

El usuario es una sola persona. La PWA no tiene cuenta, backend ni sincronización de datos de usuario. Los datos de progreso permanecen en almacenamiento local del origen. El respaldo es manual mediante un archivo exportado e importado por el usuario.

Quedan fuera del alcance vigente: nutrición y suplementos; administración o detección de gimnasios y equipos; IA; app Android nativa; Amazfit/Zepp, Health Connect y otras integraciones; cuentas, nube y sincronización entre dispositivos. Los identificadores heredados de esos temas se conservan como diferidos en [DEFERRED_SCOPE.md](DEFERRED_SCOPE.md); no son trabajo comprometido ni requisitos activos.

## 2. Convenciones

- **SHALL / deberá:** obligatorio.
- **SHOULD / debería:** recomendado, con desviación justificada.
- **MAY / podrá:** opcional.
- Prioridad: P0 imprescindible para la PWA; P1 importante; P2 experimental.
- `Implemented` solo se asigna cuando existe evidencia ejecutada; `Partial` indica cobertura incompleta; `Planned` indica ausencia de evidencia de implementación.

## 3. Actor y entorno

- `PwaUser`: persona que abre la PWA en un navegador compatible, instalada o en una pestaña.
- `Browser`: proporciona almacenamiento local, Cache API, Service Worker y, si está disponible, señales de conectividad.
- `LocalFile`: respaldo JSON elegido, guardado o restaurado por el usuario.

La compatibilidad efectiva depende del navegador y el sistema operativo. Las pruebas automatizadas o emuladas no demuestran por sí solas comportamiento en un teléfono físico.

## 4. Requisitos funcionales

### 4.1 Inicio, instalación y recursos offline

- **FUN-PWA-001 · P0:** el inicio deberá distinguir la lectura de datos locales de la comprobación y preparación de recursos; solo mostrará porcentajes medibles.
  - Aceptación: el progreso de descarga informa recursos completados y total; la lectura local no se cancela por un timeout fijo; los errores explican la causa disponible y ofrecen reintentar sin borrar datos.
- **FUN-PWA-002 · P0:** la inicialización local y la preparación de recursos deberán poder avanzar en paralelo sin interrumpir una rutina abierta.
  - Aceptación: la versión completa previa sigue utilizable ante una actualización fallida; la actualización pendiente se informa y no fuerza una recarga durante la sesión.
- **FUN-PWA-003 · P0:** la preparación offline deberá incluir la portada, las cuatro rutinas canónicas y el inventario visual local vigente.
  - Aceptación: solo se declara completo el paquete después de guardar todo el inventario requerido; las cuatro rutinas abren sin red y muestran los recursos locales disponibles.
- **FUN-PWA-004 · P1:** el usuario podrá elegir `Preguntar cada vez` (predeterminado), `Permitir siempre` o `Solo Wi-Fi` para descargas gestionadas por la PWA.
  - Aceptación: una autorización temporal solo dura la apertura actual; la preferencia queda local; si el navegador no identifica Wi-Fi, no se inicia una descarga automática bajo `Solo Wi-Fi`; la interfaz ofrece continuar sin descargar.
- **FUN-PWA-005 · P0:** una descarga interrumpida o un error de cuota no deberá eliminar la versión offline completa anterior ni los datos de usuario.
  - Aceptación: la descarga incompleta no se activa; la recuperación elimina solo cachés Gymratik obsoletas/incompletas y reintenta una vez; los almacenes de progreso no se borran.
- **FUN-PWA-006 · P1:** el splash deberá animar los personajes locales y respetar `prefers-reduced-motion`.
  - Aceptación: con movimiento reducido se muestra una pose estática accesible y el estado sigue explicado en texto.
- **FUN-PWA-007 · P0:** una actualización de la PWA no deberá eliminar progreso de sesión ni almacenes IndexedDB existentes.
  - Aceptación: las actualizaciones preservan stores y registros; si falta el registro central se recuperan snapshots conocidos de las cuatro rutinas antes de consultar historial. En una pestaña no instalada se pueden consultar rutinas, pero no leer ni guardar progreso personal; en modo instalado se habilitan perfil e historial.
- **FUN-PWA-008 · P1:** durante actividad y descanso de una sesión, el resumen podrá mostrar una mascota animada local según el perfil instalado.
  - Aceptación: usa variante neutral si no hay preferencia aplicable; los recursos se sirven offline, se ocultan fuera de actividad/descanso y respetan `prefers-reduced-motion`.
- **FUN-PWA-009 · P1:** las actualizaciones deberán respetar la política de red y no reemplazar la versión activa durante la apertura que detectó la actualización.
  - Aceptación: la primera instalación toma control al completar el inventario; una versión nueva queda en espera hasta una apertura o acción permitida; tipo de conexión desconocido no autoriza descarga automática bajo `Preguntar cada vez` o `Solo Wi-Fi`; solicitudes runtime no amplían la caché fuera del inventario.
- **FUN-PWA-010 · P1:** el manifiesto declarará iconos raster locales válidos de 192×192 y 512×512, incluidos en el paquete offline.
  - Aceptación: dimensiones, rutas y archivos coinciden; iconos externos, ausentes o inválidos fallan la validación.

### 4.2 Perfil, sesiones e historial local

- **FUN-PRO-001 · P0:** el usuario podrá crear y editar un perfil local básico.
  - Aceptación: los campos disponibles se validan y persisten tras recargar sin conectividad.
- **FUN-PRO-002 · P0:** el progreso y las sesiones deberán almacenarse en IndexedDB v3 del origen PWA.
  - Aceptación: instalar, abrir o actualizar Gymratik conserva los datos disponibles en el mismo origen; migraciones y datos no interpretables nunca provocan limpieza silenciosa; una importación se valida antes de modificar el estado.
- **FUN-PRO-003 · P0:** el usuario podrá consultar sesiones locales recientes.
  - Aceptación: estado, fecha, rutina y series completadas se muestran sin duplicar una sesión al recargar.
- **FUN-PRO-004 · P0:** el usuario podrá exportar e importar un archivo de respaldo JSON v3 de su perfil y registros locales.
  - Aceptación: solo se importa esquema 3; se valida antes del reemplazo y se pide confirmación; un archivo inválido o de versión incompatible no muta los datos.
- **FUN-PRO-005 · P1:** la portada reflejará localmente la preferencia de ilustración del perfil y ofrecerá una variante general.
  - Aceptación: imágenes y textos alternativos cambian al editar la preferencia; los recursos están en el paquete offline.
- **FUN-PRO-006 · P1:** la portada ofrecerá completar el perfil inicial cuando no existan datos definidos.
  - Aceptación: el formulario inicial no elimina ni altera progreso existente.
- **FUN-PRO-007 · P1:** la portada podrá mostrar una frase derivada del historial local reciente.
  - Aceptación: el texto no usa datos corporales, no promete resultados y no se envía a un servicio.
- **FUN-PRO-008 · P1:** el usuario podrá registrar repeticiones y carga por serie y consultar una sugerencia local de progresión.
  - Aceptación: solo datos de series completadas alimentan la sugerencia; nunca se cambia automáticamente una rutina o carga.
- **FUN-PRO-009 · P1:** el usuario podrá consultar días frecuentes y configurar avisos que aparecen al abrir o volver a la PWA.
  - Aceptación: la PWA no promete avisos con la aplicación cerrada.
- **FUN-PRO-010 · P1:** el nombre visible podrá contextualizar localmente el mensaje de portada.
  - Aceptación: se representa como texto, nunca como HTML interpolado ni se envía remotamente.
- **FUN-PRO-011 · P0:** perfil, historial y escritura del avance solo estarán disponibles en modo instalado.
  - Aceptación: una pestaña sin instalar no lee ni modifica datos personales de entrenamiento.
- **FUN-PRO-012 · P1:** la portada propondrá continuar una sesión activa de hoy o el siguiente día de la rotación.
  - Aceptación: una sesión activa de hoy se conserva aun con cero series; el enlace abre el día correcto; la rotación vuelve al día 1 después del día 4.
- **FUN-PRO-013 · P1:** la carga se podrá editar mediante entrada numérica además del deslizador.
  - Aceptación: valores decimales válidos y unidad seleccionada se conservan de manera coherente; el selector presenta un intervalo por ejercicio de ±25% alrededor de una referencia inicial rotulada como orientativa, sin recortar cargas registradas fuera de ese intervalo. Las referencias en kg no son equivalencias universales entre máquinas ni prescripción individual; ajustar la carga al esfuerzo y la ejecución observados. [ACSM, Position Stand 2026](https://acsm.org/resistance-training-guidelines-update-2026/).
- **FUN-PRO-014 · P1:** el formulario inicial será breve y dejará los datos opcionales bajo solicitud del usuario.
  - Aceptación: un perfil existente no causa redirección ni pérdida de datos.
- **FUN-PRO-015 · P1:** la portada y el historial mostrarán un resumen de sesiones, series, repeticiones y cargas locales.
  - Aceptación: los filtros no escriben ni borran registros; solo compara cargas del mismo ejercicio y unidad; ausencia de dato no se interpreta como cero.
- **FUN-PRO-016 · P0:** el avance operativo pertenecerá a la semana local actual y se renovará sin eliminar capturas anteriores.
  - Aceptación: avance anterior deja de contar para la semana actual; sesiones terminadas permanecen en historial; snapshots fuera de semana se conservan en el archivo local antes de renovar la vista operativa; abrir portada varias veces no duplica el archivo; una sesión iniciada hoy conserva calentamiento, series, tiempos y selecciones al navegar o actualizar, incluso con cero series.
- **FUN-PRO-017 · P1:** la interfaz explicará dónde residen los datos y sus formatos.
  - Aceptación: identifica IndexedDB `entrenamiento-progress` v3, el fallback `entrenamiento-progress-fallback-v3`, los snapshots/archivo JSON de localStorage y la exportación `gymratik-backup` esquema 3.
- **FUN-PRO-018 · P0:** Gymratik solo eliminará datos de usuario tras una acción manual explícita.
  - Aceptación: los controles de reinicio y reemplazo por importación explican el alcance y requieren confirmación; instalación, inicio, actualización, migración y rotación semanal conservan datos; la documentación distingue el ciclo de vida externo del almacenamiento del navegador/sistema operativo.

### 4.3 Interacción de rutina en la PWA

- **FUN-TRN-010 · P0:** la preparación inicial y de cada serie durará al menos 15 s y continuará tras recarga o actualización.
  - Aceptación: el instante de vencimiento persiste; no inicia una serie antes de terminar la cuenta regresiva.
- **FUN-TRN-011 · P1:** durante el descanso mínimo, el usuario podrá omitirlo manteniendo pulsado 5 s el control de serie.
  - Aceptación: el feedback es visible; soltar antes cancela y un descanso vencido no se marca como omitido.
- **FUN-TRN-012 · P1:** el usuario podrá omitir un ejercicio manteniendo pulsado 10 s un control independiente.
  - Aceptación: la interfaz registra solo la omisión, permite deshacer y no inventa series o rendimiento.
- **FUN-TRN-013 · P0:** el usuario podrá terminar manualmente una rutina incompleta y conservar el progreso local de esa sesión.
  - Aceptación: «Terminar día» cierra la sesión como parcial, persiste hora de cierre y series confirmadas en IndexedDB o fallback local; no confirma series activas/no marcadas, no borra snapshots ni historial y se distingue de una rutina completada en el resumen y el historial. Una nueva instalación o actualización no cambia estos datos.

La rutina canónica no cambia automáticamente según el objetivo del perfil, el calendario o una inferencia.

## 5. Requisitos no funcionales

### Fiabilidad y disponibilidad

- **NFR-REL-001 · P0:** una serie confirmada deberá sobrevivir a una recarga o cierre ordinario de la pestaña mientras el almacenamiento del origen siga disponible.
- **NFR-REL-002 · P0:** reintentar la persistencia de la misma acción no duplicará la sesión o serie.
- **NFR-AVA-001 · P0:** la portada, rutinas y datos locales ya guardados deberán seguir disponibles sin conexión después de completar la preparación offline.
- **NFR-REC-001 · P0:** la exportación e importación v3 deberán validarse con restauración de un fixture sintético antes de considerar fiable el flujo de respaldo.

### Seguridad y privacidad

- **NFR-SEC-002 · P0:** secretos y datos personales reales no deberán existir en el repositorio, fixtures ni logs.
- **NFR-SEC-003 · P0:** importaciones y entradas de usuario se tratarán como datos no confiables, con validación de tipo, tamaño y esquema antes de usarse.
- **NFR-PRI-001 · P0:** la PWA no solicitará ni almacenará fotografías personales en el alcance vigente.
- **NFR-PRI-002 · P0:** los diagnósticos no incluirán nombre, perfil, sesiones ni cargas por defecto.
- **NFR-PRI-003 · P0:** la PWA no implementará autenticación; no almacenará credenciales ni tokens.

### Usabilidad y mantenibilidad

- **NFR-USA-001 · P0:** completar una serie normal requerirá como máximo dos acciones deliberadas, además de capturar repeticiones/carga si el usuario decide ingresarlas.
- **NFR-USA-002 · P0:** pendiente, guardado, error y dato opcional se distinguirán con texto o semántica además del color.
- **NFR-MAI-002 · P0:** los cambios de arquitectura significativa de la PWA tendrán un ADR actualizado.
- **NFR-COM-001 · P0:** los cambios incompatibles del esquema de respaldo o almacenamiento tendrán versión explícita y una migración probada.

## 6. Restricciones y límites

- Cache API contiene recursos de la aplicación; IndexedDB/localStorage contienen datos locales del usuario. La caché de recursos no es sincronización ni respaldo del historial.
- No hay recuperación automática entre dispositivos. El usuario guarda una exportación fuera del dispositivo y controla su traslado.
- IndexedDB y localStorage pertenecen al origen y perfil del navegador. `navigator.storage.persist()` puede solicitar persistencia adicional, pero la PWA no controla la política de borrado del navegador o del sistema operativo durante una desinstalación, limpieza manual o cambio de origen/perfil.
- Actualizar la PWA y migrar IndexedDB debe preservar los datos aún disponibles en el mismo origen.
- No se afirma compatibilidad física ni cobertura offline completa hasta probar recursos y flujos en el navegador objetivo.

## 7. Supuestos por verificar

- Navegadores objetivo y capacidades de instalación/almacenamiento.
- Comportamiento del paquete offline en el dispositivo Android objetivo.
- Tamaño de descarga real, distinto del tamaño de archivos del inventario.
- Restauración manual desde un archivo v3 en el navegador objetivo.
