from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_routine_media import validate_path  # noqa: E402


CANONICAL = ROOT / "data" / "rutinas_autocontenidas" / "canonicas"


class RoutineMediaValidationTests(unittest.TestCase):
    def test_current_canonical_media_references_exist(self) -> None:
        for path in sorted(CANONICAL.glob("*.html")):
            with self.subTest(path=path.name):
                self.assertEqual(validate_path(path), [])

    def test_missing_media_is_reported(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = Path(directory)
            html = root / "routine.html"
            html.write_text(
                '<img src="missing.gif" alt="GIF del ejercicio">', encoding="utf-8"
            )
            errors = validate_path(html)
        self.assertTrue(any("medio faltante" in error for error in errors))

    def test_derived_static_media_reference_is_reported(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = Path(directory)
            image = root / "motion.gif"
            image.write_bytes(b"fixture")
            html = root / "routine.html"
            html.write_text(
                '<img src="motion.gif" data-static-src="missing.jpg" alt="GIF con respaldo">',
                encoding="utf-8",
            )
            errors = validate_path(html)
        self.assertTrue(any("medio faltante" in error and "missing.jpg" in error for error in errors))

    def test_script_portrait_media_reference_is_reported(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = Path(directory)
            html = root / "routine.html"
            html.write_text(
                '<script>const quote = { portrait: "retratos/missing.jpg" };</script>',
                encoding="utf-8",
            )
            errors = validate_path(html)
        self.assertTrue(any("medio faltante" in error and "missing.jpg" in error for error in errors))

    def test_ignored_artifacts_reference_is_reported(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = Path(directory)
            html = root / "routine.html"
            html.write_text(
                '<img src="../../artifacts/hidden.gif" alt="GIF fuera de publicación">',
                encoding="utf-8",
            )
            errors = validate_path(html)
        self.assertTrue(any("ruta no publicable bajo artifacts" in error for error in errors))

    def test_content_image_without_alt_is_reported(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            root = Path(directory)
            image = root / "image.jpg"
            image.write_bytes(b"fixture")
            html = root / "routine.html"
            html.write_text('<img src="image.jpg">', encoding="utf-8")
            errors = validate_path(html)
        self.assertTrue(any("sin alt" in error for error in errors))

    def test_day1_media_mapping_order_is_detected(self) -> None:
        source = (CANONICAL / "Rutina_Dia_1_Espalda_Biceps_V1.html").read_text(
            encoding="utf-8"
        )
        mutated = source.replace(
            'key:"APERTURA INVERSA EN MÁQUINA"',
            'key:"REMO HORIZONTAL EN MÁQUINA"',
            1,
        )
        with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as directory:
            path = Path(directory) / "Rutina_Dia_1_Espalda_Biceps_V1.html"
            path.write_text(mutated, encoding="utf-8")
            errors = validate_path(path)
        self.assertTrue(any("mapa de GIFs esperado" in error for error in errors))

    def test_all_four_routines_require_seven_real_exercise_gifs(self) -> None:
        for path in sorted(CANONICAL.glob("Rutina_Dia_*_V1.html")):
            with self.subTest(routine=path.name):
                source = path.read_text(encoding="utf-8")
                self.assertEqual(validate_path(path), [])
                self.assertNotRegex(
                    source,
                    r"<(?:animate|animateTransform|animateMotion|set)\b",
                )

    def test_hip_thrust_uses_the_documented_official_gif(self) -> None:
        source = (CANONICAL / "Rutina_Dia_2_Pierna_Gluteo_V1.html").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "hip_thrust_machine_booty_builder_correct_form.gif", source
        )
        self.assertIn("https://bootybuilder.com/how-to-use-the-booty-builder/", source)
        self.assertIn('key:"HIP THRUST"', source)


if __name__ == "__main__":
    unittest.main()
