# Día 1 · Espalda + bíceps

**Estado:** `CANONICAL_TEMPLATE`
**Versión:** 1.0
**Fecha:** 2026-09-12
**Base visual:** `canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html`

## Objetivo

Documentar el contenido del Día 1 y la plantilla canónica reutilizable. La pantalla debe ser principalmente visual: el GIF o la secuencia de fotogramas explica el movimiento y el texto solo fija los puntos de decisión.

## Resumen de sesión

- **Título:** `DÍA 1 · ESPALDA + BÍCEPS`
- **Enfoque:** tirón vertical, remos, deltoides posterior y bíceps.
- **Perfil objetivo:** adulto sano de nivel intermedio, con margen de progresión hacia medio-avanzado.
- **Supuesto:** sin dolor limitante ni lesión conocida; si existe, la selección y el rango deben individualizarse.
- **Series efectivas:** `20`.
- **Distribución:** `4 + 4 + 3 + 3 + 3 + 3 = 20 series`.
- **Esfuerzo orientativo:** `RIR` (repeticiones en reserva) 2–3 al inicio y 1–2 en las últimas series de los compuestos; aislamientos en `RIR 1–2`.
- **Estado del material visual:** seis referencias locales mapeadas por patrón.

La serie de aproximación no forma parte de las 20 series efectivas.

## Contador de series

La ficha incluye un contador interactivo dentro de cada tarjeta, justo debajo de las métricas de series, repeticiones y descanso. Cada ejercicio permite marcar sus propias series efectivas; el jalón también tiene un botón independiente para la serie de aproximación. El avance de cada ejercicio se guarda localmente en el navegador y cada botón permite desmarcar una serie.

Cada serie marcada produce un pulso breve. Al completar todas las series del ejercicio aparece `✓ Completado` a la derecha, se ejecuta una celebración visual amplia y se muestra una flecha animada hacia el siguiente ejercicio; el último muestra `Sesión completada`. Las animaciones se desactivan con `prefers-reduced-motion`.

Al completar los seis ejercicios aparece una celebración global, con una frase motivacional cambiante tomada del banco local de 1,000 frases fitness traducidas al español. Los hitos emiten tonos sintetizados mediante `Web Audio API`, con control para silenciarlos. La celebración global no se reproduce automáticamente al recargar una sesión ya completada.

La ficha incluye además un resumen flotante, plegable y compacto. Muestra ejercicios terminados, series realizadas, series pendientes por ejercicio y permite marcar `Máquina ocupada` cuando una serie queda pendiente por disponibilidad del equipo. Este estado también se conserva localmente. El contador de cada ejercicio usa una única acción secuencial (`Completar serie`), por lo que no permite saltar directamente a una serie posterior.

El mensaje motivacional usa exclusivamente el banco local `frases_fitness/fitness_quotes.json`, con 1,000 frases seleccionadas por vocabulario explícito de ejercicio/deporte. Se cambia de forma secuencial; en pantalla solo aparecen la frase, el autor y, cuando existe una imagen local verificada, ese apoyo visual. No se atribuyen frases a una marca ni se consulta una API de frases aleatorias durante el uso.

El banco conserva por registro el texto, autor y temas; `fitness_quotes.js` es la copia embebible generada desde ese JSON para que la ficha siga funcionando sin conexión.

## Criterio científico actualizado

