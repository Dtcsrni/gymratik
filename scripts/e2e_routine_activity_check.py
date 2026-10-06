"""E2E visual/funcional para las cuatro rutinas y mascotas de actividad.

Uso: python scripts/e2e_routine_activity_check.py
Requiere Playwright para Python y Chromium disponible en el host.
Todos los datos se crean en contextos efímeros del navegador.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

from PIL import Image
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


def service_worker_cache_name(source: str) -> str:
    """Return the exact cache identifier declared by the generated worker."""
    match = re.search(r"^const CACHE_NAME = '([^']+)';$", source, flags=re.MULTILINE)
    if not match:
        raise AssertionError("sw.js no declara CACHE_NAME con el formato esperado")
    return match.group(1)


def capture_visual(page, filename: str) -> None:
    if SCREENSHOT_DIR is None:
        return
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SCREENSHOT_DIR / filename), full_page=False)


def validate_home_cover_animation(browser) -> dict:
    """Verify poster artwork with subtle drift and the slow animated loading/update splash."""
    context = browser.new_context(viewport={"width": 412, "height": 915}, device_scale_factor=2, is_mobile=True, has_touch=True)
    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1','true');localStorage.setItem('gymratik-network-preference-v1','always')")
    page = context.new_page()
    page.goto(f"http://127.0.0.1:{PORT}/", wait_until="domcontentloaded")
    page.wait_for_function("!document.documentElement.classList.contains('gymratik-loading') && getComputedStyle(document.querySelector('#appSplash')).visibility === 'hidden'", timeout=15_000)
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    page.wait_for_function("(() => { const hero=document.querySelector('.hero')?.getBoundingClientRect(); return hero && hero.top < innerHeight && hero.bottom > 0; })()", timeout=10_000)
    image = page.locator("#heroStrengthArt")
    page.wait_for_function("document.querySelector('#heroStrengthArt')?.currentSrc.endsWith('gymratik-cover-seated-v1-poster.webp')")
    visible = image.evaluate("element => ({complete:element.complete, size:[element.naturalWidth,element.naturalHeight], src:element.currentSrc, stage:(() => { const stage=element.parentElement.getBoundingClientRect(); const box=element.getBoundingClientRect(); return {stage:[stage.left,stage.top,stage.right,stage.bottom], image:[box.left,box.top,box.right,box.bottom]} })()})")
    if not visible["complete"] or visible["size"] != [372, 332]:
        context.close()
        raise AssertionError(f"El arte estático sentado de bienvenida no carga como WebP apaisado: {visible}")
    stage = visible["stage"]["stage"]
    bounds = visible["stage"]["image"]
    if bounds[0] < stage[0] - 1 or bounds[1] < stage[1] - 1 or bounds[2] > stage[2] + 1 or bounds[3] > stage[3] + 1:
        context.close()
        raise AssertionError(f"El arte de bienvenida se recorta en el escenario: {visible}")
    first_source = image.evaluate("element => element.currentSrc")
    first_transform = image.evaluate("element => getComputedStyle(element).transform")
    capture_visual(page, "home-welcome-subtle-motion-mobile.png")
    page.wait_for_timeout(650)
    second_source = image.evaluate("element => element.currentSrc")
    second_transform = image.evaluate("element => getComputedStyle(element).transform")
    if first_source != second_source or not second_source.endswith("gymratik-cover-seated-v1-poster.webp"):
        context.close()
        raise AssertionError("La portada debe conservar el mismo póster fijo")
    if first_transform == second_transform:
        context.close()
        raise AssertionError("El movimiento sutil y lento de la portada no avanza")
    cover_viewports = []
    for width, height in RESPONSIVE_VIEWPORTS:
        page.set_viewport_size({"width": width, "height": height})
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        page.wait_for_timeout(80)
        geometry = image.evaluate("element => { const stage=element.parentElement.getBoundingClientRect(), box=element.getBoundingClientRect(), actions=document.querySelector('.hero-actions').getBoundingClientRect(); return {stage:[stage.left,stage.top,stage.right,stage.bottom],image:[box.left,box.top,box.right,box.bottom],actionsTop:actions.top} }")
        stage, bounds = geometry["stage"], geometry["image"]
        center_delta = [abs((bounds[0] + bounds[2] - stage[0] - stage[2]) / 2), abs((bounds[1] + bounds[3] - stage[1] - stage[3]) / 2)]
        uncropped = bounds[0] >= stage[0] - 1 and bounds[1] >= stage[1] - 1 and bounds[2] <= stage[2] + 1 and bounds[3] <= stage[3] + 1
        centered = max(center_delta) <= 1.5
        buttons_clear = geometry["stage"][3] <= geometry["actionsTop"] + 1
        if not uncropped or not centered or not buttons_clear:
            context.close()
            raise AssertionError(f"El arte sentado se recorta o queda debajo de los botones a {width}x{height}: {geometry}; delta={center_delta}")
        cover_viewports.append({"viewport": [width, height], "centerDeltaPx": center_delta, "centered": centered, "uncropped": uncropped, "buttonsClear": buttons_clear})
    page.evaluate("window.scrollTo({top:document.body.scrollHeight,behavior:'instant'})")
    if not image.evaluate("element => element.currentSrc.endsWith('gymratik-cover-seated-v1-poster.webp')"):
        context.close()
        raise AssertionError("La portada no conserva el poster estático al salir del viewport")
    page.evaluate("document.querySelector('#appSplash').setAttribute('aria-hidden','false');document.documentElement.classList.add('gymratik-loading')")
    page.wait_for_function("element => element.complete && element.naturalWidth === 352 && element.currentSrc.endsWith('gymratik-cover-seated-breath-30fps.webp')", arg=page.locator("#splashPoseArt").element_handle())
    splash_art = page.locator("#splashPoseArt")
    splash_first = splash_art.screenshot()
    capture_visual(page, "home-loading-slow-animation-mobile.png")
    page.wait_for_timeout(800)
    splash_second = splash_art.screenshot()
    if splash_first == splash_second:
        context.close()
        raise AssertionError("La animación lenta de carga no avanzó en pantalla")
    page.evaluate("document.documentElement.classList.remove('gymratik-loading');document.querySelector('#appSplash').setAttribute('aria-hidden','true')")
    context.close()

    reduced_context = browser.new_context(viewport={"width": 412, "height": 915}, reduced_motion="reduce", is_mobile=True, has_touch=True)
    reduced_context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1','true');localStorage.setItem('gymratik-network-preference-v1','always')")
    reduced_page = reduced_context.new_page()
    reduced_page.goto(f"http://127.0.0.1:{PORT}/", wait_until="domcontentloaded")
    reduced_page.wait_for_function("!document.documentElement.classList.contains('gymratik-loading') && getComputedStyle(document.querySelector('#appSplash')).visibility === 'hidden'", timeout=15_000)
    reduced_page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    reduced_page.wait_for_function("window.scrollY === 0 && (() => { const hero=document.querySelector('.hero')?.getBoundingClientRect(); return hero && hero.top < innerHeight && hero.bottom > 0; })()")
    reduced_page.wait_for_function("document.querySelector('#heroStrengthArt')?.currentSrc.endsWith('gymratik-cover-seated-v1-poster.webp')")
    reduced = reduced_page.locator("#heroStrengthArt").evaluate("element => ({src:element.currentSrc,complete:element.complete,naturalWidth:element.naturalWidth,animation:getComputedStyle(element).animationName})")
    capture_visual(reduced_page, "home-cover-reduced-motion-mobile.png")
    reduced_context.close()
    if not reduced["complete"] or reduced["naturalWidth"] != 372 or not reduced["src"].endswith("gymratik-cover-seated-v1-poster.webp") or reduced["animation"] != "none":
        raise AssertionError(f"prefers-reduced-motion no usa el poster estático: {reduced}")
    animation_path = ROOT / "assets/branding/gymratik-cover-seated-breath-30fps.webp"
    with Image.open(animation_path) as animation:
        frame_count = animation.n_frames
        animation.seek(0)
        animation.convert("RGBA")
        animation.seek(1)
        frame_duration_ms = animation.info.get("duration")
    return {
        "viewport": [412, 915],
        "frames": frame_count,
        "nominalFps": round(1000 / frame_duration_ms) if frame_duration_ms else None,
        "cycleDurationMs": frame_count * frame_duration_ms if frame_duration_ms else None,
        "welcomeMotion": "mascotas-sentadas-con-deriva-css-sutil",
        "splashBreathing": "respiracion-local-suave-en-ciclo-cerrado",
        "loop": "closed",
        "welcomeImageStatic": True,
        "splashFramesAdvance": True,
        "offscreenWelcomeRemainsStatic": True,
        "reducedMotionPoster": True,
        "responsiveViewports": cover_viewports,
    }


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, _format, *_args):
        pass


def create_isolated_server() -> ThreadingHTTPServer:
    """Serve synthetic tests on an OS-assigned port, separate from ADB's 8768."""
    return ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)


