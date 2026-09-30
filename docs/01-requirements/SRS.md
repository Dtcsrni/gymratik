# Especificación de requisitos de software

## 1. Propósito

Definir requisitos verificables para Gymratik: Rutinas y progreso. Este documento es la referencia funcional; las decisiones de implementación viven en arquitectura y ADR.

## 2. Convenciones

- **SHALL / deberá:** obligatorio.
- **SHOULD / debería:** recomendado, con desviación justificada.
- **MAY / podrá:** opcional.
- Prioridad: P0 imprescindible, P1 importante, P2 experimental.

## 3. Actores y sistemas externos

- `PersonalUser`: propietario y único usuario.
- `AndroidClient`: aplicación en Realme GT 6.
- `TezkatliNode`: cómputo e inferencia privada.
- `AmazfitActive`: interfaz auxiliar.
- `ZeppApp`: puente del reloj.
- `HealthConnect`: intercambio de datos de salud en Android.
- `FoodCatalog`: catálogos importados y normalizados.

## 4. Requisitos funcionales

### 4.1 Entrenamiento

- **FUN-TRN-001 · P0:** el sistema deberá iniciar, pausar, reanudar, revisar y finalizar una sesión.
  - Aceptación: cada transición se persiste y se restaura después de cerrar el proceso.
- **FUN-TRN-002 · P0:** una sesión deberá admitir cardio inicial, fuerza y cardio final, permitiendo omitir cualquiera.
  - Aceptación: la sesión final conserva fases realizadas, orden y tiempos.
- **FUN-TRN-003 · P0:** cada serie deberá registrar ejercicio, variante/máquina, repeticiones, carga, unidad, RIR o RPE, tipo y marca temporal.
  - Aceptación: se rechazan cantidades negativas y unidades incompatibles.
- **FUN-TRN-004 · P0:** la pantalla deberá mostrar valores anteriores y objetivo sin navegación adicional.
  - Aceptación: se muestra el registro anterior de la misma variante/equipo.
- **FUN-TRN-005 · P0:** el usuario deberá corregir o deshacer una serie preservando auditoría.
  - Aceptación: la corrección conserva valor previo, valor nuevo, hora y motivo opcional.
- **FUN-TRN-006 · P0:** deberá existir temporizador automático configurable por ejercicio o serie.
  - Aceptación: continúa correctamente tras background o recreación de UI.
- **FUN-TRN-007 · P1:** deberá soportar calentamiento, trabajo, drop set, fallo y series asistidas.
- **FUN-TRN-008 · P1:** deberá calcular discos por lado y calentamientos sin alterar registros.
- **FUN-TRN-009 · P1:** deberá detectar récords con fórmula y versión explícitas.
- **FUN-TRN-010 · P0:** la preparación inicial y de cada serie durará al menos 15 s y la cuenta regresiva continuará correctamente tras recarga o actualización.
  - Aceptación: se persiste el instante de vencimiento; tras reabrir se muestra el tiempo restante y la serie no se inicia antes del vencimiento.
- **FUN-TRN-011 · P1:** durante el descanso mínimo, el usuario podrá omitirlo manteniendo pulsado 5 s el control de serie.
  - Aceptación: el llenado/animación es visible mientras se mantiene; soltar antes cancela sin iniciar la serie; el descanso ya vencido no se marca como omitido.
- **FUN-TRN-012 · P1:** el usuario podrá omitir un ejercicio manteniendo pulsado 10 s un control independiente.
  - Aceptación: mostrar feedback de pulsación; registrar el ejercicio como omitido, no inventar series ni rendimiento, permitir deshacer y avanzar la sesión.

### 4.2 Rutinas y gimnasio

- **FUN-ROU-001 · P0:** el usuario deberá crear, clonar, editar, versionar y archivar rutinas.
- **FUN-ROU-002 · P1:** el sistema deberá proponer rutinas compatibles con objetivo, tiempo, historial y equipo.
- **FUN-ROU-003 · P1:** toda propuesta deberá presentar razones y alternativas.
- **FUN-ROU-004 · P1:** el usuario deberá marcar ejercicios como preferidos, menos recomendados, temporalmente no disponibles o excluidos.
- **FUN-GYM-001 · P1:** el sistema deberá detectar una posible llegada al gimnasio y solicitar confirmación antes de iniciar.
- **FUN-GYM-002 · P0:** el catálogo del gimnasio deberá ser editable, versionado y distinguir verificado de inferido.
- **FUN-GYM-003 · P1:** el estado temporal de una máquina no deberá modificar su existencia en el catálogo.

