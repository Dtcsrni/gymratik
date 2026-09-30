"""Build the slow 30-fps breathing loop and static cover poster from the seated mascots."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "branding" / "gymratik-cover-seated-v1-source.png"
ANIMATION = ROOT / "assets" / "branding" / "gymratik-cover-seated-breath-30fps.webp"
POSTER = ROOT / "assets" / "branding" / "gymratik-cover-seated-v1-poster.webp"
FRAME_SIZE = (352, 314)
POSTER_SIZE = (372, 332)
FRAME_COUNT = 188
FRAME_DURATION_MS = 33
ART_SCALE = 0.86
MESH_STEP = 12
SAFE_MARGIN = 14
BREATH_CENTERS = ((125.0, 113.0), (232.0, 106.0))


def prepare_canvas(source: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", FRAME_SIZE, (0, 0, 0, 0))
    target = (round(FRAME_SIZE[0] * ART_SCALE), round(FRAME_SIZE[1] * ART_SCALE))
    scale = min(target[0] / source.width, target[1] / source.height)
    art_size = (round(source.width * scale), round(source.height * scale))
    art = source.convert("RGBA").resize(art_size, Image.Resampling.LANCZOS)
    canvas.alpha_composite(art, ((FRAME_SIZE[0] - target[0]) // 2,
                                 (FRAME_SIZE[1] - target[1]) // 2))
    bounds = canvas.getchannel("A").getbbox()
    if bounds is None or min(bounds[0], bounds[1], FRAME_SIZE[0] - bounds[2], FRAME_SIZE[1] - bounds[3]) < SAFE_MARGIN:
        raise ValueError(f"Las mascotas no mantienen margen seguro en el lienzo: {bounds}")
    return canvas


def source_point(x: float, y: float, inhale: float) -> tuple[float, float]:
    """Inverse-map points so only each mascot's chest subtly expands on inhale."""
    strength = 0.038 * inhale
    dx = dy = 0.0
    for center_x, center_y in BREATH_CENTERS:
        weight = math.exp(-0.5 * (((x - center_x) / 31.0) ** 2 + ((y - center_y) / 25.0) ** 2))
        dx += (x - center_x) * strength * weight
        dy += (y - center_y) * strength * 0.5 * weight
    return x - dx, y - dy


def breathing_frame(base: Image.Image, inhale: float) -> Image.Image:
    width, height = FRAME_SIZE
    x_edges = list(range(0, width, MESH_STEP)) + [width]
    y_edges = list(range(0, height, MESH_STEP)) + [height]
    mesh = []
    for y0, y1 in zip(y_edges, y_edges[1:]):
        for x0, x1 in zip(x_edges, x_edges[1:]):
            quad = (source_point(x0, y0, inhale), source_point(x0, y1, inhale),
                    source_point(x1, y1, inhale), source_point(x1, y0, inhale))
            mesh.append(((x0, y0, x1, y1), tuple(value for point in quad for value in point)))
    return base.transform(FRAME_SIZE, Image.Transform.MESH, mesh,
                          resample=Image.Resampling.BICUBIC)


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"No existe la fuente editable de las mascotas sentadas: {SOURCE}")
    if not Image.registered_extensions().get(".webp"):
        raise SystemExit("Pillow no tiene soporte WebP disponible")

    with Image.open(SOURCE) as image:
        base = prepare_canvas(image)
    sequence = []
    for index in range(FRAME_COUNT):
        phase = index / (FRAME_COUNT - 1)
        inhale = 0.5 - 0.5 * math.cos(2 * math.pi * phase)
        sequence.append(breathing_frame(base, inhale))
    sequence[-1] = sequence[0].copy()

    ANIMATION.parent.mkdir(parents=True, exist_ok=True)
    sequence[0].save(ANIMATION, format="WEBP", save_all=True,
                     append_images=sequence[1:], duration=[FRAME_DURATION_MS] * len(sequence),
                     loop=0, quality=46, alpha_quality=82, method=6, exact=True)
    base.resize(POSTER_SIZE, Image.Resampling.LANCZOS).save(
        POSTER, format="WEBP", quality=88, method=6, exact=True)

    with Image.open(ANIMATION) as encoded:
        if encoded.n_frames < 180:
            raise RuntimeError(f"La secuencia tiene pocos cuadros: {encoded.n_frames}")
        encoded.seek(0)
        first = encoded.convert("RGBA")
        encoded.seek(encoded.n_frames // 2)
        middle = encoded.convert("RGBA")
        if ImageChops.difference(first, middle).getbbox() is None:
            raise RuntimeError("La respiración no produce cambio visual entre cuadros")
        encoded.seek(encoded.n_frames - 1)
        loop_difference = ImageChops.difference(first.convert("RGB"), encoded.convert("RGB"))
        channel_error = sum(value * count for value, count in enumerate(loop_difference.convert("L").histogram())) / (FRAME_SIZE[0] * FRAME_SIZE[1])
        if channel_error > 2.0:
            raise RuntimeError(f"El ciclo tiene un salto visible en el cierre: error medio={channel_error:.2f}")
        durations = []
        for frame_index in range(encoded.n_frames):
            encoded.seek(frame_index)
            durations.append(encoded.info.get("duration", 0))
        if not durations or any(duration != FRAME_DURATION_MS for duration in durations) or encoded.info.get("loop") != 0:
            raise RuntimeError("La animación no conserva 30 fps y repetición continua")
    if ANIMATION.stat().st_size >= 3_000_000:
        raise RuntimeError(f"La animación supera 3 MB: {ANIMATION.stat().st_size}")
    print(f"COVER_BREATHING_ANIMATION_OK frames={len(durations)} nominal_fps={round(1000 / FRAME_DURATION_MS)} cycle_ms={len(durations) * FRAME_DURATION_MS} size={FRAME_SIZE}")
    print(f"animation={ANIMATION.relative_to(ROOT).as_posix()} bytes={ANIMATION.stat().st_size}")
    print(f"poster={POSTER.relative_to(ROOT).as_posix()} bytes={POSTER.stat().st_size}")


if __name__ == "__main__":
    main()
