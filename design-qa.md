# Design QA · miniaturas anatómicas de músculos

## Contexto de comparación

- Fuente visual: `C:\Users\evega\AppData\Local\Temp\codex-clipboard-e94b864b-c233-42b7-8a29-4b5ff64a4215.png`.
- Fuente visible: recorte de la sección «Músculos del día» del Día 1, 915 × 287 px, formato anterior con chips de texto y sin imágenes anatómicas.
- Implementación: rutinas canónicas servidas localmente desde `http://127.0.0.1:8765/`.
- Captura de implementación: evidencia visual inline de CUA en esta ejecución; el conector no expone una ruta de archivo persistible para sus bytes de captura.
- Viewport de implementación: 390 × 844 CSS px, mobile-first, densidad predeterminada del navegador.
- Estado: cabecera visible al cargar cada rutina; progreso existente conservado y no modificado.

## Evidencia y comparación

- Vista completa: Día 1, Día 2 y Día 3 cargaron la cabecera en móvil con la jerarquía existente, tarjetas de imagen legibles, etiquetas de músculo y dock de sesión sin bloquear el contenido superior.
- Región enfocada: «Músculos del día». El cambio intencional reemplaza los badges planos por miniaturas anatómicas rasterizadas locales, manteniendo el nombre visible y los códigos de identificación.
- Día 2 usa vista anterior para cuádriceps/aductores y posterior para glúteo/isquiosurales/pantorrilla; Día 1 combina posterior para espalda/hombro y anterior para bíceps/pecho.
- Las imágenes se verificaron con `complete=true`, `hidden=false` y `naturalWidth=1254` en el render del Día 3.
- Consola del navegador: sin errores ni advertencias reportadas durante la captura.

## Comparación histórica

1. Primera captura: el fallback «ANATOMÍA» se superponía a las imágenes porque una regla `!important` anulaba `hidden`.
2. Corrección: se añadió `.muscleDayFallback[hidden]{display:none!important}` y se regeneraron Día 2 y Día 3.
3. Capturas posteriores: las tres cabeceras quedaron sin superposición, con recortes estables y texto legible en 390 × 844.

## Findings

No hay hallazgos accionables P0, P1 o P2.

## Open Questions

- Las placas son ilustraciones anatómicas educativas generadas para la interfaz; no deben interpretarse como diagnóstico, evidencia fisiológica ni validación clínica.
- Queda como refinamiento P3 opcional producir placas individuales con resaltado específico por músculo, en vez de reutilizar una placa regional por grupo.

## Implementation Checklist

- [x] Miniaturas locales en las tres rutinas canónicas.
- [x] Alt text descriptivo y fallback accesible por error de carga.
- [x] Composición mobile-first y breakpoint de una columna.
- [x] Vista anatómica anterior/posterior ajustada a los grupos del día.
- [x] Service worker regenerado con los cuatro recursos nuevos.
- [x] Validación visual de Día 1, Día 2 y Día 3.
- [x] Consola sin errores.

final result: passed

## Selector de discos · opción 2 · 2026-11-19

### Evidencia

- Se integró en el registro de carga de las cuatro rutinas canónicas: panel plegable, discos individuales con arte local, suma mixta kg/lb, ajuste por pieza y aplicación al borrador de carga existente.
- Se comparó la implementación con el mockup seleccionado en el código y con las comprobaciones estáticas automatizadas. El render del navegador no pudo capturarse en esta ejecución.
- El navegador en app recibió una página ajena al abrir el puerto local conocido; un puerto libre no permitió enlazar el servidor local en el entorno. La navegación `file://` quedó rechazada por la política del navegador. No se probaron interacciones visuales en navegador.

### Findings

- P0/P1 funcionales conocidos: ninguno en pruebas estáticas.
- Verificación visual P1: pendiente; no hay evidencia de captura a 390 px ni revisión de contraste/tamaño táctil en navegador.

### Verificaciones disponibles

- [x] 83 pruebas focalizadas de rutina y selector aprobadas.
- [x] Sintaxis de 68 scripts inline verificada con `node --check`.
- [x] Validador del repositorio aprobado.
- [ ] Captura, recorrido de interacción y comparación visual en navegador.

final result: blocked
