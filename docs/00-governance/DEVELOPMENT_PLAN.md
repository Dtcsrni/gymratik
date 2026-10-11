# Plan de desarrollo de Gymratik PWA

## Modelo

Iteraciones pequeñas sobre una PWA estática/local. Cada cambio debe tener criterio observable, trazabilidad cuando afecte un requisito, y evidencia proporcional al comportamiento cambiado.

## Etapas

### M0 — Alcance y requisitos

- Confirmar que el trabajo pertenece a la PWA y a sus cuatro rutinas canónicas.
- Mantener SRS, casos de uso, riesgos y trazabilidad alineados.
- **Gate:** cada requisito activo tiene prioridad, aceptación y prueba/evidencia asociada.

### M1 — Funcionamiento local

- Portada, perfil local, sesiones, historial y progreso semanal.
- Migraciones IndexedDB no destructivas y continuidad de sesión.
- **Gate:** pruebas sintéticas muestran persistencia, idempotencia y conservación del historial.

### M2 — Uso offline y actualización

- Inventario offline generado, instalación, política de red y actualización por Service Worker.
- **Gate:** paquete completo previo permanece utilizable ante descarga incompleta; recursos inventariados abren offline en navegador de prueba.

### M3 — Respaldo y privacidad

- Exportación/importación manual JSON v3, mensajes de límites y datos sintéticos para pruebas.
- **Gate:** restauración fixture v3 verificada; inválidos no modifican el estado.

### M4 — Validación de entrega

- Ejecutar validadores documentales, de rutinas, medios, pruebas y sintaxis que correspondan al cambio.
- Revisar la interfaz en viewport móvil; ejecutar verificación física solo cuando el dispositivo esté disponible y autorizado.
- **Gate:** reportar separadamente evidencia local, emulada, navegador publicado y física.

## Fuera del plan vigente

Nutrición, suplementos, gimnasio/equipo, IA, Android nativo, integraciones, backend y sincronización multi-dispositivo están diferidos. No se crean hitos, dependencias ni estimaciones para esas áreas dentro del plan de la PWA.

## Gestión

- Backlog por comportamiento observable de la PWA.
- ADR para decisiones arquitectónicas significativas.
- Proteger cambios locales existentes; revisar `git status` y diffs antes de integrar.
- No publicar, desplegar ni cambiar datos personales como parte de validación local.

## Definition of Done

- Criterios de aceptación y trazabilidad actualizados.
- Validaciones aplicables ejecutadas y resultados reales reportados.
- Fallos repetibles corregidos con una protección antirregresión.
- Documentación distingue implementado, parcial, propuesto y no verificado.
