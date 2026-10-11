# Serie documental TDD y SDD de la PWA

## 1. Propósito

`SDD` (Software Design Description) describe responsabilidades, datos e invariantes. `TDD` (Test Design Document) describe casos de prueba, datos y evidencia. El SRS define el alcance activo; un documento de diseño no puede ampliarlo.

## 2. Alcance y fuentes

La serie activa cubre cuatro rutinas canónicas, su generación y medios, la portada PWA, persistencia local, historial, respaldo JSON v3 y actualización offline.

Android nativo, gimnasio/equipo, nutrición, suplementos, IA, servicios externos e integración/sincronización multi-dispositivo están diferidos. Consulta [DEFERRED_SCOPE.md](../01-requirements/DEFERRED_SCOPE.md). Las referencias en ADR antiguos son históricas.

| Área | Fuente | Regla |
|---|---|---|
| Requisitos | `docs/01-requirements/SRS.md` | No ampliar alcance por un SDD/TDD. |
| Arquitectura | `docs/03-architecture/ARCHITECTURE.md` y ADR PWA | Cambio arquitectónico significativo requiere ADR. |
| Calidad | `docs/05-quality/TEST_STRATEGY.md` | Prueba automatizada no sustituye verificación visual/física. |
| Rutinas | `data/rutinas_autocontenidas/canonicas/` | Salida canónica validada. |
| Medios | manifiestos de evidencia y medios locales | Estado visual no prueba procedencia o técnica. |

## 3. Estados y evidencia

Estados: `Planned`, `In progress`, `Partial`, `Verified`, `Blocked`. `Verified` solo cubre la combinación y plataforma realmente probadas.

- **A:** automatizada/reproducible.
- **V:** navegador, interacción o inspección visual.
- **H:** dispositivo real o revisión humana.
- **P:** procedencia del recurso.

## 4. Defectos repetibles que deben prevenirse

| ID | Defecto o límite | Regresión que debe evitarse |
|---|---|---|
| DEF-CAN-001 | Tarjetas o series no coinciden con el contrato canónico. | Validar cantidad, índices, series y resumen de cada día. |
| DEF-CAN-002 | Navegación guiada apunta a un ejercicio incorrecto. | Comparar `data-next` con título e índice siguiente. |
| DEF-MED-001 | Manifiestos tienen estados/procedencia incompletos. | No declarar recursos aprobados sin fuente/estado verificable. |
| DEF-QA-001 | Un cambio de plantilla puede romper las cuatro rutinas. | Validar las salidas generadas, no solo el builder. |
| DEF-DATA-001 | Progreso viejo o ambiguo puede adoptarse como semana actual o perder una sesión de hoy. | Probar lunes local, snapshots sin fecha, sesión de hoy con cero series y navegación repetida. |
| DEF-BACKUP-001 | Importar esquema inválido podría sobrescribir registros. | Validar archivo completo antes de pedir confirmación o mutar datos. |

## 5. Diseños activos

| Documento | Alcance | Estado |
|---|---|---|
| [SDD-001](../03-architecture/SDD-001-rutina-canonica-versionado.md) | Rutinas canónicas y versionado | In progress |
| [SDD-003](../03-architecture/SDD-003-medios-fallback-procedencia-tecnica.md) | Medios y procedencia | In progress |
| [SDD-004](../03-architecture/SDD-004-generacion-validacion-publicacion-pwa.md) | Generación, perfil local, actualización y recursos offline | In progress |

## 6. Diseños de pruebas activos

| Documento | Alcance mínimo | Estado |
|---|---|---|
| TDD-001 | Integridad del repo, enlaces, contratos y secretos | Partial |
| [TDD-002](../05-quality/TDD-002-integridad-rutinas-canonicas.md) | Estructura, índices, series y contenido de las cuatro rutinas | In progress |
| TDD-003 | Estados interactivos, calentamiento, descanso, deshacer y navegación | Partial |
| [TDD-004](../05-quality/TDD-004-medios-formato-y-correspondencia.md) | Medios, fallback, formatos y revisión visual | In progress |
| [TDD-005](../05-quality/TDD-005-pwa-perfil-e2e.md) | Persistencia PWA, perfil, respaldo y Service Worker | In progress |

Los TDD de Android, servidores, IA e integraciones no forman parte del plan activo.

## 7. Casos de prueba con IDs estables

- **TST-CAN-001:** cada HTML canónico satisface el contrato de estructura y cantidad de tarjetas.
- **TST-CAN-002:** la suma de series coincide con atributos, resumen y contenido documentado.
- **TST-CAN-003:** `data-next` apunta al índice/título correcto y el último ejercicio termina el flujo.
- **TST-CAN-004:** layout compartido conserva `main.cards`, tarjetas contiguas y acciones únicas.
- **TST-UI-001:** calentamiento y bloqueos se muestran antes de permitir completar una serie.
- **TST-UI-002:** reset reinicia el estado operativo esperado sin borrar historial no incluido en el reset.
- **TST-MED-001:** HTML, manifiesto y archivo local coinciden en ruta, hash y estado de procedencia.
- **TST-MED-002:** error de medio y movimiento reducido muestran fallback con texto accesible.
- **TST-BLD-001:** builders repetidos producen inventario determinista y sin referencias inesperadas.
- **TST-PRO-008:** progresión se basa solo en series registradas y no cambia la rutina/carga automáticamente.
- **TST-PRO-009:** días sugeridos y aviso local respetan selección y primer plano.
- **TST-PRO-010:** nombre se inserta como texto local, no como HTML.

## 8. Gates

1. **Repositorio:** `python scripts/validate_repository.py` y validadores de contrato aplicables.
2. **Contenido:** TST-CAN confirma tarjetas, índices, series y títulos.
3. **Interacción:** TDD-003 cubre flujo, deshacer, descanso y navegación.
4. **Medios:** TDD-004 mantiene estado y procedencia explícitos.
5. **PWA:** TDD-005 distingue pruebas automatizadas, navegador y dispositivo.

El estado `Verified` requiere comando reproducible, resultado, plataforma y limitaciones registrados en [TRACEABILITY.md](TRACEABILITY.md).
