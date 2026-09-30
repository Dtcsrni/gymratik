# Serie documental TDD y SDD

## 1. Propósito y significado local

Este documento define la serie de documentos que gobernará los siguientes
incrementos de Gymratik: Rutinas y progreso. En este repositorio:

- **SDD** significa *Software Design Description*: diseño de software. Describe
  responsabilidades, datos, interfaces, estados, invariantes y decisiones de
  implementación.
- **TDD** significa *Test Design Document*: diseño de pruebas. Describe qué se
  verifica, con qué datos, qué evidencia se acepta y qué evidencia no autoriza
  una conclusión.

No sustituyen al `SRS`, a `TEST_STRATEGY.md` ni a los ADR. El `SRS` define qué
debe hacer el producto; los SDD definen cómo se estructura; los TDD definen
cómo se demostrará; los ADR registran decisiones arquitectónicas que cambian
el rumbo del diseño.

## 2. Alcance y fuentes de verdad

La serie cubre dos capas relacionadas pero no intercambiables:

1. **Rutinas canónicas actuales:** HTML autocontenido, builders, manifiestos de
   medios, PWA y comportamiento interactivo de calentamiento, progreso y reset.
2. **Producto Gymratik previsto:** Android local-first, Room,
   outbox, contratos, Tezkatli, nutrición, IA, Zepp, Health Connect,
   recuperación, seguridad y operación.

Fuentes de verdad vigentes:

| Área | Fuente | Regla |
|---|---|---|
| Requisitos | `docs/01-requirements/SRS.md` | No cambiar el alcance mediante un SDD. |
| Arquitectura | `docs/03-architecture/ARCHITECTURE.md` y ADR | Todo cambio significativo requiere ADR. |
| Calidad | `docs/05-quality/TEST_STRATEGY.md` | La cobertura no sustituye evidencia funcional, visual o real. |
| Rutinas | `data/rutinas_autocontenidas/canonicas/` | Es la salida canónica; las fuentes históricas no se parchean como sustituto. |
| Generación | `scripts/build_day2_canonical.py` y `scripts/build_day3_canonical.py` | El resultado debe ser reproducible y auditable. |
| Medios | `data/rutinas_autocontenidas/evidencia/*_media_manifest.json` | Un medio no se considera aprobado por verse correcto. |

## 3. Convención de estado y evidencia

Estados documentales: `Planned`, `In progress`, `Partial`, `Verified`,
`Blocked`. `Verified` exige evidencia ejecutada para el alcance exacto del
documento; no significa que el proyecto completo esté listo para producción.

Tipos de evidencia:

- **A — Automatizada:** script, prueba unitaria, contrato, hash o validación
  reproducible.
- **V — Visual/live:** render en escritorio/móvil, interacción en navegador o
  inspección de UI; no demuestra por sí sola derechos ni seguridad.
- **H — Humana/real:** dispositivo, red, captura física, usuario o revisión
  experta; no se sustituye con mocks o fixtures sintéticos.
- **P — Procedencia:** fuente, identidad, versión y hash del recurso.

Una conclusión debe indicar explícitamente qué combinación de A, V, H y P la
sostiene. Un comando con salida verde no cierra automáticamente V, H o P.

## 4. Línea base de defectos que la serie debe controlar

Estos hallazgos fueron observados en la revisión focalizada del estado actual;
son criterios de regresión, no cambios aplicados por este documento.

