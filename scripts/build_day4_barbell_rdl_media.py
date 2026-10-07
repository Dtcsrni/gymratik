"""Crea una guía propia y esquemática del peso muerto rumano con barra libre."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated"
GIFS = ROOT / "data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos"
MANIFEST = ROOT / "data/rutinas_autocontenidas/evidencia/dia4_media_manifest.json"
SIZE = (540, 360)
BG = (246, 250, 251)
INK = (24, 43, 53)
TEAL = (25, 171, 164)
GOLD = (222, 165, 60)
SKIN = (151, 92, 62)
SHIRT = (18, 45, 62)
PANTS = (31, 41, 52)
BAR = (60, 73, 82)
PLATE = (27, 38, 47)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def render_phase(hinge: float, label: str) -> Image.Image:
    """Renderiza un perfil didáctico: barra pegada al muslo y tibia."""
    scale = 2
    image = Image.new("RGB", (SIZE[0] * scale, SIZE[1] * scale), BG)
    draw = ImageDraw.Draw(image)
    def xy(point: tuple[float, float]) -> tuple[int, int]:
        return round(point[0] * scale), round(point[1] * scale)
    def line(points, fill, width):
        draw.line([xy(point) for point in points], fill=fill, width=width * scale, joint="curve")
    def ellipse(box, fill, outline=None, width=1):
        draw.ellipse(tuple(round(value * scale) for value in box), fill=fill, outline=outline, width=width * scale)

    draw.rounded_rectangle((20 * scale, 16 * scale, 520 * scale, 344 * scale), radius=20 * scale,
                           fill=(250, 252, 253), outline=(211, 226, 231), width=2 * scale)
    draw.text((38 * scale, 28 * scale), "PESO MUERTO RUMANO · BARRA LIBRE", font=_font(15 * scale), fill=INK)
    draw.text((38 * scale, 52 * scale), label, font=_font(12 * scale), fill=TEAL)
    # Perfil esquemático sin rótulos encima del cuerpo: rodillas suaves,
    # tronco y cadera se desplazan como una unidad durante la bisagra.
    hip = (217 - 24 * hinge, 207 + 4 * hinge)
    shoulder = (205 + 47 * hinge, 145 + 5 * hinge)
    head = (shoulder[0] + 4, shoulder[1] - 23)
    knee = (217, 250)
    ankle = (204, 299)
    hand = (218 + 1 * hinge, 207 + 55 * hinge)
    bar_y = hand[1] + 1
    # Floor and bar path guide.
    line([(78, 317), (467, 317)], (183, 201, 207), 2)
    line([hip, (hip[0] + 32, hip[1] - 2)], GOLD, 3)
    draw.polygon([xy((hip[0] + 32, hip[1] - 2)), xy((hip[0] + 23, hip[1] - 8)), xy((hip[0] + 24, hip[1] + 2))], fill=GOLD)
    # Legs: hip -> knee -> ankle; arms stay long and hands travel with the bar.
    line([hip, knee, ankle], PANTS, 25)
    line([(hip[0] + 3, hip[1] + 5), (knee[0] + 3, knee[1] + 2), (ankle[0] + 3, ankle[1] - 1)], (76, 89, 99), 4)
    line([ankle, (232, 305)], PANTS, 10)
    line([shoulder, (shoulder[0] + 5, (shoulder[1] + hand[1]) / 2), hand], SKIN, 11)
    line([(shoulder[0] - 1, shoulder[1] + 2), (shoulder[0] + 4, (shoulder[1] + hand[1]) / 2), (hand[0] - 2, hand[1])], INK, 2)
    # Shirt follows the torso; it tips forward with the hip hinge, never the lower back.
    torso = [shoulder, (shoulder[0] - 14, shoulder[1] + 4), (hip[0] + 3, hip[1] - 4), hip]
    line(torso, SHIRT, 26)
    line([shoulder, hip], (90, 133, 149), 2)
    # Head faces forward in profile; eye direction stays neutral instead of looking up.
    ellipse((head[0] - 12, head[1] - 15, head[0] + 12, head[1] + 15), SKIN, INK, 2)
    ellipse((head[0] + 5, head[1] - 2, head[0] + 8, head[1] + 1), INK)
    # Bar stays in front of the legs; the near hand visibly closes around it.
    line([(151, bar_y), (307, bar_y)], BAR, 8)
    for x in (151, 307):
        ellipse((x - 15, bar_y - 24, x + 15, bar_y + 24), PLATE, TEAL, 2)
    ellipse((hand[0] - 5, hand[1] - 5, hand[0] + 5, hand[1] + 5), SKIN, INK, 1)
    return image.resize(SIZE, Image.Resampling.LANCZOS)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict[str, object]:
    MEDIA.mkdir(parents=True, exist_ok=True)
    GIFS.mkdir(parents=True, exist_ok=True)
    start = MEDIA / "barbell-rdl-v1-start.jpg"
    final = MEDIA / "barbell-rdl-v1-final.jpg"
    reference = MEDIA / "barbell-rdl-v1-machine-reference.png"
    motion = GIFS / "barbell-rdl-v1.gif"
    render_phase(0, "INICIO · DE PIE · BARRA FRENTE A LOS MUSLOS").save(start, format="JPEG", quality=92, optimize=True)
    render_phase(1, "BISAGRA · RODILLAS SUAVES · ESPALDA NEUTRA").save(final, format="JPEG", quality=92, optimize=True)
    plate = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(plate)
    draw.rounded_rectangle((20, 16, 520, 344), radius=20, fill=(250, 252, 253), outline=(211, 226, 231), width=2)
    draw.text((38, 34), "IMPLEMENTO · BARRA LIBRE", font=_font(22), fill=INK)
    draw.text((38, 70), "Sin rieles ni máquina Smith", font=_font(16), fill=TEAL)
    draw.line((170, 203, 370, 203), fill=BAR, width=12)
    for x in (170, 370):
        draw.rounded_rectangle((x - 13, 157, x + 13, 249), radius=7, fill=PLATE, outline=TEAL, width=3)
    draw.rounded_rectangle((93, 278, 447, 318), radius=12, fill=(230, 244, 246), outline=(181, 219, 224), width=2)
    draw.text((119, 290), "BARRA + DISCOS · CARGA TOTAL", font=_font(15), fill=INK)
    plate.save(reference, format="PNG", optimize=True)
    # A 30 fps loop with meaningful lowering and return; the endpoints are steady.
    frames = []
    frame_count = 72
    for frame in range(frame_count):
        phase = frame / frame_count
        down_up = (1 - math.cos(phase * math.tau)) / 2
        frames.append(render_phase(down_up, "BAJA CONTROLADO · SUBE SIN TIRAR DE LA ESPALDA"))
    frames[0].save(motion, format="GIF", save_all=True, append_images=frames[1:], duration=33,
                   loop=0, optimize=True, disposal=2)
    return {
        "repo_id": "barbell-rdl-v1", "title_es": "Peso muerto rumano con barra",
        "target": "glúteos e isquiosurales", "body_part": "upper legs",
        "secondary": ["cadena posterior", "bisagra de cadera"],
        "source_repo": "Gymratik · guía esquemática propia", "source_commit": "",
        "published": {
            "gif": str(motion.relative_to(ROOT)).replace("\\", "/"),
            "thumbnail": str(reference.relative_to(ROOT)).replace("\\", "/"),
            "start": str(start.relative_to(ROOT)).replace("\\", "/"),
            "final": str(final.relative_to(ROOT)).replace("\\", "/"),
            "machine_reference": str(reference.relative_to(ROOT)).replace("\\", "/"),
        },
        "sha256": {"source_gif": sha256(motion), "published_gif": sha256(motion),
                   "thumbnail": sha256(reference), "start": sha256(start), "final": sha256(final),
                   "machine_reference": sha256(reference)},
        "gif": {"width": SIZE[0], "height": SIZE[1], "frames": frame_count, "frame_duration_ms": 33},
        "visual_review": "SCHEMATIC_RENDERED_AND_FRAME_CHECK_REQUIRED",
        "rights_status": "ORIGINAL_LOCAL_ASSET", "equipment_identity_status": "FREE_BAR_AND_PLATES",
    }


def main() -> None:
    entry = build()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["entries"] = [
        row for row in manifest["entries"]
        if row.get("repo_id") not in {"0578-GUT8I22", "barbell-rdl-v1"}
    ]
    manifest["entries"].append(entry)
    manifest["equipment_note"] = "El peso muerto rumano usa barra libre y discos; no requiere la Smith ni una máquina de bisagra."
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"BARBELL_RDL_MEDIA_OK frames={entry['gif']['frames']} output={entry['published']['gif']}")


if __name__ == "__main__":
    main()
