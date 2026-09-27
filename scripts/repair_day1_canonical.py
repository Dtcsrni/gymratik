"""Repara la estructura de tarjetas del HTML canónico del Día 1."""

import re
from pathlib import Path

from standardize_muscle_visuals import sanitize_canonical_metadata, standardize_muscle_visuals


HTML = Path(__file__).parents[1] / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html"
HEADER_SOURCE = Path(__file__).parents[1] / "data/rutinas_autocontenidas/fuentes_locales/Rutina_Dia_1_Espalda_Biceps_Autocontenida_v10_HEADER_REPARADO.html"


CARDS_4_5 = r'''<!-- 4 -->
<article class="card"><div aria-hidden="true" class="cardGlow"></div>
<div class="meta">
<div class="metaTop"><div class="num">4</div></div>
<div class="exTitle">APERTURA INVERSA EN MÁQUINA</div>
<div class="zone">HOMBRO · DELTOIDES POSTERIOR</div><div class="chipRow"><span class="infoChip chipExercise">Ejercicio 4</span><span class="infoChip">HOMBRO</span><span class="infoChip">DELTOIDES POSTERIOR</span></div>
<div class="machinePill"><span class="pillText">butterfly reverse · apoyo de pecho</span></div>
</div>
<div class="visual"><div class="referenceRow"><div class="machineRefBox"><img alt="Máquina de apertura inversa para deltoides posterior, sin persona" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/3025-butterfly-reverse-front.jpg"/><span class="refTag">VISTA AISLADA · REFERENCIA DE MÁQUINA</span></div></div><div class="phaseRow">
<div class="phaseCol"><div class="phaseLabel">Inicio</div><div class="photo techZoom"><img alt="Apertura inversa en máquina, posición inicial" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/0602-myfUsKf.jpg"/></div></div>
<div class="swap" aria-hidden="true">→</div>
<div class="phaseCol"><div class="phaseLabel">Final</div><div class="photo techZoom"><img alt="Apertura inversa en máquina, referencia final" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/3025-butterfly-reverse-front.jpg"/></div></div>
</div></div>
<div class="coach"><div class="coachHeader">Técnica clave</div><div class="exerciseQuickSummary" data-exercise-quick-summary aria-label="Resumen del ejercicio"></div><div class="metrics"><div class="metric series"><div class="metricText"><div class="metricLabel">Series</div><div class="metricVal">3 series</div></div></div><div class="metric reps"><div class="metricText"><div class="metricLabel">Repeticiones</div><div class="metricVal">12–20 rep.</div></div></div><div class="metric rest"><div class="metricText"><div class="metricLabel">Descanso</div><div class="metricVal"><strong class="timeCue">1.5 min</strong></div></div></div></div><div class="exerciseTracker" data-exercise="4" data-series-keys="e4s1 e4s2 e4s3"><div class="exerciseTrackerHead"><span>Contador de series</span><span class="exerciseTrackerMeta"><strong class="exerciseProgress">0/3</strong><span class="exerciseStatus" hidden>Completado</span></span></div><div class="exerciseSetButtons" role="group" aria-label="Contador de series de apertura inversa"><button type="button" class="completeSetButton" aria-label="Completar serie 1 de 3">Completar serie 1 de 3</button><button type="button" class="machinePendingToggle" data-pending-key="p4" aria-pressed="false">⚠ Máquina ocupada</button><div class="nextExerciseRow"><button type="button" class="nextExerciseCue" data-next="5" hidden><span class="nextArrow" aria-hidden="true">↓</span> Siguiente: 05 · Curl de bíceps en máquina</button></div></div></div></div>
<div class="techSteps"><div class="techStep setup"><div class="techStepTitle">1 · Ajuste</div><div class="techStepText">Ajusta el asiento y el apoyo para que los hombros queden cómodos y los codos alineados con el eje.</div></div><div class="techStep move"><div class="techStepTitle">2 · Ejecución</div><div class="techStepText">Abre los brazos hacia atrás en un arco controlado, sin encoger los hombros ni perder el apoyo del pecho.</div></div><div class="techStep control"><div class="techStepTitle">3 · Ritmo y respiración</div><div class="techStepText">Exhala al abrir y regresa en 2–3 s manteniendo tensión continua.</div></div><div class="techStep warning"><div class="techStepTitle">⚠ Evita</div><div class="techStepText">Impulsarte, extender de más el hombro o convertir el movimiento en un remo.</div></div></div>
</div></article>
<!-- 5 -->
<article class="card"><div aria-hidden="true" class="cardGlow"></div>
<div class="meta">
<div class="metaTop"><div class="num">5</div></div>
<div class="exTitle">CURL DE BÍCEPS EN MÁQUINA</div>
<div class="zone">BRAZO · BÍCEPS</div><div class="chipRow"><span class="infoChip chipExercise">Ejercicio 5</span><span class="infoChip">BRAZO</span><span class="infoChip">BÍCEPS</span></div>
<div class="machinePill"><span class="pillText">curl tipo preacher · brazo apoyado</span></div>
</div>
<div class="visual"><div class="referenceRow"><div class="machineRefBox"><img alt="Máquina de curl de bíceps con apoyo, sin persona" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/0592-b6hQYMb-machine-only.jpg"/><span class="refTag">VISTA AISLADA · REFERENCIA DE MÁQUINA</span></div></div><div class="phaseRow">
<div class="phaseCol"><div class="phaseLabel">Inicio</div><div class="photo techZoom"><img alt="Curl de bíceps en máquina, posición inicial" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/0592-b6hQYMb-start.jpg"/></div></div>
<div class="swap" aria-hidden="true">→</div>
<div class="phaseCol"><div class="phaseLabel">Final</div><div class="photo techZoom"><img alt="Curl de bíceps en máquina, posición final" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/0592-b6hQYMb-final.png"/></div></div>
</div></div>
<div class="coach"><div class="coachHeader">Técnica clave</div><div class="exerciseQuickSummary" data-exercise-quick-summary aria-label="Resumen del ejercicio"></div><div class="metrics"><div class="metric series"><div class="metricText"><div class="metricLabel">Series</div><div class="metricVal">3 series</div></div></div><div class="metric reps"><div class="metricText"><div class="metricLabel">Repeticiones</div><div class="metricVal">10–15 rep.</div></div></div><div class="metric rest"><div class="metricText"><div class="metricLabel">Descanso</div><div class="metricVal"><strong class="timeCue">1.5–2 min</strong></div></div></div></div><div class="exerciseTracker" data-exercise="5" data-series-keys="e5s1 e5s2 e5s3"><div class="exerciseTrackerHead"><span>Contador de series</span><span class="exerciseTrackerMeta"><strong class="exerciseProgress">0/3</strong><span class="exerciseStatus" hidden>Completado</span></span></div><div class="exerciseSetButtons" role="group" aria-label="Contador de series de curl de bíceps"><button type="button" class="completeSetButton" aria-label="Completar serie 1 de 3">Completar serie 1 de 3</button><button type="button" class="machinePendingToggle" data-pending-key="p5" aria-pressed="false">⚠ Máquina ocupada</button><div class="nextExerciseRow"><button type="button" class="nextExerciseCue" data-next="6" hidden><span class="nextArrow" aria-hidden="true">↓</span> Siguiente: 06 · Press de pecho complementario</button></div></div></div></div>
<div class="techSteps"><div class="techStep setup"><div class="techStepTitle">1 · Ajuste</div><div class="techStepText">Alinea el codo con el eje y apoya por completo la parte posterior del brazo.</div></div><div class="techStep move"><div class="techStepTitle">2 · Ejecución</div><div class="techStepText">Flexiona el codo sin despegarlo del apoyo; sube hasta una contracción cómoda.</div></div><div class="techStep control"><div class="techStepTitle">3 · Ritmo y respiración</div><div class="techStepText">Exhala al subir y desciende en 2–3 s sin perder tensión.</div></div><div class="techStep warning"><div class="techStepTitle">⚠ Evita</div><div class="techStepText">Levantar el hombro, adelantar el codo, doblar la muñeca o rebotar.</div></div></div>
</div></article>'''


