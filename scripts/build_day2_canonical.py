from __future__ import annotations

import re
from pathlib import Path

from standardize_muscle_visuals import sanitize_canonical_metadata, standardize_muscle_visuals


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html"
SOURCE = ROOT / "data/rutinas_autocontenidas/fuentes_locales/Rutina_Dia_2_Pierna_Gluteo_Autocontenida_v6_mejoras_integradas.html"
OUTPUT = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html"


def between(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    return text[start_index:end_index]


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"No se encontró el fragmento esperado: {old[:80]!r}")
    return text.replace(old, new, 1)


def build_header(day1_header: str) -> str:
    header = day1_header
    replacements = {
        "DÍA 1 · TIRÓN: ESPALDA Y BÍCEPS": "DÍA 2 · PIERNA: CUÁDRICEPS Y GLÚTEOS",
        "Tirones verticales y remos · deltoides posterior · bíceps · pecho complementario":
            "Patrón de sentadilla · extensión de cadera · flexión y extensión de rodilla · pantorrilla",
        "Tren superior": "Tren inferior",
        "Máquinas + fotos reales": "Máquinas + implementos · guía visual",
        "Perfil intermedio. Tren inferior con prioridad en espalda y bíceps; deltoides posterior y pecho complementarios.":
            "Perfil intermedio. Tren inferior con prioridad en cuádriceps y glúteo; isquiosurales y pantorrilla reciben trabajo específico.",
        "Perfil intermedio. Tren superior con prioridad en espalda y bíceps; deltoides posterior y pecho complementarios.":
            "Perfil intermedio. Tren inferior con prioridad en cuádriceps y glúteo; isquiosurales y pantorrilla reciben trabajo específico.",
    }
    for old, new in replacements.items():
        header = header.replace(old, new)
    header = re.sub(
        r'(<div class="subtitle">).*?(</div>)',
        r'\1Patrón de sentadilla · extensión de cadera · flexión y extensión de rodilla · pantorrilla\2',
        header,
        count=1,
        flags=re.S,
    )
    header = re.sub(
        r'(<div class="heroSummaryText">).*?(</div>)',
        r'\1Rutina de <b>tren inferior</b> con prioridad en cuádriceps y glúteo; isquiosurales y pantorrilla reciben trabajo específico.\2',
        header,
        count=1,
        flags=re.S,
    )
    header = re.sub(
        r'(<div class="heroSummaryText"><b>Perfil intermedio\.</b> ).*?(</div>)',
        r'\1Tren inferior con prioridad en cuádriceps y glúteo; isquiosurales y pantorrilla reciben trabajo específico.\2',
        header,
        count=1,
        flags=re.S,
    )

    old_grid = re.search(r'<div class="muscleDayGrid"[^>]*>.*?</div>\s*</div></div>', header, re.S)
    if not old_grid:
        raise ValueError("No se encontró la cuadrícula muscular de la cabecera")
    new_grid = '''<div class="muscleDayGrid">
<div class="muscleDayItem" data-muscle-visual="lower-anterior"><span class="muscleDayVisual lower anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior del muslo" decoding="async" fetchpriority="high"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#64d7ff">CUÁDRI</span><span class="muscleName">Cuádriceps</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-posterior"><span class="muscleDayVisual lower"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa posterior de la cadera" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#64d7ff">GLÚTEO</span><span class="muscleName">Glúteo mayor</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-posterior"><span class="muscleDayVisual lower"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa posterior del muslo" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#64d7ff">ISQUIO</span><span class="muscleName">Isquiosurales</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-anterior"><span class="muscleDayVisual lower anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior del muslo y la cadera" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#64d7ff">ADUCT</span><span class="muscleName">Aductores</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-posterior"><span class="muscleDayVisual lower"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa posterior de la pantorrilla" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#64d7ff">GASTRO</span><span class="muscleName">Gastrocnemio</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-posterior"><span class="muscleDayVisual lower"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa posterior de la pantorrilla" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#64d7ff">SÓLEO</span><span class="muscleName">Sóleo</span></span></div>
</div>
</div></div>'''
    return header[: old_grid.start()] + new_grid + header[old_grid.end() :]


