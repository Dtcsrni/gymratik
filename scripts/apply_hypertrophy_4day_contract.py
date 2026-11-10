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


INTERACTION_REDESIGN = r'''<style data-enhancement="exercise-focus-occupied-quote-v4">
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
@keyframes exerciseFocusReveal{from{opacity:.4;transform:translateY(4px) scale(.98)}to{opacity:1;transform:none}}
@keyframes exerciseBarPulse{from{filter:brightness(1)}to{filter:brightness(1.22)}}
@media(max-width:640px){.floatingSessionSummary .summaryFocusBadge{font-size:.55rem}.sessionCompletionCopy p#motivationMessage{padding:.75rem .8rem .75rem 1.05rem}}
@media(prefers-reduced-motion:reduce){.floatingSessionSummary.is-exercise-focused .summaryFocusBadge,.floatingSessionSummary.is-exercise-focused .summaryToggle,.summaryExercise.isCurrent{animation:none!important}main.cards article.card[data-exercise-index]{transition:none}}
</style>
<script data-enhancement="exercise-focus-occupied-quote-v4">
(() => {
  const cards = [...document.querySelectorAll('main.cards article.card[data-exercise-index]')];
  const summary = document.querySelector('.floatingSessionSummary');
  const toggle = document.getElementById('summaryToggle');
  if (!cards.length || !summary || !toggle) return;
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
.performanceWarmupLoad{display:grid;gap:.4rem;margin:.55rem 0;padding:.62rem;border:1px solid rgba(255,209,102,.55);border-left:3px solid #ffd166;border-radius:.78rem;background:linear-gradient(145deg,rgba(81,60,22,.5),rgba(27,27,22,.72))}
.performanceWarmupLoadHead{display:flex;align-items:center;justify-content:space-between;gap:.55rem;color:#ffe5a4;font-size:.76rem;font-weight:950}
.performanceWarmupLoadHead label{display:flex;align-items:center;gap:.4rem;min-width:0}
.performanceWarmupLoadHead label::before{content:"A";display:grid;place-items:center;width:1.35rem;height:1.35rem;flex:none;border:1px solid rgba(255,209,102,.68);border-radius:.38rem;background:rgba(132,91,20,.48);color:#fff0bf;font-size:.7rem}
.performanceWarmupLoadControls{display:grid;grid-template-columns:minmax(0,1fr) 4.2rem auto;align-items:center;gap:.4rem}
.performanceWarmupLoadInput{width:100%;min-width:0;min-height:44px;padding:.45rem .55rem;border:1px solid rgba(255,209,102,.55);border-radius:.58rem;background:rgba(9,23,31,.92);color:#fff4d3;font:inherit;font-size:1rem;font-weight:900;text-align:center;font-variant-numeric:tabular-nums}
.performanceWarmupLoadUnit{min-height:44px;padding:.3rem;border:1px solid rgba(255,209,102,.45);border-radius:.55rem;background:#211d12;color:#fff0bf;font:inherit;font-weight:850}
.performanceWarmupClear{min-height:44px;padding:.3rem .5rem;border:1px solid rgba(255,209,102,.4);border-radius:.52rem;background:rgba(91,65,20,.35);color:#ffe5a4;font:inherit;font-size:.65rem;font-weight:850}
.performanceWarmupLast,.performanceNormalLast{margin:0;color:#c1d8df;font-size:.68rem;font-weight:800;line-height:1.4}
.performanceWarmupLast{color:#ffe5a4}.performanceNormalLast{padding:.25rem .1rem;color:#aef5e7}
.performanceEntry .progressionCue{padding:.45rem .55rem;border-top:1px solid rgba(114,220,255,.17)}
@media(max-width:400px){.performanceWarmupLoadControls{grid-template-columns:minmax(0,1fr) 3.4rem}.performanceWarmupClear{grid-column:1/-1;min-height:38px}}
@media(prefers-reduced-motion:reduce){.performanceWarmupLoadInput{transition:none}}
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
      block.insertBefore(stamp, block.firstChild);
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
    const warmup = document.createElement('section');
    warmup.className = 'performanceWarmupLoad';
    const head = document.createElement('div'); head.className = 'performanceWarmupLoadHead';
    const label = document.createElement('label'); label.htmlFor = `warmup-load-${card.dataset.exerciseIndex}`; label.textContent = 'Peso de aproximación';
    const required = document.createElement('span'); required.textContent = 'APARTE'; head.append(label,required);
    const controls = document.createElement('div'); controls.className = 'performanceWarmupLoadControls';
    const input = document.createElement('input'); input.id = label.htmlFor; input.type = 'number'; input.inputMode = 'decimal'; input.step = '0.1'; input.min = '0'; input.max = String(item.performanceLoadProfile.maxKg); input.className = 'performanceWarmupLoadInput'; input.setAttribute('aria-label',`Peso de aproximación en ${item.title}`); input.placeholder = 'Sin registrar';
    const unit = document.createElement('select'); unit.className = 'performanceWarmupLoadUnit'; unit.setAttribute('aria-label',`Unidad del peso de aproximación en ${item.title}`);
    [['kg','kg'],['lb','lb']].forEach(([value,text]) => { const option = document.createElement('option'); option.value = value; option.textContent = text; unit.append(option); });
    const clear = document.createElement('button'); clear.type='button'; clear.className='performanceWarmupClear'; clear.textContent='Limpiar'; clear.setAttribute('aria-label',`Limpiar peso de aproximación de ${item.title}`);
    controls.append(input,unit,clear);
    const last = document.createElement('p'); last.className='performanceWarmupLast'; last.setAttribute('aria-live','polite');
    warmup.append(head,controls,last);
    const cue = panel.querySelector('.progressionCue');
    panel.insertBefore(warmup,cue || null);
    const warmupStored = state.__warmupPerformance?.[exerciseId];
    const draft = state.__warmupDraft?.[exerciseId];
    const initial = draft || warmupStored || {};
    let warmupUnit = initial.loadUnit === 'lb' ? 'lb' : item.performanceLoadUnit;
    let warmupSelected = initial.loadSelected === true || (initial.loadSelected !== false && initial.load !== null && initial.load !== undefined && Number(initial.load) > 0);
    let warmupExact = Number(initial.load) || 0;
    unit.value = warmupUnit;
    if (warmupSelected) input.value = String(warmupExact);
    const toKg = (value, units) => units === 'lb' ? value * 0.45359237 : value;
    const syncWarmupBounds = () => {
      const factor = warmupUnit === 'lb' ? 1 / 0.45359237 : 1;
      input.min = String(Math.max(0,item.performanceLoadProfile.minKg * factor));
      input.max = String(item.performanceLoadProfile.maxKg * factor);
      input.step = warmupUnit === 'lb' ? '0.1' : String(item.performanceLoadProfile.stepKg);
      input.setAttribute('aria-label',`Peso de aproximación en ${warmupUnit} para ${item.title}`);
    };
    const updateWarmupLast = () => {
      const saved = state.__warmupPerformance?.[exerciseId];
      const draftValue = state.__warmupDraft?.[exerciseId];
      const kg = saved?.loadKg == null ? (saved?.load == null ? NaN : toKg(Number(saved.load),saved.loadUnit === 'lb' ? 'lb' : 'kg')) : Number(saved.loadKg);
      const draftKg = draftValue?.loadKg == null ? (draftValue?.load == null ? NaN : toKg(Number(draftValue.load),draftValue.loadUnit === 'lb' ? 'lb' : 'kg')) : Number(draftValue.loadKg);
      last.textContent = Number.isFinite(kg)
        ? `Última aproximación registrada: ${formatKg(kg,warmupUnit)} · no cuenta como serie normal.`
        : Number.isFinite(draftKg)
          ? `Carga preparada para aproximación: ${formatKg(draftKg,warmupUnit)} · se guarda aparte al completar.`
          : 'Peso de aproximación sin registrar; no se mezclará con la carga normal.';
    };
    const persistWarmupDraft = () => {
      const value = Number(input.value);
      warmupUnit = unit.value === 'lb' ? 'lb' : 'kg';
      warmupExact = value;
      const valueKg = toKg(value,warmupUnit);
      warmupSelected = input.value.trim() !== '' && Number.isFinite(valueKg) && valueKg >= item.performanceLoadProfile.minKg && valueKg <= item.performanceLoadProfile.maxKg;
      item.warmupLoadUnit = warmupUnit;
      item.warmupLoadExact = value;
      item.warmupLoadSelected = warmupSelected;
      state.__warmupDraft ||= {};
      state.__warmupDraft[exerciseId] = {load:warmupSelected ? value : null,loadUnit:warmupUnit,loadKg:warmupSelected ? valueKg : null,loadSelected:warmupSelected};
      panel.__persistRoutineState?.();
      updateWarmupLast();
    };
    item.warmupLoadUnitSelect = unit;
    item.warmupLoadInput = input;
    item.warmupLoadExact = warmupExact;
    item.warmupLoadUnit = warmupUnit;
    item.warmupLoadSelected = warmupSelected;
    syncWarmupBounds();
    input.addEventListener('input',persistWarmupDraft);
    unit.addEventListener('change',() => {
      const oldKg = warmupSelected ? toKg(Number(input.value),warmupUnit) : NaN;
      warmupUnit = unit.value === 'lb' ? 'lb' : 'kg';
      syncWarmupBounds();
      if (Number.isFinite(oldKg)) input.value = String(Math.round(toKg(oldKg,warmupUnit)*10)/10);
      persistWarmupDraft();
    });
    clear.addEventListener('click',() => { input.value=''; persistWarmupDraft(); });
    item.updateWarmupLast = updateWarmupLast;
    updateWarmupLast();
    window.gymratikSyncOccupiedCard?.(card);
  });
})();
</script>'''


