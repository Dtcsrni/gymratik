"""E2E visual/funcional para las cuatro rutinas y mascotas de actividad.

Uso: python scripts/e2e_routine_activity_check.py
Requiere Playwright para Python y Chromium disponible en el host.
Todos los datos se crean en contextos efímeros del navegador.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_pwa_service_worker import build_precache  # noqa: E402

ROUTINES = (
    ("Rutina_Dia_1_Espalda_Biceps_V1.html", "female", "female"),
    ("Rutina_Dia_2_Pierna_Gluteo_V1.html", "male", "male"),
    ("Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html", "nonbinary", "neutral"),
    ("Rutina_Dia_4_Pierna_Equilibrio_V1.html", "", "neutral"),
)
PORT = 8768
SCREENSHOT_DIR = Path(os.environ["GYMRATIK_E2E_SCREENSHOT_DIR"]) if os.environ.get("GYMRATIK_E2E_SCREENSHOT_DIR") else None
RESPONSIVE_VIEWPORTS = (
    (320, 568),   # Android compacto
    (360, 640),   # Android estrecho
    (375, 812),   # formato móvil clásico
    (390, 844),   # Pixel compacto / viewport CSS representativo
    (412, 915),   # referencia móvil actual
    (432, 960),   # móvil grande
    (640, 360),   # horizontal con poca altura
)


def capture_visual(page, filename: str) -> None:
    if SCREENSHOT_DIR is None:
        return
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENSHOT_DIR / filename), full_page=False)


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, _format, *_args):
        pass


def assert_image_inventory(page, routine_name: str) -> dict:
    page.evaluate("() => [...document.images].forEach(image => { image.loading = 'eager'; })")
    page.wait_for_function(
        "() => [...document.images].every(image => image.complete && "
        "(image.naturalWidth > 0 || (!image.getAttribute('src') && image.hidden) || (image.currentSrc.includes('/videos/') && image.hidden)))",
        timeout=20_000,
    )
    inventory = page.evaluate(
        """async () => {
          const images = [...document.images];
          return await Promise.all(images.map(async image => {
            let decodeError = '';
            try { await image.decode(); } catch (error) { decodeError = String(error); }
            const rect = image.getBoundingClientRect();
            const style = getComputedStyle(image);
            const frame = image.closest('.warmupVisual,.gifFrame');
            const fallback = image.parentElement?.querySelector('.warmupFallback,.gifFallback');
            const fallbackRect = fallback?.getBoundingClientRect();
            return {
              src: image.currentSrc || image.src,
              className: image.className,
              complete: image.complete,
              naturalWidth: image.naturalWidth,
              naturalHeight: image.naturalHeight,
              renderedWidth: Math.round(rect.width),
              renderedHeight: Math.round(rect.height),
              display: style.display,
              visible: rect.width > 0 && rect.height > 0 && style.display !== 'none',
              mediaState: frame?.dataset.mediaState || '',
              fallback: fallback ? {
                complete: fallback.complete,
                naturalWidth: fallback.naturalWidth,
                naturalHeight: fallback.naturalHeight,
                renderedWidth: Math.round(fallbackRect.width),
                renderedHeight: Math.round(fallbackRect.height),
                src: fallback.currentSrc || fallback.src,
                visible: fallbackRect.width > 0 && fallbackRect.height > 0 && getComputedStyle(fallback).display !== 'none'
              } : null,
              decodeError
            };
          }));
        }"""
    )
    intentional_empty = lambda item: not item["src"] and not item["visible"]
    broken = [item for item in inventory if not intentional_empty(item) and (not item["complete"] or not item["naturalWidth"] or not item["naturalHeight"] or item["decodeError"] or ("/videos/" in item["src"] and not item["visible"]))]
    if broken:
        raise AssertionError(f"{routine_name}: imágenes que no decodifican: {json.dumps(broken, ensure_ascii=False)}")
    invalid_layout = [item for item in inventory if item["visible"] and (item["renderedWidth"] <= 0 or item["renderedHeight"] <= 0)]
    if invalid_layout:
        raise AssertionError(f"{routine_name}: imágenes sin tamaño renderizado: {invalid_layout}")
    remote = [item["src"] for item in inventory if not intentional_empty(item) and not item["src"].startswith(("http://127.0.0.1:", "http://localhost:", "data:image/"))]
    if remote:
        raise AssertionError(f"{routine_name}: recursos visuales inesperados fuera del servidor local: {remote}")
    return {
        "images": len(inventory),
        "rendered": sum(item["visible"] for item in inventory),
        "offlineStaticFallbacks": 0,
        "animatedGifs": sum("/videos/" in item["src"] and item["visible"] for item in inventory),
    }


def assert_visual_resource_quality(page, routine_name: str) -> dict:
    """Valida tamaño, proporción, ajuste y legibilidad de recursos instructivos."""
    audit = page.evaluate("""() => {
      const rect = element => { const r=element.getBoundingClientRect(); return {width:r.width,height:r.height}; };
      const images = [...document.querySelectorAll('.phaseRow .photo img.realphoto,.warmupVisual img,.gifFrame img,.muscleDayVisual img')].map(image => {
        const box=rect(image), parent=rect(image.parentElement), style=getComputedStyle(image);
        return {group:image.matches('.phaseRow .photo img.realphoto')?'exercise':image.matches('.warmupVisual img')?'warmup':image.matches('.gifFrame img')?'gif':'anatomy',src:image.currentSrc||image.src,alt:image.alt,ariaHidden:image.getAttribute('aria-hidden')==='true',naturalWidth:image.naturalWidth,naturalHeight:image.naturalHeight,width:box.width,height:box.height,parentWidth:parent.width,parentHeight:parent.height,fit:style.objectFit,position:style.objectPosition,hidden:image.hidden,display:style.display};
      });
      const captions=[...document.querySelectorAll('.phaseRow .phaseLabel,.phaseRow .source,.warmupHead p,.warmupCopy p,.warmupInstructions')].map(element=>({tag:element.tagName,className:String(element.className),text:element.textContent.trim().slice(0,90),fontSize:parseFloat(getComputedStyle(element).fontSize),width:rect(element).width})).filter(item=>item.width>0);
      const instructional=images.filter(image=>image.group==='exercise'&&!image.hidden&&image.display!=='none');
      const cropFractions=instructional.filter(image=>image.fit==='cover'&&image.naturalWidth&&image.naturalHeight&&image.width&&image.height).map(image=>{const source=image.naturalWidth/image.naturalHeight,box=image.width/image.height;return 1-Math.min(source,box)/Math.max(source,box)});
      return {images,captions,exerciseImages:instructional.length,minExerciseWidth:instructional.length?Math.min(...instructional.map(image=>image.width)):0,minExerciseHeight:instructional.length?Math.min(...instructional.map(image=>image.height)):0,maxExerciseCoverCrop:cropFractions.length?Math.max(...cropFractions):0,minCaptionFont:captions.length?Math.min(...captions.map(caption=>caption.fontSize)):0,fitModes:[...new Set(images.map(image=>image.fit))]};
    }""")
    visible_images = [item for item in audit["images"] if not item["hidden"] and item["display"] != "none"]
    invalid = [item for item in visible_images if item["naturalWidth"] and (item["width"] <= 0 or item["height"] <= 0)]
    distorted = [item for item in visible_images if item["naturalWidth"] and item["fit"] == "fill" and item["width"] and item["height"] and abs((item["naturalWidth"] / item["naturalHeight"]) - (item["width"] / item["height"])) > 0.12]
    missing_alt = [item["src"] for item in visible_images if item["group"] in ("exercise", "warmup") and not item["ariaHidden"] and not item["alt"].strip()]
    cropped_instructional = [item for item in audit["images"] if item["group"] == "exercise" and not item["hidden"] and item["display"] != "none" and item["fit"] != "contain"]
    if invalid or distorted or missing_alt or cropped_instructional:
        raise AssertionError(f"{routine_name}: recurso sin escala/alt utilizable: invalid={invalid}, distorted={distorted}, missingAlt={missing_alt}, cropped={cropped_instructional}")
    if audit["exerciseImages"] and (audit["minExerciseWidth"] < 96 or audit["minExerciseHeight"] < 68):
        raise AssertionError(f"{routine_name}: imagen de ejercicio demasiado pequeña: {audit}")
    if audit["minCaptionFont"] and audit["minCaptionFont"] < 12:
        small_captions = [item for item in audit["captions"] if item["width"] > 0 and item["fontSize"] < 12]
        raise AssertionError(f"{routine_name}: texto instructivo menor a 12 CSS px: {audit['minCaptionFont']}; elementos={small_captions}")
    if audit["maxExerciseCoverCrop"] > 0.48:
        worst = [item for item in audit["images"] if item["group"] == "exercise" and item["fit"] == "cover"]
        raise AssertionError(f"{routine_name}: recorte potencialmente excesivo (>48% de un eje): {audit['maxExerciseCoverCrop']:.2%}; recursos={worst}")
    return {key:value for key,value in audit.items() if key != "images"} | {"imageGroups":{group:sum(item["group"]==group for item in audit["images"]) for group in ("exercise","warmup","gif","anatomy")}}


def assert_animation_changes(page, image) -> None:
    first = image.screenshot()
    for _ in range(10):
        time.sleep(0.22)
        second = image.screenshot()
        if first != second:
            return
    raise AssertionError("El GIF se decodifica, pero el fotograma visible no avanzó en 2.2 s")


def assert_series_segment_fill_stable(page, routine_name: str) -> str:
    segment = page.locator("article.card .seriesProgressSegment.is-current")
    transform = segment.evaluate("element => getComputedStyle(element, '::after').transform")
    time.sleep(1.25)
    after = segment.evaluate("element => getComputedStyle(element, '::after').transform")
    if transform != after:
        raise AssertionError(f"{routine_name}: el relleno de la serie oscila durante actividad: {transform} -> {after}")
    return transform


def assert_mascot(page, variant: str, state: str, reduced: bool = False) -> str:
    image = page.locator("#summaryActivityMascot")
    expected_suffix = f"{variant}-{state}-{'still.webp' if reduced else '25fps.gif'}"
    src = image.get_attribute("src") or ""
    if not src.endswith(expected_suffix):
        raise AssertionError(f"Mascota inesperada: src={src!r}; se esperaba *{expected_suffix}")
    if image.is_hidden():
        state = page.locator("#summaryActivityStatus").evaluate("element => ({activity: element.dataset.activity, label: element.querySelector('#summaryActivityLabel')?.textContent, hidden: element.querySelector('#summaryActivityMascot')?.hidden})")
        raise AssertionError(f"La mascota debe verse durante actividad o descanso: {state}")
    dimensions = image.evaluate("async image => { await image.decode(); const box = image.getBoundingClientRect(); return [image.naturalWidth, image.naturalHeight, box.width, box.height]; }")
    if dimensions[0:2] != [128, 128] or min(dimensions[2:]) <= 0:
        raise AssertionError(f"La mascota no se renderiza a tamaño válido: {dimensions}")
    return src


def assert_activity_feedback(page, activity: str) -> dict:
    """Comprueba que actividad/descanso transmiten estado mediante color y pulso real."""
    styles = page.evaluate("""() => {
      const toggle=document.querySelector('#summaryToggle');
      const status=document.querySelector('#summaryActivityStatus');
      const indicator=status?.querySelector('.summaryActivityIndicator');
      const button=document.querySelector('article.card .completeSetButton');
      const segment=document.querySelector('article.card .seriesProgressSegment.is-current');
      const style=element=>element?getComputedStyle(element):null;
      const toggleStyle=style(toggle), indicatorStyle=style(indicator), buttonStyle=style(button), segmentStyle=style(segment);
      return {
        activity:status?.dataset.activity,
        toggleClass:toggle?.className,
        toggleBackground:toggleStyle?.backgroundImage,
        indicatorColor:indicatorStyle?.backgroundColor,
        indicatorAnimation:indicatorStyle?.animationName,
        indicatorDuration:indicatorStyle?.animationDuration,
        buttonClass:button?.className,
        segmentClass:segment?.className,
        segmentAnimation:segmentStyle?.animationName,
        segmentDuration:segmentStyle?.animationDuration
      };
    }""")
    if activity == "active":
        checks = (
            styles["activity"] == "active",
            "isActive" in styles["toggleClass"],
            "19, 105, 91" in styles["toggleBackground"],
            styles["indicatorColor"] == "rgb(101, 242, 221)",
            styles["indicatorAnimation"] == "activityFastPulse",
            styles["indicatorDuration"] == "0.68s",
            "is-series-active" in styles["buttonClass"],
            "is-active" in styles["segmentClass"],
            styles["segmentAnimation"] == "activityFastPulse",
            styles["segmentDuration"] == "0.68s",
        )
    elif activity == "rest":
        checks = (
            styles["activity"] == "rest",
            "isResting" in styles["toggleClass"],
            "112, 79, 21" in styles["toggleBackground"],
            styles["indicatorColor"] == "rgb(255, 210, 119)",
            styles["indicatorAnimation"] == "restSlowPulse",
            styles["indicatorDuration"] == "2.4s",
            "is-resting" in styles["buttonClass"],
            "is-resting" in styles["segmentClass"],
            styles["segmentAnimation"] == "restSlowPulse",
            styles["segmentDuration"] == "2.4s",
        )
    else:
        raise ValueError(f"Estado de actividad desconocido: {activity}")
    if not all(checks):
        raise AssertionError(f"Feedback visual/animado incorrecto para {activity}: {styles}")
    return styles


def dispatch_touch_hold(page, button, duration_ms: int, release_click: bool = True) -> None:
    pointer = {"pointerId": 7, "pointerType": "touch", "isPrimary": True, "button": 0, "buttons": 1}
    button.evaluate("element => element.setAttribute('data-e2e-hold-target', 'true')")
    button.dispatch_event("pointerdown", pointer)
    selector = "[data-e2e-hold-target='true'].is-holding"
    try:
        page.wait_for_function("selector => document.querySelector(selector)", arg=selector)
        page.clock.run_for(duration_ms)
        button.dispatch_event("pointerup", {**pointer, "buttons": 0})
        if release_click:
            button.dispatch_event("click", {})
    finally:
        button.evaluate("element => element.removeAttribute('data-e2e-hold-target')")


def validate_day(browser, name: str, sex: str, variant: str) -> dict:
    context = browser.new_context(
        viewport={"width": 412, "height": 915},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
        reduced_motion="no-preference",
    )
    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    page = context.new_page()
    page.clock.install()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="networkidle")

    if page.locator("#installGate").count() and page.locator("#installGate").is_visible():
        raise AssertionError(f"{name}: el gate instalado no se aplicó al contexto E2E")
    if sex:
        page.evaluate("sex => window.TrainingProgressStore.saveProfile({sex})", sex)
    else:
        empty_profile = page.evaluate("async () => await window.TrainingProgressStore.getProfile()")
        if empty_profile.get("sex"):
            raise AssertionError(f"{name}: el caso default ya tiene sexo persistido: {empty_profile}")
    page.wait_for_function("expected => window.gymratikMascotVariant === expected", arg=variant)

    images = assert_image_inventory(page, name)
    resource_quality = assert_visual_resource_quality(page, name)
    exercise_gif_locator = page.locator(".day3ExerciseGif,.day4ExerciseGif").first
    if exercise_gif_locator.count() == 0:
        exercise_gif_locator = page.locator('img[src*="/videos/"]').first
    exercise_gif_locator.scroll_into_view_if_needed()
    assert_animation_changes(page, exercise_gif_locator)
    cards = page.locator("article.card[data-exercise-index]")
    exercise_count = cards.count()
    reps_inputs = page.locator("input.performanceReps")
    load_inputs = page.locator("input.performanceLoad")
    if exercise_count != reps_inputs.count() or exercise_count != load_inputs.count():
        raise AssertionError(f"{name}: selectores de rendimiento incompletos: exercises={exercise_count}, reps={reps_inputs.count()}, loads={load_inputs.count()}")

    # Comprueba controles de repeticiones y carga en todos los ejercicios con gestos de teclado.
    for index in range(exercise_count):
        card = cards.nth(index)
        reps = card.locator("input.performanceReps")
        load = card.locator("input.performanceLoad")
        reps.focus()
        reps.press("ArrowRight")
        if reps.get_attribute("data-selected") != "true":
            raise AssertionError(f"{name}: el selector de repeticiones {index + 1} no registra el gesto")
        fill = reps.evaluate("element => element.style.getPropertyValue('--range-progress')")
        if not fill.endswith("%") or float(fill[:-1]) <= 0:
            raise AssertionError(f"{name}: el slider de repeticiones {index + 1} no refleja el valor en su pista")
        if card.locator(".lucide-repeat-2").count() != 1 or card.locator(".lucide-weight").count() != 1:
            raise AssertionError(f"{name}: faltan iconos SVG vectoriales en la zona de registro {index + 1}")
        rep_clear = card.locator(".performanceFieldTitleRow .performanceClear")
        clear_style = rep_clear.evaluate("element => { const style = getComputedStyle(element); const box = element.getBoundingClientRect(); return {border: style.borderStyle, background: style.backgroundColor, color: style.color, height: box.height}; }")
        if clear_style["border"] != "solid" or clear_style["background"] == "rgb(239, 239, 239)" or clear_style["height"] < 34:
            raise AssertionError(f"{name}: el botón Quitar {index + 1} conserva estilo nativo o área insuficiente: {clear_style}")
        touch_targets = card.locator(".performanceRepsNudge").evaluate_all("buttons => buttons.map(button => { const box = button.getBoundingClientRect(); return [box.width, box.height]; })")
        if any(width < 42 or height < 42 for width, height in touch_targets):
            raise AssertionError(f"{name}: botones +/- pequeños para toque en el ejercicio {index + 1}: {touch_targets}")
        rep_clear.click()
        if reps.get_attribute("data-selected") != "false":
            raise AssertionError(f"{name}: no se pudo limpiar repeticiones del ejercicio {index + 1}")
        load.focus()
        load.press("ArrowRight")
        if not card.locator(".performanceLoadValue").inner_text().strip():
            raise AssertionError(f"{name}: el deslizador de carga no actualiza su lectura en el ejercicio {index + 1}")
        load_clear = card.locator(".performanceLoadOutputRow .performanceClear")
        load_clear.click()
        if load.get_attribute("aria-valuenow") not in (None, "0"):
            raise AssertionError(f"{name}: no se pudo limpiar la carga del ejercicio {index + 1}")
        machine_pending = card.locator(".machinePendingToggle")
        if machine_pending.count() != 1:
            raise AssertionError(f"{name}: el ejercicio {index + 1} no tiene exactamente un control de máquina ocupada")
        machine_pending.scroll_into_view_if_needed()
        if machine_pending.get_attribute("aria-pressed") != "false":
            raise AssertionError(f"{name}: el estado inicial de máquina ocupada es incorrecto en el ejercicio {index + 1}")
        machine_pending.click()
        if machine_pending.get_attribute("aria-pressed") != "true":
            raise AssertionError(f"{name}: no se pudo marcar la máquina ocupada en el ejercicio {index + 1}")
        machine_pending.click()
        if machine_pending.get_attribute("aria-pressed") != "false":
            raise AssertionError(f"{name}: no se pudo liberar la máquina en el ejercicio {index + 1}")
        if card.locator(".completeSetButton").count() != 1 or card.locator(".skipExerciseButton").count() != 1:
            raise AssertionError(f"{name}: falta el botón dinámico o el control secundario de omisión en el ejercicio {index + 1}")

    # Prueba edición decimal directa y conversión de unidad en el primer ejercicio.
    first = cards.first
    entry_zone = first.locator(".performanceEntry")
    entry_zone.evaluate("element => element.scrollIntoView({block:'center',behavior:'instant'})")
    if SCREENSHOT_DIR is not None:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        entry_zone.screenshot(path=str(SCREENSHOT_DIR / f"{name.split('_')[2]}-series-entry-mobile.png"))
    first.locator(".performanceLoadValue").click()
    direct = first.locator("input.performanceLoadDirect")
    direct.fill("17.5")
    direct.press("Enter")
    if "17.5" not in first.locator(".performanceLoadValue").inner_text():
        raise AssertionError(f"{name}: no se confirmó la edición decimal directa")
    first.locator("select.performanceLoadUnit").select_option("lb")
    if "lb" not in first.locator(".performanceLoadValue").inner_text():
        raise AssertionError(f"{name}: el selector kg/lb no actualizó la carga")

    # Barra de progreso flotante: una sola tarjeta y una fila por ejercicio.
    page.locator("#summaryToggle").click()
    if page.locator("#floatingSessionSummary").count() != 1 or page.locator(".summaryExercise").count() != exercise_count:
        raise AssertionError(f"{name}: resumen flotante duplicado o incompleto")
    if not page.locator(".sessionSummaryList").evaluate("element => element.scrollHeight >= element.clientHeight"):
        raise AssertionError(f"{name}: lista flotante no conserva desplazamiento táctil")

    # Calentamiento completo, con su mínimo de preparación de 15 s.
    warmup = page.locator("#warmupAction")
    warmup.click()
    page.clock.run_for(15_000)
    if warmup.get_attribute("data-phase") != "cardio":
        raise AssertionError(f"{name}: el calentamiento no terminó la preparación de 15 s")
    exercise_gif = assert_mascot(page, variant, "exercise")
    assert_animation_changes(page, page.locator("#summaryActivityMascot"))
    warmup.click()
    if warmup.get_attribute("data-phase") != "mobility":
        raise AssertionError(f"{name}: el botón no avanzó de cardio a movilidad")
    warmup.click()
    if warmup.get_attribute("data-phase") != "done":
        raise AssertionError(f"{name}: el botón no finalizó el calentamiento")
    if not page.locator("#summaryActivityMascot").is_hidden() or page.locator("#summaryActivityMascot").get_attribute("src"):
        raise AssertionError(f"{name}: la animación no se detuvo al volver a idle")

    # Completa la aproximación, espera 15 s de preparación, registra una serie y verifica descanso.
    button = first.locator(".completeSetButton")
    button.click()  # serie ligera de aproximación
    button.click()  # inicia la preparación de la serie efectiva
    page.clock.run_for(5_000)
    page.reload(wait_until="networkidle")
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'preparing'")
    page.clock.run_for(10_000)
    activity = page.locator("#summaryActivityStatus")
    if activity.get_attribute("data-activity") != "active":
        raise AssertionError(f"{name}: la serie efectiva no aparece activa tras la preparación")
    if "isActive" not in page.locator("#summaryToggle").get_attribute("class"):
        raise AssertionError(f"{name}: se perdió el indicador de actividad del botón flotante tras recargar")
    if page.locator("#summaryToggle").get_attribute("aria-expanded") != "true":
        page.locator("#summaryToggle").click()
    assert_mascot(page, variant, "exercise")
    active_feedback = assert_activity_feedback(page, "active")
    stable_fill = assert_series_segment_fill_stable(page, name)
    if "isActive" not in page.locator("#summaryToggle").get_attribute("class"):
        raise AssertionError(f"{name}: cabecera flotante no refleja actividad verde")
    routine_id = name.split("_")[2]
    capture_visual(page, f"day-{routine_id}-active-mobile.png")
    button.click()
    if activity.get_attribute("data-activity") != "rest":
        state = button.evaluate("element => ({disabled: element.disabled, text: element.textContent, className: element.className, ariaLabel: element.getAttribute('aria-label')})")
        raise AssertionError(f"{name}: completar serie no inició el descanso; actividad={activity.get_attribute('data-activity')!r}, botón={state}, errores={errors}")
    rest_gif = assert_mascot(page, variant, "rest")
    rest_feedback = assert_activity_feedback(page, "rest")
    assert_animation_changes(page, page.locator("#summaryActivityMascot"))
    capture_visual(page, f"day-{routine_id}-rest-mobile.png")
    if "isResting" not in page.locator("#summaryToggle").get_attribute("class"):
        raise AssertionError(f"{name}: cabecera flotante no refleja descanso amarillo")
    progress = page.locator(".summaryExercise").first.evaluate("element => Number(element.style.getPropertyValue('--summary-progress'))")
    if progress <= 0:
        raise AssertionError(f"{name}: barra de progreso no avanzó al completar la serie")

    # La sesión intermedia debe sobrevivir a una recarga durante el descanso.
    page.reload(wait_until="networkidle")
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'rest'")
    if not page.locator("#summaryToggle").evaluate("element => element.classList.contains('isResting')"):
        raise AssertionError(f"{name}: la recarga perdió el estado visual de descanso")
    if page.locator("#summaryToggle").get_attribute("aria-expanded") != "true":
        page.locator("#summaryToggle").click()
    if not page.locator("#summaryActivityMascot").get_attribute("src").endswith(f"{variant}-rest-25fps.gif"):
        raise AssertionError(f"{name}: la recarga perdió la mascota de descanso")
    restored_progress = page.locator(".summaryExercise").first.evaluate("element => Number(element.style.getPropertyValue('--summary-progress'))")
    if restored_progress != progress:
        raise AssertionError(f"{name}: la recarga alteró el progreso de la serie ({progress} -> {restored_progress})")

    # El descanso conserva el GIF salvo que el usuario solicite movimiento reducido.
    page.emulate_media(reduced_motion="reduce")
    page.wait_for_function("document.querySelector('#summaryActivityMascot')?.currentSrc.endsWith('still.webp')")
    still = assert_mascot(page, variant, "rest", reduced=True)
    if page.locator("#summaryActivityStatus .summaryActivityIndicator").evaluate("element => getComputedStyle(element).animationName") != "none":
        raise AssertionError(f"{name}: el pulso no respeta prefers-reduced-motion")

    # Gestos largos reales de puntero táctil: cancelar temprano y luego omitir el descanso.
    page.emulate_media(reduced_motion="no-preference")
    rest_button = first.locator(".completeSetButton")
    dispatch_touch_hold(page, rest_button, 4_000)
    if activity.get_attribute("data-activity") != "rest" or "is-holding" in (rest_button.get_attribute("class") or ""):
        raise AssertionError(f"{name}: soltar antes de 5 s no canceló el gesto de descanso")
    dispatch_touch_hold(page, rest_button, 5_000)
    if activity.get_attribute("data-activity") != "active":
        raise AssertionError(f"{name}: mantener 5 s no omitió el descanso y reanudó la serie")
    assert_activity_feedback(page, "active")

    if errors:
        raise AssertionError(f"{name}: errores JavaScript: {errors}")

    result = {
        "routine": name,
        "profileSex": sex or "empty",
        "variant": variant,
        "exercises": exercise_count,
        "images": images,
        "resourceQuality": resource_quality,
        "activityGif": exercise_gif,
        "restGif": rest_gif,
        "reducedMotionAsset": still,
        "activityVisuals": {"active": active_feedback, "rest": rest_feedback},
        "stableActiveFillTransform": stable_fill,
        "skipGestures": {"rest": "cancelled <5 s; continued at 5 s", "exercise": "cancelled <10 s; skip+undo at 10 s"},
        "progress": progress,
    }
    context.close()
    return result


def validate_primary_set_buttons(browser, name: str, sex: str) -> dict[str, int]:
    """Exercise each card's dynamic and skip controls in a clean session."""
    context_settings = {
        "viewport": {"width": 412, "height": 915},
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
    }
    checked = 0
    skipped = 0
    initial_context = browser.new_context(**context_settings)
    initial_context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    initial_page = initial_context.new_page()
    initial_page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
    initial_page.wait_for_function("() => [...document.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)")
    initial_page.wait_for_selector("article.card[data-exercise-index] .completeSetButton")
    exercise_count = initial_page.locator("article.card[data-exercise-index]").count()
    initial_context.close()

    for index in range(exercise_count):
        context = browser.new_context(**context_settings)
        context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
        page = context.new_page()
        page.clock.install()
        page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
        page.wait_for_function("() => [...document.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)")
        page.wait_for_selector("article.card[data-exercise-index] .completeSetButton")
        if sex:
            page.evaluate("sex => window.TrainingProgressStore.saveProfile({sex})", sex)

        warmup = page.locator("#warmupAction")
        warmup.click()
        page.clock.run_for(15_000)
        if warmup.get_attribute("data-phase") != "cardio":
            context.close()
            raise AssertionError(f"{name}: no se pudo completar el calentamiento antes del botón del ejercicio {index + 1}")
        warmup.click()
        warmup.click()
        if warmup.get_attribute("data-phase") != "done":
            context.close()
            raise AssertionError(f"{name}: el calentamiento no finalizó antes del ejercicio {index + 1}")

        card = page.locator("article.card[data-exercise-index]").nth(index)
        button = card.locator(".completeSetButton")
        segments = card.locator(".seriesProgressSegment").count()
        button.scroll_into_view_if_needed()
        button.click()
        # El primer ejercicio incluye una serie de aproximación tras el calentamiento general.
        if index == 0:
            button.click()
        if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "preparing":
            context.close()
            raise AssertionError(f"{name}: el botón principal del ejercicio {index + 1} no inició preparación")
        page.clock.run_for(15_000)
        if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "active":
            context.close()
            raise AssertionError(f"{name}: el botón principal del ejercicio {index + 1} no pasó de preparación a actividad")
        button.click()
        if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "rest":
            context.close()
            raise AssertionError(f"{name}: el botón principal del ejercicio {index + 1} no completó la serie ni inició descanso")
        expected_progress = f"1/{segments}"
        if card.locator(".exerciseProgress").inner_text().strip() != expected_progress:
            context.close()
            raise AssertionError(f"{name}: el contador del ejercicio {index + 1} no registró la serie: esperado={expected_progress}, actual={card.locator('.exerciseProgress').inner_text().strip()!r}")

        skip_button = card.locator(".skipExerciseButton")
        skip_status = card.locator(".holdFeedback")
        tracker = card.locator(".exerciseTracker")
        completed_before_skip = card.locator(".seriesProgressSegment.is-complete").count()
        exercise_series_total = card.locator(".seriesProgressSegment").count()
        skip_button.scroll_into_view_if_needed()
        dispatch_touch_hold(page, skip_button, 9_000)
        if "exerciseSkipped" in (tracker.get_attribute("class") or ""):
            context.close()
            raise AssertionError(f"{name}: omitir ejercicio {index + 1} se activó antes de cumplir 10 s")
        dispatch_touch_hold(page, skip_button, 10_500)
        if "exerciseSkipped" not in (tracker.get_attribute("class") or ""):
            state = skip_button.evaluate("element => ({className:element.className, disabled:element.disabled, style:element.getAttribute('style'), aria:element.getAttribute('aria-label'), feedback:element.closest('.exerciseTracker')?.querySelector('.holdFeedback')?.textContent})")
            context.close()
            raise AssertionError(f"{name}: mantener 10 s no omitió el ejercicio {index + 1}: state={state}")
        if card.locator(".seriesProgressSegment.is-complete").count() != completed_before_skip or skip_status.inner_text().strip() != "Ejercicio omitido":
            context.close()
            raise AssertionError(f"{name}: la omisión del ejercicio {index + 1} fabricó series o no confirmó el resultado")
        undo = card.locator(".exerciseUndoButton[aria-label^='Deshacer el ejercicio']")
        page.once("dialog", lambda dialog: dialog.accept())
        undo.click()
        if "exerciseSkipped" in (tracker.get_attribute("class") or "") or card.locator(".exerciseProgress").inner_text().strip() != f"0/{exercise_series_total}":
            context.close()
            raise AssertionError(f"{name}: deshacer omisión no restauró el progreso del ejercicio {index + 1}")
        checked += 1
        skipped += 1
        context.close()
    # El descanso también debe comenzar tras la última serie de un ejercicio
    # cuando quedan ejercicios en la rutina.
    context = browser.new_context(**context_settings)
    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    page = context.new_page()
    page.clock.install()
    page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
    page.wait_for_selector("article.card[data-exercise-index] .completeSetButton")
    warmup = page.locator("#warmupAction")
    warmup.click()
    page.clock.run_for(15_000)
    warmup.click()
    warmup.click()
    card = page.locator("article.card[data-exercise-index]").first
    button = card.locator(".completeSetButton")
    button.click()  # aproximación
    for series_index in range(card.locator(".seriesProgressSegment").count()):
        activity_state = page.locator("#summaryActivityStatus").get_attribute("data-activity")
        if activity_state not in ("preparing", "active"):
            button.click()
            activity_state = page.locator("#summaryActivityStatus").get_attribute("data-activity")
        if activity_state == "preparing":
            page.clock.run_for(15_000)
        if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "active":
            context.close()
            raise AssertionError(f"{name}: preparación incorrecta antes de serie {series_index + 1}")
        button.click()
        expected = "rest" if series_index < card.locator(".seriesProgressSegment").count() - 1 or page.locator("article.card").count() > 1 else "complete"
        actual = page.locator("#summaryActivityStatus").get_attribute("data-activity")
        if actual != expected:
            context.close()
            raise AssertionError(f"{name}: resultado tras serie {series_index + 1}: esperado={expected}, actual={actual}")
        if series_index < card.locator(".seriesProgressSegment").count() - 1:
            dispatch_touch_hold(page, button, 5_000)
    if page.locator("#summaryActivityStatus").get_attribute("data-activity") == "rest" and not card.locator(".completeSetButton").get_attribute("aria-label").startswith("Descanso"):
        context.close()
        raise AssertionError(f"{name}: el botón no indica descanso al terminar la última serie del ejercicio")
    context.close()
    return {"primarySetButtonsTested": checked, "exerciseSkipButtonsTested": skipped, "exerciseCompletionRestTested": True}