def build_quick_rules(day1_rules: str) -> str:
    rules = day1_rules
    replacements = {
        "Reglas clave de la sesión": "Reglas clave de la sesión",
        '<h3>Ritmo</h3><p><strong class="timeCue">1–2 s</strong> al tirar · <strong class="timeCue">2–3 s</strong> al regresar · sin rebotes.</p>':
            "<h3>Ritmo</h3><p><strong class=\"timeCue\">1–2 s</strong> al esfuerzo · <strong class=\"timeCue\">2–3 s</strong> al regresar · pausa breve arriba cuando corresponda.</p>",
        "RIR (repeticiones en reserva): compuestos 2–3 al inicio y 1–2 al final; aislamientos 1–2. No sacrifiques técnica.":
            "RIR (repeticiones en reserva): compuestos 2–3 al inicio y 1–2 al final; aislamientos 1–2. No sacrifiques apoyo ni alineación.",
        "Si cae la postura, descansa más o reduce carga; ante dolor agudo, detén y reajusta.":
            "Si pierdes apoyo, alineación o control pélvico, descansa más o reduce carga; ante dolor agudo, detén y reajusta.",
    }
    for old, new in replacements.items():
        rules = rules.replace(old, new)
    return rules


def build_warmup(template: str) -> str:
    tracker_match = re.search(
        r'(<div class="warmupTracker" id="warmupTracker".*?</div>)\s*</div>\s*</section><section class="routineSummary"',
        template,
        flags=re.S,
    )
    if not tracker_match:
        raise ValueError("No se encontró el seguimiento del calentamiento del template")
    tracker = tracker_match.group(1)
    return f'''<section class="warmupGuide" data-fix="day2-warmup-guide" aria-labelledby="warmup-title">
  <div class="warmupHead">
    <div>
      <div class="warmupKicker"><span class="warmupKickerIcon"><svg aria-hidden="true" viewBox="0 0 64 64"><path d="M5 34h12l6-15 9 30 7-21 5 6h15" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="5"></path></svg></span>ANTES DE LOS EJERCICIOS</div>
      <h2 id="warmup-title">Calentamiento · <strong class="timeCue">8–13 min</strong></h2>
      <p>Eleva la temperatura y prepara cadera, rodilla y tobillo sin fatigar la pierna antes de las series efectivas.</p>
    </div>
  </div>
  <div class="warmupSteps">
    <article class="warmupStep cardio">
      <div class="warmupMedia warmupMediaStrip warmupTextStrip" role="list" aria-label="Opciones de cardio suave">
        <div class="warmupVisual warmupMotionCard" role="listitem"><img class="warmupMotionGif warmupGif" src="../medios_publicados/ejercicios-compartido/videos/2141-rjtuP6X.gif" alt="GIF de caminata en elíptica con movimiento continuo y ritmo suave" loading="lazy"/><img class="warmupFallback" src="../medios_publicados/ejercicios-compartido/images/2141-rjtuP6X.jpg" alt="" aria-hidden="true" hidden/><span class="warmupMediaLabel">ELÍPTICA</span></div>
        <div class="warmupVisual warmupMotionCard" role="listitem"><img class="warmupMotionGif warmupGif" src="../medios_publicados/ejercicios-compartido/videos/0798-a8VDgLw.gif" alt="GIF de pedaleo suave en bicicleta fija" loading="lazy"/><img class="warmupFallback" src="../medios_publicados/ejercicios-compartido/images/0798-a8VDgLw.jpg" alt="" aria-hidden="true" hidden/><span class="warmupMediaLabel">BICI</span></div>
        <div class="warmupVisual warmupMotionCard" role="listitem"><img class="warmupMotionGif warmupGif" src="../medios_publicados/ejercicios-compartido/videos/3666-rjiM4L3.gif" alt="GIF de caminata en caminadora inclinada a ritmo suave" loading="lazy"/><img class="warmupFallback" src="../medios_publicados/ejercicios-compartido/images/3666-rjiM4L3.jpg" alt="" aria-hidden="true" hidden/><span class="warmupMediaLabel">CAMINADORA</span></div>
      </div>
      <div class="warmupCopy"><div class="warmupIndex">01 · CARDIO</div><h3>Cardio suave</h3><p><strong class="timeCue">5–8 min</strong> · elige una máquina y mantén un ritmo conversacional; evita intervalos y fatiga local antes del primer ejercicio.</p></div>
    </article>
    <article class="warmupStep mobility">
      <div class="warmupMedia warmupMediaPair warmupMotionPair" role="list" aria-label="Movilidad dinámica de cadera, rodilla y tobillo sin equipo">
        <div class="warmupVisual warmupMotionCard" role="listitem"><img class="warmupMotionGif warmupGif" src="../medios_publicados/ejercicios-compartido/videos/1512-qBcKorM.gif" alt="GIF de movilidad dinámica de cadera y rodilla en cuadrupedia, con rango controlado" loading="lazy"/><img class="warmupFallback" src="../medios_publicados/ejercicios-compartido/images/1512-qBcKorM.jpg" alt="" aria-hidden="true" hidden/><span class="warmupMediaLabel">CADERA</span></div>
        <div class="warmupVisual warmupMotionCard" role="listitem"><img class="warmupMotionGif warmupGif" src="../medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.gif" alt="GIF filmado de círculos de tobillo: pie elevado, círculos controlados y regreso sin rebotes" loading="lazy"/><img class="warmupFallback" src="../medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.jpg" alt="" aria-hidden="true" hidden/><span class="warmupMediaLabel">TOBILLO</span></div>
        <div class="warmupVisual warmupMotionCard" role="listitem"><img class="warmupMotionGif warmupGif" src="../medios_publicados/ejercicios-compartido/videos/0257-X7jbxra.gif" alt="GIF de círculos de rodilla controlados, sin rebotes" loading="lazy"/><img class="warmupFallback" src="../medios_publicados/ejercicios-compartido/images/0257-X7jbxra.jpg" alt="" aria-hidden="true" hidden/><span class="warmupMediaLabel">RODILLA</span></div>
      </div>
      <div class="warmupCopy"><div class="warmupIndex">02 · MOVILIDAD</div><h3>Cadera, rodilla y tobillo</h3><p><strong class="timeCue">3–5 min</strong> · realiza movimientos dinámicos lentos y cómodos, sin rebotes ni dolor. La movilidad prepara el patrón; no busca fatigar ni forzar el rango.</p></div>
    </article>
    {tracker}
  </div>
</section>'''