def apply_interaction_redesign(source: str) -> str:
    for previous in ("exercise-focus-occupied-quote-v2", "exercise-focus-occupied-quote-v3", "section-ledger-load-v1"):
        source = re.sub(
            rf'<style\s+data-enhancement="{re.escape(previous)}">.*?</script>',
            "",
            source,
            count=1,
            flags=re.I | re.S,
        )
    source = re.sub(r'(<meta\b(?=[^>]*\bname=["\']viewport["\'])[^>]*\bcontent=["\'])([^"\']*)(["\'][^>]*>)', lambda m: m.group(1) + re.sub(r',?\s*(?:maximum-scale|user-scalable)=[^,]+', '', m.group(2)) + ', maximum-scale=1, user-scalable=no' + m.group(3), source, count=1, flags=re.I)
    if 'data-enhancement="exercise-focus-occupied-quote-v4"' not in source:
        source = source.replace('</body>', INTERACTION_REDESIGN + '\n</body>', 1)
    source = source.replace(
        'item.performancePanel = performancePanel;',
        'item.performancePanel = performancePanel; performancePanel.__routineItem = item; performancePanel.__routineState = state; performancePanel.__persistRoutineState = save;',
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
        'if (Number.isFinite(storedKg)) item.previousLoadKg = storedKg; item.updateNormalLast?.();',
    )
    source = source.replace(
        'item.previousLoadKg = loadKg;\n      } else if (load !== null) item.previousLoadKg = loadKg;',
        'item.previousLoadKg = loadKg; item.updateNormalLast?.();\n      } else if (load !== null) { item.previousLoadKg = loadKg; item.updateNormalLast?.(); }',
    )
    if 'data-enhancement="section-ledger-load-v2"' not in source:
        source = source.replace('</body>', SECTION_LOAD_REDESIGN + '\n</body>', 1)
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
