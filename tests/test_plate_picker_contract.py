from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from plate_picker_contract import apply_plate_picker_contract  # noqa: E402


class PlatePickerContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = (
            "<head></head><script>"
            "loadLabel.append(loadHead, loadOutputRow, loadInput);\n"
            "    const savedReps = Number(savedDraft?.reps);"
            "</script>"
        )

    def test_injects_mixed_unit_visual_selector_and_existing_load_commit(self) -> None:
        result = apply_plate_picker_contract(self.source)

        for marker in (
            'data-enhancement="plate-picker-v1"',
            ".platePickerUnits{display:grid;grid-template-columns:minmax(0,1fr)",
            "grid-template-rows:auto auto minmax(0,1fr) auto;overflow:hidden",
            "max-height:min(52svh,480px)",
            "const fitPlatePickerAboveSessionBar = () => requestAnimationFrame",
            "grid-template-rows:1fr;justify-items:center",
            ".platePickerOption{display:grid;justify-items:center;align-content:center;gap:.1rem;width:100%;min-width:0;min-height:64px",
            "platePickerGroups.className = 'platePickerUnits'",
            "Discos en lb",
            "Discos en kg",
            "desplázate para ver kg y mezclar unidades",
            "Sin discos seleccionados",
            "No incluye barra ni máquina.",
            "[45,35,25,20,15,10,5,2.5]",
            "[25,20,15,10,5,2.5,1.25,0.5,0.25]",
            "loadMath.toKg(weight * count, unit)",
            "totalKg >= item.performanceLoadProfile.minKg",
            "item.performanceLoadExact = loadMath.toDisplay(normalizedKg, item.performanceLoadUnit)",
            "savePerformanceDraft()",
            "barra ni máquina",
            "aria-expanded",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, result)

    def test_injection_is_idempotent(self) -> None:
        once = apply_plate_picker_contract(self.source)
        twice = apply_plate_picker_contract(once)

        self.assertEqual(once, twice)

    def test_missing_insertion_point_fails_explicitly(self) -> None:
        with self.assertRaisesRegex(ValueError, "selector base de carga"):
            apply_plate_picker_contract("<head></head><script></script>")

    def test_all_canonical_routines_ship_the_same_selector(self) -> None:
        routines = sorted((ROOT / "data/rutinas_autocontenidas/canonicas").glob("Rutina_Dia_*_V1.html"))

        self.assertEqual(len(routines), 4)
        for routine in routines:
            with self.subTest(routine=routine.name):
                source = routine.read_text(encoding="utf-8")
                self.assertIn('data-enhancement="plate-picker-v1"', source)
                self.assertIn("className = 'platePickerToggle'", source)
                self.assertIn("platePickerGroups.className = 'platePickerUnits'", source)
                self.assertIn(".platePickerUnits{display:grid;grid-template-columns:minmax(0,1fr)", source)
                self.assertIn("grid-template-rows:auto auto minmax(0,1fr) auto;overflow:hidden", source)
                self.assertIn("max-height:min(52svh,480px)", source)
                self.assertIn("desplázate para ver kg y mezclar unidades", source)
                self.assertIn("gymratik-plate-dark.webp", source)


if __name__ == "__main__":
    unittest.main()
