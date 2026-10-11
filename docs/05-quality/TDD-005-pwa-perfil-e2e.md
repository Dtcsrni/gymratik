# TDD-005 — PWA, perfil local y verificación E2E

**Estado:** `In progress`
**Versión:** `0.3`
**Fecha:** `2026-10-09`
**Diseño asociado:** [SDD-004](../03-architecture/SDD-004-generacion-validacion-publicacion-pwa.md)
**Fuentes normativas:** [SRS](../01-requirements/SRS.md), [ADR-013](../03-architecture/adr/ADR-013-perfil-local-y-respaldo-pwa.md), [ADR-014](../03-architecture/adr/ADR-014-progresion-e-horarios-locales-pwa.md), [ADR-015](../03-architecture/adr/ADR-015-base-local-v3-exclusiva.md), [ADR-017](../03-architecture/adr/ADR-017-politica-de-actualizacion-y-cache-pwa.md), [ADR-018](../03-architecture/adr/ADR-018-retencion-manual-de-datos-pwa.md)

## 1. Objetivo y frontera

Demostrar requisitos PWA, perfil, sesión, historial, respaldo y recursos offline
en pruebas automatizadas y navegador. `FUN-TRN-010..013` se limita al
calentamiento, descanso y omisión interactiva en las fichas web. No se afirma
comportamiento de app Android nativa.

Niveles de evidencia: **A** automatizada, **V** navegador/visual, **H**
dispositivo/validación humana. Un check estático no equivale a E2E.

## 2. Matriz de trazabilidad

