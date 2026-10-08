# Fuente modular 2D: jalón al pecho

Prototipo editable para Krita/OpenRaster con módulos independientes que se pueden abrir, modificar y colocar en otras composiciones. El personaje y la máquina se preparan primero como recursos separados; `lat-pulldown-modular.ora` los reúne como escena de ejercicio.

## Archivos

- `lat-pulldown-modular.ora`: composición por capas, con el estado inicial visible.
- `character.ora`: personaje separado en componentes; incluye variantes intercambiables de brazos.
- `machine.ora`: máquina separada en estructura, asiento, rodillo, placas, cables y barras; inicia en reposo.
- `preview-start.png` y `preview-pulled.png`: comprobación visual de las dos posiciones.
- `parts/*.svg`: fuente vectorial individual de cada pieza; el generador conserva sus ediciones por defecto.
- `parts/*.png`: raster de cada pieza utilizado por el documento ORA.
- Generador del repositorio: `scripts/build_modular_krita_source.py` (ejecutar desde la raíz).

Abre `character.ora` y `machine.ora` para editar cada recurso por separado y luego impórtalos como capas o grupos a una nueva escena. Para cambiar la escena de jalón en `lat-pulldown-modular.ora`, oculta «Brazos y manos · inicio», «Barra · arriba», «Cable · posición alta» y «Placas de carga · reposo»; muestra sus variantes «jalón», «al pecho», «posición de trabajo» y «elevadas».

Las SVG son la fuente de componentes; los documentos `.ora` y sus PNG son módulos y montajes de trabajo por capas. Al editar en Krita, guarda una copia `.kra` para conservar esa edición. El generador vuelve a componer los `.ora` desde las SVG. `--force-source` restaura las SVG al diseño base del código y reemplaza sus ediciones, así que no debe usarse después de personalizarlas.

Este primer montaje es una guía gráfica modular, no una animación final ni una evaluación biomecánica certificada. Antes de integrarlo a una rutina publicada, debe revisarse el recorrido y la geometría de la máquina con una referencia fiable y validar el movimiento completo.
