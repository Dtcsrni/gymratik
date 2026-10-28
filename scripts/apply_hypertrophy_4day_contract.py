"""Aplica el plan de hipertrofia v3 sin mover las claves de progreso existentes.

Los ejercicios añadidos ocupan índices vacíos. El cuarto día es opcional; los
tres primeros conforman la rotación base. Los índices históricos se conservan.
"""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "data/rutinas_autocontenidas/canonicas"

ROUTINES = {
    1: ("Rutina_Dia_1_Espalda_Biceps_V1.html", 7, (4, 4, 3, 3, 3, 3, 3), 23),
    2: ("Rutina_Dia_2_Pierna_Gluteo_V1.html", 7, (3, 3, 3, 4, 4, 3, 3), 23),
    3: ("Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html", 7, (4, 3, 3, 3, 3, 3, 3), 22),
    4: ("Rutina_Dia_4_Pierna_Equilibrio_V1.html", 7, (3, 3, 4, 3, 3, 3, 3), 22),
}

# (routine receiving card, source routine, exact source title)
ADDITIONS = {
    1: [(3, "PRESS DE PECHO SENTADO EN MÁQUINA")],
    2: [(4, "ABDUCCIÓN DE CADERA SENTADA")],
    3: [],
    4: [],
}

BASE_COUNTS = {1: 6, 2: 6, 3: 7, 4: 7}

CARD_RE = re.compile(r"<article\b(?=[^>]*\bclass=[\"'][^\"']*\bcard\b)[^>]*>.*?</article>", re.I | re.S)
TITLE_RE = re.compile(r'<div\s+class=["\']exTitle["\']\s*>(.*?)</div>', re.I | re.S)


def title_of(card: str) -> str:
    match = TITLE_RE.search(card)
    if not match:
        raise ValueError("Tarjeta sin .exTitle")
    return " ".join(html.unescape(re.sub(r"<[^>]*>", " ", match.group(1))).split()).upper()


def cards_of(source: str) -> list[str]:
    return [match.group(0) for match in CARD_RE.finditer(source)]


def set_series(card: str, index: int, series: int, *, appended: bool = False) -> str:
    opening = re.match(r"<article\b[^>]*>", card, re.I | re.S)
    if not opening:
        raise ValueError("Tarjeta inválida")
    tag = opening.group(0)
    tag = re.sub(r'\sdata-exercise-index=["\'][^"\']*["\']', "", tag, flags=re.I)
    tag = tag[:-1] + f' data-exercise-index="{index}"' + (f' data-generated-routine="hypertrophy-v3"' if appended else "") + ">"
    card = tag + card[opening.end():]

    card = re.sub(r'(<div\s+class=["\']num["\']\s*>).*?(</div>)', rf'\g<1>{index}\g<2>', card, count=1, flags=re.I | re.S)
    card = re.sub(r'(<span\s+class=["\']infoChip\s+chipExercise["\']\s*>).*?(</span>)', rf'\g<1>Ejercicio {index}\g<2>', card, count=1, flags=re.I | re.S)
    tracker = re.search(r'<div\b(?=[^>]*\bclass=["\'][^"\']*\bexerciseTracker\b)[^>]*>', card, re.I)
    if not tracker:
        raise ValueError(f"{title_of(card)}: falta exerciseTracker")
    tracker_tag = tracker.group(0)
    tracker_tag = re.sub(r'\sdata-exercise=["\'][^"\']*["\']', f' data-exercise="{index}"', tracker_tag, flags=re.I)
    tracker_tag = re.sub(r'\sdata-series-keys=["\'][^"\']*["\']', f' data-series-keys="{" ".join(f"e{index}s{n}" for n in range(1, series + 1))}"', tracker_tag, flags=re.I)
    card = card[:tracker.start()] + tracker_tag + card[tracker.end():]
    card = re.sub(r'data-pending-key=["\']p\d+["\']', f'data-pending-key="p{index}"', card, count=1, flags=re.I)
    def update_series_metric(match: re.Match[str]) -> str:
        old_value = html.unescape(re.sub(r"<[^>]*>", "", match.group(2))).strip()
        suffix = " + 1 calent." if "calent" in old_value.casefold() else " series"
        return f"{match.group(1)}{series}{suffix}{match.group(3)}"

    card = re.sub(
        r'(<div\s+class=["\']metric series["\'].*?<div\s+class=["\']metricVal["\']\s*>)(.*?)(</div>)',
        update_series_metric,
        card,
        count=1,
        flags=re.I | re.S,
    )
    card = re.sub(r'(<strong\s+class=["\']exerciseProgress["\']\s*>\s*0/)\d+(</strong>)', rf'\g<1>{series}\g<2>', card, count=1, flags=re.I)
    card = re.sub(r'(aria-label=["\']Completar serie 1 de )\d+(["\'])', rf'\g<1>{series}\g<2>', card, count=1, flags=re.I)
    card = re.sub(r'(<button\b[^>]*class=["\'][^"\']*\bcompleteSetButton\b[^"\']*["\'][^>]*>\s*(?:<[^>]+>\s*)*Completar serie 1 de )\d+', rf'\g<1>{series}', card, count=1, flags=re.I)
    for old_day in (1, 2, 3, 4):
        card = card.replace(f"day{old_day}StaticFrame", "routineStaticFrame")
        card = card.replace(f"day{old_day}ExerciseGif", "routineExerciseGif")
    if appended:
        card = card.replace("data-generated-routine=\"hypertrophy-v3\" data-exercise-index", "data-exercise-index")
        card = card.replace(f'data-exercise-index="{index}"', f'data-exercise-index="{index}" data-generated-routine="hypertrophy-v3"', 1)
    return card


