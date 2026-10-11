# TDD-002 — Integridad semántica de rutinas canónicas

**Estado:** `Verified (local PWA)`
**Versión:** `0.2`
**Fecha de verificación:** `2026-10-09`
**Diseño asociado:** [SDD-001](../03-architecture/SDD-001-rutina-canonica-versionado.md)

## 1. Objetivo

Detectar automáticamente inconsistencias entre el contenido declarado y las
las HTML canónicas, especialmente las que no detectan los checks actuales del
repositorio: tarjetas ausentes, índices discontinuos, claves incompletas y
totales falsos.

## 2. Sistema bajo prueba

| Día | Archivo | Contrato declarado |
|---|---|---|
| 1 | `data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html` | 6 ejercicios; 20 series; `4 + 4 + 3 + 3 + 3 + 3` según el documento actual |
| 2 | `data/rutinas_autocontenidas/canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html` | 6 ejercicios; 20 series; `3 + 3 + 3 + 4 + 3 + 4` |
| 3 | `data/rutinas_autocontenidas/canonicas/Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html` | 7 ejercicios; 22 series; `4 + 3 + 3 + 3 + 3 + 3 + 3` |
| 4 | `data/rutinas_autocontenidas/canonicas/Rutina_Dia_4_Pierna_Equilibrio_V1.html` | 7 ejercicios; 20 series; `3 + 3 + 4 + 2 + 2 + 3 + 3` |

El contrato del Día 1 debe mantenerse explícito: si se decide volver a otra
distribución, se actualizarán SDD-001, el documento de contenido, la salida y
la matriz de trazabilidad en el mismo cambio.

## 3. Casos de prueba

### TST-CAN-001 — Conteo e índices

**Preparación:** leer cada HTML sin ejecutar scripts y localizar tarjetas con
`data-exercise`.

**Comprobaciones:**

- cantidad de tarjetas igual a `exerciseCount`;
- índices únicos y exactamente contiguos;
- ningún ejercicio declarado desaparece del DOM canónico;
- cada tarjeta tiene título, métricas y tracker.

**Resultado esperado:** las cuatro salidas deben superar este caso; las
mutaciones sintéticas deben producir un fallo localizado.

### TST-CAN-002 — Suma de series efectivas

**Preparación:** extraer `data-series-keys` por tarjeta y contar las claves.

**Comprobaciones:**

- cada conjunto tiene claves `e{index}s1..e{index}sN`;
- la suma coincide con el total declarado;
- la distribución coincide con dashboard, resumen y documento del día;
- `warmupSet` no se suma como serie efectiva.

**Resultado esperado:** ningún total depende solo de texto visible; cualquier
discrepancia produce ubicación de archivo, ejercicio y valor esperado/real.

### TST-CAN-003 — Navegación sucesiva

**Preparación:** extraer cada `nextExerciseCue`, `data-next` y etiqueta visible.

**Comprobaciones:**

- tarjeta `i` apunta a `i + 1` cuando no es la última;
- la etiqueta del botón coincide con el título de la tarjeta `i + 1`;
- la última tarjeta muestra finalización y no un siguiente inexistente;
- no se permiten índices 0, repetidos o fuera del rango.

**Resultado esperado:** cualquier botón que no apunte al título siguiente se
reporta indicando el índice, etiqueta y valor esperado.

### TST-CAN-004 — Layout compartido

**Preparación:** leer cada HTML canónica sin ejecutar scripts y localizar el
contenedor de tarjetas, los índices de tarjeta y el footer de acciones.

**Comprobaciones:**

- existe exactamente un `<main class="cards">`;
- las tarjetas declaran `data-exercise-index="1..N"` sin huecos;
- existe exactamente un `<footer class="sessionFooter">`;
- no se conserva un footer alternativo de la fuente local.

**Resultado esperado:** las cuatro salidas tienen la misma estructura de página y
solo difieren en prescripción, contenido visual y contrato específico del día.

## 4. Casos negativos y de frontera

- HTML sin tarjetas.
- Dos tarjetas con el mismo `data-exercise`.
- Salto de índice, por ejemplo 2 → 4.
- `data-series-keys` vacío, duplicado o con `s0`.
- Total declarado distinto de la suma.
- Calentamiento contado como serie efectiva.
- Última tarjeta con `data-next`.
- Texto del dashboard con total correcto pero trackers incompletos.
- Atributo presente en una tarjeta y ausente en otra.

## 5. Implementación

El validador de solo lectura es
`scripts/validate_canonical_routines.py` y usa el parser HTML de la biblioteca
estándar o una estrategia equivalente estable. Debe:

1. recibir rutas explícitas o usar las cuatro canónicas por defecto;
2. emitir errores estructurados con archivo, ejercicio, atributo, esperado y
   observado;
3. devolver código distinto de cero ante cualquier discrepancia;
4. no modificar HTML, documentos, manifiestos ni artefactos;
5. poder ejecutarse desde PowerShell y desde una prueba Python; y
6. evitar volcar imágenes embebidas o contenido base64 en la salida.

Comando de ejecución sobre las cuatro salidas:

```powershell
python scripts/validate_canonical_routines.py
```

También acepta rutas explícitas para aislar un día durante el diagnóstico.

La prueba se mantiene separada del validador general; las mutaciones negativas
siguen siendo evidencia explícita y no se ocultan cambiando el esperado.

## 6. Evidencia requerida

- salida del validador con versión de Python y rutas revisadas;
- prueba de que el caso falla ante una mutación sintética de cada invariante;
- salida posterior sin discrepancias tras corregir el contenido;
- `python scripts/validate_repository.py` y `git diff --check`;
- revisión visual independiente para confirmar que el DOM corregido se ve y
  navega correctamente.

La prueba automatizada demuestra estructura y aritmética; no demuestra por sí
sola técnica de ejercicio, exactitud del equipo, experiencia de usuario ni
validez científica de la prescripción.

### Resultado ejecutado — 2026-10-09

- `validate_canonical_routines.py`: `CANONICAL_ROUTINES_OK routines=4`.
- Contratos: Día 1 `6/20 (4+4+3+3+3+3)`; Día 2 `6/20
  (3+3+3+4+3+4)`; Día 3 `7/22 (4+3+3+3+3+3+3)`; Día 4 `7/20
  (3+3+4+2+2+3+3)`.
- Pruebas de corrupción e invariantes: batería focalizada aprobada.
- Recorrido E2E local: 26 ejercicios y 82/82 series completadas con
  persistencia de clave, repeticiones, carga y duración; véase el
  [registro por ejercicio y serie](evidence/pwa-exercise-verification-2026-10-09.json).
- La ejecución es navegador local sintético; no certifica el Realme GT 6 ni
  el despliegue público.

## 7. Criterio de cierre

TDD-002 queda `Verified (local PWA)` para los contratos de estructura, series
y comportamiento sintético descritos en este documento. La validación en el
dispositivo instalado y en el despliegue público pertenece a TDD-005 y sigue
separada de esta evidencia.
