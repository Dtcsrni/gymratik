"""Regresiones para pausar animaciones que no son visibles en la PWA."""

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from repair_day1_canonical import apply_battery_motion  # noqa: E402


class BatteryAwareMotionTests(unittest.TestCase):
    def test_enhancement_is_idempotent_and_pauses_hidden_or_offscreen_motion(self) -> None:
        source = "<html><head></head><body></body></html>"
        once = apply_battery_motion(source, "\n")
        twice = apply_battery_motion(once, "\n")

        self.assertEqual(once, twice)
        self.assertEqual(once.count('data-enhancement="battery-aware-motion-v1"'), 2)
        self.assertIn("document.addEventListener('visibilitychange', syncVisibility", once)
        self.assertIn("new IntersectionObserver(", once)
        self.assertIn("setAttribute('data-motion-paused', String(!entry.isIntersecting))", once)
        self.assertIn("animation-play-state:paused!important", once)
        self.assertIn("rootMargin: '96px 0px'", once)

    def test_all_canonical_routines_include_battery_aware_motion(self) -> None:
        routines = sorted((ROOT / "data/rutinas_autocontenidas/canonicas").glob("Rutina_Dia_*_V1.html"))
        self.assertEqual(len(routines), 4)
        for path in routines:
            with self.subTest(routine=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertEqual(source.count('data-enhancement="battery-aware-motion-v1"'), 2)
                self.assertIn("document.addEventListener('visibilitychange', syncVisibility", source)
                self.assertIn("new IntersectionObserver(", source)
                self.assertIn("setAttribute('data-motion-paused', String(!entry.isIntersecting))", source)
                self.assertNotIn("toggleAttribute('data-motion-paused'", source)


if __name__ == "__main__":
    unittest.main()