def set_rep_range(card: str) -> str:
    title = title_of(card)
    value = "8–12 por lado repeticiones" if title == "PRENSA UNILATERAL ALTERNA" else "8–12 repeticiones"
    return re.sub(
        r'(<div\s+class=["\']metric reps["\'].*?<div\s+class=["\']metricVal["\']\s*>).*?(</div>)',
        lambda m: m.group(1) + value + m.group(2), card, count=1, flags=re.I | re.S,
    )


def adapt_smith_rdl(card: str) -> str:
    if title_of(card) != "PESO MUERTO RUMANO CON BARRA":
        return card
    card = card.replace("PESO MUERTO RUMANO CON BARRA", "PESO MUERTO RUMANO EN SMITH")
    card = card.replace("barra libre y discos · bisagra de cadera", "máquina Smith · barra guiada y seguros")
    card = card.replace("barbell-rdl-v1", "smith-rdl-v2")
    card = card.replace("barra libre", "barra guiada en Smith")
    card = card.replace("barra sobre el mediopié. Tómala apenas por fuera de las piernas y empieza de pie, con rodillas suaves, abdomen firme y espalda neutra.", "Ajusta la barra a una altura cómoda y coloca los seguros justo por debajo del rango previsto. Alinea los pies bajo la barra; confirma cómo contrapesa la Smith antes de cargar.")
    card = card.replace("Desplaza la cadera atrás y baja la barra pegada a muslos y piernas. Detén el descenso cuando notes tensión clara en isquiosurales antes de redondear la espalda; vuelve llevando la cadera al frente.", "Desliza la barra por los rieles mientras llevas la cadera atrás. Baja solo hasta sentir tensión en isquiosurales sin redondear la espalda y vuelve extendiendo la cadera.")
    card = card.replace("Baja en 2–3 s y sube en 1–2 s. Mantén los brazos largos y la barra rozando las piernas.", "Baja en 2–3 s y sube en 1–2 s. Mantén la barra cerca de las piernas y el recorrido controlado.")
    card = card.replace("Convertirlo en sentadilla, alejar la barra, doblar más las rodillas durante el descenso, redondear la espalda o hiperextender al subir.", "Convertirlo en sentadilla, separar la barra del cuerpo, perder la espalda neutra o bloquear los seguros durante la repetición.")
    card = re.sub(r'(<article\b[^>]*>)', r'\1', card, count=1)
    card = card.replace('data-exercise-index="2"', 'data-exercise-index="2" data-history-exercise-id="day4-smith-rdl-v2"', 1)
    card = card.replace("weightLoadProfilePlaceholder", "")
    return card


