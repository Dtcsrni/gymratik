#!/usr/bin/env python3
"""Derive the held end-position still from the licensed reverse-fly GIF."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0602-myfUsKf.gif"
OUTPUT = ROOT / "data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0602-myfUsKf-final.png"
FINAL_HOLD_FRAME = 6
EXPECTED_SIZE = (180, 180)


def build_final_pose(source: Path = SOURCE, output: Path = OUTPUT) -> Path:
    """Export the GIF's one-second stable open-arm pose without rescaling."""
    with Image.open(source) as animation:
        if animation.size != EXPECTED_SIZE or animation.n_frames <= FINAL_HOLD_FRAME:
            raise ValueError(f"La fuente debe tener al menos {FINAL_HOLD_FRAME + 1} cuadros de 180×180: {source}")
        animation.seek(FINAL_HOLD_FRAME)
        if animation.info.get("duration", 0) < 500:
            raise ValueError("El cuadro seleccionado no es una pose final estable")
        frame = animation.convert("RGB")
        output.parent.mkdir(parents=True, exist_ok=True)
        frame.save(output, format="PNG", optimize=True)
    return output


if __name__ == "__main__":
    print(f"REVERSE_FLY_FINAL_STILL_OK {build_final_pose()}")