def build_prep(day1_prep: str) -> str:
    prep = day1_prep
    replacements = {
        "16–17 min": "5–8 min",
        "Activación breve": "Movilidad dinámica",
        "1–2 min": "3–5 min",
        "3 + 1": "2–3 + 1",
        "Jalón: series + calentamiento": "Hack squat: aproximación",
    }
    for old, new in replacements.items():
        prep = prep.replace(old, new)
    return prep


def build_dashboard(day1_dashboard: str) -> str:
    dashboard = day1_dashboard
    replacements = {
        "75–95 min": "65–85 min",
        "Tirón · espalda y bíceps": "Pierna · cuádriceps y glúteos",
        "Con trabajo complementario de deltoides posterior y pecho": "Con trabajo específico de isquiosurales y pantorrilla",
        "4 + 4 + 3 + 3 + 3 + 3 series": "3 + 3 + 3 + 4 + 3 + 4 series",
        "De 60 s a 2.5 min según el ejercicio": "De 90 s a 3 min según el ejercicio",
    }
    for old, new in replacements.items():
        dashboard = dashboard.replace(old, new)
    return dashboard


def build_summary(day1_summary: str) -> str:
    summary = day1_summary.replace("6 ejercicios · 20 series efectivas", "6 ejercicios · 20 series efectivas")
    summary = summary.replace("75–95 min", "65–85 min")
    summary = summary.replace("60 s–2.5 min", "90 s–3 min")
    summary = summary.replace("descanso según ejercicio", "descanso según ejercicio")
    return summary


def build_note(day1_note: str) -> str:
    note = day1_note
    note = note.replace("Puntos clave de la sesión", "Puntos clave del Día 2")
    note = note.replace(
        "La serie de aproximación prepara el movimiento y no cuenta como efectiva. Trabaja cerca del fallo técnico (RIR 2–3 al inicio y 1–2 al final), sin fallar por sistema. Si cae la postura, reduce carga o descansa más.",
        "Las series de aproximación preparan el movimiento y no cuentan como efectivas. Usa RIR 2–3 en los primeros compuestos y RIR 1–2 en las últimas series y aislamientos; no falles por sistema. Si cae el apoyo, la alineación o el control pélvico, reduce carga o descansa más.",
    )
    return note