La prescripción se ajustó con síntesis recientes en adultos sanos. La revisión de posición de [ACSM 2026](https://pubmed.ncbi.nlm.nih.gov/41843416/) integra 137 revisiones sistemáticas y respalda que el entrenamiento de resistencia mejora la hipertrofia, que un volumen semanal mayor suele ayudar con rendimientos decrecientes y que no hay una ventaja consistente de entrenar siempre al fallo ni de un tipo concreto de equipo. La meta-regresión de [Pelland et al. 2026](https://pubmed.ncbi.nlm.nih.gov/41343037/) también encuentra una relación positiva entre volumen e hipertrofia, con rendimientos decrecientes, y advierte que las series indirectas deben contabilizarse con cautela.

Aplicación práctica para este día:

- Las `20` series son el volumen efectivo de esta sesión, no una garantía de volumen semanal óptimo. Para decidir si se añaden o retiran series hay que sumar el resto de la semana y contar el trabajo indirecto de bíceps, deltoides posterior y espalda.
- Se evita el fallo sistemático. El objetivo es terminar normalmente con `RIR 2–3` en los primeros compuestos, `RIR 1–2` en las últimas series y acercarse más solo si la técnica permanece estable. La evidencia de [Robinson et al. 2024](https://pubmed.ncbi.nlm.nih.gov/38970765/) favorece la cercanía al fallo para hipertrofia, pero la relación exacta es exploratoria y no justifica fallar en todas las series.
- Se mantienen descansos de `2–2.5 min` en los tirones principales y de `1.5–2 min` en aislamientos. La revisión de [Singer et al. 2024](https://pubmed.ncbi.nlm.nih.gov/39205815/) sugiere una pequeña ventaja sobre descansos de hasta 60 s, sin diferencias apreciables al superar aproximadamente 90 s; por eso el descanso se amplía si cae el rendimiento.
- El orden prioriza espalda antes de bíceps y pecho. El orden no parece cambiar por sí mismo la hipertrofia, pero colocar antes el objetivo prioritario protege el rendimiento de sus ejercicios; véase [Nunes et al. 2021](https://pubmed.ncbi.nlm.nih.gov/32077380/).
- El cardio previo se conserva por el requisito de la sesión, pero debe ser moderado y con prueba del habla, no intervalos ni una prueba de rendimiento. Una revisión de entrenamiento concurrente no observó interferencia consistente sobre hipertrofia o fuerza máxima; la señal de posible interferencia se concentra más en fuerza explosiva y en demandas de tren inferior ([Schumann et al. 2022](https://pubmed.ncbi.nlm.nih.gov/34757594/)). Si el primer ejercicio pierde claramente rendimiento, se reduce la intensidad del cardio sin reducir su duración.

**Supuesto y límite:** esta ficha representa una sesión, no el programa semanal completo. Sin conocer frecuencia, experiencia, recuperación y volumen de los demás días no es válido declarar que `20` series sea el óptimo individual.

## Verificación de máquinas

Se revisó la correspondencia entre el patrón del ejercicio y la referencia visual de la máquina. La revisión identifica la estación por su geometría funcional (polea o palancas, asiento, apoyo de pecho y rodillos), sin asumir que una marca o color implique superioridad fisiológica.

| # | Ejercicio | Referencia visual aplicada | Resultado |
|---:|---|---|---|
| 1 | Jalón al pecho | Estación de polea alta con barra recta, asiento y rodillos de muslo | Reemplazada; se eliminó la imagen de otra configuración y se alineó con la estación de la foto de ejecución |
| 2 | Remo alto unilateral | Panatta Super High Row, palancas independientes y apoyo de pecho | Confirmada |
| 3 | Remo horizontal en máquina | Panatta Super Rowing, asiento y apoyo frontal para remo | Confirmada |
| 4 | Apertura inversa en máquina | gym80 3025 Butterfly Reverse, vista frontal oficial, asiento y apoyo de pecho | Corregida; se reemplazó la imagen anterior de jalón por la referencia frontal oficial localizada |
| 5 | Curl de bíceps en máquina | Máquina selectorizada con apoyo de brazos | Confirmada |
| 6 | Curl de bíceps sentado en máquina | Máquina de palancas con respaldo, asas y agarre supino | Confirmada como referencia visual; no confirma el equipo instalado |

Las referencias de los ejercicios 2–6 se conservan porque su configuración visible coincide con el patrón descrito. La identidad exacta del equipo del gimnasio requiere una fotografía directa de cada estación; las fuentes de fabricante/distribuidor documentan el modelo de referencia, no la instalación concreta del usuario. El ejercicio 6 usa `0575` y no repite el press `0577` reservado para el Día 3.

## Preparación

- Cardio moderado: `16–17 min`.
- Movilidad dinámica y activación de hombros: `1–2 min`.
- Calentamiento específico: `1 serie de aproximación` del primer jalón.
- Ritmo de referencia: `1–2 s` en el esfuerzo y `2–3 s` en el regreso, sin rebotes.

La preparación se explica dentro de la sección visual de calentamiento; no se repite en tarjetas-resumen independientes.

Texto de apoyo:

> Prepara el movimiento con una carga progresiva. Las series de aproximación no cuentan como series efectivas. Reduce la carga si la postura o el recorrido dejan de ser estables.

### Calentamiento visual

La ficha muestra dos pasos antes de las tarjetas de ejercicios, cada uno con un recurso visual y, cuando aplica, una miniatura de respaldo. La serie de aproximación permanece integrada en el checklist del primer ejercicio:

1. **Cardio moderado:** `16–17 min`; elige elíptica, bicicleta estacionaria o caminadora inclinada a ritmo constante.
2. **Movilidad y activación de hombros:** `1–2 min`; movimiento dinámico y controlado, sin bandas, pared ni equipo. Se muestran dos GIF reales y diferenciados: círculos de brazos y círculos de hombros de pie, ambos con recorrido lento y cómodo.

Los GIF de los ejercicios y los dos GIF de movilidad se sirven desde archivos locales para evitar depender de URLs externas.

Criterio de selección: se priorizaron círculos de hombros y elevación controlada de brazos, movimientos corporales suaves descritos en recursos de fisioterapia del NHS. La animación local es una guía visual de recorrido, no una prescripción clínica; detenerse ante dolor o limitación.

La ficha integra el tiempo total, el volumen y el rango de descansos en una banda compacta junto al encabezado de la rutina principal; el enfoque muscular permanece en la cabecera de la sesión y el ritmo base en la guía rápida.

## Ejercicios y prescripción

| # | Ejercicio | Función visual | Series | Repeticiones | Descanso |
|---|---|---|---:|---:|---:|
| 1 | Jalón al pecho | Tirón vertical; codos hacia abajo y atrás | 4 | 8–12 | 2–2.5 min |
| 2 | Remo alto unilateral | Tirón unilateral con apoyo de pecho | 4 | 8–12 por lado | 2–2.5 min |
| 3 | Remo horizontal en máquina | Remo horizontal con pecho apoyado | 3 | 8–12 | 2–2.5 min |
| 4 | Apertura inversa en máquina | Deltoides posterior; brazos en arco horizontal | 3 | 12–20 | 1.5 min |
| 5 | Curl de bíceps en máquina | Flexión de codo con brazo apoyado | 3 | 10–15 | 1.5–2 min |
| 6 | Curl de bíceps sentado en máquina | Flexión de codo con espalda apoyada y agarre supino | 3 | 10–15 | 1.5–2 min |

Regla de progresión:

> Comienza cerca del límite inferior del rango. Cuando completes el límite superior en todas las series prescritas con técnica limpia y RIR 1–3, aumenta ligeramente la carga y vuelve al límite inferior.

## Plantilla gráfica de cada tarjeta

```text
NÚMERO · NOMBRE DEL EJERCICIO
Músculo principal · máquina o variante

[ GIF PRINCIPAL DE TÉCNICA ]
Inicio → recorrido → final

AJUSTE       EJECUCIÓN       RITMO       EVITA

3–4 series · 8–12 rep. · 2 min · RIR 1–3
Referencia visual · timestamp
```

### Reglas del GIF

- Debe mostrar el cuerpo y la máquina completos, sin cortar articulaciones, apoyos ni agarres.
- Debe tener un bucle corto, nítido y suficientemente lento para distinguir inicio, recorrido y final.
- Debe incluir una imagen estática de respaldo para `prefers-reduced-motion` y para carga fallida.
- Debe llevar texto alternativo descriptivo, no solo el nombre del ejercicio.
- El GIF demuestra una ejecución visual; no justifica por sí mismo series, repeticiones, descanso ni superioridad del equipo.
- Conservar identificador local, minuto/segundo de origen, fecha de consulta y SHA-256 del archivo local.
- No llamar `foto real`, `máquina exacta` o `técnica correcta` a un recurso que no haya sido comprobado para ese uso.

## Inventario visual histórico

Este inventario describe archivos de extracciones anteriores; no describe los
medios mostrados actualmente por la PWA. En la salida canónica del 9 de octubre
de 2026, los seis ejercicios usan una pareja estática Inicio/Final
(`data-media-mode="STATIC_ONLY"`). Los GIF candidatos de este inventario no se
insertan en esas tarjetas. El calentamiento conserva su visor GIF independiente.
La revisión de las seis parejas está en la
[evidencia visual](../../docs/05-quality/evidence/routine-phase-pairs-2026-10-09.jpg).

### Inventario local preliminar de una extracción anterior

La revisión local encontró cinco GIF técnicamente válidos y un marcador vacío:

- Cinco archivos tienen `6` fotogramas, resolución `400×400` y duración total aproximada de `1.82 s`.
- Un archivo tiene `34` bytes y dimensiones `1×1`; se descarta como medio visual.
- La inspección de fotogramas sugiere candidatos para curl, remo y jalón, pero esa observación no demuestra todavía qué ejercicio representa cada archivo.
- Los registros extraídos no conservan un identificador utilizable para estos GIF; permanecen como candidatos históricos, no como medios aprobados.

Por tanto, ningún archivo de este inventario se incrustará en la ficha hasta completar la relación `ejercicio → recurso → patrón → archivo local`.

### Candidatos históricos por orden de extracción

La extracción del HTML histórico v20 conserva el orden de los medios, pero no una fuente reutilizable. La tabla sirve para auditoría, no para aprobar la técnica:

| Ejercicio del HTML histórico | Ocurrencia GIF | Recurso local | Resultado de la revisión visual |
|---|---:|---|---|
| Panatta Super High Row · unilateral | 7 | `9591406174d72d098640c0b02844249daf082ec90eb6a5cf3f3613c5a6b1282f.gif` | `PENDIENTE`: el fotograma parece un jalón; no coincide de forma suficiente con el título |
| Panatta Super Rowing · remo horizontal | 11 | `87fcf78d64eeb8bc519dac0de15191fe06c66c7019a7884412eea3ca728963c2.gif` | `PENDIENTE`: equipo y trayectoria no están confirmados |
| Jalón al pecho · máquina selectorized | 15 | `d58cd315059b6518fd7488765cf362368020c91600b7e1c8bd018b20466247a7.gif` | `PENDIENTE`: el fotograma parece un remo; no se reutiliza |
| Reverse fly / rear delt · máquina | 19 | `74cf0090f65381e5bbcef2b9aeb567932998ebc18d084d6da14649f380950970.gif` | `PENDIENTE`: el gesto parece un remo; no se reutiliza |
| Curl de bíceps · máquina con apoyo | 23 | `0e40c4b93ce53de1a27e36f3bc42b3c387f5d0c29044ad620eebe1e5ef3c9686.gif` | `CANDIDATO`: el gesto parece compatible, pero la correspondencia no está confirmada |
| Curl martillo · máquina de agarre neutro | — | — | `SIN RECURSO HISTÓRICO` |

La conclusión operativa es conservar estos archivos solo como evidencia de extracción y buscar para cada tarjeta un recurso cuya identidad y técnica se puedan verificar independientemente. La apariencia del fotograma no basta para corregir el mapeo del HTML.

### Candidatos históricos de la fuente versionada de ejercicios

Para la maqueta se localizaron seis candidatos de ejercicio y dos GIF de calentamiento en `artifacts/ejercicios-compartido/`. Sus hashes y miniaturas son evidencia de origen, no prueba de que estén publicados en las tarjetas actuales.

La tarjeta debe mostrar una referencia visual clara y un fallback estático cuando corresponda.

## Textos técnicos

### 1 · Jalón al pecho

- **Ajuste:** Ajusta el asiento y los rodillos para que los muslos queden firmes sin levantarse. Toma la barra sin saltar y mantén los pies apoyados.
- **Ejecución:** Lleva los codos hacia abajo y ligeramente hacia atrás hasta acercar la barra a la parte alta del pecho, sin convertir el movimiento en un balanceo.
- **Ritmo:** Exhala durante el tirón y regresa en 2–3 s, permitiendo el estiramiento sin perder el control del torso.
- **Evita:** Tirar detrás de la nuca, arquear excesivamente la zona lumbar o usar impulso.

### 2 · Remo alto unilateral

- **Ajuste:** Regula asiento y apoyo de pecho para quedar estable. Mantén el esternón en el apoyo durante todo el movimiento.
- **Ejecución:** Tira del codo hacia abajo y atrás siguiendo la palanca, manteniendo pelvis y tórax orientados al frente.
- **Ritmo:** Exhala al remar, controla brevemente la contracción y regresa en 2–3 s.
- **Evita:** Girar el tronco, despegar el pecho, encoger el hombro o recortar el recorrido por usar demasiado peso.

### 3 · Remo horizontal en máquina

- **Ajuste:** Centra el pecho sobre el apoyo y regula el asiento para alcanzar los agarres con los brazos extendidos.
- **Ejecución:** Rema hacia las costillas o el abdomen alto sin despegar el pecho del soporte.
- **Ritmo:** Exhala al tirar, pausa brevemente atrás y deja avanzar las escápulas de forma controlada al regresar.
- **Evita:** Dar tirones con el torso, hiperextender la espalda baja o golpear la carga.

### 4 · Apertura inversa en máquina

- **Ajuste:** Coloca hombros y agarres aproximadamente a la misma altura. Mantén el pecho apoyado y los codos ligeramente flexionados.
- **Ejecución:** Abre los brazos en un arco horizontal guiando con los codos. Detente cuando los brazos queden cerca de la línea del torso.
- **Ritmo:** Exhala al abrir y vuelve en 2–3 s conservando la misma flexión del codo.
- **Evita:** Convertirlo en un remo, elevar los hombros o buscar un rango excesivo.

### 5 · Curl de bíceps en máquina

- **Ajuste:** Alinea el codo con el eje de giro. Apoya completamente la parte posterior del brazo y mantén las muñecas rectas.
- **Ejecución:** Flexiona el codo sin despegar el brazo del apoyo. Sube hasta una contracción fuerte y cómoda.
- **Ritmo:** Exhala al subir y desciende en 2–3 s sin dejar caer la carga.
- **Evita:** Levantar los hombros, adelantar los codos, doblar las muñecas o rebotar en la parte baja.

### 6 · Curl de bíceps sentado en máquina

- **Ajuste:** Regula la altura del asiento y apoya la espalda en la almohadilla. Mantén los codos cerca de los costados y las muñecas neutras.
- **Ejecución:** Sujeta las asas con agarre supino, flexiona los codos y eleva los mangos sin despegar los brazos del soporte.
- **Ritmo:** Exhala al subir, pausa brevemente arriba e inhala mientras bajas en 2–3 s hasta extender los brazos.
- **Evita:** Impulsarte con el tronco, adelantar los codos, doblar las muñecas o bloquear la articulación al final.

## Cierre de sesión

- **Técnica:** recorrido controlado y postura estable.
- **Carga:** termina normalmente con 1–3 repeticiones posibles sin perder la técnica.
- **Progresión:** sube repeticiones dentro del rango y después aumenta ligeramente la carga.
- **Control:** dolor articular agudo, hormigueo o pérdida clara de posición detienen la serie.
- **Duración orientativa:** `17–19 min` de preparación + aproximadamente `45–60 min` de trabajo efectivo y descansos + transiciones; por eso `75–95 min` es un rango operativo, no una medición individual.

## Criterios de aceptación

- El resumen muestra exactamente `20 series efectivas`.
- Cada tarjeta muestra 3 o 4 series y el rango de repeticiones correspondiente.
- Cada ejercicio tiene GIF o secuencia estática de respaldo con procedencia trazable.
- Cada tarjeta declara `data-media-mode="STATIC_ONLY"` mientras use su pareja estática; no muestra un rótulo que prometa un GIF inexistente.
- Ningún medio se presenta como real, exacto o clínicamente validado sin evidencia específica.
- La composición sigue siendo legible en escritorio y móvil.
- Se revisan correspondencia visual, integridad y SHA-256 antes de incrustar medios.
- Se ejecuta `python scripts/validate_repository.py` antes de proponer integración.

## Pendientes

1. Confirmar derechos de redistribución antes de publicar medios de terceros.
2. Verificar el render en la PWA instalada en el GT6 cuando ADB esté disponible; la cobertura local de navegador no sustituye esa comprobación.
3. Recalcular la duración estimada si cambia la prescripción; `75–95 min` sigue siendo una estimación heredada, no una medición individual.