| Requisito SRS | Caso | Automatizado | E2E/navegador | Evidencia adicional | Estado de esta ejecución |
|---|---|---|---|---|---|
| FUN-PWA-001 | TST-PWA-001 splash, lectura local, error/reintento y estados separados | `test_homepage_shows_a_brief_splash_until_local_data_initialization_settles`; `test_homepage_exposes_persistent_progress_dashboard` | apertura, fallo IndexedDB, reintento sin pérdida | A+V; fallo real de almacenamiento H | Parcial |
| FUN-PWA-002 | TST-PWA-002 tareas paralelas y límites independientes | contratos de 20 s y flujo de inicio en `test_homepage.py` | actualización con sesión activa, ninguna recarga forzada | A+V; Android H | Parcial |
| FUN-PWA-003 | TST-PWA-003 inventario offline, cuatro rutinas, medios y completitud | `test_generated_worker_cache_fingerprint_matches_current_precache`, `test_all_routine_images_are_local_and_packaged`, `test_optional_gifs_reveal_packaged_posters_when_offline`, resto de `test_service_worker.py`, `validate_repository.py`, generador | `scripts/e2e_routine_activity_check.py --offline-only`: cotejo de inventario y carga sin red de medios/imágenes de las cuatro rutinas y fallback de ruta profunda desconocida | A+V; publicación y modo avión en Realme GT 6 H | Parcial |
| FUN-PWA-004 | TST-PWA-004 preferencias ask/always/wifi, permiso por apertura y continuar | `test_network_permission_is_explained_and_chosen_inside_the_splash`; `test_cellular_update_is_manual_and_detected_version_uses_the_mascot_animation`; `test_network_defer_reason_distinguishes_cellular_from_data_saver` | elegir las tres políticas, tipo de conexión desconocido, ahorro de datos activo y abrir sin descargar | A+V; API de conexión variable | Parcial |
| FUN-PWA-005 | TST-PWA-005 cuota/interrupción preserva caché e historial | marcadores de caché, `QuotaExceededError` y lógica de limpieza en pruebas SW | provocar cuota/fallo de red con datos sintéticos; confirmar versión previa | A+V; cuota Android H | Parcial |
| FUN-PWA-006 | TST-PWA-006 poses diferenciadas y movimiento reducido | `test_homepage_uses_animated_original_pair_outside_install_invitation`; CSS reducido | observar poses, contrastar `prefers-reduced-motion` | A+V; lector de pantalla H | Parcial |
| FUN-PWA-007 | TST-PWA-029 preservar stores y snapshots locales ante actualización | `test_existing_indexeddb_v1_or_v2_is_upgraded_without_deleting_stores_or_local_routine_state`; `test_missing_central_progress_is_recovered_from_local_routine_snapshot` | `scripts/e2e_routine_activity_check.py`: recarga en preparación y descanso conserva actividad y progreso; estado legado sin fecha queda archivado y fuera del avance semanal | A+V; migración con datos reales/Realme GT 6 H | Parcial |
| FUN-PWA-008 | TST-PWA-030 mascota local animada por estado/perfil | `tests/test_mascot_motion.py`; `test_service_worker.py` | `scripts/e2e_routine_activity_check.py`: actividad/descanso con perfiles femenino, masculino y neutral; idle/reducido; imagen 128×128, cambio visible de fotogramas, carga offline | A+V; Realme GT 6 H | Parcial |
| FUN-PWA-009 | TST-PWA-031 actualización versionada, red identificada y caché runtime acotada | `test_detected_pwa_updates_activate_automatically_on_allowed_networks`; `test_updates_are_staged_until_the_application_authorizes_activation`; `test_runtime_cache_is_bounded_to_precache_resources_and_revalidates_http_cache`; fingerprint SW | primera instalación toma control al completar; actualización permanece en espera hasta reapertura o solicitud manual; tipo de red desconocido no autoriza actualización automática; query y rutas fuera de scope no crean caché | A+V; host publicado y Chrome Android H | Parcial |
| FUN-PWA-010 | TST-PWA-032 iconos 192/512 coherentes e incluidos offline | `test_pwa_icon_is_the_shared_mascot_mark`; `test_pwa_precache_derives_installed_icons_from_manifest`; `test_generated_worker_cache_fingerprint_matches_current_precache` | E2E offline carga y decodifica ambos iconos | A+V; Chrome Android instalado H | Parcial |
| FUN-PRO-001 | TST-PRO-001 validar/guardar perfil local | `test_profile_is_saved_and_normalized_in_local_fallback`, contrato de campos | editar y recargar cada campo | A+V | Parcial |
| FUN-PRO-014 | TST-PRO-014 formulario inicial progresivo y redirección solo sin datos | `test_initial_profile_form_is_progressive_and_optional`; `test_profile_editor_closes_and_page_reloads_after_successful_save` | perfil vacío abre formulario simple; perfil existente permanece en portada; extras siguen accesibles | A+V | Parcial |
| FUN-PRO-015 | TST-PRO-015 resumen de portada e historial estadístico local | `tests/test_records.py`; `test_homepage_exposes_persistent_progress_dashboard` | validar filtros 7/30/todo, conteos, gráfica semanal, cargas por ejercicio y detalles de sesión con fixture local; verificar que refrescar no muta datos | A+V | Parcial |
| FUN-PRO-002 | TST-PRO-002 asociación al perfil y migración no destructiva IndexedDB v3 | `test_existing_indexeddb_v1_or_v2_is_upgraded_without_deleting_stores_or_local_routine_state`, schema tests | actualizar desde stores v1/v2 con perfil/sesión/snapshot; verificar mismo contenido y que stores desconocidos no se borran | A+V; migración/restauración H | Parcial |
| FUN-PRO-003 | TST-PRO-003 sesiones recientes sin duplicación | `test_activity_requires_completed_warmup_and_at_least_one_work_set_for_all_routines`, store runtime | completar/reabrir una sesión | A+V | Parcial |
| FUN-PRO-004 | TST-PRO-004 backup v3 export/import, inválido no muta | `test_backup_import_round_trip_preserves_profile_and_session_summary`; `test_backup_import_rejects_older_schemas` | exportar, limpiar fixture y restaurar; comparar todo antes/después | A+V; restauración de release H | Parcial |
| FUN-PRO-005 | TST-PRO-005 avatar por sexo y variante general offline | `test_homepage_derives_effort_mascot_from_profile_sex`, inventario SW | cambiar selector y revisar imagen/alt en viewport móvil | A+V | Parcial |
| FUN-PRO-006 | TST-PRO-006 onboarding a perfil solo si vacío | `test_profile_and_progress_reads_are_gated_by_installation`; contrato de homepage | perfil vacío vs definido, conservar hash y avance | A+V | Parcial |
| FUN-PRO-007 | TST-PRO-007 motivación por hoy/7 días/antiguo/futuro/vacío | `tests/test_progress_store_runtime.py` y contrato de portada | historial fixture y texto seguro visible | A+V | Parcial |
| FUN-PRO-008 | TST-PRO-008 reps/carga/historial/progresión; no mutación automática | `test_repetition_selector_uses_exercise_range_plus_four_without_defaulting`, `test_capture_persists_only_completed_sets_with_valid_repetitions` | `scripts/e2e_routine_activity_check.py`: selectores de cada ejercicio, gesto, limpiar valores, entrada decimal, cambio kg/lb y progreso de una serie por rutina | A+V; dispositivo H | Parcial |
| FUN-PRO-009 | TST-PRO-009 días frecuentes y avisos flexibles de primer plano | contratos de perfil/runtime | editar días, descartar, ya entrenado, reabrir portada | A+V; PWA cerrada explícitamente fuera | Parcial |
| FUN-PRO-010 | TST-PRO-010 nombre local con `textContent` | `test_homepage_exposes_local_profile_and_backup_controls` y análisis de interpolación | nombre con caracteres HTML se presenta como texto | A+V | Parcial |
| FUN-PRO-011 | TST-PRO-011 gate no instalado/instalado | `test_uninstalled_browser_cannot_read_or_write_profile_or_progress`; homepage gate tests | pestaña: navegar/consultar sin progreso; modo instalado: perfil disponible | A+V; Android H | Parcial |
| FUN-PRO-012 | TST-PRO-012 reanudar sesión activa y avanzar por última rutina de hoy/ayer | `test_homepage_selects_active_session_or_next_routine_from_latest_activity`; `test_homepage_cta_continues_a_session_started_today_even_before_first_set` | ayer Día 1 → Día 2; sesión activa hoy con cero series muestra `Continuar Día N` y abre esa rutina; Día 4 → Día 1 | A+V; Realme GT 6 H | Parcial |
| FUN-PRO-016 | TST-PRO-016 rollover semanal archiva todas las capturas previas sin duplicarlas | `test_home_dashboard_rolls_previous_week_state_but_preserves_a_session_started_today`; `test_home_dashboard_clears_unscoped_legacy_completion_before_it_can_be_adopted`; `test_unscoped_legacy_completion_is_reset_instead_of_adopted_as_current_week`; `test_previous_week_progress_is_excluded_from_current_plan_without_deleting_history` | avanzar reloj a lunes local, abrir portada repetidamente y luego rutina; archivo previo conserva captura completa y semana de origen; historial terminado y sesión actual persisten | A; E2E móvil y zona horaria H pendientes | Parcial |
| FUN-PRO-017 | TST-PRO-017 ubicación y formato de datos | prueba de contenido y export/import v3 | verificar en perfil el origen, IndexedDB v3, clave fallback, snapshots/archivo JSON localStorage y JSON `gymratik-backup` esquema 3 | A+V | Partial |
| FUN-PRO-018 | TST-PRO-018 solo borrar mediante acción manual confirmada | pruebas de llamadas de borrado, importación y reset | instalación/actualización/rotación no borra; reset e importación reemplazante piden confirmación; revisar límites de limpieza externa | A+V; reinstalación física H | Partial |
| FUN-PRO-013 | TST-PRO-013 edición decimal y rango orientativo ±25% por ejercicio | `test_all_26_exercises_have_explicit_equipment_appropriate_load_ranges`; `test_editable_load_value_persists_decimal_independently_of_slider_step` | comprobar cálculo desde referencia en los 24 perfiles que cubren 26 ejercicios; kg/lb, límites, decimal y que una carga personal fuera del intervalo se conserve | A+V; referencias calibrables por persona/aparato | Parcial |
| NFR-REL-001 | TST-PWA-012 serie confirmada después de cierre inesperado | persistencia de capture y v3 | cerrar/reabrir tras guardar; no borrar datos del usuario | A+V; process death H | Parcial |
| FUN-TRN-010 | TST-TRN-010 temporizador de preparación de 15 s, reanudable | contrato de preparación persistente en los cuatro HTML | `scripts/e2e_routine_activity_check.py`: recargar tras 5 s y completar los 10 s restantes antes de iniciar serie | A+V; Realme GT 6 H | Parcial |
| FUN-TRN-011 | TST-TRN-011 mantener 5 s para omitir descanso | `test_series_flow_uses_one_button_and_enforces_minimum_rest`; `test_all_routines_expose_direct_decimal_load_entry_and_hold_feedback` | feedback visible; liberar temprano; verificar límite mínimo | A+V; Realme GT 6 H | Parcial |
| FUN-TRN-012 | TST-TRN-012 mantener 10 s para omitir ejercicio sin falsear series | `test_all_routines_expose_direct_decimal_load_entry_and_hold_feedback`; `test_skipped_exercise_advances_completion_without_fabricating_sets` | mantener, liberar temprano, revisar progreso y deshacer | A+V; Realme GT 6 H | Parcial |
| FUN-TRN-013 | TST-TRN-013 cierre manual parcial preserva progreso | `test_partial_session_capture_is_closed_and_distinguishable`; prueba de contrato del control en las cuatro rutinas | iniciar sesión, confirmar una serie, dejar otra sin confirmar, terminar día y recargar; historial marca «Terminada · parcial», cuenta solo la serie confirmada y conserva la sesión tras reapertura | runtime A+V; dispositivo H | Parcial |
| NFR-REL-002 | TST-PWA-013 retry idempotente | `test_progress_store_serializes_writes_and_merges_fallback`, temporales | reintentar mismo evento y comprobar una sola fila | A+V | Parcial |
| NFR-AVA-001 | TST-PWA-014 shell y fichas sin Internet | inventario y cache-first tests | instalar paquete, modo avión, abrir cuatro días | A+V; modo avión H | Pendiente H |
| NFR-REC-001 | TST-PWA-015 restauración íntegra v3 | round-trip/invalid schema tests | comparar perfil, progreso, sesión, actividad y rendimiento | A+V; gate de release H | Parcial |
| NFR-SEC-002 | TST-PWA-020 ausencia de secretos | `validate_repository.py` | revisar bundle publicado y consola/logs | A+V | Parcial |
| NFR-SEC-003 | TST-PWA-021 entradas locales no confiables | import v3 rechaza esquemas inválidos | probar JSON corrupto, grande, mal tipado y nombre HTML | A+V | Parcial |
| NFR-PRI-001 | TST-PWA-022 retención de imágenes | PWA no captura ni persiste fotos personales | verificar import/export e IndexedDB no guardan fotos | A | Parcial |
| NFR-PRI-002 | TST-PWA-023 logs sin contenido personal por defecto | static/runtime log tests | simular error de perfil y revisar console/logs | A+V | Parcial |
| NFR-PRI-003 | TST-PWA-024 no guardar tokens/credenciales | PWA no implementa autenticación | escanear `localStorage`, IndexedDB y bundle | A | Parcial |
| NFR-USA-001 | TST-PWA-025 acción única y límite de acciones | `test_series_flow_uses_one_button_and_enforces_minimum_rest` | completar, descanso, hold 5 s y siguiente serie en cada día | A+V | Parcial |
| NFR-USA-002 | TST-PWA-026 estado textual además de color | labels/status y anunciadores | lector de pantalla, foco/teclado y contraste | A+V; accesibilidad H | Parcial |
| NFR-MAI-002 | TST-PWA-027 cambio arquitectónico con ADR | revisión de docs/ADR | revisar diff de arquitectura | A | Aplicable si hay cambio arquitectónico |
| NFR-COM-001 | TST-PWA-028 compatibilidad de contratos/migración | schema v3 y rechazo v1/v2 | importar/actualizar desde bases de fixture | A+V | Parcial |

