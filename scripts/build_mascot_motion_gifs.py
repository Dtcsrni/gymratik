#!/usr/bin/env python3
"""Compila las hojas de cuadros Gymratik en GIFs pequeños y accesibles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "data" / "profile" / "mascot-motion"
SOURCE_DIR = ASSET_DIR / "sources"
OUTPUT_SIZE = 128
FPS = 25
FRAME_MS = 40
GRID_COLUMNS = 4
GRID_ROWS = 3
INTERPOLATION_STEPS = 3
VARIANTS = ("female", "male", "neutral")
STATES = ("exercise", "rest")


def crop_frames(sheet_path: Path) -> list[Image.Image]:
    sheet = Image.open(sheet_path).convert("RGBA")
    width, height = sheet.size
    if width % GRID_COLUMNS or height % GRID_ROWS:
        raise ValueError(f"La hoja no tiene una cuadrícula 4×3 exacta: {sheet_path}")
    cell_width, cell_height = width // GRID_COLUMNS, height // GRID_ROWS
    if cell_width != cell_height:
        raise ValueError(f"Los cuadros no son cuadrados: {sheet_path} ({cell_width}×{cell_height})")
    frames = []
    for row in range(GRID_ROWS):
        for column in range(GRID_COLUMNS):
            frame = sheet.crop((column * cell_width, row * cell_height, (column + 1) * cell_width, (row + 1) * cell_height))
            alpha = frame.getchannel("A")
            bounds = alpha.point(lambda value: 255 if value > 8 else 0).getbbox()
            if not bounds:
                raise ValueError(f"Cuadro transparente/vacío: {sheet_path}, fila {row + 1}, columna {column + 1}")
            # Mantiene el marco cuadrado común y recentra por celda para evitar saltos.
            frame = frame.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.Resampling.LANCZOS)
            frames.append(frame)
    return frames


def _flow_intermediates(first: Image.Image, second: Image.Image) -> list[Image.Image]:
    a = np.asarray(first.convert("RGBA"), dtype=np.float32) / 255.0
    b = np.asarray(second.convert("RGBA"), dtype=np.float32) / 255.0
    background = np.array([12.0, 34.0, 49.0], dtype=np.float32)

    def visible_rgb(rgba: np.ndarray) -> np.ndarray:
        alpha = rgba[:, :, 3:4]
        return rgba[:, :, :3] * alpha + background * (1.0 - alpha)

    gray_a = cv2.cvtColor(visible_rgb(a).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    gray_b = cv2.cvtColor(visible_rgb(b).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    flow_ab = cv2.calcOpticalFlowFarneback(gray_a, gray_b, None, 0.5, 3, 17, 3, 5, 1.1, 0)
    flow_ba = cv2.calcOpticalFlowFarneback(gray_b, gray_a, None, 0.5, 3, 17, 3, 5, 1.1, 0)
    height, width = gray_a.shape
    grid_x, grid_y = np.meshgrid(np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32))
    intermediates = []
    for step in range(1, INTERPOLATION_STEPS):
        amount = step / INTERPOLATION_STEPS
        map_a = np.stack((grid_x - flow_ab[:, :, 0] * amount, grid_y - flow_ab[:, :, 1] * amount), axis=-1)
        map_b = np.stack((grid_x - flow_ba[:, :, 0] * (1 - amount), grid_y - flow_ba[:, :, 1] * (1 - amount)), axis=-1)
        warped_a = cv2.remap(a, map_a, None, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        warped_b = cv2.remap(b, map_b, None, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        alpha_a, alpha_b = warped_a[:, :, 3:4], warped_b[:, :, 3:4]
        alpha = alpha_a * (1 - amount) + alpha_b * amount
        premultiplied = warped_a[:, :, :3] * alpha_a * (1 - amount) + warped_b[:, :, :3] * alpha_b * amount
        rgb = np.divide(premultiplied, alpha, out=np.zeros_like(premultiplied), where=alpha > 1e-4)
        rgba = np.concatenate((rgb, alpha), axis=2)
        intermediates.append(Image.fromarray(np.uint8(np.clip(rgba * 255.0, 0, 255)), "RGBA"))
    return intermediates


def smooth_loop(keyframes: list[Image.Image]) -> list[Image.Image]:
    # La hoja contiene una vuelta; invertirla antes de cerrar evita el salto final.
    cycle = keyframes + keyframes[-2:0:-1]
    result: list[Image.Image] = []
    for index, frame in enumerate(cycle):
        next_frame = cycle[(index + 1) % len(cycle)]
        result.append(frame)
        result.extend(_flow_intermediates(frame, next_frame))
    return result


def quantize_frames(
    frames: list[Image.Image], dither: Image.Dither = Image.Dither.FLOYDSTEINBERG
) -> list[Image.Image]:
    palette_sample = Image.new("RGB", (OUTPUT_SIZE, OUTPUT_SIZE * len(frames)), (12, 34, 49))
    for index, frame in enumerate(frames):
        background = Image.new("RGBA", frame.size, (12, 34, 49, 255))
        background.alpha_composite(frame)
        palette_sample.paste(background.convert("RGB"), (0, index * OUTPUT_SIZE))
    palette = palette_sample.quantize(colors=255, method=Image.Quantize.FASTOCTREE)
    palette_data = palette.getpalette()[: 255 * 3] + [0, 0, 0]
    palette.putpalette(palette_data)

    result = []
    for frame in frames:
        indexed = frame.convert("RGB").quantize(palette=palette, dither=dither)
        transparent = frame.getchannel("A").point(lambda value: 255 if value < 128 else 0)
        indexed.paste(255, mask=transparent)
        indexed.putpalette(palette_data)
        indexed.info["transparency"] = 255
        result.append(indexed)
    return result


def build_one(variant: str, state: str) -> dict[str, object]:
    source_path = SOURCE_DIR / f"{variant}-{state}.webp"
    if not source_path.is_file():
        raise FileNotFoundError(f"Falta la hoja de cuadros: {source_path}")
    keyframes = crop_frames(source_path)
    animated = quantize_frames(smooth_loop(keyframes))
    gif_path = ASSET_DIR / f"{variant}-{state}-25fps.gif"
    animated[0].save(
        gif_path,
        format="GIF",
        save_all=True,
        append_images=animated[1:],
        duration=FRAME_MS,
        loop=0,
        transparency=255,
        disposal=2,
        optimize=False,
    )
    still_path = ASSET_DIR / f"{variant}-{state}-still.webp"
    keyframes[0].save(still_path, format="WEBP", quality=88, method=6)
    return {
        "variant": variant,
        "state": state,
        "gif": gif_path.relative_to(ROOT).as_posix(),
        "still": still_path.relative_to(ROOT).as_posix(),
        "width": OUTPUT_SIZE,
        "height": OUTPUT_SIZE,
        "fps": FPS,
        "frames": len(animated),
        "frameDurationMs": FRAME_MS,
        "gifBytes": gif_path.stat().st_size,
        "sha256": hashlib.sha256(gif_path.read_bytes()).hexdigest(),
        "source": source_path.relative_to(ROOT).as_posix(),
    }


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    records = [build_one(variant, state) for variant in VARIANTS for state in STATES]
    manifest = {
        "schemaVersion": 1,
        "description": "Mascotas Gymratik locales: ciclo GIF solo durante ejercicio/descanso; WebP estático con movimiento reducido.",
        "defaultVariant": "neutral",
        "minimumFps": FPS,
        "records": records,
    }
    manifest_path = ASSET_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total_bytes = sum(int(record["gifBytes"]) for record in records)
    print(f"MASCOT_MOTION_OK variants={len(VARIANTS)} states={len(STATES)} fps={FPS} gifs={len(records)} total_bytes={total_bytes}")


if __name__ == "__main__":
    main()