DAY1_CARD6 = r'''<!-- 6 -->
<article class="card" data-exercise-index="6"><div aria-hidden="true" class="cardGlow"></div>
<div class="meta">
<div class="metaTop"><div class="num">6</div></div>
<div class="exTitle">CURL DE BÍCEPS SENTADO EN MÁQUINA</div>
<div class="zone">BRAZO · BÍCEPS</div><div class="chipRow"><span class="infoChip chipExercise">Ejercicio 6</span><span class="infoChip">BRAZO</span><span class="infoChip">BÍCEPS</span></div>
<div class="machinePill"><span class="pillText">curl sentado en máquina · agarre supino</span></div>
</div>
<div class="visual"><div class="referenceRow"><div class="machineRefBox"><img alt="Máquina de curl de bíceps sentado, sin persona" class="realphoto" loading="lazy" src="../medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-machine-reference.png"/><span class="refTag">VISTA AISLADA · REFERENCIA DE MÁQUINA</span></div></div><div class="phaseRow">
<div class="phaseCol"><div class="phaseLabel">Inicio</div><div class="photo techZoom"><img alt="Curl de bíceps sentado en máquina, brazos extendidos y espalda apoyada" class="realphoto" loading="lazy" src="../medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-start.jpg"/><div class="brokenFallback"><div class="fallbackIcon"><svg aria-hidden="true" viewbox="0 0 64 64"><path d="M10 32h38M38 20l12 12-12 12" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="6"></path></svg></div>Referencia de inicio no disponible.</div></div><div class="source">Inicio · espalda apoyada · codos junto al torso</div></div>
<div class="swap" aria-hidden="true">→</div>
<div class="phaseCol"><div class="phaseLabel">Final</div><div class="photo techZoom"><img alt="Curl de bíceps sentado en máquina, asas elevadas y bíceps contraídos" class="realphoto" loading="lazy" src="../medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-final.jpg"/><div class="brokenFallback"><div class="fallbackIcon"><svg aria-hidden="true" viewbox="0 0 64 64"><path d="M10 32h38M38 20l12 12-12 12" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="6"></path></svg></div>Referencia final no disponible.</div></div><div class="source">Final · pausa breve · sin despegar los codos</div></div>
</div><div class="videoProof"><span>▶ GIF LOCAL · Curl de bíceps sentado en máquina</span></div></div>
<div class="coach"><div class="coachHeader">Técnica clave</div><div class="exerciseQuickSummary" data-exercise-quick-summary aria-label="Resumen del ejercicio"></div><div class="metrics"><div class="metric series"><div class="metricText"><div class="metricLabel">Series</div><div class="metricVal">3 series</div></div></div><div class="metric reps"><div class="metricText"><div class="metricLabel">Repeticiones</div><div class="metricVal">10–15 rep.</div></div></div><div class="metric rest"><div class="metricText"><div class="metricLabel">Descanso</div><div class="metricVal"><strong class="timeCue">1.5–2 min</strong></div></div></div><div class="metric duration"><div class="metricText"><div class="metricLabel">Duración aprox.</div><div class="metricVal"><strong class="timeCue">5–7 min</strong></div></div></div></div><div class="exerciseTracker" data-exercise="6" data-series-keys="e6s1 e6s2 e6s3"><div class="exerciseTrackerHead"><span>Contador de series</span><span class="exerciseTrackerMeta"><strong class="exerciseProgress">0/3</strong><span class="exerciseStatus" hidden>Completado</span></span></div><div class="exerciseSetButtons" role="group" aria-label="Contador de series de curl de bíceps sentado"><button type="button" class="completeSetButton" aria-label="Completar serie 1 de 3">Completar serie 1 de 3</button><button type="button" class="machinePendingToggle" data-pending-key="p6" aria-pressed="false">⚠ Máquina ocupada</button></div></div></div>
<div class="techSteps"><div class="techStep setup"><div class="techStepTitle">1 · Ajuste</div><div class="techStepText">Regula la altura del asiento y apoya la espalda. Coloca los codos cerca de los costados y las muñecas neutras.</div></div><div class="techStep move"><div class="techStepTitle">2 · Ejecución</div><div class="techStepText">Sujeta las asas con agarre supino, flexiona los codos y eleva los mangos sin despegar los brazos del soporte.</div></div><div class="techStep control"><div class="techStepTitle">3 · Ritmo y respiración</div><div class="techStepText">Exhala al subir, pausa brevemente arriba e inhala mientras bajas en 2–3 s hasta extender los brazos.</div></div><div class="techStep warning"><div class="techStepTitle">⚠ Evita</div><div class="techStepText">Impulsarte con el tronco, adelantar los codos, doblar las muñecas o bloquear la articulación al final.</div></div></div>
</div></article>'''