def close_div_offset(fragment: str, start: int) -> int:
    depth = 1
    token = re.compile(r"</?div\b[^>]*>", re.I)
    for match in token.finditer(fragment, start):
        if match.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return match.start()
        else:
            depth += 1
    raise ValueError("No se encontró cierre de div")


def set_next_cue(card: str, index: int, following: tuple[int, str] | None) -> str:
    cue_re = re.compile(r'<button\b(?=[^>]*\bclass=["\'][^"\']*\bnextExerciseCue\b)[^>]*>.*?</button>', re.I | re.S)
    cue = (
        f'<button type="button" class="nextExerciseCue" data-next="{following[0]}" hidden>'
        f'<span class="nextArrow" aria-hidden="true">↓</span> Siguiente: {following[0]:02d} · {following[1].capitalize()}</button>'
        if following else ""
    )
    if cue_re.search(card):
        card = cue_re.sub(cue, card, count=1)
    elif following:
        row = re.search(r'<div\s+class=["\']nextExerciseRow["\']\s*>.*?</div>', card, re.I | re.S)
        if row:
            card = card[:row.start()] + f'<div class="nextExerciseRow">{cue}</div>' + card[row.end():]
        else:
            button_group = re.search(r'<div\b(?=[^>]*\bclass=["\'][^"\']*\bexerciseSetButtons\b)[^>]*>', card, re.I)
            if not button_group:
                raise ValueError(f"Ejercicio {index}: falta .exerciseSetButtons")
            close = close_div_offset(card, button_group.end())
            card = card[:close] + f'<div class="nextExerciseRow">{cue}</div>' + card[close:]
    return card