Los requisitos y pruebas heredados de Android, servidores, IA, métricas físicas
y batería quedan fuera de esta matriz. `NFR-PRI-001` limita el alcance: la PWA
no captura ni persiste fotos personales.

## 3. Definición de casos

### Casos de inicio/actualización

- **TST-PWA-001 — Splash y lectura local:** abrir con almacén vacío, demora y fallo de lectura. El texto identifica fase; reintento conserva datos y el splash no termina antes del resultado local.
- **TST-PWA-002 — Paralelismo y timeout:** bloquear actualización hasta 20 s y lectura local independientemente. La UI permite continuar con versión completa sin recarga de sesión activa.
- **TST-PWA-003 — Inventario offline y actualización:** regenerar `sw.js` y comprobar que su fingerprint coincide con el contenido actual de cada recurso precacheado (`test_generated_worker_cache_fingerprint_matches_current_precache`). `scripts/e2e_routine_activity_check.py` instala el worker en contexto aislado, espera el marcador completo, comprueba cada ruta del precache y recorre las cuatro fichas sin red; imágenes fallidas de GIF didácticos opcionales deben revelar un poster local decodificado. La prueba de publicación de una versión nueva sobre una instalación física y preservación con cuota/red interrumpida sigue pendiente.
- **TST-PWA-004 — Preferencias de red:** comprobar `ask` inicial, `always`, `wifi`, permiso de una apertura, conexión desconocida, estimación y opción de continuar.
- **TST-PWA-005 — Fallo de instalación:** simular cuota y respuesta de red interrumpida. Se conserva caché anterior completa e historial; se borra solo la parcial y se reintenta una vez.
- **TST-PWA-006 — Animación accesible:** comprobar dos fases de los personajes, `prefers-reduced-motion`, pose estática y estado legible.

