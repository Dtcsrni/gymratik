# Auditoría de interfaz y recursos de las cuatro rutinas

Fecha: 2026-11-25
Alcance: 28 ejercicios, recursos visuales, prescripción, carga, selector de discos, control de series, textos de estado y navegación de sesión.

## Hallazgos y criterio de cierre

| ID | Prioridad | Hallazgo | Criterio verificable | Estado |
|---|---|---|---|---|
| AUD-TMR-001 | P1 | Al acabar el último set de un ejercicio, podía quedar un descanso o el cronómetro del ejercicio corriendo mientras la rutina seguía. | El último set fija `endedAt`, elimina el descanso de ese ejercicio y no lo publica como actividad; estados antiguos completados dejan de avanzar. | Corregido en el contrato compartido y los cuatro HTML. |
| AUD-WGT-001 | P1 | El slider y la entrada directa normalizaban la selección a un incremento de perfil; en lb se redondeaba a enteros y el valor visible podía diferir de la posición elegida. | Slider, entrada, conversión kg/lb y valor guardado conservan la misma carga; el selector muestra hasta dos decimales. | Corregido en el contrato compartido y los cuatro HTML. |
| AUD-PLT-001 | P2 | El encabezado «Discos» mostraba la carga elegida aunque no hubiera piezas en la suma; además, las placas se veían como círculos concéntricos poco legibles. | Sin piezas, el encabezado muestra «Añadir» y la suma permanece en cero; cada placa distingue centro, aro, unidad y diámetro por masa. | Corregido; visual vectorial CSS sin depender de una foto única para todos los pesos. |
| AUD-MED-001 | P2 | La referencia del curl sentado del Día 1 mostraba a una persona, pero el `alt` y la etiqueta decían que era una máquina aislada. | Texto alternativo y etiqueta describen que es una demostración con persona y equipo. | Corregido en el HTML y en `repair_day1_canonical.py`. |
| AUD-MED-002 | P2 | El manifiesto del Día 2 indica que la procedencia individual de las parejas Inicio/Final y referencias anatómicas heredadas no está documentada; parte está embebida como `data:image`. | Documentar procedencia/licencia o sustituir por un recurso aprobado; no atribuir la foto a una persona o máquina sin evidencia. | Pendiente de evidencia; las imágenes adjuntas HEIC no se copiaron al producto. |
| AUD-MED-003 | P1 | Día 4, prensa unilateral alterna: el GIF `2287-V07qpXy` mostraba empuje con ambas piernas a la vez. | La referencia enseña la prensa a una pierna, coherente con el título y la ejecución alterna. | Corregido con `1425-WWD6FzI` (prensa inclinada a una pierna). |
| AUD-MED-004 | P2 | Día 1, ejercicios 4–6: las tarjetas ofrecen referencias estáticas incompletas; la apertura inversa carece de imagen de fases y los curls no exponen un recorrido animado junto a su referencia. | Cada tarjeta indica claramente cuándo la imagen es solo referencia o añade fases verificables del movimiento. | Pendiente: patrón descrito por texto y referencias, requiere curar/autorizar medios adicionales antes de agregarlos. |
| AUD-MED-005 | P2 | Día 2, hip thrust: el GIF muestra el patrón con apoyo elevado, pero no la máquina de la tarjeta; el alt y la etiqueta lo describían como demostración oficial en máquina. | El recurso se identifica como referencia del patrón y no como imagen de la máquina. | Corregidos etiqueta, texto alternativo y nota en el generador y el HTML. |
| AUD-E2E-001 | P2 | El E2E funcional inicial agotaba 60 s al volver de una rutina a la portada, y su fixture disparaba un precache innecesario de 177 recursos. | La matriz de portada/flujo usa permiso de red denegado en el fixture; los cuatro días completan sus series en E2E. | Corregido; cuatro días funcionales y responsive validados. La prueba aislada offline sigue pendiente: el precache termina, pero Edge headless no conserva una registration activa o controladora. |

## Recorrido por ejercicio

Se cotejaron título, equipo declarado, referencias, fases, texto alternativo y recurso animado o estático. Las ilustraciones sirven para mostrar el patrón y no certifican el modelo exacto de la máquina instalada.