def update_sections(source: str, day: int, count: int, distribution: tuple[int, ...], total: int) -> str:
    summary = re.compile(r'(<h2\s+id=["\']routine-summary-title["\'][^>]*>).*?(</h2>)', re.I | re.S)
    source = summary.sub(lambda m: f'{m.group(1)}{count} ejercicios · {total} series efectivas{m.group(2)}', source, count=1)
    source, headline_count = re.subn(
        r'(<span\b[^>]*\bid=["\']summaryHeadline["\'][^>]*>)\s*\d+/\d+\s+ejercicios',
        rf'\g<1>0/{count} ejercicios',
        source,
        count=1,
        flags=re.I,
    )
    if headline_count != 1:
        raise ValueError(f"Día {day}: falta el contador de ejercicios de la barra de estado")
    source = re.sub(r'(data-total-series=["\'])\d+(["\'])', rf'\g<1>{total}\2', source, flags=re.I)
    source = re.sub(r'(0/\d+ ejercicios · 0/)\d+( series)', rf'\g<1>{total}\2', source, flags=re.I)
    source = re.sub(r'(doneSeries\s*}}/)\d+', rf'\g<1>{total}', source)
    source = re.sub(r'(class=["\'][^"\']*\bdashValue\b[^"\']*["\'][^>]*>)[^<]*', rf'\g<1>{total}', source, count=1, flags=re.I)
    # Dashboard counters have one summary value and one series-distribution value.
    distribution_text = " + ".join(map(str, distribution)) + " series"
    source = re.sub(r'(<div\s+class=["\']dashSub["\'][^>]*>).*?\s+series(</div>)', rf'\g<1>{distribution_text}\g<2>', source, count=1, flags=re.I | re.S)
    for section_name in ("routineSummary", "sessionDashboard"):
        section = re.search(rf'(<section\s+class=["\'][^"\']*\b{section_name}\b[^"\']*["\'][^>]*>).*?</section>', source, re.I | re.S)
        if section:
            content = re.sub(r'\b\d+\s*[–-]\s*\d+\s*min\b', '90–115 min', section.group(0), count=1, flags=re.I)
            source = source[:section.start()] + content + source[section.end():]
    # Calentamiento conserva su duración propia; la duración objetivo es de la sesión.
    source = source.replace('Calentamiento · 90–115 min', 'Calentamiento · 8–10 min')
    source = re.sub(r'\b\d+ pendientes\b', f'{total} pendientes', source)
    source = re.sub(r'\b\d+/\d+ series\b', f'0/{total} series', source)
    source = source.replace(' · v1 responsive', ' · rutina v3')
    headings = {
        1: {
            "DÍA 1 · TIRÓN: ESPALDA Y BÍCEPS": "DÍA 1 · TREN SUPERIOR A: ESPALDA Y BÍCEPS",
            "Tirones verticales y remos · deltoides posterior · bíceps · pecho complementario": "Espalda y bíceps con press de pecho complementario",
            "Rutina de tren superior enfocada principalmente en espalda y bíceps, con trabajo complementario de deltoides posterior y un segundo patrón de bíceps.": "Tren superior A: espalda y bíceps, con press de pecho complementario.",
        },
        2: {
            "DÍA 1 · TREN SUPERIOR A: ESPALDA Y BÍCEPS": "DÍA 2 · TREN INFERIOR A: CUÁDRICEPS Y GLÚTEOS",
            "DÍA 2 · PIERNA: CUÁDRICEPS Y GLÚTEOS": "DÍA 2 · TREN INFERIOR A: CUÁDRICEPS Y GLÚTEOS",
            "Rutina de tren inferior con prioridad en cuádriceps y glúteo; isquiosurales y pantorrilla reciben trabajo específico.": "Tren inferior A: cuádriceps y glúteos, más isquiosurales, abductores y pantorrilla.",
        },
        3: {
            "DÍA 1 · TREN SUPERIOR A: ESPALDA Y BÍCEPS": "DÍA 3 · TREN SUPERIOR B: PECHO Y HOMBROS",
            "DÍA 3 · EMPUJE: PECHO, HOMBROS Y TRÍCEPS": "DÍA 3 · TREN SUPERIOR B: PECHO Y HOMBROS",
            "Rutina de tren superior equilibrada, con trabajo de pecho, hombros y tríceps.": "Tren superior B: pecho, hombros y tríceps.",
        },
        4: {
            "DÍA 1 · TREN SUPERIOR A: ESPALDA Y BÍCEPS": "DÍA 4 · OPCIONAL: POSTERIOR Y CORE",
            "DÍA 4 · PIERNA Y CORE: CADERA Y ESTABILIDAD": "DÍA 4 · OPCIONAL: POSTERIOR Y CORE",
            "Rutina de tren inferior equilibrada, con trabajo de rodilla, cadera, pantorrilla y core.": "Tren inferior B: bisagra en Smith, flexión y extensión de rodilla, cadera, pantorrilla y core.",
        },
    }
    for old, new in headings[day].items():
        source = source.replace(old, new)
    source = source.replace("MÁQUINAS + IMPLEMENTOS · GUÍA VISUAL", "MÁQUINAS + SMITH · GUÍA VISUAL")
    page_titles = {
        1: "Día 1 · Tren superior A: espalda y bíceps · rutina v3",
        2: "Día 2 · Tren inferior A: cuádriceps y glúteos · rutina v3",
        3: "Día 3 · Tren superior B: pecho y hombros · rutina v3",
        4: "Día 4 · Opcional: posterior y core · rutina v3",
    }
    source = re.sub(r'<title>.*?</title>', f'<title>{page_titles[day]}</title>', source, count=1, flags=re.I | re.S)
    source = re.sub(r'(data-label=["\'])[^"\']*(Día\s+\d+)[^"\']*(["\'])', lambda m: f'{m.group(1)}{page_titles[day]}{m.group(3)}', source, count=1, flags=re.I)
    source = re.sub(r'data-routine-cover="day\d+"', f'data-routine-cover="day{day}"', source, flags=re.I)
    source = re.sub(r'src="\.\./\.\./\.\./assets/branding/routine-covers/day\d+\.webp"', f'src="../../../assets/branding/routine-covers/day{day}.webp"', source, flags=re.I)
    source = re.sub(
        r'(<html\b[^>]*)(>)',
        lambda m: re.sub(r'\sdata-(?:routine-content-version|routine-cover)=["\'][^"\']*["\']', '', m.group(1))
        + f' data-routine-content-version="3" data-routine-cover="day{day}"' + m.group(2),
        source,
        count=1,
        flags=re.I,
    )
    return source


