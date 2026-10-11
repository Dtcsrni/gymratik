# Architecture Decision Records

Estados documentales: `Proposed`, `Accepted`, `Superseded`, `Rejected`.
`Accepted` en un ADR histórico no lo incorpora al alcance vigente. El producto
activo es la PWA; solo ADR-013 a ADR-017 describen decisiones directamente
relacionadas con su estado actual. Las decisiones de Android, servidor,
nutrición, IA e integraciones quedan diferidas.

| ADR | Decisión | Estado |
|---|---|---|
| [ADR-001](ADR-001-monorepo.md) | Monorepo | Accepted |
| [ADR-002](ADR-002-native-android.md) | Android nativo | Diferido |
| [ADR-003](ADR-003-local-first.md) | Local-first y Room | Diferido |
| [ADR-004](ADR-004-transactional-outbox.md) | Outbox transaccional | Diferido |
| [ADR-005](ADR-005-tezkatli-modular-monolith.md) | Monolito modular Tezkatli | Diferido |
| [ADR-006](ADR-006-ai-drafts.md) | IA produce borradores | Diferido |
| [ADR-007](ADR-007-food-provenance.md) | Procedencia nutricional | Diferido |
| [ADR-008](ADR-008-private-network.md) | Red privada | Diferido |
| [ADR-009](ADR-009-model-governance.md) | Gobierno de modelos | Diferido |
| [ADR-010](ADR-010-health-connect.md) | Health Connect como adaptador | Diferido |
| [ADR-011](ADR-011-backup.md) | Respaldo de servicios | Diferido |
| [ADR-012](ADR-012-zepp-poc.md) | Zepp condicionado por PoC | Diferido |
| [ADR-013](ADR-013-perfil-local-y-respaldo-pwa.md) | Perfil local, historial y respaldo de la PWA | Superseded |
| [ADR-014](ADR-014-progresion-e-horarios-locales-pwa.md) | Progresión, días habituales y avisos locales de la PWA | Superseded |
| [ADR-015](ADR-015-base-local-v3-exclusiva.md) | Uso exclusivo de la base local y respaldos v3 | Accepted |
| [ADR-016](ADR-016-actualizacion-segura-pwa.md) | Inicio y actualización segura de la PWA | Superseded |
| [ADR-017](ADR-017-politica-de-actualizacion-y-cache-pwa.md) | Política de actualización, red y caché acotada de la PWA | Accepted |
| [ADR-018](ADR-018-retencion-manual-de-datos-pwa.md) | Retención manual de datos y archivo semanal | Accepted |

## Plantilla

```text
# ADR-NNN — Título
Estado, fecha, contexto, decisión, consecuencias, alternativas, evidencia.
```