def build_session_overlays(template: str) -> str:
    start = template.index('<section class="sessionCompletionPanel"')
    end_marker = "</aside>"
    end = template.index(end_marker, start) + len(end_marker)
    return template[start:end]


def build_gif_script(template: str) -> str:
    return '''<script data-fix="day2-exercise-gifs">
(function(){
  const media = [
    {
      gif:"../medios_publicados/ejercicios-compartido/videos/0743-Qa55kX1.gif",
      thumbnail:"../medios_publicados/ejercicios-compartido/images/0743-Qa55kX1.jpg",
      key:"HACK SQUAT",
      kind:"gif",
      label:"GIF · patrón guiado",
      alt:"GIF ilustrado de hack squat guiada: descenso y ascenso con espalda y hombros apoyados"
    },
    {
      gif:"../medios_publicados/ejercicios-compartido/videos/0739-10Z2DXU.gif",
      thumbnail:"../medios_publicados/ejercicios-compartido/images/0739-10Z2DXU.jpg",
      key:"PRENSA DE PIERNAS",
      kind:"gif",
      label:"GIF · patrón guiado",
      alt:"GIF ilustrado de prensa de piernas inclinada: flexión y extensión controladas"
    },
    {
      gif:"../medios_publicados/ejercicios-compartido/videos/0599-Zg3XY7P.gif",
      thumbnail:"../medios_publicados/ejercicios-compartido/images/0599-Zg3XY7P.jpg",
      key:"CURL FEMORAL EN MÁQUINA",
      kind:"gif",
      label:"GIF · patrón guiado",
      alt:"GIF ilustrado de curl femoral sentado en máquina: flexión y regreso controlado de rodilla"
    },
    {
      gif:"../medios_publicados/ejercicios-compartido/videos/0585-my33uHU.gif",
      thumbnail:"../medios_publicados/ejercicios-compartido/images/0585-my33uHU.jpg",
      key:"EXTENSIÓN DE PIERNAS",
      kind:"gif",
      label:"GIF · patrón guiado",
      alt:"GIF ilustrado de extensión de piernas en máquina: extensión y descenso controlados"
    },
    {
      gif:"../medios_publicados/ejercicios-compartido/videos/0605-ykUOVze.gif",
      thumbnail:"../medios_publicados/ejercicios-compartido/images/0605-ykUOVze.jpg",
      key:"PANTORRILLAS DE PIE",
      kind:"gif",
      label:"GIF · patrón guiado",
      alt:"GIF ilustrado de elevación de pantorrillas de pie en máquina: descenso y elevación del talón"
    }
  ];
  function make(tag, className, text){
    const node = document.createElement(tag);
    if(className) node.className = className;
    if(text !== undefined) node.textContent = text;
    return node;
  }
  document.querySelectorAll(".card").forEach(function(card){
    const visual = card.querySelector(".visual");
    const title = card.querySelector(".exTitle")?.textContent?.trim() || "";
    const item = media.find(function(candidate){ return title.includes(candidate.key); });
    if(!item || !visual) return;
    const box = make("div","gifProof");
    box.dataset.gifProof = "true";
    box.dataset.mediaKind = item.kind || "gif";
    const frame = make("div","gifFrame");
    const motion = make("img","gifMotion");
    motion.src = item.gif;
    motion.alt = item.alt;
    motion.loading = "lazy";
    motion.decoding = "async";
    const fallback = make("img","gifFallback");
    fallback.src = item.thumbnail;
    fallback.alt = "";
    fallback.setAttribute("aria-hidden","true");
    fallback.hidden = true;
    frame.append(motion,fallback);
    const copy = make("div","gifCopy");
    copy.append(
      make("div","gifKicker",item.label || "GIF · patrón guiado"),
      make("div","gifTitle","Recorrido completo en bucle"),
      make("div","gifNote",item.note || "Animación ilustrada de referencia. Confirma el equipo, el rango y el control con la secuencia fotográfica y el checklist.")
    );
    box.append(frame,copy);
    motion.addEventListener("error", function(){
      motion.hidden = true;
      fallback.hidden = false;
    });
    visual.insertBefore(box, visual.querySelector(".videoProof"));
  });
})();
</script>'''