def apply() -> list[str]:
    files = {day: CANONICAL / contract[0] for day, contract in ROUTINES.items()}
    texts = {day: path.read_text(encoding="utf-8") for day, path in files.items()}
    original = {day: cards_of(text) for day, text in texts.items()}
    additions: dict[int, list[str]] = {day: [] for day in ROUTINES}
    for target, source_specs in ADDITIONS.items():
        for source_day, title in source_specs:
            source_card = next((card for card in original[source_day] if title_of(card) == title), None)
            if source_card is None:
                raise ValueError(f"No se encontró tarjeta origen: Día {source_day} · {title}")
            additions[target].append(source_card)

    changed: list[str] = []
    for day, (filename, expected_count, distribution, total) in ROUTINES.items():
        cards = original[day][:BASE_COUNTS[day]] + additions[day]
        if len(original[day]) < BASE_COUNTS[day]:
            raise ValueError(f"Día {day}: faltan tarjetas base; recibidas={len(original[day])}")
        if len(cards) != expected_count or len(distribution) != expected_count or sum(distribution) != total:
            raise ValueError(f"Día {day}: contrato interno inconsistente")
        normalized = [set_rep_range(set_series(card, index, distribution[index - 1], appended=index > BASE_COUNTS[day])) for index, card in enumerate(cards, 1)]
        if day == 4:
            normalized[1] = adapt_smith_rdl(normalized[1])
            normalized[1] = re.sub(
                r'(<article\b[^>]*data-exercise-index="2"[^>]*>)',
                lambda match: match.group(1) if 'data-history-exercise-id=' in match.group(1)
                else match.group(1)[:-1] + ' data-history-exercise-id="day4-smith-rdl-v2">',
                normalized[1],
                count=1,
                flags=re.I,
            )
        for index, card in enumerate(normalized, 1):
            following = (index + 1, title_of(normalized[index])) if index < len(normalized) else None
            normalized[index - 1] = set_next_cue(card, index, following)
        first = CARD_RE.search(texts[day])
        last = list(CARD_RE.finditer(texts[day]))[-1]
        updated = texts[day][:first.start()] + "\n".join(normalized) + texts[day][last.end():]
        updated = update_sections(updated, day, expected_count, distribution, total)
        if day == 4:
            # El peso muerto cambió de barra libre a Smith: separa su historial
            # del identificador numérico que antes pertenecía al movimiento previo.
            updated = updated.replace(
                "const exerciseId = String(item.index + 1);",
                "const exerciseId = item.historyExerciseId || String(item.index + 1);",
            )
            updated = updated.replace(
                "const historyExerciseId = String(item.index + 1);",
                "const historyExerciseId = item.historyExerciseId || String(item.index + 1);",
            )
            updated = updated.replace(
                "record.exerciseId === String(item.index + 1)",
                "record.exerciseId === (item.historyExerciseId || String(item.index + 1))",
            )
        files[day].write_text(updated, encoding="utf-8", newline="\n")
        changed.append(filename)
    return changed


if __name__ == "__main__":
    for filename in apply():
        print(f"UPDATED {filename}")
