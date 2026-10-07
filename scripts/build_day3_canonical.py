from __future__ import annotations

import re
from pathlib import Path

from standardize_muscle_visuals import sanitize_canonical_metadata, standardize_muscle_visuals


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html"
OUTPUT = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html"
IMAGE_ASSETS = ROOT / "data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images"


EXERCISES = [
    {
        "title": "PRESS DE PECHO SENTADO EN MÁQUINA",
        "zone": "PECHO · PECTORAL MAYOR",
        "equipment": "press sentado con respaldo y empuñaduras independientes",
        "repo": "0577-T0yTjgW",
        "series": 4,
        "reps": "6–10",
        "rest": "2–3 min",
        "duration": "12–15 min",
        "focus": "Pectoral mayor; asisten tríceps y deltoides anterior",
        "setup": "Ajusta el asiento para que las empuñaduras queden aproximadamente a la altura media del pecho. Apoya espalda, pelvis y pies; mantén las muñecas neutras.",
        "execution": "Empuja las empuñaduras hacia delante siguiendo la trayectoria de la máquina. Extiende casi por completo sin despegar la espalda ni adelantar los hombros.",
        "rhythm": "Exhala al empujar y regresa en 2–3 s hasta un estiramiento cómodo, sin rebote.",
        "avoid": "Despegar la pelvis, abrir los codos a 90°, bloquear con golpe los codos o usar impulso del tronco.",
    },
    {
        "title": "PRESS INCLINADO CONVERGENTE EN MÁQUINA",
        "zone": "PECHO · PORCIÓN CLAVICULAR",
        "equipment": "press inclinado convergente con brazos independientes",
        "repo": "1299-jHAnWmT",
        "series": 3,
        "reps": "8–12",
        "rest": "2–3 min",
        "duration": "10–13 min",
        "focus": "Pectoral mayor, con énfasis clavicular; asisten deltoides anterior y tríceps",
        "setup": "Regula el asiento y el respaldo para que las empuñaduras comiencen entre la parte alta y media del pecho. Mantén glúteos y espalda apoyados.",
        "execution": "Empuja en una trayectoria convergente sin perder el apoyo del torso. Deja que los codos sigan el plano natural de la máquina, sin forzar el hombro hacia atrás.",
        "rhythm": "Empuja con control y vuelve en 2–3 s; pausa brevemente cuando las empuñaduras se acerquen sin chocar.",
        "avoid": "Usar una inclinación excesiva, arquear la zona lumbar, rebotar en el fondo o convertirlo en un press de hombro.",
    },
    {
        "title": "PEC DECK / CONTRACTOR DE PECHO",
        "zone": "PECHO · ADUCCIÓN HORIZONTAL",
        "equipment": "pec deck / máquina de aperturas sentada",
        "repo": "0596-v3xmPAR",
        "series": 3,
        "reps": "10–15",
        "rest": "90–120 s",
        "duration": "7–9 min",
        "focus": "Pectoral mayor; deltoides anterior como sinergista",
        "setup": "Ajusta el asiento para que los brazos queden aproximadamente a la altura del hombro. Apoya la espalda y conserva una ligera flexión de codo.",
        "execution": "Cierra los brazos mediante aducción horizontal del húmero, sin encoger los hombros. Abre sólo hasta el rango que puedas controlar sin dolor anterior.",
        "rhythm": "Cierra en 1–2 s, pausa medio segundo y regresa en 2–3 s sin perder el contacto con el respaldo.",
        "avoid": "Convertirlo en un movimiento de manos, abrir demasiado, lanzar los brazos hacia delante o elevar los hombros.",
    },
    {
        "title": "PRESS DE HOMBRO EN MÁQUINA",
        "zone": "HOMBRO · DELTOIDES ANTERIOR Y LATERAL",
        "equipment": "press vertical sentado con respaldo y brazos independientes",
        "repo": "2318-dNFYIU1",
        "series": 3,
        "reps": "8–12",
        "rest": "2 min",
        "duration": "8–10 min",
        "focus": "Deltoides anterior y lateral; asiste el tríceps",
        "setup": "Ajusta el asiento para comenzar con las empuñaduras cerca de hombros u orejas. Apoya espalda y pelvis, y fija los pies al suelo.",
        "execution": "Empuja hacia arriba en el plano de la máquina hasta una extensión cómoda. Mantén antebrazos relativamente verticales y el torso estable.",
        "rhythm": "Exhala al subir y desciende en 2–3 s, sin perder el respaldo ni colapsar los hombros.",
        "avoid": "Hiperextender la zona lumbar, bajar a un rango doloroso, encoger los hombros o usar rebote de piernas.",
    },
    {
        "title": "ELEVACIÓN LATERAL EN MÁQUINA",
        "zone": "HOMBRO · DELTOIDES LATERAL",
        "equipment": "máquina de elevación lateral con apoyos para brazos",
        "repo": "0584-dRTfGZT",
        "series": 3,
        "reps": "10–15",
        "rest": "60–90 s",
        "duration": "7–9 min",
        "focus": "Deltoides lateral; trapecio sólo como estabilizador",
        "setup": "Alinea el eje de la máquina con la articulación del hombro y apoya el torso según el diseño. Usa una carga que permita iniciar sin impulso.",
        "execution": "Eleva los brazos en el plano permitido por la máquina hasta una altura cómoda, manteniendo el cuello largo y los hombros bajos.",
        "rhythm": "Sube en 1–2 s y desciende en 2–3 s; evita descansar completamente entre repeticiones si eso rompe el control.",
        "avoid": "Encoger los hombros, balancear el tronco, elevar por encima del rango cómodo o convertirlo en un encogimiento.",
    },
    {
        "title": "JALÓN DE TRÍCEPS EN POLEA",
        "zone": "BRAZO · TRÍCEPS",
        "equipment": "polea alta con cuerda",
        "repo": "0200-dU605di",
        "series": 3,
        "reps": "8–12",
        "rest": "75–90 s",
        "duration": "7–9 min",
        "focus": "Tríceps braquial; extensión de codo",
        "setup": "Coloca la polea por encima de la cabeza y toma la cuerda con el torso erguido. Mantén los codos próximos al costado y los pies estables.",
        "execution": "Extiende los codos hacia abajo sin inclinarte para vencer la carga. Separa ligeramente las puntas de la cuerda al final si resulta natural.",
        "rhythm": "Exhala al extender y regresa en 2–3 s hasta una flexión cómoda del codo.",
        "avoid": "Empujar con el peso corporal, adelantar los codos, redondear la espalda o perder tensión por rebote.",
    },
    {
        "title": "EXTENSIÓN DE TRÍCEPS SOBRE CABEZA CON CUERDA",
        "zone": "BRAZO · TRÍCEPS, CABEZA LARGA",
        "equipment": "polea baja o media con cuerda, de espaldas a la estación",
        "repo": "0194-2IxROQ1",
        "series": 3,
        "reps": "10–15",
        "rest": "75–90 s",
        "duration": "7–9 min",
        "focus": "Tríceps braquial con el brazo elevado; énfasis práctico en la cabeza larga",
        "setup": "Toma la cuerda por encima o detrás de la cabeza y adopta una postura estable. Mantén costillas controladas y codos orientados al frente.",
        "execution": "Extiende los codos hasta acercar los brazos a la línea del torso, sin mover los hombros. Regresa permitiendo flexión controlada del codo.",
        "rhythm": "Extiende en 1–2 s y vuelve en 2–3 s, sin perder la posición del tronco.",
        "avoid": "Abrir excesivamente los codos, arquear la espalda, convertirlo en un pullover o forzar el rango del hombro.",
    },
]