### Casos de perfil local

- **TST-PRO-001 — Edición de perfil:** guardar campos permitidos, rechazar valores fuera de formato y reabrir con valores conservados sin red.
- **TST-PRO-002 — Perfil y esquema v3:** crear esquema actual; fixture v1/v2 añade stores actuales sin borrar stores o claves locales según ADR-015.
- **TST-PRO-003 — Historial reciente:** completar/reabrir una sesión y comprobar estado, fecha, rutina y series sin duplicados.
- **TST-PRO-004 — Backup v3:** exportar e importar datos de fixture; comparar perfil, progreso, sesiones, actividad y rendimiento. Versión inválida no modifica nada.
- **TST-PRO-005 — Avatar:** cambiar variante en vivo, verificar texto alternativo y recursos offline; selección desconocida usa variante general.
- Las definiciones canónicas de TST-PRO-006 y TST-PRO-007 están en `TEST_STRATEGY.md`; las de TST-PRO-008, TST-PRO-009 y TST-PRO-010 están en `TDD_SDD_SERIES.md`. Esta matriz las referencia sin duplicar su definición.
- **TST-PRO-011 — Gate instalado:** pestaña permite consultar rutinas sin leer/escribir perfil/progreso; modo instalado habilita ambos.
- **TST-PRO-012 — Rotación de rutina:** sesión activa de hoy continúa; actividad más reciente en Día 1 de ayer propone Día 2; Día 4 envuelve al Día 1.
- **TST-PRO-013 — Edición precisa de carga:** tocar el valor abre entrada decimal, aplica límites y actualiza slider/borrador; cambiar kg/lb conserva conversión. Incrementos de máquina no se presumen sin modelo identificado.
- **TST-PRO-014 — Formulario inicial progresivo:** perfil vacío abre el editor con solo nombre y selección de mascota visibles; campos opcionales avanzados permanecen cerrados. Perfil con datos guardados no cambia la ruta ni expande el editor. Guardar un perfil aún vacío muestra validación y no cierra el onboarding como si estuviera completo.
- **TST-PRO-015 — Consulta estadística local:** con sesiones sintéticas en varias fechas, el selector filtra por periodo y las tarjetas, la tendencia semanal, la distribución por rutina, las cargas por ejercicio y el historial coinciden con los datos guardados. Confirmar que la vista solo llama a `getHistory`, representa texto mediante `textContent` y no cambia perfil, sesiones ni progreso.
- **TST-PWA-029 — Actualización no destructiva:** fixtures IndexedDB v1/v2 conservan stores y datos existentes mientras crean los actuales; fallback v1 y snapshots `fitlovers-dayN-series-v1` no se eliminan.
- **TST-PWA-030 — Mascota de actividad:** validar existencia, transparencia, tamaño 128×128 y cadencia mínima 24 fps de cada GIF y pose estática; en cuatro rutinas comprobar estado visual de actividad/descanso, selección local femenina/masculina y fallback neutral; comprobar ocultamiento en idle/preparación, `prefers-reduced-motion` y disponibilidad sin red.
- **TST-PWA-031 — Actualización escalonada y caché acotada:** validar que solo la primera instalación se activa automáticamente tras completar el precache; una actualización sobre una instalación activa queda en espera hasta una apertura o recarga manual autorizada. Bajo `ask`/`wifi`, una red desconocida o datos móviles no identificados como Wi-Fi no disparan la comprobación automática de la aplicación. Variantes con query y GET fuera del inventario no crean entradas de caché; los recursos del precache usan revalidación HTTP al actualizar (`test_updates_are_staged_until_the_application_authorizes_activation`, `test_runtime_cache_is_bounded_to_precache_resources_and_revalidates_http_cache`, pruebas de política en `tests/test_homepage.py`). La activación y el ahorro de bytes en navegador/dispositivo físico siguen sujetos a prueba instalada.
- **TST-PWA-032 — Iconos instalables y offline:** validar PNG rasterizados de 192×192 y 512×512 contra las dimensiones declaradas en el manifiesto, su inclusión derivada en el precache y su decodificación en el E2E offline.
- **TST-MED-007 — Técnica y geometría de animaciones propias:** antes de integrar un recurso, revisar individualmente las cuatro poses contra las referencias exactas del ejercicio. Registrar el ángulo didáctico elegido y verificar orientación del personaje respecto a la máquina, asiento/apoyos, agarre, puntos de contacto, piezas móviles/pivotes, trayectoria y extremos del recorrido. Rechazar si el personaje mira o trabaja en sentido contrario, queda de espaldas al punto de trabajo, usa la pieza incorrecta, pierde un apoyo, cambia de escala/ángulo entre poses o la máquina cambia de geometría. Revisar inicio, final, los dos intermedios y el bucle; que renderice no demuestra técnica correcta.
- **TST-TRN-010 — Preparación reanudable:** calentamiento y preparación de serie requieren 15 s; recarga durante ambos conserva el vencimiento y reanuda el tiempo restante.
- **TST-TRN-011 — Omisión de descanso:** mantener 5 s muestra llenado; soltar antes cancela; iniciar antes del descanso mínimo solo ocurre tras mantener el tiempo completo.
- **TST-TRN-012 — Omisión de ejercicio:** mantener 10 s completa la acción, un toque/soltar antes no lo hace; el resumen marca omitido, no aumenta series ni registros de rendimiento y deshacer lo revierte.
- **TST-TRN-013 — Cierre parcial:** confirmar el diálogo termina la sesión con `completionKind=partial`; una serie no confirmada sigue pendiente; se guarda en el almacén local, se reabre con el mismo estado y el resumen/historial la distingue de una rutina completa. Cancelar el diálogo no altera el estado.