def assert_image_inventory(page, routine_name: str) -> dict:
    images = page.locator("img")
    for index in range(images.count()):
        image = images.nth(index)
        source = image.get_attribute("src") or ""
        state = image.evaluate("""image => {const box=image.getBoundingClientRect();let painted=true;for(let node=image;node;node=node.parentElement){const style=getComputedStyle(node);if(node.hidden||style.display==='none'||style.visibility==='hidden'||Number(style.opacity)===0){painted=false;break}}return {visible:painted&&box.width>0&&box.height>0,hidden:image.hidden,complete:image.complete,naturalWidth:image.naturalWidth}}""")
        if not source or state["hidden"] or not state["visible"] or not image.is_visible():
            continue
        # A continuously breathing cover is never considered geometrically
        # stable by Playwright's auto-scroll action. An instant DOM scroll is
        # deterministic and still triggers lazy loading at the target image.
        image.evaluate("image => image.scrollIntoView({block:'center',behavior:'instant'})")
        refreshed = image.evaluate("image => {const box=image.getBoundingClientRect();let painted=true;for(let node=image;node;node=node.parentElement){const style=getComputedStyle(node);if(node.hidden||style.display==='none'||style.visibility==='hidden'||Number(style.opacity)===0){painted=false;break}}return {visible:painted&&box.width>0&&box.height>0,hidden:image.hidden,connected:image.isConnected}}")
        if not refreshed["connected"] or refreshed["hidden"] or not refreshed["visible"] or not image.is_visible():
            continue
        try:
            page.wait_for_function(
                "image => image.complete && image.naturalWidth > 0 && image.naturalHeight > 0",
                arg=image.element_handle(),
                timeout=20_000,
            )
            image.evaluate("image => image.decode()")
        except Exception as error:
            raise AssertionError(f"{routine_name}: recurso no decodifica al mostrarse: {source[:140]}") from error
    page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
    # Scrolling back can trigger the battery-aware GIF/poster swap one last
    # time. Require decoded dimensions and an unchanged source across two
    # polls; `complete` alone can describe a stale request during a source swap.
    try:
        page.wait_for_function(
            """() => [...document.images].every(image => {
          const rect = image.getBoundingClientRect();
          const onScreen = rect.bottom > 0 && rect.top < innerHeight && rect.right > 0 && rect.left < innerWidth;
          let painted=true;for(let node=image;node;node=node.parentElement){const style=getComputedStyle(node);if(node.hidden||style.display==='none'||style.visibility==='hidden'||Number(style.opacity)===0){painted=false;break}}
          const visible = onScreen && painted && rect.width > 0 && rect.height > 0;
          return !visible || (image.complete && image.naturalWidth > 0 && image.naturalHeight > 0);
        })""",
            timeout=20_000,
        )
    except Exception as error:
        pending = page.evaluate("""() => [...document.images].filter(image => {
          const r=image.getBoundingClientRect(),s=getComputedStyle(image);
          return r.bottom>0&&r.top<innerHeight&&r.right>0&&r.left<innerWidth&&!image.hidden
            &&r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'&&Number(s.opacity)!==0
            &&(!image.complete||image.naturalWidth<=0||image.naturalHeight<=0);
        }).map(image=>({id:image.id,className:image.className,alt:image.alt,html:image.outerHTML.slice(0,260),src:image.currentSrc||image.src,motion:image.dataset.batteryMotionSrc||'',complete:image.complete,
          size:[image.naturalWidth,image.naturalHeight],box:(()=>{const r=image.getBoundingClientRect();return [r.left,r.top,r.right,r.bottom]})(),
          paused:image.dataset.batteryPaused||'',fallback:image.parentElement?.querySelector('.warmupFallback,.gifFallback')?.currentSrc||''}))""")
        raise AssertionError(f"{routine_name}: imágenes visibles no estabilizaron tras volver al inicio: {pending}") from error
    page.wait_for_timeout(120)
    page.wait_for_function(
        """() => {
          const images = [...document.images];
          const visible = images.filter(image => {
            const rect=image.getBoundingClientRect();let painted=true;for(let node=image;node;node=node.parentElement){const style=getComputedStyle(node);if(node.hidden||style.display==='none'||style.visibility==='hidden'||Number(style.opacity)===0){painted=false;break}}
            return rect.bottom>0 && rect.top<innerHeight && rect.right>0 && rect.left<innerWidth
              && painted && rect.width>0 && rect.height>0;
          });
          if (!visible.every(image => image.complete && image.naturalWidth>0 && image.naturalHeight>0)) return false;
          const signature = visible.map(image => `${image.currentSrc||image.src}:${image.naturalWidth}x${image.naturalHeight}`).join('|');
          const stable = window.__gymratikImageAuditSignature === signature;
          window.__gymratikImageAuditSignature = signature;
          return stable;
        }""",
        timeout=5_000,
    )
    inventory = page.evaluate(
        """async () => {
          const images = [...document.images];
          return await Promise.all(images.map(async image => {
            const rect = image.getBoundingClientRect();
            let painted=true;for(let node=image;node;node=node.parentElement){const ancestorStyle=getComputedStyle(node);if(node.hidden||ancestorStyle.display==='none'||ancestorStyle.visibility==='hidden'||Number(ancestorStyle.opacity)===0){painted=false;break}}
            const rendered = painted && rect.width > 0 && rect.height > 0;
            const onScreen = rect.bottom > 0 && rect.top < innerHeight && rect.right > 0 && rect.left < innerWidth;
            const visible = rendered && onScreen;
            const style=getComputedStyle(image);
            let decodeError = '';
            const sourceBeforeDecode = image.currentSrc || image.src;
            if (!image.complete || image.naturalWidth <= 0 || image.naturalHeight <= 0) {
              if (visible) decodeError = 'visible image is incomplete or has no decoded dimensions';
            } else if (visible) {
              try { await image.decode(); } catch (error) {
                // Battery-aware GIFs can swap to their poster while decode() is
                // pending. Retry the current source before calling it broken.
                const sourceAfterFailure = image.currentSrc || image.src;
                if (sourceAfterFailure !== sourceBeforeDecode) {
                  try { await image.decode(); } catch (retryError) { decodeError = String(retryError); }
                } else {
                  decodeError = String(error);
                }
              }
            }
            const frame = image.closest('.warmupVisual,.gifFrame');
            const fallback = image.parentElement?.querySelector('.warmupFallback,.gifFallback');
            const fallbackRect = fallback?.getBoundingClientRect();
            return {
              src: image.currentSrc?.startsWith('data:') ? `data:${image.currentSrc.slice(5, image.currentSrc.indexOf(';') > 0 ? image.currentSrc.indexOf(';') : image.currentSrc.indexOf(','))}` : image.currentSrc || image.src,
              motionSource: image.dataset.batteryMotionSrc || '',
              className: image.className,
              complete: image.complete,
              naturalWidth: image.naturalWidth,
              naturalHeight: image.naturalHeight,
              renderedWidth: Math.round(rect.width),
              renderedHeight: Math.round(rect.height),
              display: style.display,
              visible,
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
    broken = [item for item in inventory if item["src"] and item["visible"] and (not item["complete"] or not item["naturalWidth"] or not item["naturalHeight"] or item["decodeError"])]
    if broken:
        raise AssertionError(f"{routine_name}: imágenes que no decodifican: {json.dumps(broken, ensure_ascii=False)}")
    invalid_layout = [item for item in inventory if item["visible"] and (item["renderedWidth"] <= 0 or item["renderedHeight"] <= 0)]
    if invalid_layout:
        raise AssertionError(f"{routine_name}: imágenes sin tamaño renderizado: {invalid_layout}")
    remote = [item["src"] for item in inventory if item["src"] and not item["src"].startswith(("http://127.0.0.1:", "http://localhost:", "data:image/"))]
    if remote:
        raise AssertionError(f"{routine_name}: recursos visuales inesperados fuera del servidor local: {remote}")
    return {
        "images": len(inventory),
        "rendered": sum(item["visible"] for item in inventory),
        "offlineStaticFallbacks": 0,
        "animatedGifs": sum("/videos/" in item["motionSource"] for item in inventory),
    }


def assert_exercise_phase_pairs(page, routine_name: str) -> dict:
    """Verifica que cada ejercicio tenga dos imágenes estáticas válidas.

    Hip thrust es la única excepción deliberada: su recurso de movimiento fue
    rechazado por no corresponder a la máquina; se conserva una guía visual de
    tres pasos y no se etiqueta una ilustración incorrecta como inicio/final.
    """
    cards = page.locator("article.card[data-exercise-index]")
    checked = 0
    for index in range(cards.count()):
        card = cards.nth(index)
        exercise_number = card.get_attribute("data-exercise-index") or str(index + 1)
        if routine_name == "Rutina_Dia_2_Pierna_Gluteo_V1.html" and exercise_number == "2":
            guide = card.locator(".hipThrustGuideTitle")
            if guide.count() != 3 or card.locator(".phaseRow .phaseCol").count():
                raise AssertionError(f"{routine_name}: hip thrust debe conservar su guía explícita de tres pasos")
            continue

        row = card.locator(".phaseRow")
        columns = row.locator(":scope > .phaseCol")
        if row.count() != 1 or columns.count() != 2:
            raise AssertionError(f"{routine_name}: ejercicio {exercise_number} debe tener exactamente las fases inicio y final")
        row.evaluate("element => element.scrollIntoView({block:'center',behavior:'instant'})")
        endpoints = []
        for phase_index, expected_label in enumerate(("inicio", "final")):
            column = columns.nth(phase_index)
            label = (column.locator(".phaseLabel").inner_text() if column.locator(".phaseLabel").count() else "").casefold()
            if expected_label not in label:
                raise AssertionError(f"{routine_name}: ejercicio {exercise_number} fase {phase_index + 1} sin etiqueta {expected_label!r}")
            image = column.locator(".photo img.realphoto")
            if image.count() != 1:
                raise AssertionError(f"{routine_name}: ejercicio {exercise_number} fase {expected_label} no tiene exactamente una imagen real")
            try:
                page.wait_for_function(
                    "image => image.complete && image.naturalWidth >= 180 && image.naturalHeight >= 180",
                    arg=image.element_handle(),
                    timeout=20_000,
                )
                image.evaluate("image => image.decode()")
            except Exception as error:
                raise AssertionError(f"{routine_name}: ejercicio {exercise_number} fase {expected_label} no decodifica a resolución mínima") from error
            state = image.evaluate("image => {const r=image.getBoundingClientRect(),p=image.closest('.photo')?.getBoundingClientRect();return {src:image.currentSrc||image.src,alt:image.alt,box:[r.width,r.height],frame:p?[p.width,p.height]:[0,0],fit:getComputedStyle(image).objectFit}}")
            if not state["alt"].strip() or min(state["box"]) <= 0 or min(state["frame"]) <= 0:
                raise AssertionError(f"{routine_name}: ejercicio {exercise_number} fase {expected_label} no es legible/renderizable: {state}")
            if state["fit"] not in ("contain", "scale-down"):
                raise AssertionError(f"{routine_name}: ejercicio {exercise_number} fase {expected_label} usa recorte {state['fit']!r}")
            endpoints.append(state["src"])
        if endpoints[0] == endpoints[1]:
            raise AssertionError(f"{routine_name}: ejercicio {exercise_number} repite el mismo recurso para inicio y final")
        checked += 1
    return {"exercisePairsValidated": checked, "intentionalHipThrustGuide": routine_name == "Rutina_Dia_2_Pierna_Gluteo_V1.html"}


def assert_warmup_single_viewers(page, routine_name: str) -> dict:
    """Each warm-up block exposes all choices but mounts and loads one GIF at a time."""
    groups = page.locator(".warmupSingleViewer")
    if not groups.count():
        raise AssertionError(f"{routine_name}: no se generaron visores únicos de calentamiento")
    before_keys = page.evaluate("() => Object.keys(localStorage).sort()")
    checked = []
    for group_index in range(groups.count()):
        group = groups.nth(group_index)
        images = group.locator(":scope > .warmupVisual .warmupGif")
        choices = group.locator(".warmupMediaChoice")
        if images.count() != 1 or choices.count() < 2:
            raise AssertionError(
                f"{routine_name}: bloque {group_index + 1} debe tener un solo GIF y opciones: "
                f"gifs={images.count()} opciones={choices.count()}"
            )
        group.scroll_into_view_if_needed()
        for choice_index in range(choices.count()):
            choice = choices.nth(choice_index)
            expected_src = choice.get_attribute("data-gif-src") or ""
            expected_poster = choice.get_attribute("data-poster-src") or ""
            expected_label = choice.get_attribute("data-label") or ""
            if not expected_src or not expected_poster or not expected_label:
                raise AssertionError(f"{routine_name}: alternativa sin GIF, poster o rótulo")
            click_control(choice)
            image = images.first
            page.wait_for_function(
                "({image, source}) => image.getAttribute('src') === source && !image.hidden && image.naturalWidth > 0",
                arg={"image": image.element_handle(), "source": expected_src},
            )
            image.evaluate("image => image.decode()")
            rendered = image.evaluate(
                "image => ({src:new URL(image.getAttribute('src'),location.href).pathname,"
                "naturalWidth:image.naturalWidth,naturalHeight:image.naturalHeight,hidden:image.hidden,"
                "alt:image.alt,posterHidden:image.parentElement.querySelector('.warmupFallback').hidden})"
            )
            expected_path = page.evaluate("src => new URL(src,location.href).pathname", expected_src)
            if (
                rendered["src"] != expected_path
                or not rendered["naturalWidth"]
                or not rendered["naturalHeight"]
                or rendered["hidden"]
                or not rendered["posterHidden"]
                or not rendered["alt"].strip()
                or choice.get_attribute("aria-pressed") != "true"
            ):
                raise AssertionError(f"{routine_name}: alternativa no se mostró correctamente: {rendered}")
            selected = group.locator('.warmupMediaChoice[aria-pressed="true"]').count()
            if selected != 1 or images.count() != 1:
                raise AssertionError(f"{routine_name}: hay más de una alternativa activa en el calentamiento")
            if SCREENSHOT_DIR:
                routine_id = routine_name.split("_")[2]
                screenshot_path = SCREENSHOT_DIR / f"day-{routine_id}-warmup-{group_index + 1:02}-{choice_index + 1:02}.png"
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                group.screenshot(path=str(screenshot_path))
            checked.append(expected_label)
        first = group.locator(".warmupMediaChoice").first
        click_control(first)
        group.evaluate("element => element.scrollIntoView({block:'center',behavior:'instant'})")
    after_keys = page.evaluate("() => Object.keys(localStorage).sort()")
    if before_keys != after_keys:
        raise AssertionError(f"{routine_name}: elegir una animación alteró claves de progreso local")
    return {"groups": groups.count(), "choicesChecked": checked, "oneGifMountedPerGroup": True, "progressKeysUnchanged": True}


def assert_visual_resource_quality(page, routine_name: str) -> dict:
    """Valida tamaño, proporción, ajuste y legibilidad de recursos instructivos."""
    audit = page.evaluate("""() => {
      const rect = element => { const r=element.getBoundingClientRect(); return {width:r.width,height:r.height}; };
      const images = [...document.querySelectorAll('.phaseRow .photo img.realphoto,.warmupVisual img,.gifFrame img,.muscleDayVisual img')].map(image => {
        const box=rect(image), parent=rect(image.parentElement), style=getComputedStyle(image);
        return {group:image.matches('.phaseRow .photo img.realphoto')?'exercise':image.matches('.warmupVisual img')?'warmup':image.matches('.gifFrame img')?'gif':'anatomy',src:image.currentSrc||image.src,motionSource:image.dataset.batteryMotionSrc||'',alt:image.alt,ariaHidden:image.getAttribute('aria-hidden')==='true',naturalWidth:image.naturalWidth,naturalHeight:image.naturalHeight,width:box.width,height:box.height,parentWidth:parent.width,parentHeight:parent.height,fit:style.objectFit,position:style.objectPosition,hidden:image.hidden,display:style.display};
      });
      const captions=[...document.querySelectorAll('.phaseRow .phaseLabel,.phaseRow .source,.warmupHead p,.warmupCopy p,.warmupInstructions')].map(element=>({tag:element.tagName,className:String(element.className),text:element.textContent.trim().slice(0,90),fontSize:parseFloat(getComputedStyle(element).fontSize),width:rect(element).width})).filter(item=>item.width>0);
      const techniqueGuides=[...document.querySelectorAll('article.card[data-exercise-index]')].map(card=>{const panel=card.querySelector('.techSteps'),steps=[...(panel?.querySelectorAll(':scope > .techStep')||[])],box=panel?.getBoundingClientRect(),style=panel?getComputedStyle(panel):null;return {exercise:card.dataset.exerciseIndex,stepTypes:steps.map(step=>['setup','move','warning'].find(type=>step.classList.contains(type))||'missing'),stepTitles:steps.map(step=>step.querySelector('.techStepTitle span')?.textContent.trim()||''),columns:style?style.gridTemplateColumns.split(/\\s+/).filter(Boolean).length:0,width:box?.width||0,steps:steps.map(step=>{const r=step.getBoundingClientRect(),text=step.querySelector('.techStepText'),t=text?.getBoundingClientRect(),s=text?getComputedStyle(text):null;return {width:r.width,height:r.height,textWidth:t?.width||0,textClientWidth:text?.clientWidth||0,fontSize:s?parseFloat(s.fontSize):0}})}});
      const instructional=images.filter(image=>image.group==='exercise'&&!image.hidden&&image.display!=='none');
      const cropFractions=instructional.filter(image=>image.fit==='cover'&&image.naturalWidth&&image.naturalHeight&&image.width&&image.height).map(image=>{const source=image.naturalWidth/image.naturalHeight,box=image.width/image.height;return 1-Math.min(source,box)/Math.max(source,box)});
      const warmupViewers=[...document.querySelectorAll('.warmupSingleViewer')].map(group=>{const frame=group.querySelector(':scope > .warmupVisual'),g=group.getBoundingClientRect(),f=frame?.getBoundingClientRect(),style=getComputedStyle(group),buttons=[...group.querySelectorAll('.warmupMediaChoice')].map(button=>{const r=button.getBoundingClientRect();return {width:r.width,height:r.height,left:r.left,right:r.right}});return {viewport:innerWidth,groupWidth:g.width,frameWidth:f?.width||0,frameHeight:f?.height||0,paddingLeft:parseFloat(style.paddingLeft),paddingRight:parseFloat(style.paddingRight),widthRatio:g.width&&f?f.width/g.width:0,buttons}});
      return {images,captions,techniqueGuides,exerciseImages:instructional.length,minExerciseWidth:instructional.length?Math.min(...instructional.map(image=>image.width)):0,minExerciseHeight:instructional.length?Math.min(...instructional.map(image=>image.height)):0,maxExerciseCoverCrop:cropFractions.length?Math.max(...cropFractions):0,minCaptionFont:captions.length?Math.min(...captions.map(caption=>caption.fontSize)):0,fitModes:[...new Set(images.map(image=>image.fit))],warmupViewers};
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
    invalid_guides = [guide for guide in audit["techniqueGuides"] if guide["stepTypes"] != ["setup", "move", "warning"] or guide["stepTitles"] != ["Posición", "Movimiento", "Evita"] or guide["columns"] != 1 or any(step["width"] <= 0 or step["height"] < 52 or step["fontSize"] < 12 or step["textWidth"] > step["textClientWidth"] + 1 for step in guide["steps"])]
    if invalid_guides:
        raise AssertionError(f"{routine_name}: la guía técnica no usa el marco/orden común y legible en cada ejercicio: {invalid_guides}; guías={audit['techniqueGuides']}")
    if audit["maxExerciseCoverCrop"] > 0.48:
        worst = [item for item in audit["images"] if item["group"] == "exercise" and item["fit"] == "cover"]
        raise AssertionError(f"{routine_name}: recorte potencialmente excesivo (>48% de un eje): {audit['maxExerciseCoverCrop']:.2%}; recursos={worst}")
    invalid_warmup_viewers = [
        item for item in audit["warmupViewers"]
        if item["widthRatio"] < 0.9
        or not (4 <= item["paddingLeft"] <= 7.1 and 4 <= item["paddingRight"] <= 7.1)
        or any(button["height"] < 44 or button["left"] < -1 or button["right"] > item["viewport"] + 1 for button in item["buttons"])
    ]
    if invalid_warmup_viewers:
        raise AssertionError(f"{routine_name}: visor de calentamiento estrecho o controles difíciles de tocar: {invalid_warmup_viewers}")
    return {key:value for key,value in audit.items() if key != "images"} | {"imageGroups":{group:sum(item["group"]==group or (group=="gif" and "/videos/" in item["motionSource"]) for item in audit["images"]) for group in ("exercise","warmup","gif","anatomy")}}


def assert_animation_changes(page, image) -> None:
    has_css_motion = image.evaluate("element => getComputedStyle(element).animationName !== 'none'")
    diagnostic = """element => {
      const style = getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      const parent = element.parentElement;
      const parentStyle = parent ? getComputedStyle(parent) : null;
      return {
        src: element.currentSrc,
        loaded: element.complete,
        naturalSize: [element.naturalWidth, element.naturalHeight],
        motion: element.dataset.motion || null,
        animation: style.animationName,
        duration: style.animationDuration,
        playState: style.animationPlayState,
        transform: style.transform,
        rect: [rect.x, rect.y, rect.width, rect.height],
        parentAnimation: parentStyle?.animationName || null,
        visibility: document.visibilityState,
        reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches
      };
    }"""
    if not has_css_motion:
        first_frame = image.screenshot()
        for _ in range(10):
            time.sleep(0.22)
            if first_frame != image.screenshot():
                return
        raise AssertionError(f"No avanzó el elemento visual; GIF o fallback inmóvil: {image.evaluate(diagnostic)}")
    snapshot = """element => {
      const canvas = document.createElement('canvas');
      canvas.width = canvas.height = 128;
      const context = canvas.getContext('2d', {willReadFrequently:true});
      let pixels = 2166136261;
      try {
        context.drawImage(element, 0, 0, 128, 128);
        const data = context.getImageData(0, 0, 128, 128).data;
        for (let index = 0; index < data.length; index += 20) pixels = Math.imul(pixels ^ data[index], 16777619);
      } catch (_) { pixels = 0; }
      return `${getComputedStyle(element).transform}:${pixels}:${element.currentSrc}`;
    }"""
    motion_samples = image.evaluate("""async element => {
      const samples = [];
      for (let index = 0; index < 12; index += 1) {
        await new Promise(requestAnimationFrame);
        const animation = element.getAnimations()[0];
        samples.push({
          transform: getComputedStyle(element).transform,
          animationTime: animation?.currentTime ?? null,
          timelineTime: document.timeline.currentTime
        });
      }
      return samples;
    }""")
    if len({sample["transform"] for sample in motion_samples}) > 1:
        return
    raise AssertionError(f"La animación CSS no cambia de pose entre fotogramas: {image.evaluate(diagnostic)}; muestras={motion_samples}")


def assert_series_segment_fill_stable(page, routine_name: str) -> str:
    segment = page.locator("article.card .seriesProgressSegment.is-current")
    transform = segment.evaluate("element => getComputedStyle(element, '::after').transform")
    time.sleep(1.25)
    after = segment.evaluate("element => getComputedStyle(element, '::after').transform")
    if transform != after:
        raise AssertionError(f"{routine_name}: el relleno de la serie oscila durante actividad: {transform} -> {after}")
    return transform


def assert_mascot(page, variant: str, state: str, reduced: bool = False, static_fallback: bool = False) -> str:
    reduced = reduced or page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
    image = page.locator("#summaryActivityMascot")
    pose_state = {
        "start": "idle", "ready": "ready", "preparing": "preparing",
        "approximation": "warmup", "strength": "strength", "cardio": "cardio",
        "mobility": "mobility", "rest": "rest", "celebration": "approval",
    }[state]
    expected_suffix = (
        f"states-v1/{variant}-{pose_state}.png"
        if variant in ("male", "female")
        else f"{variant}-{'rest' if pose_state in ('rest', 'idle', 'ready') else 'exercise'}-still.webp"
    )
    try:
        page.wait_for_function(
            "suffix => document.querySelector('#summaryActivityMascot')?.getAttribute('src')?.endsWith(suffix)",
            arg=expected_suffix,
            timeout=10_000,
        )
    except Exception as error:
        actual = page.locator("#summaryActivityMascot").evaluate("element => ({src:element.getAttribute('src'),requestedSrc:element.dataset.requestedSrc,loadedSrc:element.dataset.loadedSrc,motion:element.dataset.motion,hidden:element.hidden,documentHidden:document.hidden,activity:document.querySelector('#summaryActivityStatus')?.dataset.activity,variant:window.gymratikMascotVariant,complete:element.complete,naturalWidth:element.naturalWidth})")
        raise AssertionError(
            f"La mascota no cargó el recurso esperado *{expected_suffix}; actual={actual}"
        ) from error
    src = image.get_attribute("src") or ""
    if not src.endswith(expected_suffix):
        raise AssertionError(f"Mascota inesperada: src={src!r}; se esperaba *{expected_suffix}")
    if image.is_hidden() or image.get_attribute("data-motion") != state or image.get_attribute("data-pose-state") != pose_state:
        status = page.locator("#summaryActivityStatus").evaluate("element => ({activity: element.dataset.activity, label: element.querySelector('#summaryActivityLabel')?.textContent, mascotHidden: document.querySelector('#summaryActivityMascot')?.hidden, motion: document.querySelector('#summaryActivityMascot')?.dataset.motion})")
        raise AssertionError(f"La mascota debe seguir visible y reflejar el modo {state}/{pose_state}: {status}")
    dimensions = image.evaluate("async image => { await image.decode(); const box = image.getBoundingClientRect(); return [image.naturalWidth, image.naturalHeight, box.width, box.height]; }")
    if dimensions[0:2] != [128, 128] or min(dimensions[2:]) <= 0:
        raise AssertionError(f"La mascota no se renderiza a tamaño válido: {dimensions}")
    if not reduced and not static_fallback and dimensions[2] < 50:
        raise AssertionError(f"La mascota de estado debe aprovechar mejor el espacio de la cabecera: {dimensions}")
    expected_animation = {
        "cardio": "mascotCardioCadence", "strength": "mascotStrengthEffort",
        "mobility": "mascotMobilityFlow", "start": "mascotIdleBreath",
        "ready": "mascotReadyShift", "preparing": "mascotPreparationBrace",
        "approximation": "mascotWarmupFlow", "rest": "mascotRecoveryBreath",
        "celebration": "mascotApprovalCelebrate",
    }.get(state)
    if expected_animation:
        animation = image.evaluate("element => getComputedStyle(element).animationName")
        if not reduced and animation != expected_animation:
            raise AssertionError(f"La mascota no tiene la animación específica de {state}: {animation!r}")
    if not reduced and not static_fallback:
        assert_animation_changes(page, image)
    return src


def assert_approval_toast(page, variant: str) -> dict:
    toast = page.locator("#gymratikEncouragement")
    page.wait_for_function("() => document.querySelector('#gymratikEncouragement')?.classList.contains('is-visible')", timeout=5_000)
    mascot = toast.locator(".toastMascot")
    source_suffix = f"states-v1/{variant}-approval.png" if variant in ("male", "female") else "neutral-exercise-still.webp"
    page.wait_for_function(
        "suffix => document.querySelector('#gymratikEncouragement .toastMascot')?.getAttribute('src')?.endsWith(suffix) && document.querySelector('#gymratikEncouragement .toastMascot')?.complete && document.querySelector('#gymratikEncouragement .toastMascot')?.naturalWidth > 0",
        arg=source_suffix,
        timeout=5_000,
    )
    if not toast.is_visible() or not mascot.is_visible():
        raise AssertionError("El toast de aprobación o su mascota no son visibles")
    dimensions = mascot.evaluate("image => {const r=image.getBoundingClientRect();return [image.naturalWidth,image.naturalHeight,r.width,r.height]}")
    animation = mascot.evaluate("image => getComputedStyle(image).animationName")
    if dimensions[:2] != [128, 128] or min(dimensions[2:]) < 40 or animation != "mascotToastApproval":
        raise AssertionError(f"La mascota de aprobación no se renderiza/animada correctamente: {dimensions}, {animation}")
    return {"visible": True, "srcSuffix": source_suffix, "dimensions": dimensions, "animation": animation}


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
    if activity in {"active", "strength"}:
        checks = (
            styles["activity"] == ("strength" if activity == "strength" else "active"),
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


def dispatch_touch_hold(page, button, duration_ms: int, release_click: bool = True, virtual_clock: bool = True) -> None:
    physical_hold = getattr(page, "_gt6_physical_hold", None)
    if physical_hold:
        physical_hold(page, button, duration_ms, release_click=release_click, virtual_clock=virtual_clock)
        return
    pointer = {"pointerId": 7, "pointerType": "touch", "isPrimary": True, "button": 0, "buttons": 1}
    button.evaluate("element => element.setAttribute('data-e2e-hold-target', 'true')")
    button.evaluate("element => { delete element.dataset.e2ePointerDownReceived; element.addEventListener('pointerdown', () => { element.dataset.e2ePointerDownReceived = 'true'; }, { capture: true, once: true }); }")
    button.dispatch_event("pointerdown", pointer)
    try:
        # La clase se agrega sincrónicamente en pointerdown. Consultarla por
        # requestAnimationFrame con page.clock congelado introduce falsos timeouts.
        holding_started = button.evaluate("element => element.classList.contains('is-holding')")
        if not holding_started:
            diagnostic = button.evaluate("""element => ({
              buttonClass:element.className,disabled:element.disabled,connected:element.isConnected,
              pointerDownReceived:element.dataset.e2ePointerDownReceived === 'true',ariaLabel:element.getAttribute('aria-label'),
              now:Date.now(),restCue:element.closest('article.card')?.querySelector('.metric.rest .timeCue')?.textContent || '',
              activity:document.querySelector('#summaryActivityStatus')?.dataset.activity || '',
              activityText:document.querySelector('#summaryActivityStatus')?.innerText || '',
              trackerIndex:element.closest('.exerciseTracker')?.dataset.exerciseIndex || '',
              seriesKeys:element.closest('.exerciseTracker')?.dataset.seriesKeys || '',
              persistedTiming:Object.entries(localStorage).filter(([key]) => /timing|series-v1/i.test(key)).map(([key,value]) => {
                try { const state=JSON.parse(value), exercises=state.__timing?.exercises || {}; return {key,exercises}; }
                catch (_) { return {key,unparsed:true}; }
              })
            })""")
            raise AssertionError(f"pointerdown no activó el feedback is-holding del botón: {diagnostic}")
        if virtual_clock:
            page.clock.run_for(duration_ms)
        else:
            page.wait_for_timeout(duration_ms)
        button.dispatch_event("pointerup", {**pointer, "buttons": 0})
        if release_click:
            button.dispatch_event("click", {})
    finally:
        button.evaluate("element => element.removeAttribute('data-e2e-hold-target')")


def dispatch_browser_hold(page, button, duration_ms: int) -> None:
    """Sostiene con eventos trusted para E2E sintético de botones en layout móvil."""
    box = button.bounding_box()
    if not box:
        raise AssertionError("El botón no tiene geometría visible para el gesto sostenido")
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    try:
        page.wait_for_timeout(duration_ms)
    finally:
        page.mouse.up()


def select_valid_performance(card) -> None:
    """Selecciona ambos datos con el incremento inicial disponible del equipo."""
    physical_select = getattr(card.page, "_gt6_physical_select_performance", None)
    if physical_select:
        physical_select(card)
        return
    reps = card.locator("input.performanceReps")
    load = card.locator("input.performanceLoad")
    reps.focus()
    reps.press("ArrowRight")
    load.focus()
    load.press("ArrowRight")
    if reps.get_attribute("data-selected") != "true" or card.locator(".performanceLoadValue").get_attribute("data-selected") != "true":
        raise AssertionError("No se pudo seleccionar una repetición y carga válidas para la serie")


def click_control(locator) -> None:
    """Usa gesto táctil CDP cuando el locator pertenece al WebAPK físico."""
    physical_tap = getattr(locator.page, "_gt6_physical_tap", None)
    if physical_tap:
        physical_tap(locator)
    else:
        locator.click()


def install_test_clock(page) -> None:
    """Install deterministic time in Chromium, including CDP-connected Android."""
    physical_install = getattr(page, "_gt6_test_clock_install", None)
    if physical_install:
        physical_install()
    else:
        page.clock.install()


def advance_test_clock(page, duration_ms: int) -> None:
    """Advance test timers without waiting for wall time on supported targets."""
    physical_advance = getattr(page, "_gt6_test_clock_advance", None)
    if physical_advance:
        physical_advance(duration_ms)
    else:
        page.clock.run_for(duration_ms)


def validate_missing_performance_confirmation(browser, name: str) -> dict[str, bool]:
    """Verifica cancelar y aceptar el registro explícito sin repeticiones ni carga."""
    context = browser.new_context(viewport={"width": 412, "height": 915}, is_mobile=True, has_touch=True)
    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    page = context.new_page()
    install_test_clock(page)
    page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
    page.wait_for_selector("article.card[data-exercise-index] .completeSetButton")
    if page.locator("#summaryToggle").get_attribute("aria-expanded") != "false" or not page.locator("#summaryBody").evaluate("element => element.hidden"):
        context.close()
        raise AssertionError(f"{name}: el resumen flotante debe iniciar compacto para no cubrir los controles")
    required_labels = [label.strip() for label in page.locator("article.card[data-exercise-index]").first.locator(".performanceRequired").all_text_contents()]
    if required_labels != ["Requerido", "Requerida"]:
        context.close()
        raise AssertionError(f"{name}: repeticiones y carga deben presentarse como requeridas; etiquetas={required_labels}")
    warmup = page.locator("#warmupAction")
    click_control(warmup)
    advance_test_clock(page, 15_000)
    click_control(warmup)
    click_control(warmup)
    card = page.locator("article.card[data-exercise-index]").first
    button = card.locator(".completeSetButton")
    select_valid_performance(card)
    click_control(button)  # inicia aproximación
    advance_test_clock(page, 20_000)
    click_control(button)  # registra aproximación y entra en descanso
    if getattr(page, "_gt6_physical_hold", None):
        dispatch_touch_hold(page, button, 5_150)
    else:
        advance_test_clock(page, 180_000)
        click_control(button)  # preparación de la primera serie efectiva
    advance_test_clock(page, 15_000)
    if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "strength":
        context.close()
        raise AssertionError(f"{name}: no se pudo iniciar la serie para probar el diálogo de omisión")
    click_control(card.locator(".performanceFieldTitleRow .performanceClear"))
    click_control(card.locator(".performanceLoadOutputRow .performanceClear"))
    click_control(button)
    dialog = page.locator("#performanceMissingDialog")
    if not dialog.is_visible() or "repeticiones" not in dialog.inner_text().lower() or "carga" not in dialog.inner_text().lower():
        context.close()
        raise AssertionError(f"{name}: no advirtió los dos datos omitidos en un diálogo accesible")
    click_control(dialog.locator("button[value='cancel']"))
    if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "strength" or card.locator(".exerciseProgress").inner_text().strip() != "0/" + str(card.locator(".seriesProgressSegment").count()):
        context.close()
        raise AssertionError(f"{name}: cancelar el diálogo alteró la serie")
    click_control(button)
    click_control(dialog.locator("button[value='continue']"))
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'rest'")
    if page.locator("#summaryToggle").get_attribute("aria-expanded") != "false" or not page.locator("#summaryBody").evaluate("element => element.hidden"):
        context.close()
        raise AssertionError(f"{name}: el resumen flotante se expandió automáticamente y cubrió el registro durante el descanso")
    progress_state = page.evaluate("""() => Object.keys(localStorage).map(key => { try { return JSON.parse(localStorage.getItem(key)); } catch (_) { return null; } }).find(value => value && value.__performance)?.__performance""")
    record = (progress_state or {}).get("1", {}).get("e1s1")
    if not record or record.get("reps") is not None or record.get("load") is not None:
        context.close()
        raise AssertionError(f"{name}: aceptar no guardó explícitamente los campos omitidos como nulos: {record}")
    context.close()
    return {"cancelKeepsSetActive": True, "acceptSavesNullRepsAndLoad": True}


def assert_background_timing_pauses(page, routine_name: str) -> dict:
    result = page.evaluate("""() => {
      const metrics = {cleared: 0, restarted: 0};
      const nativeSetInterval = window.setInterval.bind(window);
      const nativeClearInterval = window.clearInterval.bind(window);
      let hidden = false;
      Object.defineProperty(document, 'hidden', {configurable: true, get: () => hidden});
      window.clearInterval = id => { metrics.cleared += 1; return nativeClearInterval(id); };
      window.setInterval = (callback, delay, ...args) => {
        if (delay === 1000) metrics.restarted += 1;
        return nativeSetInterval(callback, delay, ...args);
      };
      hidden = true;
      document.dispatchEvent(new Event('visibilitychange'));
      const paused = metrics.cleared === 1;
      hidden = false;
      document.dispatchEvent(new Event('visibilitychange'));
      return {paused, resumed: metrics.restarted === 1, metrics};
    }""")
    if not result["paused"] or not result["resumed"]:
        raise AssertionError(f"{routine_name}: el cronómetro de segundo plano no se detiene y reanuda correctamente: {result}")
    return result


def assert_battery_motion_pauses(page, image, routine_name: str, media_name: str) -> dict:
    """Verify an animated asset swaps to its poster offscreen and resumes onscreen."""
    image.scroll_into_view_if_needed()
    page.wait_for_function(
        "image => image.dataset.batteryMotionSrc && image.getAttribute('src') === image.dataset.batteryMotionSrc && image.dataset.batteryPaused !== 'true'",
        arg=image.element_handle(),
    )
    animated_source = image.get_attribute("src")
    if not animated_source or not re.search(r"\.gif(?:$|[?#])", animated_source, re.I):
        raise AssertionError(f"{routine_name}: recurso animado {media_name} no usa un GIF cargado: {animated_source!r}")
    assert_animation_changes(page, image)
    page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
    page.wait_for_function("image => image.dataset.batteryPaused === 'true'", arg=image.element_handle())
    poster_source = image.evaluate("image => image.parentElement?.querySelector('.gifFallback,.warmupFallback')?.getAttribute('src') || image.dataset.staticSrc || image.getAttribute('data-static-src')")
    paused_source = image.get_attribute("src")
    if not poster_source or paused_source != poster_source:
        raise AssertionError(f"{routine_name}: {media_name} no cambió a su póster al salir de pantalla: actual={paused_source!r}, póster={poster_source!r}")
    image.scroll_into_view_if_needed()
    page.wait_for_function(
        "image => image.dataset.batteryPaused !== 'true' && image.getAttribute('src') === image.dataset.batteryMotionSrc",
        arg=image.element_handle(),
    )
    if image.get_attribute("src") != animated_source:
        raise AssertionError(f"{routine_name}: {media_name} no restauró el GIF al volver a pantalla")
    assert_animation_changes(page, image)
    return {"pausedOffscreen": True, "posterShown": True, "resumedOnscreen": True, "animatedSource": animated_source, "posterSource": poster_source}


def validate_day(browser, name: str, sex: str, variant: str) -> dict:
    context = browser.new_context(
        viewport={"width": 412, "height": 915},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
        reduced_motion="no-preference",
        # Este flujo ahora sale a la portada y la recarga como lo hace la PWA
        # real; bloquear el worker dejaba el splash esperando una versión
        # offline que el propio contexto de prueba impedía instalar.
        service_workers="allow",
    )
    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true');localStorage.setItem('gymratik-network-preference-v1','always')")
    page = context.new_page()
    if getattr(page, "_gt6_physical_tap", None):
        page.add_init_script("""(() => {
          const original = EventTarget.prototype.addEventListener;
          EventTarget.prototype.addEventListener = function(type, listener, options) {
            if (type !== 'click' || !this.matches?.('.completeSetButton') || typeof listener !== 'function')
              return original.call(this, type, listener, options);
            const button = this;
            const wrapped = function(event) {
              const sample = phase => {
                const key = Object.keys(localStorage).find(value => /^fitlovers-day\\d+-series-v1$/.test(value));
                const saved = key ? JSON.parse(localStorage.getItem(key) || '{}') : {};
                (window.__gt6SeriesClickTrace ||= []).push({phase, trusted:event.isTrusted, target:event.target?.tagName, time:Date.now(), activity:document.querySelector('#summaryActivityStatus')?.dataset.activity, button:button.textContent.trim(), selectedReps:button.closest('.exerciseTracker')?.querySelector('.performanceReps')?.dataset.selected, selectedLoad:button.closest('.exerciseTracker')?.querySelector('.performanceLoadValue')?.dataset.selected, timing:saved.__timing?.exercises?.[button.closest('.exerciseTracker')?.dataset.exercise]});
              };
              sample('before');
              let result;
              try { result = listener.call(this, event); }
              catch (error) { sample('sync-error:' + String(error)); throw error; }
              if (result && typeof result.then === 'function') result.then(() => sample('resolved'), error => sample('rejected:' + String(error)));
              else sample('returned');
              return result;
            };
            return original.call(this, type, wrapped, options);
          };
        })()""")
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="networkidle")
    page.bring_to_front()

    if page.locator("#installGate").count() and page.locator("#installGate").is_visible():
        raise AssertionError(f"{name}: el gate instalado no se aplicó al contexto E2E")
    background_timing = assert_background_timing_pauses(page, name)
    if sex:
        page.evaluate("sex => window.TrainingProgressStore.saveProfile({sex})", sex)
    else:
        empty_profile = page.evaluate("async () => await window.TrainingProgressStore.getProfile()")
        if empty_profile.get("sex"):
            raise AssertionError(f"{name}: el caso default ya tiene sexo persistido: {empty_profile}")
    page.evaluate("sex => window.TrainingProgressStore.saveProfile({displayName: 'Perfil E2E', sex})", sex)
    page.wait_for_function("expected => window.gymratikMascotVariant === expected", arg=variant)
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'start'")
    start_asset = assert_mascot(page, variant, "start")
    routine_id = name.split("_")[2]
    if SCREENSHOT_DIR:
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        capture_visual(page, f"day-{routine_id}-start-mobile.png")
    if page.locator("#summaryToggle").get_attribute("aria-expanded") == "true":
        click_control(page.locator("#summaryToggle"))
    if page.locator("#summaryBody").is_visible() or not page.locator(".summaryMascotWrap").is_visible():
        raise AssertionError(f"{name}: la mascota de inicio debe permanecer visible con el resumen plegado")
    assert_animation_changes(page, page.locator("#summaryActivityMascot"))

    images = assert_image_inventory(page, name)
    resource_quality = assert_visual_resource_quality(page, name)
    exercise_gif_locator = page.locator(".day3ExerciseGif:visible,.day4ExerciseGif:visible").first
    if exercise_gif_locator.count() == 0:
        exercise_gif_locator = page.locator('img[src*="/videos/"]:visible,img[data-battery-motion-src*="/videos/"]:visible').first
    if exercise_gif_locator.count() == 0:
        context.close()
        raise AssertionError(f"{name}: no se encontró una animación de ejercicio visible para validar")
    exercise_gif_locator.scroll_into_view_if_needed()
    assert_animation_changes(page, exercise_gif_locator)
    # Reactiva el visor en pantalla: fuera de ella el ahorro de batería oculta
    # el GIF y deja visible el póster estático.
    warmup_viewer = page.locator(".warmupSingleViewer").first
    warmup_viewer.scroll_into_view_if_needed()
    click_control(warmup_viewer.locator('.warmupMediaChoice[aria-pressed="true"]'))
    battery_gif = warmup_viewer.locator("img.warmupGif").first
    if battery_gif.count() == 0:
        context.close()
        raise AssertionError(f"{name}: no hay GIF visible para validar pausa/reanudación de ahorro de batería")
    battery_motion = {"warmup": assert_battery_motion_pauses(page, battery_gif, name, "calentamiento")}
    exercise_motion = page.locator("img.day3ExerciseGif:visible,img.day4ExerciseGif:visible").first
    if exercise_motion.count():
        battery_motion["exercise"] = assert_battery_motion_pauses(page, exercise_motion, name, "GIF de técnica")
    cards = page.locator("article.card[data-exercise-index]")
    exercise_count = cards.count()
    reps_inputs = page.locator("input.performanceReps")
    load_inputs = page.locator("input.performanceLoad")
    if exercise_count != reps_inputs.count() or exercise_count != load_inputs.count():
        raise AssertionError(f"{name}: selectores de rendimiento incompletos: exercises={exercise_count}, reps={reps_inputs.count()}, loads={load_inputs.count()}")

    # Physical audits retain one accepted screenshot per complete exercise card.
    if SCREENSHOT_DIR:
        for index in range(exercise_count):
            card = cards.nth(index)
            card.scroll_into_view_if_needed()
            page.wait_for_timeout(100)
            card.screenshot(path=str(SCREENSHOT_DIR / f"day-{routine_id}-exercise-{index + 1:02}.png"))

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
        click_control(rep_clear)
        if reps.get_attribute("data-selected") != "false":
            raise AssertionError(f"{name}: no se pudo limpiar repeticiones del ejercicio {index + 1}")
        load.focus()
        load.press("ArrowRight")
        if not card.locator(".performanceLoadValue").inner_text().strip():
            raise AssertionError(f"{name}: el deslizador de carga no actualiza su lectura en el ejercicio {index + 1}")
        load_clear = card.locator(".performanceLoadOutputRow .performanceClear")
        click_control(load_clear)
        if load.get_attribute("aria-valuenow") not in (None, "0"):
            raise AssertionError(f"{name}: no se pudo limpiar la carga del ejercicio {index + 1}")
        machine_pending = card.locator(".machinePendingToggle")
        if machine_pending.count() != 1:
            raise AssertionError(f"{name}: el ejercicio {index + 1} no tiene exactamente un control de máquina ocupada")
        machine_pending.scroll_into_view_if_needed()
        if machine_pending.get_attribute("aria-pressed") != "false":
            raise AssertionError(f"{name}: el estado inicial de máquina ocupada es incorrecto en el ejercicio {index + 1}")
        click_control(machine_pending)
        if machine_pending.get_attribute("aria-pressed") != "true":
            raise AssertionError(f"{name}: no se pudo marcar la máquina ocupada en el ejercicio {index + 1}")
        click_control(machine_pending)
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
    click_control(first.locator(".performanceLoadValue"))
    direct = first.locator("input.performanceLoadDirect")
    direct.fill("17.5")
    direct.press("Enter")
    if "17.5" not in first.locator(".performanceLoadValue").inner_text():
        raise AssertionError(f"{name}: no se confirmó la edición decimal directa")
    first.locator("select.performanceLoadUnit").select_option("lb")
    if "lb" not in first.locator(".performanceLoadValue").inner_text():
        raise AssertionError(f"{name}: el selector kg/lb no actualizó la carga")
    unit_selector = first.locator("select.performanceLoadUnit")
    unit_selector.evaluate("element => element.scrollIntoView({block:'center',behavior:'instant'})")
    page.wait_for_timeout(80)
    unit_selector.focus()
    before_enter = page.evaluate("({scrollY, active: document.activeElement?.className})")
    unit_selector.press("Enter")
    after_enter = page.evaluate("({scrollY, active: document.activeElement?.className})")
    expected_progress = f"0/{first.locator('.seriesProgressSegment').count()}"
    if unit_selector.input_value() != "lb" or first.locator(".exerciseProgress").inner_text().strip() != expected_progress:
        raise AssertionError(f"{name}: Enter en kg/lb alteró la unidad o registró una serie")
    if abs(after_enter["scrollY"] - before_enter["scrollY"]) > 120:
        raise AssertionError(f"{name}: Enter en el selector kg/lb desplazó la página a otro ejercicio: {before_enter} -> {after_enter}")

    # Barra de progreso flotante: una sola tarjeta y una fila por ejercicio.
    click_control(page.locator("#summaryToggle"))
    if page.locator("#floatingSessionSummary").count() != 1 or page.locator(".summaryExercise").count() != exercise_count:
        raise AssertionError(f"{name}: resumen flotante duplicado o incompleto")
    if not page.locator(".sessionSummaryList").evaluate("element => element.scrollHeight >= element.clientHeight"):
        raise AssertionError(f"{name}: lista flotante no conserva desplazamiento táctil")
    summary_list = page.locator(".sessionSummaryList")
    summary_geometry = summary_list.evaluate("element => { const bounds=element.getBoundingClientRect(); const rows=[...element.querySelectorAll('.summaryExercise')].map(row=>{const rect=row.getBoundingClientRect();return {top:rect.top,bottom:rect.bottom}});return {viewport:[innerWidth,innerHeight],clientHeight:element.clientHeight,scrollHeight:element.scrollHeight,fullyVisibleRows:rows.filter(row=>row.top>=bounds.top-1&&row.bottom<=bounds.bottom+1).length,rows}; }")
    if summary_geometry["fullyVisibleRows"] != 3:
        raise AssertionError(f"{name}: el resumen móvil debe mostrar exactamente tres ejercicios completos (anterior/actual/siguiente): {summary_geometry}")
    target_summary_row = page.locator(".summaryExercise").last
    target_index = int(target_summary_row.get_attribute("data-exercise")) - 1
    click_control(target_summary_row)
    page.wait_for_function("index => window.gymratikFocusedExerciseIndex === index", arg=target_index, timeout=5_000)
    page.wait_for_function("index => document.querySelectorAll('.summaryExercise')[index]?.classList.contains('isCurrent')", arg=target_index, timeout=5_000)
    target_card = page.locator("article.card[data-exercise-index]").nth(target_index)
    page.wait_for_function("index => { const card=document.querySelectorAll('article.card[data-exercise-index]')[index]; if(!card)return false; const rect=card.getBoundingClientRect(); return rect.top>=-1&&rect.top<innerHeight*.7; }", arg=target_index, timeout=5_000)
    if "isCurrent" not in target_summary_row.get_attribute("class"):
        raise AssertionError(f"{name}: tocar una fila no mantiene enfocado ese ejercicio en la barra")

    # Calentamiento completo, con su mínimo de preparación de 15 s.
    warmup = page.locator("#warmupAction")
    click_control(warmup)
    page.wait_for_timeout(15_000)
    if warmup.get_attribute("data-phase") != "cardio":
        raise AssertionError(f"{name}: el calentamiento no terminó la preparación de 15 s")
    exercise_gif = assert_mascot(page, variant, "cardio")
    assert_animation_changes(page, page.locator("#summaryActivityMascot"))
    click_control(warmup)
    if warmup.get_attribute("data-phase") != "mobility":
        raise AssertionError(f"{name}: el botón no avanzó de cardio a movilidad")
    assert_mascot(page, variant, "mobility")
    assert_animation_changes(page, page.locator("#summaryActivityMascot"))
    click_control(warmup)
    if warmup.get_attribute("data-phase") != "done":
        raise AssertionError(f"{name}: el botón no finalizó el calentamiento")
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'ready'", timeout=5_000)
    assert_mascot(page, variant, "ready")

    # Registra la aproximación por separado y comprueba que su estado sobrevive a una recarga.
    button = first.locator(".completeSetButton")
    select_valid_performance(first)
    click_control(button)
    if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "approximation":
        raise AssertionError(f"{name}: el inicio de aproximación no refleja actividad en la portada flotante")
    page.wait_for_timeout(5_000)
    page.reload(wait_until="networkidle")
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'approximation'")
    page.wait_for_timeout(15_000)
    select_valid_performance(first)
    click_control(button)
    if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "rest":
        raise AssertionError(f"{name}: completar aproximación no inició descanso")
    if first.locator(".exerciseProgress").inner_text().strip() != f"0/{first.locator('.seriesProgressSegment').count()}":
        raise AssertionError(f"{name}: aproximación sumada incorrectamente a series efectivas")
    # Mantener 5 s omite solo el descanso; siguen siendo obligatorios 15 s de preparación.
    dispatch_touch_hold(page, button, 5_150, virtual_clock=False)
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'preparing'")
    page.wait_for_timeout(15_000)
    activity = page.locator("#summaryActivityStatus")
    if activity.get_attribute("data-activity") != "strength":
        raise AssertionError(f"{name}: la serie efectiva no aparece activa tras la preparación")
    if "isActive" not in page.locator("#summaryToggle").get_attribute("class"):
        raise AssertionError(f"{name}: se perdió el indicador de actividad del botón flotante tras recargar")
    if page.locator("#summaryToggle").get_attribute("aria-expanded") != "true":
        click_control(page.locator("#summaryToggle"))
    strength_asset = assert_mascot(page, variant, "strength")
    assert_animation_changes(page, page.locator("#summaryActivityMascot"))
    click_control(page.locator("#summaryToggle"))
    if page.locator("#summaryBody").is_visible() or not page.locator(".summaryMascotWrap").is_visible():
        raise AssertionError(f"{name}: la mascota activa desaparece al plegar el resumen")
    if page.locator("#summaryActivityMascot").evaluate("element => getComputedStyle(element).animationName") != "mascotStrengthEffort":
        raise AssertionError(f"{name}: la mascota dejó de animarse cuando el resumen está plegado")
    click_control(page.locator("#summaryToggle"))
    active_feedback = assert_activity_feedback(page, "strength")
    stable_fill = assert_series_segment_fill_stable(page, name)
    if "isActive" not in page.locator("#summaryToggle").get_attribute("class"):
        raise AssertionError(f"{name}: cabecera flotante no refleja actividad verde")
    capture_visual(page, f"day-{routine_id}-active-mobile.png")
    select_valid_performance(first)
    click_control(button)
    try:
        activity.wait_for_function("element => element.dataset.activity === 'rest'", timeout=2_000)
    except Exception:
        pass
    if activity.get_attribute("data-activity") != "rest":
        state = button.evaluate("element => { const key=Object.keys(localStorage).find(value=>/^fitlovers-day\\d+-series-v1$/.test(value)); const saved=key?JSON.parse(localStorage.getItem(key)||'{}'):{}; return {disabled:element.disabled,text:element.textContent,className:element.className,ariaLabel:element.getAttribute('aria-label'),reps:element.closest('.exerciseTracker')?.querySelector('.performanceReps')?.getAttribute('data-selected'),repsValue:element.closest('.exerciseTracker')?.querySelector('.performanceReps')?.value,load:element.closest('.exerciseTracker')?.querySelector('.performanceLoadValue')?.getAttribute('data-selected'),loadValue:element.closest('.exerciseTracker')?.querySelector('.performanceLoadOutput')?.textContent,dialogOpen:document.querySelector('#performanceMissingDialog')?.open,dialogText:document.querySelector('#performanceMissingDialog')?.innerText,timing:saved.__timing?.exercises?.['1'],clickReceived:window.__gt6TouchClickReceived}; }")
        click_trace = page.evaluate("() => window.__gt6SeriesClickTrace || []")
        raise AssertionError(f"{name}: completar serie no inició el descanso; actividad={activity.get_attribute('data-activity')!r}, botón/estado={state}, clickTrace={click_trace}, errores={errors}")
    set_marker = first.locator('.exerciseTimerChip[data-kind="set"]').first.inner_text().strip()
    if not re.search(r"S1 · \d+r · [\d.]+(?:kg|lb)", set_marker, re.IGNORECASE):
        raise AssertionError(f"{name}: el marcador de series no muestra repeticiones y carga junto al tiempo: {set_marker!r}")
    toast_feedback = assert_approval_toast(page, variant)
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
        click_control(page.locator("#summaryToggle"))
    expected_rest_asset = f"states-v1/{variant}-rest.png" if variant in ("male", "female") else "neutral-rest-still.webp"
    if not page.locator("#summaryActivityMascot").get_attribute("src").endswith(expected_rest_asset):
        raise AssertionError(f"{name}: la recarga perdió la mascota de descanso")
    restored_progress = page.locator(".summaryExercise").first.evaluate("element => Number(element.style.getPropertyValue('--summary-progress'))")
    if restored_progress != progress:
        raise AssertionError(f"{name}: la recarga alteró el progreso de la serie ({progress} -> {restored_progress})")

    # Salir explícitamente a la portada no debe perder perfil, series, carga,
    # repeticiones ni el estado de descanso de la sesión en curso.
    page.locator(".routine-home-link").click()
    page.wait_for_url("**/index.html", timeout=10_000)
    page.wait_for_function(
        "!document.documentElement.classList.contains('gymratik-loading') && getComputedStyle(document.querySelector('#appSplash')).visibility === 'hidden'",
        timeout=60_000,
    )
    page.wait_for_function("document.querySelector('#profileDisplayName')?.value === 'Perfil E2E'", timeout=10_000)
    if page.locator("#profileEditor").evaluate("element => element.open"):
        raise AssertionError(f"{name}: el formulario se volvió a abrir pese a que ya existe un perfil guardado")
    routine_id = f"day{routine_id}"
    page.wait_for_function("""async routineId => {
      const [dashboard, history] = await Promise.all([
        window.TrainingProgressStore.getDashboard(), window.TrainingProgressStore.getHistory(50)
      ]);
      const routine = dashboard.routines.find(item => item.routineId === routineId);
      return routine?.doneSeries >= 1 && history.some(item => item.routineId === routineId
        && item.status === 'active' && item.completedSeries >= 1);
    }""", arg=routine_id, timeout=10_000)
    home_snapshot = page.evaluate("""async routineId => {
      const [profile, dashboard, history] = await Promise.all([
        window.TrainingProgressStore.getProfile(), window.TrainingProgressStore.getDashboard(),
        window.TrainingProgressStore.getHistory(50)
      ]);
      return {
        profile: {displayName: profile.displayName, sex: profile.sex},
        profileFormOpen: document.querySelector('#profileEditor')?.open === true,
        routine: dashboard.routines.find(item => item.routineId === routineId),
        activeSession: history.find(item => item.routineId === routineId && item.status === 'active')
      };
    }""", routine_id)
    page.reload(wait_until="networkidle")
    page.wait_for_function(
        "!document.documentElement.classList.contains('gymratik-loading') && getComputedStyle(document.querySelector('#appSplash')).visibility === 'hidden'",
        timeout=60_000,
    )
    page.wait_for_function("document.querySelector('#profileDisplayName')?.value === 'Perfil E2E'", timeout=10_000)
    if page.locator("#profileSex").input_value() != sex:
        raise AssertionError(f"{name}: recargar la portada alteró el sexo/perfil almacenado")
    day_card = page.locator(f'a.routine-card[href$="{name}"]')
    if day_card.count() != 1:
        raise AssertionError(f"{name}: la portada ya no permite reabrir la misma rutina")
    day_card.click()
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'rest'", timeout=15_000)
    resumed_card = page.locator("article.card[data-exercise-index]").first
    resumed_progress = resumed_card.locator(".exerciseProgress").inner_text().strip()
    resumed_marker = resumed_card.locator('.exerciseTimerChip[data-kind="set"]').first.inner_text().strip()
    if not re.fullmatch(r"1/\d+", resumed_progress):
        raise AssertionError(f"{name}: volver desde portada perdió el avance de la serie: {resumed_progress!r}")
    if not re.search(r"S1 · \d+r · [\d.]+(?:kg|lb)", resumed_marker, re.IGNORECASE):
        raise AssertionError(f"{name}: volver desde portada perdió repeticiones/carga/tiempo: {resumed_marker!r}")
    page.reload(wait_until="networkidle")
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'rest'", timeout=15_000)
    if not re.fullmatch(r"1/\d+", page.locator("article.card[data-exercise-index]").first.locator(".exerciseProgress").inner_text().strip()):
        raise AssertionError(f"{name}: recargar la sesión reabierta perdió el progreso actual")
    persistence_roundtrip = {
        "profileAndForm": "perfil preservado; formulario no reaparece",
        "homeReload": "portada recargada con perfil y progreso",
        "session": "portada → misma rutina → recarga; serie, carga, repeticiones y descanso preservados",
        "homeSnapshot": home_snapshot,
    }

    # La pose de descanso permanece; reduced-motion detiene solo la animación.
    page.emulate_media(reduced_motion="reduce")
    page.wait_for_function("getComputedStyle(document.querySelector('#summaryActivityMascot')).animationName === 'none'")
    still = assert_mascot(page, variant, "rest", reduced=True)
    if page.locator("#summaryActivityStatus .summaryActivityIndicator").evaluate("element => getComputedStyle(element).animationName") != "none":
        raise AssertionError(f"{name}: el pulso no respeta prefers-reduced-motion")

    # Gestos largos reales de puntero táctil: cancelar temprano y luego omitir el descanso.
    page.emulate_media(reduced_motion="no-preference")
    rest_button = first.locator(".completeSetButton")
    dispatch_touch_hold(page, rest_button, 4_000, virtual_clock=False)
    if activity.get_attribute("data-activity") != "rest" or "is-holding" in (rest_button.get_attribute("class") or ""):
        raise AssertionError(f"{name}: soltar antes de 5 s no canceló el gesto de descanso")
    # Margen de 150 ms sobre el umbral: el motor de reloj del navegador
    # puede entregar pointerup antes que el timeout al coincidir ambos en 5 s.
    dispatch_touch_hold(page, rest_button, 5_150, virtual_clock=False)
    if activity.get_attribute("data-activity") != "preparing":
        raise AssertionError(f"{name}: mantener 5 s no omitió el descanso e inició preparación")
    page.wait_for_timeout(15_000)
    if activity.get_attribute("data-activity") != "strength":
        raise AssertionError(f"{name}: la preparación de 15 s no inició la serie después del descanso omitido")
    assert_activity_feedback(page, "strength")

    if errors:
        raise AssertionError(f"{name}: errores JavaScript: {errors}")

    result = {
        "routine": name,
        "profileSex": sex or "empty",
        "variant": variant,
        "exercises": exercise_count,
        "images": images,
        "resourceQuality": resource_quality,
        "cardioMascotAsset": exercise_gif,
        "strengthMascotAsset": strength_asset,
        "restGif": rest_gif,
        "batteryGifPauseResume": battery_motion,
        "backgroundTimer": background_timing,
        "reducedMotionAsset": still,
        "startMascotAsset": start_asset,
        "activityVisuals": {"active": active_feedback, "rest": rest_feedback},
        "approvalToast": toast_feedback,
        "homeReturnPersistence": persistence_roundtrip,
        "stableActiveFillTransform": stable_fill,
        "skipGestures": {"rest": "cancelled <5 s; continued at 5 s", "exercise": "cancelled <10 s; skip+undo at 10 s"},
        "progress": progress,
    }
    context.close()
    return result


def validate_approximation_moves_to_first_available(browser, name: str, sex: str) -> None:
    """La aproximación pertenece al primer ejercicio libre, no al índice 1 fijo."""
    context = browser.new_context(
        viewport={"width": 412, "height": 915},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
    )
    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    page = context.new_page()
    try:
        page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
        page.wait_for_function("() => [...document.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)")
        cards = page.locator("article.card[data-exercise-index]")
        if cards.count() < 2:
            raise AssertionError(f"{name}: se requieren al menos dos ejercicios para probar el cambio de aproximación")
        install_test_clock(page)
        if sex:
            page.evaluate("sex => window.TrainingProgressStore.saveProfile({sex})", sex)

        first, second = cards.nth(0), cards.nth(1)
        warmup = page.locator("#warmupAction")
        click_control(warmup)
        advance_test_clock(page, 15_000)
        click_control(warmup)
        click_control(warmup)
        if warmup.get_attribute("data-phase") != "done":
            raise AssertionError(f"{name}: no se completó la preparación general de la regresión")
        advance_test_clock(page, 2_600)

        pending = first.locator(".machinePendingToggle")
        if pending.get_attribute("aria-pressed") != "false":
            raise AssertionError(f"{name}: el primer ejercicio no inicia disponible")
        click_control(pending)
        first_marker = first.locator(".warmupSet")
        second_marker = second.locator(".warmupSet")
        if first_marker.count() != 0 or second_marker.count() != 1 or second_marker.get_attribute("data-key") != "w2":
            raise AssertionError(
                f"{name}: al ocupar el ejercicio 1, la aproximación no se trasladó exclusivamente al 2 "
                f"(marcadores 1={first_marker.count()}, 2={second_marker.count()})"
            )

        first_hint = first.locator(".exerciseWarmupHint")
        second_hint = second.locator(".exerciseWarmupHint")
        if first_hint.count() or not second_hint.is_visible():
            raise AssertionError(f"{name}: la indicación de aproximación no quedó únicamente en el primer ejercicio disponible")
        if "aproximación" not in second.locator(".completeSetButton").inner_text().lower():
            raise AssertionError(f"{name}: el botón del primer ejercicio disponible no ofrece iniciar la aproximación")
    finally:
        context.close()


def validate_primary_set_buttons(browser, name: str, sex: str, exercise_limit: int | None = None) -> dict[str, int]:
    """Exercise each card's dynamic and skip controls in a clean session."""
    context_settings = {
        "viewport": {"width": 412, "height": 915},
        "device_scale_factor": 2,
        "is_mobile": True,
        "has_touch": True,
    }
    confirmation = validate_missing_performance_confirmation(browser, name)
    validate_approximation_moves_to_first_available(browser, name, sex)
    checked = 0
    skipped = 0
    initial_context = browser.new_context(**context_settings)
    initial_context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    initial_page = initial_context.new_page()
    initial_page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
    initial_page.wait_for_function("() => [...document.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)")
    initial_page.wait_for_selector("article.card[data-exercise-index] .completeSetButton")
    exercise_count = initial_page.locator("article.card[data-exercise-index]").count()
    context = initial_context
    page = initial_page
    install_test_clock(page)
    exercised_count = exercise_count if exercise_limit is None else max(1, min(exercise_count, exercise_limit))
    for index in range(exercised_count):
        page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
        page.wait_for_function("() => [...document.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)")
        page.wait_for_selector("article.card[data-exercise-index] .completeSetButton")
        if sex:
            page.evaluate("sex => window.TrainingProgressStore.saveProfile({sex})", sex)
        mascot_variant = sex if sex in {"male", "female"} else "neutral"
        assert_mascot(page, mascot_variant, "start")

        warmup = page.locator("#warmupAction")
        click_control(warmup)
        assert_mascot(page, mascot_variant, "preparing")
        advance_test_clock(page, 15_000)
        if warmup.get_attribute("data-phase") != "cardio":
            context.close()
            raise AssertionError(f"{name}: no se pudo completar el calentamiento antes del botón del ejercicio {index + 1}")
        assert_mascot(page, mascot_variant, "cardio")
        click_control(warmup)
        assert_mascot(page, mascot_variant, "mobility")
        click_control(warmup)
        if warmup.get_attribute("data-phase") != "done":
            context.close()
            raise AssertionError(f"{name}: el calentamiento no finalizó antes del ejercicio {index + 1}")
        # The synthetic clock does not advance while the three warm-up controls
        # are tapped; let the short "session just started" banner expire.
        advance_test_clock(page, 2_600)
        assert_mascot(page, mascot_variant, "ready")

        card = page.locator("article.card[data-exercise-index]").nth(index)
        button = card.locator(".completeSetButton")
        segments = card.locator(".seriesProgressSegment").count()
        button.scroll_into_view_if_needed()
        select_valid_performance(card)
        if card.locator(".warmupSet").count():
            click_control(button)
            warmup_progress = card.locator(".approximationProgress")
            if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "approximation" or not warmup_progress.is_visible():
                context.close()
                raise AssertionError(f"{name}: la aproximación no inició actividad ni mostró su progreso separado en el ejercicio {index + 1}")
            assert_mascot(page, mascot_variant, "approximation")
            if warmup_progress.get_attribute("aria-valuenow") != "0" or card.locator(".exerciseProgress").inner_text().strip() != f"0/{segments}":
                context.close()
                raise AssertionError(f"{name}: la aproximación se mezcló con el contador de series efectivas en el ejercicio {index + 1}")
            hint = card.locator(".exerciseWarmupHint")
            if not hint.is_visible() or "carga ligera" not in hint.inner_text().lower():
                context.close()
                raise AssertionError(f"{name}: faltó el consejo visual de aproximación cuando correspondía en el ejercicio {index + 1}")
            advance_test_clock(page, 20_000)
            click_control(button)
            warmup_record = page.evaluate(f"""() => Object.values(localStorage).map(raw => {{ try {{ return JSON.parse(raw); }} catch (_) {{ return null; }} }}).find(value => value?.__warmupPerformance)?.__warmupPerformance?.['{index + 1}']""")
            if not warmup_record or not warmup_record.get("durationMs") or warmup_progress.get_attribute("aria-valuenow") != "1":
                context.close()
                raise AssertionError(f"{name}: no guardó por separado repeticiones/carga/duración de la aproximación: {warmup_record}")
            if card.locator(".exerciseProgress").inner_text().strip() != f"0/{segments}" or hint.is_visible():
                context.close()
                raise AssertionError(f"{name}: la aproximación cambió el volumen efectivo o dejó su ayuda visible fuera de turno")
            if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "rest":
                context.close()
                raise AssertionError(f"{name}: al completar la aproximación no comenzó el descanso antes de las series efectivas")
            assert_mascot(page, mascot_variant, "rest")
            if getattr(page, "_gt6_physical_hold", None):
                dispatch_touch_hold(page, button, 5_150)
            else:
                advance_test_clock(page, 600_000)
                click_control(button)
            assert_mascot(page, mascot_variant, "preparing")
        else:
            if card.locator(".exerciseWarmupHint:visible,.approximationProgress:visible").count():
                context.close()
                raise AssertionError(f"{name}: mostró contenido de aproximación donde no corresponde, ejercicio {index + 1}")
            click_control(button)
            assert_mascot(page, mascot_variant, "preparing")
        if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "preparing":
            status = page.evaluate("() => ({activity:document.querySelector('#summaryActivityStatus')?.dataset.activity, button:document.querySelector('article.card[data-exercise-index] .completeSetButton')?.outerHTML, rest:document.querySelector('article.card[data-exercise-index] .metric.rest .timeCue')?.textContent, timing:Object.values(localStorage).map(raw=>{try{return JSON.parse(raw)}catch{return null}}).find(value=>value?.__timing)?.__timing})")
            raise AssertionError(f"{name}: el botón principal del ejercicio {index + 1} no inició preparación: {status}")
        advance_test_clock(page, 15_000)
        if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "strength":
            context.close()
            raise AssertionError(f"{name}: el botón principal del ejercicio {index + 1} no pasó de preparación a actividad")
        assert_mascot(page, mascot_variant, "strength")
        active_set_chip = card.locator('.exerciseTimerChip[data-kind="active-set"]')
        if active_set_chip.count() != 1 or not active_set_chip.is_visible() or "en curso" not in active_set_chip.get_attribute("aria-label").lower():
            context.close()
            raise AssertionError(f"{name}: el cronómetro de la serie no tiene una ficha visible de actividad")
        if active_set_chip.evaluate("element => getComputedStyle(element, '::before').animationName") != "timerActivityPulse":
            context.close()
            raise AssertionError(f"{name}: la ficha del cronómetro no anima durante la serie activa")
        select_valid_performance(card)
        click_control(button)
        if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "rest":
            context.close()
            raise AssertionError(f"{name}: el botón principal del ejercicio {index + 1} no completó la serie ni inició descanso")
        assert_mascot(page, mascot_variant, "rest")
        active_rest_chip = card.locator('.exerciseTimerChip[data-kind="active-rest"]')
        if active_rest_chip.count() != 1 or not active_rest_chip.is_visible():
            context.close()
            raise AssertionError(f"{name}: el cronómetro no cambió a ficha de descanso después de la serie")
        if active_rest_chip.evaluate("element => getComputedStyle(element, '::before').animationName") != "timerActivityPulse":
            context.close()
            raise AssertionError(f"{name}: la ficha del cronómetro no anima durante el descanso")
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
        click_control(undo)
        if "exerciseSkipped" in (tracker.get_attribute("class") or "") or card.locator(".exerciseProgress").inner_text().strip() != f"0/{exercise_series_total}":
            context.close()
            raise AssertionError(f"{name}: deshacer omisión no restauró el progreso del ejercicio {index + 1}")
        checked += 1
        skipped += 1
        page.evaluate("async () => { await window.TrainingProgressStore.clearAll(); Object.keys(localStorage).filter(key => /series-v1$/.test(key)).forEach(key => localStorage.removeItem(key)); }")
    # Reutiliza la misma pestaña/contexto en Android: Chromium puede cerrar el
    # target remoto al descartar y recrear contextos repetidamente.
    # El descanso también debe comenzar tras la última serie de un ejercicio
    # cuando quedan ejercicios en la rutina.
    install_test_clock(page)
    page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
    page.wait_for_selector("article.card[data-exercise-index] .completeSetButton")
    warmup = page.locator("#warmupAction")
    click_control(warmup)
    advance_test_clock(page, 15_000)
    click_control(warmup)
    click_control(warmup)
    card = page.locator("article.card[data-exercise-index]").first
    button = card.locator(".completeSetButton")
    select_valid_performance(card)
    click_control(button)  # inicia aproximación
    advance_test_clock(page, 20_000)
    click_control(button)  # completa aproximación, con contador aparte
    if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "rest":
        context.close()
        raise AssertionError(f"{name}: la aproximación no inició descanso antes del ciclo de series")
    dispatch_touch_hold(page, button, 5_150)
    if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "preparing":
        context.close()
        raise AssertionError(f"{name}: omitir el descanso de aproximación no inició preparación")
    for series_index in range(card.locator(".seriesProgressSegment").count()):
        activity_state = page.locator("#summaryActivityStatus").get_attribute("data-activity")
        if activity_state not in ("preparing", "strength"):
            click_control(button)
            activity_state = page.locator("#summaryActivityStatus").get_attribute("data-activity")
        if activity_state == "preparing":
            advance_test_clock(page, 15_000)
        if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "strength":
            diagnostic = page.evaluate("""() => ({activity: document.querySelector('#summaryActivityStatus')?.dataset.activity,
              label: document.querySelector('#summaryActivityStatus')?.innerText,
              button: document.querySelector('article.card[data-exercise-index] .completeSetButton')?.getAttribute('aria-label'),
              timingKeys: Object.keys(localStorage).filter(key => key.includes('series-v1'))})""")
            context.close()
            raise AssertionError(f"{name}: preparación incorrecta antes de serie {series_index + 1}: {diagnostic}")
        select_valid_performance(card)
        click_control(button)
        expected = "rest" if series_index < card.locator(".seriesProgressSegment").count() - 1 or page.locator("article.card").count() > 1 else "complete"
        actual = page.locator("#summaryActivityStatus").get_attribute("data-activity")
        if actual != expected:
            context.close()
            raise AssertionError(f"{name}: resultado tras serie {series_index + 1}: esperado={expected}, actual={actual}")
        if series_index < card.locator(".seriesProgressSegment").count() - 1:
            # Mantener >5 s evita una carrera del simulador justo en el límite.
            dispatch_touch_hold(page, button, 5_150)
            if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "preparing":
                diagnostic = page.evaluate("""() => ({
                  activity:document.querySelector('#summaryActivityStatus')?.dataset.activity || '',
                  label:document.querySelector('#summaryActivityStatus')?.innerText || '',
                  button:document.querySelector('article.card[data-exercise-index] .completeSetButton')?.getAttribute('aria-label') || '',
                  timing:Object.entries(localStorage).filter(([key]) => /timing|series-v1/i.test(key)).map(([key,value]) => ({key,value}))
                })""")
                context.close()
                raise AssertionError(f"{name}: omitir el descanso debe iniciar preparación, no una serie inmediata: {diagnostic}")
            advance_test_clock(page, 15_000)
            if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "strength":
                diagnostic = page.evaluate("""() => ({
                  activity:document.querySelector('#summaryActivityStatus')?.dataset.activity || '',
                  label:document.querySelector('#summaryActivityStatus')?.innerText || '',
                  button:document.querySelector('article.card[data-exercise-index] .completeSetButton')?.getAttribute('aria-label') || '',
                  timing:Object.entries(localStorage).filter(([key]) => /timing|series-v1/i.test(key)).map(([key,value]) => ({key,value}))
                })""")
                context.close()
                raise AssertionError(f"{name}: completar preparación de 15 s tras omitir descanso falló después de serie {series_index + 1}: {diagnostic}")
    if page.locator("#summaryActivityStatus").get_attribute("data-activity") == "rest" and not card.locator(".completeSetButton").get_attribute("aria-label").startswith("Descanso"):
        context.close()
        raise AssertionError(f"{name}: el botón no indica descanso al terminar la última serie del ejercicio")
    context.close()
    return {"primarySetButtonsTested": checked, "exerciseSkipButtonsTested": skipped, "exerciseCompletionRestTested": True, **confirmation}


def validate_completed_session_celebration(browser, name: str, sex: str, variant: str) -> dict[str, str | bool]:
    """Rehidrata una sesión completada aislada y comprueba su celebración persistente."""
    context = browser.new_context(
        viewport={"width": 412, "height": 915}, device_scale_factor=2,
        is_mobile=True, has_touch=True, reduced_motion="no-preference", service_workers="block",
    )
    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    page = context.new_page()
    install_test_clock(page)
    page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="networkidle")
    if sex:
        page.evaluate("sex => window.TrainingProgressStore.saveProfile({sex})", sex)
    counter_script = page.locator('script[data-enhancement="series-counter-v6"]').text_content() or ""
    match = re.search(r"const storageKey = '([^']+)'", counter_script)
    if not match:
        context.close()
        raise AssertionError(f"{name}: no se pudo leer la clave aislada del progreso para validar la celebración")
    page.evaluate("""key => {
      const state = {};
      document.querySelectorAll('.exerciseTracker').forEach(tracker => {
        (tracker.dataset.seriesKeys || '').trim().split(/\\s+/).filter(Boolean).forEach(seriesKey => { state[seriesKey] = true; });
      });
      const now = Date.now();
      state.__timing = { sessionStartedAt: now - 60000, sessionEndedAt: now, exercises: {} };
      localStorage.setItem(key, JSON.stringify(state));
    }""", match.group(1))
    page.reload(wait_until="networkidle")
    page.wait_for_function("document.querySelector('#summaryActivityStatus')?.dataset.activity === 'complete'")
    page.wait_for_function("expected => window.gymratikMascotVariant === expected", arg=variant)
    assert_mascot(page, variant, "celebration")
    if page.locator(".exerciseTimerChip[data-kind^='active-']").count() != 0:
        context.close()
        raise AssertionError(f"{name}: quedó animado un cronómetro de serie/descanso tras completar la rutina")
    effects = page.locator(".summaryMascotWrap").evaluate("element => ({before: getComputedStyle(element, '::before').content, after: getComputedStyle(element, '::after').content, motion: getComputedStyle(element.querySelector('#summaryActivityMascot')).animationName, label: document.querySelector('#summaryActivityLabel')?.textContent})")
    if effects["motion"] != "mascotApprovalCelebrate" or effects["before"] in ("none", "normal") or effects["after"] in ("none", "normal") or effects["label"] != "Rutina completada":
        context.close()
        raise AssertionError(f"{name}: no se mostró la celebración completa: {effects}")
    if not page.locator("#summaryActivityMascot").is_visible():
        context.close()
        raise AssertionError(f"{name}: la mascota de celebración desapareció del resumen")
    assert_animation_changes(page, page.locator("#summaryActivityMascot"))
    page.evaluate("() => window.scrollTo({top:0,behavior:'instant'})")
    page.wait_for_timeout(250)
    capture_visual(page, f"day-{name.split('_')[2]}-celebration-mobile.png")
    context.close()
    return {"completedSessionCelebration": True, "mascotAnimation": effects["motion"]}


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
    offline_cancelled_requests = []
    offline_bad_responses = []
    origin = f"http://127.0.0.1:{PORT}/"
    page.on("pageerror", lambda error: offline_page_errors.append(str(error)))

    def record_failed_request(request) -> None:
        if request.url.startswith(origin):
            failure = request.failure or "fallo sin detalle"
            record = {"url": request.url, "failure": failure}
            if "ERR_ABORTED" in failure:
                offline_cancelled_requests.append(record)
            else:
                offline_failed_requests.append(record)

    def record_bad_response(response) -> None:
        if response.status >= 400 and response.url.startswith(origin):
            offline_bad_responses.append({"url": response.url, "status": response.status})

    page.on("requestfailed", record_failed_request)
    page.on("response", record_bad_response)
    expected_cache_name = service_worker_cache_name((ROOT / "sw.js").read_text(encoding="utf-8"))
    page.goto(f"http://127.0.0.1:{PORT}/", wait_until="domcontentloaded")
    page.wait_for_function(
        "async cacheName => { const cache = await caches.open(cacheName); "
        "return Boolean(await cache.match(new URL('./__gymratik_complete__', location.origin + '/').href)); }",
        arg=expected_cache_name,
        timeout=120_000,
    )
    page.wait_for_function("navigator.serviceWorker.controller !== null", timeout=30_000)
    expected_precache = build_precache()
    cache_summary = page.evaluate(
        "async ({expected, cacheName}) => { const names = (await caches.keys()).filter(name => name.startsWith('entrenamiento-pwa-')); "
        "const cache = await caches.open(cacheName); "
        "const missing = []; for (const path of expected) { "
        "if (!await cache.match(new URL(path, location.origin + '/').href)) missing.push(path); } "
        "return {names, cacheName, entries: (await cache.keys()).length, expected: expected.length, missing}; }",
        {"expected": expected_precache, "cacheName": expected_cache_name},
    )
    if expected_cache_name not in cache_summary["names"] or cache_summary["missing"]:
        raise AssertionError(f"El paquete instalado no contiene todo el precache: {cache_summary}")

    context.set_offline(True)
    page.goto(origin, wait_until="domcontentloaded")
    manifest_icons = page.evaluate(
        """async () => {
          const response = await fetch('./manifest.webmanifest');
          if (!response.ok) throw new Error(`manifest offline HTTP ${response.status}`);
          const manifest = await response.json();
          return await Promise.all(manifest.icons.map(async icon => {
            const image = new Image();
            image.src = new URL(icon.src, location.href).href;
            await image.decode();
            return {src: icon.src, declared: icon.sizes, width: image.naturalWidth, height: image.naturalHeight};
          }));
        }"""
    )
    for icon in manifest_icons:
        if icon["declared"] != f'{icon["width"]}x{icon["height"]}' or icon["width"] != icon["height"]:
            raise AssertionError(f"Icono PWA incorrecto o no decodificable sin conexión: {icon}")
    if {icon["width"] for icon in manifest_icons} != {192, 512}:
        raise AssertionError(f"Se esperan iconos instalables de 192 y 512 px: {manifest_icons}")
    portrait_urls = [path for path in expected_precache if "/frases_fitness/retratos/" in path]
    portrait_audit = page.evaluate("""async paths => {
      const failures=[];
      for(const path of paths){
        try{const response=await fetch(path);if(!response.ok)throw new Error(`HTTP ${response.status}`);const bitmap=await createImageBitmap(await response.blob());if(bitmap.width<80||bitmap.height<80)throw new Error(`dimensión ${bitmap.width}x${bitmap.height}`);bitmap.close();}
        catch(error){failures.push({path,error:String(error)});}
      }
      return {count:paths.length,failures};
    }""", portrait_urls)
    if portrait_audit["count"] != 58 or portrait_audit["failures"]:
        raise AssertionError(f"Retratos de citas no decodificables sin conexión: {portrait_audit}")
    offline_results = []
    for name, _sex, _variant in ROUTINES:
        page.goto(f"{origin}data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        if not page.evaluate("Boolean(navigator.serviceWorker.controller)"):
            raise AssertionError(f"{name}: documento abierto sin estar controlado por el service worker")
        inventory = assert_image_inventory(page, name)
        resource_quality = assert_visual_resource_quality(page, name)
        offline_results.append({"routine": name, **inventory, "resourceQuality": resource_quality})
        offline_gif = page.locator(".day3ExerciseGif:visible,.day4ExerciseGif:visible").first
        if offline_gif.count() == 0:
            offline_gif = page.locator('img[src*="/videos/"]:visible,img[data-battery-motion-src*="/videos/"]:visible').first
        if offline_gif.count() == 0:
            raise AssertionError(f"{name}: no se encontró un GIF visible para validar sin conexión")
        offline_gif.scroll_into_view_if_needed()
        assert_animation_changes(page, offline_gif)
    # Usa una ruta profunda no precacheada: las rutas canónicas sí existen en
    # Cache API y deben continuar abriendo su rutina, no sustituirse por portada.
    deep_link = f"{origin}offline/deep-link.html?e2e=offline-fallback"
    page.goto(deep_link, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")
    page.wait_for_function("!document.documentElement.classList.contains('gymratik-loading')", timeout=10_000)
    fallback_heading = page.locator("#pageTitle").inner_text().strip()
    base_href = page.locator("base").get_attribute("href")
    fallback_inventory = assert_image_inventory(page, "respaldo offline desde ruta profunda")
    if fallback_heading != "Empieza a tu ritmo." or base_href != origin:
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
    return {"cache": cache_summary, "manifestIcons": manifest_icons, "offlineRoutines": offline_results, "runtime": {**runtime_failures, "cancelledSupersededRequests": offline_cancelled_requests}}


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
            install_test_clock(page)
            page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(name)}", wait_until="networkidle")
            page.wait_for_function("() => [...document.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)")
            page.locator(".performanceEntry").first.wait_for(state="visible")
            page.evaluate("async () => { await document.fonts.ready; }")
            advance_test_clock(page, 100)
            layout = page.evaluate("""() => {
              const rect = element => { const r = element.getBoundingClientRect(); return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}; };
              const entry = document.querySelector('.performanceEntry');
              const controls = [...entry.querySelectorAll('button,input,select,[role=button]')].map(rect);
              const offenders = [...document.body.querySelectorAll('*')].map(element => ({element,box:rect(element),scrollWidth:element.scrollWidth,clientWidth:element.clientWidth})).filter(item => item.box.right>innerWidth+1 || item.box.left < -1 || item.scrollWidth>item.clientWidth+2).slice(0,30).map(item => ({tag:item.element.tagName,id:item.element.id,className:String(item.element.className).slice(0,100),box:item.box,scrollWidth:item.scrollWidth,clientWidth:item.clientWidth}));
              const edgeOverflow=[...document.body.querySelectorAll('*')].map(element=>({element,box:rect(element)})).filter(item=>item.box.right>innerWidth+1||item.box.left < -1).slice(0,30).map(item=>({tag:item.element.tagName,id:item.element.id,className:String(item.element.className).slice(0,100),box:item.box}));
              const card=entry.closest('.card');
              const ancestry=[]; for(let node=entry;node&&node!==card;node=node.parentElement){const s=getComputedStyle(node);ancestry.push({tag:node.tagName,className:String(node.className),box:rect(node),display:s.display,gridColumns:s.gridTemplateColumns,overflow:s.overflow});}
              const responsiveElements=[...document.querySelectorAll('.page,.hero,.hero>div,.heroMeta,.heroDetails,.muscleDayGrid,.muscleDayItem,.muscleDayVisual,.performanceFieldTitleRow,.performanceFieldLabel')].slice(0,22).map(element=>{const s=getComputedStyle(element);return {className:String(element.className).slice(0,60),box:rect(element),scrollWidth:element.scrollWidth,clientWidth:element.clientWidth,display:s.display,gridColumns:s.gridTemplateColumns,minWidth:s.minWidth,overflow:s.overflow,text:(element.innerText||'').trim().replace(/\\s+/g,' ').slice(0,70)}});
              const homeLink=document.querySelector('.routine-home-link'), eyebrow=document.querySelector('.hero .eyebrow');
              const headerGap=homeLink&&eyebrow?eyebrow.getBoundingClientRect().top-homeLink.getBoundingClientRect().bottom:null;
              return {viewport:{width:innerWidth,height:innerHeight},documentWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth,entry:rect(entry),card:rect(card),cardGrid:getComputedStyle(card).gridTemplateColumns,cardChildren:[...card.children].map(child=>({className:String(child.className),box:rect(child),gridColumn:getComputedStyle(child).gridColumn})),headerGap,ancestry,controls,offenders,edgeOverflow,responsiveElements};
            }""")
            visual_audit = page.evaluate("""() => {
              const techniqueAccordions=[...document.querySelectorAll('article.card details.techAccordion')];
              const accordionsCollapsedByDefault=techniqueAccordions.every(details=>!details.open);
              if(techniqueAccordions[0]) techniqueAccordions[0].querySelector('summary')?.click();
              const accordionTapWorks=Boolean(techniqueAccordions[0]?.open);
              techniqueAccordions.forEach(details=>{details.open=true});
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
              const expandedTechniqueVisible=techniqueAccordions.length>0&&techniqueAccordions.every(details=>{const section=details.querySelector('.techSteps,.techniqueSteps');return Boolean(section&&visible(section)&&section.textContent.trim().length>0)});
              techniqueAccordions.forEach(details=>{details.open=false});
              return {positioned:positioned.length,controls:controls.length,textNodes:text.length,offscreen,clippedText,clippedControls,missingExerciseParts,detachedTechniqueSections,cardTopology,accordions:{count:techniqueAccordions.length,collapsedByDefault:accordionsCollapsedByDefault,tapWorks:accordionTapWorks,expandedTechniqueVisible}};
            }""")
            if layout["documentWidth"] > width:
                raise AssertionError(f"{name} {width}x{height}: el documento permite desplazamiento horizontal: ancho={layout['documentWidth']}, viewport={width}, bordes={layout['edgeOverflow']}, elementosConOverflow={layout['offenders']}")
            if layout["headerGap"] is None or layout["headerGap"] < 8:
                raise AssertionError(f"{name} {width}x{height}: el botón Portada invade o queda demasiado cerca de la etiqueta del encabezado: separación={layout['headerGap']} px")
            if layout["entry"]["left"] < -1 or layout["entry"]["right"] > width + 1:
                raise AssertionError(f"{name} {width}x{height}: zona de registro fuera del viewport: {layout['entry']}")
            if any(control["left"] < -1 or control["right"] > width + 1 for control in layout["controls"]):
                raise AssertionError(f"{name} {width}x{height}: control recortado horizontalmente: {layout['controls']}")
            if visual_audit["offscreen"] or visual_audit["clippedText"] or visual_audit["clippedControls"] or visual_audit["missingExerciseParts"] or visual_audit["detachedTechniqueSections"] or visual_audit["cardTopology"]["total"] != visual_audit["cardTopology"]["insideRoutineGrid"] or visual_audit["accordions"]["count"] != visual_audit["cardTopology"]["total"] or not visual_audit["accordions"]["collapsedByDefault"] or not visual_audit["accordions"]["tapWorks"] or not visual_audit["accordions"]["expandedTechniqueVisible"]:
                raise AssertionError(f"{name} {width}x{height}: auditoría de geometría visual falló: {visual_audit}")

            overlap = None
            summary_visible_rows = None
            if width <= 640:
                warmup = page.locator("#warmupAction")
                warmup.scroll_into_view_if_needed()
                click_control(warmup)
                advance_test_clock(page, 15_000)
                click_control(warmup)
                click_control(warmup)
                button = page.locator("article.card[data-exercise-index]").first.locator(".completeSetButton")
                button.scroll_into_view_if_needed()
                first_card = page.locator("article.card[data-exercise-index]").first
                select_valid_performance(first_card)
                click_control(button)  # inicia aproximación
                advance_test_clock(page, 20_000)
                click_control(button)  # registra aproximación
                dispatch_browser_hold(page, button, 5_150)
                if page.locator("#summaryActivityStatus").get_attribute("data-activity") != "preparing":
                    state = page.evaluate("""() => ({activity:document.querySelector('#summaryActivityStatus')?.dataset.activity,
                      activityText:document.querySelector('#summaryActivityStatus')?.innerText,
                      button:[...document.querySelectorAll('.completeSetButton')].slice(0,2).map(element=>({text:element.innerText,
                        className:element.className,connected:element.isConnected,hidden:element.hidden,disabled:element.disabled})),
                      warmup:document.querySelector('#warmupAction')?.innerText,
                      timers:Object.entries(localStorage).filter(([key])=>/timing|series-v1/i.test(key)).map(([key,value])=>({key,value:value.slice(0,500)}))})""")
                    raise AssertionError(f"{name} {width}x{height}: omitir descanso de aproximación no inició la preparación: {state}")
                advance_test_clock(page, 15_000)
                summary = page.locator("#floatingSessionSummary")
                if page.locator("#summaryToggle").get_attribute("aria-expanded") != "true":
                    click_control(page.locator("#summaryToggle"))
                button.scroll_into_view_if_needed()
                overlap = page.evaluate("""() => {
                  const button = document.querySelector('.completeSetButton');
                  const panel = document.querySelector('#floatingSessionSummary');
                  const a = button.getBoundingClientRect(), b = panel.getBoundingClientRect();
                  return {button:{left:a.left,right:a.right,top:a.top,bottom:a.bottom},panel:{left:b.left,right:b.right,top:b.top,bottom:b.bottom},intersects:a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top};
                }""")
                if overlap["intersects"]:
                    raise AssertionError(f"{name} {width}x{height}: resumen flotante tapa el botón de acción: {overlap}")
                summary_visible_rows = summary.locator(".sessionSummaryList").evaluate("element => {const bounds=element.getBoundingClientRect(),panel=document.querySelector('#floatingSessionSummary'),body=document.querySelector('#summaryBody');const rect=node=>{const r=node.getBoundingClientRect();return {top:r.top,bottom:r.bottom,height:r.height}};const rows=[...element.querySelectorAll('.summaryExercise')].map(row=>{const r=row.getBoundingClientRect();return {top:r.top,bottom:r.bottom}});return {viewport:[innerWidth,innerHeight],visible:rows.filter(row=>row.top>=bounds.top-1&&row.bottom<=bounds.bottom+1).length,clientHeight:element.clientHeight,scrollHeight:element.scrollHeight,panel:rect(panel),panelMax:getComputedStyle(panel).maxHeight,body:rect(body),bodyChildren:[...body.children].map(node=>({className:node.className,box:rect(node),flex:getComputedStyle(node).flex,minHeight:getComputedStyle(node).minHeight})),rows};}")
                if summary_visible_rows["visible"] != 3:
                    raise AssertionError(f"{name} {width}x{height}: el resumen flotante no deja exactamente tres ejercicios visibles: {summary_visible_rows}")
            results.append({"routine": name, "viewport": f"{width}x{height}", "horizontalOverflow": False, "visualGeometry": visual_audit, "actionPanelOverlap": overlap, "summaryVisibleRows": summary_visible_rows})
            context.close()
    return {"viewports": len(RESPONSIVE_VIEWPORTS), "routineViewportChecks": results}


def validate_motivation_card(browser, widths=(320, 360, 412, 530)) -> dict:
    """Render an Arnold quote and portrait in isolated phone-sized contexts."""
    results = []
    for width in widths:
        context = browser.new_context(
            viewport={"width": width, "height": 915},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
        )
        context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true');")
        page = context.new_page()
        portrait_failures = []
        portrait_responses = []
        page.on("requestfailed", lambda request: portrait_failures.append({"url": request.url, "failure": request.failure}) if "/frases_fitness/retratos/" in request.url else None)
        page.on("response", lambda response: portrait_responses.append({"url": response.url, "status": response.status}) if "/frases_fitness/retratos/" in response.url else None)
        page.goto(f"http://127.0.0.1:{PORT}/data/rutinas_autocontenidas/canonicas/{quote(ROUTINES[0][0])}", wait_until="domcontentloaded")
        page.wait_for_function("window.fitnessQuotesData?.quotes?.length === 60")
        page.locator("#sessionCompletionPanel").evaluate("element => { element.hidden = false; }")
        page.locator("#summaryToggle").evaluate("element => element.setAttribute('aria-expanded', 'false')")
        page.locator("#summaryBody").evaluate("element => { element.hidden = true; }")
        page.evaluate("""() => {
          const button=document.getElementById('newMotivation'), author=document.getElementById('motivationNote');
          const quotes=window.fitnessQuotesData.quotes, target=quotes.findIndex(item=>item.author==='Arnold Schwarzenegger');
          if(target<0)throw new Error('Falta Arnold en el banco de citas');
          Math.random=()=>((target+.5)/quotes.length);
          button.click();
          if(!author.textContent.includes('Arnold Schwarzenegger'))throw new Error('La selección aleatoria controlada no eligió la cita esperada');
        }""")
        page.evaluate("() => { const panel=document.getElementById('sessionCompletionPanel'); window.scrollTo(0, Math.max(0, panel.getBoundingClientRect().top + window.scrollY - 16)); }")
        try:
            page.wait_for_function("document.getElementById('motivationPortrait')?.complete && document.getElementById('motivationPortrait')?.naturalWidth > 0", timeout=8_000)
        except Exception as error:
            diagnosis = page.evaluate("""() => {const image=document.getElementById('motivationPortrait');return {src:image?.getAttribute('src'),resolvedSrc:image?.src,complete:image?.complete,naturalWidth:image?.naturalWidth,naturalHeight:image?.naturalHeight,hidden:image?.hidden,loading:image?.loading,alt:image?.alt,quote:document.getElementById('motivationMessage')?.textContent,author:document.getElementById('motivationNote')?.textContent,portraitData:window.fitnessQuotesData?.quotes?.find(item=>item.author==='Arnold Schwarzenegger')?.portrait}}""")
            context.close()
            raise AssertionError(f"Retrato de la frase no se cargó/decodificó: diagnosis={diagnosis}, failed={portrait_failures}, responses={portrait_responses}") from error
        layout = page.evaluate("""() => {
          const panel=document.querySelector('#sessionCompletionPanel'), message=document.querySelector('#motivationMessage'), image=document.querySelector('#motivationPortrait'), credit=document.querySelector('#motivationPhotoCredit'), source=document.querySelector('#motivationNote');
          const box=node=>{const r=node.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
          const style=getComputedStyle(message);
          const overflowingDescendants=[...panel.querySelectorAll('*')].map(node=>({tag:node.tagName,id:node.id,className:typeof node.className==='string'?node.className:'',box:box(node),scrollWidth:node.scrollWidth,clientWidth:node.clientWidth})).filter(node=>node.box.left<box(panel).left-1||node.box.right>box(panel).right+1||node.scrollWidth>node.clientWidth+3);
          return {viewport:innerWidth,panel:box(panel),panelClientWidth:panel.clientWidth,panelScrollWidth:panel.scrollWidth,overflowingDescendants,children:[...panel.children].map(node=>({className:node.className,visible:getComputedStyle(node).display!=='none',box:box(node),scrollWidth:node.scrollWidth,clientWidth:node.clientWidth})),message:box(message),messageScrollWidth:message.scrollWidth,messageClientWidth:message.clientWidth,messageScrollHeight:message.scrollHeight,messageClientHeight:message.clientHeight,messageOverflow:style.overflow,quote:message.textContent,author:source.textContent,source:source.href,portrait:box(image),portraitNaturalWidth:image.naturalWidth,portraitAlt:image.alt,photoCredit:credit.textContent,photoCreditHref:credit.href};
        }""")
        if SCREENSHOT_DIR is not None:
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(SCREENSHOT_DIR / f"quote-card-{width}px.png"), full_page=False)
        page.evaluate("""() => { Math.random=()=>0; document.getElementById('newMotivation').click(); }""")
        next_author = page.locator("#motivationNote").text_content() or ""
        if "Arnold Schwarzenegger" in next_author:
            context.close()
            raise AssertionError(f"La rotación repitió consecutivamente la cita de Arnold a {width}px")
        layout["nextAuthor"] = next_author
        if layout["author"].find("Arnold Schwarzenegger") < 0 or layout["portraitNaturalWidth"] < 500 or layout["portrait"]["width"] < 80 or layout["portrait"]["height"] < 100:
            context.close()
            raise AssertionError(f"Cita de Arnold/retrato no se presentó en tamaño grande a {width}px: {layout}")
        if layout["panel"]["left"] < -1 or layout["panel"]["right"] > width + 1 or any(child["visible"] and (child["box"]["left"] < layout["panel"]["left"] or child["box"]["right"] > layout["panel"]["right"] or child["scrollWidth"] > child["clientWidth"] + 3) for child in layout["children"]):
            context.close()
            raise AssertionError(f"La tarjeta o alguno de sus bloques visibles se recorta/desborda a {width}px: {layout}")
        if layout["messageScrollWidth"] > layout["messageClientWidth"] + 1 or layout["messageScrollHeight"] > layout["messageClientHeight"] + 1 or layout["messageOverflow"] in ("hidden", "clip"):
            context.close()
            raise AssertionError(f"El texto de la cita se recorta a {width}px: {layout}")
        if "CC BY 4.0" not in layout["photoCredit"] or "schwarzenegger.com/fitness/post" not in layout["source"]:
            context.close()
            raise AssertionError(f"Falta la atribución enlazada de la cita o fotografía: {layout}")
        page.route("**/data/rutinas_autocontenidas/frases_fitness/retratos/*.jpg", lambda route: route.abort())
        page.evaluate("() => { Math.random=()=>0; document.getElementById('newMotivation').click(); }")
        page.wait_for_function("document.getElementById('motivationPortrait')?.hidden === true && document.getElementById('motivationInitials')?.hidden === false")
        fallback = page.evaluate("() => ({imageHidden:document.getElementById('motivationPortrait').hidden, initialsVisible:!document.getElementById('motivationInitials').hidden})")
        if not fallback["imageHidden"] or not fallback["initialsVisible"]:
            context.close()
            raise AssertionError(f"La cita dejó visible un retrato roto en vez del avatar de respaldo: {fallback}")
        layout["brokenPortraitFallback"] = fallback
        results.append(layout)
        context.close()
    return {"viewports": results, "quotePortraitAndTextVerified": True}


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
        phase_pairs = assert_exercise_phase_pairs(page, name)
        warmup_viewers = assert_warmup_single_viewers(page, name)
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
        result = {"routine": name, **inventory, **phase_pairs, "warmupViewers": warmup_viewers, "quality": quality}
        results.append(result)
        context.close()
    return results


def main() -> None:
    global SCREENSHOT_DIR, PORT
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screenshot-dir", type=Path, default=SCREENSHOT_DIR, help="opcional: guarda capturas de actividad y fallbacks en viewport móvil")
    parser.add_argument("--responsive-only", action="store_true", help="ejecuta solo la matriz de tamaños móviles")
    parser.add_argument("--resources-only", action="store_true", help="valida imágenes, proporciones y legibilidad de las cuatro rutinas")
    parser.add_argument("--functional-only", action="store_true", help="ejecuta los flujos funcionales táctiles de las cuatro rutinas")
    parser.add_argument("--celebration-only", action="store_true", help="valida la mascota persistente de una sesión completada en las cuatro rutinas")
    parser.add_argument("--cover-only", action="store_true", help="valida y captura la animación de portada en movimiento y con movimiento reducido")
    parser.add_argument("--day", type=int, choices=range(1, 5), help="limita el E2E funcional a un día para diagnóstico reproducible")
    parser.add_argument("--offline-only", action="store_true", help="ejecuta solo la validación offline del precache y rutas profundas")
    parser.add_argument("--quote-only", action="store_true", help="valida solo selección aleatoria y retrato/fallback de la frase")
    args = parser.parse_args()
    SCREENSHOT_DIR = args.screenshot_dir
    server = create_isolated_server()
    PORT = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    results = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="msedge", headless=True)
            if args.offline_only:
                result = validate_installed_offline_package(browser)
                browser.close()
                print(json.dumps({"status": "E2E_OFFLINE_OK", "result": result}, ensure_ascii=False, indent=2))
                return
            if args.celebration_only:
                results = [validate_completed_session_celebration(browser, name, sex, variant) for name, sex, variant in ROUTINES]
                browser.close()
                print(json.dumps({"status": "E2E_CELEBRATION_OK", "days": len(results), "results": results}, ensure_ascii=False, indent=2))
                return
            print("Sintético: portada y animación de bienvenida", flush=True)
            cover_animation = validate_home_cover_animation(browser)
            if args.cover_only:
                browser.close()
                print(json.dumps({"status": "E2E_COVER_OK", "coverAnimation": cover_animation}, ensure_ascii=False, indent=2))
                return
            if args.quote_only:
                quote_card = validate_motivation_card(browser)
                browser.close()
                print(json.dumps({"status": "E2E_QUOTE_OK", "quoteCard": quote_card}, ensure_ascii=False, indent=2))
                return
            if args.resources_only:
                print("Sintético: recursos visuales de las cuatro rutinas", flush=True)
                results = validate_resource_pages(browser)
                quote_card = validate_motivation_card(browser)
                responsive = None
                offline = None
            else:
                quote_card = None
                responsive = None if args.functional_only else validate_responsive_layout(browser)
            if not args.responsive_only and not args.resources_only:
                routines = ROUTINES if args.day is None else [ROUTINES[args.day - 1]]
                for name, sex, variant in routines:
                    print(f"Sintético: E2E funcional {name}", flush=True)
                    day_result = validate_day(browser, name, sex, variant)
                    day_result.update(validate_primary_set_buttons(browser, name, sex))
                    day_result.update(validate_completed_session_celebration(browser, name, sex, variant))
                    results.append(day_result)
                    print(f"Sintético: día validado {name}", flush=True)
                offline = None if args.functional_only else validate_installed_offline_package(browser)
            else:
                offline = None
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
    print(json.dumps({"status": "E2E_ROUTINES_OK", "days": len(results), "results": results, "coverAnimation": cover_animation, "quoteCard": quote_card, "responsive": responsive, "offlinePackage": offline}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
