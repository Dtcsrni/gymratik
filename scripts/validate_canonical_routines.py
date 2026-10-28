from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIR = ROOT / "data" / "rutinas_autocontenidas" / "canonicas"

EXPECTED_CONTRACTS: dict[str, tuple[int, int, tuple[int, ...]]] = {
    "Rutina_Dia_1_Espalda_Biceps_V1.html": (7, 23, (4, 4, 3, 3, 3, 3, 3)),
    "Rutina_Dia_2_Pierna_Gluteo_V1.html": (7, 23, (3, 3, 3, 4, 4, 3, 3)),
    "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html": (7, 22, (4, 3, 3, 3, 3, 3, 3)),
    "Rutina_Dia_4_Pierna_Equilibrio_V1.html": (7, 22, (3, 3, 4, 3, 3, 3, 3)),
}


def classes(attrs: list[tuple[str, str | None]]) -> set[str]:
    value = dict(attrs).get("class") or ""
    return set(value.split())


def text_content(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def comparable_title(value: str) -> str:
    value = re.sub(r"^\s*\d+\s*[·.-]\s*", "", value)
    return " ".join(value.casefold().split())


@dataclass
class Tracker:
    index: int
    series_keys: list[str]
    next_cues: list[tuple[int, str]] = field(default_factory=list)


class RoutineParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.trackers: list[Tracker] = []
        self.exercise_titles: list[str] = []
        self._current_tracker: Tracker | None = None
        self._tracker_depth: int | None = None
        self._capture: tuple[str, int, list[str]] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.depth += 1
        attr_map = dict(attrs)
        class_set = classes(attrs)

        if "exerciseTracker" in class_set and attr_map.get("data-exercise"):
            try:
                index = int(attr_map["data-exercise"] or "")
            except ValueError:
                index = -1
            keys = (attr_map.get("data-series-keys") or "").split()
            tracker = Tracker(index=index, series_keys=keys)
            self.trackers.append(tracker)
            self._current_tracker = tracker
            self._tracker_depth = self.depth

        if "nextExerciseCue" in class_set and self._current_tracker is not None:
            target = attr_map.get("data-next")
            try:
                target_index = int(target or "")
            except ValueError:
                target_index = -1
            self._capture = ("next", self.depth, [])
            self._current_tracker.next_cues.append((target_index, ""))

        if "exTitle" in class_set:
            self._capture = ("title", self.depth, [])

    def handle_endtag(self, tag: str) -> None:
        if self._capture is not None:
            kind, capture_depth, buffer = self._capture
            if self.depth == capture_depth:
                value = " ".join("".join(buffer).split())
                if kind == "title":
                    self.exercise_titles.append(value)
                elif kind == "next" and self._current_tracker is not None:
                    target, _ = self._current_tracker.next_cues[-1]
                    self._current_tracker.next_cues[-1] = (target, value)
                self._capture = None

        if self._tracker_depth == self.depth:
            self._current_tracker = None
            self._tracker_depth = None
        self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._capture[2].append(data)


@dataclass
class Inspection:
    path: Path
    trackers: list[Tracker]
    titles: list[str]
    summary: tuple[int, int] | None
    dashboard_total: int | None
    dashboard_distribution: tuple[int, ...] | None


def extract_summary(text: str) -> tuple[int, int] | None:
    match = re.search(
        r'<h2\s+id=["\']routine-summary-title["\'][^>]*>(.*?)</h2>',
        text,
        flags=re.I | re.S,
    )
    if not match:
        return None
    numbers = re.search(r"(\d+)\s+ejercicios.*?(\d+)\s+series\s+efectivas", text_content(match.group(1)), re.I)
    return (int(numbers.group(1)), int(numbers.group(2))) if numbers else None


def extract_dashboard(text: str) -> tuple[int | None, tuple[int, ...] | None]:
    value_match = re.search(
        r'<div\s+class=["\']dashValue["\'][^>]*>.*?(\d+)\s+series\s+efectivas.*?</div>',
        text,
        flags=re.I | re.S,
    )
    sub_match = re.search(
        r'<div\s+class=["\']dashSub["\'][^>]*>.*?([0-9]+(?:\s*\+\s*[0-9]+)+)\s+series.*?</div>',
        text,
        flags=re.I | re.S,
    )
    distribution = (
        tuple(int(part.strip()) for part in sub_match.group(1).split("+"))
        if sub_match
        else None
    )
    # El dashboard canónico muestra la distribución por ejercicio; su suma es
    # la fuente verificable del total y evita depender del marcado visual anidado.
    total = sum(distribution) if distribution else int(value_match.group(1)) if value_match else None
    return total, distribution


def inspect(path: Path) -> Inspection:
    text = path.read_text(encoding="utf-8")
    parser = RoutineParser()
    parser.feed(text)
    dashboard_total, dashboard_distribution = extract_dashboard(text)
    return Inspection(
        path=path,
        trackers=parser.trackers,
        titles=parser.exercise_titles,
        summary=extract_summary(text),
        dashboard_total=dashboard_total,
        dashboard_distribution=dashboard_distribution,
    )


def extract_displayed_series(path: Path) -> tuple[int, ...]:
    """Read the visible series count from every card's technique summary."""
    source = path.read_text(encoding="utf-8")
    cards = re.findall(
        r'<article\b(?=[^>]*\bclass=["\'][^"\']*\bcard\b)[^>]*>.*?</article>',
        source,
        flags=re.I | re.S,
    )
    displayed: list[int] = []
    for card in cards:
        metric = re.search(
            r'<div\s+class=["\']metric series["\'].*?'
            r'<div\s+class=["\']metricVal["\']\s*>(.*?)</div>',
            card,
            flags=re.I | re.S,
        )
        match = re.match(r"\s*(\d+)", text_content(metric.group(1)) if metric else "")
        displayed.append(int(match.group(1)) if match else -1)
    return tuple(displayed)


def validate_path(path: Path) -> list[str]:
    expected = EXPECTED_CONTRACTS.get(path.name)
    if expected is None:
        return [f"{path}: no tiene contrato canónico registrado"]

    expected_count, expected_total, expected_distribution = expected
    try:
        result = inspect(path)
    except (OSError, UnicodeError) as exc:
        return [f"{path}: no se pudo leer: {exc}"]

    errors: list[str] = []
    indexes = [tracker.index for tracker in result.trackers]
    counts = [len(tracker.series_keys) for tracker in result.trackers]

    if len(result.trackers) != expected_count:
        errors.append(
            f"{path}: ejercicio count esperado={expected_count} observado={len(result.trackers)}"
        )
    if indexes != list(range(1, len(indexes) + 1)):
        errors.append(f"{path}: índices observados={indexes}; se esperaba una secuencia contigua desde 1")
    if len(result.titles) != len(result.trackers):
        errors.append(
            f"{path}: títulos esperados={len(result.trackers)} observados={len(result.titles)}"
        )
    if tuple(counts) != expected_distribution:
        errors.append(
            f"{path}: distribución de series esperada={expected_distribution} observada={tuple(counts)}"
        )
    displayed_series = extract_displayed_series(path)
    if displayed_series != tuple(counts):
        errors.append(
            f"{path}: series visibles por ejercicio={displayed_series}; "
            f"el contador registra={tuple(counts)}"
        )
    if sum(counts) != expected_total:
        errors.append(f"{path}: suma de series esperada={expected_total} observada={sum(counts)}")

    for tracker in result.trackers:
        expected_keys = [f"e{tracker.index}s{number}" for number in range(1, len(tracker.series_keys) + 1)]
        if tracker.series_keys != expected_keys:
            errors.append(
                f"{path}: ejercicio {tracker.index} claves esperadas={expected_keys} observadas={tracker.series_keys}"
            )
        if len(set(tracker.series_keys)) != len(tracker.series_keys):
            errors.append(f"{path}: ejercicio {tracker.index} contiene claves de serie duplicadas")

        if tracker.index < expected_count:
            if len(tracker.next_cues) != 1:
                errors.append(f"{path}: ejercicio {tracker.index} debe tener un nextExerciseCue")
            for target, label in tracker.next_cues:
                if target != tracker.index + 1:
                    errors.append(
                        f"{path}: ejercicio {tracker.index} apunta a {target}; se esperaba {tracker.index + 1}"
                    )
                label_has_title = "siguiente:" in label.casefold()
                normalized_label = label.split(":", 1)[1].strip() if label_has_title else ""
                if (
                    label_has_title
                    and len(result.titles) > tracker.index
                    and comparable_title(normalized_label)
                    != comparable_title(result.titles[tracker.index])
                ):
                    errors.append(
                        f"{path}: etiqueta siguiente del ejercicio {tracker.index}={normalized_label!r}; "
                        f"se esperaba {result.titles[tracker.index]!r}"
                    )
        elif tracker.next_cues:
            errors.append(f"{path}: el último ejercicio {tracker.index} no debe tener nextExerciseCue")

    source = path.read_text(encoding="utf-8")
    cards = re.findall(r'<article\b(?=[^>]*\bclass=["\'][^"\']*\bcard\b)[^>]*>.*?</article>', source, re.I | re.S)
    for index, card in enumerate(cards, 1):
        reps_match = re.search(r'<div\s+class=["\']metric\s+reps["\'].*?<div\s+class=["\']metricVal["\']\s*>(.*?)</div>', card, re.I | re.S)
        reps = text_content(reps_match.group(1)) if reps_match else ""
        if not re.search(r"\b8\s*[–-]\s*12(?:\s+por\s+lado)?\s+repeticiones\b", reps, re.I):
            errors.append(f"{path}: ejercicio {index} repeticiones esperadas=8–12 observadas={reps!r}")

    if 'data-routine-content-version="3"' not in source:
        errors.append(f"{path}: falta data-routine-content-version=3")
    if path.name == "Rutina_Dia_4_Pierna_Equilibrio_V1.html" and "PESO MUERTO RUMANO EN SMITH" not in source:
        errors.append(f"{path}: el ejercicio de bisagra debe usar Smith")

    if result.summary != (expected_count, expected_total):
        errors.append(
            f"{path}: resumen esperado={(expected_count, expected_total)} observado={result.summary}"
        )
    if result.dashboard_total != expected_total:
        errors.append(
            f"{path}: dashboard total esperado={expected_total} observado={result.dashboard_total}"
        )
    if result.dashboard_distribution != expected_distribution:
        errors.append(
            f"{path}: dashboard distribución esperada={expected_distribution} "
            f"observada={result.dashboard_distribution}"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Valida la estructura de las rutinas HTML canónicas.")
    parser.add_argument("paths", nargs="*", type=Path, help="HTML canónicas; por defecto se validan todas las salidas contractuales")
    args = parser.parse_args(argv)
    paths = args.paths or [CANONICAL_DIR / name for name in EXPECTED_CONTRACTS]

    errors = [error for path in paths for error in validate_path(path)]
    if errors:
        print("CANONICAL_ROUTINES_FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"CANONICAL_ROUTINES_OK routines={len(paths)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
