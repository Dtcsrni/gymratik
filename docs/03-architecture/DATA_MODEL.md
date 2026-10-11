# Datos locales de la PWA

## Alcance

Este modelo describe los datos que la PWA mantiene en el origen del navegador. No define entidades para nutrición, suplementos, reloj, backend o sincronización multi-dispositivo; esos dominios están diferidos.

## Registros principales

- **Perfil local:** preferencias mínimas para personalizar la interfaz. No es una cuenta ni identidad autenticada.
- **Sesión:** fecha local/instante, día de rutina y estado (`active`, `completed`, `abandoned` o `edited`) según el esquema vigente. Las sesiones cerradas guardan `completionKind` (`complete` o `partial`) para distinguir terminar toda la rutina de cerrar voluntariamente con avance parcial; es un campo opcional compatible con respaldos previos.
- **Serie:** ejercicio, repeticiones, carga opcional y unidad; solo una serie confirmada cuenta como completada.
- **Snapshot operativo:** progreso temporal de una rutina para continuar la sesión y reflejar la semana local.
- **Metadata:** versión de esquema y datos auxiliares necesarios para migrar o restaurar.

Los nombres y la forma exacta de stores/índices se verifican en `progress-store.js`; este documento no reemplaza el contrato ejecutable.

## Persistencia y respaldo

- IndexedDB v3 es el almacén operativo preferido.
- `localStorage` es compatibilidad/fallback limitado y no una base sincronizada.
- Ubicación exacta: origen y perfil del navegador; base IndexedDB `entrenamiento-progress`, versión 3, stores `profiles`, `routineProgress`, `sessions`, `activity` y `meta`. El fallback usa `entrenamiento-progress-fallback-v3`; snapshots de rutina y archivo histórico usan claves `fitlovers-dayN-series-v1` y `gymratik-legacy-progress-archive-v1`.
- Cache API guarda recursos estáticos; no contiene el historial como respaldo.
- Exportar produce un JSON `gymratik-backup` esquema 3.
- Importar valida esquema y contenido y pide confirmación antes de reemplazar registros.
- La PWA no elimina datos como parte de instalación, actualización, migración o rotación semanal. Reinicio e importación de reemplazo son acciones manuales confirmadas.
- El navegador/sistema operativo administra el almacenamiento del origen; la PWA no puede impedir su eliminación por limpieza del usuario/sistema, cambio de perfil/origen ni todas las rutas de desinstalación.

## Reglas de integridad

- Una migración añade lo requerido sin borrar stores/registros preexistentes; versiones futuras deben conservar también datos que no interpreten.
- Una sesión fechada iniciada hoy sobrevive a navegación, recarga y actualización.
- El avance semanal se calcula en fecha local; snapshots antiguos o sin fecha confiable no se adoptan como actuales y se archivan íntegramente antes de renovar el estado operativo.
- Una restauración inválida se detiene antes de mutar el estado.
- Un dato ausente no se convierte en cero ni se inventa durante una proyección.
