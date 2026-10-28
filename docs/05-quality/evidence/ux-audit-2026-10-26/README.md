# Auditoría de UX/UI de rutinas · 2026-10-26

## Alcance y método

Se revisaron las cuatro salidas canónicas en navegador sintético móvil (390 ×
844 CSS px), además de estructura y contenido de las 26 tarjetas. Cada día
incluye cabecera, contexto y anatomía, reglas, preparación, calentamiento,
resumen/progreso, tarjetas, técnica y cierre. Las capturas conservadas muestran
cabecera, primera tarjeta y cierre de cada día.

## Hallazgos y cambios

1. **Entrada al día:** antes del cambio, el panel de objetivo/anatomía estaba
   siempre expandido y medía entre 472 y 825 px dentro de la cabecera; el primer
   ejercicio comenzaba entre 3,235 y 3,581 px desde el inicio. Ahora se resume
   en un desplegable nativo cerrado por defecto. La cabecera mide 769–807 px y
   el desplegable cerrado 65 px. Objetivo y anatomía siguen disponibles al
   expandirlo.
2. **Registro de series en móvil:** las 26 fichas compartían el orden título,
   referencias visuales y controles. Se priorizan ahora título, métricas y
   registro, seguidos por referencias visuales y técnica. Se conserva el orden
   de escritorio; la estructura HTML continúa uniforme entre los cuatro días.
3. **Cierre y reinicio:** al llevar la página al final se ven `Terminar día` y
   `Reiniciar día`; ambos quedan antes de la barra de progreso flotante. El
   reinicio sigue siendo acción al final y conserva su confirmación existente.
4. **Consistencia de fichas:** las 26 tarjetas conservan las cuatro métricas,
   contador, referencia visual y acordeón técnico cerrado con Posición,
   Movimiento y Evita. La comprobación estática no encontró imágenes de
   ejercicio sin texto alternativo.

## Capturas posteriores al cambio

Capturas móviles JPG de calidad moderada; cada imagen es una vista de 390 × 844.

| Día | Encabezado | Ficha | Cierre |
|---|---|---|---|
| 1 | `day1-top.jpg` | `day1-exercise.jpg` | `day1-footer.jpg` |
| 2 | `day2-top.jpg` | `day2-exercise.jpg` | `day2-footer.jpg` |
| 3 | `day3-top.jpg` | `day3-exercise.jpg` | `day3-footer.jpg` |
| 4 | `day4-top.jpg` | `day4-exercise.jpg` | `day4-footer.jpg` |

## Verificación

- `python scripts/validate_canonical_routines.py`:
  `CANONICAL_ROUTINES_OK routines=4`.
- `python scripts/validate_routine_media.py`:
  `ROUTINE_MEDIA_OK routines=4`.
- `python scripts/validate_repository.py`: `VALIDATION_OK markdown=84`.
- Pruebas unitarias focalizadas de plantilla, portada y versión del service
  worker: 3 aprobadas.
- E2E interactivo responsive pendiente: `sync_playwright().start()` no
  completa el handshake del driver en este entorno, antes de iniciar Edge. No
  se contabiliza como aprobado; el script conserva los controles para repetir
  cuatro días, estados de teclado y matriz responsive cuando el driver inicie.

## Límites

La revisión visual descrita usa navegador local sintético. No acredita la PWA
instalada en GT6 ni el despliegue público. La inspección por capturas tampoco
equivale a certificación completa de accesibilidad.
