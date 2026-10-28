from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIR = ROOT / "data" / "rutinas_autocontenidas" / "canonicas"
LOCAL_REFERENCE = re.compile(r"(?:\.\./|\.\\|/|[A-Za-z]:[\\/])")
MEDIA_SUFFIXES = {".gif", ".jpg", ".jpeg", ".png", ".webp"}
SCRIPT_MEDIA = re.compile(
    r"(?:src|staticSrc|static-src|fallback|gif|thumbnail|path|portrait)\s*:\s*[\"']([^\"']+\.(?:gif|jpg|jpeg|png|webp)(?:\?[^\"']*)?)[\"']",
    flags=re.I,
)
DAY1_MEDIA_KEYS = (
    "JALÓN AL PECHO",
    "REMO ALTO UNILATERAL",
    "REMO HORIZONTAL EN MÁQUINA",
    "APERTURA INVERSA EN MÁQUINA",
    "CURL DE BÍCEPS EN MÁQUINA",
    "CURL DE BÍCEPS SENTADO EN MÁQUINA",
)
DAY2_MEDIA_KEYS = (
    "HIP THRUST",
    "HACK SQUAT",
    "PRENSA DE PIERNAS",
    "CURL FEMORAL EN MÁQUINA",
    "EXTENSIÓN DE PIERNAS",
    "PANTORRILLAS DE PIE",
)
EXPECTED_STATIC_GIFS = {
    "Rutina_Dia_1_Espalda_Biceps_V1.html": 1,
    "Rutina_Dia_2_Pierna_Gluteo_V1.html": 1,
    "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html": 7,
    "Rutina_Dia_4_Pierna_Equilibrio_V1.html": 7,
}
EXPECTED_DYNAMIC_GIFS = {
    "Rutina_Dia_1_Espalda_Biceps_V1.html": 6,
    "Rutina_Dia_2_Pierna_Gluteo_V1.html": 6,
    "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html": 0,
    "Rutina_Dia_4_Pierna_Equilibrio_V1.html": 0,
}
DAY1_MEDIA_ENTRY = re.compile(
    r"gif\s*:\s*[\"']([^\"']+)[\"']\s*,\s*"
    r"thumbnail\s*:\s*[\"']([^\"']+)[\"']\s*,\s*"
    r"key\s*:\s*[\"']([^\"']+)[\"']",
    flags=re.I | re.S,
)


@dataclass
class ImageReference:
    path: str
    alt: str
    aria_hidden: str
    line: int


class MediaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.images: list[ImageReference] = []
        self.attribute_references: list[str] = []
        self.depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.depth += 1
        if tag.lower() != "img":
            return
        attr_map = dict(attrs)
        for name, value in attrs:
            if name.casefold() in {"src", "data-static-src", "data-fallback", "poster"} and value:
                self.attribute_references.append(value)
        src = attr_map.get("src") or ""
        if not src:
            return
        self.images.append(
            ImageReference(
                path=src,
                alt=attr_map.get("alt") or "",
                aria_hidden=attr_map.get("aria-hidden") or "",
                line=self.getpos()[0],
            )
        )

    def handle_endtag(self, tag: str) -> None:
        self.depth = max(0, self.depth - 1)


def local_references(text: str, parser: MediaParser) -> list[str]:
    references = [image.path for image in parser.images]
    references.extend(parser.attribute_references)
    references.extend(
        match.group(1)
        for match in SCRIPT_MEDIA.finditer(text)
        if LOCAL_REFERENCE.search(match.group(1))
    )
    return sorted(set(references))


def resolve_local(path: Path, reference: str) -> tuple[Path | None, str | None]:
    if reference.startswith(("data:", "http://", "https://", "//")):
        return None, None
    try:
        resolved = (path.parent / reference).resolve()
        relative = resolved.relative_to(ROOT)
    except (OSError, ValueError) as exc:
        return None, f"ruta fuera del repositorio o inválida {reference!r}: {exc}"
    if relative.parts and relative.parts[0] == "artifacts":
        return None, f"ruta no publicable bajo artifacts {reference!r}"
    return resolved, None