MUSCLE_PECTORAL = r'''<div class="muscleDayItem" data-muscle-focus="pectoralis-major" data-muscle-view="anterior" data-muscle-visual="upper-anterior" aria-label="Pectoral mayor; foco visual en tórax anterior"><span class="muscleDayVisual anterior" title="Foco visual: tórax anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior del músculo Pectoral mayor; foco visual aproximado en tórax anterior" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#ff9da2">PECHO</span><span class="muscleName">Pectoral mayor</span></span></div>'''


BATTERY_MOTION_STYLE = r'''<style data-enhancement="battery-aware-motion-v1">
html.is-document-hidden *,html.is-document-hidden *::before,html.is-document-hidden *::after,
[data-motion-paused="true"] *,[data-motion-paused="true"] *::before,[data-motion-paused="true"] *::after{
  animation-play-state:paused!important
}
</style>'''

BATTERY_MOTION_SCRIPT = r'''<script data-enhancement="battery-aware-motion-v1">
(() => {
  const root = document.documentElement;
  const syncVisibility = () => root.classList.toggle('is-document-hidden', document.hidden);
  document.addEventListener('visibilitychange', syncVisibility, { passive: true });
  syncVisibility();

  if (!('IntersectionObserver' in window)) return;
  const sections = document.querySelectorAll('.hero,.quickRules,.prep,.routineSummary,.sessionGamification,.sessionDashboard,.notePanel,.cards>.card,.sessionFooter');
  const observer = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      entry.target.setAttribute('data-motion-paused', String(!entry.isIntersecting));
    }
  }, { rootMargin: '96px 0px' });
  sections.forEach((section) => observer.observe(section));
})();
</script>'''


