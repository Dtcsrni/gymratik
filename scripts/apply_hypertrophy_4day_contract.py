"""Aplica el plan de hipertrofia v3 sin mover las claves de progreso existentes.

Los ejercicios añadidos ocupan índices vacíos. El cuarto día es opcional; los
tres primeros conforman la rotación base. Los índices históricos se conservan.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from standardize_muscle_visuals import apply_warmup_load_selector_contract, standardize_quote_portrait_loading


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


INTERACTION_REDESIGN = r'''<style data-enhancement="exercise-focus-occupied-quote-v8">
/* Separa visualmente cada ejercicio y reserva el ámbar para una máquina ocupada. */
main.cards article.card[data-exercise-index]{--exercise-accent:#72dcff;position:relative;border:1px solid color-mix(in srgb,var(--exercise-accent) 30%,transparent);transition:border-color .24s ease,box-shadow .24s ease,transform .24s ease}
main.cards article.card[data-exercise-index]:focus-within,main.cards article.card[data-exercise-index].is-exercise-focused{border-color:var(--exercise-accent);box-shadow:0 0 0 2px color-mix(in srgb,var(--exercise-accent) 22%,transparent),0 18px 42px rgba(0,0,0,.24)}
main.cards article.card[data-exercise-index] .num{background:color-mix(in srgb,var(--exercise-accent) 20%,#071b28)!important;border-color:var(--exercise-accent)!important;color:#f3fcff!important}
main.cards article.card[data-exercise-index] .exTitle{ text-wrap:balance }
main.cards article.card[data-exercise-index][data-machine-occupied="true"]{isolation:isolate;border:2px solid #ffd166!important;background:linear-gradient(145deg,rgba(102,74,22,.68),rgba(36,31,19,.94))!important;box-shadow:0 0 0 2px rgba(255,209,102,.18),0 16px 42px rgba(0,0,0,.22)!important}
main.cards article.card[data-machine-occupied="true"]::after{position:absolute;z-index:1;inset:0;border-radius:inherit;background:rgba(255,196,67,.12);backdrop-filter:blur(1.2px);-webkit-backdrop-filter:blur(1.2px);content:"";pointer-events:none}
main.cards article.card[data-machine-occupied="true"]>:not(.exerciseTracker),main.cards article.card[data-machine-occupied="true"] .exerciseTracker> :not(.exerciseSetButtons),main.cards article.card[data-machine-occupied="true"] .exerciseSetButtons>:not(.machinePendingToggle){filter:blur(1.7px) saturate(.55)!important;opacity:.52!important;pointer-events:none!important;user-select:none!important}
main.cards article.card[data-machine-occupied="true"] .exerciseTracker{border-color:#ffd166!important;background:linear-gradient(145deg,rgba(105,75,19,.56),rgba(43,35,18,.72))!important;box-shadow:inset 0 0 0 1px rgba(255,209,102,.2),0 0 18px rgba(255,209,102,.1)!important}
main.cards article.card[data-machine-occupied="true"] .machinePendingToggle{position:relative;z-index:5;pointer-events:auto!important;border-color:#ffe08a!important;background:linear-gradient(135deg,#8b641c,#624715)!important;color:#fff3c6!important;box-shadow:0 0 0 2px rgba(255,209,102,.2)}
.floatingSessionSummary .summaryFocusBadge{display:none;min-width:0;max-width:100%;margin:.1rem 0;padding:.22rem .35rem;border:1px solid rgba(255,209,102,.68);border-radius:.38rem;background:rgba(107,75,18,.82);color:#fff0bf;font-size:.57rem;font-weight:950;line-height:1.15;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.floatingSessionSummary.is-exercise-focused .summaryFocusBadge{display:block;animation:exerciseFocusReveal .34s cubic-bezier(.2,.8,.2,1) both}
.floatingSessionSummary.is-exercise-focused .summaryToggle{box-shadow:inset 3px 0 #ffd166,0 0 16px rgba(255,209,102,.2);animation:exerciseBarPulse 1.25s ease-in-out infinite alternate}
.summaryExercise.isCurrent{outline:2px solid #ffd166;outline-offset:1px;animation:exerciseFocusReveal .34s ease both}
.warmupSet:not([hidden]){display:inline-flex;align-items:center;gap:.35rem;padding:.38rem .58rem;border:1px solid #ffd166;border-radius:.58rem;background:rgba(104,73,18,.62);color:#fff0bf;font-size:.68rem;font-weight:950;letter-spacing:.035em}
.exerciseWarmupHint:not([hidden]){border-color:rgba(255,209,102,.7)!important;background:linear-gradient(110deg,rgba(103,73,20,.35),rgba(38,31,19,.42))!important;color:#ffedbd!important}
.sessionCompletionPanel:not([hidden]){border:1px solid rgba(117,230,255,.36);background:radial-gradient(ellipse at 0 0,rgba(45,153,173,.2),transparent 52%),linear-gradient(145deg,rgba(14,43,59,.98),rgba(10,20,38,.99));box-shadow:0 20px 60px rgba(0,0,0,.42),inset 0 1px rgba(255,255,255,.08)}
.sessionCompletionCopy{padding:.2rem .25rem}
.sessionCompletionKicker{display:inline-flex;align-items:center;gap:.4rem;padding:.28rem .48rem;border:1px solid rgba(101,242,221,.38);border-radius:999px;background:rgba(20,91,83,.25);letter-spacing:.1em}
.sessionCompletionCopy p#motivationMessage{position:relative;margin:.35rem 0 .25rem;padding:.85rem 1rem .85rem 1.2rem;border-left:3px solid #65f2dd;border-radius:.2rem .8rem .8rem .2rem;background:linear-gradient(100deg,rgba(18,91,83,.2),rgba(8,27,39,.45));color:#f4fdff;font-size:clamp(1.05rem,2.6vw,1.45rem);font-weight:850;line-height:1.38;letter-spacing:-.015em;text-wrap:pretty}
.sessionCompletionCopy p#motivationMessage::before{content:"“";position:absolute;left:.35rem;top:.15rem;color:#65f2dd;font-size:1.1rem;line-height:1}
.motivationNote{font-weight:800}
.sessionCompletionPanel.isPartial{border-color:rgba(255,209,102,.52)!important;background:radial-gradient(ellipse at 0 0,rgba(177,123,35,.17),transparent 52%),linear-gradient(145deg,rgba(55,43,24,.98),rgba(19,27,38,.99))!important}
.sessionCompletionPanel.isPartial .sessionCompletionKicker{border-color:rgba(255,209,102,.4);background:rgba(111,77,22,.24);color:#ffdc8c}
.sessionRecap{margin-top:.8rem;padding:.8rem;border:1px solid rgba(114,220,255,.2);border-radius:.9rem;background:linear-gradient(135deg,rgba(4,22,34,.7),rgba(14,34,48,.7));animation:recapReveal .5s cubic-bezier(.2,.8,.2,1) both}
.sessionRecapHeader{display:flex;align-items:center;justify-content:space-between;gap:.8rem;margin-bottom:.65rem}
.sessionRecapTitle{margin:0;color:#dff8ff;font-size:clamp(1rem,2.2vw,1.35rem);font-weight:950;letter-spacing:.06em;text-transform:uppercase}
.sessionProgressRing{position:relative;flex:0 0 4.6rem;width:4.6rem;height:4.6rem;filter:drop-shadow(0 0 14px rgba(101,242,221,.16))}
.sessionProgressRing svg{display:block;width:100%;height:100%;transform:rotate(-90deg)}
.sessionProgressRing circle{fill:none;stroke-width:7}
.sessionRingTrack{stroke:rgba(157,204,218,.2)}
.sessionRingProgress{stroke:#65f2dd;stroke-linecap:round;transition:stroke-dashoffset .65s cubic-bezier(.2,.8,.2,1)}
.sessionRingValue{position:absolute;inset:0;display:grid;align-content:center;justify-items:center;color:#eafffc}
.sessionRingValue strong{font-size:1rem;line-height:1;font-variant-numeric:tabular-nums}
.sessionRingValue small{margin-top:.16rem;color:#a9d2d6;font-size:.57rem;font-weight:850;text-transform:uppercase;letter-spacing:.1em}
.sessionRecapGrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.5rem;margin:0}
.sessionRecapMetric{min-width:0;padding:.5rem .55rem;border:1px solid rgba(157,204,218,.12);border-radius:.65rem;background:rgba(3,16,25,.5);animation:recapMetricIn .42s cubic-bezier(.2,.8,.2,1) both}
.sessionRecapMetric:nth-child(2){animation-delay:.05s}.sessionRecapMetric:nth-child(3){animation-delay:.1s}.sessionRecapMetric:nth-child(4){animation-delay:.15s}.sessionRecapMetric:nth-child(5){animation-delay:.2s}
.sessionRecapMetric dt{color:#91adba;font-size:.6rem;font-weight:800;line-height:1.2}
.sessionRecapMetric dd{margin:.2rem 0 0;color:#a9f1dd;font-size:clamp(.86rem,1.5vw,1.12rem);font-weight:950;line-height:1.1;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.sessionCompletionPanel.isPartial .sessionRecapMetric dd{color:#ffe0a0}
.sessionMuscleViz{position:relative;margin-top:.7rem;padding:.82rem .7rem .7rem;border:1px solid rgba(255,91,112,.38);border-radius:.9rem;background:radial-gradient(ellipse at 0 0,rgba(183,42,62,.2),transparent 56%),linear-gradient(145deg,rgba(17,27,43,.94),rgba(3,16,25,.76));box-shadow:inset 0 1px rgba(255,255,255,.045),0 12px 28px rgba(0,0,0,.16);overflow:hidden}
.sessionMuscleViz::before{position:absolute;top:0;left:.7rem;right:.7rem;height:2px;background:linear-gradient(90deg,transparent,#f0445d 25%,#ff927d 50%,#f0445d 75%,transparent);box-shadow:0 0 14px rgba(240,68,93,.55);content:""}
.muscleVizHeader{display:flex;align-items:center;justify-content:space-between;gap:.5rem;margin-bottom:.45rem}
.muscleVizHeader h4{display:flex;align-items:center;gap:.5rem}
.muscleVizHeader h4::before{width:.28rem;height:1.1em;border-radius:99px;background:linear-gradient(#ff6573,#bd243e);box-shadow:0 0 10px rgba(240,68,93,.44);content:""}
.muscleVizHeader h4{margin:0;color:#e4fbff;font-size:clamp(.92rem,2vw,1.12rem);font-weight:950}
.muscleVizHeader{margin-bottom:.62rem}
.muscleVizLayout{display:grid;grid-template-columns:minmax(7.2rem,.85fr) minmax(0,1.5fr);align-items:center;gap:.55rem}
.sessionMuscleMap{display:grid;grid-template-columns:minmax(0,1fr);gap:.36rem;width:100%;min-width:0}
.muscleAnatomyFigure{position:relative;display:grid;grid-template-rows:minmax(0,1fr) auto;gap:.24rem;min-width:0;margin:0;padding:.28rem;border:1px solid rgba(255,108,123,.34);border-radius:.7rem;background:linear-gradient(155deg,#f5f2e9,#dbe3df);overflow:hidden;isolation:isolate;box-shadow:inset 0 0 0 1px rgba(255,255,255,.24),0 0 18px rgba(212,42,65,.12)}
.muscleAnatomyFigure::after{position:absolute;z-index:-1;inset:8% 8%;border-radius:50%;background:radial-gradient(ellipse,rgba(244,46,72,.58),rgba(226,54,73,.2) 48%,transparent 76%);filter:blur(19px);content:"";opacity:.5;animation:muscleTissueGlow 2.15s ease-in-out infinite;will-change:transform,opacity}
.muscleAnatomyFigure:nth-child(2)::after{animation-delay:-1.6s}
.muscleAnatomyFigure img{display:block;width:100%;height:8.5rem;object-fit:contain;transform-origin:50% 52%;animation:muscleGrowthPulse 2.15s cubic-bezier(.4,0,.2,1) infinite;will-change:transform}
.muscleAnatomyFigure:nth-child(2) img{animation-delay:-1.6s}
.muscleAnatomyFigure figcaption{overflow:hidden;color:#263a43;font-size:.52rem;font-weight:950;letter-spacing:.04em;text-align:center;text-overflow:ellipsis;text-transform:uppercase;white-space:nowrap}
.sessionMuscleRows{display:grid;gap:.34rem;min-width:0;margin:0;padding:0;list-style:none}
.sessionMuscleRow{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:.14rem .4rem;align-items:center;min-width:0;padding:.3rem .42rem;border:1px solid rgba(157,204,218,.12);border-radius:.52rem;background:rgba(11,32,45,.72);animation:recapMetricIn .35s both}
.sessionMuscleRowLabel{overflow:hidden;color:#e2f6fa;font-size:.72rem;font-weight:850;text-overflow:ellipsis;white-space:nowrap}
.sessionMuscleRowCount{color:#ffb7c0;font-size:.68rem;font-weight:950;white-space:nowrap;font-variant-numeric:tabular-nums}
.sessionMuscleBar{grid-column:1/-1;height:.32rem;overflow:hidden;border-radius:99px;background:rgba(157,204,218,.13)}
.sessionMuscleBar span{display:block;width:0;height:100%;border-radius:inherit;background:linear-gradient(90deg,#b92540,#f0445d 58%,#ff9a86);box-shadow:0 0 12px rgba(240,68,93,.48);transition:width .8s cubic-bezier(.2,.8,.2,1)}
.sessionMuscleEmpty{grid-column:1/-1;margin:0;padding:.7rem;color:#b9d2db;font-size:.78rem;line-height:1.4}
.sessionFunFact{margin:.55rem 0 0;padding:.55rem .65rem;border-left:3px solid #ffd166;border-radius:.25rem .6rem .6rem .25rem;background:rgba(117,79,18,.16);color:#ffe6b3;font-size:.76rem;font-weight:850;line-height:1.4;animation:factReveal .6s .12s both}
.sessionRecapFoot{margin:.38rem 0 0;color:#8fa9b6;font-size:.61rem;line-height:1.35}
.motivationPhotoWrap.hasMascot{grid-column:2;align-self:center;justify-self:center;width:100%;min-height:10rem;overflow:visible}
.motivationPhotoWrap.hasMascot .motivationPortrait.isMascot{position:relative;display:block;width:clamp(8rem,16vw,11rem)!important;height:clamp(8rem,16vw,11rem)!important;border:0!important;border-radius:0!important;background-color:transparent!important;background-repeat:no-repeat;background-position:50% 50%;background-size:300% 300%;box-shadow:none!important;filter:drop-shadow(0 0 15px rgba(240,68,93,.42));overflow:hidden;animation:completionPoseCycle 5.2s steps(1,end) infinite,completionMascotPose 2.3s ease-in-out infinite;will-change:background-position,transform}
.motivationPhotoWrap.hasMascot .motivationPortrait.isMascot[data-mascot-variant="male"]{background-image:url("../../../data/profile/mascot-motion/states-v1/male-pose-atlas.png")}
.motivationPhotoWrap.hasMascot .motivationPortrait.isMascot[data-mascot-variant="female"]{background-image:url("../../../data/profile/mascot-motion/states-v1/female-pose-atlas.png")}
.motivationPhotoWrap.hasMascot .motivationPortrait.isMascot[data-mascot-variant="neutral"]{background-image:url("../../../data/profile/mascot-motion/neutral-exercise-25fps.gif");background-size:contain;background-position:center;animation:completionMascotPose 2.3s ease-in-out infinite}
.motivationPhotoWrap.hasMascot .motivationPortrait.isMascot img,.motivationPhotoWrap.hasMascot #motivationInitials{display:none!important}
.motivationPhotoWrap.hasMascot::before{position:absolute;inset:12% 8%;border-radius:50%;background:radial-gradient(ellipse,rgba(243,54,83,.3),rgba(243,54,83,.08) 48%,transparent 72%);filter:blur(13px);content:"";pointer-events:none;animation:completionMascotGlow 1.7s ease-in-out infinite}
.motivationPhotoWrap::after{position:absolute;right:4%;top:5%;z-index:2;color:#ff7280;font-size:1.25rem;content:"✦";pointer-events:none;animation:completionSparkle 1s ease-in-out infinite}
@keyframes recapReveal{from{opacity:0;transform:translateY(8px) scale(.985)}to{opacity:1;transform:none}}
@keyframes recapMetricIn{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:none}}
@keyframes factReveal{from{opacity:0;filter:blur(3px)}to{opacity:1;filter:blur(0)}}
@keyframes exerciseFocusReveal{from{opacity:.4;transform:translateY(4px) scale(.98)}to{opacity:1;transform:none}}
@keyframes exerciseBarPulse{from{filter:brightness(1)}to{filter:brightness(1.22)}}
@keyframes completionPoseCycle{0%,22%{background-position:50% 0%}25%,47%{background-position:50% 50%}50%,72%{background-position:100% 100%}75%,97%{background-position:0% 100%}}
@keyframes completionMascotPose{0%,100%{transform:translateY(2px) rotate(-2deg) scale(.98,1)}30%{transform:translateY(-6px) rotate(2deg) scale(1.04,.97)}55%{transform:translateY(-2px) rotate(-1deg) scale(.99,1.03)}78%{transform:translateY(-5px) rotate(1deg) scale(1.025,.98)}}
@keyframes completionMascotGlow{0%,100%{opacity:.38;transform:scale(.86)}50%{opacity:.92;transform:scale(1.13)}}
@keyframes completionSparkle{0%,100%{opacity:.45;transform:scale(.72) rotate(-15deg)}50%{opacity:1;transform:scale(1.28) rotate(22deg)}}
@keyframes muscleGrowthPulse{0%,100%{transform:scale(1)}48%{transform:scale(1.065)}}
@keyframes muscleTissueGlow{0%,100%{opacity:.28;transform:scale(.78)}48%{opacity:.92;transform:scale(1.16)}}
@keyframes snackOffer{0%,100%{transform:translate(0,0) rotate(5deg) scale(.94)}45%{transform:translate(-5px,-5px) rotate(-9deg) scale(1.06)}70%{transform:translate(-2px,-1px) rotate(2deg) scale(1)}}
@media(max-width:640px){.floatingSessionSummary .summaryFocusBadge{font-size:.55rem}.sessionCompletionCopy p#motivationMessage{padding:.75rem .8rem .75rem 1.05rem}.sessionRecap{padding:.62rem}.sessionRecapGrid{grid-template-columns:repeat(2,minmax(0,1fr));gap:.35rem}.sessionRecapMetric{padding:.45rem}.sessionRecapMetric dt{font-size:.64rem}.sessionRecapMetric dd{font-size:.92rem}.sessionFunFact{font-size:.78rem}.sessionRecapHeader{margin-bottom:.5rem}.sessionRecapTitle{font-size:1.04rem}.sessionProgressRing{flex-basis:4rem;width:4rem;height:4rem}.sessionMuscleViz{padding:.82rem .56rem .56rem}.muscleVizLayout{grid-template-columns:minmax(6.3rem,.78fr) minmax(0,1.5fr);gap:.4rem}.muscleAnatomyFigure{padding:.2rem}.muscleAnatomyFigure img{height:7.4rem}.muscleAnatomyFigure figcaption{font-size:.45rem}.sessionMuscleRowLabel{font-size:.68rem}.sessionMuscleRowCount{font-size:.64rem}
  .sessionCompletionPanel:not([hidden]){grid-template-columns:minmax(0,1fr) minmax(6.2rem,7.2rem)!important;grid-template-rows:auto auto auto auto auto auto!important;align-items:start!important;gap:.3rem .45rem!important;padding:.65rem .72rem!important;overflow:hidden!important}
  .sessionCompletionPanel:not([hidden])>*{min-width:0!important;max-width:100%!important}
  .sessionCompletionPanel .completionOrb{display:none!important}
  .sessionCompletionPanel .motivationPhotoWrap{grid-column:2!important;grid-row:1/3!important;align-self:center!important;justify-self:center!important;width:100%!important;min-height:6.5rem!important;gap:0!important}
  .sessionCompletionPanel .motivationPhotoWrap.hasMascot .motivationPortrait{width:min(6.6rem,24vw)!important;height:min(6.6rem,24vw)!important}
  .sessionCompletionPanel .motivationPhotoCredit{display:none!important}
  .sessionCompletionPanel .sessionCompletionCopy{display:contents!important}
  .sessionCompletionPanel .sessionCompletionKicker{grid-column:1!important;grid-row:1!important;align-self:center!important;max-width:100%!important;padding:.18rem .34rem!important;font-size:.55rem!important;letter-spacing:.07em!important;line-height:1.15!important}
  .sessionCompletionPanel #session-completion-title{grid-column:1!important;grid-row:2!important;margin:.05rem 0 .08rem!important;font-size:1.18rem!important;line-height:1.08!important}
  .sessionCompletionPanel #motivationMessage{grid-column:1/-1!important;grid-row:3!important;margin:.12rem 0!important;padding:.42rem .55rem .42rem .85rem!important;font-size:.9rem!important;line-height:1.28!important}
  .sessionCompletionPanel #motivationMessage::before{left:.24rem!important;top:.08rem!important}
  .sessionCompletionPanel .motivationNote{grid-column:1/-1!important;grid-row:4!important;margin:.05rem 0 .12rem!important;font-size:.58rem!important;line-height:1.2!important}
  .sessionCompletionPanel .sessionRecap{grid-column:1/-1!important;grid-row:5!important;margin:.12rem 0 0!important;padding:.48rem!important;border-radius:.68rem!important}
  .sessionCompletionPanel .sessionRecapTitle{margin:0!important;font-size:.92rem!important}
  .sessionCompletionPanel .sessionProgressRing{flex-basis:3.9rem!important;width:3.9rem!important;height:3.9rem!important}
  .sessionCompletionPanel .sessionRecapGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:.34rem!important}
  .sessionCompletionPanel .sessionRecapMetric{padding:.34rem .38rem!important;border-radius:.5rem!important}
  .sessionCompletionPanel .sessionRecapMetric dt{font-size:.64rem!important;line-height:1.15!important}
  .sessionCompletionPanel .sessionRecapMetric dd{margin-top:.16rem!important;font-size:.9rem!important;line-height:1.1!important}
  .sessionCompletionPanel .sessionMuscleViz{grid-column:1/-1!important;margin:.35rem 0 0!important;padding:.58rem!important}
  .sessionCompletionPanel .muscleVizHeader h4{font-size:1rem!important}
  .sessionCompletionPanel .sessionMuscleMap{grid-template-columns:minmax(0,1fr)!important}.sessionCompletionPanel .muscleAnatomyFigure img{height:7.2rem!important}.sessionCompletionPanel .sessionMuscleRow{padding:.28rem .34rem!important}.sessionCompletionPanel .sessionMuscleRowLabel{font-size:.65rem!important}.sessionCompletionPanel .sessionMuscleRowCount{font-size:.62rem!important}
  .sessionCompletionPanel .sessionFunFact{grid-column:1/-1!important;margin:.3rem 0 0!important;padding:.35rem .45rem!important;font-size:.64rem!important;line-height:1.25!important}
  .sessionCompletionPanel .sessionRecapFoot{margin:.24rem 0 0!important;font-size:.53rem!important;line-height:1.22!important}
  .sessionCompletionPanel .sessionCompletionActions{grid-column:1/-1!important;grid-row:6!important;gap:.3rem!important;margin:.12rem 0 0!important}
  .sessionCompletionPanel .newMotivation,.sessionCompletionPanel .soundToggle,.sessionCompletionPanel .hapticsToggle{flex:1 1 8rem!important;min-width:0!important;min-height:40px!important;padding:.32rem .42rem!important;font-size:.62rem!important;line-height:1.15!important}
}
@media(max-width:380px){.sessionCompletionPanel:not([hidden]){grid-template-columns:minmax(0,1fr) minmax(5.5rem,6.1rem)!important;padding:.58rem!important}.sessionCompletionPanel .motivationPhotoWrap{width:100%!important;min-height:5.7rem!important}.sessionCompletionPanel .motivationPhotoWrap.hasMascot .motivationPortrait{width:min(5.8rem,23vw)!important;height:min(5.8rem,23vw)!important}.sessionCompletionPanel .sessionRecapGrid{grid-template-columns:repeat(2,minmax(0,1fr))!important}.sessionCompletionPanel #session-completion-title{font-size:1.08rem!important}.sessionCompletionPanel #motivationMessage{font-size:.85rem!important}}
@media(prefers-reduced-motion:reduce){.floatingSessionSummary.is-exercise-focused .summaryFocusBadge,.floatingSessionSummary.is-exercise-focused .summaryToggle,.summaryExercise.isCurrent,.sessionRecap,.sessionRecapMetric,.sessionFunFact,.motivationPhotoWrap.hasMascot .motivationPortrait,.motivationPhotoWrap.hasMascot::before,.motivationPhotoWrap::after,.muscleAnatomyFigure img,.muscleAnatomyFigure::after{animation:none!important}.motivationPhotoWrap.hasMascot .motivationPortrait{will-change:auto}.muscleAnatomyFigure img,.muscleAnatomyFigure::after{will-change:auto}.sessionRingProgress,.sessionMuscleBar span{transition:none!important}main.cards article.card[data-exercise-index]{transition:none}}
</style>
<script data-enhancement="exercise-focus-occupied-quote-v8">
(() => {
  const cards = [...document.querySelectorAll('main.cards article.card[data-exercise-index]')];
  const summary = document.querySelector('.floatingSessionSummary');
  const toggle = document.getElementById('summaryToggle');
  if (!cards.length || !summary || !toggle) return;
  const syncSummaryClearance = () => {
    const height = summary.getBoundingClientRect().height;
    if (Number.isFinite(height) && height > 0) document.documentElement.style.setProperty('--floating-summary-clearance', `${Math.ceil(height + 16)}px`);
  };
  syncSummaryClearance();
  if (typeof ResizeObserver === 'function') { window.gymratikSummaryClearanceObserver = new ResizeObserver(syncSummaryClearance); window.gymratikSummaryClearanceObserver.observe(summary); }
  window.addEventListener('resize', syncSummaryClearance, { passive: true });
  window.visualViewport?.addEventListener('resize', syncSummaryClearance, { passive: true });
  const badge = document.createElement('span');
  badge.className = 'summaryFocusBadge';
  badge.setAttribute('aria-hidden', 'true');
  toggle.insertAdjacentElement('afterend', badge);
  const originalControlState = new WeakMap();
  let focusedCard = null;
  const setFocusedCard = card => {
    if (!card) return;
    focusedCard?.classList.remove('is-exercise-focused');
    focusedCard = card;
    focusedCard.classList.add('is-exercise-focused');
    const number = String(card.dataset.exerciseIndex).padStart(2, '0');
    const title = card.querySelector('.exTitle')?.textContent?.trim() || `Ejercicio ${number}`;
    badge.textContent = `EN FOCO · ${number} · ${title}`;
    summary.classList.add('is-exercise-focused');
    window.gymratikFocusedExerciseIndex = Number(card.dataset.exerciseIndex) - 1;
    document.querySelectorAll('.summaryExercise').forEach(item => item.classList.toggle('isCurrent', Number(item.dataset.exercise) === Number(card.dataset.exerciseIndex)));
  };
  const syncOccupiedState = card => {
    const button = card.querySelector('.machinePendingToggle');
    const occupied = button?.getAttribute('aria-pressed') === 'true';
    card.dataset.machineOccupied = String(occupied);
    button?.setAttribute('aria-label', occupied ? 'Desactivar máquina ocupada para este ejercicio' : 'Marcar máquina ocupada para este ejercicio');
    card.querySelectorAll('button,input,select,textarea,a,summary,[tabindex]').forEach(control => {
      if (control === button) return;
      if (occupied) {
        if (!originalControlState.has(control)) originalControlState.set(control, { disabled: 'disabled' in control ? control.disabled : null, tabindex: control.getAttribute('tabindex'), ariaDisabled: control.getAttribute('aria-disabled') });
        if ('disabled' in control) control.disabled = true;
        control.setAttribute('tabindex', '-1');
        control.setAttribute('aria-disabled', 'true');
      } else if (originalControlState.has(control)) {
        const original = originalControlState.get(control);
        if (original.disabled !== null) control.disabled = original.disabled;
        if (original.tabindex === null) control.removeAttribute('tabindex'); else control.setAttribute('tabindex', original.tabindex);
        if (original.ariaDisabled === null) control.removeAttribute('aria-disabled'); else control.setAttribute('aria-disabled', original.ariaDisabled);
        originalControlState.delete(control);
      }
    });
  };
  cards.forEach((card, index) => {
    const palette = ['#72dcff','#65f2dd','#c2a4ff','#ffd166'];
    card.style.setProperty('--exercise-accent', palette[index % palette.length]);
    card.addEventListener('pointerenter', () => setFocusedCard(card));
    card.addEventListener('focusin', () => setFocusedCard(card));
    card.querySelector('.machinePendingToggle')?.addEventListener('click', () => requestAnimationFrame(() => syncOccupiedState(card)));
    syncOccupiedState(card);
  });
  document.addEventListener('click', event => {
    const card = event.target.closest('article.card[data-machine-occupied="true"]');
    if (card && !event.target.closest('.machinePendingToggle')) { event.preventDefault(); event.stopImmediatePropagation(); }
  }, true);
  document.addEventListener('keydown', event => {
    const card = event.target.closest?.('article.card[data-machine-occupied="true"]');
    if (card && event.target.closest?.('.machinePendingToggle')) return;
    if (card && ['Enter',' '].includes(event.key)) { event.preventDefault(); event.stopImmediatePropagation(); }
  }, true);
  window.gymratikSyncOccupiedCard = syncOccupiedState;
  const visible = new IntersectionObserver(entries => {
    const candidate = entries.filter(entry => entry.isIntersecting).sort((a,b) => b.intersectionRatio-a.intersectionRatio)[0];
    if (candidate && candidate.intersectionRatio > .28) setFocusedCard(candidate.target);
  }, { threshold: [.28,.5,.72] });
  cards.forEach(card => visible.observe(card));
})();
</script>'''

MOBILE_SUMMARY_REDESIGN = r'''<style data-enhancement="mobile-summary-layout-v1">
@media(max-width:640px){
  /* En móvil, presenta la demostración justo después del nombre; la ficha y
     los controles quedan después de la referencia visual del movimiento. */
  main.cards article.card>.meta{display:contents!important}
  main.cards article.card>.meta>*{order:3!important}
  main.cards article.card>.meta>.metaTop{order:0!important}
  main.cards article.card>.meta>.exTitle{order:1!important}
  main.cards article.card>.visual{order:2!important}
  main.cards article.card>.meta>.zone{order:3!important}
  main.cards article.card>.meta>.chipRow{order:4!important}
  main.cards article.card>.meta>.machinePill{order:5!important}
  main.cards article.card>.meta>.referenceRow{order:6!important}
  main.cards article.card>.coach{order:7!important}
  #floatingSessionSummary{left:50%!important;right:auto!important;transform:translateX(-50%)!important;bottom:max(.45rem,env(safe-area-inset-bottom))!important;width:min(420px,calc(100vw - .9rem))!important;max-height:min(36dvh,260px)!important;border-radius:.82rem!important;background:rgba(6,24,37,.94)!important;backdrop-filter:blur(14px) saturate(1.08)!important;-webkit-backdrop-filter:blur(14px) saturate(1.08)!important}
  html body .page{padding-bottom:calc(max(10rem,var(--floating-summary-clearance,10rem)) + env(safe-area-inset-bottom,0px))!important}
  main.cards article.card .zone{display:inline-flex!important;align-self:flex-start!important;max-width:100%!important;margin:9px 0 0!important;padding:.34rem .58rem!important;border:1px solid rgba(114,220,255,.28)!important;border-radius:999px!important;background:rgba(14,57,75,.84)!important;color:#d5f5ff!important;font-size:.72rem!important;line-height:1.2!important;font-weight:850!important;overflow-wrap:anywhere!important}
  main.cards article.card .chipRow{display:none!important}
  #summaryToggle{grid-template-columns:auto minmax(0,1fr) 68px auto!important;grid-template-rows:auto auto!important;min-height:68px!important;gap:.12rem .42rem!important;padding:.36rem .52rem!important}
  #summaryToggle #summaryHeadline{grid-column:2;grid-row:1;font-size:.7rem!important;line-height:1.15!important}
  #summaryToggle #summaryActivityHeadline{grid-column:2;grid-row:2;display:block!important;font-size:.62rem!important;line-height:1.1!important}
  #summaryToggle .summaryMascotWrap{grid-column:3;grid-row:1/3!important;width:66px!important;height:66px!important;border-radius:.78rem!important}
  #summaryToggle #summaryActivityMascot{width:62px!important;height:62px!important}
  #summaryToggle .summaryChevron{grid-column:4;grid-row:1/3!important;font-size:.85rem!important}
  #summaryToggle.isResting{background:linear-gradient(105deg,rgba(112,79,21,.94),rgba(83,61,29,.94))!important}
  #summaryToggle.isActive{background:linear-gradient(105deg,rgba(19,105,91,.94),rgba(19,73,72,.94))!important}
  #summaryToggle.isPreparing{background:linear-gradient(105deg,rgba(24,75,101,.94),rgba(15,45,65,.94))!important}
  #summaryToggle.isComplete{background:linear-gradient(105deg,rgba(112,79,21,.94),rgba(72,51,80,.94))!important}
  #summaryToggle[aria-expanded="true"]{grid-template-rows:auto auto!important;min-height:54px!important}
  #summaryToggle[aria-expanded="true"] #summaryActivityHeadline{display:block!important}
  #summaryToggle[aria-expanded="true"] .summaryMascotWrap{width:66px!important;height:66px!important}
  #summaryToggle[aria-expanded="true"] #summaryActivityMascot{width:62px!important;height:62px!important}
  #summaryToggle[aria-expanded="true"] + #summaryBody{max-height:min(26dvh,190px)!important;padding:.28rem .42rem .36rem!important;gap:.24rem!important}
  #summaryToggle[aria-expanded="true"] + #summaryBody .summaryActivityStatus{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
  #summaryToggle[aria-expanded="true"] + #summaryBody #summaryElapsed{display:none!important}
  #floatingSessionSummary .summaryFocusBadge{margin:0!important;padding:.14rem .34rem!important;font-size:.51rem!important;line-height:1.12!important}
  #summaryActivityMascot[data-motion="strength"]{animation:mascotBarStrength .9s cubic-bezier(.35,0,.2,1) infinite}
  #summaryActivityMascot[data-motion="cardio"]{animation:mascotBarCardio .48s cubic-bezier(.4,0,.6,1) infinite}
  #summaryActivityMascot[data-motion="celebration"]{animation:mascotBarCelebrate 1.1s cubic-bezier(.2,.8,.2,1) infinite;filter:drop-shadow(0 0 12px rgba(255,82,102,.92))}
  .summaryMascotWrap:has(#summaryActivityMascot[data-motion="celebration"]){border-color:rgba(255,93,111,.92)!important;background:rgba(130,28,51,.38)!important;box-shadow:0 0 22px rgba(255,55,88,.5)!important}
  @keyframes mascotBarStrength{0%,100%{transform:translateY(2px) rotate(-2deg) scale(1)}35%{transform:translateY(-6px) rotate(3deg) scale(1.12,.95)}68%{transform:translateY(-1px) rotate(-2deg) scale(.97,1.1)}}
  @keyframes mascotBarCardio{0%,100%{transform:translateY(1px) rotate(-4deg) scale(.96,1.02)}25%{transform:translateY(-6px) rotate(3deg) scale(1.08,.96)}50%{transform:translateY(0) rotate(-2deg) scale(.96,1.08)}75%{transform:translateY(-4px) rotate(4deg) scale(1.08,.96)}}
  @keyframes mascotBarCelebrate{0%,100%{transform:translateY(0) rotate(-4deg) scale(1)}24%{transform:translateY(-8px) rotate(6deg) scale(1.16)}48%{transform:translateY(-2px) rotate(-3deg) scale(1.04)}72%{transform:translateY(-6px) rotate(4deg) scale(1.13)}}
  #floatingSessionSummary .sessionSummaryList{max-height:min(17dvh,110px)!important}
  main.cards article.card .phaseRow{grid-template-columns:minmax(0,1fr)!important;gap:.55rem!important;align-items:stretch!important}
  main.cards article.card .phaseRow>.phaseCol{min-width:0!important;width:100%!important}
  main.cards article.card .phaseRow .phaseLabel{max-width:100%!important;white-space:normal!important;word-break:normal!important;overflow-wrap:anywhere!important;line-height:1.2!important}
  main.cards article.card .phaseRow .source{min-width:0!important;max-width:100%!important;word-break:normal!important;overflow-wrap:anywhere!important;hyphens:auto}
  main.cards article.card .phaseRow .swap{justify-self:center!important;align-self:center!important;margin:.1rem 0!important;transform:rotate(90deg)!important}
}
@media(max-width:380px){#summaryToggle{grid-template-columns:auto minmax(0,1fr) 60px auto!important}#summaryToggle .summaryMascotWrap,#summaryToggle[aria-expanded="true"] .summaryMascotWrap{width:58px!important;height:58px!important}#summaryToggle #summaryActivityMascot,#summaryToggle[aria-expanded="true"] #summaryActivityMascot{width:54px!important;height:54px!important}}
@media(max-width:360px){.performanceRepsControl{grid-template-columns:40px minmax(0,1fr) 40px!important;gap:.25rem!important}.performanceRepsNudge{min-width:40px!important;min-height:44px!important}.performanceFieldTitleRow{flex-wrap:wrap!important;justify-content:flex-start!important;gap:.25rem .4rem!important}.performanceFieldLabel{flex:1 1 120px!important;flex-wrap:wrap!important}.performanceRequired{margin-left:26px!important}}
@media(prefers-reduced-motion:reduce){#floatingSessionSummary,#summaryToggle{scroll-behavior:auto!important;transition:none!important}}
</style>'''


SECTION_LOAD_REDESIGN = r'''<style data-enhancement="section-ledger-load-v2">
/* Los bloques de cada ejercicio tienen rótulos, bordes y tonos propios. */
.card .routineSectionStamp{display:flex;align-items:center;gap:.48rem;margin:.72rem 0 .45rem;padding:.38rem .55rem;border:1px solid currentColor;border-left-width:3px;border-radius:.55rem;font-size:.64rem;font-weight:950;letter-spacing:.09em;line-height:1.2}
.card .routineSectionStamp::before{content:"";width:.46rem;height:.46rem;flex:0 0 .46rem;border-radius:50%;background:currentColor;box-shadow:0 0 9px currentColor}
.card .routineSectionStamp[data-section="prescription"]{color:#75dcff;background:rgba(23,86,112,.2)}
.card .routineSectionStamp[data-section="normal-load"]{color:#65f2dd;background:rgba(15,88,78,.22)}
.card .routineSectionStamp[data-section="series"]{color:#c2a4ff;background:rgba(71,48,116,.2)}
.card .routineSectionStamp[data-section="visual"]{color:#89baff;background:rgba(41,67,125,.22)}
.card .routineSectionStamp[data-section="technique"]{color:#ffd277;background:rgba(111,77,22,.2)}
.performanceEntry{border-left:3px solid #65f2dd!important}
.performanceNormalLoad{border-color:rgba(101,242,221,.35)!important;background:linear-gradient(145deg,rgba(9,43,47,.72),rgba(5,22,34,.96))!important}
.performanceNormalLast{margin:0;padding:.25rem .1rem;color:#aef5e7;font-size:.68rem;font-weight:800;line-height:1.4}
.performanceEntry .progressionCue{padding:.45rem .55rem;border-top:1px solid rgba(114,220,255,.17)}
</style>
<script data-enhancement="section-ledger-load-v2">
(() => {
  const sectionSpec = [
    ['.metrics','01 · PRESCRIPCIÓN','prescription'],
    ['.performanceEntry','02 · CARGAS REGISTRADAS','normal-load'],
    ['.exerciseTracker','03 · CONTROL DE SERIES','series'],
    ['.phaseRow','04 · REFERENCIA VISUAL','visual'],
    ['.techAccordion','05 · TÉCNICA','technique']
  ];
  document.querySelectorAll('main.cards article.card[data-exercise-index]').forEach(card => {
    sectionSpec.forEach(([selector,label,section]) => {
      const block = card.querySelector(selector);
      if (!block || block.querySelector(':scope > .routineSectionStamp')) return;
      const stamp = document.createElement('div');
      stamp.className = 'routineSectionStamp';
      stamp.dataset.section = section;
      stamp.textContent = label;
      if (selector === '.phaseRow') block.before(stamp); else block.insertBefore(stamp, block.firstChild);
    });
    const panel = card.querySelector('.performanceEntry');
    const item = panel?.__routineItem;
    const state = panel?.__routineState;
    if (!panel || !item || !state) return;
    const exerciseId = String(item.index + 1);
    const normalField = panel.querySelector('.performanceField:has(.performanceLoad)');
    if (normalField) normalField.classList.add('performanceNormalLoad');
    const normalLast = document.createElement('p');
    normalLast.className = 'performanceNormalLast';
    normalLast.setAttribute('aria-live','polite');
    normalLast.textContent = 'Última serie normal registrada: aún no hay carga.';
    normalField?.append(normalLast);
    const formatKg = (kg, unit) => {
      const value = unit === 'lb' ? kg / 0.45359237 : kg;
      const rounded = unit === 'lb' ? Math.round(value * 10) / 10 : Math.round(value * 10) / 10;
      return `${Number.isInteger(rounded) ? rounded : rounded.toFixed(1)} ${unit}`;
    };
    const updateNormalLast = () => {
      const kg = Number(item.previousLoadKg);
      normalLast.textContent = Number.isFinite(kg)
        ? `Última serie normal registrada: ${formatKg(kg,item.performanceLoadUnit)}.`
        : 'Última serie normal registrada: aún no hay carga.';
    };
    item.updateNormalLast = updateNormalLast;
    item.performanceLoadUnitSelect?.addEventListener('change',updateNormalLast);
    updateNormalLast();
    window.gymratikSyncOccupiedCard?.(card);
  });
})();
</script>'''


SESSION_RECAP_MARKUP = '''<div class="sessionRecap" id="sessionRecap" role="group" aria-label="Resumen de la sesión">
<div class="sessionRecapHeader"><h3 class="sessionRecapTitle">Así fue tu sesión</h3><div class="sessionProgressRing" id="sessionProgressRing" role="img" aria-label="Progreso de series"><svg viewBox="0 0 80 80" aria-hidden="true"><circle class="sessionRingTrack" cx="40" cy="40" r="31"></circle><circle class="sessionRingProgress" id="sessionRingProgress" cx="40" cy="40" r="31" stroke-dasharray="194.78" stroke-dashoffset="194.78"></circle></svg><span class="sessionRingValue"><strong id="sessionRingPercent">0%</strong><small>series</small></span></div></div>
<dl class="sessionRecapGrid">
<div class="sessionRecapMetric"><dt>Series confirmadas</dt><dd id="sessionRecapSets">—</dd></div>
<div class="sessionRecapMetric"><dt>Ejercicios completos</dt><dd id="sessionRecapExercises">—</dd></div>
<div class="sessionRecapMetric"><dt>Repeticiones registradas</dt><dd id="sessionRecapReps">—</dd></div>
<div class="sessionRecapMetric"><dt>Ejercicios omitidos</dt><dd id="sessionRecapSkipped">—</dd></div>
<div class="sessionRecapMetric"><dt>Tiempo transcurrido</dt><dd id="sessionRecapDuration">—</dd></div>
</dl>
<section class="sessionMuscleViz" id="sessionMuscleViz" aria-labelledby="sessionMuscleTitle">
<div class="muscleVizHeader"><h4 id="sessionMuscleTitle">Músculos trabajados</h4></div>
<div class="muscleVizLayout">
<div class="sessionMuscleMap" id="sessionMuscleMap" role="group" aria-label="Vistas anterior y posterior de los músculos trabajados">
<figure class="muscleAnatomyFigure"><img id="sessionAnatomyAnterior" src="../../../data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp" data-upper-src="../../../data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp" data-lower-src="../../../data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp" alt="Músculos del tren superior, vista anterior" loading="lazy" decoding="async"><figcaption>Frente</figcaption></figure>
<figure class="muscleAnatomyFigure"><img id="sessionAnatomyPosterior" src="../../../data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp" data-upper-src="../../../data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp" data-lower-src="../../../data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp" alt="Músculos del tren superior, vista posterior" loading="lazy" decoding="async"><figcaption>Espalda</figcaption></figure>
</div>
<ol class="sessionMuscleRows" id="sessionMuscleRows" aria-live="polite"></ol>
</div>
</section>
<p class="sessionFunFact" id="sessionFunFact" role="status" aria-live="polite"></p>
<p class="sessionRecapFoot">Solo cuentan series confirmadas; aproximaciones, cargas y repeticiones de calentamiento permanecen aparte. El tiempo incluye descansos.</p>
</div>'''

SESSION_RECAP_HEADER_MARKUP = '''<div class="sessionRecapHeader"><h3 class="sessionRecapTitle">Así fue tu sesión</h3><div class="sessionProgressRing" id="sessionProgressRing" role="img" aria-label="Progreso de series"><svg viewBox="0 0 80 80" aria-hidden="true"><circle class="sessionRingTrack" cx="40" cy="40" r="31"></circle><circle class="sessionRingProgress" id="sessionRingProgress" cx="40" cy="40" r="31" stroke-dasharray="194.78" stroke-dashoffset="194.78"></circle></svg><span class="sessionRingValue"><strong id="sessionRingPercent">0%</strong><small>series</small></span></div></div>'''
SESSION_MUSCLE_VIZ_MARKUP = re.search(r'<section class="sessionMuscleViz".*?</section>', SESSION_RECAP_MARKUP, re.S).group(0)


SESSION_COMPLETION_UPDATE = r'''  const renderSessionRecap = complete => {
    const rows = exerciseItems.map(snapshot);
    const doneSeries = rows.reduce((sum, row) => sum + row.done, 0);
    const completedExercises = rows.filter(row => row.complete && !row.skipped).length;
    const skippedExercises = rows.filter(row => row.skipped).length;
    const recordedReps = [];
    exerciseItems.forEach(item => item.seriesKeys.forEach((key, index) => {
      if (state[key] !== true) return;
      const record = state.__performance?.[String(item.index + 1)]?.[key];
      const reps = Number(record?.reps);
      if (record && Number.isInteger(reps) && reps >= 1 && reps <= 100) recordedReps.push({ reps, exercise: item.title, setNumber: index + 1 });
    }));
    const totalReps = recordedReps.reduce((sum, record) => sum + record.reps, 0);
    const bestSet = recordedReps.reduce((best, record) => !best || record.reps > best.reps ? record : best, null);
    const setText = (id, value) => { const node = document.getElementById(id); if (node) node.textContent = String(value); };
    const timing = state.__timing || {};
    const elapsedMs = Number(timing.sessionStartedAt) > 0 && Number(timing.sessionEndedAt) >= Number(timing.sessionStartedAt)
      ? Number(timing.sessionEndedAt) - Number(timing.sessionStartedAt) : 0;
    const elapsedMinutes = Math.floor(elapsedMs / 60000);
    const elapsedHours = Math.floor(elapsedMinutes / 60);
    const duration = elapsedMs < 1000 ? '—' : elapsedHours ? `${elapsedHours} h ${elapsedMinutes % 60} min` : elapsedMinutes ? `${elapsedMinutes} min` : '<1 min';
    setText('sessionRecapSets', `${doneSeries}/${plannedSeries}`);
    setText('sessionRecapExercises', `${completedExercises}/${exerciseItems.length}`);
    setText('sessionRecapReps', totalReps ? totalReps : '—');
    setText('sessionRecapSkipped', skippedExercises);
    setText('sessionRecapDuration', duration);
    const progressRing = document.getElementById('sessionProgressRing');
    const ringProgress = document.getElementById('sessionRingProgress');
    const ringPercent = plannedSeries ? Math.round(Math.min(1, doneSeries / plannedSeries) * 100) : 0;
    if (ringProgress) ringProgress.style.strokeDashoffset = String(194.78 * (1 - ringPercent / 100));
    setText('sessionRingPercent', `${ringPercent}%`);
    if (progressRing) progressRing.setAttribute('aria-label', `${doneSeries} de ${plannedSeries} series confirmadas (${ringPercent} %) `);

    const muscleRows = document.getElementById('sessionMuscleRows');
    const muscleMap = document.getElementById('sessionMuscleMap');
    if (muscleRows && muscleMap) {
      const groupCounts = new Map();
      exerciseItems.forEach((item, index) => {
        const row = rows[index];
        if (!row) return;
        const zone = item.tracker.closest('article.card')?.querySelector('.zone')?.textContent || '';
        const groups = zone.split('·').slice(1).join('·').trim().split('+').map(group => group.trim()).filter(Boolean);
        groups.forEach(group => {
          const current = groupCounts.get(group) || { done: 0, planned: 0 };
          current.done += row.done;
          current.planned += item.seriesKeys.length;
          groupCounts.set(group, current);
        });
      });
      const normalizeMuscle = value => value.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toUpperCase();
      const entries = [...groupCounts.entries()].filter(([, count]) => count.done > 0).sort((a, b) => b[1].done - a[1].done || a[0].localeCompare(b[0], 'es'));
      let lowerFocus = 0;
      let upperFocus = 0;
      entries.forEach(([group, count]) => {
        if (/GLUTEO|CUADRICEPS|ISQUIO|ADUCTOR|ABDUCTOR|PANTORRILLA|PIERNA/.test(normalizeMuscle(group))) lowerFocus += count.done;
        else upperFocus += count.done;
      });
      const anatomyVariant = lowerFocus > upperFocus ? 'lower' : 'upper';
      muscleMap.querySelectorAll('img[data-upper-src][data-lower-src]').forEach(image => {
        const source = image.dataset[`${anatomyVariant}Src`];
        if (source && image.getAttribute('src') !== source) image.src = source;
        image.alt = `Ilustración anatómica muscular realista del tren ${anatomyVariant === 'lower' ? 'inferior' : 'superior'}, vista ${image.id.endsWith('Anterior') ? 'anterior' : 'posterior'}`;
      });
      muscleRows.replaceChildren();
      if (!entries.length) {
        const empty = document.createElement('li');
        empty.className = 'sessionMuscleEmpty';
        empty.textContent = 'Aún no hay series confirmadas para mostrar.';
        muscleRows.append(empty);
      } else entries.forEach(([group, count], index) => {
        const row = document.createElement('li');
        row.className = 'sessionMuscleRow';
        row.style.animationDelay = `${Math.min(index, 8) * 45}ms`;
        row.dataset.muscleRegion = lowerFocus > upperFocus ? 'lower' : 'upper';
        const label = document.createElement('span');
        label.className = 'sessionMuscleRowLabel';
        label.textContent = group;
        const value = document.createElement('strong');
        value.className = 'sessionMuscleRowCount';
        value.textContent = `${count.done}/${count.planned} series`;
        const bar = document.createElement('span');
        bar.className = 'sessionMuscleBar';
        bar.setAttribute('role', 'progressbar');
        bar.setAttribute('aria-label', `Series de ${group}`);
        bar.setAttribute('aria-valuemin', '0');
        bar.setAttribute('aria-valuemax', String(count.planned));
        bar.setAttribute('aria-valuenow', String(count.done));
        bar.setAttribute('aria-valuetext', `${count.done} de ${count.planned} series`);
        const fill = document.createElement('span');
        fill.style.width = `${Math.round(Math.min(1, count.done / Math.max(1, count.planned)) * 100)}%`;
        bar.append(fill);
        row.append(label, value, bar);
        muscleRows.append(row);
      });
    }
    const kicker = completionPanel.querySelector('.sessionCompletionKicker');
    const title = document.getElementById('session-completion-title');
    if (kicker) kicker.textContent = complete ? 'RUTINA COMPLETADA · GUARDADO AUTOMÁTICO' : 'SESIÓN GUARDADA · PROGRESO PARCIAL';
    if (title) title.textContent = complete ? '¡Día completo!' : 'Buen trabajo. Día guardado.';
    const fact = bestSet
      ? `Dato curioso: tu serie con más repeticiones fue de ${bestSet.reps} en ${bestSet.exercise} · serie ${bestSet.setNumber}.`
      : doneSeries
        ? `Dato curioso: confirmaste ${doneSeries} de ${plannedSeries} series (${Math.round(doneSeries / Math.max(1, plannedSeries) * 100)} % del plan).`
        : 'Dato curioso: cerraste el día sin series confirmadas; las aproximaciones no cuentan como series de trabajo.';
    setText('sessionFunFact', fact);
  };
  const updateSessionCompletion = (celebrate = false) => {
    const rows = exerciseItems.map(snapshot);
    const complete = rows.length > 0 && rows.every(row => row.complete && !row.skipped);
    const partial = !complete && state.__timing?.sessionEndReason === 'partial' && Number(state.__timing?.sessionEndedAt) > 0;
    if (!complete && !partial) { completionPanel.hidden = true; completionPanel.classList.remove('isPartial'); return; }
    if (summaryToggle && summaryBody) { summaryToggle.setAttribute('aria-expanded', 'false'); summaryBody.hidden = true; }
    renderSessionRecap(complete);
    completionPanel.classList.toggle('isPartial', partial);
    completionPanel.dataset.completionKind = complete ? 'complete' : 'partial';
    if (!completionPanel.dataset.quoteShown) { showMotivation(); completionPanel.dataset.quoteShown = 'true'; }
    completionPanel.hidden = false;
    const doneSeries = exerciseItems.reduce((sum, item) => sum + snapshot(item).done, 0);
    const celebrationKey = `${completionPanel.dataset.completionKind}:${Number(state.__timing?.sessionEndedAt) || doneSeries}`;
    if (celebrate && completionPanel.dataset.celebrationKey !== celebrationKey) {
      completionPanel.dataset.celebrationKey = celebrationKey;
      playFeedback('session');
      completionPanel.classList.remove('sessionCelebrating');
      void completionPanel.offsetWidth;
      completionPanel.classList.add('sessionCelebrating');
      window.setTimeout(() => completionPanel.classList.remove('sessionCelebrating'), 1800);
      window.setTimeout(() => completionPanel.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth', block: 'center' }), 120);
    }
  };'''


def apply_interaction_redesign(source: str) -> str:
    if './page-update-client.js' not in source:
        source = source.replace('</head>', '  <script src="../../../page-update-client.js" defer></script>\n</head>', 1)
    source = source.replace(
        'const activityText = `${displayActivity.label} · ${displayActivity.clock}`;',
        "const compactActivityLabels = { rest: 'Descanso', ready: 'Descanso listo', approximation: 'Aproximación', preparing: 'Preparación', strength: displayActivity.label.split(' · ')[0], cardio: 'Calentamiento · cardio', mobility: 'Calentamiento · movilidad', complete: 'Rutina completada', start: 'Listo para iniciar' };\n      const activityText = `${compactActivityLabels[displayActivity.kind] || 'Sesión activa'} · ${displayActivity.clock}`;",
    )
    source = source.replace(
        '      block.insertBefore(stamp, block.firstChild);',
        "      if (selector === '.phaseRow') block.before(stamp); else block.insertBefore(stamp, block.firstChild);",
    )
    for previous in ("exercise-focus-occupied-quote-v2", "exercise-focus-occupied-quote-v3", "exercise-focus-occupied-quote-v4", "exercise-focus-occupied-quote-v5", "exercise-focus-occupied-quote-v6", "exercise-focus-occupied-quote-v7", "exercise-focus-occupied-quote-v8", "section-ledger-load-v1", "section-ledger-load-v2"):
        source = re.sub(
            rf'<style\s+data-enhancement="{re.escape(previous)}">.*?</script>',
            "",
            source,
            count=1,
            flags=re.I | re.S,
        )
    source = re.sub(r'(<meta\b(?=[^>]*\bname=["\']viewport["\'])[^>]*\bcontent=["\'])([^"\']*)(["\'][^>]*>)', lambda m: m.group(1) + re.sub(r',?\s*(?:maximum-scale|user-scalable)=[^,]+', '', m.group(2)) + ', maximum-scale=1, user-scalable=no' + m.group(3), source, count=1, flags=re.I)
    if 'data-enhancement="exercise-focus-occupied-quote-v8"' not in source:
        source = source.replace('</body>', INTERACTION_REDESIGN + '\n</body>', 1)
    if 'performancePanel.__routineItem = item;' not in source:
        source = source.replace(
            'item.performancePanel = performancePanel;',
            'item.performancePanel = performancePanel; performancePanel.__routineItem = item; performancePanel.__routineState = state; performancePanel.__persistRoutineState = save;',
        )
    source = re.sub(
        r'(item\.performancePanel = performancePanel;)(?:\s*performancePanel\.__routineItem = item; performancePanel\.__routineState = state; performancePanel\.__persistRoutineState = save;)+',
        r'\1 performancePanel.__routineItem = item; performancePanel.__routineState = state; performancePanel.__persistRoutineState = save;',
        source,
    )
    if 'item.warmupLoadExact' not in source:
        source = source.replace(
            'const load = Number(item.performanceLoadExact);\n        const loadSelected = item.performanceLoadSelected && Number.isFinite(load) && load >= Number(item.performanceLoad?.min) && load <= Number(item.performanceLoad?.max);',
            'const load = Number(item.warmupLoadExact);\n        const warmupLoadUnit = item.warmupLoadUnit === \'lb\' ? \'lb\' : \'kg\';\n        const warmupLoadKg = warmupLoadUnit === \'lb\' ? load * 0.45359237 : load;\n        const loadSelected = item.warmupLoadSelected && Number.isFinite(warmupLoadKg) && warmupLoadKg >= item.performanceLoadProfile.minKg && warmupLoadKg <= item.performanceLoadProfile.maxKg;',
        )
        source = source.replace(
            'loadUnit: item.performanceLoadUnit, loadKg: loadSelected ? (item.performanceLoadUnit === \'lb\' ? load * 0.45359237 : load) : null,',
            'loadUnit: warmupLoadUnit, loadKg: loadSelected ? warmupLoadKg : null,',
        )
        source = source.replace(
            'completedAt };\n        timing.warmupStartedAt',
            'completedAt };\n        item.updateWarmupLast?.();\n        timing.warmupStartedAt',
        )
    source = source.replace(
        'if (Number.isFinite(storedKg)) item.previousLoadKg = storedKg;',
        'if (Number.isFinite(storedKg)) { item.previousLoadKg = storedKg; item.updateNormalLast?.(); }',
    )
    source = re.sub(
        r'(?m)^(\s*if \(Number\.isFinite\(storedKg\)\) \{ item\.previousLoadKg = storedKg; item\.updateNormalLast\?\.\(\); \})(?: item\.updateNormalLast\?\.\(\);)+[ \t]*$',
        r'\1',
        source,
    )
    source = source.replace(
        'item.previousLoadKg = loadKg;\n      } else if (load !== null) item.previousLoadKg = loadKg;',
        'item.previousLoadKg = loadKg; item.updateNormalLast?.();\n      } else if (load !== null) { item.previousLoadKg = loadKg; item.updateNormalLast?.(); }',
    )
    source = re.sub(
        r'(item\.updateNormalLast\?\.\(\);)(?:\s*item\.updateNormalLast\?\.\(\);)+',
        r'\1',
        source,
    )
    section_ledger_pattern = r'<style data-enhancement="section-ledger-load-v2">.*?</style>\s*<script data-enhancement="section-ledger-load-v2">.*?</script>'
    if re.search(section_ledger_pattern, source, flags=re.S):
        source = re.sub(section_ledger_pattern, lambda _: SECTION_LOAD_REDESIGN, source, count=1, flags=re.S)
    else:
        source = source.replace('</body>', SECTION_LOAD_REDESIGN + '\n</body>', 1)
    if 'id="sessionRecap"' not in source:
        source, inserted = re.subn(
            r'(<a class="motivationNote" id="motivationNote"[^>]*></a>)(</div>)',
            lambda match: match.group(1) + SESSION_RECAP_MARKUP + match.group(2),
            source,
            count=1,
        )
        if inserted != 1:
            raise ValueError("No se encontró el punto de inserción del resumen de sesión")
    if 'id="sessionProgressRing"' not in source:
        source, header_updated = re.subn(
            r'<h3 class="sessionRecapTitle">.*?</h3>',
            lambda _: SESSION_RECAP_HEADER_MARKUP,
            source,
            count=1,
            flags=re.S,
        )
        if header_updated != 1:
            raise ValueError("No se encontró el título del resumen para instalar el anillo de progreso")
    if 'id="sessionMuscleViz"' in source and any(phrase in source for phrase in ("Ilustración anatómica educativa", "PULSO ILUSTRATIVO", "Series confirmadas por zona")):
        source, muscle_viz_replaced = re.subn(
            r'<section class="sessionMuscleViz".*?</section>',
            lambda _: SESSION_MUSCLE_VIZ_MARKUP,
            source,
            count=1,
            flags=re.S,
        )
        if muscle_viz_replaced != 1:
            raise ValueError("No se encontró el mapa muscular anterior para reemplazarlo por ilustraciones anatómicas")
    elif 'id="sessionMuscleViz"' not in source:
        source, muscle_viz_inserted = re.subn(
            r'(</dl>)(\s*)(<p class="sessionFunFact")',
            lambda match: match.group(1) + '\n' + SESSION_MUSCLE_VIZ_MARKUP + '\n' + match.group(3),
            source,
            count=1,
        )
        if muscle_viz_inserted != 1:
            raise ValueError("No se encontró el resumen de sesión para insertar el mapa muscular")
    source, recap_functions = re.subn(
        r'  const renderSessionRecap = complete => \{.*?(?=\n  const updateTracker = \(tracker, celebrate = false\) => \{)',
        SESSION_COMPLETION_UPDATE,
        source,
        count=1,
        flags=re.S,
    )
    if recap_functions != 1:
        raise ValueError("No se encontró el actualizador del panel de fin de sesión")
    source = source.replace(
        """      const finishDayButton = document.getElementById('finishDay');
      if (finishDayButton) {
        finishDayButton.disabled = Boolean(root?.sessionEndedAt);
        finishDayButton.textContent = root?.sessionEndedAt ? 'Día terminado' : 'Terminar día';
      }""",
        """      const finishDayButton = document.getElementById('finishDay');
      if (finishDayButton) {
        const canRetryPartialSave = root?.sessionEndReason === 'partial' && finishDayButton.dataset.saveFailed === 'true';
        finishDayButton.disabled = Boolean(root?.sessionEndedAt) && !canRetryPartialSave;
        finishDayButton.textContent = canRetryPartialSave ? 'Reintentar guardado' : root?.sessionEndedAt ? (root.sessionEndReason === 'partial' ? 'Sesión parcial guardada' : 'Rutina guardada') : 'Cerrar sesión parcial (opcional)';
      }""",
    )
    source = source.replace(
        """        const canRetryPartialSave = root?.sessionEndReason === 'partial' && finishDayButton.dataset.saveFailed === 'true';
        finishDayButton.disabled = Boolean(root?.sessionEndedAt) && !canRetryPartialSave;
        finishDayButton.textContent = canRetryPartialSave ? 'Reintentar guardado' : root?.sessionEndedAt ? 'Día terminado' : 'Terminar día';""",
        """        const canRetryPartialSave = root?.sessionEndReason === 'partial' && finishDayButton.dataset.saveFailed === 'true';
        finishDayButton.disabled = Boolean(root?.sessionEndedAt) && !canRetryPartialSave;
        finishDayButton.textContent = canRetryPartialSave ? 'Reintentar guardado' : root?.sessionEndedAt ? (root.sessionEndReason === 'partial' ? 'Sesión parcial guardada' : 'Rutina guardada') : 'Cerrar sesión parcial (opcional)';""",
    )
    finish_handler = r'''  document.addEventListener('click', async event => {
    const finishDayButton = event.target instanceof Element ? event.target.closest('#finishDay') : null;
    const isRetry = state.__timing?.sessionEndReason === 'partial' && Number(state.__timing?.sessionEndedAt) > 0;
    if (!finishDayButton || (state.__timing?.sessionEndedAt && !isRetry)) return;
    if (!isRetry && !window.confirm('Tu progreso se guarda automáticamente al confirmar cada serie. ¿Quieres cerrar ahora esta sesión parcial y registrar su hora de cierre?')) return;
    finishDayButton.disabled = true;
    finishDayButton.textContent = 'Guardando…';
    clearPreparationTimers();
    const timingRoot = getTimingState();
    const endedAt = Number(timingRoot.sessionEndedAt) || Date.now();
    if (!timingRoot.sessionStartedAt) timingRoot.sessionStartedAt = endedAt;
    timingRoot.sessionEndedAt = endedAt;
    timingRoot.sessionEndReason = 'partial';
    Object.values(timingRoot.exercises || {}).forEach(timing => {
      timing.preparationEndsAt = 0;
      timing.seriesStartedAt = 0;
      timing.restStartedAt = 0;
      timing.restNotifiedAt = 0;
      timing.restReminderNotifiedAt = 0;
    });
    if (timingRoot.warmup?.phase === 'preparing') timingRoot.warmup.phase = 'paused';
    let saved;
    try { saved = await save(); }
    catch (error) { window.dispatchEvent(new CustomEvent('training-storage-error', { detail: { error } })); }
    if (!saved?.source) {
      finishDayButton.disabled = false;
      finishDayButton.dataset.saveFailed = 'true';
      finishDayButton.textContent = 'Reintentar guardado';
      finishDayButton.setAttribute('aria-label', 'No se confirmó el guardado. Pulsa para reintentar.');
      window.dispatchEvent(new CustomEvent('training-storage-error', { detail: { message: 'El cierre parcial no pudo confirmarse en el almacén local.' } }));
      return;
    }
    delete finishDayButton.dataset.saveFailed;
    finishDayButton.textContent = 'Día terminado';
    finishDayButton.setAttribute('aria-label', 'Cierre parcial guardado. El progreso se guarda automáticamente.');
    exerciseItems.forEach(item => updateTracker(item.tracker, false));
    updateSessionCompletion(true);
  });'''
    source, finish_handlers = re.subn(
        r"  document\.addEventListener\('click', async event => \{\s*const finishDayButton.*?\n  \}\);",
        finish_handler,
        source,
        count=1,
        flags=re.S,
    )
    if finish_handlers != 1:
        raise ValueError("No se encontró el controlador del botón Terminar día")
    source = source.replace(
        "if (exerciseItems.every(entry => snapshot(entry).complete) && !root.sessionEndedAt) root.sessionEndedAt = timestamp;",
        "if (exerciseItems.every(entry => snapshot(entry).complete) && !root.sessionEndedAt) { root.sessionEndedAt = timestamp; root.sessionEndReason = Object.values(state.__skippedExercises || {}).some(Boolean) ? 'partial' : 'complete'; }",
    )
    source = source.replace(
        "if (exerciseItems.every(entry => snapshot(entry).complete || entry === item)) getTimingState().sessionEndedAt = timestamp;\n      save(); updateTracker(item.tracker, false);",
        "if (exerciseItems.every(entry => snapshot(entry).complete || entry === item)) { const root = getTimingState(); root.sessionEndedAt = timestamp; root.sessionEndReason = 'partial'; }\n      save(); updateTracker(item.tracker, exerciseItems.every(entry => snapshot(entry).complete || entry === item));",
    )
    source, footers = re.subn(
        r'<div class="sessionResetCopy"><strong>.*?</strong><span>.*?</span></div><button type="button" id="finishDay">.*?</button>',
        '<div class="sessionResetCopy"><strong>El progreso se guarda automáticamente</strong><span>Cada serie confirmada se guarda al instante; no necesitas cerrar el día para conservarla. Si terminas antes de completar la rutina, puedes registrar el cierre parcial aquí.</span></div><button type="button" id="finishDay">Cerrar sesión parcial (opcional)</button>',
        source,
        count=1,
        flags=re.S,
    )
    if footers != 1:
        raise ValueError("No se encontró el pie de acciones para explicar el guardado automático")
    source = source.replace(
        "    state = {};\n    save();",
        "    state = {};\n    delete document.getElementById('finishDay')?.dataset.saveFailed;\n    save();",
        1,
    )
    source = re.sub(r'\n{3,}(?=<style data-enhancement="exercise-focus-occupied-quote-v8">)', '\n\n', source)
    if 'data-enhancement="mobile-summary-layout-v1"' not in source:
        source = source.replace('</body>', MOBILE_SUMMARY_REDESIGN + '\n</body>', 1)
    else:
        source = re.sub(
            r'<style data-enhancement="mobile-summary-layout-v1">.*?</style>',
            lambda _: MOBILE_SUMMARY_REDESIGN,
            source,
            count=1,
            flags=re.S,
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
        updated = apply_interaction_redesign(updated)
        updated = standardize_quote_portrait_loading(updated)
        updated = apply_warmup_load_selector_contract(updated)
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
