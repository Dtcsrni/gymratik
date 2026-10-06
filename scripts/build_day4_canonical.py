"""Genera la rutina canónica del Día 4 desde la plantilla compartida del Día 1."""

from __future__ import annotations

import re
from pathlib import Path

from build_day2_canonical import build_warmup as build_lower_warmup
from build_day3_canonical import between, build_section, build_day3_script, replace_all
from build_day4_barbell_rdl_media import main as build_barbell_rdl_media
from standardize_muscle_visuals import sanitize_canonical_metadata, standardize_muscle_visuals


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html"
OUTPUT = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_4_Pierna_Equilibrio_V1.html"
MEDIA_ROOT = "../medios_publicados/rutinas_autocontenidas/dia4_media_generated"

EXERCISES = [
    {
        "title": "PRENSA UNILATERAL ALTERNA",
        "zone": "PIERNA · CUÁDRICEPS",
        "equipment": "prensa de piernas con plataforma y apoyo estable",
        "repo": "2287-V07qpXy",
        "series": 3,
        "reps": "8–12 por lado",
        "rest": "2–3 min",
        "duration": "10–13 min",
        "focus": "Cuádriceps; asisten isquiosurales y glúteos",
        "setup": "Ajusta el respaldo y la plataforma para que la rodilla pueda flexionarse sin perder el apoyo de la pelvis. Empieza con una carga que permita controlar cada lado.",
        "execution": "Empuja con un pie sin bloquear la rodilla y desciende hasta el rango que puedas mantener estable. Alterna lados sólo después de completar el objetivo del lado activo.",
        "rhythm": "Empuja en 1–2 s y desciende en 2–3 s; mantén el talón y la pelvis apoyados.",
        "avoid": "Despegar la pelvis, colapsar la rodilla hacia dentro, rebotar en el fondo o usar una carga que obligue a compensar con el tronco.",
    },
    {
        "title": "PESO MUERTO RUMANO CON BARRA",
        "zone": "CADERA · GLÚTEOS E ISQUIOSURALES",
        "equipment": "barra libre y discos · bisagra de cadera",
        "repo": "barbell-rdl-v1",
        "series": 3,
        "reps": "8–12",
        "rest": "2–3 min",
        "duration": "10–13 min",
        "focus": "Glúteos e isquiosurales; bisagra de cadera",
        "setup": "Pies al ancho de cadera; barra sobre el mediopié. Tómala apenas por fuera de las piernas y empieza de pie, con rodillas suaves, abdomen firme y espalda neutra.",
        "execution": "Desplaza la cadera atrás y baja la barra pegada a muslos y piernas. Detén el descenso cuando notes tensión clara en isquiosurales antes de redondear la espalda; vuelve llevando la cadera al frente.",
        "rhythm": "Baja en 2–3 s y sube en 1–2 s. Mantén los brazos largos y la barra rozando las piernas.",
        "avoid": "Convertirlo en sentadilla, alejar la barra, doblar más las rodillas durante el descenso, redondear la espalda o hiperextender al subir.",
    },
    {
        "title": "CURL FEMORAL TUMBADO",
        "zone": "PIERNA · ISQUIOSURALES",
        "equipment": "máquina de curl femoral tumbado",
        "repo": "0586-17lJ1kr",
        "series": 4,
        "reps": "8–12",
        "rest": "90–120 s",
        "duration": "10–12 min",
        "focus": "Isquiosurales; pantorrilla como sinergista",
        "setup": "Alinea la rodilla con el eje de la máquina y coloca el rodillo por encima del talón. Apoya cadera y tronco, con el abdomen activo.",
        "execution": "Flexiona la rodilla llevando el rodillo hacia los glúteos sin levantar la pelvis. Regresa hasta una extensión cómoda manteniendo tensión.",
        "rhythm": "Acerca el rodillo en 1–2 s y regresa en 2–3 s; evita que el peso caiga al final.",
        "avoid": "Despegar la cadera, acortar el recorrido para mover más carga, golpear el tope o apuntar los pies de forma exagerada.",
    },
    {
        "title": "ABDUCCIÓN DE CADERA SENTADA",
        "zone": "CADERA · ABDUCTORES",
        "equipment": "máquina de abducción de cadera sentada",
        "repo": "0597-CHpahtl",
        "series": 2,
        "reps": "12–20",
        "rest": "60–90 s",
        "duration": "6–8 min",
        "focus": "Abductores y glúteo medio; glúteo mayor como asistente",
        "setup": "Ajusta el respaldo y el punto de inicio para no forzar la cadera. Mantén la pelvis neutra y el tronco apoyado.",
        "execution": "Separa las rodillas con control sin inclinarte para ganar recorrido. Regresa lentamente hasta el límite cómodo sin perder la tensión.",
        "rhythm": "Abre en 1–2 s, pausa breve y cierra en 2–3 s sin dejar caer las placas.",
        "avoid": "Rebotar, inclinar el tronco, forzar una apertura dolorosa o convertir cada repetición en un impulso.",
    },
    {
        "title": "ADUCCIÓN DE CADERA SENTADA",
        "zone": "CADERA · ADUCTORES",
        "equipment": "máquina de aducción de cadera sentada",
        "repo": "0598-oHsrypV",
        "series": 2,
        "reps": "12–20",
        "rest": "60–90 s",
        "duration": "6–8 min",
        "focus": "Aductores; glúteos e isquiosurales como estabilizadores",
        "setup": "Ajusta el inicio a un rango cómodo y apoya espalda y pelvis. Coloca las piernas simétricas antes de iniciar.",
        "execution": "Acerca las rodillas mediante aducción controlada y regresa sin soltar de golpe la carga. Mantén el tronco estable durante todo el recorrido.",
        "rhythm": "Cierra en 1–2 s y abre en 2–3 s; evita descansar completamente entre repeticiones.",
        "avoid": "Forzar el estiramiento, mover la pelvis, separar los pies de los apoyos o golpear el límite de la máquina.",
    },
    {
        "title": "ELEVACIÓN DE PANTORRILLA SENTADA",
        "zone": "PIERNA · PANTORRILLA",
        "equipment": "máquina de elevación de pantorrilla sentada",
        "repo": "0594-bOOdeyc",
        "series": 3,
        "reps": "10–15",
        "rest": "60–90 s",
        "duration": "7–9 min",
        "focus": "Tríceps sural; énfasis práctico en sóleo",
        "setup": "Coloca la almohadilla sobre los muslos y la parte anterior del pie en el apoyo, dejando el talón libre. Asegura la posición antes de liberar la carga.",
        "execution": "Eleva el talón con el tobillo, alcanza una contracción cómoda y desciende hasta un estiramiento controlado sin perder el apoyo del antepié.",
        "rhythm": "Sube en 1–2 s, pausa arriba y baja en 2–3 s; no rebotes en la parte baja.",
        "avoid": "Mover la rodilla para ayudar, rebotar, girar los pies de forma asimétrica o acortar el descenso.",
    },
    {
        "title": "CRUNCH CON ELEVACIÓN DE PIERNAS SENTADA",
        "zone": "CORE · ABDOMINALES",
        "equipment": "máquina de crunch con apoyo de piernas",
        "repo": "0600-PQ2AtC3",
        "series": 3,
        "reps": "10–15",
        "rest": "60–90 s",
        "duration": "7–9 min",
        "focus": "Abdominales; flexores de cadera como asistentes",
        "setup": "Ajusta el asiento y el apoyo para que la pelvis permanezca estable. Coloca manos y pies según la máquina sin tirar del cuello.",
        "execution": "Acerca el tronco y las piernas mediante flexión controlada del tronco, sin despegar la pelvis de forma brusca. Regresa lentamente al inicio.",
        "rhythm": "Cierra en 1–2 s, exhala en la contracción y regresa en 2–3 s sin dejar caer el peso.",
        "avoid": "Jalar de la cabeza, hiperflexionar la columna, usar impulso o convertir el movimiento en una elevación de piernas sin control del tronco.",
    },
]


