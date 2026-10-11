from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "data/rutinas_autocontenidas/canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html"
BUILDER = ROOT / "scripts/build_day2_canonical.py"


class Day2HipThrustVisualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.builder = BUILDER.read_text(encoding="utf-8")
        start_match = re.search(r'<article\b(?=[^>]*\bdata-exercise-index="2")[^>]*>', cls.html)
        end_match = re.search(r'<article\b(?=[^>]*\bdata-exercise-index="3")[^>]*>', cls.html)
        if start_match is None or end_match is None:
            raise AssertionError("No se encontraron las tarjetas 2 y 3 del Día 2 por data-exercise-index")
        start = start_match.start()
        end = end_match.start()
        cls.card = cls.html[start:end]

    def test_card_uses_machine_photo_and_does_not_render_mismatched_motion_art(self) -> None:
        self.assertRegex(self.card, r'<div class="machineRefBox"><img alt="Máquina de hip thrust" src="data:image/jpeg;base64,')
        for incorrect_asset in (
            "hip_thrust_panatta_guide.svg",
            "hip_thrust_panatta_inicio.svg",
            "hip_thrust_panatta_final.svg",
            "hip_thrust_machine_booty_builder_correct_form.gif",
        ):
            with self.subTest(asset=incorrect_asset):
                self.assertNotIn(incorrect_asset, self.card)
        self.assertNotIn('class="gifProof"', self.card)

    def test_technique_copy_matches_manufacturer_machine_contact_points(self) -> None:
        self.assertIn('aria-label="Puntos de colocación y recorrido del hip thrust en máquina"', self.card)
        self.assertIn("Espalda y cabeza apoyadas", self.card)
        self.assertIn("pies firmes en la plataforma", self.card)
        self.assertIn("rodillo acolchado sobre el abdomen bajo", self.card)
        self.assertIn("zona lumbar estable", self.card)
        self.assertIn("sin arquear la zona lumbar", self.card)

    def test_video_is_opt_in_official_model_reference(self) -> None:
        self.assertIn('href="https://www.youtube.com/watch?v=lMk6ZFXbY00"', self.card)
        self.assertIn('target="_blank" rel="noopener noreferrer"', self.card)
        self.assertIn("Ver demostración oficial · Panatta Fit Evo", self.card)

    def test_builder_no_longer_injects_generated_hip_thrust_motion(self) -> None:
        self.assertNotIn("hip_thrust_panatta_guide.svg", self.builder)
        self.assertNotIn('key:"HIP THRUST"', self.builder)
        self.assertIn("hipThrustGuide", self.builder)


if __name__ == "__main__":
    unittest.main()