def validate_path(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"{path}: no se pudo leer: {exc}"]

    parser = MediaParser()
    parser.feed(text)
    errors: list[str] = []

    for reference in local_references(text, parser):
        resolved, error = resolve_local(path, reference)
        if error:
            errors.append(f"{path}: {error}")
            continue
        if resolved is None:
            continue
        if not resolved.exists():
            errors.append(f"{path}: medio faltante {reference!r}")
            continue
        if resolved.suffix.casefold() not in MEDIA_SUFFIXES:
            errors.append(f"{path}: extensión de medio no reconocida {reference!r}")

    for image in parser.images:
        if image.alt.strip() == "" and image.aria_hidden.casefold() != "true":
            errors.append(
                f"{path}:{image.line}: imagen de contenido sin alt ni aria-hidden: {image.path!r}"
            )

    if path.name in EXPECTED_STATIC_GIFS:
        static_gifs = re.findall(
            r'<img\b(?=[^>]*\bclass=["\'][^"\']*\broutineExerciseGif\b)[^>]*>',
            text,
            flags=re.I | re.S,
        )
        expected_static = EXPECTED_STATIC_GIFS[path.name]
        if len(static_gifs) != expected_static:
            errors.append(
                f"{path}: GIF estáticos esperados={expected_static}; observados={len(static_gifs)}"
            )

        day = 1 if "Dia_1_" in path.name else 2 if "Dia_2_" in path.name else 0
        expected_dynamic = EXPECTED_DYNAMIC_GIFS[path.name]
        if day:
            fix_name = "day1-gif-candidates" if day == 1 else "day2-exercise-gifs"
            script = re.search(
                rf'<script\b(?=[^>]*\bdata-fix=["\']{fix_name}["\'])[^>]*>(.*?)</script>',
                text,
                flags=re.I | re.S,
            )
            script_text = script.group(1) if script else ""
            entries = DAY1_MEDIA_ENTRY.findall(script_text)
            expected_keys = DAY1_MEDIA_KEYS if day == 1 else DAY2_MEDIA_KEYS
            observed_keys = tuple(entry[2] for entry in entries)
            if observed_keys != expected_keys:
                errors.append(
                    f"{path}: mapa de GIFs esperado={expected_keys}; observado={observed_keys}"
                )
            injector_count = script_text.count('make("img","gifMotion routineExerciseGif")')
            if injector_count != 1:
                errors.append(
                    f"{path}: inyector debe usar una vez la clase compartida routineExerciseGif; observado={injector_count}"
                )
            if len(entries) != expected_dynamic:
                errors.append(
                    f"{path}: GIF dinámicos esperados={expected_dynamic}; observados={len(entries)}"
                )

        total_gifs = len(static_gifs) + expected_dynamic
        if total_gifs != 7:
            errors.append(f"{path}: cada rutina debe cubrir 7 GIFs reales; observados={total_gifs}")

        cards = re.findall(r'<article\b[^>]*>.*?</article>', text, flags=re.I | re.S)
        svg_motion = re.compile(r'<(?:animate|animateTransform|animateMotion|set)\b', re.I)
        for index, card in enumerate(cards, start=1):
            if svg_motion.search(card):
                errors.append(f"{path}: ejercicio {index} contiene animación SVG; el movimiento requiere un GIF real")

    return errors


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argument_parser = argparse.ArgumentParser(
        description="Valida referencias técnicas de medios en rutinas canónicas."
    )
    argument_parser.add_argument(
        "paths", nargs="*", type=Path, help="HTML canónicas; por defecto se validan todas"
    )
    args = argument_parser.parse_args(argv)
    paths = args.paths or sorted(CANONICAL_DIR.glob("*.html"))
    errors = [error for path in paths for error in validate_path(path)]
    if errors:
        print("ROUTINE_MEDIA_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"ROUTINE_MEDIA_OK routines={len(paths)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
