# Trazabilidad del alcance activo PWA

Cada requisito funcional/no funcional del SRS aparece una sola vez. `Partial` indica que hay implementación o pruebas incompletas; no demuestra conformidad total. `Planned` indica que falta evidencia ejecutada.

| Requisito | Riesgo | Diseño/ADR | Prueba o evidencia | Estado |
|---|---|---|---|---|
| FUN-PWA-001 | RISK-011 | ADR-017 | TST-PWA-001 | Partial |
| FUN-PWA-002 | RISK-011 | ADR-017 | TST-PWA-002 | Partial |
| FUN-PWA-003 | RISK-011 | ADR-017 | TST-PWA-003 | Partial |
| FUN-PWA-004 | RISK-011 | ADR-017 | TST-PWA-004 | Partial |
| FUN-PWA-005 | RISK-011 | ADR-017 | TST-PWA-005 | Partial |
| FUN-PWA-006 | RISK-011 | ADR-016 | TST-PWA-006 | Partial |
| FUN-PWA-007 | RISK-004 | ADR-015 | TST-PWA-029 | Partial |
| FUN-PWA-008 | RISK-011 | SDD-004 | TST-PWA-030 | Partial |
| FUN-PWA-009 | RISK-011 | ADR-017 | TST-PWA-031 | Partial |
| FUN-PWA-010 | RISK-011 | ADR-017 | TST-PWA-032 | Partial |
| FUN-PRO-001 | RISK-004 | ADR-013 | TST-PRO-001 | Partial |
| FUN-PRO-002 | RISK-004, RISK-014 | ADR-015 | TST-PRO-002 | Partial |
| FUN-PRO-003 | RISK-004 | ADR-013 | TST-PRO-003 | Partial |
| FUN-PRO-004 | RISK-014 | ADR-015 | TST-PRO-004 | Partial |
| FUN-PRO-005 | RISK-011 | ADR-013 | TST-PRO-005 | Partial |
| FUN-PRO-006 | RISK-004 | ADR-013 | TST-PRO-006 | Partial |
| FUN-PRO-007 | RISK-004 | ADR-013 | TST-PRO-007 | Partial |
| FUN-PRO-008 | RISK-004 | ADR-014 | TST-PRO-008 | Partial |
| FUN-PRO-009 | RISK-004 | ADR-014 | TST-PRO-009 | Partial |
| FUN-PRO-010 | RISK-004 | ADR-014 | TST-PRO-010 | Partial |
| FUN-PRO-011 | RISK-003 | ADR-015 | TST-PRO-011 | Partial |
| FUN-PRO-012 | RISK-004 | ADR-014 | TST-PRO-012 | Partial |
| FUN-PRO-013 | RISK-004 | ADR-014 | TST-PRO-013 | Partial |
| FUN-PRO-014 | RISK-004 | ADR-013 | TST-PRO-014 | Partial |
| FUN-PRO-015 | RISK-004 | SDD-004 | TST-PRO-015 | Partial |
| FUN-PRO-016 | RISK-004, RISK-014 | SDD-004, ADR-015 | TST-PRO-016 | Partial |
| FUN-PRO-017 | RISK-014 | SDD-004, ADR-013 | TST-PRO-017 | Partial |
| FUN-PRO-018 | RISK-014 | ADR-018 | TST-PRO-018 | Partial |
| FUN-TRN-010 | RISK-004 | SDD-001 | TST-TRN-010 | Partial |
| FUN-TRN-011 | RISK-004 | SDD-001 | TST-TRN-011 | Partial |
| FUN-TRN-012 | RISK-004 | SDD-001 | TST-TRN-012 | Partial |
| FUN-TRN-013 | RISK-004 | SDD-001 | TST-TRN-013 | Partial |
| NFR-REL-001 | RISK-004 | ADR-013, ADR-015 | TST-PWA-012 | Partial |
| NFR-REL-002 | RISK-004 | ADR-015 | TST-PWA-013 | Partial |
| NFR-AVA-001 | RISK-011 | ADR-017 | TST-PWA-014 | Partial; navegador físico pendiente |
| NFR-REC-001 | RISK-014 | ADR-015 | TST-PWA-015 | Partial |
| NFR-SEC-002 | RISK-003 | SDD-004 | TST-PWA-020 | Partial |
| NFR-SEC-003 | RISK-003 | ADR-015 | TST-PWA-021 | Partial |
| NFR-PRI-001 | RISK-010 | SDD-004 | TST-PWA-022 | Partial |
| NFR-PRI-002 | RISK-010 | SDD-004 | TST-PWA-023 | Partial |
| NFR-PRI-003 | RISK-010 | ADR-015 | TST-PWA-024 | Partial |
| NFR-USA-001 | RISK-004 | ADR-014 | TST-PWA-025 | Partial |
| NFR-USA-002 | RISK-004 | SDD-004 | TST-PWA-026 | Partial |
| NFR-MAI-002 | RISK-011 | SDD-004 | TST-PWA-027 | Partial |
| NFR-COM-001 | RISK-004 | ADR-015 | TST-PWA-028 | Partial |

## Diseños y pruebas activos

| Diseño | Alcance | Prueba/evidencia | Estado |
|---|---|---|---|
| SDD-001 · Rutinas canónicas | Cuatro rutinas y contratos compartidos | [TDD-002](../05-quality/TDD-002-integridad-rutinas-canonicas.md), [evidencia por ejercicio/serie](../05-quality/evidence/pwa-exercise-verification-2026-10-09.md) | Verified (local PWA; physical/public pending) |
| SDD-003 · Medios y procedencia | Recursos visuales locales de rutinas | [TDD-004](../05-quality/TDD-004-medios-formato-y-correspondencia.md), [evidencia visual](../05-quality/evidence/pwa-exercise-verification-2026-10-09.md) | PWA runtime verified; provenance pending |
| [SDD-004](../03-architecture/SDD-004-generacion-validacion-publicacion-pwa.md) · PWA local/offline | FUN-PWA-*, FUN-PRO-*, FUN-TRN-010..013 y NFR activos | [TDD-005](../05-quality/TDD-005-pwa-perfil-e2e.md) | In progress |

Los diseños Android, sincronización de backend, nutrición/IA e integraciones permanecen diferidos; consulta [DEFERRED_SCOPE.md](../01-requirements/DEFERRED_SCOPE.md). Los ADR históricos se conservan como decisiones previas, no amplían el alcance activo.
