from __future__ import annotations

import sys
import re
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_canonical_routines import validate_path  # noqa: E402
from build_fitness_quotes_js import compact_payload  # noqa: E402
from standardize_muscle_visuals import (  # noqa: E402
    close_unterminated_segmented_progress_style,
    standardize_offline_image_sources,
    standardize_series_entry_zone,
    standardize_summary_navigation,
    standardize_technique_accordion,
    standardize_technique_guidance,
    TECHNIQUE_CUES,
    standardize_visual_language,
    standardize_warmup_single_viewers,
)


CANONICAL = ROOT / "data" / "rutinas_autocontenidas" / "canonicas"


class CanonicalRoutineValidationTests(unittest.TestCase):
    def test_technique_steps_are_collapsed_in_an_accessible_accordion(self) -> None:
        source = '''<html><head></head><body><article><details class="techAccordion" data-enhancement="technique-accordion-v1"><summary>Guía breve de técnica</summary></details><div class="techSteps"><div class="techStep"><div class="techStepTitle">Ajuste</div><div class="techStepText">Postura estable.</div></div><div class="techStep"><div class="techStepTitle">Ejecución</div><div class="techStepText">Controla el recorrido.</div></div></div></article></body></html>'''
        result = standardize_technique_accordion(source)
        self.assertEqual(result.count('data-enhancement="technique-accordion-v1"'), 1)
        self.assertIn('<summary>Técnica esencial</summary>', result)
        self.assertNotIn('<details class="techAccordion" open', result)
        self.assertEqual(result.count('<div class="techSteps">'), 1)
        accordion = re.search(r'<details class="techAccordion".*?</details>', result, re.S).group(0)
        self.assertIn('<div class="techSteps">', accordion)
        self.assertEqual(standardize_technique_accordion(result), result)

    def test_technique_guidance_uses_three_compact_exercise_specific_cues(self) -> None:
        source = '''<article class="card"><div class="exTitle">JALÓN AL PECHO</div><div class="techSteps"><div class="techStep setup">old setup</div><div class="techStep move">old movement</div><div class="techStep control">old tempo</div><div class="techStep warning">old warning</div></div></article>'''
        result = standardize_technique_guidance(source)
        self.assertEqual(len(TECHNIQUE_CUES), 26)
        self.assertEqual(result.count('class="techStep setup"'), 1)
        self.assertEqual(result.count('class="techStep move"'), 1)
        self.assertEqual(result.count('class="techStep warning"'), 1)
        self.assertNotIn('class="techStep control"', result)
        self.assertIn("Movimiento", result)
        self.assertIn("Exhala al tirar", result)
        self.assertEqual(standardize_technique_guidance(result), result)

    def test_summary_navigation_preserves_free_scroll_and_clicks_to_exercise(self) -> None:
        source = '''<html><head></head><body><div class="sessionSummaryList"></div><script>
const focusedIndex = rows.findIndex(row => !row.complete && row.done > 0) >= 0 ? rows.findIndex(row => !row.complete && row.done > 0) : rows.findIndex(row => !row.complete);
if (list) {
    new MutationObserver(scheduleAlignment).observe(list, {childList:true, subtree:true});
    list.addEventListener('click', function(event){
      var button = event.target.closest('.summaryExercise');
      if (!button) return;
      requestedExercise = button.dataset.exercise || '';
      window.setTimeout(scheduleAlignment, 0);
    });
  }
function alignSummary(exerciseNumber){
    list.scrollTop = target.offsetTop;
  }
function scheduleAlignment() {}
</script></body></html>'''
        result = standardize_summary_navigation(source)
        self.assertNotIn('new MutationObserver(scheduleAlignment)', result)
        self.assertIn('window.gymratikFocusedExerciseIndex', result)
        self.assertIn("scrollIntoView({behavior:'smooth', block:'start'})", result)
        self.assertIn('max-height:min(24dvh,168px)', result)
        self.assertIn('#floatingSessionSummary .sessionSummaryList{max-height:150px!important}', result)
        self.assertIn('#floatingSessionSummary .sessionSummaryList{max-height:78px!important', result)
        self.assertIn('width:82px!important;height:82px!important', result)

    def test_warmup_media_groups_become_single_active_viewers_with_accessible_choices(self) -> None:
        source = '''<html><head></head><body><article class="warmupStep cardio">
          <div class="warmupMedia warmupMediaStrip" role="list" aria-label="Opciones">
            <div class="warmupVisual"><img class="warmupGif" src="videos/elliptical.gif" alt="Elíptica"><img class="warmupFallback" src="images/elliptical.jpg" hidden><span class="warmupMediaLabel">ELÍPTICA</span></div>
            <div class="warmupVisual"><img class="warmupGif" src="videos/treadmill.gif" alt="Caminadora"><img class="warmupFallback" src="images/treadmill.jpg" hidden><span class="warmupMediaLabel">CAMINADORA</span></div>
          </div>
        </article></body></html>'''

        standardized = standardize_warmup_single_viewers(source)

        self.assertIn('data-enhancement="warmup-single-active-viewer-v1"', standardized)
        self.assertEqual(standardized.count('class="warmupVisual"'), 1)
        self.assertEqual(standardized.count('class="warmupGif"'), 1)
        self.assertEqual(standardized.count('class="warmupMediaChoice"'), 2)
        self.assertIn('aria-pressed="true"', standardized)
        self.assertIn('data-gif-src="videos/treadmill.gif"', standardized)
        self.assertIn('data-poster-src="images/treadmill.jpg"', standardized)
        self.assertEqual(standardize_warmup_single_viewers(standardized), standardized)

    def test_all_canonical_warmup_viewers_keep_one_active_gif_and_local_choices(self) -> None:
        class ViewerInventory(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.groups: list[dict[str, list[dict[str, str]]]] = []
                self.current: dict[str, list[dict[str, str]]] | None = None
                self.depth = 0

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                values = {key: value or "" for key, value in attrs}
                classes = values.get("class", "").split()
                if tag == "div" and "warmupSingleViewer" in classes:
                    self.current = {"gifs": [], "choices": []}
                    self.groups.append(self.current)
                    self.depth = 1
                    return
                if self.current is None:
                    return
                if tag == "div":
                    self.depth += 1
                if tag == "img" and "warmupGif" in classes:
                    self.current["gifs"].append(values)
                elif tag == "button" and "warmupMediaChoice" in classes:
                    self.current["choices"].append(values)

            def handle_endtag(self, tag: str) -> None:
                if self.current is not None and tag == "div":
                    self.depth -= 1
                    if self.depth == 0:
                        self.current = None

        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            inventory = ViewerInventory()
            inventory.feed(source)
            with self.subTest(routine=path.name):
                self.assertEqual(source.count('data-fix="warmup-single-active-viewer-script-v1"'), 1)
                self.assertIn("document.querySelectorAll('.warmupSingleViewer')", source, path.name)
                self.assertNotIn("document.querySelectorAll('.warmupMediaSingleViewer')", source, path.name)
                self.assertTrue(inventory.groups)
                for group in inventory.groups:
                    self.assertEqual(len(group["gifs"]), 1)
                    self.assertGreaterEqual(len(group["choices"]), 2)
                    for choice in group["choices"]:
                        for attr in ("data-gif-src", "data-poster-src"):
                            asset = (path.parent / unquote(choice[attr].split("?", 1)[0])).resolve()
                            self.assertTrue(asset.is_relative_to(ROOT.resolve()))
                            self.assertTrue(asset.is_file(), f"{path.name}: falta el recurso {choice[attr]}")
                        self.assertTrue(choice["data-label"])

    def test_unterminated_progress_style_is_closed_before_the_next_stylesheet(self) -> None:
        malformed = (
            '<head><style data-enhancement="segmented-progress-bars-v1">.progress{color:red}'
            '<style data-enhancement="interaction-feedback-v1">.clear{color:blue}</style></head>'
        )
        repaired = close_unterminated_segmented_progress_style(malformed)
        self.assertIn(
            '.progress{color:red}\n</style>\n<style data-enhancement="interaction-feedback-v1">',
            repaired,
        )
        self.assertEqual(close_unterminated_segmented_progress_style(repaired), repaired)

    def test_series_entry_standardizer_adds_licensed_icons_and_touch_slider_feedback(self) -> None:
        source = """<script>
const performancePanel = document.createElement('div');
const repsTitle = document.createElement('span'); repsTitle.textContent = 'Repeticiones realizadas · opcional'; const repsClear = document.createElement('button');
const loadHead = document.createElement('span'); loadHead.className = 'performanceLoadHead';
    const loadTitle = document.createElement('span'); loadTitle.textContent = 'Carga utilizada (opcional)';
const updateLoadControl = () => {};
loadOutput.textContent = item.performanceLoadSelected ? `${Number.isInteger(value) ? value : value.toFixed(1)} ${item.performanceLoadUnit}` : 'Sin registrar · tocar para añadir'; loadClear.hidden = !item.performanceLoadSelected;
item.performanceRepsOutput.dataset.selected = String(selected); repsClear.hidden = !selected; repsDown.disabled
</script>"""
        standardized = standardize_series_entry_zone(source)
        self.assertIn("createPerformanceIcon('repeat-2')", standardized)
        self.assertIn("createPerformanceIcon('weight')", standardized)
        self.assertIn("const updateRangeFill = input =>", standardized)
        self.assertIn("updateRangeFill(item.performanceReps)", standardized)
        self.assertIn("loadOutput.dataset.selected = String(item.performanceLoadSelected)", standardized)

    def test_standardizer_replaces_img_src_without_overwriting_provenance(self) -> None:
        source = (
            '<img data-original-src="https://shop.lifefitness.com/machine.jpg" '
            'src="https://shop.lifefitness.com/machine.jpg" alt="Máquina">'
        )
        standardized = standardize_offline_image_sources(source)
        self.assertIn('data-original-src="https://shop.lifefitness.com/machine.jpg"', standardized)
        self.assertIn(
            'src="../medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-machine-only.webp"',
            standardized,
        )

    def test_optional_gifs_reveal_packaged_posters_when_offline(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn(
                    "loadUnitSelect.addEventListener('keydown', event => { if (event.key === 'Enter') event.stopPropagation(); });",
                    source,
                    "Enter en kg/lb no debe propagarse y activar otra acción de la rutina",
                )
                self.assertEqual(source.count('data-fix="offline-optional-gif-fallback-v1"'), 1)
                self.assertIn('.warmupVisual[data-media-state="FALLBACK_STATIC"] .warmupFallback', source)
                self.assertIn('.gifFrame[data-media-state="FALLBACK_STATIC"] .gifFallback', source)
                self.assertIn("document.addEventListener('error', event => revealPoster(event.target), true)", source)
                self.assertIn("fallback.hidden = false", source)

    def test_all_routine_images_are_local_and_packaged(self) -> None:
        class ImageSources(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.sources: list[str] = []

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                if tag.lower() == "img":
                    source = dict(attrs).get("src") or ""
                    if source:
                        self.sources.append(source)

        for path in sorted(CANONICAL.glob("Rutina_Dia_*.html")):
            parser = ImageSources()
            parser.feed(path.read_text(encoding="utf-8"))
            for source in parser.sources:
                with self.subTest(routine=path.name, source=source[:100]):
                    self.assertFalse(source.startswith(("http://", "https://")), "la imagen requiere red")
                    if source.startswith("data:image/"):
                        continue
                    asset = (path.parent / unquote(source.split("?", 1)[0])).resolve()
                    self.assertTrue(asset.is_relative_to(ROOT.resolve()), "la imagen sale del repositorio")
                    self.assertTrue(asset.is_file(), f"no existe el recurso empaquetado: {source}")

    def test_day2_matches_its_declared_contract(self) -> None:
        self.assertEqual(
            validate_path(CANONICAL / "Rutina_Dia_2_Pierna_Gluteo_V1.html"), []
        )

    def test_day1_matches_its_declared_contract(self) -> None:
        self.assertEqual(
            validate_path(CANONICAL / "Rutina_Dia_1_Espalda_Biceps_V1.html"), []
        )

    def test_day1_corruption_is_detected(self) -> None:
        source = (CANONICAL / "Rutina_Dia_1_Espalda_Biceps_V1.html").read_text(
            encoding="utf-8"
        )
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            path = Path(directory) / "Rutina_Dia_1_Espalda_Biceps_V1.html"
            path.write_text(source.replace('data-exercise="3"', 'data-exercise="5"', 1), encoding="utf-8")
            errors = validate_path(path)
        self.assertTrue(any("secuencia contigua" in error for error in errors))

    def test_day3_matches_its_declared_contract(self) -> None:
        self.assertEqual(
            validate_path(CANONICAL / "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html"), []
        )

    def test_day4_matches_its_declared_contract(self) -> None:
        self.assertEqual(
            validate_path(CANONICAL / "Rutina_Dia_4_Pierna_Equilibrio_V1.html"), []
        )

    def test_day3_current_exercise_cue_is_detected(self) -> None:
        source = (CANONICAL / "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html").read_text(
            encoding="utf-8"
        )
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            path = Path(directory) / "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html"
            path.write_text(source.replace('data-next="2"', 'data-next="1"', 1), encoding="utf-8")
            errors = validate_path(path)
        self.assertTrue(any("apunta a 1; se esperaba 2" in error for error in errors))

    def test_day3_does_not_keep_day1_media_repairs(self) -> None:
        source = (CANONICAL / "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("machineOnlyCurl", source)
        self.assertNotIn("finalAssets", source)
        self.assertNotIn(
            "confirma directamente la identidad de la máquina del gimnasio", source
        )

    def test_canonical_routines_do_not_embed_license_or_attribution_metadata(self) -> None:
        forbidden_markers = (
            '"license":',
            'portraitLicense',
            'portraitCredit',
            'portraitSource',
            'authorContextSource',
            'CANDIDATE_PENDING_LICENSE_REVIEW',
            'sourceUrl:',
            'mediaStatus',
            'motivationSource',
            'gifAttribution',
        )
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            for marker in forbidden_markers:
                with self.subTest(path=path.name, marker=marker):
                    self.assertNotIn(marker, source)

    def test_canonical_routines_show_full_motivational_phrases(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            match = re.search(r"\.sessionCompletionCopy p\{([^}]*)\}", source)
            self.assertIsNotNone(match, path.name)
            rules = match.group(1)
            self.assertIn("display:block", rules, path.name)
            self.assertIn("overflow:visible", rules, path.name)
            self.assertIn("overflow-wrap:anywhere", rules, path.name)
            self.assertNotIn("-webkit-line-clamp", rules, path.name)

    def test_day1_has_machine_only_reference_and_two_phases_per_exercise(self) -> None:
        source = (CANONICAL / "Rutina_Dia_1_Espalda_Biceps_V1.html").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            len(re.findall(r'<div[^>]*class="[^"]*machineRefBox[^"]*"', source)),
            6,
        )
        self.assertEqual(source.count('<div class="phaseLabel">Inicio'), 6)
        self.assertEqual(source.count('<div class="phaseLabel">Final'), 6)
        self.assertIn("3025-butterfly-reverse-front.jpg", source)
        self.assertIn("0592-b6hQYMb-machine-only.jpg", source)

    def test_every_exercise_has_a_complete_position_pair_or_explicit_hip_thrust_guide(self) -> None:
        expected_counts = {
            "Rutina_Dia_1_Espalda_Biceps_V1.html": 6,
            "Rutina_Dia_2_Pierna_Gluteo_V1.html": 6,
            "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html": 7,
            "Rutina_Dia_4_Pierna_Equilibrio_V1.html": 7,
        }
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            cards = re.findall(
                r'<article class="card" data-exercise-index="(\d+)">(.*?)</article>',
                source,
                re.S,
            )
            with self.subTest(routine=path.name):
                self.assertEqual(len(cards), expected_counts[path.name])
                for index, card in cards:
                    if path.name == "Rutina_Dia_2_Pierna_Gluteo_V1.html" and index == "2":
                        self.assertIn('class="phaseRow hipThrustGuide"', card)
                        self.assertEqual(card.count('class="hipThrustGuideTitle"'), 3)
                        self.assertNotIn('class="phaseCol"', card)
                        continue
                    self.assertEqual(card.count('class="phaseCol"'), 2, f"ejercicio {index}")
                    self.assertEqual(card.count('class="phaseLabel">Inicio'), 1, f"ejercicio {index}")
                    self.assertEqual(card.count('class="phaseLabel">Final'), 1, f"ejercicio {index}")
                    phase_images = re.findall(r'<div class="phaseCol">.*?</div>\s*</div>', card, re.S)
                    self.assertEqual(len(phase_images), 2, f"ejercicio {index}")
                    self.assertTrue(all(re.search(r'<img\b[^>]*class="[^"]*realphoto[^"]*"', phase) for phase in phase_images), f"ejercicio {index}")
                if path.name == "Rutina_Dia_1_Espalda_Biceps_V1.html":
                    first = dict(cards)["1"]
                    self.assertIn("0197-qdRxqCj-start.jpg", first)
                    self.assertIn("0197-qdRxqCj-final.jpg", first)
                    self.assertNotIn("0577-T0yTjgW", first)

    def test_day1_row_has_matching_media_and_metrics(self) -> None:
        source = (CANONICAL / "Rutina_Dia_1_Espalda_Biceps_V1.html").read_text(
            encoding="utf-8"
        )
        card = source[source.index("<!-- 3 -->") : source.index("<!-- 4 -->")]
        self.assertIn("▶ VIDEO TÉCNICO · Remo horizontal", card)
        self.assertIn("Jl0r78dnqGU", card)
        self.assertIn("8–12 repeticiones", card)
        self.assertIn("2–2.5 min", card)
        self.assertIn("7–9 min", card)

    def test_all_routines_have_explicit_rest_transition_and_alert_contract(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            self.assertIn("startSeriesButton", source)
            self.assertIn("restPhase", source)
            self.assertIn("restNotifiedAt", source)
            self.assertIn("restReminderNotifiedAt", source)
            self.assertIn("sessionAbandonedAt", source)
            self.assertIn("sendBrowserNotification", source)
            self.assertIn("navigator.vibrate", source)
            self.assertIn("timing.timingVersion = 5", source)

    def test_series_flow_uses_one_button_and_enforces_minimum_rest(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("className = 'startSeriesButton'", source)
                self.assertIn(
                    "const startSeriesButton = item.tracker.querySelector('.completeSetButton');",
                    source,
                )
                self.assertIn("Completar serie ${nextIndex + 1}", source)
                self.assertIn("Iniciar serie ${nextIndex + 1}", source)
                self.assertIn("Descanso · ${formatElapsed(restRemaining)}", source)
                self.assertIn("mantén 5 s para continuar", source)
                self.assertNotIn("startExerciseButton", source)
                self.assertNotIn("item.startButton", source)
                self.assertIn("beginSeries(item, Date.now())", source)
                self.assertIn("}, 5000);", source)
                self.assertIn(
                    "longPressResetTimer = window.setTimeout(() => { longPressDetected = false; longPressResetTimer = 0; }, 350);",
                    source,
                )
                self.assertIn("window.clearTimeout(longPressResetTimer);", source)
                self.assertIn(
                    "resting && restRemaining > 0",
                    source,
                )
                self.assertIn(
                    "Date.now() - timing.restStartedAt < getRestRecommendation(item).minMs",
                    source,
                )
                self.assertNotRegex(source, r"\bseriesPreparing\b")

    def test_machine_series_rest_countdown_and_floating_activity_indicator(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            timing_display = source[
                source.index("const renderTimingDisplays = () => {") : source.index(
                    "// El cronómetro empieza después de una preparación explícita de 15 segundos."
                )
            ]
            complete_button = source[
                source.index("const updateCompleteButton = item => {") : source.index(
                    "const updateSummary = () => {"
                )
            ]
            with self.subTest(path=path.name):
                self.assertIn("const restRemaining = Math.max(0, recommendation.minMs - restElapsed);", timing_display)
                self.assertIn("Descanso restante: <strong>${formatCountdown(restRemaining)}</strong>", timing_display)
                self.assertIn("item.restDisplay.hidden = !restActive", timing_display)
                self.assertIn("if (!root?.sessionEndedAt && timing?.restStartedAt) notifyRestReady(item, timing, restElapsed);", timing_display)
                self.assertIn("Boolean(!root?.sessionEndedAt && timing?.restStartedAt && restRemaining > 0)", timing_display)
                self.assertIn("exerciseItems.some(entry => !snapshot(entry).complete)", source)
                self.assertIn("button.classList.toggle('is-resting', resting && restRemaining > 0)", complete_button)
                self.assertIn("button.classList.toggle('is-series-active', seriesActive && !preparing)", complete_button)
                self.assertIn("summaryButton.classList.toggle('isResting', restActive)", timing_display)
                self.assertIn("summaryButton.classList.toggle('isSeriesActive', seriesActive)", timing_display)
                self.assertIn("`● S${row.done + 1} activa · ${formatElapsed(now - timing.seriesStartedAt)}`", timing_display)
                self.assertIn("item.timerChips = new Map()", timing_display)
                self.assertIn("display.setAttribute('aria-live', 'off')", timing_display)
                self.assertIn("kind: 'active-set'", timing_display)
                self.assertIn("kind: 'active-rest'", timing_display)
                self.assertIn("entries.push({ key: `set-${index + 1}`", timing_display)
                self.assertIn(".exerciseTimerChip[data-kind=\"active-set\"]::after", source)
                self.assertIn(".exerciseTimerChip[data-kind=\"active-rest\"]::after", source)
                self.assertIn(".exerciseTimerChip[data-kind=\"active-set\"]::before", source)
                self.assertIn("@media(prefers-reduced-motion:reduce){.exerciseTimerChip", source)
                floating_summary = source[
                    source.index('<aside class="floatingSessionSummary"') : source.index("</aside>")
                ]
                self.assertEqual(source.count('<aside class="floatingSessionSummary"'), 1)
                self.assertEqual(floating_summary.count('<button'), 1)
                self.assertIn('id="summaryActivityIcon"', floating_summary)
                self.assertIn('id="summaryHeadline"', floating_summary)
                self.assertEqual(source.count('id="summaryActivityHeadline"'), 1)
                self.assertEqual(source.count('id="summaryActivityStatus"'), 1)
                self.assertEqual(source.count('id="summaryOverallProgress"'), 1)
                self.assertEqual(floating_summary.count('id="summaryActivityMascot"'), 1)
                self.assertIn('id="summaryToggle"', floating_summary[:floating_summary.index('id="summaryBody"')])
                self.assertIn('aria-expanded="false"', floating_summary)
                self.assertRegex(floating_summary, r'<div class="summaryBody" id="summaryBody"[^>]*\shidden(?:\s|>)')
                self.assertIn('class="summaryMascotWrap"', floating_summary[:floating_summary.index('id="summaryBody"')])
                self.assertEqual(floating_summary.count('class="summaryMascotWrap"'), 1)
                self.assertNotIn('id="summaryActivityMascot"', floating_summary[floating_summary.index('id="summaryBody"'):])
                self.assertNotIn('id="summaryActivity"', floating_summary)
                self.assertIn("let currentActivity = null", timing_display)
                self.assertIn("Descanso listo · ${item.title}", timing_display)
                self.assertIn("activityButton.classList.toggle('isActive'", timing_display)
                self.assertIn("activityHeadline.textContent = progressText", timing_display)
                self.assertIn("if (compactActivityHeadline) compactActivityHeadline.textContent = activityText", timing_display)
                self.assertIn("kind: 'strength'", timing_display)
                self.assertIn("kind: warmup.phase", timing_display)
                self.assertIn("const mascotMode = displayActivity.kind === 'complete' ? 'celebration' : displayActivity.kind", timing_display)
                self.assertIn("kind: 'complete', label: 'Rutina completada'", timing_display)
                self.assertIn("kind: 'start', label: '¡Rutina iniciada!'", timing_display)
                self.assertIn("document.getElementById('summaryActivityMascot')", timing_display)
                self.assertIn("summaryToggle.getAttribute('aria-expanded') === 'true'", source)
                self.assertIn("mascot.hidden = false", timing_display)
                self.assertIn("neutral-${fallbackState}-still.webp", timing_display)
                self.assertIn("const poseState = ({ start: 'idle', ready: 'ready'", timing_display)
                self.assertIn("states-v1/${mascotVariant}-${poseState}.png", timing_display)
                self.assertIn("mascot.dataset.poseState = poseState", timing_display)
                self.assertIn("mascot.dataset.motion = document.hidden ? 'paused' : mascotMode", timing_display)
                summary_style_source = re.search(r'<style data-fix="rest-countdown-activity-v1">.*?</style>', source, re.S).group(0)
                self.assertIn("#summaryActivityMascot{display:block;width:70px;height:70px", summary_style_source)
                self.assertIn("width:62px;height:62px", summary_style_source)
                self.assertIn("width:58px;height:58px", summary_style_source)
                self.assertIn("width:54px;height:54px", summary_style_source)
                self.assertIn("clamp(50px,14vw,68px)", summary_style_source)
                self.assertNotIn("mascot.removeAttribute('src')", timing_display)
                self.assertIn("document.addEventListener('visibilitychange', syncTimingInterval", source)
                self.assertIn("window.clearInterval(timingInterval)", source)
                self.assertIn("mascotCardioCadence", summary_style_source)
                self.assertIn("mascotStrengthEffort", summary_style_source)
                self.assertIn("mascotIdleBreath", summary_style_source)
                self.assertIn("mascotApprovalCelebrate", summary_style_source)
                self.assertIn("mascotRecoveryBreath", summary_style_source)
                self.assertIn("mascotWarmupFlow", summary_style_source)
                self.assertIn("mascotPreparationBrace", summary_style_source)
                self.assertIn(".summaryMascotWrap{position:relative;grid-column:3", summary_style_source)
                self.assertNotIn("25fps.gif", timing_display)
                self.assertIn('data-enhancement="compact-routine-metrics-v1"', source)
                self.assertIn('data-enhancement="approval-toast-mascot-v1"', source)
                self.assertIn("if (longPressTimer) { window.clearTimeout(longPressTimer); longPressTimer = 0; } longPressDetected = false;", source)
                self.assertNotIn("timing.seriesStartedAt || longPressTimer) return;", source)
                self.assertIn("window.TrainingProgressStore?.getProfile?.().then(updateActivityMascotProfile)", source)
                self.assertIn("activityStatus.classList.toggle('isIdle', ['start', 'ready', 'complete'].includes(displayActivity.kind))", timing_display)
                self.assertIn("overallProgress.setAttribute('aria-valuenow', String(doneSeries))", timing_display)
                summary_style = re.search(
                    r'<style data-fix="rest-countdown-activity-v1">.*?</style>', source, re.S
                )
                self.assertIsNotNone(summary_style)
                self.assertIn(".summaryToggle.isResting", summary_style.group(0))
                self.assertIn(".summaryToggle.isActive", summary_style.group(0))
                self.assertNotIn(".summaryActivity{", summary_style.group(0))
                self.assertIn(".summaryExercise.isSeriesActive .summaryExerciseState", summary_style.group(0))
                self.assertIn("button.completeSetButton.is-resting", summary_style.group(0))
                self.assertIn("animation:restSlowPulse 2.4s", summary_style.group(0))
                self.assertIn("animation:activityFastPulse .68s", summary_style.group(0))
                self.assertIn(".exerciseTracker:has(.completeSetButton.is-series-active) .seriesProgressSegment.is-current", summary_style.group(0))
                self.assertIn("#summaryActivityHeadline", summary_style.group(0))
                self.assertIn("#floatingSessionSummary{position:fixed!important", summary_style.group(0))
                self.assertIn("max-height:min(44dvh,400px)", summary_style.group(0))
                self.assertIn("max-height:min(28dvh,180px)", summary_style.group(0))
                self.assertIn("max-height:min(62dvh,380px)", summary_style.group(0))
                self.assertIn("max-height:min(58dvh,380px)", summary_style.group(0))
                self.assertIn('#summaryToggle[aria-expanded="true"] #summaryActivityHeadline{display:block!important', summary_style.group(0))
                self.assertIn('#summaryToggle[aria-expanded="true"] + #summaryBody .summaryActivityStatus{position:absolute!important', summary_style.group(0))
                self.assertIn('#summaryToggle[aria-expanded="true"] + #summaryBody .summaryTotals{display:none!important}', summary_style.group(0))
                self.assertIn("max-height:min(62.5dvh,225px)", summary_style.group(0))
                self.assertIn("max-height:min(24dvh,90px)", summary_style.group(0))
                self.assertIn(".summaryTotals span{min-height:20px!important", summary_style.group(0))
                self.assertIn(".summaryExercise::after", summary_style.group(0))
                self.assertIn(".summaryExercise::before,.summaryExercise::after", summary_style.group(0))
                self.assertIn("transform:scaleX(var(--summary-progress,0))", summary_style.group(0))
                self.assertIn(".summaryExercise.isSeriesActive::after", summary_style.group(0))
                self.assertIn("white-space:nowrap!important;display:block!important", summary_style.group(0))
                self.assertIn(".summaryExercise.isSeriesActive::after,button.completeSetButton", summary_style.group(0))
                self.assertIn(".summaryProgressTrack>span", summary_style.group(0))
                self.assertIn(".summaryActivityStatus.isIdle .summaryActivityIndicator{background:#82aebb;animation:none}", summary_style.group(0))
                self.assertIn(".seriesProgressSegment.is-current.is-resting", summary_style.group(0))
                self.assertIn("@keyframes activityFillGlow", summary_style.group(0))
                self.assertNotIn("@keyframes progressActivityFill", summary_style.group(0))
                self.assertIn("repsRequired.textContent = 'Requerido'", source)
                self.assertIn("loadRequired.textContent = 'Requerida'", source)
                self.assertNotIn("repsOptional", source)
                self.assertNotIn("loadOptional", source)
                self.assertIn("Registra repeticiones y carga para completar", source)
                self.assertNotRegex(summary_style.group(0), r"@keyframes activityFillGlow\s*\{[^}]*transform\s*:")
                self.assertIn("@media(prefers-reduced-motion:reduce)", summary_style.group(0))

    def test_repetition_selector_uses_exercise_range_plus_four_without_defaulting(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            control = source[
                source.index("const repsTitle"):source.index("const loadLabel")
            ]
            reps_logic = source[
                source.index("const renderPerformanceReps"):source.index(
                    "item.performanceLoad.addEventListener"
                )
            ]
            with self.subTest(path=path.name):
                self.assertIn("repsInput.min = String(Math.max(1, item.repMinimum - 3))", source)
                self.assertIn("repsInput.max = String(item.repMaximum + 4)", source)
                self.assertIn("repsInput.dataset.selected = 'false'", source)
                self.assertIn("item.performanceReps.dataset.selected === 'true'", source)
                self.assertIn("reps <= item.repMaximum + 4", source)
                self.assertIn("performanceRepsNudge", control)
                self.assertIn("repsLabelText.textContent = 'Repeticiones'", source)
                self.assertIn("createPerformanceIcon('repeat-2')", source)
                self.assertIn("const repFeedbackZone = value =>", source)
                self.assertIn("data-zone=\"below\"", source)
                self.assertIn("const loadProfile = /prensa|hack squat|hip thrust|bisagra/", source)
                self.assertIn("dataset.maxKg = String(item.performanceLoadProfile.maxKg)", source)
                self.assertIn("Elige ${minPossible}–${maxPossible}; objetivo ${item.repMinimum}–${item.repMaximum}", reps_logic)
                self.assertIn("repsClear.addEventListener('click'", source)
                self.assertIn("aria-live', 'polite", source)
                self.assertIn("Math.min(item.repMaximum + 4", reps_logic)
                self.assertIn("Math.max(item.repMinimum", reps_logic)
                self.assertIn("savePerformanceDraft()", reps_logic)
                self.assertIn("data-enhancement=\"interaction-feedback-v1\"", source)
                self.assertIn("performanceClear", source)
                self.assertIn("loadClear.addEventListener('click'", source)
                self.assertIn("loadLabelText.textContent = 'Carga'", source)
                self.assertIn("createPerformanceIcon('weight')", source)
                self.assertIn("await confirmMissingPerformance(missingPerformance)", source)
                self.assertIn("Guardar sin estos datos", source)
                self.assertIn("reps: repsSelected ? reps : null", source)
                self.assertIn("durationMs: Math.min(MAX_TIMING_MS", source)
                self.assertIn("item.performanceRepsClear.hidden = true", source)
                self.assertNotIn("repsClear.hidden = true; updateRangeFill", source)
                self.assertEqual(source.count("repsClear.addEventListener('click'"), 1)
                self.assertEqual(source.count("loadClear.addEventListener('click'"), 1)
                self.assertEqual(source.count("const activeRest = Boolean("), 1)
                self.assertIn("button:not(:disabled):active", source)
                self.assertNotIn("Number(item.performanceReps.value) > 0 ?", source)

    def test_all_routines_use_persistent_fifteen_second_preparation_before_timing(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertEqual(source.count("const PREPARATION_MS = 15000;"), 1)
                self.assertIn("warmup.phase = 'preparing'", source)
                self.assertIn("warmup.preparationEndsAt = warmupPreparationEndsAt", source)
                self.assertIn("timing.preparationEndsAt = endsAt", source)
                self.assertIn("if (restoredWarmup.phase === 'preparing')", source)
                self.assertIn("Omitir ejercicio · mantén 10 s", source)
                self.assertIn("setTimeout(() => { skipHoldTimer = 0", source)
                self.assertIn("loadOutput.addEventListener('click'", source)
                self.assertIn("performanceLoadDirect", source)
                self.assertIn("--hold-progress", source)
                self.assertIn("root.sessionStartedAt = timestamp", source)
                self.assertIn("startSeriesPreparation(item);", source)
                self.assertIn(
                    "const startTiming = (item, timestamp = Date.now(), startSeries = false)",
                    source,
                )
                self.assertIn("startTiming(item, timestamp, true)", source)
                self.assertIn("clearPreparationTimers();", source)
                self.assertEqual(
                    source.count("sendBrowserNotification('Descanso listo'"), 1
                )
                self.assertNotIn(
                    "const preparing = isSeriesPreparing(item); if (preparing) "
                    "{ renderPreparationDisplay(item); if (item.restDisplay) item.restDisplay.hidden = true; return; } "
                    "const preparing = isSeriesPreparing(item);",
                    source,
                )

    def test_all_routines_expose_direct_decimal_load_entry_and_hold_feedback(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("loadOutput.addEventListener('click'", source)
                self.assertIn("editor.step = '0.1'", source)
                self.assertIn("entered <= Number(loadInput.max)", source)
                self.assertIn("item.performanceLoadExact = Math.round(entered * 10) / 10", source)
                self.assertIn("load: item.performanceLoadSelected ? String(item.performanceLoadExact) : ''", source)
                self.assertIn("loadSelected: item.performanceLoadSelected", source)
                self.assertIn("item.tracker.append(performancePanel)", source)
                self.assertIn("item.performanceLoadSelected && Number.isFinite(loadValue)", source)
                self.assertIn("queueMicrotask(() => finish(true))", source)
                self.assertIn("startSeriesButton.style.setProperty('--hold-progress', '100%')", source)
                self.assertIn("--hold-progress", source)
                self.assertIn("}, 10000);", source)
                self.assertIn("state.__skippedExercises[key] = true", source)
                self.assertIn("row.skipped ? '↷ Omitido'", source)

    def test_editable_load_value_persists_decimal_independently_of_slider_step(self) -> None:
        source = (CANONICAL / "Rutina_Dia_1_Espalda_Biceps_V1.html").read_text(encoding="utf-8")
        self.assertIn("item.performanceLoadExact = Math.round(entered * 10) / 10", source)
        self.assertIn("load: item.performanceLoadSelected ? String(item.performanceLoadExact) : ''", source)
        self.assertIn("item.performanceLoadSelected = true", source)
        self.assertIn("item.performanceLoadSelected = false", source)
        self.assertIn("const loadValue = Number(item.performanceLoadExact)", source)
        self.assertIn("editor.addEventListener('blur', () => queueMicrotask(() => finish(true))", source)

    def test_all_routines_share_the_canonical_page_layout_contract(self) -> None:
        expected_cards = {"Rutina_Dia_1_Espalda_Biceps_V1.html": 6, "Rutina_Dia_2_Pierna_Gluteo_V1.html": 6, "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html": 7, "Rutina_Dia_4_Pierna_Equilibrio_V1.html": 7}
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertEqual(source.count('<main class="cards">'), 1)
                self.assertEqual(source.count('<footer class="sessionFooter"'), 1)
                self.assertNotIn('<footer class="footer">', source)
                card_indexes = [int(value) for value in re.findall(r'<article class="card" data-exercise-index="(\d+)">', source)]
                self.assertEqual(card_indexes, list(range(1, expected_cards[path.name] + 1)))

    def test_routine_navigation_targets_every_exercise_card_in_the_document(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("main.cards > article.card", source)
                self.assertGreaterEqual(
                    source.count("article.card[data-exercise-index]"), 4
                )
                self.assertIn("summaryExercise", source)
                self.assertIn("nextExerciseCue", source)

    def test_all_routines_expose_accessible_segmented_warmup_and_series_progress(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertEqual(source.count('data-enhancement="segmented-progress-bars-v1"'), 1)
                self.assertIn("warmupProgressSegments", source)
                self.assertIn('id="warmupProgress"', source)
                self.assertIn('aria-label="Progreso del calentamiento"', source)
                self.assertIn("warmupProgress.setAttribute('aria-valuenow', String(completedPhases))", source)
                self.assertIn("warmupProgress.dataset.state = progressState", source)
                self.assertEqual(source.count('id="warmupAction"'), 1)
                self.assertIn("warmupActionButton?.addEventListener('click'", source)
                self.assertIn('id="warmupInstructions"', source)
                self.assertIn("Sigue cardio y movilidad en ese orden.", source)
                self.assertNotIn('id="warmupStart"', source)
                self.assertNotIn('id="warmupAdvance"', source)
                self.assertNotIn('id="warmupFinish"', source)
                self.assertNotIn("warmupFinishButton", source)
                self.assertIn("Progreso del calentamiento", source)
                self.assertIn('aria-valuemax="2"', source)
                self.assertIn("seriesProgressSegments", source)
                self.assertIn("Series completadas", source)
                self.assertIn("seriesProgress.setAttribute('aria-valuenow', String(done))", source)
                self.assertIn("segment.classList.toggle('is-complete'", source)
                self.assertIn("seriesProgress.dataset.state = seriesState", source)
                self.assertIn("'empty'", source)
                self.assertIn("'filling'", source)
                self.assertIn("'full'", source)
                self.assertIn("@keyframes progressSweep", source)
                self.assertIn("@keyframes progressPulse", source)
                self.assertIn("@keyframes progressFinish", source)
                self.assertIn("@keyframes progressActiveSweep{from{background-position:100% 0}to{background-position:-120% 0}}", source)
                self.assertNotRegex(source, r"@keyframes progressFinish\s*\{[^}]*transform\s*:")
                self.assertIn("background-size:220% 100%;animation:progressActiveSweep", source)
                self.assertIn("prefers-reduced-motion:reduce", source)

    def test_all_routines_have_well_formed_progress_and_open_licensed_logging_icons(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                progress_style = source.index('<style data-enhancement="segmented-progress-bars-v1">')
                interaction_style = source.index('<style data-enhancement="interaction-feedback-v1">')
                self.assertLess(source.index("</style>", progress_style), interaction_style)
                self.assertIn("createPerformanceIcon('repeat-2')", source)
                self.assertIn("createPerformanceIcon('weight')", source)
                self.assertIn("lucide lucide-repeat-2", source)
                self.assertIn("lucide lucide-weight", source)

    def test_shared_visual_language_uses_local_lucide_sprite_and_keeps_copy_compact(self) -> None:
        expected_icons = (
            "activity", "arrow-left", "dumbbell", "list-checks", "move-up-right",
            "repeat-2", "settings-2", "target", "timer", "triangle-alert", "weight", "wind",
        )
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertEqual(source.count('id="gymratikLucideSprite"'), 1)
                for icon in expected_icons:
                    self.assertIn(f'id="gymratik-icon-{icon}"', source)
                    self.assertIn(f"gymratik-icon-{icon}", source)
                self.assertIn('data-enhancement="visual-language-lucide-v1"', source)
                self.assertIn(".exerciseQuickSummary{display:none!important}", source)
                self.assertIn("Sigue cardio y movilidad en ese orden.", source)
                self.assertNotIn("Sigue las actividades, tiempos y técnica indicados arriba para este día.", source)
                self.assertIn(".note.notePanel{display:none!important}", source)
                self.assertEqual(standardize_visual_language(source), source)

    def test_each_exercise_has_one_dynamic_action_for_approximation_and_sets(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn('class="setButton warmupSet"', source)
                self.assertRegex(source, r'class="setButton warmupSet"[^>]*\shidden')
                self.assertIn('class="completeSetButton"', source)
                self.assertIn('id="exerciseWarmupHint"', source)
                self.assertRegex(source, r'class="exerciseWarmupHint" id="exerciseWarmupHint" hidden')
                self.assertIn("Serie de aproximación", source)
                self.assertIn("__warmupPerformance", source)
                self.assertIn("warmupDurationMs", source)
                self.assertIn("approximationProgress", source)
                self.assertIn("Aproximación activa ·", source)
                self.assertIn("if (warmup && state[warmup.dataset.key] !== true) {", source)
                self.assertIn("state[warmup.dataset.key] = true;", source)
                self.assertIn("const approximationTarget = activeApproximation || (!warmupRecorded ? exerciseItems.find(entry => !snapshot(entry).complete && !snapshot(entry).machinePending) : null);", source)
                self.assertIn("if (item) updatePendingButton(item);\n      exerciseItems.forEach(updateCompleteButton);\n      updateSummary();", source)
                self.assertNotIn("warmup.click(); return;", source)
                self.assertIn("longPressDetected = false; startSeriesButton.style.setProperty('--hold-progress', '0%');", source)
                self.assertIn("button.classList.toggle('is-preparing', preparing)", source)

    def test_routine_audio_and_haptic_feedback_match_session_events(self) -> None:
        expected_cues = ("warmup", "cardio", "mobility", "preparation", "activity", "series", "rest", "exercise", "session")
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("const playFeedback = type => { playMilestoneSound(type); playHaptic(type); };", source)
                self.assertIn("gymratik-haptics-v1", source)
                self.assertIn('id="hapticsToggle"', source)
                self.assertEqual(source.count('id="hapticsToggle"'), 1)
                self.assertIn("exponentialRampToValueAtTime", source)
                for cue in expected_cues:
                    self.assertIn(f"{cue}:", source)

    def test_load_slider_can_be_saved_when_completing_a_series(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("item.performanceLoadOutput = loadOutput", source)
                self.assertIn("item.performanceLoadOutput.textContent = loadUnit", source)
                self.assertNotIn("loadOutput.textContent = loadUnit", source)

    def test_motivation_button_has_multiple_offline_fallback_phrases(self) -> None:
        fallback_phrases = (
            "La constancia convierte cada entrenamiento en progreso.",
            "Una serie bien hecha también cuenta.",
            "El avance se construye repetición a repetición.",
        )
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("if (!motivationalQuotes.length) motivationalQuotes.push(", source)
                for phrase in fallback_phrases:
                    self.assertIn(phrase, source)

    def test_motivation_quotes_are_compact_credited_and_randomized_across_days(self) -> None:
        bank_path = ROOT / "data" / "rutinas_autocontenidas" / "frases_fitness" / "fitness_quotes.json"
        bank = json.loads(bank_path.read_text(encoding="utf-8"))
        compact = compact_payload(bank)
        self.assertGreaterEqual(compact["count"], 23)
        self.assertLessEqual(compact["count"], 60)
        self.assertEqual(len({quote["author"] for quote in compact["quotes"]}), compact["count"] - 2)
        self.assertTrue(all(len(quote["quoteEs"]) <= 220 for quote in compact["quotes"]))
        self.assertFalse(any("MTV fue un gran entrenamiento para mí" in quote["quoteEs"] for quote in compact["quotes"]))
        self.assertFalse(any("Football Manager" in quote["quoteEs"] or "booing" in quote["quoteEs"] for quote in compact["quotes"]))
        self.assertNotIn("Claire Danes", {quote["author"] for quote in compact["quotes"]})
        portrait_root = bank_path.parent
        self.assertTrue(all((portrait_root / quote["portrait"]).is_file() for quote in compact["quotes"]))
        arnold = [quote for quote in compact["quotes"] if quote["author"] == "Arnold Schwarzenegger"]
        self.assertEqual(len(arnold), 3)
        self.assertTrue(all(quote["sourceUrl"].startswith("https://www.schwarzenegger.com/") for quote in arnold))
        self.assertTrue(all(quote["photoCredit"].endswith("CC BY 4.0") for quote in arnold))
        runtime_js = ROOT / "data" / "rutinas_autocontenidas" / "frases_fitness" / "fitness_quotes.js"
        runtime = runtime_js.read_text(encoding="utf-8")
        self.assertIn("window.fitnessQuotesData = ", runtime)
        self.assertLess(runtime_js.stat().st_size, 35_000)
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn('<script defer src="../frases_fitness/fitness_quotes.js"></script>', source)
                self.assertIn("const fitnessQuotePayload = window.fitnessQuotesData || {};", source)
                self.assertIn("const motivationKey = 'gymratik-motivation-rotation-v1';", source)
                self.assertIn("Math.random() * poolSize", source)
                self.assertIn("if (avoidLast && motivationIndex >= lastMotivationIndex)", source)
                self.assertNotIn("motivationIndex = (motivationIndex + 1)", source)
                self.assertIn("window.fitnessQuotesData?.quotes?.length", source)
                self.assertTrue(
                    "photoCreditEl.textContent = phrase.photoLine" in source,
                    f"{path.name}: el crédito de la foto no se enlaza con la frase visible",
                )
                self.assertEqual(source.count("photoCreditEl.textContent = phrase.photoLine"), 1)
                self.assertIn('class="motivationPhotoWrap"', source)
                self.assertEqual(source.count('class="motivationPhotoWrap"'), 1)
                self.assertIn("sessionCompletionCopy p{display:block!important", source)
                self.assertIn("portraitEl.onload = () =>", source)
                self.assertIn("portraitEl.onerror = showPortraitFallback", source)
                self.assertIn("portraitEl.loading = 'eager'", source)
                self.assertIn("portraitEl.hidden = true; initialsEl.hidden = false;", source)
                self.assertNotIn('id="fitnessQuotesPayload"', source)

    def test_shared_technique_template_is_compact_and_identical_across_all_days(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                card_count = len(re.findall(r'<article class="card', source))
                for step_class in ("setup", "move", "warning"):
                    self.assertEqual(source.count(f'class="techStep {step_class}"'), card_count)
                self.assertNotIn('class="techStep control"', source)
                self.assertEqual(source.count('class="techSteps"'), card_count)
                self.assertEqual(source.count('data-enhancement="technique-accordion-v1"'), card_count)
                self.assertEqual(source.count('<summary>Técnica esencial</summary>'), card_count)
                self.assertIn(".techSteps{display:grid!important", source)
                self.assertIn('data-enhancement="summary-free-navigation-v1"', source)
                self.assertNotIn("new MutationObserver(scheduleAlignment)", source)
                self.assertIn("scrollIntoView({behavior:'smooth', block:'start'})", source)
                self.assertIn("width:82px!important;height:82px!important", source)

    def test_day_four_uses_free_barbell_romanian_deadlift_and_owned_local_media(self) -> None:
        path = CANONICAL / "Rutina_Dia_4_Pierna_Equilibrio_V1.html"
        source = path.read_text(encoding="utf-8")
        manifest = json.loads((ROOT / "data/rutinas_autocontenidas/evidencia/dia4_media_manifest.json").read_text(encoding="utf-8"))
        entry = next(item for item in manifest["entries"] if item["repo_id"] == "barbell-rdl-v1")
        self.assertIn("PESO MUERTO RUMANO CON BARRA", source)
        self.assertIn("barbell-rdl-v1.gif", source)
        self.assertIn("Lleva la cadera atrás", source)
        self.assertIn("barra pegada a las piernas", source)
        self.assertIn("barra libre y discos", source)
        self.assertNotIn("PESO MUERTO EN MÁQUINA", source)
        self.assertNotIn("0578-GUT8I22", source)
        self.assertEqual(entry["gif"]["frames"], 72)
        self.assertEqual(entry["equipment_identity_status"], "FREE_BAR_AND_PLATES")
        for key in ("gif", "start", "final", "machine_reference"):
            asset = (ROOT / entry["published"][key]).resolve()
            self.assertTrue(asset.is_file(), f"Falta medio del peso muerto rumano: {asset}")

    def test_all_routines_expose_access_to_homepage(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                match = re.search(
                    r'<a class="routine-home-link" href="([^"]+)"[^>]*>', source
                )
                self.assertIsNotNone(match)
                self.assertEqual((path.parent / match.group(1)).resolve(), ROOT / "index.html")
                self.assertIn('aria-label="Volver a la portada"', source)
                self.assertIn('<span>Portada</span></a>', source)

    def test_all_routines_use_the_shared_liquid_glass_redesign(self) -> None:
        stylesheet = ROOT / "routine-liquid-glass-v13.css"
        self.assertTrue(stylesheet.is_file())
        css = stylesheet.read_text(encoding="utf-8")
        for marker in ("backdrop-filter:blur(18px)", "#ffd166", "prefers-reduced-motion:reduce"):
            self.assertIn(marker, css)
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            with self.subTest(path=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertIn('href="../../../routine-liquid-glass-v13.css"', source)
                self.assertIn('grid-template-areas:"intro meta" "details details"', css)

    def test_all_routines_share_the_canonical_exercise_card_contract(self) -> None:
        required_markers = (
            r'class="machineRefBox(?:\s|\")',
            r'class="muscleRefBox(?:\s|\")',
            r'class="phaseRow(?:\s|\")',
            r'data-exercise-quick-summary',
            r'class="exerciseTracker(?:\s|\")',
            r'class="techSteps(?:\s|\")',
        )
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            cards = re.findall(
                r'<article class="card" data-exercise-index="\d+">.*?</article>',
                source,
                re.S,
            )
            with self.subTest(path=path.name):
                self.assertTrue(cards)
                self.assertIn('data-enhancement="canonical-card-contract-v1"', source)
                for card in cards:
                    for marker in required_markers:
                        self.assertEqual(len(re.findall(marker, card)), 1, marker)

    def test_each_canonical_day_has_its_own_shared_template_cover(self) -> None:
        cover_dir = ROOT / "assets" / "branding" / "routine-covers"
        for day, path in enumerate(sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")), start=1):
            source = path.read_text(encoding="utf-8")
            cover_ref = f"../../../assets/branding/routine-covers/day{day}.webp"
            with self.subTest(day=day, path=path.name):
                self.assertIn(f'data-routine-cover="day{day}"', source)
                self.assertIn(f'src="{cover_ref}"', source)
                self.assertEqual(source.count('class="routineDayCover"'), 1)
                self.assertIn('data-enhancement="routine-day-cover-v1"', source)
                self.assertIn('object-fit:contain', source)
                self.assertIn('width="1536" height="1024"', source)
                self.assertTrue((cover_dir / f"day{day}.webp").is_file())

    def test_all_routines_share_the_realistic_muscle_day_media_contract(self) -> None:
        expected_images = {
            "Rutina_Dia_1_Espalda_Biceps_V1.html": 6,
            "Rutina_Dia_2_Pierna_Gluteo_V1.html": 6,
            "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html": 3,
            "Rutina_Dia_4_Pierna_Equilibrio_V1.html": 6,
        }
        asset_root = ROOT / "data" / "rutinas_autocontenidas" / "medios_publicados"
        manifest = ROOT / "data" / "rutinas_autocontenidas" / "evidencia" / "muscle_day_visuals_manifest.json"
        self.assertTrue(manifest.is_file())
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            items = re.findall(r'<div class="muscleDayItem"[^>]*>', source)
            images = re.findall(
                r'<img class="muscleDayImage"[^>]+src="([^"]+)"[^>]+alt="([^"]+)"',
                source,
            )
            with self.subTest(path=path.name):
                self.assertEqual(len(items), expected_images[path.name])
                self.assertEqual(len(images), expected_images[path.name])
                self.assertIn('muscle-day-realistic-media-v1', source)
                self.assertIn('muscle-day-image-fallback-v1', source)
                for reference, alt in images:
                    self.assertTrue(alt.startswith("Referencia anatómica ilustrativa"))
                    self.assertTrue((path.parent / reference).is_file(), reference)
                self.assertTrue(all((asset_root / name).is_file() for name in (
                    "rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp",
                    "rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp",
                    "rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp",
                    "rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp",
                )))

    def test_all_routines_keep_specific_muscle_focus_and_valid_document_structure(self) -> None:
        expected = {
            "Rutina_Dia_1_Espalda_Biceps_V1.html": {
                "Dorsal ancho": ("latissimus", "posterior", "upper-posterior"),
                "Romboides": ("rhomboids", "posterior", "upper-posterior"),
                "Trapecio medio": ("middle-trapezius", "posterior", "upper-posterior"),
                "Deltoides posterior": ("rear-deltoid", "posterior", "upper-posterior"),
                "Bíceps braquial": ("biceps", "anterior", "upper-anterior"),
                "Pectoral mayor": ("pectoralis-major", "anterior", "upper-anterior"),
            },
            "Rutina_Dia_2_Pierna_Gluteo_V1.html": {
                "Cuádriceps": ("quadriceps", "anterior", "lower-anterior"),
                "Glúteo mayor": ("gluteus-maximus", "posterior", "lower-posterior"),
                "Isquiosurales": ("hamstrings", "posterior", "lower-posterior"),
                "Aductores": ("adductors", "anterior", "lower-anterior"),
                "Gastrocnemio": ("gastrocnemius", "posterior", "lower-posterior"),
                "Sóleo": ("soleus", "posterior", "lower-posterior"),
            },
            "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html": {
                "Pectoral mayor": ("pectoralis-major", "anterior", "upper-anterior"),
                "Deltoides": ("deltoid", "anterior", "upper-anterior"),
                "Tríceps": ("triceps", "posterior", "upper-posterior"),
            },
            "Rutina_Dia_4_Pierna_Equilibrio_V1.html": {
                "Cuádriceps": ("quadriceps", "anterior", "lower-anterior"),
                "Glúteo mayor": ("gluteus-maximus", "posterior", "lower-posterior"),
                "Isquiosurales": ("hamstrings", "posterior", "lower-posterior"),
                "Abductores": ("abductors", "posterior", "lower-posterior"),
                "Aductores": ("adductors", "anterior", "lower-anterior"),
                "Gastrocnemio": ("gastrocnemius", "posterior", "lower-posterior"),
            },
        }
        item_pattern = re.compile(
            r'<div class="muscleDayItem"[^>]*data-muscle-focus="([^"]+)"'
            r'[^>]*data-muscle-view="([^"]+)"[^>]*data-muscle-visual="([^"]+)"'
            r'[^>]*>.*?<span class="muscleName">([^<]+)</span>',
            re.S,
        )
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            observed = {
                name: (focus, view, visual)
                for focus, view, visual, name in item_pattern.findall(source)
            }
            with self.subTest(path=path.name):
                self.assertIn("</head>", source)
                self.assertIn("<body>", source)
                self.assertIn('<header class="hero">', source)
                self.assertIn('data-fix="muscle-specific-focus-v1"', source)
                self.assertEqual(observed, expected[path.name])
                if path.name == "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html":
                    self.assertIn(
                        'data-muscle-focus="triceps" data-muscle-view="posterior" '
                        'data-muscle-visual="upper-posterior"',
                        source,
                    )

    def test_all_routines_keep_explicit_anatomical_focus_markers(self) -> None:
        bilateral = {
            "Dorsal ancho",
            "Romboides",
            "Trapecio medio",
            "Deltoides posterior",
            "Bíceps braquial",
            "Pectoral mayor",
            "Cuádriceps",
            "Glúteo mayor",
            "Isquiosurales",
            "Aductores",
            "Abductores",
            "Gastrocnemio",
            "Sóleo",
            "Deltoides",
            "Tríceps",
        }
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            items = re.findall(r'<div class="muscleDayItem"[^>]*>.*?</div>', source, flags=re.S)
            for item in items:
                name_match = re.search(r'<span class="muscleName">([^<]+)</span>', item)
                self.assertIsNotNone(name_match, f"Tarjeta sin nombre: {path.name}")
                name = name_match.group(1)
                marker_count = len(re.findall(r'class="muscleFocusMarker"', item))
                with self.subTest(path=path.name, muscle=name):
                    self.assertEqual(marker_count, 2 if name in bilateral else 1)
                    self.assertIn('data-enhancement="muscle-marker-precision-v2"', source)
                    self.assertIn('data-enhancement="mobile-first-muscle-grid-v1"', source)
                    self.assertIn("--marker-x:", item)
                    self.assertIn("--marker-y:", item)

    def test_all_routines_keep_phase_media_readable_on_dark_ui(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            source = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn('data-fix="phase-media-clarity-v5"', source)
                self.assertIn("article.card .phaseRow .photo img.realphoto{", source)
                self.assertIn("background:transparent!important;", source)
                self.assertIn("mix-blend-mode:normal!important;", source)
                self.assertIn('data-fix="day1-rowing-phase-pair-v1"', source)
                self.assertIn("1350-7I6LNUG.jpg", source)
                self.assertIn("1350-7I6LNUG-final.png", source)
                if path.name == "Rutina_Dia_1_Espalda_Biceps_V1.html":
                    self.assertIn(
                        "panatta-super-high-row-unilateral-start.webp",
                        source,
                    )
                    self.assertIn(
                        "panatta-super-high-row-unilateral-final.webp",
                        source,
                    )
                self.assertIn('data-enhancement="warmup-motion-zoom-v2"', source)
                self.assertIn("object-fit:contain!important}", source)


if __name__ == "__main__":
    unittest.main()