def build_header(template: str) -> str:
    header = between(template, '<header class="hero">', "</header>")
    header = replace_all(header, {
        "DÍA 1 · TIRÓN: ESPALDA Y BÍCEPS": "DÍA 4 · PIERNA Y CORE: CADERA Y ESTABILIDAD",
        "Máquinas + fotos reales": "Máquinas + guía visual",
        "Perfil intermedio. Tren superior con prioridad en espalda y bíceps; deltoides posterior y pecho complementarios.": "Perfil intermedio. Tren inferior equilibrado con trabajo de rodilla, cadera, pantorrilla y core.",
    })
    header = re.sub(
        r'(<div class="subtitle">).*?(</div>)',
        r'\1Cuádriceps · bisagra de cadera · isquiosurales · cadera · pantorrilla · core\2',
        header,
        count=1,
        flags=re.S,
    )
    header = re.sub(
        r'(<div class="heroSummaryText">).*?(</div>)',
        r'\1Rutina de <b>tren inferior</b> equilibrada, con trabajo de rodilla, cadera, pantorrilla y core.\2',
        header,
        count=1,
        flags=re.S,
    )
    header = header.replace('<span>Tren superior</span>', '<span>Tren inferior</span>', 1)
    grid = re.search(r'<div class="muscleDayGrid"[^>]*>.*?</div>\s*</div></div>', header, flags=re.S)
    if not grid:
        raise ValueError("No se encontró la cuadrícula muscular de la cabecera")
    new_grid = """<div class="muscleDayGrid">
<div class="muscleDayItem" data-muscle-visual="lower-anterior"><span class="muscleDayVisual anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior del muslo" decoding="async" fetchpriority="high"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#ff9da2">CUÁDRI</span><span class="muscleName">Cuádriceps</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-posterior"><span class="muscleDayVisual posterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa posterior de glúteos e isquiosurales" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#7ff0cc">GLÚTEO</span><span class="muscleName">Glúteo mayor</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-posterior"><span class="muscleDayVisual posterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa posterior de los isquiosurales" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#ffd277">ISQUIO</span><span class="muscleName">Isquiosurales</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-anterior"><span class="muscleDayVisual anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior de los abductores" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#ff9da2">ABDUCT</span><span class="muscleName">Abductores</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-anterior"><span class="muscleDayVisual anterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa anterior de los aductores" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#7ff0cc">ADUCT</span><span class="muscleName">Aductores</span></span></div>
<div class="muscleDayItem" data-muscle-visual="lower-posterior"><span class="muscleDayVisual posterior"><img class="muscleDayImage" src="../medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp" alt="Referencia anatómica ilustrativa posterior de la pantorrilla" decoding="async"><span class="muscleDayFallback" hidden>ANATOMÍA</span></span><span class="muscleDayCopy"><span class="muscleCode" style="color:#ffd277">GASTRO</span><span class="muscleName">Gastrocnemio</span></span></div>
</div>
</div></div>"""
    return header[: grid.start()] + new_grid + header[grid.end() :]