| ID | Hallazgo verificable | Impacto | Documento que lo captura |
|---|---|---|---|
| DEF-CAN-001 | Cerrado en la revisión actual: la salida de Día 1 conserva 6 tarjetas contiguas y 20 series contractuales. | La ficha y el flujo representan el volumen anunciado; conservar como regresión. | `SDD-001`, `TDD-002` |
| DEF-CAN-002 | Cerrado en la revisión actual: la navegación guiada de Día 3 apunta al título siguiente. | Evita mantener al usuario en el ejercicio equivocado; conservar como regresión. | `SDD-002`, `TDD-003` |
| DEF-MED-001 | `dia1` y `dia2` mantienen estados de revisión pendientes y no exponen campos `source_url`/`sourceUrl` por elemento; `dia3` es un arreglo sin el esquema homogéneo de estado, fuente y hash. | No se puede afirmar procedencia técnica completa ni trazabilidad uniforme. | `SDD-003`, `TDD-004` |
| DEF-QA-001 | Cerrado en la revisión actual: el validador y las pruebas cubren estructura y aritmética de las cuatro HTML canónicas. | El contrato detecta regresiones de tarjetas, series y navegación. | `SDD-004`, `TDD-001`, `TDD-002` |
| DEF-FMT-001 | Día 2, Día 3 y Día 4 heredan la plantilla de Día 1; una plantilla canónica incompleta puede propagar defectos a nuevas salidas. | El mecanismo de reutilización conserva un contrato estructural independiente. | `SDD-002`, `SDD-004`, `TDD-005` |

## 5. Serie SDD — diseño de software

La prioridad es resolver primero la capa que ya tiene artefactos ejecutables y
después materializar los módulos Android previstos. Cada SDD debe incluir
contexto, alcance, interfaces, modelo de datos, invariantes, errores,
observabilidad, seguridad, migración/compatibilidad y pruebas asociadas.

| ID | Título y alcance | Dependencias principales | Estado inicial |
|---|---|---|---|
| [SDD-001](../03-architecture/SDD-001-rutina-canonica-versionado.md) | **Modelo de rutina canónica y versionado.** Prescripción, ejercicios, series efectivas, calentamiento, rangos, descansos, RIR, alternativas y versión por día. | `SRS`, `DATA_MODEL`, `DIA_1/2/3_CONTENIDO_Y_MAQUETACION` | In progress |
| SDD-002 | **Plantilla visual y máquina de estados de la ficha.** Estructura de tarjeta, progreso, calentamiento general/específico, bloqueos, descanso, navegación siguiente y reset delegado. | `Rutina_Dia_1...V1.html`, `UX_FLOWS`, decisiones previas de `timingVersion === 3` | Partial |
| [SDD-003](../03-architecture/SDD-003-medios-fallback-procedencia-tecnica.md) | **Medios, fallback y procedencia técnica.** Contrato único de manifiesto, relación ejercicio–recurso, `sourceUrl`, fuente, versión, SHA-256, alt, miniatura y `prefers-reduced-motion`. | `*_media_manifest.json`, `data/rutinas_autocontenidas/README.md` | In progress |
| [SDD-004](../03-architecture/SDD-004-generacion-validacion-publicacion-pwa.md) | **Generación, validación y publicación PWA.** Shell, perfil local, estado instalado, recursos offline, actualización segura, rutinas y límites de publicación personal. | `SRS`, ADR-013..016, `validate_repository.py`, `PWA_ANDROID.md` | In progress |
| SDD-005 | **Gymratik local-first.** `WorkoutSession`, fases, `PerformedSet`, revisiones, temporizador, Room como fuente operativa y recuperación tras process death. | `SRS` FUN-TRN-001..009, `DATA_MODEL`, ADR-003 | Planned |
| SDD-010 | **Progresión y avisos de la PWA.** Carga/repeticiones por serie, recomendación no automática, días frecuentes configurables y aviso al primer plano. | `ADR-014`, `SRS` FUN-PRO-008..010, `progress-store.js`, builders canónicos | In progress |
| SDD-006 | **Sincronización, contratos y recuperación.** Outbox transaccional, estados, claves de idempotencia, reordenamiento, duplicación, tombstones, exportación y restauración. | `SYNC_AND_AI`, ADR-004, ADR-011, JSON Schema | Planned |
| SDD-007 | **Captura nutricional e IA como borrador.** Routing, calidad de entrada, catálogo, procedencia por componente, jobs, validación de esquema, incertidumbre y confirmación humana. | `SRS` FUN-NUT/FUN-AI, `AI_MLOPS`, ADR-006/007/009 | Planned |
| SDD-008 | **Integraciones externas condicionadas.** Tezkatli privado, Health Connect, Zepp/Amazfit y sus adaptadores anticorrupción; ningún dispositivo externo es fuente definitiva sin PoC. | `ARCHITECTURE`, `USE_CASES`, ADR-008/010/012 | Planned |
| SDD-009 | **Seguridad, rendimiento y operación.** Límites de entrada, privacidad, logs saneados, permisos, health/readiness, backup, rollback y métricas en Realme GT 6/Tezkatli. | `THREAT_MODEL`, `RUNBOOK`, `TEST_STRATEGY`, SRS NFR | Planned |