| Día | Ejercicio | Resultado de revisión visual y de contenido |
|---|---|---|
| 1 | Jalón al pecho | Polea alta y tracción vertical; fases y GIF representan el jalón. |
| 1 | Remo alto unilateral | Referencia Panatta y recorrido unilateral corresponden al remo alto; la foto no confirma la máquina personal del usuario. |
| 1 | Remo horizontal en máquina | Recorrido sentado y referencia de remo horizontal coherentes; la referencia está embebida en el HTML. |
| 1 | Apertura inversa en máquina | Referencia de butterfly inverso y recorrido de apertura posterior coherentes. |
| 1 | Curl de bíceps en máquina | Curl con brazo apoyado; referencia aislada y patrón preacher coherentes. |
| 1 | Curl de bíceps sentado en máquina | Patrón sentado coherente; corregida la descripción de una imagen que incluye a una persona. |
| 1 | Press de pecho sentado en máquina | Empuje sentado; fases y referencia aislada corresponden al patrón. |
| 2 | Hack squat | Sentadilla guiada en hack; fotos de referencia y recorrido muestran el patrón. |
| 2 | Hip thrust | El GIF muestra hip thrust con apoyo elevado sin identificar la máquina de la tarjeta; se corrigió su etiqueta/alt para dejar explícita esa diferencia. La procedencia y licencia siguen pendientes. |
| 2 | Prensa de piernas | Empuje en prensa inclinada; fases y GIF concuerdan con el patrón. |
| 2 | Curl femoral en máquina | Flexión de rodilla sentado; máquina, fases y GIF concuerdan. |
| 2 | Extensión de piernas | Extensión de rodilla sentado; fases y GIF concuerdan. |
| 2 | Pantorrillas de pie | Elevación de talones de pie; fases y GIF concuerdan. |
| 2 | Abducción de cadera sentada | Separación de rodillas en máquina; referencia y GIF concuerdan. |
| 3 | Press de pecho sentado en máquina | Empuje horizontal; referencia, fases y GIF concuerdan. |
| 3 | Press inclinado convergente en máquina | Empuje inclinado convergente; medios locales concuerdan. |
| 3 | Pec deck / contractor de pecho | Aducción horizontal de hombros; medios locales concuerdan. |
| 3 | Press de hombro en máquina | Empuje vertical sentado; medios locales concuerdan. |
| 3 | Elevación lateral en máquina | Abducción de hombros con apoyos; medios locales concuerdan. |
| 3 | Jalón de tríceps en polea | Extensión de codos en polea alta; medios locales concuerdan. |
| 3 | Extensión de tríceps sobre cabeza con cuerda | Extensión de codos por encima de la cabeza; medios locales concuerdan. |
| 4 | Prensa unilateral alterna | El antiguo GIF mostraba ambas piernas. Sustituido por `1425-WWD6FzI`, que muestra el patrón unilateral en prensa inclinada; la tarjeta y la técnica indican alternar lados. |
| 4 | Peso muerto rumano en Smith | Bisagra de cadera con barra guiada; recurso vectorial propio y GIF corresponden al patrón. |
| 4 | Curl femoral tumbado | Flexión de rodillas tumbado; máquina, fases y GIF concuerdan. |
| 4 | Abducción de cadera sentada | Separación de rodillas; medios locales corresponden al patrón. |
| 4 | Aducción de cadera sentada | Aproximación de rodillas; medios locales corresponden al patrón. |
| 4 | Elevación de pantorrilla sentada | Flexión plantar sentado; medios locales corresponden al patrón. |
| 4 | Crunch con elevación de piernas sentada | Flexión controlada de tronco con apoyo de piernas; medios locales corresponden al patrón descrito. |

## Controles y textos revisados

- **Repeticiones:** límites vinculados al rango del ejercicio, botones +/- y opción para quitar el registro; el valor no se preselecciona como resultado confirmado.
- **Carga:** rango validado por perfil, entrada decimal, selector kg/lb, último registro normal y modo separado de aproximación. El incremento orientativo del perfil ya no altera la carga elegida.
- **Discos:** suma de piezas de ambas unidades, botón de quitar por pieza, transferencia bloqueada cuando está vacía o fuera del rango y aviso de que no incluye barra/máquina.
- **Series/descanso:** iniciar serie, descanso entre sets, máquina ocupada, omitir con pulsación larga, deshacer y completar; el temporizador de una tarjeta completada queda cerrado.
- **Accesibilidad/copy:** las 28 tarjetas tienen `alt` no vacío en imágenes; las referencias se presentan como apoyo del patrón. El manifiesto del Día 2 conserva un pendiente de procedencia.

## Validación ejecutada

- `python -m unittest discover -s tests` — 266 pruebas, OK.
- `python scripts/validate_repository.py` — `VALIDATION_OK markdown=91`.
- `python scripts/validate_canonical_routines.py` — `CANONICAL_ROUTINES_OK routines=4`.
- `python scripts/validate_routine_media.py` — `ROUTINE_MEDIA_OK routines=4`.
- `python scripts/e2e_routine_activity_check.py` — validó portada, responsive y el flujo funcional de series en los cuatro días; la corrida general quedó fallida en el tramo offline al esperar el controlador del service worker.
- `python scripts/e2e_routine_activity_check.py --resources-only` — cuatro rutinas, recursos visuales, GIF, selector de discos y traspaso exacto, OK.
- `python scripts/e2e_routine_activity_check.py --quote-only` — alternancia de frase famosa con fuente y frase Gymratik original, retrato y fallback, OK.
- `python scripts/e2e_routine_activity_check.py --celebration-only` — celebración y contador en cuatro días, OK.
- `python scripts/e2e_routine_activity_check.py --cover-only` — animación de portada y matriz de siete tamaños, OK.
- `python scripts/e2e_routine_activity_check.py --machine-pending-layer-only` — selector de máquina ocupada en cuatro días, OK.
- `python scripts/e2e_routine_activity_check.py --load-warning-only` — confirmación kg/lb y borrador, OK.
- **Pendiente:** E2E offline reproducible en Edge headless. El precache llega a completarse, pero a los 30 s la página informa `controller=null`, sin workers `active`, `waiting` o `installing`, ni registration; no se declara validado el uso offline.
- La matriz E2E usa navegador sintético; no sustituye la comprobación física en Android.