def build_card(item: dict[str, object], index: int) -> str:
    title, zone, repo, series = str(item["title"]), str(item["zone"]), str(item["repo"]), int(item["series"])
    next_button = (
        f'<button type="button" class="nextExerciseCue" data-next="{index + 2}" hidden><span class="nextArrow" aria-hidden="true">↓</span> Siguiente: {EXERCISES[index + 1]["title"].title()}</button>'
        if index < len(EXERCISES) - 1 else ""
    )
    warmup = '<button type="button" class="setButton warmupSet" data-key="w1" aria-pressed="false">Calentamiento</button>' if index == 0 else ""
    keys = " ".join(f"e{index + 1}s{n}" for n in range(1, series + 1))
    base = f'''<article class="card" data-exercise-index="{index + 1}">
<div aria-hidden="true" class="cardGlow"></div>
<div class="meta"><div class="metaTop"><div class="num">{index + 1}</div></div><div class="exTitle">{title}</div><div class="zone">{zone}</div><div class="chipRow"><span class="infoChip chipExercise">Ejercicio {index + 1}</span><span class="infoChip">{zone.split(" · ")[0]}</span><span class="infoChip">{zone.split(" · ")[-1]}</span></div><div class="machinePill"><span class="pillIcon" aria-hidden="true">▣</span><span class="pillText">{item["equipment"]}</span></div></div>
<div class="visual"><div class="referenceRow"><div class="machineRefBox"><img alt="Referencia visual del patrón {title.lower()}" src="{MEDIA_ROOT}/{repo}-machine-reference.png" loading="lazy"/><span class="refTag">REFERENCIA VISUAL · NO CONFIRMA EQUIPO</span></div><div class="muscleRefBox"><div class="muscleInfo"><span class="primary"><span class="muscleTag">ENFOQUE</span> {item["focus"]}</span><span class="secondary">La referencia ayuda a identificar el patrón; no confirma la identidad del equipo instalado.</span></div></div></div>
<div class="photoTitleRow"><b>POSICIÓN Y RECORRIDO</b></div><div class="phaseRow"><div class="phaseCol"><div class="phaseLabel">Inicio · imagen estática</div><div class="photo techniqueVisual"><img class="realphoto day4StaticFrame" src="{MEDIA_ROOT}/{repo}-start.jpg" alt="{title} · posición inicial estática" loading="lazy"/><div class="brokenFallback">Imagen estática inicial no disponible.</div></div><div class="source">Inicio · posición de partida · sin rebotes</div></div><div class="swap" aria-hidden="true">→</div><div class="phaseCol"><div class="phaseLabel">Final · imagen estática</div><div class="photo techniqueVisual"><img class="realphoto day4StaticFrame" src="{MEDIA_ROOT}/{repo}-final.jpg" alt="{title} · posición final estática" loading="lazy"/><div class="brokenFallback">Imagen estática final no disponible.</div></div><div class="source">Final · contracción controlada · regreso lento</div></div></div>
<div class="gifProof"><div class="gifProofTitle">GIF · RECORRIDO COMPLETO</div><div class="photo techniqueVisual gifPreview"><img class="realphoto day4ExerciseGif" src="../medios_publicados/ejercicios-compartido/videos/{repo}.gif" data-static-src="{MEDIA_ROOT}/{repo}-start.jpg" alt="{title} · GIF local del recorrido completo" loading="lazy"/><div class="brokenFallback">GIF no disponible; se conserva la referencia estática.</div></div><div class="videoProof"><span>GIF local · {repo} · secuencia de referencia técnica</span></div></div></div>
<div class="coach"><div class="coachRibbon"><span class="coachRibbonIcon" aria-hidden="true">✓</span><span>Checklist técnico</span></div><div class="coachHeader">Técnica clave</div><div class="exerciseQuickSummary" data-exercise-quick-summary aria-label="Resumen del ejercicio"></div><div class="metrics"><div class="metric series"><div class="metricText"><div class="metricLabel">Series</div><div class="metricVal">{series} series</div></div></div><div class="metric reps"><div class="metricText"><div class="metricLabel">Repeticiones</div><div class="metricVal">{item["reps"]} repeticiones</div></div></div><div class="metric rest"><div class="metricText"><div class="metricLabel">Descanso</div><div class="metricVal"><strong class="timeCue">{item["rest"]}</strong></div></div></div><div class="metric duration"><div class="metricText"><div class="metricLabel">Duración aprox.</div><div class="metricVal"><strong class="timeCue">{item["duration"]}</strong></div></div></div></div>
<div class="exerciseTracker" data-exercise="{index + 1}" data-series-keys="{keys}"><div class="exerciseTrackerHead"><span>Contador de series</span><span class="exerciseTrackerMeta"><strong class="exerciseProgress">0/{series}</strong><span class="exerciseStatus" hidden><span class="completionMark" aria-hidden="true">✓</span> Completado</span></span></div><div class="exerciseSetButtons" role="group" aria-label="Contador de series del ejercicio {index + 1}">{warmup}<button type="button" class="completeSetButton" aria-label="Completar serie 1 de {series}">Completar serie 1 de {series}</button><button type="button" class="machinePendingToggle" data-pending-key="p{index + 1}" aria-pressed="false">⚠ Máquina ocupada</button><div class="nextExerciseRow">{next_button}</div></div></div>
<div class="techSteps"><div class="techStep setup"><div class="techStepTitle">1 · Ajuste</div><div class="techStepText">{item["setup"]}</div></div><div class="techStep move"><div class="techStepTitle">2 · Ejecución</div><div class="techStepText">{item["execution"]}</div></div><div class="techStep control"><div class="techStepTitle">3 · Ritmo y respiración</div><div class="techStepText">{item["rhythm"]}</div></div><div class="techStep warning"><div class="techStepTitle">⚠ Evita</div><div class="techStepText">{item["avoid"]}</div></div></div></div></article>'''
    return base