def validate_installed_offline_package(browser) -> dict:
    """Install the generated worker, then render every routine with network off."""
    context = browser.new_context(
        viewport={"width": 412, "height": 915},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
        service_workers="allow",
    )
    context.add_init_script(
        "sessionStorage.setItem('gymratik-install-confirmed-v1', 'true');"
        "localStorage.setItem('gymratik-network-preference-v1', 'always');"
    )
    page = context.new_page()
    offline_page_errors = []
    offline_failed_requests = []
    offline_bad_responses = []
    origin = f"http://127.0.0.1:{PORT}/"
    page.on("pageerror", lambda error: offline_page_errors.append(str(error)))

    def record_failed_request(request) -> None:
        if request.url.startswith(origin):
            offline_failed_requests.append(request.url)

    def record_bad_response(response) -> None:
        if response.status >= 400 and response.url.startswith(origin):
            offline_bad_responses.append({"url": response.url, "status": response.status})

    page.on("requestfailed", record_failed_request)
    page.on("response", record_bad_response)
    page.goto(f"http://127.0.0.1:{PORT}/", wait_until="domcontentloaded")
    page.wait_for_function(
        "async () => { const names = await caches.keys(); "
        "for (const name of names) { if (!name.startsWith('entrenamiento-pwa-')) continue; "
        "const cache = await caches.open(name); "
        "if (await cache.match(new URL('./__gymratik_complete__', location.origin + '/').href)) return true; } "
        "return false; }",
        timeout=120_000,
    )
    page.wait_for_function("navigator.serviceWorker.controller !== null", timeout=30_000)
    expected_precache = build_precache()
    cache_summary = page.evaluate(
        "async expected => { const names = (await caches.keys()).filter(name => name.startsWith('entrenamiento-pwa-')); "
        "const cache = await caches.open(names[0]); "
        "const missing = []; for (const path of expected) { "
        "if (!await cache.match(new URL(path, location.origin + '/').href)) missing.push(path); } "
        "return {names, entries: (await cache.keys()).length, expected: expected.length, missing}; }",
        expected_precache,
    )
    if not cache_summary["names"] or cache_summary["missing"]:
        raise AssertionError(f"El paquete instalado no contiene todo el precache: {cache_summary}")

    context.set_offline(True)
    offline_results = []
    for name, _sex, _variant in ROUTINES:
        page.goto(f"{origin}data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        if not page.evaluate("Boolean(navigator.serviceWorker.controller)"):
            raise AssertionError(f"{name}: documento abierto sin estar controlado por el service worker")
        inventory = assert_image_inventory(page, name)
        resource_quality = assert_visual_resource_quality(page, name)
        offline_results.append({"routine": name, **inventory, "resourceQuality": resource_quality})
        offline_gif = page.locator(".day3ExerciseGif,.day4ExerciseGif").first
        if offline_gif.count() == 0:
            offline_gif = page.locator('img[src*="/videos/"]').first
        offline_gif.scroll_into_view_if_needed()
        assert_animation_changes(page, offline_gif)
    deep_link = f"{origin}data/rutinas_autocontenidas/canonicas/{quote(ROUTINES[1][0])}?e2e=offline-fallback"
    page.goto(deep_link, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    page.wait_for_function("!document.documentElement.classList.contains('gymratik-loading')", timeout=10_000)
    fallback_heading = page.locator("#pageTitle").inner_text().strip()
    base_href = page.locator("base").get_attribute("href")
    fallback_inventory = assert_image_inventory(page, "respaldo offline desde ruta profunda")
    if fallback_heading != "Una serie a la vez." or base_href != origin:
        raise AssertionError(f"El respaldo offline no fija la raíz de la PWA: heading={fallback_heading!r}, base={base_href!r}")
    capture_visual(page, "offline-deep-link-fallback-home.png")
    offline_results.append({"routine": "respaldo offline desde ruta profunda", **fallback_inventory, "base": base_href})
    runtime_failures = {
        "pageErrors": offline_page_errors,
        "failedRequiredRequests": offline_failed_requests,
        "badRequiredResponses": offline_bad_responses,
    }
    if any(runtime_failures.values()):
        raise AssertionError(f"Fallos de recursos/runtime en el paquete offline: {runtime_failures}")
    context.close()
    return {"cache": cache_summary, "offlineRoutines": offline_results, "runtime": runtime_failures}


def validate_responsive_layout(browser) -> dict:
    """Comprueba desbordamientos, controles y solapamiento con el resumen en tamaños móviles."""
    results = []
    for name, _sex, _variant in ROUTINES:
        for width, height in RESPONSIVE_VIEWPORTS:
            context = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=2 if width < 640 else 1,
                is_mobile=True,
                has_touch=True,
            )
            context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
            page = context.new_page()
            page.clock.install()
            page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="networkidle")
            page.wait_for_function("() => [...document.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)")
            page.locator(".performanceEntry").first.wait_for(state="visible")
            page.evaluate("async () => { await document.fonts.ready; }")
            page.clock.run_for(100)
            layout = page.evaluate("""() => {
              const rect = element => { const r = element.getBoundingClientRect(); return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}; };
              const entry = document.querySelector('.performanceEntry');
              const controls = [...entry.querySelectorAll('button,input,select,[role=button]')].map(rect);
              const offenders = [...document.body.querySelectorAll('*')].map(element => ({element,box:rect(element),scrollWidth:element.scrollWidth,clientWidth:element.clientWidth})).filter(item => item.box.right>innerWidth+1 || item.box.left < -1 || item.scrollWidth>item.clientWidth+2).slice(0,30).map(item => ({tag:item.element.tagName,id:item.element.id,className:String(item.element.className).slice(0,100),box:item.box,scrollWidth:item.scrollWidth,clientWidth:item.clientWidth}));
              const edgeOverflow=[...document.body.querySelectorAll('*')].map(element=>({element,box:rect(element)})).filter(item=>item.box.right>innerWidth+1||item.box.left < -1).slice(0,30).map(item=>({tag:item.element.tagName,id:item.element.id,className:String(item.element.className).slice(0,100),box:item.box}));
              const card=entry.closest('.card');
              const ancestry=[]; for(let node=entry;node&&node!==card;node=node.parentElement){const s=getComputedStyle(node);ancestry.push({tag:node.tagName,className:String(node.className),box:rect(node),display:s.display,gridColumns:s.gridTemplateColumns,overflow:s.overflow});}
              return {viewport:{width:innerWidth,height:innerHeight},documentWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth,entry:rect(entry),card:rect(card),cardGrid:getComputedStyle(card).gridTemplateColumns,cardChildren:[...card.children].map(child=>({className:String(child.className),box:rect(child),gridColumn:getComputedStyle(child).gridColumn})),ancestry,controls,offenders,edgeOverflow};
            }""")
            visual_audit = page.evaluate("""() => {
              const visible = element => { const box=element.getBoundingClientRect(), style=getComputedStyle(element); return box.width>0&&box.height>0&&style.display!=='none'&&style.visibility!=='hidden'&&Number(style.opacity)!==0; };
              const box = element => { const r=element.getBoundingClientRect(); return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}; };
              const positioned = [...document.querySelectorAll('article.card,.performanceEntry,.exerciseTracker,.warmupSteps,.warmupVisual,.muscleDayGrid,#summaryToggle,#floatingSessionSummary')].filter(visible).map(element=>({tag:element.tagName,id:element.id,className:String(element.className).slice(0,90),box:box(element)}));
              const controls = [...document.querySelectorAll('button:not([hidden]),input:not([hidden]),select:not([hidden]),[role=button]:not([hidden])')].filter(visible).map(element=>({tag:element.tagName,id:element.id,className:String(element.className).slice(0,80),label:(element.getAttribute('aria-label')||element.innerText||element.getAttribute('title')||'').trim().slice(0,80),box:box(element)}));
              const textSelector = '.exTitle,.zone,.coachHeader,.techStepTitle,.techStepText,.phaseLabel,.source,.performanceFieldTitle,.metricLabel,.metricVal,.warmupIndex,.warmupHead h2,.warmupCopy h3,.warmupCopy p,.warmupInstructions,.warmupMediaLabel';
              const text = [...document.querySelectorAll(textSelector)].filter(visible).map(element=>{const s=getComputedStyle(element);return {tag:element.tagName,className:String(element.className).slice(0,70),text:(element.innerText||element.textContent||'').trim().replace(/\\s+/g,' ').slice(0,100),box:box(element),scrollWidth:element.scrollWidth,clientWidth:element.clientWidth,scrollHeight:element.scrollHeight,clientHeight:element.clientHeight,overflowX:s.overflowX,overflowY:s.overflowY,textOverflow:s.textOverflow,lineClamp:s.webkitLineClamp};});
              const clippedText = text.filter(item => (item.scrollWidth>item.clientWidth+2 && ['hidden','clip'].includes(item.overflowX) && item.textOverflow!=='ellipsis') || (item.scrollHeight>item.clientHeight+2 && ['hidden','clip'].includes(item.overflowY) && item.lineClamp==='none'));
              const offscreen = positioned.filter(item=>item.box.left < -1 || item.box.right > innerWidth+1);
              const clippedControls = controls.filter(item=>item.box.left < -1 || item.box.right > innerWidth+1 || item.box.width<32 || item.box.height<32);
              const missingExerciseParts = [...document.querySelectorAll('article.card[data-exercise-index]')].map(card=>{const technique=card.querySelector('.techSteps,.techniqueSteps');return {exercise:card.dataset.exerciseIndex,title:card.querySelector('.exTitle')?.textContent.trim()||'',technique:Boolean(technique?.innerText.trim()),techniqueCharacters:technique?.innerText.trim().length||0,cta:card.querySelectorAll('.completeSetButton').length,reps:card.querySelectorAll('input.performanceReps').length,load:card.querySelectorAll('input.performanceLoad').length,progress:card.querySelectorAll('.seriesProgressSegment').length};}).filter(item=>!item.title||!item.technique||item.cta!==1||item.reps!==1||item.load!==1||item.progress===0);
              const detachedTechniqueSections=[...document.querySelectorAll('.techSteps,.techniqueSteps')].filter(section=>!section.closest('article.card')).map(section=>({text:(section.innerText||'').trim().slice(0,90),parent:section.parentElement?.tagName+'.'+String(section.parentElement?.className||''),grandparent:section.parentElement?.parentElement?.tagName+'.'+String(section.parentElement?.parentElement?.className||'')}));
              const allExerciseCards=[...document.querySelectorAll('article.card[data-exercise-index]')];
              const cardTopology={total:allExerciseCards.length,insideRoutineGrid:document.querySelectorAll('main.cards>article.card[data-exercise-index]').length,detached:allExerciseCards.filter(card=>card.parentElement!==document.querySelector('main.cards')).map(card=>card.dataset.exerciseIndex)};
              return {positioned:positioned.length,controls:controls.length,textNodes:text.length,offscreen,clippedText,clippedControls,missingExerciseParts,detachedTechniqueSections,cardTopology};
            }""")
            if layout["documentWidth"] > width:
                raise AssertionError(f"{name} {width}x{height}: el documento permite desplazamiento horizontal: ancho={layout['documentWidth']}, viewport={width}, bordes={layout['edgeOverflow']}, elementosConOverflow={layout['offenders']}")
            if layout["entry"]["left"] < -1 or layout["entry"]["right"] > width + 1:
                raise AssertionError(f"{name} {width}x{height}: zona de registro fuera del viewport: {layout['entry']}")
            if any(control["left"] < -1 or control["right"] > width + 1 for control in layout["controls"]):
                raise AssertionError(f"{name} {width}x{height}: control recortado horizontalmente: {layout['controls']}")
            if visual_audit["offscreen"] or visual_audit["clippedText"] or visual_audit["clippedControls"] or visual_audit["missingExerciseParts"] or visual_audit["detachedTechniqueSections"] or visual_audit["cardTopology"]["total"] != visual_audit["cardTopology"]["insideRoutineGrid"]:
                raise AssertionError(f"{name} {width}x{height}: auditoría de geometría visual falló: {visual_audit}")

            overlap = None
            if width <= 640:
                warmup = page.locator("#warmupAction")
                warmup.scroll_into_view_if_needed()
                warmup.click()
                page.clock.run_for(15_000)
                warmup.click()
                warmup.click()
                button = page.locator("article.card[data-exercise-index]").first.locator(".completeSetButton")
                button.scroll_into_view_if_needed()
                button.click()  # aproximación
                button.click()  # preparación de serie efectiva
                page.clock.run_for(15_000)
                summary = page.locator("#floatingSessionSummary")
                if page.locator("#summaryToggle").get_attribute("aria-expanded") != "true":
                    page.locator("#summaryToggle").click()
                button.scroll_into_view_if_needed()
                overlap = page.evaluate("""() => {
                  const button = document.querySelector('.completeSetButton');
                  const panel = document.querySelector('#floatingSessionSummary');
                  const a = button.getBoundingClientRect(), b = panel.getBoundingClientRect();
                  return {button:{left:a.left,right:a.right,top:a.top,bottom:a.bottom},panel:{left:b.left,right:b.right,top:b.top,bottom:b.bottom},intersects:a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top};
                }""")
                if overlap["intersects"]:
                    raise AssertionError(f"{name} {width}x{height}: resumen flotante tapa el botón de acción: {overlap}")
            results.append({"routine": name, "viewport": f"{width}x{height}", "horizontalOverflow": False, "visualGeometry": visual_audit, "actionPanelOverlap": overlap})
            context.close()
    return {"viewports": len(RESPONSIVE_VIEWPORTS), "routineViewportChecks": results}