Orden recomendado: `SDD-001 → SDD-002 → SDD-003 → SDD-004` para corregir y
cerrar las rutinas actuales; después `SDD-005 → SDD-006`; finalmente
`SDD-007 → SDD-009` según los spikes del backlog. `SDD-008` no se declara
implementado por tener un puerto o health check.

## 6. Serie TDD — diseño de pruebas

Cada TDD debe contener: objetivo, alcance, fixtures permitidos, precondiciones,
casos positivos/negativos/frontera, datos esperados, comando reproducible,
artefacto de evidencia, requisitos/riesgos cubiertos y limitaciones.

| ID | Título y alcance | Casos mínimos de aceptación | Evidencia | Estado inicial |
|---|---|---|---|---|
| TDD-001 | **Integridad del repositorio y contratos.** | Validador documental; esquemas válidos e inválidos; ejemplos; ausencia de secretos; links internos y formato Markdown. | A | Partial |
| [TDD-002](../05-quality/TDD-002-integridad-rutinas-canonicas.md) | **Integridad semántica de rutinas canónicas.** | Número de tarjetas; índices contiguos; suma de `data-series-keys`; coincidencia con encabezado/dashboard; no contar calentamiento; cuatro días contractuales. | A | Planned |
| TDD-003 | **Comportamiento interactivo de sesión.** | Bloqueo antes del calentamiento; calentamiento global y específico; completar/deshacer si aplica; descanso; navegación al siguiente índice; reset de estado, UI y `localStorage`; cero errores de consola. | A + V | Partial |
| [TDD-004](../05-quality/TDD-004-medios-formato-y-correspondencia.md) | **Medios, formato y correspondencia visual.** | Rutas; ausencia de imágenes/GIF; decodificación; hash; thumbnail/fallback; fuente y versión; alt; reduced motion; revisión visual por ejercicio. | A + V + P | In progress |
| [TDD-005](../05-quality/TDD-005-pwa-perfil-e2e.md) | **Builders, publicación, requisitos PWA/perfil y E2E.** | Salida reproducible; inventario/drift; FUN-PWA-001..010, FUN-PRO-001..014, NFR aplicables; cuatro rutinas y cache/update. | A + V + H | In progress |
| TDD-006 | **Dominio de entrenamiento y persistencia.** | Transiciones válidas/ inválidas; unidades y límites; revisión; temporizador; cierre sin pérdida; process death; duración y valores anteriores. | A + integración | Planned |
| TDD-007 | **Outbox, contratos, idempotencia y restauración.** | Commit agregado+outbox atómico; reintento; duplicación; reordenamiento; respuesta tardía; tombstone; migración; restauración limpia sin pérdida silenciosa. | A + integración + H | Planned |
| TDD-008 | **Nutrición e IA gobernada.** | Cada captura produce borrador; catálogo y método por componente; esquema; incertidumbre; IA no confirma/sobrescribe; respuesta tardía no vence una corrección; golden set separado de ajuste. | A + golden set + H | Planned |
| TDD-009 | **Dispositivos y servicios externos.** | Tezkatli ausente/fuera de LAN; readiness real; reloj con ACK y deduplicación; Health Connect conserva `DataOrigin`; fallback manual; PoC Amazfit antes de declarar compatibilidad. | Integración + H | Planned |
| TDD-010 | **Seguridad, rendimiento y release.** | Servicio no público; entradas limitadas; secretos ausentes; logs sin contenido personal; TTID/TTFD y persistencia medidos; backup/restore; permisos/MASVS; rollback. | A + benchmark + H | Planned |

