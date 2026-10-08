#!/usr/bin/env python3
"""Build a layered, reusable 2D lat-pulldown study for Krita/OpenRaster."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "data" / "rutinas_autocontenidas" / "medios_publicados" / "rutinas_autocontenidas" / "mascot_exercise_motion"
OUTPUT_DIR = ASSET_DIR / "editable" / "modular-lat-pulldown"
WIDTH = 800
HEIGHT = 900

DEFS = '''<defs>
  <linearGradient id="steel" x2="1" y2="0"><stop stop-color="#59646b"/><stop offset=".2" stop-color="#f0f4f5"/><stop offset=".48" stop-color="#a9b3b8"/><stop offset=".72" stop-color="#f8fafb"/><stop offset="1" stop-color="#657178"/></linearGradient>
  <linearGradient id="darkSteel" x2="0" y2="1"><stop stop-color="#424b50"/><stop offset=".45" stop-color="#171d20"/><stop offset="1" stop-color="#555f63"/></linearGradient>
  <linearGradient id="fabric" x2="0" y2="1"><stop stop-color="#313a40"/><stop offset="1" stop-color="#101518"/></linearGradient>
  <linearGradient id="skin" x2="1" y2="1"><stop stop-color="#ffd09d"/><stop offset=".48" stop-color="#e99a62"/><stop offset="1" stop-color="#b85e3f"/></linearGradient>
  <linearGradient id="hair" x2=".85" y2="1"><stop stop-color="#303239"/><stop offset=".53" stop-color="#11161b"/><stop offset=".78" stop-color="#087d79"/><stop offset="1" stop-color="#123e47"/></linearGradient>
  <linearGradient id="tail" x2="1" y2="1"><stop stop-color="#ffbf68"/><stop offset=".5" stop-color="#f27643"/><stop offset="1" stop-color="#d94832"/></linearGradient>
  <filter id="shadow" x="-.3" y="-.3" width="1.6" height="1.7"><feGaussianBlur stdDeviation="7"/></filter>
</defs>'''


def svg(body: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">{DEFS}{body}</svg>'


FRAME = svg('''
<g stroke="#171c1f" stroke-width="9" stroke-linejoin="round">
 <path d="M132 744h386l44 28H105z" fill="url(#steel)"/>
 <path d="M128 754h72v25h-72zM465 754h80v25h-80z" fill="url(#darkSteel)"/>
 <path d="M231 156h28v590h-28z" fill="url(#steel)"/>
 <path d="M266 153h31v593h-31z" fill="url(#steel)"/>
 <path d="M237 169c-3-49 22-75 69-75h46v29h-42c-25 0-38 12-38 39z" fill="url(#steel)"/>
 <path d="M266 96h75v27h-75z" fill="url(#steel)"/>
 <path d="M326 96h24v37h-24z" fill="url(#darkSteel)"/>
 <circle cx="326" cy="139" r="22" fill="url(#darkSteel)"/>
 <circle cx="326" cy="139" r="8" fill="#cbd3d6" stroke-width="5"/>
 <path d="M231 208h-21v425h21M297 208h14v425h-14" fill="none" stroke="#747e83" stroke-width="8"/>
 <path d="M277 565v169h24V565M255 577h167v27H255" fill="url(#steel)"/>
 <path d="M414 590h28v162h-28z" fill="url(#steel)"/>
 <path d="M406 738h50v28h-50z" fill="url(#darkSteel)"/>
 <circle cx="247" cy="716" r="7" fill="#e7ecee" stroke-width="4"/><circle cx="285" cy="716" r="7" fill="#e7ecee" stroke-width="4"/>
</g>
''')

STACK_BODY = '''
<g stroke="#080b0d" stroke-width="4" stroke-linejoin="round" fill="url(#darkSteel)">
 <path d="M202 263h74v27h-74zM202 294h74v27h-74zM202 325h74v27h-74zM202 356h74v27h-74zM202 387h74v27h-74zM202 418h74v27h-74zM202 449h74v27h-74zM202 480h74v27h-74zM202 511h74v27h-74zM202 542h74v27h-74z"/>
 <path d="M207 270h64M207 301h64M207 332h64M207 363h64M207 394h64M207 425h64M207 456h64M207 487h64M207 518h64M207 549h64" fill="none" stroke="#7d878b" stroke-width="2"/>
 <path d="M215 255v-30h48v30" fill="url(#steel)"/><circle cx="239" cy="431" r="7" fill="#e4a346"/>
</g>'''
STACK_REST = svg(STACK_BODY)
STACK_LIFTED = svg(f'<g transform="translate(0 -34)">{STACK_BODY}</g>')

SEAT = svg('''
<g stroke="#14191c" stroke-width="7" stroke-linejoin="round">
 <path d="M358 542h174q14 0 14 13v18H354z" fill="url(#fabric)"/>
 <path d="M385 558h122v10H385z" fill="#0d1113" stroke="none"/>
</g>''')

THIGH_ROLLER = svg('''
<g stroke="#14191c" stroke-width="7" stroke-linejoin="round">
 <path d="M378 502q0-15 15-15h160q15 0 15 15v19H378z" fill="url(#darkSteel)"/>
 <path d="M390 501h153" fill="none" stroke="#7d878b" stroke-width="3"/>
 <circle cx="385" cy="511" r="8" fill="#e64d3f" stroke="#8e2b23" stroke-width="3"/>
 <path d="M559 509h18" stroke="#aab3b7" stroke-width="8"/>
</g>''')

LEGS_TAIL = svg('''
<!-- Cola detrás de la cadera: identidad visual de la mascota. -->
<path d="M441 493c-58 2-111-19-119-68-5-31 14-59 45-70 28-10 52 1 58 22-19-10-40-5-48 11-13 26 9 49 51 48l44 22z" fill="none" stroke="#9a402b" stroke-width="24" stroke-linecap="round"/>
<path d="M441 493c-58 2-111-19-119-68-5-31 14-59 45-70 28-10 52 1 58 22-19-10-40-5-48 11-13 26 9 49 51 48l44 22z" fill="none" stroke="url(#tail)" stroke-width="17" stroke-linecap="round"/>
<!-- Muslos apoyados en el asiento, rodillas flexionadas; pies en el suelo. -->
<g stroke="#090d10" stroke-width="7" stroke-linejoin="round">
 <path d="M430 481q-48 4-67 39l10 59q25 23 70 7l32-43-9-48z" fill="url(#fabric)"/>
 <path d="M478 484q50-5 77 31l-8 66q-28 18-72 2l-29-42 9-42z" fill="url(#fabric)"/>
 <path d="M380 567q-4 62-17 128l7 24q27 12 56 0l8-22q-9-68 8-112l-29-24z" fill="url(#fabric)"/>
 <path d="M528 566q9 67 25 127l-7 25q-27 12-56 0l-9-21q9-67-8-112l27-23z" fill="url(#fabric)"/>
 <!-- Zapatillas estables apoyadas; suela y puntera legibles. -->
 <path d="M365 713q18-7 42 0l13 26q28 3 40 20v15h-97q-13-7-9-21z" fill="#20272c"/>
 <path d="M490 713q18-7 42 0l13 26q28 3 40 20v15h-97q-13-7-9-21z" fill="#20272c"/>
 <path d="M357 760h105v14H357q-9-5 0-14zm125 0h105v14H482q-9-5 0-14z" fill="#f0f2ef" stroke-width="4"/>
 <path d="M385 727l22 13m-13-18 20 12m92-7 22 13m-12-18 20 12" fill="none" stroke="#eef1ed" stroke-width="4"/>
 <path d="M397 738l14 8m103-8 14 8" fill="none" stroke="#e64d3f" stroke-width="6"/>
</g>''')

TORSO = svg('''
<g stroke="#111619" stroke-linejoin="round">
 <!-- Cintura y abdomen: torso erguido, leve inclinación desde la cadera. -->
 <path d="M435 353q-31 19-35 54l8 79q14 15 54 15t59-15l8-79q-7-37-41-54z" fill="url(#skin)" stroke-width="6"/>
 <path d="M415 373q-8-25 8-35l32 6q27 4 50-3l23 21-9 67q-47 24-104 0z" fill="url(#fabric)" stroke-width="7"/>
 <path d="M430 379q44 19 87 0M456 450q18 7 35 0" fill="none" stroke="#566168" stroke-width="3" opacity=".8"/>
 <path d="M409 471q45 20 111 0l6 25q-54 21-123 0z" fill="#141a1e" stroke-width="5"/>
 <path d="M452 487v15m12-15v15m12-15v15" stroke="#69737a" stroke-width="3"/>
</g>''')

HEAD = svg('''
<!-- Cabello posterior y mechones teal, separado del rostro para edición. -->
<path d="M414 287q-5-73 56-83 62-7 78 50 17 47 0 106l-24 36-23-48-76 13-29 38q-21-47-9-112z" fill="url(#hair)" stroke="#101519" stroke-width="8" stroke-linejoin="round"/>
<path d="M423 323q-22 55-13 88 20-10 31-42m82-44q20 43 10 76-19-11-25-37" fill="none" stroke="#087d79" stroke-width="13" stroke-linecap="round"/>
<!-- Orejas felinas de la mascota; no son piezas de la máquina. -->
<path d="M421 249l-4-43q1-10 10-4l38 36m38 2 26-35q7-8 12 1l2 51" fill="#171c20" stroke="#101519" stroke-width="7" stroke-linejoin="round"/>
<path d="M425 232l-1-17 19 17m65 2 13-18 1 22" fill="#f07857"/>
<ellipse cx="477" cy="285" rx="49" ry="58" fill="url(#skin)" stroke="#422b27" stroke-width="5"/>
<path d="M431 273q6-58 55-57 41 2 46 43-24-21-45-18-30 3-56 32z" fill="url(#hair)" stroke="#101519" stroke-width="6"/>
<path d="M432 279q10-29 32-38m-7 50q14-9 27-1m18 1q12-8 23 0" fill="none" stroke="#422b27" stroke-width="4" stroke-linecap="round"/>
<!-- Gafas teal con lentes claros. -->
<g fill="none" stroke="#172126" stroke-width="5"><rect x="438" y="278" width="31" height="22" rx="9"/><rect x="484" y="278" width="31" height="22" rx="9"/><path d="M469 286h15m31-2 15-5"/></g>
<path d="M457 290h9m35 0h8" stroke="#fff4db" stroke-width="4" stroke-linecap="round"/>
<path d="M474 310q5 4 10 0m-17 16q11 10 23 0" fill="none" stroke="#773e36" stroke-width="3" stroke-linecap="round"/>
<path d="M420 260q18-43 57-45" fill="none" stroke="#00a89f" stroke-width="8" stroke-linecap="round"/>
''')


def arms(pose: str) -> str:
    if pose == "start":
        left = 'M426 372q-17-6-27-28l-29-68q-11-24-20-49l-12-38 22-10 18 31q15 29 23 55l42 79z'
        right = 'M519 372q17-6 27-28l29-68q11-24 20-49l12-38-22-10-18 31q-15 29-23 55l-42 79z'
        hands = '''<path d="M321 180q-2-11 8-15l10 1 8 12-5 11-13 1zm279 0q2-11-8-15l-10 1-8 12 5 11 13 1z" fill="url(#skin)" stroke="#6e392d" stroke-width="4"/>'''
        cuffs = '<path d="M323 181l21 3m276-3-21 3" stroke="#ed4c40" stroke-width="8"/>'
        pose_label = "inicio"
    else:
        left = 'M426 372q-21-6-35 19l-15 28q-9 16-24 10l-16-17q5-16 15-30l22-30q24-25 53-7z'
        right = 'M519 372q21-6 35 19l15 28q9 16 24 10l16-17q-5-16-15-30l-22-30q-24-25-53-7z'
        hands = '''<path d="M325 405q0-12 11-14l11 3 5 12-8 11-13-3zm293 0q0-12-11-14l-11 3-5 12 8 11 13-3z" fill="url(#skin)" stroke="#6e392d" stroke-width="4"/>'''
        cuffs = '<path d="M324 414l21 3m272-3-21 3" stroke="#ed4c40" stroke-width="8"/>'
        pose_label = "tiron"
    return svg(f'''<g stroke="#60372c" stroke-width="5" stroke-linejoin="round">
 <path d="{left}" fill="url(#skin)"/><path d="{right}" fill="url(#skin)"/>
 {hands}
 {cuffs}
 </g><!-- articulation pivots: shoulders/elbows/wrists are intentionally jointed -->''')


def cable(pose: str) -> str:
    y = 178 if pose == "start" else 395
    return svg(f'''<path d="M326 139Q334 163 353 173L470 {y}" fill="none" stroke="#171c20" stroke-width="5"/>
 <path d="M326 139Q334 163 353 173L470 {y}" fill="none" stroke="#929da2" stroke-width="1.5"/>
 <circle cx="470" cy="{y}" r="8" fill="#dce2e4" stroke="#14191c" stroke-width="4"/>''')


def bar(pose: str) -> str:
    y = 178 if pose == "start" else 395
    return svg(f'''<g transform="translate(0 {y - 220})" stroke="#171c20" stroke-linejoin="round">
 <path d="M309 213q-14 7 0 14l24 15m274-29q14 7 0 14l-24 15" fill="none" stroke="#111619" stroke-width="16" stroke-linecap="round"/>
 <path d="M330 220h280" fill="none" stroke="#b9c3c7" stroke-width="15" stroke-linecap="round"/>
 <path d="M332 217h276" fill="none" stroke="#f5f7f7" stroke-width="2"/>
 <path d="M345 209v22m12-22v22m230-22v22m12-22v22" stroke="#20282d" stroke-width="4"/>
 <circle cx="470" cy="220" r="10" fill="#68747a" stroke-width="3"/>
 </g>''')


def parts() -> list[tuple[str, str, str, bool]]:
    return [
        ("Brazos y manos · inicio", "arms-start", arms("start"), True),
        ("Barra · arriba", "bar-start", bar("start"), True),
        ("Brazos y manos · jalón", "arms-pulled", arms("pulled"), False),
        ("Barra · al pecho", "bar-pulled", bar("pulled"), False),
        ("Cable · posición alta", "cable-start", cable("start"), True),
        ("Cable · posición de trabajo", "cable-pulled", cable("pulled"), False),
        ("Rostro y cabello · mascota", "mascot-head", HEAD, True),
        ("Torso y ropa · mascota", "mascot-torso", TORSO, True),
        ("Placas de carga · elevadas (jalón)", "weight-stack-lifted", STACK_LIFTED, False),
        ("Rodillo de muslos · sobre piernas", "thigh-restraint", THIGH_ROLLER, True),
        ("Piernas, calzado y cola · mascota", "mascot-legs-tail", LEGS_TAIL, True),
        ("Asiento y soporte", "seat-thigh-restraint", SEAT, True),
        ("Placas de carga · reposo", "weight-stack-rest", STACK_REST, True),
        ("Estructura, polea y soporte", "machine-frame", FRAME, True),
    ]


def render_layers(
    output_dir: Path,
    all_parts: list[tuple[str, str, str, bool]],
    force_source: bool = False,
) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    parts_dir = output_dir / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT}, device_scale_factor=1)
        for _name, key, source, _visible in all_parts:
            svg_path = parts_dir / f"{key}.svg"
            if svg_path.exists() and not force_source:
                source = svg_path.read_text(encoding="utf-8")
            else:
                svg_path.write_text(source, encoding="utf-8")
            page.set_content(f'<html><body style="margin:0;width:{WIDTH}px;height:{HEIGHT}px">{source}</body></html>')
            png = page.locator("svg").screenshot(omit_background=True, animations="disabled")
            rendered[key] = png
            (parts_dir / f"{key}.png").write_bytes(png)
        browser.close()
    return rendered


def build_project(output_dir: Path = OUTPUT_DIR, force_source: bool = False) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_parts = parts()
    rendered = render_layers(output_dir, all_parts, force_source=force_source)

    stack = ElementTree.Element("image", {"version": "0.0.1", "w": str(WIDTH), "h": str(HEIGHT), "name": "Jalón al pecho · rig 2D modular"})
    layer_stack = ElementTree.SubElement(stack, "stack", {"name": "Personaje + máquina · poses editables"})
    for name, key, _source, visible in all_parts:
        ElementTree.SubElement(layer_stack, "layer", {
            "name": name,
            "src": f"data/{key}.png",
            "opacity": "1.0",
            "visibility": "visible" if visible else "hidden",
            "composite-op": "svg:src-over",
            "x": "0",
            "y": "0",
        })

    # ORA lists layers top-to-bottom; composite from bottom to top for previews.
    def compose(pose: str) -> Image.Image:
        selected = {key for _name, key, _source, visible in all_parts if visible}
        if pose == "pulled":
            selected.difference_update({"arms-start", "bar-start", "cable-start", "weight-stack-rest"})
            selected.update({"arms-pulled", "bar-pulled", "cable-pulled", "weight-stack-lifted"})
        composite = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        for _name, key, _source, _visible in reversed(all_parts):
            if key in selected:
                composite.alpha_composite(Image.open(BytesIO(rendered[key])).convert("RGBA"))
        canvas = Image.new("RGBA", (WIDTH, HEIGHT), (241, 246, 248, 255))
        canvas.alpha_composite(composite)
        return canvas.convert("RGB")

    preview_path = output_dir / "preview-start.png"
    preview = compose("start")
    preview.save(preview_path, optimize=True)
    finish_preview_path = output_dir / "preview-pulled.png"
    compose("pulled").save(finish_preview_path, optimize=True)

    # Exportar personaje y máquina como documentos independientes permite
    # reutilizarlos y colocarlos en nuevas escenas sin reconstruir sus piezas.
    reusable_modules = {
        "character.ora": {
            "mascot-head": ("Cabeza y cabello · personaje", True),
            "mascot-torso": ("Torso y ropa · personaje", True),
            "arms-start": ("Brazos · pose inicial", True),
            "arms-pulled": ("Brazos · pose de jalón", False),
            "mascot-legs-tail": ("Piernas, calzado y cola · personaje", True),
        },
        "machine.ora": {
            "machine-frame": ("Estructura, polea y soporte", True),
            "seat-thigh-restraint": ("Asiento y soporte de muslos", True),
            "thigh-restraint": ("Rodillo de muslos", True),
            "weight-stack-rest": ("Placas de carga · reposo", True),
            "weight-stack-lifted": ("Placas de carga · elevadas", False),
            "cable-start": ("Cable · posición inicial", True),
            "cable-pulled": ("Cable · posición de jalón", False),
            "bar-start": ("Barra · posición elevada", True),
            "bar-pulled": ("Barra · posición al pecho", False),
        },
    }

    def write_reusable_module(filename: str, selected_parts: dict[str, tuple[str, bool]]) -> Path:
        module_stack = ElementTree.Element("image", {
            "version": "0.0.1", "w": str(WIDTH), "h": str(HEIGHT),
            "name": Path(filename).stem.replace("-", " ").title() + " · módulo reutilizable",
        })
        module_layers = ElementTree.SubElement(module_stack, "stack", {"name": "Componentes editables"})
        for key, (label, visible) in selected_parts.items():
            ElementTree.SubElement(module_layers, "layer", {
                "name": label, "src": f"data/{key}.png", "opacity": "1.0",
                "visibility": "visible" if visible else "hidden", "composite-op": "svg:src-over", "x": "0", "y": "0",
            })
        composite = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        for key, (_label, visible) in reversed(list(selected_parts.items())):
            if visible:
                composite.alpha_composite(Image.open(BytesIO(rendered[key])).convert("RGBA"))
        buffer = BytesIO()
        composite.save(buffer, format="PNG", optimize=True)
        merged = buffer.getvalue()
        thumbnail = composite.copy()
        thumbnail.thumbnail((256, 256), Image.Resampling.LANCZOS)
        thumb_buffer = BytesIO()
        thumbnail.save(thumb_buffer, format="PNG", optimize=True)
        path = output_dir / filename
        with ZipFile(path, "w") as archive:
            archive.writestr("mimetype", "image/openraster", compress_type=ZIP_STORED)
            archive.writestr("stack.xml", ElementTree.tostring(module_stack, encoding="utf-8", xml_declaration=True), compress_type=ZIP_DEFLATED)
            archive.writestr("mergedimage.png", merged, compress_type=ZIP_DEFLATED)
            archive.writestr("Thumbnails/thumbnail.png", thumb_buffer.getvalue(), compress_type=ZIP_DEFLATED)
            for key in selected_parts:
                archive.writestr(f"data/{key}.png", rendered[key], compress_type=ZIP_DEFLATED)
        with ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"Documento ORA reutilizable dañado: {filename}")
            verified = ElementTree.fromstring(archive.read("stack.xml"))
            verified_layers = verified.find("stack")
            if verified_layers is None or len(verified_layers) != len(selected_parts):
                raise ValueError(f"Pila incompleta en módulo reutilizable: {filename}")
        return path

    for filename, module_parts in reusable_modules.items():
        write_reusable_module(filename, module_parts)

    ora_path = output_dir / "lat-pulldown-modular.ora"
    thumbnail = preview.copy()
    thumbnail.thumbnail((256, 256), Image.Resampling.LANCZOS)
    with ZipFile(ora_path, "w") as archive:
        archive.writestr("mimetype", "image/openraster", compress_type=ZIP_STORED)
        archive.writestr("stack.xml", ElementTree.tostring(stack, encoding="utf-8", xml_declaration=True), compress_type=ZIP_DEFLATED)
        archive.writestr("mergedimage.png", preview_path.read_bytes(), compress_type=ZIP_DEFLATED)
        buffer = BytesIO()
        thumbnail.save(buffer, format="PNG", optimize=True)
        archive.writestr("Thumbnails/thumbnail.png", buffer.getvalue(), compress_type=ZIP_DEFLATED)
        for _name, key, _source, _visible in all_parts:
            archive.writestr(f"data/{key}.png", rendered[key], compress_type=ZIP_DEFLATED)

    with ZipFile(ora_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("El ORA modular contiene datos ZIP dañados")
        check = ElementTree.fromstring(archive.read("stack.xml"))
        check_layers = check.find("stack")
        if check_layers is None or len(check_layers) != len(all_parts):
            raise ValueError("La pila de capas del ORA no coincide con sus componentes")
        keys = [layer.attrib["src"] for layer in check_layers]
        if len(keys) != len(set(keys)):
            raise ValueError("Hay referencias de capa duplicadas")
        visible_layers = [layer for layer in check_layers if layer.attrib["visibility"] == "visible"]
        if not visible_layers or not any("inicio" in layer.attrib["name"] or "arriba" in layer.attrib["name"] for layer in visible_layers):
            raise ValueError("El documento no presenta el estado inicial del ejercicio")
        for key in keys:
            with Image.open(BytesIO(archive.read(key))) as image:
                image.verify()
                if image.size != (WIDTH, HEIGHT):
                    raise ValueError(f"Dimensiones de capa incorrectas: {key}")
    return ora_path, preview_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Genera la fuente modular por capas para Krita.")
    parser.add_argument("--force-source", action="store_true", help="Restaura las SVG al diseño base definido por el generador.")
    options = parser.parse_args()
    ora, preview = build_project(force_source=options.force_source)
    print(f"MODULAR_KRITA_SOURCE_OK layers={len(parts())} ora={ora} preview={preview}")