### Casos no funcionales aplicables

- **TST-PWA-012 — Persistencia tras cierre:** guardar serie y reconstruir sesión desde almacenamiento tras cerrar/reabrir; no borrar la base para la prueba.
- **TST-PWA-013 — Idempotencia:** repetir la misma captura y comprobar un registro lógico y estadísticas estables.
- **TST-PWA-014 — Offline:** servir shell y cuatro rutinas tras precache y modo avión; verificar imágenes esenciales y marcar evidencia H solo en dispositivo real.
- **TST-PWA-015 — Restauración:** round-trip v3 y comparación exacta de entidades; requiere gate humano de release.
- **TST-PWA-020 — Secretos:** escanear repo y recursos servidos; no incluir tokens/contraseñas en source o logs.
- **TST-PWA-021 — Entrada no confiable:** importar JSON corrupto, estructura profunda/grande y nombre con HTML; rechazar sin cambio parcial ni ejecución.
- **TST-PWA-022 — Retención de imágenes:** confirmar que PWA no captura ni persiste fotos personales; no atribuirle capacidades de borrado inexistentes.
- **TST-PWA-023 — Logs privados:** provocar errores con datos de fixture y revisar consola/logs sin nombre, fecha de nacimiento ni contenido de registro.
- **TST-PWA-024 — Sin credenciales:** buscar tokens/contraseñas/identificadores de autenticación en `localStorage`, IndexedDB y bundles.
- **TST-PWA-025 — Esfuerzo de serie:** en cada día, acción única y máximo dos acciones deliberadas para completar una serie normal; descanso mínimo bloquea.
- **TST-PWA-026 — Estado no solo color:** probar pendiente/estimado/confirmado con texto, foco y tecnología asistiva; reporte de contraste aparte.
- **TST-PWA-027 — ADR:** cualquier modificación de responsabilidades, almacenamiento o protocolo de actualización incluye ADR aprobado/versionado.
- **TST-PWA-028 — Compatibilidad:** fixtures de esquema v3 aceptan; v1/v2 se rechazan o pasan por migración declarada, nunca por conversión silenciosa.