def build_day4_script(template: str) -> str:
    tail = build_day3_script(template)
    tail = tail.replace("day3", "day4").replace("Día 3", "Día 4")
    tail = tail.replace("/22 series", "/20 series").replace("doneSeries}/22", "doneSeries}/20")
    tail = tail.replace("completedExercises === 7", "completedExercises === 7").replace("completedExercises >= 7", "completedExercises >= 7")
    tail = tail.replace("fitlovers-day4-series-v1", "fitlovers-day4-series-v1")
    return tail


def main() -> None:
    build_barbell_rdl_media()
    template = TEMPLATE.read_text(encoding="utf-8")
    head = template[: template.index("</head>") + len("</head>")]
    head = replace_all(head, {
        'data-label="Día 1 · Tirón: espalda y bíceps · v1 responsive"': 'data-label="Día 4 · Pierna y core: cadera y estabilidad · v1 responsive"',
        "<title>Día 1 · Tirón: espalda y bíceps · v1 responsive</title>": "<title>Día 4 · Pierna y core: cadera y estabilidad · v1 responsive</title>",
        'data-fix="day1-gif-candidates"': 'data-fix="day4-gif-layout"',
    })
    head = head.replace("</head>", '''<style data-fix="day4-static-and-gif-layout">
.phaseRow .day4StaticFrame{object-fit:contain!important;background:#fff!important}.gifProof{margin-top:12px;padding:10px 12px;border:1px solid rgba(45,97,121,.55);border-radius:14px;background:rgba(12,24,34,.68)}.gifProofTitle{font-size:12px;font-weight:900;letter-spacing:.6px;color:#72D4F0;margin-bottom:7px}.gifPreview{max-width:240px;margin:0 auto;aspect-ratio:1/1}.gifPreview img.day4ExerciseGif{object-fit:contain!important}.gifProof .videoProof{margin-top:7px!important}@media(max-width:700px){.gifPreview{max-width:220px}}
</style></head>''', 1)
    quick_rules = build_section(template, '<section class="footer quickRules"', {"espalda y bíceps": "pierna y cadera", "tirones": "series", "remo": "recorrido", "Jalón": "Prensa", "1–2 s al tirar": "1–2 s al empujar", "al tirar": "al empujar", "Si cae la postura": "Si pierdes la postura o el control"})
    summary = build_section(template, '<section class="routineSummary"', {"6 ejercicios · 20 series efectivas": "7 ejercicios · 20 series efectivas", "Día 1": "Día 4", "Tirón · espalda y bíceps": "Pierna y core · cadera y estabilidad", "75–95 min": "75–90 min", "60 s–2.5 min": "60 s–3 min"})
    gamification = build_section(template, '<section class="sessionGamification"', {})
    prep = build_section(template, '<section class="prep">', {"16–17 min": "8–10 min", "3 + 1": "3 + 1", "Jalón: series + calentamiento": "Prensa: series + aproximación"})
    dashboard = build_section(template, '<section class="sessionDashboard">', {"75–95 min": "75–90 min", "20 series efectivas": "20 series efectivas", "4 + 4 + 3 + 3 + 3 + 3 series": "3 + 3 + 4 + 2 + 2 + 3 + 3 series", "Tirón · espalda y bíceps": "Pierna y core · cadera y estabilidad", "Con trabajo complementario de deltoides posterior y pecho": "Con trabajo distribuido entre rodilla, cadera, pantorrilla y core", "De 60 s a 2.5 min según el ejercicio": "De 60 s a 3 min según el ejercicio"})
    note = build_section(template, '<section class="note notePanel"', {"Puntos clave de la sesión": "Puntos clave del Día 4", "La serie de aproximación prepara el movimiento y no cuenta como efectiva.": "Las series de aproximación preparan el movimiento y no cuentan como efectivas.", "RIR 2–3 al inicio y 1–2 al final": "RIR 1–3, manteniendo técnica y rango controlados", "Si cae la postura": "Si pierdes la postura o el control"})
    cards = "\n".join(build_card(item, index) for index, item in enumerate(EXERCISES))
    overlays = replace_all(between(template, '<section class="sessionCompletionPanel"', "</aside>"), {"0/6 ejercicios · 0/20 series": "0/7 ejercicios · 0/20 series", "0 pendientes": "20 pendientes"})
    footer = replace_all(between(template, '<footer class="sessionFooter"', "</footer>"), {"Día 1": "Día 4", "espalda y bíceps": "pierna y cadera", "18 series": "20 series"})
    lower_warmup = build_lower_warmup(template).replace('data-fix="day2-warmup-guide"', 'data-fix="day4-warmup-guide"', 1)
    body = "\n".join(["<body>", '<div class="page">', build_header(template), quick_rules, lower_warmup, summary, gamification, prep, dashboard, note, '<main class="cards">', cards, "</main>", overlays, footer, build_day4_script(template), "</div>", "</body>", "</html>"])
    if body.count('<article class="card" data-exercise-index="') != 7 or body.count("realphoto day4StaticFrame") != 14 or body.count("realphoto day4ExerciseGif") != 7:
        raise ValueError("El Día 4 debe contener 7 tarjetas con 14 fases estáticas y 7 GIFs")
    if "0/20 series" not in body or "20 series efectivas" not in body or "3 + 3 + 4 + 2 + 2 + 3 + 3 series" not in body:
        raise ValueError("El volumen del Día 4 no quedó sincronizado")
    if "fitlovers-day1-series-v1" in body or '<script data-fix="day1-gif-candidates">' in body:
        raise ValueError("El Día 4 conserva referencias del Día 1")
    forbidden = ('"license":', "portraitLicense", "portraitCredit", "portraitSource", "authorContextSource", "CANDIDATE_PENDING_LICENSE_REVIEW", "sourceUrl:", "mediaStatus", "motivationSource", "gifAttribution")
    leaked = [marker for marker in forbidden if marker in body]
    if leaked:
        raise ValueError(f"Metadatos de media no permitidos en HTML: {leaked}")
    canonical = sanitize_canonical_metadata(standardize_muscle_visuals(head + body))
    OUTPUT.write_text(canonical, encoding="utf-8", newline="\n")
    print(f"GENERATED {OUTPUT.relative_to(ROOT)} bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    main()
