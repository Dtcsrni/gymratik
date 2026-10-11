#!/usr/bin/env python3
"""Compila hojas 2×2 de poses Gymratik en GIFs de ejercicio en bucle."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_mascot_motion_gifs as motion_tools  # noqa: E402


ASSET_DIR = ROOT / "data" / "rutinas_autocontenidas" / "medios_publicados" / "rutinas_autocontenidas" / "mascot_exercise_motion"
OUTPUT_SIZE = 256
FPS = 25
FRAME_MS = 1000 // FPS
INTERPOLATION_STEPS = 16
GRID_COLUMNS = 2
GRID_ROWS = 2
SHEET_PATTERN = re.compile(r"^day(?P<day>[1-4])-exercise(?P<exercise>\d{2})-(?P<slug>[a-z0-9-]+)-sheet\.png$")


def crop_keyframes(sheet_path: Path) -> list[Image.Image]:
    sheet = Image.open(sheet_path).convert("RGBA")
    width, height = sheet.size
    if width % GRID_COLUMNS or height % GRID_ROWS:
        raise ValueError(f"La hoja debe dividirse exactamente en una cuadrícula 2×2: {sheet_path} ({width}×{height})")
    cell_width, cell_height = width // GRID_COLUMNS, height // GRID_ROWS
    if cell_width != cell_height:
        raise ValueError(f"Los cuadros deben ser cuadrados: {sheet_path} ({cell_width}×{cell_height})")

    frames = []
    margin = max(2, round(min(cell_width, cell_height) * 0.003))
    for row in range(GRID_ROWS):
        for column in range(GRID_COLUMNS):
            left = column * cell_width + margin
            top = row * cell_height + margin
            right = (column + 1) * cell_width - margin
            bottom = (row + 1) * cell_height - margin
            frame = sheet.crop((left, top, right, bottom))
            frame = frame.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)
            frames.append(frame)
    return frames


def build_sheet(sheet_path: Path) -> dict[str, object]:
    match = SHEET_PATTERN.fullmatch(sheet_path.name)
    if not match:
        raise ValueError(f"Nombre no normalizado; esperado dayN-exerciseNN-slug-sheet.png: {sheet_path.name}")

    keyframes = crop_keyframes(sheet_path)
    motion_tools.OUTPUT_SIZE = OUTPUT_SIZE
    motion_tools.INTERPOLATION_STEPS = INTERPOLATION_STEPS
    animation = motion_tools.quantize_frames(motion_tools.smooth_loop(keyframes))
    asset_stem = sheet_path.name.removesuffix("-sheet.png") + f"-{FPS}fps"
    gif_path = sheet_path.with_name(asset_stem + ".gif")
    poster_path = sheet_path.with_name(asset_stem + "-poster.webp")
    final_poster_path = sheet_path.with_name(asset_stem + "-final-poster.webp")
    animation[0].save(
        gif_path,
        format="GIF",
        save_all=True,
        append_images=animation[1:],
        duration=FRAME_MS,
        loop=0,
        transparency=255,
        disposal=2,
        optimize=True,
    )
    keyframes[0].save(poster_path, format="WEBP", quality=90, method=6)
    keyframes[-1].save(final_poster_path, format="WEBP", quality=90, method=6)

    with Image.open(gif_path) as rendered:
        frame_count = getattr(rendered, "n_frames", 1)
        dimensions = rendered.size
        rendered.verify()
    if dimensions != (OUTPUT_SIZE, OUTPUT_SIZE) or frame_count < 72:
        raise ValueError(f"GIF inválido/inmóvil: {gif_path} size={dimensions} frames={frame_count}")

    record = {
        "exerciseId": f"day{match['day']}-exercise{match['exercise']}",
        "sourceSheet": sheet_path.relative_to(ROOT).as_posix(),
        "gif": gif_path.relative_to(ROOT).as_posix(),
        "poster": poster_path.relative_to(ROOT).as_posix(),
        "finalPoster": final_poster_path.relative_to(ROOT).as_posix(),
        "keyframes": len(keyframes),
        "frames": frame_count,
        "width": dimensions[0],
        "height": dimensions[1],
        "frameDurationMs": FRAME_MS,
        "fps": FPS,
        "cycleDurationMs": frame_count * FRAME_MS,
        "gifBytes": gif_path.stat().st_size,
        "sha256": hashlib.sha256(gif_path.read_bytes()).hexdigest(),
    }
    return record


def main() -> None:
    sheets = sorted(ASSET_DIR.glob("day*-exercise*-*-sheet.png"))
    if not sheets:
        raise SystemExit(f"No hay hojas 2×2 en {ASSET_DIR}")
    records = [build_sheet(sheet) for sheet in sheets]
    manifest = {
        "schemaVersion": 1,
        "description": "Animaciones de técnica Gymratik a 25 fps, generadas desde cuatro poses anatómicas mediante interpolación de flujo óptico.",
        "frameSize": OUTPUT_SIZE,
        "fps": FPS,
        "frameDurationMs": FRAME_MS,
        "records": records,
    }
    (ASSET_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MASCOT_EXERCISE_MOTION_OK exercises={len(records)} frames={sum(int(item['frames']) for item in records)}")


if __name__ == "__main__":
    main()
