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

    def test_injects_large_readable_mixed_unit_selector_and_exact_load_transfer(self) -> None:
        result = apply_plate_picker_contract(self.source)

        for marker in (
            'data-enhancement="plate-picker-v1"',
            ".platePicker .platePickerUnits{display:flex!important;flex-direction:column!important;align-items:stretch!important",
            "grid-template-rows:auto auto minmax(0,1fr) auto;overflow:hidden",
            "max-height:min(52svh,480px)",
            "const fitPlatePickerAboveSessionBar = () => requestAnimationFrame",
            "grid-template-rows:64px auto;justify-items:center",
            ".platePickerDiscFace",
            "width:var(--plate-size,50px);height:var(--plate-size,50px)",
            "platePickerDiscValue",
            "platePickerGroups.className = 'platePickerUnits'",
            "const plateKg = loadMath.toKg(weight, unit)",
            "const plateSize = 34 + 28 * Math.max(0,Math.min(1,(Math.sqrt(plateKg)-minRoot)/(maxRoot-minRoot)))",
            "tile.style.setProperty('--plate-size'",
            "Discos · libras (lb)",
            "Discos · kilogramos (kg)",
            "Toca + para añadir una pieza",
            "0 kg · 0 lb",
            "Carga recibirá",
            "[45,35,25,20,15,10,5,2.5]",
            "[25,20,15,10,5,2.5,1.25,0.5,0.25]",
            "loadMath.toKg(weight * count, unit)",
            "totalKg >= item.performanceLoadProfile.minKg",
            "item.platePickerExactLoadKg = totalKg",
            "item.performanceLoadExact = loadMath.toDisplay(totalKg, item.performanceLoadUnit)",
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

    def test_existing_picker_styles_are_upgraded_in_place(self) -> None:
        source = self.source.replace(
            "<head></head>",
            '<head><style data-enhancement="plate-picker-v1">.platePickerGrid{columns:2}</style></head>',
        )

        updated = apply_plate_picker_contract(source)

        self.assertIn(".platePicker .platePickerUnits{display:flex!important", updated)
        self.assertNotIn("columns:2", updated)
        self.assertEqual(updated.count('data-enhancement="plate-picker-v1"'), 1)

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
                self.assertIn(".platePicker .platePickerUnits{display:flex!important;flex-direction:column!important", source)
                self.assertIn("grid-template-rows:auto auto minmax(0,1fr) auto;overflow:hidden", source)
                self.assertIn("max-height:min(52svh,480px)", source)
                self.assertIn("Toca + para añadir una pieza", source)
                self.assertIn("platePickerDiscValue", source)
                self.assertIn("platePickerExactLoadKg = totalKg", source)
                picker_start = source.index("const platePickerToggle")
                picker_end = source.index("const progressionCue", picker_start)
                picker_markup = source[picker_start:picker_end]
                self.assertNotIn("gymratik-plate-dark.webp", picker_markup)
                self.assertIn("grid-template-rows:64px auto", source)
                self.assertIn("const plateKg = loadMath.toKg(weight, unit)", source)
                self.assertIn("tile.style.setProperty('--plate-size'", source)
                self.assertIn("loadInput.step = hasExactPlateLoad ? 'any' : String(unitStep)", source)
                self.assertIn("platePickerExactLoadKg: item.platePickerExactLoadKg", source)
                self.assertIn("item.platePickerExactLoadKg != null ? loadMath.toDisplay(kilograms, nextUnit)", source)


if __name__ == "__main__":
    unittest.main()
