#!/usr/bin/env python3
"""Create an editable OpenRaster pose-sheet project from the 2x2 pilot sheet.

Each pose is preserved as its own layer. The character and machine remain one
painted image per pose because the source sheet does not contain separated art.
Krita can open the resulting .ora file and save it as its native .kra format.
"""

from __future__ import annotations

from io import BytesIO
import argparse
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "data" / "rutinas_autocontenidas" / "medios_publicados" / "rutinas_autocontenidas" / "mascot_exercise_motion"
OUTPUT_DIR = ASSET_DIR / "editable"
POSE_NAMES = (
    "Pose 01 - brazos extendidos",
    "Pose 02 - inicio del jalon",
    "Pose 03 - barra al pecho",
    "Pose 04 - contraccion controlada",
)


def png_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def create_project(
    sheet_path: Path = ASSET_DIR / "day1-exercise01-lat-pulldown-sheet.png",
    output_path: Path | None = None,
) -> Path:
    """Build one standard layered ORA source from a four-pose contact sheet."""
    sheet_path = Path(sheet_path)
    if output_path is None:
        output_path = OUTPUT_DIR / f"{sheet_path.stem.removesuffix('-sheet')}.ora"
    output_path = Path(output_path)
    with Image.open(sheet_path) as source:
        source.load()
        if source.width % 2 or source.height % 2 or source.width // 2 != source.height // 2:
            raise ValueError(f"Se esperaba una hoja 2x2 con poses cuadradas; se recibió {source.size}")
        width, height = source.size[0] // 2, source.size[1] // 2
        poses = [
            source.crop((column * width, row * height, (column + 1) * width, (row + 1) * height)).convert("RGBA")
            for row in range(2)
            for column in range(2)
        ]
        reference = source.convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)

    title = sheet_path.stem.removesuffix("-sheet").replace("-", " ").title()
    stack = ElementTree.Element("image", {"version": "0.0.1", "w": str(width), "h": str(height), "name": f"{title} - fuente 2D"})
    layers = ElementTree.SubElement(stack, "stack", {"name": f"{title} | poses y referencia"})
    ElementTree.SubElement(layers, "layer", {
        "name": "Referencia - hoja original (50%)",
        "src": "data/reference.png",
        "opacity": "1.0",
        "visibility": "hidden",
        "composite-op": "svg:src-over",
        "x": "0",
        "y": "0",
    })
    for index in reversed(range(len(poses))):
        ElementTree.SubElement(layers, "layer", {
            "name": POSE_NAMES[index],
            "src": f"data/pose-{index + 1:02d}.png",
            "opacity": "1.0",
            "visibility": "visible" if index == 0 else "hidden",
            "composite-op": "svg:src-over",
            "x": "0",
            "y": "0",
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged = png_bytes(poses[0])
    thumbnail = poses[0].copy()
    thumbnail.thumbnail((256, 256), Image.Resampling.LANCZOS)
    with ZipFile(output_path, "w") as archive:
        archive.writestr("mimetype", "image/openraster", compress_type=ZIP_STORED)
        archive.writestr("stack.xml", ElementTree.tostring(stack, encoding="utf-8", xml_declaration=True), compress_type=ZIP_DEFLATED)
        archive.writestr("mergedimage.png", merged, compress_type=ZIP_DEFLATED)
        archive.writestr("Thumbnails/thumbnail.png", png_bytes(thumbnail), compress_type=ZIP_DEFLATED)
        archive.writestr("data/reference.png", png_bytes(reference), compress_type=ZIP_DEFLATED)
        for index, pose in enumerate(poses, start=1):
            archive.writestr(f"data/pose-{index:02d}.png", png_bytes(pose), compress_type=ZIP_DEFLATED)

    with ZipFile(output_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("OpenRaster contiene una entrada ZIP dañada")
        metadata = ElementTree.fromstring(archive.read("stack.xml"))
        layer_stack = metadata.find("stack")
        if layer_stack is None or len(layer_stack) != 5:
            raise ValueError("El documento no contiene las cuatro poses y la referencia esperadas")
        pose_layers = [layer for layer in layer_stack if layer.attrib.get("name", "").startswith("Pose ")]
        visible_layers = [layer for layer in layer_stack if layer.attrib.get("visibility") == "visible"]
        if len(pose_layers) != 4 or len(visible_layers) != 1 or visible_layers[0] not in pose_layers:
            raise ValueError("La pila debe tener cuatro poses y exactamente una pose visible")
        for layer in [*layer_stack, ElementTree.Element("layer", {"src": "mergedimage.png"})]:
            with Image.open(BytesIO(archive.read(layer.attrib["src"]))) as image:
                image.verify()
                if image.size != (width, height):
                    raise ValueError(f"Tamaño inesperado en {layer.attrib['src']}: {image.size}")
    return output_path


def create_all_projects() -> list[Path]:
    """Build matching editable sources for every available canonical pose sheet."""
    sheets = sorted(ASSET_DIR.glob("*-sheet.png"))
    if not sheets:
        raise FileNotFoundError(f"No hay hojas de poses *-sheet.png en {ASSET_DIR}")
    return [create_project(sheet) for sheet in sheets]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crea documentos OpenRaster editables por poses para Krita.")
    parser.add_argument("--input", type=Path, help="Hoja de poses; si se omite, procesa todas las disponibles.")
    parser.add_argument("--output", type=Path, help="Ruta .ora (solo junto con --input).")
    args = parser.parse_args()
    if args.output and not args.input:
        parser.error("--output requiere --input")
    outputs = [create_project(args.input, args.output)] if args.input else create_all_projects()
    print("\n".join(str(output) for output in outputs))