def validate_resource_pages(browser) -> list[dict]:
    """Recorre todos los recursos visuales de cada plantilla en un viewport móvil realista."""
    results = []
    home_context = browser.new_context(viewport={"width": 412, "height": 915}, device_scale_factor=2, is_mobile=True, has_touch=True)
    home_context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    home = home_context.new_page()
    home.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
    results.append({"routine": "Inicio", **assert_image_inventory(home, "Inicio")})
    home_context.close()
    for name, _sex, _variant in ROUTINES:
        context = browser.new_context(viewport={"width": 412, "height": 915}, device_scale_factor=2, is_mobile=True, has_touch=True)
        context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
        page = context.new_page()
        page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="networkidle")
        inventory = assert_image_inventory(page, name)
        quality = assert_visual_resource_quality(page, name)
        if SCREENSHOT_DIR is not None:
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            page.add_style_tag(content=".card .meta,.card .visual,.card .coach,.phaseRow,.phaseCol,.phaseLabel,.source,.photo,.photo img.realphoto{opacity:1!important;visibility:visible!important;transform:none!important;animation:none!important}.gifMotion{display:none!important}.gifFallback{display:block!important}")
            day = name.split("_")[2]
            cards = page.locator("article.card[data-exercise-index]")
            for index in range(cards.count()):
                phase_row = cards.nth(index).locator(".phaseRow").first
                if phase_row.count():
                    phase_row.scroll_into_view_if_needed()
                    phase_row.screenshot(path=str(SCREENSHOT_DIR / f"resource-day-{day}-exercise-{index+1:02d}.png"))
            anatomy = page.locator(".muscleDayGrid").first
            if anatomy.count():
                anatomy.scroll_into_view_if_needed()
                anatomy.screenshot(path=str(SCREENSHOT_DIR / f"resource-day-{day}-anatomy.png"))
            warmup = page.locator(".warmupSteps").first
            if warmup.count():
                warmup.scroll_into_view_if_needed()
                warmup.screenshot(path=str(SCREENSHOT_DIR / f"resource-day-{day}-warmup.png"))
        result = {"routine": name, **inventory, "quality": quality}
        results.append(result)
        context.close()
    return results