### 4.3 Nutrición

- **FUN-NUT-001 · P0:** el sistema deberá aceptar alimentos por búsqueda, texto, código de barras, OCR, fotografía y captura manual.
- **FUN-NUT-002 · P0:** una inferencia deberá producir un borrador editable y nunca una entrada confirmada automática.
- **FUN-NUT-003 · P0:** toda cantidad deberá clasificar su método como `MEASURED`, `CALCULATED`, `ESTIMATED`, `ASSUMED` o `USER_CONFIRMED`.
- **FUN-NUT-004 · P0:** un alimento deberá conservar fuente, identificador externo, versión y nivel de calidad.
- **FUN-NUT-005 · P0:** el usuario deberá ajustar, sustituir, dividir, agregar o eliminar componentes antes de confirmar.
- **FUN-NUT-006 · P1:** deberá soportar recetas con ingredientes, masa final, rendimiento y porciones.
- **FUN-NUT-007 · P1:** deberá guardar y reutilizar comidas habituales y porciones personales.
- **FUN-NUT-008 · P1:** una captura precisa deberá admitir múltiples vistas, referencia geométrica o peso visible.
- **FUN-NUT-009 · P1:** deberá advertir ingredientes visualmente ocultos probables sin inventarlos como confirmados.

### 4.4 Suplementos

- **FUN-SUP-001 · P0:** deberá registrar producto, marca, presentación, cantidad por unidad, dosis y hora.
- **FUN-SUP-002 · P0:** deberá permitir confirmar, omitir, posponer o corregir una ingesta.
- **FUN-SUP-003 · P1:** deberá mantener inventario y estimar fecha de reposición.
- **FUN-SUP-004 · P1:** deberá aceptar producto por texto, código u OCR de etiqueta.
- **FUN-SUP-005 · P0:** no deberá generar prescripciones ni modificar dosis por decisión de IA.

### 4.5 IA

- **FUN-AI-001 · P0:** la inferencia deberá ejecutarse solo en el teléfono o Tezkatli.
- **FUN-AI-002 · P0:** todo resultado deberá guardar hash de entrada, modelo, pesos, prompt, preprocesamiento, esquema y tiempos.
- **FUN-AI-003 · P0:** la salida deberá validarse contra un esquema estructurado antes de mostrarse.
- **FUN-AI-004 · P0:** si Tezkatli está ausente, el trabajo deberá permanecer en cola y existir entrada manual.
- **FUN-AI-005 · P1:** el sistema deberá reutilizar correcciones personales antes de ejecutar inferencia pesada cuando exista coincidencia suficiente.
- **FUN-AI-006 · P1:** ningún modelo nuevo deberá promoverse sin evaluación contra baseline y aprobación manual.

### 4.6 Amazfit y Health Connect

- **FUN-WEA-001 · P1:** el reloj deberá mostrar ejercicio/serie actual y permitir confirmar acciones rápidas si la PoC resulta viable.
- **FUN-WEA-002 · P1:** deberá almacenar eventos hasta confirmar recepción.
- **FUN-WEA-003 · P1:** los eventos deberán incluir ID, origen, secuencia, hora y versión.
- **FUN-WEA-004 · P0:** el reloj no será fuente definitiva para repeticiones detectadas automáticamente.
- **FUN-HC-001 · P1:** deberá importar registros autorizados conservando `DataOrigin` y método de grabación.
- **FUN-HC-002 · P1:** deberá exportar sesiones terminadas mediante trabajo puntual.

### 4.7 Sincronización, exportación y recuperación

- **FUN-SYN-001 · P0:** entrenamiento, nutrición manual y suplementos deberán operar offline.
- **FUN-SYN-002 · P0:** toda mutación sincronizada deberá ser idempotente y tolerar reordenamiento y duplicación.
- **FUN-SYN-003 · P0:** Android deberá mostrar trabajos pendientes y fallos recuperables.
- **FUN-SYN-004 · P1:** los borrados sincronizados deberán usar tombstones hasta ser reconocidos.
- **FUN-EXP-001 · P0:** deberá exportar datos y metadatos en un formato documentado.
- **FUN-EXP-002 · P0:** deberá restaurar un respaldo compatible sin pérdida silenciosa.

### 4.8 PWA: inicio, actualización y recursos offline