## 7. Casos de prueba iniciales con identificadores estables

Los siguientes identificadores se agregan a la estrategia vigente sin invalidar
los `TST-*` existentes:

| ID | Caso | Resultado esperado |
|---|---|---|
- **TST-CAN-001:** validar los cuatro HTML canónicos contra el contrato de estructura. Cada día tiene la cantidad de tarjetas declarada y los índices son contiguos.
- **TST-CAN-002:** recalcular las series desde `data-series-keys`. El total coincide con resumen, dashboard y distribución documentada.
- **TST-CAN-003:** validar navegación entre ejercicios. `data-next` es el índice siguiente; el último muestra finalización.
- **TST-CAN-004:** validar el layout compartido. Cada salida tiene un único `main.cards`, índices de tarjeta contiguos y un único footer de acciones.
- **TST-UI-001:** intentar iniciar antes y después del calentamiento. La secuencia obligatoria es general → específico → ejercicio → series.
- **TST-UI-002:** completar parcialmente y ejecutar reset. UI, contadores, calentamiento y `localStorage` vuelven a estado inicial.
- **TST-MED-001:** cruzar HTML, manifest y archivos locales. Cada recurso existe, tiene hash verificable y estado de procedencia explícito.
- **TST-MED-002:** activar error de carga y `prefers-reduced-motion`. Se muestra fallback estático sin pérdida de significado ni doble anuncio.
- **TST-BLD-001:** ejecutar cada builder dos veces y comparar inventario. Salida determinista, sin drift ni referencias remotas inesperadas.
- **TST-PRO-008:** capturar series hechas/no hechas, carga/repeticiones válidas, histórico y recomendación sin modificar la rutina.
- **TST-PRO-009:** derivar días de sesiones recientes, permitir selección libre, descartar por fecha y comprobar que el aviso se limita a la portada activa.
- **TST-PRO-010:** comprobar que el nombre solo se combina con texto local y que se inserta mediante `textContent`.

Los casos futuros conservan la nomenclatura existente: `TST-TRN-*`,
`TST-SYN-*`, `TST-NUT-*`, `TST-AI-*`, `TST-WEA-*`, `TST-SEC-*` y `TST-REC-*`.

## 8. Gates de aceptación y cierre

Un incremento de rutinas no se cierra hasta superar, en orden:

1. **G0 — Repositorio:** `python scripts/validate_repository.py`,
   `python scripts/validate_contracts.py`, pruebas disponibles y `git diff
   --check`.
2. **G1 — Semántica:** TDD-002 sin discrepancias de tarjetas, índices, series,
   dashboard, resumen o títulos.
3. **G2 — Comportamiento:** TDD-003 con navegador autorizado, interacción
   completa y consola limpia.
4. **G3 — Medios:** TDD-004; todo recurso debe conservar procedencia técnica
   y estado de revisión explícito mientras falte evidencia P.
5. **G4 — Visual/responsive:** revisión de escritorio y móvil con artefactos
   guardados; no confundirla con cierre de accesibilidad o procedencia.
6. **G5 — Producto:** para Android/servicios, TDD-006..010 según alcance,
   migración/rollback y evidencia real requerida.

La definición de terminado de cada SDD/TDD exige: documento versionado,
requisitos y riesgos enlazados, comando reproducible, evidencia ubicada,
limitaciones explícitas y actualización de `TRACEABILITY.md`. Un estado
`Verified` no se asigna por intención, mock, archivo generado o puerto
alcanzable aislado.