def main() -> None:
    global SCREENSHOT_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshot-dir", type=Path, default=SCREENSHOT_DIR, help="opcional: guarda capturas de actividad y fallbacks en viewport móvil")
    parser.add_argument("--responsive-only", action="store_true", help="ejecuta solo la matriz de tamaños móviles")
    parser.add_argument("--resources-only", action="store_true", help="valida imágenes, proporciones y legibilidad de las cuatro rutinas")
    parser.add_argument("--functional-only", action="store_true", help="ejecuta los flujos funcionales táctiles de las cuatro rutinas")
    args = parser.parse_args()
    SCREENSHOT_DIR = args.screenshot_dir
    server = ThreadingHTTPServer(("127.0.0.1", PORT), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    results = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            if args.resources_only:
                results = validate_resource_pages(browser)
                responsive = None
                offline = None
            else:
                responsive = None if args.functional_only else validate_responsive_layout(browser)
            if not args.responsive_only and not args.resources_only:
                for name, sex, variant in ROUTINES:
                    day_result = validate_day(browser, name, sex, variant)
                    day_result.update(validate_primary_set_buttons(browser, name, sex))
                    results.append(day_result)
                offline = None if args.functional_only else validate_installed_offline_package(browser)
            else:
                offline = None
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    print(json.dumps({"status": "E2E_ROUTINES_OK", "days": len(results), "results": results, "responsive": responsive, "offlinePackage": offline}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
