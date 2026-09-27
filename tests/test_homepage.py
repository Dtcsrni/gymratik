import json
import unittest
from pathlib import Path


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
        self.assertIn('aria-label="Gymratik, inicio"', self.html)
        self.assertIn('<span class="brand-mark" aria-hidden="true"><img src="./icon.png" alt=""></span>', self.html)
        self.assertIn("background:rgba(11,16,23,.72)", self.html)
        self.assertIn(".hero-mascot-bg", self.html)
        self.assertIn('class="hero-mascot-bg" src="./icon.png"', self.html)
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

    def test_homepage_summary_matches_all_four_routines(self):
        self.assertIn("Calienta, entrena con técnica y registra cada serie.", self.html)
        self.assertIn('<span class="plan-pill">4 días · 82 series</span>', self.html)
        self.assertIn('<div class="quick-stat"><strong>4</strong><span>sesiones para rotar</span></div>', self.html)
        self.assertIn('<div class="quick-stat"><strong>82</strong><span>series efectivas programadas</span></div>', self.html)
        self.assertIn('id="nextSessionTitle"', self.html)
        self.assertIn('href="#routines">Ver plan completo</a>', self.html)

    def test_homepage_uses_four_local_visual_references(self):
        image_paths = (
            "1350-7I6LNUG.jpg",
            "0739-10Z2DXU.jpg",
            "0577-T0yTjgW.jpg",
            "2287-V07qpXy.jpg",
        )
        for path in image_paths:
            self.assertIn(path, self.html)
        self.assertEqual(self.html.count('class="routine-card"'), 4)

    def test_pwa_icon_is_the_mascot_png_and_maskable_manifest_entry(self):
        icon = (ROOT / "icon.png").read_bytes()
        self.assertEqual(icon[:8], b"\x89PNG\r\n\x1a\n")
        self.assertNotIn(b"Gymratic", icon)
        self.assertNotIn(b"Entrenamiento Local", icon)
        self.assertEqual(self.manifest["icons"][0]["src"], "./icon.png")
        self.assertEqual(self.manifest["icons"][0]["type"], "image/png")
        self.assertEqual(self.manifest["icons"][0]["purpose"], "any maskable")
        self.assertTrue((ROOT / "icon.png").is_file())

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
        self.assertIn('grid-template-columns:96px minmax(0,1fr)', self.html)
        self.assertIn('h1 { max-width:100%; font-size:clamp(2.8rem,14vw,5.2rem); }', self.html)

    def test_homepage_shows_a_brief_splash_until_local_data_initialization_settles(self):
        self.assertIn("document.documentElement.classList.add('gymratik-loading')", self.html)
        self.assertIn('id="appSplash" class="app-splash" role="status"', self.html)
        self.assertIn('class="splash-mascots" role="img"', self.html)
        self.assertIn("Leyendo el avance guardado", self.html)
        self.assertIn('html.gymratik-loading .app-splash', self.html)
        self.assertIn("document.documentElement.classList.remove('gymratik-loading')", self.html)
        self.assertIn("await networkDecisionPhase", self.html)
        self.assertIn("if (!navigator.serviceWorker?.controller) await syncTask", self.html)
        self.assertNotIn("await Promise.all([localInitialization, syncTask])", self.html)
        self.assertIn("1000 - (performance.now() - start)", self.html)
        self.assertIn('id="splashRetry"', self.html)
        self.assertIn("Tus datos permanecen en este dispositivo", self.html)
        self.assertIn("setAttribute('aria-hidden', 'true')", self.html)
        self.assertIn("@media (prefers-reduced-motion:reduce)", self.html)

    def test_network_permission_is_explained_and_chosen_inside_the_splash(self):
        self.assertIn('id="splashNetworkActions"', self.html)
        self.assertIn('id="splashAllowNetwork"', self.html)
        self.assertIn('id="splashSkipNetwork"', self.html)
        self.assertIn("function requestNetworkPermission(message, sizeNote)", self.html)
        self.assertIn("No se descargará nada hasta que elijas una opción.", self.html)
        self.assertIn("allowed = await requestNetworkPermission(", self.html)
        self.assertIn("if (!firstInstall || preference === 'ask') { syncFinished = true; return; }", self.html)

    def test_homepage_prioritizes_next_session_and_gym_flow(self):
        self.assertIn("Una serie a la vez.", self.html)
        self.assertIn('id="nextSessionCta"', self.html)
        self.assertIn('id="nextSessionLink"', self.html)
        self.assertIn('function renderNextSession', self.html)
        self.assertIn('Continúa donde te quedaste', self.html)
        self.assertIn('Calentamiento incluido', self.html)
        self.assertIn('Tres pasos y a entrenar.', self.html)
        self.assertIn('Mi avance', self.html)
        self.assertIn('Proteger avance', self.html)

    def test_homepage_uses_animated_original_pair_outside_install_invitation(self):
        self.assertIn('<img class="hero-mascot-bg" src="./icon.png"', self.html)
        self.assertIn("background-image:url('./data/profile/gymratik-machine-sprite.webp')", self.html)
        self.assertTrue((ROOT / "data/profile/gymratik-machine-sprite.webp").is_file())
        self.assertIn("legPressCycle", self.html)
        self.assertIn("chestPressCycle", self.html)
        self.assertIn("prefers-reduced-motion:reduce", self.html)
        self.assertIn('animation:mascotDrift 9s ease-in-out infinite alternate', self.html)
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

    def test_profile_and_progress_reads_are_gated_by_installation(self):
        self.assertIn("if (!window.GymratikInstallGate?.isInstalled()) return;", self.html.split("async function refreshProfile()", 1)[1])
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
