from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageChops

from scripts.build_day1_reverse_fly_still import FINAL_HOLD_FRAME, ROOT, SOURCE, build_final_pose


class ReverseFlyStillTests(unittest.TestCase):
    def test_day_one_final_phase_uses_the_open_arm_pose(self) -> None:
        routine = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html"
        html = routine.read_text(encoding="utf-8")
        self.assertIn("images/0602-myfUsKf-final.png", html)
        self.assertIn("brazos abiertos en línea con el torso", html)

    def test_export_uses_stable_full_resolution_end_position(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = build_final_pose(SOURCE, Path(temporary) / "reverse-fly-final.png")
            with Image.open(SOURCE) as animation, Image.open(output) as still:
                animation.seek(FINAL_HOLD_FRAME)
                expected = animation.convert("RGB")
                self.assertEqual(still.size, (180, 180))
                self.assertIsNone(ImageChops.difference(expected, still).getbbox())


if __name__ == "__main__":
    unittest.main()
