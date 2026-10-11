# Sincronización e IA: alcance diferido

No se implementan sincronización de datos de usuario, cuentas, backend ni IA dentro del alcance vigente de Gymratik PWA.

## Transferencia de datos que sí existe

- **Respaldo manual:** exportación/importación local de un archivo JSON v3 validado y confirmada por el usuario.
- **Actualización de recursos:** Service Worker prepara recursos estáticos y aplica la política descrita en [ADR-017](adr/ADR-017-politica-de-actualizacion-y-cache-pwa.md).

Son flujos separados. La actualización del paquete no transmite sesiones/perfil y el archivo de respaldo no sincroniza automáticamente otro dispositivo.

## Futuras decisiones

Si el alcance se amplía, definir primero identidad, autorización, privacidad, resolución de conflictos, retención, respaldo, costos y recuperación. Los requisitos heredados están en [DEFERRED_SCOPE.md](../01-requirements/DEFERRED_SCOPE.md) y no constituyen diseño aprobado.