def preserve_machine_hip_thrust_card(card: str) -> str:
    required = (
        '<div class="exTitle">HIP THRUST</div>',
        "máquina de hip thrust",
        '<div class="machineRefBox">',
        "Ajusta la máquina",
    )
    missing = [marker for marker in required if marker not in card]
    if missing:
        raise ValueError(f"La tarjeta de hip thrust no conserva la referencia de máquina: {missing}")
    card, count = re.subn(
        r'(<span class="pillText">).*?(</span>)',
        r'\1máquina hip thrust con carga de discos y respaldo basculante\2',
        card,
        count=1,
    )
    if count != 1:
        raise ValueError("No se pudo normalizar la descripción del equipo de hip thrust")
    return card


def extract_div_block(text: str, marker: str) -> tuple[str, int, int]:
    start = text.index(marker)
    opening_end = text.index(">", start) + 1
    depth = 1
    token_pattern = re.compile(r"<div\b|</div>", flags=re.I)
    for token in token_pattern.finditer(text, opening_end):
        if token.group().lower().startswith("<div"):
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return text[start : token.end()], start, token.end()
    raise ValueError(f"No se pudo cerrar el bloque: {marker}")


def enforce_machine_hip_thrust_visuals(card: str) -> str:
    card = preserve_machine_hip_thrust_card(card)
    phase, phase_start, phase_end = extract_div_block(card, '<div class="phaseRow">')
    replacement = '''<div class="phaseRow hipThrustGuide" aria-label="Puntos de colocación y recorrido del hip thrust en máquina">
<div class="hipThrustGuideTitle"><span aria-hidden="true">01</span><strong>Colócate</strong><p>Espalda y cabeza apoyadas; ambos pies firmes en la plataforma. Ajusta el rodillo acolchado sobre el abdomen bajo.</p></div>
<div class="hipThrustGuideTitle"><span aria-hidden="true">02</span><strong>Desciende</strong><p>Flexiona la cadera con control, manteniendo el tronco apoyado y la zona lumbar estable.</p></div>
<div class="hipThrustGuideTitle"><span aria-hidden="true">03</span><strong>Extiende</strong><p>Empuja la plataforma y eleva la cadera junto con el respaldo; termina sin arquear la zona lumbar.</p></div>
<a class="hipThrustOfficialLink" href="https://www.youtube.com/watch?v=lMk6ZFXbY00" target="_blank" rel="noopener noreferrer">Ver demostración oficial · Panatta Fit Evo <span aria-hidden="true">↗</span></a>
</div>'''
    return card[:phase_start] + replacement + card[phase_end:]


def improve_card_layout(card: str) -> str:
    reference, reference_start, reference_end = extract_div_block(card, '<div class="referenceRow">')
    visual_start = card.index('<div class="visual">')
    visual_open_end = card.index(">", visual_start) + 1
    card_without_reference = card[:reference_start] + card[reference_end:]
    visual_start = card_without_reference.index('<div class="visual">')
    visual_open_end = card_without_reference.index(">", visual_start) + 1
    return (
        card_without_reference[:visual_open_end]
        + "\n"
        + reference
        + card_without_reference[visual_open_end:]
    )