- **FUN-PWA-001 · P0:** el splash deberá identificar la fase de inicio local y, por separado, el estado de comprobación/descarga de la aplicación y recursos offline; el avance porcentual solo se mostrará cuando sea medible.
  - Aceptación: una descarga muestra recursos completados/total; el inicio local no tiene un timeout fijo; el splash permanece al menos 1 s y no desaparece antes de completar la lectura local; si falla, explica el error y ofrece `Reintentar` sin borrar datos.
- **FUN-PWA-002 · P0:** las comprobaciones de versión y la preparación de recursos deberán ejecutarse en paralelo con la inicialización local y tener límites independientes de 20 s cada una.
  - Aceptación: al vencer un límite, una versión completa previa permanece utilizable y la actualización pendiente se informa dentro de la portada; una actualización nueva no fuerza la recarga de una sesión de entrenamiento abierta.
- **FUN-PWA-003 · P0:** la preparación offline deberá incluir la portada, las cuatro rutinas canónicas, sus imágenes estáticas y los medios animados locales usados como guía visual.
  - Aceptación: la nueva versión solo se considera instalada cuando todo el inventario requerido termina de guardarse en caché; las cuatro rutinas abren sin red, sus imágenes/GIF locales no están rotos y los posters conservan el fallback estático; se informa el progreso por recursos y el tamaño local estimado.
- **FUN-PWA-004 · P1:** el usuario podrá elegir `Preguntar cada vez` (predeterminado), `Permitir siempre` o `Solo Wi‑Fi` para actualizaciones y descargas estáticas.
  - Aceptación: el permiso concedido o denegado dura únicamente la apertura actual; la preferencia se guarda localmente; `Solo Wi‑Fi` difiere la descarga si el navegador no identifica Wi‑Fi; `Preguntar cada vez` y `Solo Wi‑Fi` también respetan `navigator.connection.saveData` cuando está disponible; la pregunta aparece dentro del splash con tamaño estimado y permite continuar sin descargar.
- **FUN-PWA-005 · P0:** ante falta de espacio o una descarga interrumpida, la versión completa anterior y los datos de entrenamiento deberán conservarse.
  - Aceptación: en error de cuota se eliminan cachés Gymratik obsoletas/incompletas y se reintenta una vez, preservando una caché previa completa; una instalación incompleta no activa ni elimina la versión anterior; sin versión offline completa, el splash reintenta al recuperar conectividad y cada 30 s.
- **FUN-PWA-006 · P1:** el splash deberá animar a los personajes Gymratik en prensa de piernas y press de pecho sentado y respetar `prefers-reduced-motion`.
  - Aceptación: hay fases visibles distintas del movimiento; con movimiento reducido se presenta una pose estática accesible y el estado textual continúa visible.
- **FUN-PWA-008 · P1:** durante actividad y descanso de una sesión, el resumen flotante mostrará una mascota Gymratik animada localmente según el sexo opcional del perfil instalado; para sexo no binario, no indicado o perfil inaccesible usará la variante neutral.
  - Aceptación: el perfil se consulta solo en almacenamiento local; actividad muestra un GIF de ejercicio y descanso un GIF de reposo con al menos 24 fps; ambos se sirven offline desde el inventario esencial, son de 128×128 px, se ocultan y paran fuera de esos estados, y `prefers-reduced-motion` sustituye el GIF por la pose estática correspondiente.
- **FUN-PWA-009 · P1:** las actualizaciones deberán respetar las preferencias de red y no reemplazar una versión activa a mitad de la apertura que detectó la actualización.
  - Aceptación: la primera instalación activa después de completar todo el inventario; con una versión activa, la nueva queda en espera y se aplica automáticamente al volver a abrir Gymratik cuando la política permite descargar/activar; `Preguntar cada vez` y `Solo Wi‑Fi` no inician actualizaciones gestionadas por la aplicación si Wi‑Fi no está identificado, salvo una acción manual en una apertura instalada; solicitudes runtime no añaden caché por URL query ni recursos ajenos al inventario.
- **FUN-PWA-010 · P1:** el manifiesto deberá declarar iconos raster locales de 192×192 y 512×512 y ambos estarán disponibles sin conexión.
  - Aceptación: las dimensiones declaradas coinciden con las reales, el generador incorpora automáticamente todos los iconos del manifiesto al precache, y se rechaza cualquier icono ausente, externo o inválido.

### 4.8 Perfil local y administración de datos

