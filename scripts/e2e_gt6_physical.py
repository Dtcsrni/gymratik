"""E2E de las cuatro rutinas en Chrome Android conectado por ADB/CDP.

Las pruebas de interacción pueden reutilizar la pestaña WebAPK en un origen
localhost separado de los datos instalados para evitar crear perfiles CDP OTR.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen

from playwright.sync_api import sync_playwright
from playwright.sync_api import Locator, Page

import e2e_routine_activity_check as suite


def resolve_cdp_websocket_url(endpoint_url: str) -> str:
    """Resolve Android CDP HTTP discovery to its WebSocket without adding Origin."""
    if endpoint_url.startswith(("ws://", "wss://")):
        return endpoint_url
    endpoint = endpoint_url.rstrip("/")
    endpoint_parts = urlsplit(endpoint)
    if endpoint_parts.scheme not in {"http", "https"} or not endpoint_parts.netloc:
        raise ValueError("El endpoint CDP debe usar http(s):// o ws(s):// con host explícito")
    with urlopen(f"{endpoint}/json/version", timeout=5) as response:
        websocket_url = json.load(response).get("webSocketDebuggerUrl")
    websocket_parts = urlsplit(websocket_url or "")
    expected_scheme = "wss" if endpoint_parts.scheme == "https" else "ws"
    if websocket_parts.scheme != expected_scheme or websocket_parts.netloc != endpoint_parts.netloc:
        raise RuntimeError("Chrome devolvió una URL WebSocket CDP inesperada")
    return websocket_url


def resolve_device_metrics(measured: list[float], width: int | None = None,
                           height: int | None = None,
                           device_scale_factor: float | None = None) -> tuple[int, int, float]:
    """Use live WebAPK metrics unless an explicit diagnostic override is requested."""
    return (
        width if width is not None else int(measured[0]),
        height if height is not None else int(measured[1]),
        device_scale_factor if device_scale_factor is not None else float(measured[2]),
    )


class PhysicalDeviceBrowser:
    """Adaptador para contextos físicos o una pestaña de prueba reutilizable."""

    def __init__(self, browser, width: int, height: int, device_scale_factor: float,
                 reuse_page=None, test_origin: str | None = None, home_url: str | None = None,
                 original_goto=None):
        self._browser = browser
        self._reuse_page = reuse_page
        self._test_origin = test_origin
        self._home_url = home_url
        self._original_goto = original_goto
        self.lightweight_assets = False
        self._metrics = {
            "viewport": {"width": width, "height": height},
            "device_scale_factor": device_scale_factor,
            "is_mobile": True,
            "has_touch": True,
        }

    def new_context(self, **options):
        if self._reuse_page is not None:
            context = ReusablePhysicalContext(
                self._reuse_page, self._test_origin, self._home_url, self._original_goto,
                lightweight_assets=self.lightweight_assets,
            )
            if self.lightweight_assets:
                context.route("**/*", lambda route: route.continue_())
            return context
        options.update(self._metrics)
        if self.lightweight_assets:
            options.setdefault("service_workers", "block")
        context = self._browser.new_context(**options)
        if self.lightweight_assets:
            pixel_gif = bytes.fromhex("47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b")

            def keep_functional_context_light(route):
                if route.request.resource_type == "image":
                    route.fulfill(status=200, content_type="image/gif", body=pixel_gif)
                else:
                    route.continue_()

            context.route("**/*", keep_functional_context_light)
        return context


class ReusablePhysicalContext:
    """Context facade that never creates/closes a Chrome Android profile."""

    def __init__(self, page, test_origin: str, home_url: str, original_goto,
                 lightweight_assets: bool = False):
        self.page = page
        self.test_origin = test_origin.rstrip("/")
        self.home_url = home_url
        self.original_goto = original_goto
        self.routes = []
        self.lightweight_assets = lightweight_assets
        self._offline = False
        self.clear_test_origin_data()
        self.page._gt6_physical_tap = android_tap
        self.page._gt6_physical_hold = android_touch_hold
        self.page._gt6_physical_select_performance = android_select_valid_performance
        self.page._gt6_test_clock_install = self.install_test_clock
        self.page._gt6_test_clock_advance = self.advance_test_clock
        self._virtual_time_session = None

    def install_test_clock(self) -> None:
        # El WebAPK usa su reloj real para conservar su timeline de animación.
        return None

    def advance_test_clock(self, duration_ms: int) -> None:
        self.page.wait_for_timeout(duration_ms)

    def add_init_script(self, script: str) -> None:
        guarded = (
            "if (location.origin === " + json.dumps(self.test_origin) + ") {\n" + script + "\n}"
        )
        self.page.context.add_init_script(guarded)

    def new_page(self):
        return self.page

    def clear_test_origin_data(self) -> None:
        """Reset only temporary localhost storage, never the installed PWA origin."""
        if not self.page.url.startswith(self.test_origin + "/"):
            return
        self.page.evaluate("""async () => {
          localStorage.clear(); sessionStorage.clear();
          await Promise.all((await navigator.serviceWorker.getRegistrations()).map(registration => registration.unregister()));
          if (typeof indexedDB.databases === 'function') {
            const databases = await indexedDB.databases();
            await Promise.all(databases.map(({name}) => new Promise(resolve => {
              if (!name) return resolve();
              const request = indexedDB.deleteDatabase(name);
              request.onsuccess = request.onerror = request.onblocked = () => resolve();
            })));
          }
          if ('caches' in window) await Promise.all((await caches.keys()).map(name => caches.delete(name)));
        }""")

    def set_offline(self, offline: bool) -> None:
        """Toggle network emulation through the existing WebAPK context."""
        self.page.context.set_offline(offline)
        self._offline = bool(offline)

    def route(self, pattern, handler) -> None:
        if self.lightweight_assets:
            original_handler = handler
            pixel_gif = bytes.fromhex(
                "47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b"
            )

            def lightweight_handler(route):
                if route.request.resource_type == "image":
                    route.fulfill(status=200, content_type="image/gif", body=pixel_gif)
                else:
                    original_handler(route)

            handler = lightweight_handler
        self.page.route(pattern, handler)
        self.routes.append((pattern, handler))

    def close(self) -> None:
        # La barrera de origen vive en clear_test_origin_data(); nunca se borra
        # IndexedDB/localStorage del origen instalado 127.0.0.1.
        if self._offline:
            self.page.context.set_offline(False)
            self._offline = False
        self.clear_test_origin_data()
        if self._virtual_time_session is not None:
            try:
                self._virtual_time_session.send(
                    "Emulation.setVirtualTimePolicy", {"policy": "pauseIfNetworkFetchesPending"}
                )
            finally:
                self._virtual_time_session.detach()
                self._virtual_time_session = None
                self.page.__dict__.pop("_gt6_virtual_time_session", None)
        for pattern, handler in self.routes:
            self.page.unroute(pattern, handler)
        self.routes.clear()
        self.page.__dict__.pop("_gt6_physical_tap", None)
        self.page.__dict__.pop("_gt6_physical_hold", None)
        self.page.__dict__.pop("_gt6_physical_select_performance", None)
        self.page.__dict__.pop("_gt6_test_clock_install", None)
        self.page.__dict__.pop("_gt6_test_clock_advance", None)
        if self.page.url != self.home_url:
            self.original_goto(self.page, self.home_url, wait_until="domcontentloaded")


def android_tap(locator: Locator, hold_ms: int = 80) -> None:
    locator.evaluate("element => element.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})")
    locator.page.wait_for_timeout(150)
    box = locator.bounding_box()
    if not box:
        raise AssertionError("El control táctil no tiene un rectángulo visible")
    page = locator.page
    before_url = page.url
    before = locator.evaluate("element => ({aria:element.getAttribute('aria-label'), text:element.innerText, className:element.className?.toString?.(), value:element.value, checked:element.checked, disabled:element.disabled, activity:document.querySelector('#summaryActivityStatus')?.dataset.activity, progress:element.closest('article')?.querySelector('.exerciseProgress')?.innerText, dialogs:document.querySelectorAll('dialog[open],[role=dialog]:not([hidden])').length})")
    locator.evaluate("element => { window.__gt6TouchClickReceived = false; window.__gt6TouchClickHandler = event => { if (event.composedPath().includes(element)) window.__gt6TouchClickReceived = true; }; document.addEventListener('click', window.__gt6TouchClickHandler, true); }")
    point = {
        "x": box["x"] + box["width"] / 2,
        "y": box["y"] + box["height"] / 2,
        "id": 1,
        "radiusX": 5,
        "radiusY": 5,
        "force": 1,
    }
    session = page.context.new_cdp_session(page)
    try:
        # synthesizeTapGesture garantiza la secuencia down/up/click del navegador;
        # dispatchTouchEvent manual solo había producido touchstart en este WebAPK.
        session.send("Input.synthesizeTapGesture", {
            "x": point["x"], "y": point["y"], "duration": max(1, hold_ms),
            "gestureSourceType": "touch",
        })
        # Android procesa el click tras cerrar el gesto CDP; espera el frame
        # de interfaz antes de que el contrato funcional lea el nuevo estado.
        page.wait_for_timeout(250)
    finally:
        session.detach()
    after = None
    try:
        after = locator.evaluate("element => ({aria:element.getAttribute('aria-label'), text:element.innerText, className:element.className?.toString?.(), value:element.value, checked:element.checked, disabled:element.disabled, activity:document.querySelector('#summaryActivityStatus')?.dataset.activity, progress:element.closest('article')?.querySelector('.exerciseProgress')?.innerText, dialogs:document.querySelectorAll('dialog[open],[role=dialog]:not([hidden])').length})")
    except Exception:
        pass
    if page.url != before_url:
        # La navegación correcta desmonta el nodo y el listener de su documento;
        # para enlaces se comprueba el destino, no el listener ya destruido.
        return
    received = page.evaluate("() => { const result = window.__gt6TouchClickReceived === true; if (window.__gt6TouchClickHandler) document.removeEventListener('click', window.__gt6TouchClickHandler, true); delete window.__gt6TouchClickHandler; delete window.__gt6TouchClickReceived; return result; }")
    state_changed = after is not None and before != after
    if not physical_tap_succeeded(before_url, page.url, received, state_changed):
        hit = page.evaluate("""({x,y})=>{const e=document.elementFromPoint(x,y);return {tag:e?.tagName,className:e?.className?.toString?.(),ariaLabel:e?.getAttribute?.('aria-label')}}""", {"x": point["x"], "y": point["y"]})
        raise AssertionError(f"El gesto táctil del GT6 no generó click ni una transición de interfaz; antes={before}, después={after}, hit-test={hit}")


def physical_tap_succeeded(before_url: str, after_url: str, click_received: bool,
                           state_changed: bool) -> bool:
    """A navigation itself proves a link tap when its old DOM listener is gone."""
    return after_url != before_url or click_received or state_changed


def android_touch_hold(page, button, duration_ms: int, release_click: bool = True,
                       virtual_clock: bool = False) -> None:
    button.evaluate("element => { window.__gt6HoldButton = element; element.setAttribute('data-e2e-hold-target', 'true'); }")
    button.evaluate("element => { delete element.dataset.e2ePointerDownReceived; element.addEventListener('pointerdown', () => { element.dataset.e2ePointerDownReceived = 'true'; }, { capture: true, once: true }); }")
    button.evaluate("element => { window.__gt6HoldReleaseClick = false; element.addEventListener('click', () => { window.__gt6HoldReleaseClick = true; }, { capture: true, once: true }); }")
    button.evaluate("element => element.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})")
    page.wait_for_timeout(150)
    box = button.bounding_box()
    if not box:
        raise AssertionError("El control mantenido no tiene un rectángulo visible")
    point = {"x": box["x"] + box["width"] / 2, "y": box["y"] + box["height"] / 2,
             "id": 1, "radiusX": 5, "radiusY": 5, "force": 1}
    session = page.context.new_cdp_session(page)
    try:
        session.send("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [point]})
        if not button.evaluate("element => element.classList.contains('is-holding')"):
            raise AssertionError("El toque real no inició el feedback de mantener pulsado")
        if virtual_clock:
            page.clock.run_for(duration_ms)
        else:
            page.wait_for_timeout(duration_ms)
        session.send("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})
        if release_click:
            # dispatchTouchEvent no siempre materializa el click de liberación
            # que Android genera tras un long-press. Sin él, longPressDetected
            # queda activo y el siguiente toque real se consume como release.
            page.wait_for_timeout(200)
            if not page.evaluate("() => window.__gt6HoldReleaseClick === true"):
                # CDP touchStart/touchEnd no siempre produce el click de
                # liberación de Android. La pulsación y el temporizador sí son
                # táctiles/reales; sintetizamos solo ese click sobre el mismo
                # nodo si sigue conectado y habilitado, aunque se haya movido.
                release_target = page.evaluate("""() => {
                  const element = window.__gt6HoldButton;
                  if (!element) return {connected:false, missing:true};
                  return {connected:element.isConnected, disabled:element.disabled};
                }""")
                if release_target.get("missing"):
                    raise AssertionError("Se perdió la referencia al botón mantenido antes de liberar el gesto")
                if release_target["connected"] and not release_target["disabled"]:
                    # Usar el mismo nodo presionado evita que un rerender
                    # convierta el fallback en una acción sobre el botón nuevo.
                    page.evaluate("() => window.__gt6HoldButton.click()")
                    if not page.evaluate("() => window.__gt6HoldReleaseClick === true"):
                        raise AssertionError(
                            "No se entregó el click de liberación al botón mantenido: "
                            f"{release_target}"
                        )
                # Si el propio flujo ya deshabilitó o retiró el botón, no
                # fabriques un click sobre otro control. La acción prolongada
                # puede desplazar la página y sacar el botón del hit-test; se
                # libera solo el mismo nodo que recibió el toque inicial.
    finally:
        session.detach()
        page.evaluate("""() => {
          window.__gt6HoldButton?.removeAttribute('data-e2e-hold-target');
          delete window.__gt6HoldButton;
        }""")


def android_select_valid_performance(card) -> None:
    """Select rep/load by real touch gestures on the GT6 range controls."""
    for selector in ("input.performanceReps", "input.performanceLoad"):
        control = card.locator(selector)
        control.evaluate("element => { element.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'}); const r=element.getBoundingClientRect(); if(r.top<0||r.bottom>innerHeight) window.scrollBy({top:r.top+r.height/2-innerHeight/2,behavior:'instant'}); }")
        control.page.wait_for_timeout(350)
        metrics = control.evaluate("element => ({min:Number(element.min),max:Number(element.max),value:Number(element.value),viewport:{width:innerWidth,height:innerHeight},rect:(()=>{const r=element.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()})")
        rect = metrics["rect"]
        x = rect["x"] + rect["width"] * (0.06 + 0.88 * 0.58)
        y = (max(rect["y"], 0) + min(rect["y"] + rect["height"], metrics["viewport"]["height"])) / 2
        page = control.page
        hit = control.evaluate("(element,point) => { const target=document.elementFromPoint(point.x,point.y); return target===element||element.contains(target); }", {"x": x, "y": y})
        if not hit:
            overlay = page.evaluate("({x,y})=>{const e=document.elementFromPoint(x,y);return {tag:e?.tagName,id:e?.id,className:e?.className?.toString?.(),aria:e?.getAttribute?.('aria-label')}}", {"x": x, "y": y})
            raise AssertionError(f"El punto táctil calculado no cae sobre {selector} después de centrarlo: rect={rect}, viewport={metrics['viewport']}, hit={overlay}")
        session = page.context.new_cdp_session(page)
        try:
            # Un toque sobre la pista selecciona un valor real y evita dejar
            # una secuencia touchstart/move viva en el contexto Chrome del usuario.
            session.send("Input.synthesizeTapGesture", {
                "x": x, "y": y, "duration": 100, "gestureSourceType": "touch",
            })
        finally:
            session.detach()
        page.wait_for_timeout(150)
        selected = control.evaluate("element => element.dataset.selected === 'true' || (element.classList.contains('performanceLoad') && element.closest('.performanceEntry')?.querySelector('.performanceLoadValue')?.dataset.selected === 'true')")
        if not selected:
            raise AssertionError(f"El gesto táctil no seleccionó un valor válido en {selector}: {metrics}")


def snapshot_installed_user_data(page) -> dict:
    """Hash the real WebAPK's local state read-only; never emit profile contents."""
    snapshot = page.evaluate("""async () => {
      if (typeof indexedDB.databases !== 'function') throw new Error('No se puede enumerar IndexedDB de forma segura');
      const localStorageState = Object.keys(localStorage).sort().map(key => [key, localStorage.getItem(key)]);
      const databaseNames = (await indexedDB.databases()).map(database => database.name);
      const indexedDbState = {};
      if (databaseNames.includes('entrenamiento-progress')) {
        const database = await new Promise((resolve, reject) => {
          const request = indexedDB.open('entrenamiento-progress');
          request.onsuccess = () => resolve(request.result);
          request.onerror = () => reject(request.error);
        });
        const stores = [...database.objectStoreNames];
        const transaction = database.transaction(stores, 'readonly');
        const records = await Promise.all(stores.map(name => new Promise((resolve, reject) => {
          const request = transaction.objectStore(name).getAll();
          request.onsuccess = () => resolve([name, request.result]);
          request.onerror = () => reject(request.error);
        })));
        records.forEach(([name, values]) => { indexedDbState[name] = values; });
        database.close();
      }
      const sessionStorageState = Object.keys(sessionStorage).sort().map(key => [key, sessionStorage.getItem(key)]);
      return {localStorageState, sessionStorageState, indexedDbState};
    }""")
    serialized = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    counts = {name: len(rows) for name, rows in snapshot["indexedDbState"].items()}
    fingerprints = {
        "localStorage": {key: hashlib.sha256(value.encode("utf-8")).hexdigest() for key, value in snapshot["localStorageState"]},
        "sessionStorage": {key: hashlib.sha256(value.encode("utf-8")).hexdigest() for key, value in snapshot["sessionStorageState"]},
        "indexedDB": {
            name: hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            for name, rows in snapshot["indexedDbState"].items()
        },
    }
    return {
        "sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        "localStorageKeys": len(snapshot["localStorageState"]),
        "sessionStorageKeys": len(snapshot["sessionStorageState"]),
        "indexedDbRecords": counts,
        "fingerprints": fingerprints,
    }