def add_exercise_tracker(card: str, exercise_number: int, series_count: int) -> str:
    if 'class="exerciseTracker"' in card:
        return card
    marker = '<div class="techSteps">'
    if marker not in card:
        raise ValueError(f"No se encontró .techSteps en la tarjeta {exercise_number}")
    keys = " ".join(f"e{exercise_number}s{index}" for index in range(1, series_count + 1))
    warmup = (
        '<button type="button" class="setButton warmupSet" data-key="w1" aria-pressed="false">Calentamiento</button>'
        if exercise_number == 1 else ""
    )
    next_button = (
        f'<button type="button" class="nextExerciseCue" data-next="{exercise_number + 1}" hidden>'
        f'<span class="nextArrow" aria-hidden="true">↓</span> Siguiente ejercicio</button>'
        if exercise_number < 6 else ""
    )
    tracker = f'''<div class="exerciseTracker" data-exercise="{exercise_number}" data-series-keys="{keys}">
<div class="exerciseTrackerHead"><span>Contador de series</span><span class="exerciseTrackerMeta"><strong class="exerciseProgress">0/{series_count}</strong><span class="exerciseStatus" hidden><span class="completionMark" aria-hidden="true">✓</span> Completado</span></span></div>
<div class="exerciseSetButtons" role="group" aria-label="Contador de series del ejercicio {exercise_number}">{warmup}<button type="button" class="completeSetButton" aria-label="Completar serie 1 de {series_count}">Completar serie 1 de {series_count}</button><button type="button" class="machinePendingToggle" data-pending-key="p{exercise_number}" aria-pressed="false">⚠ Máquina ocupada</button><div class="nextExerciseRow">{next_button}</div></div>
</div>'''
    return card.replace(marker, tracker + "\n" + marker, 1)


def add_exercise_quick_summary(card: str) -> str:
    marker = '<div class="coachHeader">Técnica clave</div>'
    summary = '<div class="exerciseQuickSummary" data-exercise-quick-summary aria-label="Resumen del ejercicio"></div>'
    if 'data-exercise-quick-summary' in card:
        return card
    if marker not in card:
        raise ValueError("No se encontró .coachHeader en una tarjeta del Día 2")
    return card.replace(marker, marker + summary, 1)


