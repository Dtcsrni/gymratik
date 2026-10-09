import json
import re
import unittest
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat
from scripts.build_pwa_service_worker import IMAGE_SUFFIXES, build_precache, resource_size


ROOT = Path(__file__).parents[1]
INDEX = ROOT / "index.html"
CANONICAL = ROOT / "data" / "rutinas_autocontenidas" / "canonicas"


class HomepageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))

    def test_public_brand_does_not_include_local(self):
        self.assertNotIn("Entrenamiento Local", self.html)
        self.assertEqual(self.manifest["id"], "./")
        self.assertEqual(self.manifest["name"], "Gymratik: Rutinas y progreso")
        self.assertEqual(self.manifest["short_name"], "Gymratik")
        self.assertIn("Gymratik: Rutinas y progreso", self.html)
        self.assertIn('aria-label="Gymratik v0.4.7, inicio"', self.html)
        self.assertIn('class="brand-version" aria-label="Versión 0.4.7">v0.4.7', self.html)
        self.assertIn('<span class="brand-mark" aria-hidden="true"><img src="./assets/branding/gymratik-mascots-mark-v2.png" alt=""></span>', self.html)
        self.assertIn("background:rgba(11,16,23,.72)", self.html)
        self.assertIn(".hero-strength-stage", self.html)
        self.assertNotIn("levantamientos de halterofilia", self.html)
        self.assertNotIn("Gymratic", self.html)
        self.assertNotIn("<title>Entrenamiento", self.html)

    def test_homepage_exposes_all_canonical_routines(self):
        routine_paths = (
            "Rutina_Dia_1_Espalda_Biceps_V1.html",
            "Rutina_Dia_2_Pierna_Gluteo_V1.html",
            "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html",
            "Rutina_Dia_4_Pierna_Equilibrio_V1.html",
        )
        for path in routine_paths:
            self.assertIn(path, self.html)

    def test_routine_names_describe_the_programmed_focus(self):
        for title in (
            "Tirón · espalda y bíceps",
            "Pierna · cuádriceps y glúteos",
            "Empuje · pecho, hombros y tríceps",
            "Pierna y core · cadera y estabilidad",
        ):
            self.assertIn(title, self.html)
        self.assertIn("routineId: 'day1'", self.html)
        self.assertIn("routineId: 'day4'", self.html)

    def test_homepage_summary_matches_all_four_routines(self):
        self.assertIn("Calienta, entrena con técnica y registra cada serie.", self.html)
        self.assertIn('<span class="plan-pill">4 días · 82 series</span>', self.html)
        self.assertIn('<div class="quick-stat"><strong>4</strong><span>sesiones para rotar</span></div>', self.html)
        self.assertIn('<div class="quick-stat"><strong>82</strong><span>series efectivas programadas</span></div>', self.html)
        self.assertIn('id="nextSessionTitle"', self.html)
        self.assertIn('href="#routines">Ver plan completo</a>', self.html)

    def test_homepage_uses_four_local_visual_references(self):
        image_paths = tuple(f"./assets/branding/routine-covers/day{day}.webp" for day in range(1, 5))
        for day, path in enumerate(image_paths, start=1):
            with self.subTest(path=path):
                self.assertEqual(self.html.count(path), 3 if day == 1 else 2)
                self.assertTrue((ROOT / path.removeprefix("./")).is_file())
        self.assertEqual(self.html.count('class="routine-card"'), 4)
        self.assertIn(".routine-visual img.routine-cover-art { box-sizing:border-box; object-fit:contain", self.html)
        self.assertIn(".routine-card:hover .routine-visual img:not(.routine-cover-art)", self.html)
        self.assertNotIn(".routine-card:hover .routine-visual img { transform:scale", self.html)
        self.assertIn("rgba(10,15,21,.24)", self.html)
        self.assertNotIn("Gymrats en pose", self.html)
        self.assertEqual(self.html.count("alt=\"Lámina anatómica:"), 5)
        self.assertIn(".next-session-image { display:block; width:100%; height:100%; min-height:264px; object-fit:contain", self.html)
        self.assertIn(".next-session-image { width:100%; height:clamp(142px,42vw,176px); min-height:0", self.html)
        self.assertIn("músculos trabajados en ${catalog.title}, destacados en rojo", self.html)

    def test_routine_cover_assets_keep_full_transparent_art_within_budget(self):
        for day in range(1, 5):
            path = ROOT / "assets" / "branding" / "routine-covers" / f"day{day}.webp"
            with self.subTest(day=day):
                self.assertLessEqual(path.stat().st_size, 450_000)
                with Image.open(path) as cover:
                    self.assertEqual(cover.size, (1536, 1024))
                    self.assertEqual(cover.mode, "RGBA")
                    self.assertLessEqual(cover.getchannel("A").getextrema()[0], 1)
                    red, green, blue = cover.convert("RGB").split()
                    red_emphasis = ImageChops.darker(
                        ImageChops.subtract(red, green),
                        ImageChops.subtract(red, blue),
                    ).point(lambda value: 255 if value > 32 else 0)
                    cyan_emphasis = ImageChops.darker(
                        ImageChops.subtract(green, red),
                        ImageChops.subtract(blue, red),
                    ).point(lambda value: 255 if value > 32 else 0)
                    self.assertGreater(sum(red_emphasis.histogram()[1:]), 20_000)
                    self.assertLess(sum(cyan_emphasis.histogram()[1:]), 500)

    def test_pwa_icon_is_dedicated_transparent_mark_with_maskable_variants(self):
        declared_sizes = {"any": set(), "maskable": set()}
        for icon in self.manifest["icons"]:
            with self.subTest(icon=icon):
                icon_path = ROOT / icon["src"].removeprefix("./")
                data = icon_path.read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(icon["type"], "image/png")
                self.assertIn(icon["purpose"], declared_sizes)
                self.assertTrue(icon_path.name.startswith("gymratik-pwa-icon-v8-"))
                self.assertLess(icon_path.stat().st_size, 500_000)
                with Image.open(icon_path) as mark:
                    self.assertEqual(icon["sizes"], f"{mark.width}x{mark.height}")
                    self.assertEqual(mark.width, mark.height)
                    self.assertLessEqual(mark.getchannel("A").getextrema()[0], 1)
                    self.assertEqual(mark.getchannel("A").getpixel((0, 0)), 0)
                    if icon["purpose"] == "maskable":
                        safe_zone = Image.new("L", mark.size, 0)
                        ImageDraw.Draw(safe_zone).ellipse(
                            (
                                mark.width * 0.1,
                                mark.height * 0.1,
                                mark.width * 0.9,
                                mark.height * 0.9,
                            ),
                            fill=255,
                        )
                        outside_safe_zone = ImageChops.multiply(
                            mark.getchannel("A"), ImageChops.invert(safe_zone)
                        )
                        self.assertLessEqual(outside_safe_zone.getextrema()[1], 8)
                    declared_sizes[icon["purpose"]].add(mark.size)
        self.assertEqual(declared_sizes["any"], {(192, 192), (512, 512)})
        self.assertEqual(declared_sizes["maskable"], {(192, 192), (512, 512)})
        self.assertIn('href="./assets/branding/gymratik-pwa-icon-v8-192.png"', self.html)
        self.assertIn('href="./assets/branding/gymratik-mascots-mark-v2.png"', self.html)

    def test_pwa_precache_derives_installed_icons_from_manifest(self):
        from scripts.build_pwa_service_worker import build_precache

        resources = set(build_precache())
        worker = (ROOT / "sw.js").read_text(encoding="utf-8")
        for icon in self.manifest["icons"]:
            with self.subTest(icon=icon["src"]):
                self.assertIn(icon["src"], resources)
                self.assertIn(icon["src"].removeprefix("./"), worker)

    def test_homepage_checks_for_service_worker_updates_on_open(self):
        self.assertIn("updateViaCache: 'none'", self.html)
        self.assertIn("registration.update()", self.html)
        self.assertNotIn("updateInstallVisibility", self.html)
        self.assertNotIn("SYNC_APP", self.html)
        self.assertIn("event.data?.type === 'APP_UPDATED'", self.html)
        self.assertIn("navigator.serviceWorker?.addEventListener('message'", self.html)
        self.assertIn("registration.waiting.postMessage({ type: 'ACTIVATE_UPDATE' })", self.html)
        self.assertIn("SYNC_TIMEOUT_MS = 20000", self.html)
        self.assertIn('name="gymratik-resource-estimate"', self.html)
        self.assertIn("applicationBytes", self.html)
        self.assertIn("imageBytes", self.html)

    def test_network_defer_reason_distinguishes_cellular_from_data_saver(self):
        self.assertIn("const isCellular = connectionType === 'cellular';", self.html)
        self.assertIn("const isDataSaver = navigator.connection?.saveData === true;", self.html)
        self.assertIn(": isDataSaver\n              ? 'está activado el ahorro de datos'", self.html)

    def test_install_size_estimate_matches_the_generated_offline_package(self):
        match = re.search(r'<meta name="gymratik-resource-estimate" content=\'([^\']+)\'>', self.html)
        self.assertIsNotNone(match)
        estimate = json.loads(match.group(1))
        package = {
            resource: resource_size(ROOT / Path(resource.removeprefix("./")))
            for resource in build_precache()
        }
        package["./sw.js"] = resource_size(ROOT / "sw.js")
        actual_images = sum(size for resource, size in package.items() if Path(resource).suffix.lower() in IMAGE_SUFFIXES)
        actual_total = sum(package.values())
        self.assertEqual(int(estimate["totalBytes"]), actual_total)
        self.assertEqual(int(estimate["imageBytes"]), actual_images)
        self.assertEqual(int(estimate["applicationBytes"]), actual_total - actual_images)

    def test_cellular_update_is_temporarily_forced_and_detected_version_uses_the_mascot_animation(self):
        self.assertIn('id="updateNotice" class="update-notice"', self.html)
        self.assertIn('id="updateNoticeArt"', self.html)
        self.assertIn('id="manualUpdateButton"', self.html)
        self.assertIn('data-motion-src="./assets/branding/gymratik-cover-seated-breath-30fps.webp"', self.html)
        self.assertIn("connectionType === 'cellular'", self.html)
        self.assertIn("preference === 'always' || isWifi", self.html)
        self.assertIn("networkPreference.value = 'always';", self.html)
        self.assertIn("networkPreference.disabled = true;", self.html)
        self.assertNotIn("preference === 'ask' && !isCellular", self.html)
        self.assertIn("(!firstInstall && isManualReload)", self.html)
        self.assertIn("consumeManualUpdateRequest()", self.html)
        self.assertIn("MANUAL_UPDATE_REQUEST_TTL_MS", self.html)
        self.assertIn("showDeferredUpdateNotice(waitingAtOpen || installInProgress, waitingAtOpen, deferredNetworkReason)", self.html)
        self.assertIn("showUpdateDetectedAnimation()", self.html)
        self.assertIn("if (!document.documentElement.classList.contains('gymratik-loading'))", self.html)
        self.assertIn("updateNotice.dataset.detected = 'true'", self.html)
        self.assertIn("Actualización automática temporalmente habilitada también con datos móviles.", self.html)
        self.assertIn(".app-splash.update-detected .splash-mascot-poses", self.html)
        self.assertIn("prefers-reduced-motion:reduce", self.html)

    def test_browser_context_invites_installation_and_hides_profile_and_history(self):
        self.assertTrue((ROOT / "install-gate.js").is_file())
        self.assertIn('src="./install-gate.js"', self.html)
        self.assertIn("data-gymratik-installed=\"false\"", self.html)
        gate = (ROOT / "install-gate.js").read_text(encoding="utf-8")
        self.assertIn("Lleva Gymratik contigo", gate)
        self.assertIn("mascot-install-phone.webp", gate)
        self.assertIn("invite.showModal()", gate)
        self.assertIn("#gymratikInstallInvite:not([open]){display:none!important}", gate)
        self.assertIn("font-size:clamp(31px,8vw,40px)", gate)
        self.assertIn("display-mode: standalone", gate)
        self.assertIn("window.navigator.standalone === true", gate)
        self.assertIn("tracker.inert = !installed", gate)
        for selector in ('#progress', '#progress-detail', '#profile', '.profile-chip', '.footer-actions'):
            with self.subTest(selector=selector):
                self.assertIn(f'html[data-gymratik-installed="false"] {selector}', self.html)
        self.assertIn('aria-label="Cerrar invitación y continuar"', (ROOT / "install-gate.js").read_text(encoding="utf-8"))
        self.assertIn("window.addEventListener('appinstalled'", (ROOT / "install-gate.js").read_text(encoding="utf-8"))

    def test_homepage_shows_last_successful_update(self):
        self.assertIn('id="updateState"', self.html)
        self.assertIn('Aplicación y recursos offline actualizados:', self.html)
        self.assertIn('Aplicación y recursos offline: comprobando actualización…', self.html)
        self.assertIn("gymratik-last-update-v1", self.html)
        self.assertNotIn('id="connectionState"', self.html)
        self.assertNotIn('Conectado', self.html)

    def test_homepage_keeps_mobile_hero_content_inside_the_viewport(self):
        self.assertIn('.hero > * { min-width:0; }', self.html)
        self.assertIn('overflow-wrap:anywhere', self.html)
        self.assertIn('.next-session-card { grid-template-columns:minmax(0,1fr); gap:10px; }', self.html)
        self.assertIn('h1 { max-width:100%; font-size:clamp(2.8rem,14vw,5.2rem); }', self.html)

    def test_homepage_shows_a_brief_splash_until_local_data_initialization_settles(self):
        self.assertIn("document.documentElement.classList.add('gymratik-loading')", self.html)
        self.assertIn('id="appSplash" class="app-splash" role="status"', self.html)
        self.assertIn('class="splash-mascot-poses" aria-hidden="true"', self.html)
        self.assertIn('id="splashPoseArt" class="splash-pose"', self.html)
        self.assertIn('data-motion-src="./assets/branding/gymratik-cover-seated-breath-30fps.webp"', self.html)
        self.assertIn('src="./assets/branding/gymratik-cover-seated-v1-poster.webp"', self.html)
        self.assertIn("Leyendo el avance guardado", self.html)
        self.assertIn('html.gymratik-loading .app-splash', self.html)
        self.assertIn('.app-splash[aria-hidden="true"] { opacity:0!important; visibility:hidden!important; pointer-events:none!important; transition:none!important; }', self.html)
        self.assertIn("document.documentElement.classList.remove('gymratik-loading')", self.html)
        self.assertIn("await networkDecisionPhase", self.html)
        self.assertIn("if (!navigator.serviceWorker?.controller) await syncTask", self.html)
        self.assertNotIn("await Promise.all([localInitialization, syncTask])", self.html)
        self.assertIn("1000 - (performance.now() - start)", self.html)
        self.assertIn('id="splashRetry"', self.html)
        self.assertIn("Tus datos permanecen en este dispositivo", self.html)
        self.assertIn("setAttribute('aria-hidden', 'true')", self.html)
        self.assertIn("@media (prefers-reduced-motion:reduce)", self.html)

    def test_loading_states_have_motion_and_do_not_stick_when_history_is_unavailable(self):
        self.assertIn('class="session-history-empty" data-loading="true" aria-busy="true">Cargando historial…', self.html)
        self.assertIn(".session-history-empty[data-loading=\"true\"]::after", self.html)
        self.assertIn("animation:historyLoadingRhythm 1.15s ease-in-out infinite", self.html)
        self.assertIn("@keyframes historyLoadingRhythm", self.html)
        refresh = self.html.split("async function refreshProfile()", 1)[1].split("async function refreshProgress()", 1)[0]
        self.assertIn("Instala Gymratik para guardar y consultar tus sesiones.", refresh)
        self.assertNotIn("Cargando historial…", refresh)

    def test_network_permission_is_explained_and_chosen_inside_the_splash(self):
        self.assertIn('id="splashNetworkActions"', self.html)
        self.assertIn('id="splashAllowNetwork"', self.html)
        self.assertIn('id="splashSkipNetwork"', self.html)
        self.assertIn("function requestNetworkPermission(message, sizeNote)", self.html)
        self.assertIn("No se descargará nada hasta que elijas una opción.", self.html)
        self.assertIn("allowed = await requestNetworkPermission(", self.html)
        self.assertIn("if (!allowed) {", self.html)
        self.assertIn("primera vez.", self.html)

    def test_detected_pwa_updates_activate_automatically_on_allowed_networks(self):
        self.assertIn("preference === 'always' || isWifi", self.html)
        self.assertNotIn("preference === 'ask' && !isCellular", self.html)
        self.assertIn("networkUpdateDeferred", self.html)
        self.assertIn("no se pudo confirmar Wi‑Fi", self.html)
        self.assertIn("preference === 'always'", self.html)
        self.assertIn("registration.waiting.postMessage({ type: 'ACTIVATE_UPDATE' })", self.html)
        self.assertIn("Actualización completa detectada; se está aplicando automáticamente.", self.html)
        self.assertNotIn("if (waitingAtOpen || isManualReload)", self.html)
        self.assertLess(self.html.index("if (!allowed) {"), self.html.index("if (registration.waiting) {", self.html.index("const updateResult")))
        self.assertNotIn("se aplicará al abrir Gymratik de nuevo", self.html)
        self.assertIn("se instalará automáticamente al tener Wi‑Fi", self.html)
        self.assertIn("arrastra hacia abajo desde el borde superior", self.html)

    def test_homepage_prioritizes_next_session_and_gym_flow(self):
        self.assertIn('id="pageTitle">Empieza a tu ritmo.', self.html)
        self.assertIn('id="nextSessionCta"', self.html)
        self.assertIn('id="nextSessionLink"', self.html)
        self.assertIn('function renderNextSession', self.html)
        self.assertIn("pageTitle.textContent = continuing", self.html)
        self.assertIn("? 'Retoma tu sesión.'", self.html)
        self.assertIn("? 'Hoy ya avanzaste.'", self.html)
        self.assertIn("`Sigue con ${catalog.day}.`", self.html)
        self.assertIn('Continúa donde te quedaste', self.html)
        self.assertIn('Calentamiento incluido', self.html)
        self.assertIn('Tres pasos y a entrenar.', self.html)
        self.assertIn('Mi avance', self.html)
        self.assertIn('Proteger avance', self.html)

    def test_homepage_has_subtle_poster_drift_and_splash_uses_a_slow_closed_30fps_loop(self):
        self.assertIn('class="hero-strength-stage" aria-hidden="true"', self.html)
        self.assertIn('id="heroStrengthArt" class="hero-strength-art"', self.html)
        self.assertIn('id="splashPoseArt"', self.html)
        self.assertIn('src="./assets/branding/gymratik-cover-seated-v1-poster.webp" alt="" width="372" height="332" fetchpriority="high"', self.html)
        self.assertEqual(self.html.count('data-motion-src="./assets/branding/gymratik-cover-seated-breath-30fps.webp"'), 2)
        self.assertIn("setCoverArtPlayback(splashPoseArt, pageVisible && splashVisible)", self.html)
        self.assertNotIn("setCoverArtPlayback(heroStrengthArt", self.html)
        self.assertNotIn("new IntersectionObserver", self.html)
        self.assertIn("animation:coverArtDrift 24s ease-in-out infinite alternate", self.html)
        self.assertIn("@keyframes coverArtDrift", self.html)
        self.assertIn("setCoverArtPlayback", self.html)
        self.assertIn("reducedMotionQuery.matches", self.html)
        self.assertIn("document.visibilityState === 'visible'", self.html)
        self.assertIn("new MutationObserver(syncCoverArtMotion)", self.html)
        self.assertIn("@media (prefers-reduced-motion:reduce)", self.html)
        self.assertIn(".hero-strength-stage { position:absolute; z-index:0; inset:0 0 auto; height:min(100%,430px);", self.html)
        self.assertIn("opacity:.88;", self.html)
        self.assertIn("height:clamp(220px,44vw,300px); opacity:.78", self.html)
        self.assertIn("height:clamp(215px,64vw,290px); opacity:.72", self.html)
        self.assertIn("height:clamp(215px,64vw,290px)", self.html)
        self.assertIn("margin:auto; aspect-ratio:3/2; object-fit:contain; object-position:center", self.html)
        source = ROOT / "assets/branding/gymratik-cover-seated-v1-source.png"
        self.assertTrue(source.is_file(), "La fuente original debe seguir disponible para edición en Krita")
        animation = ROOT / "assets/branding/gymratik-cover-seated-breath-30fps.webp"
        poster = ROOT / "assets/branding/gymratik-cover-seated-v1-poster.webp"
        self.assertTrue(animation.is_file())
        self.assertTrue(poster.is_file())
        self.assertLess(animation.stat().st_size, 3_000_000, "La animación de carga debe seguir comprimida para red móvil")
        with Image.open(poster) as cover:
            self.assertEqual(cover.n_frames, 1, "La portada debe ser una imagen estática")
            self.assertEqual(cover.size, (372, 332))
            self.assertEqual(cover.mode, "RGBA")
            self.assertEqual(cover.getchannel("A").getextrema()[0], 0)
        with Image.open(animation) as image:
            self.assertEqual(image.format, "WEBP")
            self.assertGreaterEqual(image.n_frames, 180, "El ciclo lento debe mantener suficientes fotogramas")
            self.assertEqual(image.info.get("loop"), 0, "El loop debe repetirse sin límite")
            image.seek(0)
            start = image.convert("RGBA")
            self.assertEqual(start.size, (352, 314))
            self.assertEqual(start.getpixel((0, 0))[3], 0)
            image.seek(1)
            self.assertEqual(image.info.get("duration"), 33, "La reproducción debe codificarse a 30 fps")
            frame_durations = []
            for index in range(image.n_frames):
                image.seek(index)
                frame_durations.append(image.info.get("duration", 0))
            cycle_ms = sum(frame_durations)
            self.assertGreaterEqual(cycle_ms, 6_000, "La bienvenida animada debe moverse despacio")
            self.assertLessEqual(cycle_ms / image.n_frames, 34, "El movimiento debe conservar al menos 29 fps")
            image.seek(image.n_frames - 1)
            end = image.convert("RGBA")
            loop_error = ImageStat.Stat(ImageChops.difference(start.convert("RGB"), end.convert("RGB"))).mean
            self.assertLess(sum(loop_error) / len(loop_error), 2.0, "El cierre del bucle no debe producir un salto visible")
            for index in range(image.n_frames):
                image.seek(index)
                alpha = image.convert("RGBA").getchannel("A")
                bounds = alpha.getbbox()
                self.assertIsNotNone(bounds)
                safe_x = round(image.width * 0.05)
                safe_y = round(image.height * 0.05)
                self.assertGreaterEqual(bounds[0], safe_x)
                self.assertGreaterEqual(bounds[1], safe_y)
                self.assertLessEqual(bounds[2], image.width - safe_x)
                self.assertLessEqual(bounds[3], image.height - safe_y)
            image.seek(image.n_frames // 2)
            middle = image.convert("RGBA")
            breathing_change = ImageChops.difference(start, middle)
            self.assertIsNotNone(breathing_change.crop((65, 65, 282, 236)).getbbox(), "La deformación local debe mover el torso al respirar")
        self.assertNotIn("gymratik-machine-sprite.webp", self.html)
        self.assertNotIn("@keyframes coverPoseOne", self.html)
        self.assertNotIn("@keyframes coverPoseTwo", self.html)
        self.assertNotIn("weightlifting-v2.webp", self.html)
        self.assertIn("elapsedDays === 2 ? 'antier'", self.html)
        self.assertIn('`el ${weekday} pasado`', self.html)
        self.assertIn('activityWeekStart < currentWeekStart', self.html)
        self.assertIn('width:62px; height:62px; flex:0 0 62px', self.html)
        self.assertIn('font-size:1.25rem', self.html)
        self.assertIn('font-size:1.15rem', self.html)
        self.assertNotIn('class="hero-mascot-bg" src="./data/profile/mascot-install-phone.webp"', self.html)

    def test_homepage_exposes_persistent_progress_dashboard(self):
        self.assertIn('src="./progress-store.js"', self.html)
        self.assertIn('progressRecordedSeries', self.html)
        self.assertIn('progressTodaySeries', self.html)
        self.assertIn('TrainingProgressStore', self.html)
        self.assertIn('persistButton', self.html)
        self.assertIn('id="resetAllButton"', self.html)
        self.assertIn('clearAll()', self.html)

    def test_homepage_selects_active_session_or_next_routine_from_latest_activity(self):
        next_session = self.html.split('function renderNextSession', 1)[1].split('function renderProgress', 1)[0]
        self.assertIn('activeToday', next_session)
        self.assertIn('progressIsNewer', next_session)
        self.assertIn('(byId.get(latestRoutineId) + 1) % routineCatalog.length', next_session)
        self.assertIn('const dashboard = await window.TrainingProgressStore.getDashboard();', self.html)
        self.assertIn('const history = await window.TrainingProgressStore.getHistory(100);', self.html)

    def test_homepage_exposes_local_profile_and_backup_controls(self):
        for marker in (
            'id="profile"',
            'id="profileBirthDate"',
            'id="profileSex"',
            'id="profileHeightCm"',
            'id="profileGoal"',
            'id="profileUnits"',
            'name="reminderDay"',
            'id="remindersEnabled"',
            'id="routineDaySuggestion"',
            'id="routineReminder"',
            'El aviso solo aparece al abrir o volver a la portada',
            'commonTrainingDays(history)',
            'session.warmupCompleted === true && Number(session.completedSeries) > 0',
            '56 * MILLISECONDS_PER_DAY',
            'updateHomeMotivation(activeProfile?.displayName',
            'id="exportDataButton"',
            'id="importDataInput"',
            'id="sessionHistory"',
            'saveProfile',
            'getHistory',
            'Exportar datos',
            'Importar respaldo',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.html)

    def test_initial_profile_form_is_progressive_and_optional(self):
        quick_fields = self.html[
            self.html.index('<div class="profile-grid">', self.html.index('id="profileForm"')):
            self.html.index('<details class="profile-extra">', self.html.index('id="profileForm"'))
        ]
        self.assertIn('¿Cómo te llamamos?', quick_fields)
        self.assertIn('Sexo, solo para elegir la mascota', quick_fields)
        self.assertIn('id="profileSex"', quick_fields)
        self.assertNotIn('id="profileBirthDate"', quick_fields)
        self.assertNotIn('id="profileHeightCm"', quick_fields)
        self.assertIn('<summary>Personalizar más (opcional)</summary>', self.html)
        self.assertIn('id="profileEditorSummary"', self.html)
        self.assertIn('profileConfigured ? \'Editar datos del perfil\' : \'Completar perfil\'', self.html)
        self.assertIn('Aún no hay datos que guardar.', self.html)
        self.assertIn('if (!profileIsDefined)', self.html)
        self.assertIn('profileEditor.open = true', self.html)

    def test_profile_editor_closes_and_page_reloads_after_successful_save(self):
        self.assertIn('<details id="profileEditor" class="profile-editor">', self.html)
        self.assertIn('<summary id="profileEditorSummary">Completar perfil</summary>', self.html)
        self.assertIn("profileEditor.open = true", self.html)
        save_handler = self.html.split("profileForm.addEventListener('submit'", 1)[1].split("profileSex.addEventListener", 1)[0]
        save_profile = save_handler.index('await window.TrainingProgressStore.saveProfile')
        close_editor = save_handler.index('profileEditor.open = false')
        reload_page = save_handler.index('reloadPageOnce()')
        self.assertLess(save_profile, close_editor)
        self.assertLess(close_editor, reload_page)

    def test_homepage_debounces_page_reloads_and_omits_generic_section_descriptions(self):
        self.assertIn('PAGE_RELOAD_GUARD_MS = 4000', self.html)
        self.assertIn('sessionStorage.getItem(PAGE_RELOAD_GUARD_KEY)', self.html)
        self.assertIn("addEventListener('controllerchange', reloadPageOnce)", self.html)
        for phrase in (
            'La portada te acompaña sin pedirte que prepares nada antes de salir.',
            'Lo que llevas registrado en este dispositivo, actualizado al abrir la portada.',
            'Consulta el avance de cada rutina. El progreso permanece en este dispositivo.',
            'Elige una sesión para ver ejercicios, descansos, técnica y controles de registro.',
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.html)

    def test_homepage_derives_effort_mascot_from_profile_sex(self):
        for asset in ("data/profile/mouse-female-effort.webp", "data/profile/mouse-male-effort.webp"):
            with self.subTest(asset=asset):
                self.assertTrue((ROOT / asset).is_file())
                image = (ROOT / asset).read_bytes()
                self.assertEqual(image[:4], b"RIFF")
                self.assertEqual(image[8:12], b"WEBP")
        self.assertIn("female: { src: './data/profile/mouse-female-effort.webp'", self.html)
        self.assertIn("male: { src: './data/profile/mouse-male-effort.webp'", self.html)
        self.assertIn("return profileAvatars[sex] || profileAvatars.neutral;", self.html)
        self.assertIn("profileSex.addEventListener('change', () => renderProfileAvatar(profileSex.value));", self.html)
        self.assertIn("alt: 'Ratona haciendo press con mancuerna, con expresión de esfuerzo'", self.html)
        self.assertIn("alt: 'Ratón haciendo press con mancuerna, con expresión de esfuerzo'", self.html)

    def test_homepage_places_recorded_statistics_below_start(self):
        hero_end = self.html.index('</section>', self.html.index('<section class="hero"'))
        stats_start = self.html.index('<section id="progress" class="recorded-summary"')
        self.assertGreater(stats_start, hero_end)
        self.assertIn('Estadísticas registradas', self.html)
        self.assertIn('series de hoy', self.html)
        self.assertIn('sesiones completas', self.html)

    def test_homepage_exposes_explicit_reset_at_bottom(self):
        self.assertIn('id="resetAllButton"', self.html)
        self.assertIn('Reiniciar registros', self.html)
        self.assertIn('Se borrarán sesiones, series y actividad', self.html)

    def test_homepage_normalizes_partial_dashboard_data(self):
        self.assertIn('function normalizeDashboard', self.html)
        self.assertIn('fallbackRoutineProgress', self.html)
        self.assertIn('Array.isArray(source.routines)', self.html)
        self.assertIn('String(dashboard.todaySeries)', self.html)
        self.assertIn("source.temporal?.sameMinute === true", self.html)

    def test_homepage_reloads_after_service_worker_controller_change(self):
        self.assertIn("addEventListener('controllerchange'", self.html)
        self.assertIn("addEventListener('controllerchange', reloadPageOnce)", self.html)
        self.assertIn('window.location.reload()', self.html)

    def test_homepage_is_offline_first_without_manual_preparation_prompt(self):
        self.assertNotIn('Prepáralo antes de salir', self.html)
        self.assertNotIn('Preparar sesiones', self.html)
        self.assertNotIn('cacheButton', self.html)
        self.assertNotIn('prepareOffline', self.html)

    def test_homepage_exposes_liquid_glass_accessibility_redesign(self):
        self.assertIn('data-redesign="liquid-glass-wcag-v13"', self.html)
        self.assertIn('backdrop-filter:blur(18px) saturate(145%)', self.html)
        self.assertIn('#ffd166', self.html)
        self.assertIn('@media (prefers-reduced-motion:reduce)', self.html)

    def test_canonical_routines_use_distinct_progress_storage_keys(self):
        keys = []
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            marker = "const storageKey = '"
            start = source.index(marker) + len(marker)
            keys.append(source[start:source.index("'", start)])
        self.assertEqual(len(keys), 4)
        self.assertEqual(len(set(keys)), 4)
        self.assertIn("day1", keys[0])
        self.assertIn("day2", keys[1])
        self.assertIn("day3", keys[2])
        self.assertIn("day4", keys[3])

    def test_canonical_routines_publish_progress_to_shared_store(self):
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            self.assertIn('src="../../../progress-store.js"', source)
            self.assertIn('src="../../../install-gate.js"', source)
            self.assertIn('TrainingProgressStore?.capture', source)
            self.assertIn("if (!window.GymratikInstallGate?.isInstalled()) return;", source)
            self.assertIn("const saved = window.GymratikInstallGate?.isInstalled() ?", source)
            self.assertIn("if (window.GymratikInstallGate?.isInstalled() && window.TrainingProgressStore?.getHistory)", source)

    def test_routine_performance_uses_clear_sliders_and_preserves_pound_reference(self):
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(routine=path.name):
                self.assertIn("repsInput.type = 'range'", source)
                self.assertIn("loadInput.type = 'range'", source)
                self.assertIn("Repeticiones realizadas", source)
                self.assertIn("value === 'kg' ? 'Kilogramos' : 'Libras'", source)
                self.assertIn("loadKg", source)
                self.assertIn("'repeticiones'", source)
                self.assertNotIn(" rep.", source)
                self.assertNotIn("reps de esta serie", source.lower())
                self.assertNotIn("performanceReps'; repsInput.type = 'number'", source)
                self.assertNotIn("performanceLoad'; loadInput.type = 'number'", source)

    def test_homepage_animates_motivation_and_entrance_with_reduced_motion_support(self):
        for marker in (
            "@keyframes homeArrive",
            "@keyframes motivationArrive",
            "@keyframes motivationRefresh",
            "@keyframes mascotDrift",
            "@keyframes cardArrive",
            "function updateHomeMotivation(message)",
            "prefers-reduced-motion:reduce",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.html)

    def test_routine_celebrations_and_motivation_are_event_based_and_motion_safe(self):
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(routine=path.name):
                self.assertIn('data-enhancement="motivational-celebrations-v1"', source)
                self.assertIn('id = \'gymratikEncouragement\'', source)
                self.assertIn("role', 'status'", source)
                self.assertIn("Ejercicio terminado. Un paso más", source)
                self.assertIn("¡Sesión completada! Buen trabajo", source)
                self.assertIn("Calentamiento listo.", source)
                self.assertIn("celebrate(completionPanel, 38)", source)
                self.assertIn("prefers-reduced-motion:reduce", source)
                self.assertIn("toastMascot.className = 'toastMascot'", source)
                self.assertIn("toastCopy.textContent = message", source)
                self.assertIn("${variant}-approval.png", source)
                self.assertIn("}, 5200);", source)
                self.assertIn("animation:mascotToastApproval 1.4s", source)

    def test_profile_and_progress_reads_are_gated_by_installation(self):
        self.assertIn("if (!window.GymratikInstallGate?.isInstalled() || !window.TrainingProgressStore)", self.html.split("async function refreshProfile()", 1)[1])
        self.assertIn("async function refreshProgress() {\n      if (!window.GymratikInstallGate?.isInstalled()) return;", self.html)

    def test_day1_replaces_cross_day_duplicate_media_id(self):
        day1 = json.loads((ROOT / "data/rutinas_autocontenidas/evidencia/dia1_media_manifest.json").read_text(encoding="utf-8"))
        day3 = json.loads((ROOT / "data/rutinas_autocontenidas/evidencia/dia3_media_manifest.json").read_text(encoding="utf-8"))
        day1_ids = {item["dataset_id"] for item in day1["items"]}
        day3_ids = {item["repo_id"] for item in day3}
        self.assertIn("0575", day1_ids)
        self.assertNotIn("0577", day1_ids)
        self.assertIn("0577", day3_ids)
        self.assertTrue(day1_ids.isdisjoint(day3_ids))


if __name__ == "__main__":
    unittest.main()
