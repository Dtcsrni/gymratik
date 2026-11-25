"""Publica y deriva los medios locales usados por la rutina canónica del Día 4.

Las fuentes se mantienen en ``artifacts`` y los binarios consumibles por la PWA
se copian a ``data/.../medios_publicados``. El script no afirma licencia ni
confirma que el equipo visual coincida con el inventario físico del gimnasio.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts" / "ejercicios-compartido"
PUBLISHED = ROOT / "data" / "rutinas_autocontenidas" / "medios_publicados"
VIDEO_OUT = PUBLISHED / "ejercicios-compartido" / "videos"
IMAGE_OUT = PUBLISHED / "ejercicios-compartido" / "images"
DERIVED_OUT = PUBLISHED / "rutinas_autocontenidas" / "dia4_media_generated"
MANIFEST_OUT = ROOT / "data" / "rutinas_autocontenidas" / "evidencia" / "dia4_media_manifest.json"
SOURCE_COMMIT = "7455efae41b330c265e7cd4b78dfa848e7ce5ebd"

EXERCISES = (
    ("1425-WWD6FzI", "Prensa unilateral alterna", "cuádriceps", "upper legs", ("isquiosurales", "glúteos")),
    ("0578-GUT8I22", "Peso muerto en máquina", "glúteos", "upper legs", ("isquiosurales", "cuádriceps")),
    ("0586-17lJ1kr", "Curl femoral tumbado", "isquiosurales", "upper legs", ("pantorrillas",)),
    ("0597-CHpahtl", "Abducción de cadera sentada", "abductores", "upper legs", ("glúteos", "isquiosurales")),
    ("0598-oHsrypV", "Aducción de cadera sentada", "aductores", "upper legs", ("isquiosurales", "glúteos")),
    ("0594-bOOdeyc", "Elevación de pantorrilla sentada", "pantorrillas", "lower legs", ("sóleo", "estabilizadores del tobillo")),
    ("0600-PQ2AtC3", "Crunch con elevación de piernas sentada", "abdominales", "waist", ("flexores de cadera",)),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_frame(source: Path, destination: Path, frame_index: int) -> dict[str, object]:
    with Image.open(source) as image:
        image.seek(frame_index)
        frame = image.convert("RGB")
        frame.save(destination, format="JPEG", quality=92, optimize=True)
        return {"width": frame.width, "height": frame.height, "frame": frame_index}


def publish_one(repo: str, title: str, primary: str, body_part: str, secondary: tuple[str, ...]) -> dict[str, object]:
    source_gif = SOURCE / "videos" / f"{repo}.gif"
    source_image = SOURCE / "images" / f"{repo}.jpg"
    if not source_gif.is_file() or not source_image.is_file():
        raise FileNotFoundError(f"Falta la pareja GIF/imagen de {repo}")

    VIDEO_OUT.mkdir(parents=True, exist_ok=True)
    IMAGE_OUT.mkdir(parents=True, exist_ok=True)
    DERIVED_OUT.mkdir(parents=True, exist_ok=True)
    published_gif = VIDEO_OUT / source_gif.name
    published_reference = IMAGE_OUT / source_image.name
    shutil.copy2(source_gif, published_gif)
    shutil.copy2(source_image, published_reference)

    with Image.open(source_gif) as gif:
        frames = int(getattr(gif, "n_frames", 1))
        duration = int(gif.info.get("duration", 0) or 0)
    start = DERIVED_OUT / f"{repo}-start.jpg"
    final = DERIVED_OUT / f"{repo}-final.jpg"
    reference = DERIVED_OUT / f"{repo}-machine-reference.png"
    dimensions = save_frame(source_gif, start, 0)
    save_frame(source_gif, final, max(frames - 1, 0))
    with Image.open(source_image) as image:
        image.convert("RGBA").save(reference, format="PNG", optimize=True)

    return {
        "repo_id": repo,
        "title_es": title,
        "target": primary,
        "body_part": body_part,
        "secondary": list(secondary),
        "source_repo": "ejercicios-compartido",
        "source_commit": SOURCE_COMMIT,
        "published": {
            "gif": str(published_gif.relative_to(ROOT)).replace("\\", "/"),
            "thumbnail": str(published_reference.relative_to(ROOT)).replace("\\", "/"),
            "start": str(start.relative_to(ROOT)).replace("\\", "/"),
            "final": str(final.relative_to(ROOT)).replace("\\", "/"),
            "machine_reference": str(reference.relative_to(ROOT)).replace("\\", "/"),
        },
        "sha256": {
            "source_gif": sha256(source_gif),
            "published_gif": sha256(published_gif),
            "thumbnail": sha256(published_reference),
            "start": sha256(start),
            "final": sha256(final),
            "machine_reference": sha256(reference),
        },
        "gif": {"width": dimensions["width"], "height": dimensions["height"], "frames": frames, "frame_duration_ms": duration},
        "visual_review": "LOOP_AND_FRAME_REVIEWED_LOCAL",
        "rights_status": "CANDIDATES_PENDING_LICENSE_REVIEW",
        "equipment_identity_status": "VISUAL_PATTERN_REFERENCE_ONLY",
    }


def main() -> None:
    entries = [publish_one(*item) for item in EXERCISES]
    manifest = json.loads(MANIFEST_OUT.read_text(encoding="utf-8")) if MANIFEST_OUT.is_file() else {}
    replaced_ids = {item[0] for item in EXERCISES}
    preserved = []
    seen_ids = set(replaced_ids)
    for item in manifest.get("entries", []):
        repo_id = item.get("repo_id")
        if repo_id and repo_id not in seen_ids:
            preserved.append(item)
            seen_ids.add(repo_id)
    manifest.update({
        "schema": "routine-media-manifest-v1",
        "routine": "Día 4 · Pierna · equilibrio",
        "global_status": "CANDIDATES_PENDING_LICENSE_REVIEW",
        "rights_note": "Los medios son candidatos locales; conservar revisión de licencia, atribución y redistribución pendiente.",
        "entries": entries + preserved,
    })
    manifest.setdefault("equipment_note", "La imagen no confirma la identidad ni disponibilidad de una máquina instalada.")
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"PREPARED_DAY4_MEDIA entries={len(entries)} manifest={MANIFEST_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