- **FUN-PRO-001 · P0:** el usuario deberá poder crear y editar un perfil local con nombre visible, fecha de nacimiento, sexo, altura, objetivo y unidades.
  - Aceptación: los campos se validan, se conservan tras recargar y no requieren conectividad.
- **FUN-PRO-002 · P0:** el sistema deberá asociar el progreso y las sesiones al perfil local activo en IndexedDB v3.
  - Aceptación: una base nueva usa v3; al abrir una base anterior a v3, se eliminan sus almacenes y se crea el esquema v3 vacío. La interfaz informa que el historial anterior se reinició.
- **FUN-PRO-003 · P0:** el usuario deberá consultar sesiones recientes con estado, fecha, rutina y series completadas.
  - Aceptación: una sesión activa o completada aparece sin duplicarse después de recargar.
- **FUN-PRO-004 · P0:** el usuario deberá exportar e importar un respaldo v3 del perfil y sus registros.
  - Aceptación: solo se acepta el esquema 3; un archivo de otro esquema se rechaza antes de modificar los datos.
- **FUN-PRO-005 · P1:** la portada deberá actualizar la ilustración de perfil según el dato seleccionado y mostrar una ilustración general cuando no se especifique una variante.
  - Aceptación: al cambiar el selector sin recargar, las imágenes y textos alternativos se actualizan; ambas variantes se sirven offline y no se persiste una imagen separada del sexo.
- **FUN-PRO-006 · P1:** en la primera apertura de la portada, si no hay datos de usuario definidos en el perfil local, el sistema deberá llevar al usuario a la sección de perfil.
  - Aceptación: un perfil sin nombre, fecha de nacimiento, sexo, altura ni preferencias distintas de los valores predeterminados abre la portada en `#profile`; un perfil con algún dato definido conserva la navegación normal y el progreso existente.
- **FUN-PRO-007 · P1:** la primera sección de la portada deberá mostrar una frase breve, amable y personalizada a partir del historial local reciente de entrenamiento.
  - Aceptación: reconoce las series registradas hoy; si no hay actividad hoy, usa la fecha de la última actividad solo dentro de una ventana de siete días; sin actividad reciente ofrece un mensaje neutral. El texto se deriva localmente, no usa datos corporales ni promete resultados.
- **FUN-PRO-008 · P1:** el usuario podrá registrar repeticiones y carga por serie, consultar esos datos en el historial y recibir una indicación de progresión para el ejercicio.
  - Aceptación: solo se conservan datos asociados a una serie completada; alcanzar el límite superior de repeticiones en todas las series con carga comparable permite sugerir considerar el menor incremento disponible, mientras los demás resultados sugieren mantener la carga e intentar sumar repeticiones. No se cambia la rutina ni la carga automáticamente; el usuario puede omitir la carga.
- **FUN-PRO-009 · P1:** el usuario podrá consultar sus días de entrenamiento más frecuentes y elegir días flexibles para avisos dentro de la PWA.
  - Aceptación: el resumen cuenta sesiones iniciadas en las últimas ocho semanas; los días sugeridos pueden editarse; el aviso aparece al abrir o volver a la portada, se puede descartar por el día, se suprime si ya se entrenó ese día y no se promete entrega con la PWA cerrada.
- **FUN-PRO-010 · P1:** el nombre visible podrá contextualizar la frase de la portada.
  - Aceptación: el texto se construye localmente y se representa como texto, sin interpolación HTML ni envío remoto.
- **FUN-PRO-011 · P0:** el perfil y la lectura o escritura del avance solo estarán disponibles al usar Gymratik en modo de aplicación instalada.
- **FUN-PRO-012 · P1:** la portada deberá proponer la sesión activa del día o el siguiente día de la rotación tras la actividad más reciente.
  - Aceptación: conserva una sesión activa iniciada hoy; si la última sesión fue ayer, propone el día siguiente y envuelve al día 1 después del día 4.
- **FUN-PRO-013 · P1:** el valor numérico de carga deberá poder editarse directamente además del deslizador.
  - Aceptación: acepta decimales válidos en unidad seleccionada y sincroniza ambos controles; no afirma incrementos o rangos propios de una máquina no identificada.
- **FUN-PRO-014 · P1:** el perfil inicial deberá pedir pocos datos, ofrecer el resto como personalización opcional y no volver a interrumpir a quien ya tenga datos guardados.
  - Aceptación: con perfil vacío, la portada abre el formulario simple; con cualquier dato de perfil existente, no redirige ni lo expande. Los campos no esenciales quedan bajo una sección opcional y los datos no se borran ni migran.
