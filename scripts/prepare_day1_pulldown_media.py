"""Extrae dos posiciones estáticas limpias del jalón al pecho del Día 1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0197-qdRxqCj.gif"
OUTPUT = ROOT / "data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated"
MANIFEST = ROOT / "data/rutinas_autocontenidas/evidencia/dia1_media_manifest.json"
EXERCISE_ID = "0197-qdRxqCj"
FRAME_INDEXES = {"start": 0, "final": 6}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if not MEDIA.is_file():
        raise FileNotFoundError(f"Falta el medio local canónico: {MEDIA}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with Image.open(MEDIA) as sequence:
        if int(getattr(sequence, "n_frames", 1)) <= FRAME_INDEXES["final"]:
            raise ValueError(f"La secuencia {EXERCISE_ID} no tiene ambos cuadros de referencia")
        generated: dict[str, str] = {}
        for phase, frame_index in FRAME_INDEXES.items():
            path = OUTPUT / f"{EXERCISE_ID}-{phase}.jpg"
            sequence.seek(frame_index)
            frame = sequence.convert("RGB")
            frame.save(path, format="JPEG", quality=92, optimize=True)
            generated[phase] = str(path.relative_to(ROOT)).replace("\\", "/")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    item = next(entry for entry in manifest["items"] if entry["exercise_number"] == 1)
    item["derived_media"] = {
        "start": generated["start"],
        "final": generated["final"],
        "source_frames": FRAME_INDEXES,
        "sha256_start": sha256(ROOT / generated["start"]),
        "sha256_final": sha256(ROOT / generated["final"]),
        "selection_note": "Cuadros terminales limpios; se excluyen transiciones con sobreimpresión del GIF fuente.",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PREPARED_DAY1_PULLDOWN_MEDIA frames={FRAME_INDEXES} output={OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
