# TDD-004 — Medios, formato y correspondencia visual

**Estado:** `In progress`  
**Versión:** `0.1`  
**Fecha:** `2026-09-17`  
**Diseño asociado:** [SDD-003](../03-architecture/SDD-003-medios-fallback-procedencia-tecnica.md)

## 1. Objetivo

Detectar tres clases de defecto que no deben confundirse:

1. **Ausencia:** falta la imagen, el GIF, el fallback o la ruta.
2. **Formato:** el archivo no es decodificable, no es animado, tiene dimensiones
   inesperadas o no cumple el rol declarado.
3. **Correspondencia incorrecta:** el archivo existe y carga, pero muestra otro
   ejercicio, otra máquina, otra trayectoria o una posición que contradice la
   tarjeta.

## 2. Casos de prueba

### TST-MED-001 — Inventario de rutas

Extraer `src` y `data-static-src` de las cuatro HTML, excluir datos embebidos y
recursos remotos no previstos, resolver rutas contra el directorio del HTML y
rechazar:

- archivos inexistentes;
- rutas fuera del árbol permitido;
- referencias vacías o con extensión no reconocida;
- fallback declarado pero ausente.

### TST-MED-002 — Completitud por tarjeta

Para cada tarjeta de ejercicio comprobar que existen sus roles declarados:

- referencia de máquina cuando la tarjeta la muestra;
- inicio y final cuando el formato los promete;
- GIF o una declaración explícita `STATIC_ONLY`;
- fallback estático para cada animación;
- alt de contenido y tratamiento correcto de elementos decorativos.

Una imagen de calentamiento no satisface el rol de un ejercicio y una imagen de
otro ejercicio no satisface la tarjeta aunque tenga dimensiones correctas.

**TST-MED-003:** Integridad técnica

Para cada elemento del manifiesto verificar existencia, SHA-256, dimensiones,
extensión y, cuando corresponda, número de fotogramas. Reportar el elemento y
el atributo divergente, sin volcar el contenido binario.

**TST-MED-004:** Correspondencia declarada

Comparar `routineId`, `exerciseIndex`, `assetId`, título y rol entre HTML y
manifiesto. Rechazar IDs faltantes, claves corregidas no reflejadas en la salida
canónica y recursos asignados a más de un ejercicio sin declaración explícita.

**TST-MED-005:** Revisión visual de recurso incorrecto

Para cada tarjeta revisar una imagen inicial, una final y el GIF o fallback:

| Dimensión | Pregunta |
|---|---|
| Ejercicio | ¿El patrón coincide con el título y la instrucción? |
| Equipo | ¿La máquina/configuración coincide con la descrita? |
| Trayectoria | ¿Se distinguen inicio, recorrido y final correctos? |
| Composición | ¿Se ven apoyos, agarres y articulaciones necesarios? |
| Texto | ¿El alt describe lo visible sin afirmar más de lo revisado? |

El resultado es `MATCH`, `MISMATCH` o `UNABLE_TO_CONFIRM`, con observación
breve y referencia al recurso. `UNABLE_TO_CONFIRM` no es un aprobado.

**TST-MED-006:** Fallback y reduced motion

Forzar error de carga y activar `prefers-reduced-motion: reduce`. Comprobar que
el fallback aparece, que no se duplica el anuncio para lectores de pantalla y
que la tarjeta conserva significado y controles utilizables.

## 3. Implementación prevista

El comprobador técnico de rutas es
`scripts/validate_routine_media.py`. Está separado del validador semántico de
rutinas, acepta rutas explícitas, produce salida compacta y devuelve código
distinto de cero para ausencias o inconsistencias técnicas.

Comando sobre las cuatro salidas:

```powershell
python scripts/validate_routine_media.py
```

La comprobación de correspondencia visual debe permanecer separada del código
automático. Puede usar revisión en navegador y capturas controladas, pero no
debe marcar `MATCH` por similitud de nombres, tamaño, color o hash.

## 4. Evidencia y cierre

### Resultado PWA ejecutado — 2026-10-09

- Cuatro páginas locales cargaron sus recursos; `validate_routine_media.py`
  terminó con `ROUTINE_MEDIA_OK routines=4`.
- Las 26 tarjetas declaran modo: 12 `STATIC_ONLY` y 14 con GIF local.
- Se revisaron 25 parejas Inicio/Final y la guía hip thrust de tres pasos.
- Las 14 animaciones mostraron poster con movimiento reducido y reanudaron con
  avance de cuadros. La evidencia individual está en el
  [registro de verificación PWA](evidence/pwa-exercise-verification-2026-10-09.md)
  y sus mosaicos de revisión visual están junto a este documento.
- La ejecución funcional de 82/82 series se comparte con TDD-002 y cubre la
  interacción por ejercicio; no certifica el dispositivo físico.

La cobertura de medios servidos y el comportamiento visual del alcance PWA
quedaron verificados. TDD-004 permanece `In progress` hasta conciliar los
catálogos históricos de procedencia con las cuatro salidas activas y completar
el estado de redistribución/licencias. Los catálogos históricos no se usan para
decidir qué medio renderiza actualmente la PWA; el atributo `data-media-mode`
declara el contrato activo por tarjeta.
