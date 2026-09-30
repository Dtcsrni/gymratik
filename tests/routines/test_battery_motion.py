"""Regresiones para pausar animaciones que no son visibles en la PWA."""

import sys
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from repair_day1_canonical import apply_battery_motion  # noqa: E402
from standardize_muscle_visuals import standardize_muscle_visuals  # noqa: E402


class BatteryAwareMotionTests(unittest.TestCase):
    def test_enhancement_is_idempotent_and_pauses_hidden_or_offscreen_motion(self) -> None:
        source = "<html><head></head><body></body></html>"
        once = apply_battery_motion(source, "\n")
        twice = apply_battery_motion(once, "\n")

        self.assertEqual(once, twice)
        self.assertEqual(once.count('data-enhancement="battery-aware-motion-v1"'), 2)
        self.assertIn("document.addEventListener('visibilitychange', syncAllMotion", once)
        self.assertIn("new IntersectionObserver(", once)
        self.assertIn("setAttribute('data-motion-paused', String(!entry.isIntersecting))", once)
        self.assertIn("animation-play-state:paused!important", once)
        self.assertIn('[data-motion-paused="true"],[data-motion-paused="true"] *', once)
        self.assertIn('html.is-document-hidden,html.is-document-hidden *', once)
        self.assertIn("rootMargin: '96px 0px'", once)
        self.assertIn("image.setAttribute('src', posterSrc)", once)
        self.assertIn("image.dataset.staticSrc || image.getAttribute('data-static-src')", once)
        self.assertIn("image.setAttribute('src', source)", once)
        self.assertIn("new MutationObserver(records", once)
        self.assertIn("const frame = image.closest('.warmupVisual,.gifFrame') || image", once)
        self.assertIn("mediaObserver.observe(frame)", once)
        self.assertIn("frameVisibility.set(entry.target, entry.isIntersecting)", once)
        self.assertIn("for (const image of imagesByFrame.get(entry.target) || [])", once)
        self.assertIn("mediaMutationObserver.observe(document.documentElement", once)
        for selector in ("img.day3ExerciseGif", "img.day4ExerciseGif", ".day3ExerciseGif", ".day4ExerciseGif"):
            self.assertIn(selector, once)

    def test_existing_battery_style_is_upgraded_to_pause_animated_container_itself(self) -> None:
        source = (
            '<html><head><style data-enhancement="battery-aware-motion-v1">'
            '[data-motion-paused="true"] *{animation-play-state:paused!important}'
            '</style></head><body></body></html>'
        )

        upgraded = apply_battery_motion(source, "\n")

        self.assertIn('[data-motion-paused="true"],[data-motion-paused="true"] *', upgraded)
        self.assertIn('html.is-document-hidden,html.is-document-hidden *', upgraded)

    def test_all_canonical_routines_include_battery_aware_motion(self) -> None:
        routines = sorted((ROOT / "data/rutinas_autocontenidas/canonicas").glob("Rutina_Dia_*_V1.html"))
        self.assertEqual(len(routines), 4)
        for path in routines:
            with self.subTest(routine=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertEqual(source.count('data-enhancement="battery-aware-motion-v1"'), 2)
                self.assertIn("document.addEventListener('visibilitychange', syncAllMotion", source)
                self.assertIn("new IntersectionObserver(", source)
                self.assertIn("setAttribute('data-motion-paused', String(!entry.isIntersecting))", source)
                self.assertIn("img.gifMotion,img.warmupGif,img.day3ExerciseGif,img.day4ExerciseGif", source)
                self.assertIn("image.dataset.staticSrc || image.getAttribute('data-static-src')", source)
                self.assertIn('[data-motion-paused="true"],[data-motion-paused="true"] *', source)
                self.assertIn('html.is-document-hidden,html.is-document-hidden *', source)
                self.assertNotIn("toggleAttribute('data-motion-paused'", source)
                self.assertIn("mediaMutationObserver.observe(document.documentElement", source)
                self.assertIn("mediaObserver.observe(frame)", source)
                self.assertIn("const syncTimingInterval = () =>", source)
                self.assertIn("window.clearInterval(timingInterval)", source)
                self.assertIn("if (document.hidden) return;", source)
                self.assertIn("timingInterval = window.setInterval(refreshTimingDisplays, 1000)", source)

    def test_shared_routine_generator_recreates_battery_contract(self) -> None:
        path = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html"
        source = path.read_text(encoding="utf-8")
        source = re.sub(r'<style data-enhancement="battery-aware-motion-v1">.*?</style>', "", source, count=1, flags=re.S)
        source = re.sub(r'<script data-enhancement="battery-aware-motion-v1">.*?</script>', "", source, count=1, flags=re.S)
        rebuilt = standardize_muscle_visuals(source)
        self.assertEqual(rebuilt.count('data-enhancement="battery-aware-motion-v1"'), 2)
        self.assertIn("mediaMutationObserver.observe(document.documentElement", rebuilt)
        self.assertIn("window.clearInterval(timingInterval)", rebuilt)


if __name__ == "__main__":
    unittest.main()