def summarize_day(result: dict) -> dict:
    return {
        "routine": result["routine"],
        "exercises": result["exercises"],
        "images": result["images"],
        "brokenImages": 0,
        "batteryGifPauseResume": bool(result["batteryGifPauseResume"])
        and all(
            item["pausedOffscreen"] and item["posterShown"] and item["resumedOnscreen"]
            for item in result["batteryGifPauseResume"].values()
        ),
        "batteryMotionDetails": result["batteryGifPauseResume"],
        "backgroundTimerPauseResume": bool(
            result["backgroundTimer"]["paused"] and result["backgroundTimer"]["resumed"]
        ),
        "primaryButtonsTested": result["primarySetButtonsTested"],
        "skipButtonsTested": result["exerciseSkipButtonsTested"],
        "exerciseCompletionRestTested": result["exerciseCompletionRestTested"],
        "celebration": result["mascotAnimation"],
    }


def require_installed_webapk_foreground() -> str:
    """Read-only guard: require the installed Gymratik WebAPK to own Android foreground."""
    devices = subprocess.run(
        ["adb", "devices", "-l"], capture_output=True, text=True, timeout=10
    )
    if devices.returncode:
        raise RuntimeError(f"No se pudo consultar ADB: {devices.stderr.strip()}")
    connected = [
        line.split()[0]
        for line in devices.stdout.splitlines()[1:]
        if len(line.split()) >= 2 and line.split()[1] == "device"
    ]
    if len(connected) != 1:
        raise RuntimeError(
            "El E2E físico requiere exactamente un Android autorizado por ADB; "
            f"se detectaron {len(connected)}. No cambiaré el foco del dispositivo."
        )

    activity = subprocess.run(
        ["adb", "-s", connected[0], "shell", "dumpsys", "activity", "activities"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if activity.returncode:
        raise RuntimeError(f"No se pudo consultar la actividad Android: {activity.stderr.strip()}")
    foreground_rows = [
        line.strip()
        for line in activity.stdout.splitlines()
        if "topResumedActivity" in line or "mResumedActivity" in line
    ]
    foreground = "\n".join(foreground_rows)
    if not foreground_rows or not all(
        "org.chromium.chrome.browser.webapps.SameTaskWebApkActivity" in row
        for row in foreground_rows
    ):
        raise RuntimeError(
            "Gymratik instalada no está confirmada como actividad Android visible "
            "(SameTaskWebApkActivity). Deja la PWA al frente y la pantalla desbloqueada; "
            "el runner no abrirá ni cambiará de aplicación."
        )

    window = subprocess.run(
        ["adb", "-s", connected[0], "shell", "dumpsys", "window"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    power = subprocess.run(
        ["adb", "-s", connected[0], "shell", "dumpsys", "power"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if window.returncode or power.returncode:
        raise RuntimeError("No se pudo verificar de forma segura que la pantalla esté despierta y desbloqueada.")
    if "mWakefulness=Awake" not in power.stdout or "isKeyguardShowing=false" not in window.stdout:
        raise RuntimeError(
            "El GT6 está dormido o bloqueado; despiértalo y desbloquéalo manualmente para validar "
            "fotogramas. El runner no omitirá la pantalla de seguridad."
        )
    return connected[0]


def bring_android_page_to_foreground(page) -> dict[str, float]:
    """Verify native WebAPK foreground and advancing visual clock before visual claims."""
    require_installed_webapk_foreground()
    page.bring_to_front()
    require_installed_webapk_foreground()
    page.wait_for_function(
        "document.visibilityState === 'visible' && document.hasFocus()",
        timeout=15_000,
    )
    before = page.evaluate("document.timeline.currentTime")
    page.wait_for_timeout(250)
    after = page.evaluate("document.timeline.currentTime")
    if before is None or after is None or after <= before:
        page.wait_for_timeout(500)
        after = page.evaluate("document.timeline.currentTime")
    if before is None or after is None or after <= before:
        raise RuntimeError(
            "El WebAPK no está avanzando su timeline visual; no se evaluarán "
            "animaciones congeladas como si fueran defectos del arte."
        )
    return {"timelineBeforeMs": float(before), "timelineAfterMs": float(after)}


def verify_visible_installed_mascot_motion(page, screenshot_dir: Path | None = None) -> dict[str, str]:
    """Sample mascot rendering in the physical WebAPK on the isolated test origin."""
    home_url = f"http://127.0.0.1:{suite.PORT}/"
    test_origin = f"http://localhost:{suite.PORT}"
    if page.url != home_url:
        raise RuntimeError("La validación visual requiere que la PWA instalada esté en portada.")
    if screenshot_dir:
        screenshot_dir.mkdir(parents=True, exist_ok=True)
    routine_url = f"http://127.0.0.1:{suite.PORT}/data/rutinas_autocontenidas/canonicas/{suite.ROUTINES[0][0]}"
    try:
        page.goto(routine_url, wait_until="domcontentloaded")
        page.wait_for_selector("#summaryActivityMascot")
        foreground = bring_android_page_to_foreground(page)
        image = page.locator("#summaryActivityMascot")
        state = image.evaluate("""element => ({
          activity: document.querySelector('#summaryActivityStatus')?.dataset.activity,
          motion: element.dataset.motion,
          animation: getComputedStyle(element).animationName,
          source: element.currentSrc,
          loaded: element.complete && element.naturalWidth > 0,
          reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches
        })""")
        expected_motion = "celebration" if state["activity"] == "complete" else state["activity"]
        if not state["loaded"] or state["motion"] != expected_motion:
            raise AssertionError(f"La mascota instalada no refleja la actividad real: {state}")
        mascot_frames_advance = False
        if not state["reducedMotion"]:
            first = image.screenshot()
            page.wait_for_timeout(500)
            mascot_frames_advance = first != image.screenshot()
            if not mascot_frames_advance:
                raise AssertionError(f"La mascota no avanzó visualmente en su estado real {state}")
        if screenshot_dir and not state["reducedMotion"]:
            image.screenshot(path=str(screenshot_dir / f"mascot-{state['motion']}-gt6.png"))

        # Una imagen temporal superpuesta permite observar los cuadros del GIF
        # en el compositor real de WebAPK, sin cambiar el nodo de la mascota,
        # el progreso ni las preferencias guardadas.
        gif_probe = page.locator("#gt6PhysicalGifProbe")
        page.evaluate("""() => {
          const probe = new Image();
          probe.id = 'gt6PhysicalGifProbe';
          probe.alt = '';
          probe.src = location.origin + '/data/profile/mascot-motion/neutral-rest-25fps.gif';
          Object.assign(probe.style, {
            position: 'fixed', left: '50%', top: '40%', transform: 'translate(-50%, -50%)',
            zIndex: '2147483647', width: '128px', height: '128px', objectFit: 'contain',
            background: '#071923', border: '1px solid #65f2dd', borderRadius: '12px'
          });
          document.body.append(probe);
        }""")
        try:
            page.wait_for_function(
                "element => element.complete && element.naturalWidth > 0",
                arg=gif_probe.element_handle(),
            )
            gif_first = gif_probe.screenshot()
            page.wait_for_timeout(650)
            if gif_first == gif_probe.screenshot():
                raise AssertionError("El GIF real no avanzó cuadros visibles en el compositor del GT6")
        finally:
            page.locator("#gt6PhysicalGifProbe").evaluate("element => element.remove()")
        return {
            "observedActivity": state["activity"],
            "observedMotion": state["motion"],
            "observedCssAnimation": state["animation"],
            "reducedMotion": state["reducedMotion"],
            "mascotFramesAdvanceVisibly": mascot_frames_advance,
            "gifFramesAdvanceVisibly": True,
            "foregroundTimeline": foreground,
        }
    finally:
        if page.url.startswith(test_origin + "/"):
            page.evaluate("""async () => {
              localStorage.clear(); sessionStorage.clear();
              if ('serviceWorker' in navigator) await Promise.all((await navigator.serviceWorker.getRegistrations()).map(reg => reg.unregister()));
              if (typeof indexedDB.databases === 'function') await Promise.all((await indexedDB.databases()).map(({name}) => new Promise(resolve => {
                if (!name) return resolve(); const request = indexedDB.deleteDatabase(name);
                request.onsuccess = request.onerror = request.onblocked = () => resolve();
              })));
              if ('caches' in window) await Promise.all((await caches.keys()).map(name => caches.delete(name)));
            }""")
        page.goto(home_url, wait_until="domcontentloaded")
        bring_android_page_to_foreground(page)


def verify_visible_installed_home(page, screenshot_dir: Path | None = None) -> dict:
    """Validate static welcome artwork, semantic app version and safe centering."""
    home_url = f"http://127.0.0.1:{suite.PORT}/"
    if page.url != home_url:
        raise RuntimeError(
            "Para proteger una posible sesión intermedia, deja Gymratik en portada "
            "antes de iniciar el E2E físico; no navegaré la pestaña instalada."
        )
    try:
        foreground = bring_android_page_to_foreground(page)
        page.wait_for_function(
            "!document.documentElement.classList.contains('gymratik-loading') && getComputedStyle(document.querySelector('#appSplash')).visibility === 'hidden'",
            polling=250,
            timeout=60_000,
        )
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        page.wait_for_function("(() => { const hero=document.querySelector('.hero')?.getBoundingClientRect(); return hero && hero.top < innerHeight && hero.bottom > 0; })()")
        image = page.locator("#heroStrengthArt")
        page.wait_for_function(
            "element => element.complete && element.currentSrc.endsWith('gymratik-cover-seated-v1-poster.webp')",
            arg=image.element_handle(),
        )
        state = image.evaluate("""element => {
          const stage=element.parentElement.getBoundingClientRect();
          const box=element.getBoundingClientRect();
          const version=document.querySelector('.brand-version')?.textContent.trim() || '';
          return {loaded:element.complete,natural:[element.naturalWidth,element.naturalHeight],
            source:element.currentSrc,version,viewport:[innerWidth,innerHeight,devicePixelRatio],
            stage:[stage.left,stage.top,stage.right,stage.bottom],
            image:[box.left,box.top,box.right,box.bottom],
            stageOpacity:Number.parseFloat(getComputedStyle(element.parentElement).opacity),
            actionsTop:document.querySelector('.hero-actions').getBoundingClientRect().top};
        }""")
        if not state["loaded"] or state["natural"] != [372, 332]:
            raise AssertionError(f"La imagen estática de bienvenida no cargó completa en la PWA instalada: {state}")
        if not re.fullmatch(r"v\d+\.\d+\.\d+", state["version"]):
            raise AssertionError(f"La versión junto al nombre no es incremental/legible: {state['version']!r}")
        if state["stageOpacity"] < 0.68:
            raise AssertionError(f"La mascota de portada queda demasiado tenue: {state}")
        stage, box = state["stage"], state["image"]
        # El póster respira con un desplazamiento CSS de hasta ~2 px; tolerarlo
        # evita marcar ese movimiento deliberado como un recorte real del arte.
        if box[0] < stage[0] - 2.5 or box[1] < stage[1] - 2.5 or box[2] > stage[2] + 2.5 or box[3] > stage[3] + 2.5:
            raise AssertionError(f"La mascota de portada queda recortada o descentrada: {state}")
        if stage[3] > state["actionsTop"] + 1:
            raise AssertionError(f"La imagen de portada invade el área de los botones: {state}")
        source_before = image.evaluate("element => element.currentSrc")
        transform_before = image.evaluate("element => getComputedStyle(element).transform")
        page.wait_for_timeout(650)
        source_after = image.evaluate("element => element.currentSrc")
        transform_after = image.evaluate("element => getComputedStyle(element).transform")
        if source_before != source_after or not source_after.endswith("gymratik-cover-seated-v1-poster.webp"):
            raise AssertionError("La portada debe conservar el póster fijo")
        if transform_before == transform_after:
            raise AssertionError("El movimiento sutil de la portada instalada no avanza")
        if screenshot_dir:
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_dir / "00-home-cover-gt6.png"), full_page=False)
        state["welcomeMotion"] = "poster-fijo-con-deriva-css-sutil"
        state["centeredUncropped"] = True
        state["foregroundTimeline"] = foreground
        return state
    finally:
        page.evaluate("window.scrollTo({top:0,behavior:'instant'})")


def verify_installed_routine_covers(browser) -> list[dict]:
    """Load every routine cover on Android without entering the user's WebAPK data."""
    context = browser.new_context()
    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1', 'true')")
    page = context.new_page()
    results = []
    try:
        for day, (name, _sex, _variant) in enumerate(suite.ROUTINES, start=1):
            url = f"http://127.0.0.1:{suite.PORT}/data/rutinas_autocontenidas/canonicas/{name}"
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_selector(f'.routineDayCover[data-routine-cover="day{day}"] img')
            image = page.locator(f'.routineDayCover[data-routine-cover="day{day}"] img')
            page.wait_for_function(
                "element => element.complete && element.naturalWidth === 1536 && element.naturalHeight === 1024",
                arg=image.element_handle(),
            )
            state = image.evaluate("""element => {
              const frame=element.parentElement.getBoundingClientRect();
              const box=element.getBoundingClientRect();
              return {source:element.currentSrc,loaded:element.complete,
                natural:[element.naturalWidth,element.naturalHeight],
                fit:getComputedStyle(element).objectFit,
                frame:[frame.left,frame.top,frame.right,frame.bottom],
                image:[box.left,box.top,box.right,box.bottom]};
            }""")
            expected = f"/assets/branding/routine-covers/day{day}.webp"
            if not state["source"].endswith(expected) or state["fit"] != "contain":
                raise AssertionError(f"Portada incorrecta para el día {day}: {state}")
            frame, box = state["frame"], state["image"]
            if box[0] < frame[0] - 1 or box[1] < frame[1] - 1 or box[2] > frame[2] + 1 or box[3] > frame[3] + 1:
                raise AssertionError(f"Portada recortada/desbordada para el día {day}: {state}")
            results.append({"day": day, "source": state["source"], "loaded": state["loaded"], "fit": state["fit"]})
    finally:
        context.close()
    return results


def verify_visible_installed_splash_motion(page, screenshot_dir: Path | None = None) -> dict:
    """Show the loading state temporarily and verify the slow motion in the installed PWA."""
    reduced_motion = page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
    if screenshot_dir:
        screenshot_dir.mkdir(parents=True, exist_ok=True)
    try:
        foreground = bring_android_page_to_foreground(page)
        page.wait_for_function("""() => !document.documentElement.classList.contains('gymratik-loading')
          && document.querySelector('#appSplash')?.getAttribute('aria-hidden') === 'true'""", timeout=30_000)
        page.evaluate("""() => {
          document.documentElement.classList.add('gymratik-loading');
          document.querySelector('#appSplash')?.setAttribute('aria-hidden', 'false');
        }""")
        splash_image = page.locator("#splashPoseArt")
        if reduced_motion:
            page.wait_for_function(
            "element => element.complete && element.currentSrc.endsWith('gymratik-cover-seated-v1-poster.webp')",
                arg=splash_image.element_handle(),
            )
            return {"reducedMotion": True, "staticPosterHonored": True, "foregroundTimeline": foreground}
        page.wait_for_function(
            "element => element.complete && element.naturalWidth === 352 && getComputedStyle(element).visibility === 'visible' && element.currentSrc.endsWith('gymratik-cover-seated-breath-30fps.webp')",
            arg=splash_image.element_handle(),
        )
        first = splash_image.screenshot()
        page.wait_for_timeout(800)
        second = splash_image.screenshot()
        if first == second:
            raise AssertionError("La animación lenta de carga no avanzó en cuadros visibles en el GT6")
        if screenshot_dir:
            page.screenshot(path=str(screenshot_dir / "01-loading-slow-animation-gt6.png"), full_page=False)
        return {
            "reducedMotion": False,
            "source": splash_image.evaluate("element => element.currentSrc"),
            "framesAdvanceVisibly": True,
            "sampleIntervalMs": 800,
            "foregroundTimeline": foreground,
        }
    finally:
        page.evaluate("""() => {
          document.documentElement.classList.remove('gymratik-loading');
          document.querySelector('#appSplash')?.setAttribute('aria-hidden', 'true');
        }""")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cdp-url", required=True, help="endpoint CDP del Chrome Android reenviado por ADB")
    parser.add_argument("--width", type=int, help="ancho CSS; por defecto usa el viewport medido en el WebAPK")
    parser.add_argument("--height", type=int, help="alto CSS; por defecto usa el viewport medido en el WebAPK")
    parser.add_argument("--device-scale-factor", type=float, help="DPR; por defecto usa el valor medido en el WebAPK")
    parser.add_argument("--screenshot-dir", type=Path, help="carpeta para capturas del flujo móvil")
    parser.add_argument("--day", type=int, choices=range(1, 5), help="limita el E2E físico a un día para aislar carga en Chromium Android")
    parser.add_argument(
        "--low-memory-interactions",
        action="store_true",
        help="usa recursos ligeros para controles físicos en el origen localhost aislado; requiere --day",
    )
    parser.add_argument("--skip-offline", action="store_true", help="omite la prueba de service worker sin conexión")
    args = parser.parse_args()
    if args.low_memory_interactions and args.day is None:
        parser.error("--low-memory-interactions requiere --day para limitar la carga del GT6")

    report = {"status": "E2E_GT6_RUNNING"}
    if args.screenshot_dir:
        suite.SCREENSHOT_DIR = args.screenshot_dir
    with sync_playwright() as playwright:
        # No sobreescribir foco ni emulación multimedia del WebAPK del usuario.
        # Playwright advierte que connect_over_cdp es de menor fidelidad; los
        # contextos de prueba reciben sus opciones explícitas por separado.
        require_installed_webapk_foreground()
        cdp_websocket_url = resolve_cdp_websocket_url(args.cdp_url)
        browser = playwright.chromium.connect_over_cdp(cdp_websocket_url, no_defaults=True)
        installed_pages = [
            page
            for context in browser.contexts
            for page in context.pages
            if page.url.startswith(f"http://127.0.0.1:{suite.PORT}/")
        ]
        if not installed_pages:
            raise RuntimeError("No se encontró la PWA abierta en el WebAPK del teléfono")
        installed_page = installed_pages[0]
        installed_state = installed_page.evaluate("""() => ({
          standalone: matchMedia('(display-mode: standalone)').matches,
          viewport: [innerWidth, innerHeight, devicePixelRatio],
          serviceWorkerControlled: Boolean(navigator.serviceWorker?.controller),
          title: document.title
        })""")
        if not installed_state["standalone"]:
            raise RuntimeError(f"El target abierto no es la PWA instalada: {installed_state}")
        if not installed_state["serviceWorkerControlled"]:
            raise RuntimeError(f"La PWA instalada no está controlada por su service worker: {installed_state}")
        installed_state["foregroundTimeline"] = bring_android_page_to_foreground(installed_pages[0])

        installed_state["cacheName"] = installed_page.evaluate("""() => new Promise(resolve => {
          const worker=navigator.serviceWorker.controller;
          if(!worker){resolve(null);return;}
          const timer=setTimeout(()=>{navigator.serviceWorker.removeEventListener('message',receive);resolve(null)},3000);
          function receive(event){if(event.data?.type==='VERSION_STATUS'){clearTimeout(timer);navigator.serviceWorker.removeEventListener('message',receive);resolve(event.data.cacheName)}}
          navigator.serviceWorker.addEventListener('message',receive);
          worker.postMessage({type:'GET_VERSION_STATUS'});
        })""")
        local_worker = (suite.ROOT / "sw.js").read_text(encoding="utf-8")
        expected_match = re.search(r"const CACHE_NAME = '([^']+)';", local_worker)
        expected_cache = expected_match.group(1) if expected_match else None
        if not expected_cache or installed_state["cacheName"] != expected_cache:
            raise RuntimeError(
                "La PWA instalada aún no tiene el Service Worker de este build; "
                f"instalado={installed_state['cacheName']!r}, esperado={expected_cache!r}. "
                "Se detiene antes de probar una interfaz obsoleta."
            )
        if installed_page.url != f"http://127.0.0.1:{suite.PORT}/":
            raise RuntimeError(
                "Para proteger una posible sesión intermedia, deja Gymratik en portada "
                "antes de iniciar el E2E físico; no navegaré la pestaña instalada."
            )
        user_data_before = snapshot_installed_user_data(installed_page)

        width, height, scale = resolve_device_metrics(
            installed_state["viewport"], args.width, args.height, args.device_scale_factor
        )
        report["deviceViewport"] = [width, height, scale]
        report["installedPwa"] = installed_state

        original_goto = Page.goto

        test_origin = f"http://localhost:{suite.PORT}"
        home_url = f"http://127.0.0.1:{suite.PORT}/"
        map_test_origin = {"enabled": False}

        def android_goto(page, url, **options):
            # Los flujos de prueba usan localhost, distinto del origen instalado
            # 127.0.0.1. Así no comparten SW, IndexedDB ni storage con la sesión real.
            if map_test_origin["enabled"] and isinstance(url, str) and url.startswith(home_url):
                url = test_origin + url[len(f"http://127.0.0.1:{suite.PORT}"):]
            if options.get("wait_until") == "networkidle":
                options["wait_until"] = "domcontentloaded"
            virtual_time = getattr(page, "_gt6_virtual_time_session", None)
            if virtual_time is not None:
                virtual_time.send("Emulation.setVirtualTimePolicy", {"policy": "pauseIfNetworkFetchesPending"})
            try:
                return original_goto(page, url, **options)
            finally:
                if virtual_time is not None:
                    virtual_time.send("Emulation.setVirtualTimePolicy", {"policy": "pause"})

        Page.goto = android_goto
        isolated = PhysicalDeviceBrowser(
            browser, width, height, scale, reuse_page=installed_page,
            test_origin=test_origin, home_url=home_url, original_goto=original_goto,
        )
        original_locator_click = Locator.click
        original_locator_scroll = Locator.scroll_into_view_if_needed
        original_touch_hold = suite.dispatch_touch_hold
        original_performance_selector = suite.select_valid_performance

        def physical_locator_click(locator, *positional, **options):
            if positional or set(options) - {"timeout", "force", "no_wait_after"}:
                raise RuntimeError(f"Opción de click no compatible con el gesto táctil GT6: {positional}, {options}")
            android_tap(locator)

        def physical_locator_scroll(locator, *positional, **options):
            if positional or options:
                raise RuntimeError(f"Opción de scroll no compatible con el viewport GT6: {positional}, {options}")
            locator.evaluate("element => element.scrollIntoView({block:'center',inline:'nearest',behavior:'instant'})")
            locator.page.wait_for_timeout(120)

        Locator.click = physical_locator_click
        Locator.scroll_into_view_if_needed = physical_locator_scroll
        suite.dispatch_touch_hold = android_touch_hold
        suite.select_valid_performance = android_select_valid_performance
        print("GT6: portada y versión visibles en la PWA instalada", flush=True)
        visible_home = verify_visible_installed_home(installed_page, args.screenshot_dir)
        print("GT6: cuatro portadas específicas en la pestaña WebAPK (origen separado)", flush=True)
        map_test_origin["enabled"] = True
        installed_covers = verify_installed_routine_covers(isolated)
        map_test_origin["enabled"] = False
        print("GT6: animación lenta de carga/actualización en la PWA instalada", flush=True)
        bring_android_page_to_foreground(installed_page)
        visible_splash_motion = verify_visible_installed_splash_motion(installed_page, args.screenshot_dir)
        print("GT6: movimiento de mascota en la PWA instalada", flush=True)
        map_test_origin["enabled"] = True
        try:
            visible_mascot_motion = verify_visible_installed_mascot_motion(installed_page, args.screenshot_dir)
        finally:
            map_test_origin["enabled"] = False
            if installed_page.url != home_url:
                original_goto(installed_page, home_url, wait_until="domcontentloaded")
            bring_android_page_to_foreground(installed_page)
        map_test_origin["enabled"] = True
        results = []
        failures = []
        routines = [item for item in suite.ROUTINES if args.day is None or f"Dia_{args.day}_" in item[0]]
        for name, sex, variant in routines:
            print(f"GT6: rutina interactiva iniciada: {name}", flush=True)
            if args.low_memory_interactions:
                isolated.lightweight_assets = True
                try:
                    day = suite.validate_primary_set_buttons(isolated, name, sex)
                finally:
                    isolated.lightweight_assets = False
                day.update(suite.validate_completed_session_celebration(isolated, name, sex, variant))
                day["routine"] = name
                day["interactionAssetPolicy"] = "recursos visuales reales durante celebración; el subconjunto de controles no descargó medios animados"
                results.append(day)
                print(f"GT6: controles táctiles y celebración validados: {name}", flush=True)
                continue

            day = {"routine": name, "status": "failed", "phaseResults": {}}
            try:
                day.update(suite.validate_day(isolated, name, sex, variant))
                day["phaseResults"]["routineActivity"] = "passed"
                print(f"GT6: actividad, GIF y persistencia validados: {name}", flush=True)
            except Exception as error:
                message = f"{name} / rutina, actividad y recursos: {error}"
                failures.append(message)
                day["phaseResults"]["routineActivity"] = {"status": "failed", "error": str(error)}
                print(f"GT6: fallo registrado; continuaré con las demás fases y rutinas: {message}", flush=True)
            isolated.lightweight_assets = True
            try:
                button_results = suite.validate_primary_set_buttons(isolated, name, sex)
                day.update(button_results)
                day["phaseResults"]["buttonsAndSkips"] = "passed"
                exercise_count = day.get("exercises", button_results["primarySetButtonsTested"])
                if button_results["primarySetButtonsTested"] != exercise_count or button_results["exerciseSkipButtonsTested"] != exercise_count:
                    raise AssertionError(
                        f"cobertura incompleta: ejercicios={exercise_count}, "
                        f"botones dinámicos={button_results['primarySetButtonsTested']}, "
                        f"omisiones={button_results['exerciseSkipButtonsTested']}"
                    )
                print(f"GT6: botones dinámicos, series y omisiones validados en todos los ejercicios: {name}", flush=True)
            except Exception as error:
                message = f"{name} / botones y omisiones: {error}"
                failures.append(message)
                day["phaseResults"]["buttonsAndSkips"] = {"status": "failed", "error": str(error)}
                print(f"GT6: fallo registrado; continuaré con las demás fases y rutinas: {message}", flush=True)
            finally:
                isolated.lightweight_assets = False
            try:
                day.update(suite.validate_completed_session_celebration(isolated, name, sex, variant))
                day["phaseResults"]["celebration"] = "passed"
                print(f"GT6: celebración validada: {name}", flush=True)
            except Exception as error:
                message = f"{name} / celebración: {error}"
                failures.append(message)
                day["phaseResults"]["celebration"] = {"status": "failed", "error": str(error)}
                print(f"GT6: fallo registrado; continuaré con las demás rutinas: {message}", flush=True)
            day["status"] = "passed" if all(value == "passed" for value in day["phaseResults"].values()) else "failed"
            results.append(day)

        # En modo --day se limita la sesión física a una rutina para evitar
        # agotar el Chrome del teléfono. Estas comprobaciones transversales se
        # ejecutan en el E2E sintético, no se presentan como omitidas globalmente.
        if args.day is None:
            print("GT6: inventario de recursos y técnica visual", flush=True)
            try:
                resource_results = suite.validate_resource_pages(isolated)
            except Exception as error:
                resource_results = []
                failures.append(f"inventario de recursos/técnica: {error}")
            print("GT6: matriz de tamaños móviles", flush=True)
            # El GT6 se conserva en su geometría real; el barrido de breakpoints
            # se ejecuta en Chromium sintético y no se falsea mediante emulación.
            response_matrix = []
            print("GT6: tarjeta de citas", flush=True)
            try:
                physical_width = int(installed_state["viewport"][0])
                quote_result = suite.validate_motivation_card(isolated, widths=(physical_width,))
            except Exception as error:
                quote_result = {"status": "failed", "error": str(error)}
                failures.append(f"tarjeta de citas: {error}")
            shared_checks = "recursos y citas en GT6; matriz de breakpoints en E2E sintético"
        else:
            resource_results = []
            response_matrix = []
            quote_result = None
            shared_checks = "omitidos en modalidad --day; cubiertos por E2E sintético"
        print("GT6: paquete offline de la PWA instalada", flush=True)
        try:
            offline_result = None if args.skip_offline else suite.validate_installed_offline_package(isolated)
        except Exception as error:
            offline_result = {"status": "failed", "error": str(error)}
            failures.append(f"paquete offline: {error}")
        # All physical flows reuse the WebAPK tab on the isolated localhost
        # origin. Restore the installed origin before reading its data; never
        # compare a localhost test snapshot with the user's 127.0.0.1 profile.
        map_test_origin["enabled"] = False
        if installed_page.url.startswith(test_origin + "/"):
            installed_page.evaluate("""async () => {
              localStorage.clear(); sessionStorage.clear();
              if (typeof indexedDB.databases === 'function') {
                await Promise.all((await indexedDB.databases()).map(({name}) => new Promise(resolve => {
                  if (!name) return resolve();
                  const request = indexedDB.deleteDatabase(name);
                  request.onsuccess = request.onerror = request.onblocked = () => resolve();
                })));
              }
              if ('caches' in window) await Promise.all((await caches.keys()).map(name => caches.delete(name)));
            }""")
            original_goto(installed_page, home_url, wait_until="domcontentloaded")
            installed_page.wait_for_function(
                "!document.documentElement.classList.contains('gymratik-loading')",
                timeout=30_000,
            )
        installed_state["restoredForegroundTimeline"] = bring_android_page_to_foreground(installed_page)
        user_data_after = snapshot_installed_user_data(installed_page)
        if user_data_after["sha256"] != user_data_before["sha256"]:
            changed_stores = {
                category: sorted(
                    key for key in set(user_data_before["fingerprints"][category]) | set(user_data_after["fingerprints"][category])
                    if user_data_before["fingerprints"][category].get(key) != user_data_after["fingerprints"][category].get(key)
                )
                for category in ("localStorage", "sessionStorage", "indexedDB")
                if user_data_before["fingerprints"][category] != user_data_after["fingerprints"][category]
            }
            raise AssertionError(
                "El estado local real cambió durante el E2E; no se afirmará preservación "
                f"(antes={user_data_before['sha256'][:12]}, después={user_data_after['sha256'][:12]}, "
                f"categorías alteradas={changed_stores})."
            )

        report.update({
            "status": "E2E_GT6_OK" if not failures else "E2E_GT6_FAILED",
            "failures": failures,
            "installedPwa": installed_state,
            "installedHome": visible_home,
            "deviceRoutineCovers": installed_covers,
            "installedSplashMotion": visible_splash_motion,
            "visibleInstalledMascotMotion": visible_mascot_motion,
            "physicalInteractionIsolation": "Los gestos se probaron en la pestaña WebAPK real sobre localhost, origen distinto del 127.0.0.1 instalado; los datos instalados no se usaron.",
            "days": results,
            "resourcePages": len(resource_results),
            "responsiveViewports": len(response_matrix),
            "quoteFlow": quote_result,
            "sharedChecks": shared_checks,
            "offline": offline_result,
            "testDataIsolation": "Los flujos se ejecutaron en la pestaña WebAPK sobre el origen separado localhost; se restauró el origen instalado antes de comparar la huella SHA-256 de localStorage, sessionStorage e IndexedDB.",
            "userDataPreserved": {"sameSnapshot": True, "sha256": user_data_after["sha256"], "stores": user_data_after["indexedDbRecords"]},
        })
        print(json.dumps(report, ensure_ascii=True, indent=2))
        Locator.click = original_locator_click
        Locator.scroll_into_view_if_needed = original_locator_scroll
        suite.dispatch_touch_hold = original_touch_hold
        suite.select_valid_performance = original_performance_selector
        # No cerrar `browser`: pertenece al Chrome del usuario en el teléfono.
        if failures:
            return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # El error conservado indica la primera comprobación que no pasó.
        print(json.dumps({"status": "E2E_GT6_FAILED", "error": str(error)}, ensure_ascii=True, indent=2))
        raise