def main() -> None:
    template = TEMPLATE.read_text(encoding="utf-8")
    source = SOURCE.read_text(encoding="utf-8")

    head = template[: template.index("</head>") + len("</head>")]
    head = head.replace("data-label=\"Día 1 · Tirón: espalda y bíceps · v1 responsive\"", "data-label=\"Día 2 · Pierna: cuádriceps y glúteos · v1 responsive\"")
    head = head.replace("<title>Día 1 · Tirón: espalda y bíceps · v1 responsive</title>", "<title>Día 2 · Pierna: cuádriceps y glúteos · v1 responsive</title>")
    head = head.replace("</head>", '''<style data-fix="day2-lower-body-visuals">
.muscleDayIcon.lower{border-color:rgba(100,215,255,.55)!important;color:#64D7FF!important;background:rgba(100,215,255,.09)!important}
.warmupStep.cardio,.warmupStep.mobility{grid-template-columns:1fr!important}
.warmupStep.cardio .warmupMedia,.warmupStep.mobility .warmupMedia{height:112px!important;min-height:112px!important}
.warmupStep.cardio .warmupTextStrip,.warmupStep.mobility .warmupMotionPair{grid-template-columns:repeat(3,minmax(0,1fr))!important;width:100%!important;height:112px!important;min-height:112px!important;padding:0!important;background:transparent!important;overflow:visible!important}
.warmupStep .warmupVisual .warmupGif:not([hidden]){display:block!important}
.warmupStep .warmupVisual .warmupGif[hidden]{display:none!important}
.warmupStep .warmupVisual .warmupFallback{display:none!important}
.warmupStep .warmupVisual .warmupFallback:not([hidden]){display:block!important}
.warmupVisual.warmupTextCard{background:linear-gradient(145deg,#0b2635,#123e50)!important;color:#e9fbff!important;display:flex!important;flex-direction:column!important;align-items:flex-start!important;justify-content:center!important;gap:5px!important;position:relative!important;padding:14px!important;min-height:112px!important}
.warmupVisual.warmupTextCard .warmupMediaLabel{position:static!important;background:rgba(4,17,25,.92)!important;color:#8eeeff!important}
.warmupVisual.warmupTextCard strong{font-size:13px!important;line-height:1.2!important;color:#f4fbff!important}
.warmupVisual.warmupTextCard small{font-size:11px!important;line-height:1.25!important;color:#a9d7e5!important}
.warmupStep .warmupCopy{width:100%!important}
@media(max-width:430px){.warmupStep.cardio .warmupTextStrip,.warmupStep.mobility .warmupMotionPair{grid-template-columns:repeat(3,minmax(0,1fr))!important}}
.techSteps{grid-template-columns:1fr!important}
.techStep{display:grid!important;grid-template-columns:minmax(0,1fr)!important;align-items:start!important;gap:4px!important}
.techStepTitle,.techStepText{grid-column:1!important;min-width:0!important;overflow-wrap:anywhere!important}
.equipmentRefBox{display:flex!important;flex-direction:column!important;align-items:center!important;justify-content:center!important;gap:7px!important;padding:16px!important;text-align:center!important}
.equipmentRefBox .refTag{position:static!important}
.equipmentRefBox strong{font-size:15px!important;color:#f4fbff!important}
.equipmentRefBox small{font-size:11px!important;line-height:1.25!important;color:#a9d7e5!important}
.hipThrustGuide{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:9px!important;margin-top:10px!important}
.hipThrustGuideTitle{min-width:0!important;padding:11px!important;border:1px solid rgba(114,220,255,.22)!important;border-radius:13px!important;background:linear-gradient(145deg,#102d3d,#0b1b29)!important;color:#cde5ec!important}
.hipThrustGuideTitle>span{display:inline-grid!important;place-items:center!important;width:25px!important;height:25px!important;margin-right:7px!important;border-radius:8px!important;background:rgba(83,217,204,.14)!important;color:#53d9cc!important;font-size:12px!important;font-weight:900!important}
.hipThrustGuideTitle strong{font-size:13px!important;color:#f4fbff!important}
.hipThrustGuideTitle p{margin:7px 0 0!important;font-size:12px!important;line-height:1.35!important;color:#b9d4de!important}
.hipThrustOfficialLink{grid-column:1/-1!important;justify-self:start!important;color:#72dcff!important;font-size:12px!important;font-weight:800!important;text-decoration-thickness:1px!important;text-underline-offset:3px!important}
@media(max-width:700px){.hipThrustGuide{grid-template-columns:1fr!important;gap:7px!important}.hipThrustGuideTitle{padding:9px 11px!important}.hipThrustGuideTitle p{margin-left:33px!important;font-size:11.5px!important}}
.gifProof .gifMotion{width:180px!important;height:180px!important;max-width:100%!important;object-fit:contain!important;margin:auto!important}
.page .card .visual .gifProof{grid-template-columns:1fr!important;align-items:center!important}
.page .card .visual .gifProof .gifFrame{width:180px!important;height:180px!important;aspect-ratio:auto!important;margin:0 auto!important}
.page .card .visual .gifProof[data-media-kind="video"] .gifMotion{width:360px!important;height:180px!important;max-width:100%!important;object-fit:contain!important}
.page .card .visual .gifProof[data-media-kind="video"] .gifFrame{width:360px!important;height:180px!important;aspect-ratio:2/1!important;margin:0 auto!important}
@media(max-width:700px){.page .card .visual .gifProof[data-media-kind="video"] .gifMotion,.page .card .visual .gifProof[data-media-kind="video"] .gifFrame{width:min(360px,100%)!important;height:auto!important;aspect-ratio:2/1!important}}
.cards>.card:nth-of-type(4) .gifProof{--accent:#f0bf70}
</style></head>''')

    day1_header = between(template, '<header class="hero">', "</header>")
    day1_rules = between(template, '<section class="footer quickRules"', "</section>")
    day1_prep = between(template, '<section class="prep">', "</section>")
    day1_gamification = between(template, '<section class="sessionGamification"', "</section>")
    day1_dashboard = between(template, '<section class="sessionDashboard">', "</section>")
    day1_summary = between(template, '<section class="routineSummary"', "</section>")
    day1_note = between(template, '<section class="note notePanel"', "</section>")

    source_cards = between(source, '<main class="cards">', "</main>")
    source_cards = re.sub(r'(\d+[–-]\d+) rep\.', r'\1 repeticiones', source_cards)
    card_matches = list(re.finditer(r'<article class="card">.*?</article>', source_cards, re.S))
    if len(card_matches) != 6:
        raise ValueError(f"Se esperaban 6 tarjetas y se encontraron {len(card_matches)}")
    card_payloads = []
    series_by_exercise = (3, 3, 3, 4, 3, 4)
    for index, match in enumerate(card_matches):
        card = match.group(0)
        card = card.replace(
            '<article class="card">',
            f'<article class="card" data-exercise-index="{index + 1}">',
            1,
        )
        if index == 1:
            card = enforce_machine_hip_thrust_visuals(card)
        if index == 3:
            card = card.replace('<div class="metricVal">3 series</div>', '<div class="metricVal">4 series</div>', 1)
            card = card.replace('<div class="metricVal">6–8 min</div>', '<div class="metricVal">8–10 min</div>', 1)
        card = improve_card_layout(card)
        card = add_exercise_tracker(card, index + 1, series_by_exercise[index])
        card_payloads.append(add_exercise_quick_summary(card))
    cards = "\n".join(card_payloads)

    tail_start = template.rfind("</div>\n<script")
    if tail_start == -1:
        raise ValueError("No se encontró el cierre de la página y los scripts del Día 1")
    tail = template[tail_start: template.rfind("</body>")]
    tail = re.sub(r'<script data-fix="day1-gif-candidates">.*?</script>', build_gif_script(template), tail, count=1, flags=re.S)
    tail = tail.replace('data-fix="day1-warmup-guide"', 'data-fix="day2-warmup-guide"')
    tail = tail.replace("fitlovers-day1-series-v1", "fitlovers-day2-series-v1")
    tail = tail.replace("fitlovers-day1-sound-v1", "fitlovers-day2-sound-v1")
    tail = tail.replace("fitlovers-day1-motivation-v1", "fitlovers-day2-motivation-v1")

    body = "\n".join([
        "<body>",
        '<div class="page">',
        build_header(day1_header),
        build_quick_rules(day1_rules),
        build_warmup(template),
        build_summary(day1_summary),
        day1_gamification,
        build_prep(day1_prep),
        build_dashboard(day1_dashboard),
        build_note(day1_note),
        '<main class="cards">',
        cards,
        '</main>',
        build_session_overlays(template),
        tail,
        "</body>",
        "</html>",
    ])
    if len(re.findall(r'<article class="card" data-exercise-index="\d+">', body)) != 6:
        raise ValueError("El HTML canónico debe conservar 6 tarjetas")
    if sum(card.count('data-exercise-quick-summary') for card in re.findall(r'<article class="card" data-exercise-index="\d+">.*?</article>', body, re.S)) != 6:
        raise ValueError("Cada tarjeta del Día 2 debe conservar un resumen rápido")
    if body.count('<main class="cards">') != 1:
        raise ValueError("El HTML canónico debe envolver las tarjetas en un único main.cards")
    if body.count('<footer class="sessionFooter"') != 1 or '<footer class="footer">' in body:
        raise ValueError("El HTML canónico debe usar únicamente el footer de acciones de sesión")
    if len(re.findall(r'<div class="visual">\s*<div class="referenceRow">', body)) != 6:
        raise ValueError("Cada tarjeta debe agrupar referencia y secuencia dentro de .visual")
    if 'data-fix="day2-exercise-gifs"' not in body:
        raise ValueError("El HTML canónico debe conservar el inyector de GIFs de ejercicios")
    if "HIP THRUST CON BARRA" in body or "Banco + barra" in body:
        raise ValueError("El hip thrust del Día 2 debe conservarse como máquina")
    if "hipThrustGuide" not in card_payloads[1] or "hip_thrust_panatta_" in card_payloads[1]:
        raise ValueError("La tarjeta de hip thrust debe evitar las ilustraciones imprecisas y conservar la guía técnica textual")
    forbidden_media_metadata = (
        '"license":',
        "portraitLicense",
        "portraitCredit",
        "portraitSource",
        "authorContextSource",
        "CANDIDATE_PENDING_LICENSE_REVIEW",
        "sourceUrl:",
        "mediaStatus",
        "motivationSource",
        "gifAttribution",
    )
    leaked_metadata = [marker for marker in forbidden_media_metadata if marker in body]
    if leaked_metadata:
        raise ValueError(f"El HTML canónico conserva metadatos de licencia/atribución: {leaked_metadata}")
    canonical = sanitize_canonical_metadata(standardize_muscle_visuals(head + body))
    OUTPUT.write_text(canonical, encoding="utf-8", newline="\n")
    print(f"GENERATED {OUTPUT.relative_to(ROOT)} bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    main()