- **FUN-PWA-007 · P0:** una actualización local no deberá eliminar progreso de sesión ni almacenes IndexedDB existentes.
  - Aceptación: actualizaciones añaden únicamente stores/índices requeridos; si falta el registro central, la portada recupera los snapshots locales de las cuatro rutinas antes de consultar historial.
  - Aceptación: al abrirse en una pestaña del navegador se muestra una invitación descartable para instalar; se pueden consultar las rutinas, pero la portada no expone perfil, historial ni estadísticas y las rutinas no restauran ni guardan progreso. En modo instalado, perfil e historial vuelven a estar disponibles sin cambiar los datos guardados.

**Estabilidad de rutina:** el objetivo guardado en el perfil es informativo y no altera ejercicios, volumen ni frecuencia del plan. La rutina permanece estable mientras resulte tolerable y permita progresar; su revisión responde a estancamiento persistente, recuperación/adherencia insuficientes, dolor o cambios contextuales, no a una rotación automática por calendario.

## 5. Requisitos no funcionales

### Fiabilidad y disponibilidad

- **NFR-REL-001 · P0:** ninguna serie confirmada deberá perderse por cierre inesperado.
- **NFR-REL-002 · P0:** reintentar la misma operación no deberá duplicar datos.
- **NFR-AVA-001 · P0:** funciones esenciales no dependerán de Tezkatli ni Internet.
- **NFR-REC-001 · P0:** deberá probarse restauración completa antes de considerar confiable el respaldo.

### Rendimiento y eficiencia

- **NFR-PER-001 · P0:** objetivo inicial de mediana menor a 100 ms para persistir una serie en Realme GT 6.
- **NFR-PER-002 · P0:** objetivo inicial de TTFD menor a 500 ms para la sesión activa.
- **NFR-PER-003 · P1:** la UI no deberá bloquearse durante inferencia o sincronización.
- **NFR-EFF-001 · P1:** ubicación y sincronización deberán respetar restricciones de batería y conectividad.

### Seguridad y privacidad

- **NFR-SEC-001 · P0:** Tezkatli no deberá exponerse directamente a Internet público.
- **NFR-SEC-002 · P0:** secretos no deberán existir en código, APK, repositorio o logs.
- **NFR-SEC-003 · P0:** las entradas de imagen/texto deberán validarse y tratarse como no confiables.
- **NFR-PRI-001 · P0:** el usuario deberá controlar retención y eliminación de imágenes.
- **NFR-PRI-002 · P0:** logs y métricas deberán excluir contenido personal por defecto.
- **NFR-PRI-003 · P0:** ningún token, contraseña o identificador de autenticación deberá almacenarse en `localStorage` o IndexedDB.

### Usabilidad, mantenibilidad y compatibilidad

- **NFR-USA-001 · P0:** marcar una serie normal como completada requerirá como máximo dos acciones deliberadas; registrar repeticiones y carga antes de confirmarla requerirá entradas adicionales.
- **NFR-USA-002 · P0:** la UI deberá distinguir pendiente, estimado y confirmado sin depender solo del color.
- **NFR-MAI-001 · P0:** no se permitirán ciclos entre módulos Gradle.
- **NFR-MAI-002 · P0:** cambios arquitectónicos deberán documentarse mediante ADR.
- **NFR-COM-001 · P0:** contratos persistentes o de red incompatibles deberán aumentar versión o incluir migración.

### IA

- **NFR-AI-001 · P0:** la IA no deberá confirmar ni sobrescribir datos del dominio.
- **NFR-AI-002 · P0:** métricas de IA deberán reportar dataset, tamaño, condiciones y versión.
- **NFR-AI-003 · P1:** la interfaz deberá mostrar incertidumbre o limitación útil, no “confianza” autodeclarada por el LLM.

## 6. Restricciones de datos

- Masa persistida en unidad base entera o decimal de escala fija.
- Tiempo persistido como `Instant` más zona cuando sea relevante.
- Identificadores globalmente únicos para eventos sincronizables.
- Ningún valor derivado sustituye el dato fuente.
- Toda métrica derivada conserva `algorithmVersion`.

## 7. Supuestos abiertos

- Capacidad exacta y software final de Tezkatli.
- API level y compatibilidad real del Amazfit Active.
- Inventario físico del gimnasio.
- Umbral personal aceptable de error en porciones.
- Frecuencia y política final de respaldos.