## 4. Casos transversales de rutina

Para cada tarjeta de cada día se verifica:

1. Hay exactamente una acción de serie visible como máximo; cambia entre
   iniciar, completar, descanso y siguiente serie. El control de calentamiento
   no se cuenta como botón de serie.
2. No se confirma una serie antes de que venza el mínimo de descanso. Mantener
   pulsado durante 5 s omite el descanso y prepara la serie siguiente; el
   llenado indica cuánto falta y soltar antes cancela sin iniciar serie.
3. Selector de repeticiones usa enteros de `min` a `max+4`; un rango `8–12`
   produce `8..16`, no la cadena prescrita ni un rango global. El deslizador y
   los controles `−/+` comparten los límites; el valor elegido se anuncia,
   queda en el borrador y no confirma una serie por sí solo. En los extremos,
   el control correspondiente queda deshabilitado. El estado activo/foco es
   perceptible y la animación de pulsación respeta `prefers-reduced-motion`.
   `test_repetition_selector_uses_exercise_range_plus_four_without_defaulting`
   comprueba contratos y los cuatro días; `scripts/e2e_routine_activity_check.py`
   verifica en Chromium los gestos básicos, limpieza, edición decimal y unidades.
   La ejecución en dispositivo físico sigue pendiente.
4. Cada rutina usa un espacio de claves distinto. No se confunden borrador,
   serie confirmada, historial ni caché de recursos.