def apply_battery_motion(source: str, newline: str) -> str:
    style_present = 'data-enhancement="battery-aware-motion-v1"' in source
    if not style_present:
        source = source.replace("</head>", BATTERY_MOTION_STYLE.replace("\n", newline) + newline + "</head>", 1)
    script_tag = '<script data-enhancement="battery-aware-motion-v1">'
    if script_tag not in source:
        source = source.replace("</body>", BATTERY_MOTION_SCRIPT.replace("\n", newline) + newline + "</body>", 1)
    else:
        source = source.replace(
            "entry.target.toggleAttribute('data-motion-paused', !entry.isIntersecting);",
            "entry.target.setAttribute('data-motion-paused', String(!entry.isIntersecting));",
            1,
        )
    return source


def main() -> None:
    with HTML.open("r", encoding="utf-8", newline="") as handle:
        source = handle.read()
    newline = "\r\n" if "\r\n" in source else "\n"
    if "</head>" not in source or '<header class="hero">' not in source:
        with HEADER_SOURCE.open("r", encoding="utf-8", newline="") as handle:
            header_source = handle.read()
        header_start = header_source.index('<header class="hero">')
        header_end = header_source.index("</header>", header_start) + len("</header>")
        fragment_start = source.index('<div class="heroSummaryText">')
        header_style_end = source.rfind("</style>", 0, fragment_start)
        current_header_end = source.index("</header>", fragment_start) + len("</header>")
        if header_style_end < 0:
            raise RuntimeError("No se encontró el cierre de estilos del encabezado del Día 1")
        source = (
            source[: header_style_end + len("</style>")]
            + newline
            + "</head>"
            + newline
            + "<body>"
            + newline
            + '<div class="page">'
            + newline
            + header_source[header_start:header_end]
            + source[current_header_end:]
        )
    source = re.sub(
        r'<img alt="Panatta Super High Row unilateral inicio"[^>]*>',
        '<img alt="Panatta Super High Row unilateral inicio" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/panatta-super-high-row-unilateral-start.webp"/>',
        source,
        count=1,
    )
    source = re.sub(
        r'<img alt="Panatta Super High Row unilateral final"[^>]*>',
        '<img alt="Panatta Super High Row unilateral final" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/panatta-super-high-row-unilateral-final.webp"/>',
        source,
        count=1,
    )
    bad_tracker = 'data-exercise="5" data-series-keys="e5s1 e5s2 e5s3"'
    e3_tracker = 'data-exercise="3" data-series-keys="e3s1 e3s2 e3s3"'
    if bad_tracker in source and e3_tracker not in source:
        source = source.replace(bad_tracker, e3_tracker, 1)
        source = source.replace('Contador del curl de bíceps', 'Contador del remo horizontal', 1)
        source = source.replace('data-pending-key="p5"', 'data-pending-key="p3"', 1)
    elif source.count(e3_tracker) >= 2:
        second = source.find(e3_tracker, source.find(e3_tracker) + 1)
        source = source[:second] + source[second:].replace(e3_tracker, bad_tracker, 1)
    source = re.sub(
        r'(<div class="exerciseTracker" data-exercise="3" data-series-keys="e3s1 e3s2 e3s3">.*?data-next=")6(" hidden><span class="nextArrow" aria-hidden="true">↓</span> Siguiente: )06 · Press de pecho(?: complementario)?(</button>)',
        r'\g<1>4\g<2>04 · Apertura inversa en máquina\g<3>',
        source,
        count=1,
        flags=re.S,
    )
    e3_next = 'data-next="4" hidden><span class="nextArrow" aria-hidden="true">↓</span> Siguiente: 04 · Apertura inversa en máquina</button>'
    if source.count(e3_next) >= 2:
        second = source.find(e3_next, source.find(e3_next) + 1)
        source = source[:second] + source[second:].replace(e3_next, 'data-next="6" hidden><span class="nextArrow" aria-hidden="true">↓</span> Siguiente: 06 · Curl de bíceps sentado en máquina</button>', 1)
    source = source.replace('Siguiente: 03 · Remo horizontal</button>', 'Siguiente: 03 · Remo horizontal en máquina</button>', 1)
    source = source.replace('images/0592-b6hQYMb-start.jpg', 'images/0592-b6hQYMb.jpg', 1)
    card3_start = source.index('<!-- 3 -->')
    card3_end = source.index('<!-- 4 -->', card3_start)
    card3 = source[card3_start:card3_end]
    card3 = re.sub(
        r'<img alt="Panatta Super Rowing inicio"[^>]*>',
        '<img alt="Panatta Super Rowing inicio" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/1350-7I6LNUG.jpg"/>',
        card3,
        count=1,
    )
    card3 = card3.replace('American Fitness · contracción', 'Inicio · brazos extendidos · pecho apoyado', 1)
    card3 = card3.replace('https://www.mayoclinic.org/healthy-lifestyle/fitness/multimedia/biceps-curl/vid-20084690', 'https://www.youtube.com/watch?v=Jl0r78dnqGU', 1)
    card3 = card3.replace('▶ VIDEO TÉCNICO · Curl de bíceps', '▶ VIDEO TÉCNICO · Remo horizontal', 1)
    card3 = card3.replace('10–15 rep.', '8–12 rep.', 1)
    card3 = card3.replace('1.5–2 min', '2–2.5 min', 1)
    card3 = card3.replace('6–8 min', '7–9 min', 1)
    card3 = card3.replace('Alinea el codo con el eje de giro de la máquina. Apoya completamente la parte posterior del brazo, hombros relajados y muñecas rectas.', 'Centra el pecho sobre el apoyo y regula el asiento para alcanzar los agarres con brazos extendidos. Pies firmes, cuello neutro y abdomen activo.', 1)
    card3 = card3.replace('Flexiona el codo sin despegar el brazo del apoyo. Sube hasta una contracción fuerte y cómoda, manteniendo antebrazo y muñeca alineados.', 'Rema hacia las costillas o el abdomen alto. Lleva los codos atrás de forma natural y acompaña con las escápulas sin despegar el pecho del soporte.', 1)
    card3 = card3.replace('Exhala al subir, pausa brevemente y desciende en <strong class="timeCue">2–3 s</strong> hasta casi extender el codo. Mantén tensión continua sin dejar caer la carga.', 'Exhala al tirar, pausa brevemente atrás y vuelve en <strong class="timeCue">2–3 s</strong>. Deja que las escápulas avancen de forma controlada al final del retorno.', 1)
    card3 = card3.replace('Levantar los hombros, adelantar el codo, doblar las muñecas, rebotar en la parte baja o sacrificar el recorrido por demasiado peso.', 'Dar tirones con el torso, hiperextender la espalda baja, encoger los hombros o golpear la carga al terminar cada repetición.', 1)
    if '<div class="phaseLabel">Final' not in card3:
        final_phase = '''<div class="swap" aria-hidden="true">→</div><div class="phaseCol"><div class="phaseLabel">Final</div><div class="photo techZoom"><img alt="REMO HORIZONTAL EN MÁQUINA · posición final estática" class="realphoto" loading="lazy" src="../medios_publicados/medios_publicados/ejercicios-compartido/images/1350-7I6LNUG-final.png" onerror="this.onerror=null;this.src=this.dataset.fallback" data-fallback="../medios_publicados/ejercicios-compartido/images/1350-7I6LNUG-final.png"/></div><div class="source">Final · codos atrás · pecho apoyado</div></div>'''
        final_phase = final_phase.replace('../medios_publicados/medios_publicados/', '../medios_publicados/')
        marker = '</div><div class="videoProof">'
        if marker not in card3:
            raise RuntimeError('No se encontró el cierre de la fase del ejercicio 3')
        card3 = card3.replace(marker, final_phase + marker, 1)
    source = source[:card3_start] + card3 + source[card3_end:]
    for marker, reference in (
        (
            '<!-- 4 -->',
            '<div class="referenceRow"><div class="machineRefBox"><img alt="Máquina de apertura inversa para deltoides posterior, sin persona" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/3025-butterfly-reverse-front.jpg"/><span class="refTag">VISTA AISLADA · REFERENCIA DE MÁQUINA</span></div></div>',
        ),
        (
            '<!-- 5 -->',
            '<div class="referenceRow"><div class="machineRefBox"><img alt="Máquina de curl de bíceps con apoyo, sin persona" class="realphoto" loading="lazy" src="../medios_publicados/ejercicios-compartido/images/0592-b6hQYMb-machine-only.jpg"/><span class="refTag">VISTA AISLADA · REFERENCIA DE MÁQUINA</span></div></div>',
        ),
    ):
        start = source.index(marker)
        end = source.index(f'<!-- {int(marker[5]) + 1} -->', start) if marker != '<!-- 5 -->' else source.index('<!-- 6 -->', start)
        card = source[start:end]
        if 'class="machineRefBox"' not in card:
            anchor = '<div class="visual">'
            if anchor not in card:
                raise RuntimeError(f'No se encontró el bloque visual de {marker}')
            card = card.replace(anchor, anchor + reference, 1)
            source = source[:start] + card + source[end:]
    if 'src="../../../progress-store.js"' not in source:
        source = source.replace('</head>', '<script src="../../../progress-store.js"></script>\n</head>', 1)
    legacy_save = "  const save = () => { try { localStorage.setItem(storageKey, JSON.stringify(state)); } catch (_) {} };"
    progress_save = """  const routineId = storageKey.match(/day\\d+/)?.[0] || 'day1';
  const plannedSeries = trackers.reduce((sum, tracker) => sum + (tracker.dataset.seriesKeys || '').trim().split(/\\s+/).filter(Boolean).length, 0);
  const publishProgress = (force = false) => {
    const hasActivity = Object.keys(state).some((key) => /^e\\d+s\\d+$/.test(key) && state[key] === true) || Boolean(state.__timing?.sessionStartedAt);
    if (!force && !hasActivity) return;
    window.TrainingProgressStore?.capture({
      routineId,
      state,
      totalExercises: trackers.length,
      totalSeries: plannedSeries
    });
  };
  const save = () => {
    try { localStorage.setItem(storageKey, JSON.stringify(state)); }
    catch (error) { window.dispatchEvent(new CustomEvent('training-storage-error', { detail: { error } })); }
    publishProgress(true);
  };
  publishProgress();"""
    if legacy_save in source:
        source = source.replace(legacy_save, progress_save, 1)
    elif 'const publishProgress = () =>' not in source:
        raise RuntimeError("No se encontró el guardado de progreso esperado")
    marker = f"{newline}<!-- 6 -->"
    if marker not in source:
        raise RuntimeError("No se encontró el punto de inserción antes de la tarjeta 6")
    if '<div class="num">4</div>' not in source and '<div class="num">5</div>' not in source:
        source = source.replace(marker, newline + CARDS_4_5.replace("\n", newline) + marker, 1)
    elif '<div class="num">4</div>' not in source or '<div class="num">5</div>' not in source:
        raise RuntimeError("Solo existe una de las tarjetas 4 o 5; se evita alterar una tarjeta parcial")
    for exercise in (4, 5):
        card_start = source.index(f"<!-- {exercise} -->")
        card_end = source.index(f"<!-- {exercise + 1} -->", card_start)
        card = source[card_start:card_end]
        technique_start = card.find('<div class="techSteps">')
        tracker_start = card.find('<div class="exerciseTracker"')
        if technique_start < 0 or tracker_start < 0:
            raise RuntimeError(f"La tarjeta {exercise} no contiene técnica y contador de series")
        depth = 0
        technique_end = None
        for tag in re.finditer(r"<div\b[^>]*>|</div>", card[technique_start:]):
            depth += 1 if not tag.group(0).startswith("</") else -1
            if depth == 0:
                technique_end = technique_start + tag.end()
                break
        if technique_end is None:
            raise RuntimeError(f"La técnica de la tarjeta {exercise} tiene etiquetas div sin balance")
        technique = card[technique_start:technique_end]
        card = card[:technique_start] + card[technique_end:]
        tracker_start = card.find('<div class="exerciseTracker"')
        card = card[:tracker_start] + technique + newline + card[tracker_start:]
        card = re.sub(r"\n</div></article>(\s*)$", r"\n</article>\1", card)
        card = card.replace('</button></div></div></div></div>', '</button></div></div></div>', 1)
        source = source[:card_start] + card + source[card_end:]
    source = source.replace('images/0592-b6hQYMb-start.jpg', 'images/0592-b6hQYMb.jpg')
    card6_start = source.index('<!-- 6 -->')
    main_end = source.index('</main>', card6_start)
    source = source[:card6_start] + DAY1_CARD6.replace("\n", newline) + newline + source[main_end:]
    source = source.replace(newline + '</div></article>' + newline + '</main>', newline + '</article>' + newline + '</main>', 1)
    source = source.replace(
        'Siguiente: 06 · Press de pecho complementario',
        'Siguiente: 06 · Curl de bíceps sentado en máquina',
    )
    source = source.replace(' · pecho complementario', ' · curl sentado en máquina')
    source = source.replace(
        'trabajo complementario de deltoides posterior y pecho.',
        'trabajo complementario de deltoides posterior y un segundo patrón de bíceps.',
    )
    source = source.replace(
        'Con trabajo complementario de deltoides posterior y pecho',
        'Con trabajo complementario de deltoides posterior y curl sentado de bíceps',
    )
    if '<div class="muscleDayItem" data-muscle-focus="pectoralis-major"' not in source:
        grid_close = f'{newline}</div>{newline}</div></div>{newline}{newline}</header>'
        if grid_close not in source:
            raise RuntimeError("No se encontró el cierre del panel muscular del Día 1")
        source = source.replace(
            grid_close,
            newline + MUSCLE_PECTORAL.replace("\n", newline) + grid_close,
            1,
        )
    source = source.replace(
        (
            'gif:"../medios_publicados/ejercicios-compartido/videos/0577-T0yTjgW.gif",\n'
            '      thumbnail:"../medios_publicados/ejercicios-compartido/images/0577-T0yTjgW.jpg",\n'
            '      key:"PRESS DE PECHO COMPLEMENTARIO",\n'
            '      alt:"GIF de press de pecho sentado en máquina"'
        ).replace("\n", newline),
        (
            'gif:"../medios_publicados/ejercicios-compartido/videos/0575-q6y3OhV.gif",\n'
            '      thumbnail:"../medios_publicados/ejercicios-compartido/images/0575-q6y3OhV.jpg",\n'
            '      key:"CURL DE BÍCEPS SENTADO EN MÁQUINA",\n'
            '      alt:"GIF de curl de bíceps sentado en máquina con agarre supino"'
        ).replace("\n", newline),
    )
    for exercise, rest, duration in ((4, "1.5 min", "5–7 min"), (5, "1.5–2 min", "5–7 min")):
        tracker_marker = f'<div class="exerciseTracker" data-exercise="{exercise}"'
        rest_metric = f'<div class="metric rest"><div class="metricText"><div class="metricLabel">Descanso</div><div class="metricVal"><strong class="timeCue">{rest}</strong></div></div></div>'
        duration_metric = f'<div class="metric duration"><div class="metricText"><div class="metricLabel">Duración aprox.</div><div class="metricVal"><strong class="timeCue">{duration}</strong></div></div></div>'
        source = re.sub(
            rf'(<!-- {exercise} -->\s*<article class="card">.*?)(<div class="metric rest">).*?(?={re.escape(tracker_marker)})',
            rf'\g<1>{rest_metric}{duration_metric}</div></div>',
            source,
            count=1,
            flags=re.S,
        )
    source = source.replace(' rep.</div>', ' repeticiones</div>')
    source = standardize_muscle_visuals(source)
    source = sanitize_canonical_metadata(source)
    source = apply_battery_motion(source, newline)
    with HTML.open("w", encoding="utf-8", newline="") as handle:
        handle.write(source)


if __name__ == "__main__":
    main()
