"""Optimiza los PNG fuente de portada en WebP transparentes para las rutinas."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
COVER_DIR = ROOT / "assets" / "branding" / "routine-covers"
MAX_BYTES = 450_000


def build() -> list[Path]:
    outputs = []
    for day in range(1, 5):
        source = COVER_DIR / f"day{day}-source.png"
        output = COVER_DIR / f"day{day}.webp"
        if not source.is_file():
            raise FileNotFoundError(f"Falta PNG editable de portada: {source}")
        with Image.open(source) as image:
            if image.size != (1536, 1024) or image.mode != "RGBA":
                raise ValueError(f"Formato esperado 1536x1024 RGBA, recibido {image.size} {image.mode}: {source}")
            alpha = image.getchannel("A")
            if alpha.getextrema() == (255, 255):
                raise ValueError(f"La portada debe conservar transparencia real: {source}")
            image.save(output, "WEBP", quality=84, method=6, exact=True)
        if output.stat().st_size > MAX_BYTES:
            raise ValueError(f"Portada supera el presupuesto de {MAX_BYTES} bytes: {output.stat().st_size}")
        with Image.open(output) as optimized:
            if optimized.size != (1536, 1024) or optimized.mode != "RGBA":
                raise ValueError(f"La salida perdió dimensiones o alfa: {output}")
        outputs.append(output)
    return outputs


if __name__ == "__main__":
    for asset in build():
        print(f"BUILT {asset.relative_to(ROOT)} bytes={asset.stat().st_size}")