def between(text: str, start: str, end: str) -> str:
    start_index = text.index(start)
    end_index = text.index(end, start_index) + len(end)
    return text[start_index:end_index]


def replace_all(text: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def build_header(template: str) -> str:
    header = between(template, '<header class="hero">', "</header>")
    header = replace_all(
        header,
        {
            "DÍA 1 · TIRÓN: ESPALDA Y BÍCEPS": "DÍA 3 · EMPUJE: PECHO, HOMBROS Y TRÍCEPS",
            "Tirones verticales y remos · deltoides posterior · bíceps · pecho complementario": "Empujes horizontales y verticales · deltoides lateral · tríceps",
            "Tren superior": "Tren superior",
            "Máquinas + fotos reales": "Máquinas + guía visual",
            "Perfil intermedio. Tren superior con prioridad en espalda y bíceps; deltoides posterior y pecho complementarios.": "Perfil intermedio. Tren superior con prioridad en pecho; hombros y tríceps reciben trabajo específico.",
        },
    )
    header = re.sub(
        r'(<div class="subtitle">).*?(</div>)',
        r'\1Empujes horizontales y verticales · deltoides lateral · tríceps\2',
        header,
        count=1,
        flags=re.S,
    )
    header = re.sub(
        r'(<div class="heroSummaryText">).*?(</div>)',
        r'\1Rutina de <b>tren superior</b> equilibrada, con trabajo de pecho, hombros y tríceps.\2',
        header,
        count=1,
        flags=re.S,
    )
    grid = re.search(r'<div class="muscleDayGrid"[^>]*>.*?</div>\s*</div></div>', header, flags=re.S)
    if not grid:
        raise ValueError("No se encontró la cuadrícula muscular de la cabecera")
    new_grid = """<div class="muscleDayGrid">
<div class="muscleDayItem" data-muscle-visual="upper-anterior"><span class="muscleDayVisual anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior del tórax" decoding="async" fetchpriority="high"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#ff9da2">PECHO</span><span class="muscleName">Pectoral mayor</span></span></div>
<div class="muscleDayItem" data-muscle-visual="upper-anterior"><span class="muscleDayVisual anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior del hombro" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#7ff0cc">HOMBRO</span><span class="muscleName">Deltoides</span></span></div>
<div class="muscleDayItem" data-muscle-visual="upper-anterior"><span class="muscleDayVisual anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior del brazo" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#ffd277">TRÍCEP</span><span class="muscleName">Tríceps</span></span></div>
</div>
</div></div>"""
    header = header[: grid.start()] + new_grid + header[grid.end() :]
    return re.sub(
        r'(<div class="heroSummaryText"><b>Perfil intermedio\.</b>).*?(</div>)',
        r'\1 Tren superior con prioridad en pecho; hombros y tríceps reciben trabajo específico.\2',
        header,
        count=1,
        flags=re.S,
    )


def build_section(template: str, start: str, replacements: dict[str, str]) -> str:
    end = "</section>"
    section = between(template, start, end)
    return replace_all(section, replacements)


def build_warmup(template: str) -> str:
    section = build_section(
        template,
        '<section class="warmupGuide"',
        {
            'data-fix="day1-warmup-guide"': 'data-fix="day3-warmup-guide"',
            "17–19 min": "18–20 min",
            "16–17 min": "16 min",
            "1–2 min": "2 min",
            "prepara espalda, hombros y codos": "prepara hombros, escápulas y codos",
            "Jalón al pecho": "Press de pecho",
            "espalda y bíceps": "pecho, hombros y tríceps",
            "al tirar": "al empujar",
        },
    )
    return section


def build_card(item: dict[str, object], index: int) -> str:
    title = str(item["title"])
    zone = str(item["zone"])
    equipment = str(item["equipment"])
    repo = str(item["repo"])
    static_start = f"../medios_publicados/ejercicios-compartido/images/{repo}-start.jpg"
    static_final = f"../medios_publicados/ejercicios-compartido/images/{repo}-final.jpg"
    series = int(item["series"])
    next_button = (
        f'<button type="button" class="nextExerciseCue" data-next="{index + 2}" hidden><span class="nextArrow" aria-hidden="true">↓</span> Siguiente: {EXERCISES[index + 1]["title"].title()}</button>'
        if index < len(EXERCISES) - 1
        else ""
    )
    warmup = (
        '<button type="button" class="setButton warmupSet" data-key="w1" aria-pressed="false">Calentamiento</button>'
        if index == 0
        else ""
    )
    keys = " ".join(f"e{index + 1}s{n}" for n in range(1, series + 1))
    return f'''<article class="card" data-exercise-index="{index + 1}">
<div aria-hidden="true" class="cardGlow"></div>
<div class="meta">
<div class="metaTop"><div class="num">{index + 1}</div></div>
<div class="exTitle">{title}</div>
<div class="zone">{zone}</div><div class="chipRow"><span class="infoChip chipExercise">Ejercicio {index + 1}</span><span class="infoChip">{zone.split(" · ")[0]}</span><span class="infoChip">{zone.split(" · ")[-1]}</span></div>
<div class="machinePill"><span class="pillIcon" aria-hidden="true">▣</span><span class="pillText">{equipment}</span></div>
 </div>
<div class="visual">
<div class="referenceRow">
<div class="machineRefBox"><img alt="Vista aislada de la máquina asociada al patrón {title.lower()}" src="../medios_publicados/ejercicios-compartido/images/{repo}-machine-only.webp" loading="lazy"/><span class="refTag">VISTA AISLADA · ILUSTRACIÓN DE APOYO</span></div>
<div class="muscleRefBox"><div class="muscleInfo"><span class="primary"><span class="muscleTag">ENFOQUE</span> {str(item["focus"])}</span><span class="secondary">La vista aislada editada es apoyo visual; no confirma la identidad del equipo instalado en el gimnasio.</span></div></div>
</div>
<div class="photoTitleRow"><b>POSICIÓN Y RECORRIDO</b></div>
<div class="phaseRow">
<div class="phaseCol"><div class="phaseLabel">Inicio · imagen estática</div><div class="photo techniqueVisual"><img class="realphoto day3StaticFrame" src="{static_start}" alt="{title} · posición inicial estática" loading="lazy"/><div class="brokenFallback">Imagen estática inicial no disponible.</div></div><div class="source">Inicio · posición de partida · sin rebotes</div></div>
<div class="swap" aria-hidden="true">→</div>
<div class="phaseCol"><div class="phaseLabel">Final · imagen estática</div><div class="photo techniqueVisual"><img class="realphoto day3StaticFrame" src="{static_final}" alt="{title} · posición final estática" loading="lazy"/><div class="brokenFallback">Imagen estática final no disponible.</div></div><div class="source">Final · contracción controlada · regreso lento</div></div>
</div>
<div class="gifProof"><div class="gifProofTitle">GIF · RECORRIDO COMPLETO</div><div class="photo techniqueVisual gifPreview"><img class="realphoto day3ExerciseGif" src="../medios_publicados/ejercicios-compartido/videos/{repo}.gif" data-static-src="{static_start}" alt="{title} · GIF local del recorrido completo" loading="lazy"/><div class="brokenFallback">GIF no disponible; se conserva la referencia estática.</div></div><div class="videoProof"><span>GIF local · {repo} · secuencia de referencia técnica</span></div></div>
</div>
<div class="coach"><div class="coachRibbon"><span class="coachRibbonIcon" aria-hidden="true">✓</span><span>Checklist técnico</span></div><div class="coachHeader">Técnica clave</div><div class="exerciseQuickSummary" data-exercise-quick-summary aria-label="Resumen del ejercicio"></div>
<div class="metrics"><div class="metric series"><div class="metricText"><div class="metricLabel">Series</div><div class="metricVal">{series} series</div></div></div><div class="metric reps"><div class="metricText"><div class="metricLabel">Repeticiones</div><div class="metricVal">{item["reps"]} repeticiones</div></div></div><div class="metric rest"><div class="metricText"><div class="metricLabel">Descanso</div><div class="metricVal"><strong class="timeCue">{item["rest"]}</strong></div></div></div><div class="metric duration"><div class="metricText"><div class="metricLabel">Duración aprox.</div><div class="metricVal"><strong class="timeCue">{item["duration"]}</strong></div></div></div></div>
<div class="exerciseTracker" data-exercise="{index + 1}" data-series-keys="{keys}"><div class="exerciseTrackerHead"><span>Contador de series</span><span class="exerciseTrackerMeta"><strong class="exerciseProgress">0/{series}</strong><span class="exerciseStatus" hidden><span class="completionMark" aria-hidden="true">✓</span> Completado</span></span></div><div class="exerciseSetButtons" role="group" aria-label="Contador de series del ejercicio {index + 1}">{warmup}<button type="button" class="completeSetButton" aria-label="Completar serie 1 de {series}">Completar serie 1 de {series}</button><button type="button" class="machinePendingToggle" data-pending-key="p{index + 1}" aria-pressed="false">⚠ Máquina ocupada</button><div class="nextExerciseRow">{next_button}</div></div></div>
<div class="techSteps"><div class="techStep setup"><div class="techStepTitle">1 · Ajuste</div><div class="techStepText">{item["setup"]}</div></div><div class="techStep move"><div class="techStepTitle">2 · Ejecución</div><div class="techStepText">{item["execution"]}</div></div><div class="techStep control"><div class="techStepTitle">3 · Ritmo y respiración</div><div class="techStepText">{item["rhythm"]}</div></div><div class="techStep warning"><div class="techStepTitle">⚠ Evita</div><div class="techStepText">{item["avoid"]}</div></div></div></div>
</article>'''


def build_day3_script(template: str) -> str:
    tail_start = template.rfind("</div>\n<script")
    if tail_start == -1:
        raise ValueError("No se encontró el cierre de la página y los scripts")
    tail = template[tail_start : template.rfind("</body>")]
    tail = re.sub(r'<script data-fix="day1-gif-candidates">.*?</script>', '', tail, count=1, flags=re.S)
    tail = re.sub(r'<footer class="sessionFooter".*?</footer>', '', tail, count=1, flags=re.S)
    # El template de Día 1 conserva un script de reparación de medios históricos.
    # Sus rutas de remo/curl no pertenecen a Día 3 y podrían sobrescribir sus
    # finales estáticos; se conserva únicamente la parte genérica de resumen.
    tail = re.sub(
        r'  var mediaBase = .*?  function normalize',
        '  function normalize',
        tail,
        count=1,
        flags=re.S,
    )
    tail = re.sub(
        r'  function repairMachineReference\(\).*?\n  function installSummaryStyle',
        '  function installSummaryStyle',
        tail,
        count=1,
        flags=re.S,
    )
    tail = tail.replace('  repairMachineReference();\n  repairMissingFinals();\n', '')
    tail = tail.replace('data-fix="day1-warmup-guide"', 'data-fix="day3-warmup-guide"')
    tail = tail.replace("/6 ejercicios", "/7 ejercicios")
    tail = tail.replace("de 6", "de 7")
    tail = tail.replace("0/6 ejercicios", "0/7 ejercicios")
    tail = tail.replace("/20 series", "/22 series")
    tail = tail.replace("doneSeries}/20", "doneSeries}/22")
    tail = tail.replace("completedExercises === 6", "completedExercises === 7")
    tail = tail.replace("completedExercises >= 6", "completedExercises >= 7")
    tail = tail.replace("fitlovers-day1-series-v1", "fitlovers-day3-series-v1")
    tail = tail.replace("fitlovers-day1-sound-v1", "fitlovers-day3-sound-v1")
    tail = tail.replace("fitlovers-day1-motivation-v1", "fitlovers-day3-motivation-v1")
    tail += '''<script data-fix="day3-local-gif-fallback">
(function(){
  const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('.day3ExerciseGif').forEach(function(img){
    const staticSrc = img.dataset.staticSrc;
    let staticAttempted = false;
    const staticUrl = staticSrc ? new URL(staticSrc, document.baseURI).href : '';
    const useStatic = function(){
      if(staticAttempted || !staticUrl) return;
      staticAttempted = true;
      img.hidden = false;
      img.style.display = '';
      img.src = staticUrl;
    };
    const showBroken = function(){
      if(!staticAttempted && staticUrl){ useStatic(); return; }
      img.hidden = true;
      img.style.display = 'none';
      const fallback = img.closest('.photo')?.querySelector('.brokenFallback');
      if(fallback) fallback.style.display = 'flex';
    };
    // El template asigna un onerror genérico que oculta la imagen. Día 3 usa
    // un fallback estático explícito, por lo que este manejador lo reemplaza.
    img.onerror = null;
    img.addEventListener('error', showBroken);
    if(reduced) useStatic();
    else if(img.complete && img.naturalWidth === 0) showBroken();
  });
})();
</script>'''
    return tail


def validate_static_assets() -> None:
    missing = []
    for item in EXERCISES:
        repo = str(item["repo"])
        for suffix in ("-start.jpg", "-final.jpg", "-machine-only.webp"):
            path = IMAGE_ASSETS / f"{repo}{suffix}"
            if not path.exists():
                missing.append(str(path.relative_to(ROOT)))
    if missing:
        raise FileNotFoundError("Faltan cuadros estáticos derivados: " + ", ".join(missing))


def main() -> None:
    validate_static_assets()
    template = TEMPLATE.read_text(encoding="utf-8")
    head = template[: template.index("</head>") + len("</head>")]
    head = replace_all(
        head,
        {
            'data-label="Día 1 · Tirón: espalda y bíceps · v1 responsive"': 'data-label="Día 3 · Empuje: pecho, hombros y tríceps · v1 responsive"',
            "<title>Día 1 · Tirón: espalda y bíceps · v1 responsive</title>": "<title>Día 3 · Empuje: pecho, hombros y tríceps · v1 responsive</title>",
            'data-fix="day1-gif-candidates"': 'data-fix="day3-gif-layout"',
        },
    )
    head = head.replace(
        "</head>",
        """<style data-fix="day3-static-and-gif-layout">
.phaseRow .day3StaticFrame{object-fit:contain!important;background:#fff!important}
.gifProof{margin-top:12px;padding:10px 12px;border:1px solid rgba(45,97,121,.55);border-radius:14px;background:rgba(12,24,34,.68)}
.gifProofTitle{font-size:12px;font-weight:900;letter-spacing:.6px;color:#72D4F0;margin-bottom:7px}
.gifPreview{max-width:240px;margin:0 auto;aspect-ratio:1/1}
.gifPreview img.day3ExerciseGif{object-fit:contain!important}
.gifProof .videoProof{margin-top:7px!important}
@media(max-width:700px){.gifPreview{max-width:220px}}
</style></head>""",
        1,
    )

    quick_rules = build_section(
        template,
        '<section class="footer quickRules"',
        {
            "espalda y bíceps": "pecho, hombros y tríceps",
            "tirones": "empujes",
            "remo": "press",
            "Jalón": "Press",
            "1–2 s al tirar": "1–2 s al empujar",
            "al tirar": "al empujar",
            "Si cae la postura": "Si pierdes el apoyo o el control",
        },
    )
    summary = build_section(
        template,
        '<section class="routineSummary"',
        {
            "6 ejercicios · 20 series efectivas": "7 ejercicios · 22 series efectivas",
            "Día 1": "Día 3",
            "Tirón · espalda y bíceps": "Empuje · pecho, hombros y tríceps",
            "75–95 min": "83–98 min",
            "60 s–2.5 min": "60–180 s",
        },
    )
    gamification = build_section(template, '<section class="sessionGamification"', {"0/20": "0/22", "20 series": "22 series"})
    prep = build_section(template, '<section class="prep">', {"16–17 min": "16 min", "3 + 1": "3 + 2", "Jalón: series + calentamiento": "Press: aproximación"})
    dashboard = build_section(
        template,
        '<section class="sessionDashboard">',
        {
            "75–95 min": "83–98 min",
            "20 series efectivas": "22 series efectivas",
            "4 + 4 + 3 + 3 + 3 + 3 series": "4 + 3 + 3 + 3 + 3 + 3 + 3 series",
            "Tirón · espalda y bíceps": "Empuje · pecho, hombros y tríceps",
            "Con trabajo complementario de deltoides posterior y pecho": "Con volumen directo para pecho, hombros y tríceps",
            "De 60 s a 2.5 min según el ejercicio": "De 60 s a 3 min según el ejercicio",
        },
    )
    note = build_section(
        template,
        '<section class="note notePanel"',
        {
            "Puntos clave de la sesión": "Puntos clave del Día 3",
            "La serie de aproximación prepara el movimiento y no cuenta como efectiva.": "Las series de aproximación preparan el movimiento y no cuentan como efectivas.",
            "RIR 2–3 al inicio y 1–2 al final": "RIR 1–2 en la mayoría de las series",
            "Si cae la postura": "Si pierdes el apoyo o el control",
        },
    )
    cards = "\n".join(build_card(item, index) for index, item in enumerate(EXERCISES))
    overlays = between(template, '<section class="sessionCompletionPanel"', "</aside>")
    overlays = re.sub(r'<footer class="sessionFooter".*?</footer>', "", overlays, count=1, flags=re.S)
    overlays = replace_all(
        overlays,
        {
            "0/6 ejercicios · 0/20 series": "0/7 ejercicios · 0/22 series",
            "0 pendientes": "22 pendientes",
        },
    )
    footer = between(template, '<footer class="sessionFooter"', "</footer>")
    footer = replace_all(footer, {"Día 1": "Día 3", "espalda y bíceps": "pecho, hombros y tríceps", "18 series": "22 series"})
    body = "\n".join([
        "<body>",
        '<div class="page">',
        build_header(template),
        quick_rules,
        build_warmup(template),
        summary,
        gamification,
        prep,
        dashboard,
        note,
        '<main class="cards">',
        cards,
        "</main>",
        overlays,
        footer,
        build_day3_script(template),
        "</div>",
        "</body>",
        "</html>",
    ])
    if body.count('<article class="card" data-exercise-index="') != 7:
        raise ValueError("El Día 3 debe contener exactamente 7 tarjetas")
    if body.count('<main class="cards">') != 1:
        raise ValueError("El HTML canónico debe envolver las tarjetas en un único main.cards")
    if body.count('<footer class="sessionFooter"') != 1 or '<footer class="footer">' in body:
        raise ValueError("El HTML canónico debe usar únicamente el footer de acciones de sesión")
    if body.count('realphoto day3StaticFrame') != 14:
        raise ValueError("Cada tarjeta debe conservar una pareja Inicio/Final estática")
    if body.count('realphoto day3ExerciseGif') != 7:
        raise ValueError("Cada tarjeta debe conservar un GIF local de recorrido")
    if body.count('-machine-only.webp') != 7:
        raise ValueError("Cada tarjeta debe mostrar una vista aislada de máquina")
    if "0/22 series" not in body or "22 series efectivas" not in body:
        raise ValueError("El volumen de 22 series no quedó sincronizado")
    if "0/6 ejercicios · 0/20 series" in body or "fitlovers-day1-series-v1" in body:
        raise ValueError("El estado inicial o el almacenamiento conserva referencias del Día 1")
    if '<script data-fix="day1-gif-candidates">' in body:
        raise ValueError("No debe quedar el inyector de GIFs del Día 1")
    if "machineOnlyCurl" in body or "finalAssets" in body:
        raise ValueError("No deben quedar reparaciones de medios específicas del Día 1")
    if "confirma directamente la identidad de la máquina del gimnasio" in body:
        raise ValueError("La vista aislada no debe presentarse como confirmación del equipo real")
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