5. Calentamiento y preparación previa a la serie duran 15 s como mínimo. Si se
   recarga la PWA durante la cuenta, se recupera el vencimiento persistido.
6. El control independiente de omisión de ejercicio requiere 10 s sostenidos,
   muestra feedback y registra un estado omitido distinto de series completadas.
7. Tocar el número de carga permite introducir un decimal válido, sincronizado
   con el deslizador. No se calibran saltos de máquinas sin identificar el
   modelo físico y su stack.

## 5. Comandos reproducibles disponibles

```powershell
python scripts/validate_repository.py
python scripts/validate_contracts.py
python -m unittest discover -s tests -p 'test_*.py' -q
python scripts/e2e_routine_activity_check.py
python scripts/validate_canonical_routines.py
python scripts/validate_routine_media.py
python scripts/build_mascot_motion_gifs.py
python scripts/build_pwa_service_worker.py
git diff --check
```

`scripts/e2e_routine_activity_check.py` es el driver E2E reproducible de navegador
para cuatro rutinas, controles y actividad visual; requiere Playwright para
Python y Chromium disponible. No es una prueba CI hasta integrarse al pipeline.
La emulación móvil no equivale a validar instalación, publicación, modo avión ni
gestos en un Realme GT 6 físico; esos casos **H** siguen pendientes.

## 6. Estado y cierre

La matriz no cambia requisitos existentes ni convierte objetivos de Realme GT
6 en medidas de escritorio. Mantener `In progress` hasta que cada fila tenga
artefacto reproducible, resultado real y limitaciones. Actualizar
`TRACEABILITY.md` junto con esta tabla al cerrar cada caso.
