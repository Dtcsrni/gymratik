from __future__ import annotations

import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

from PIL import Image, ImageChops

from scripts.build_modular_krita_source import build_project


class ModularKritaSourceTests(unittest.TestCase):
    def test_builds_layered_machine_character_and_two_exercise_states(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary)
            ora_path, start_preview = build_project(output_dir)
            finish_preview = output_dir / "preview-pulled.png"

            with ZipFile(ora_path) as archive:
                self.assertIsNone(archive.testzip())
                image = ElementTree.fromstring(archive.read("stack.xml"))
                layer_stack = image.find("stack")
                self.assertIsNotNone(layer_stack)
                layers = list(layer_stack)
                names = {layer.attrib["name"]: layer.attrib["visibility"] for layer in layers}
                self.assertEqual(len(layers), 14)
                self.assertEqual(names["Brazos y manos · inicio"], "visible")
                self.assertEqual(names["Barra · arriba"], "visible")
                self.assertEqual(names["Brazos y manos · jalón"], "hidden")
                self.assertEqual(names["Placas de carga · elevadas (jalón)"], "hidden")
                self.assertEqual(names["Estructura, polea y soporte"], "visible")
                for layer in layers:
                    png = archive.read(layer.attrib["src"])
                    with Image.open(BytesIO(png)) as bitmap:
                        self.assertEqual(bitmap.size, (800, 900))
                    self.assertTrue((output_dir / "parts" / f"{Path(layer.attrib['src']).stem}.svg").is_file())

            for filename, expected_layers in (("character.ora", 5), ("machine.ora", 9)):
                with ZipFile(output_dir / filename) as archive:
                    self.assertIsNone(archive.testzip())
                    module = ElementTree.fromstring(archive.read("stack.xml"))
                    module_stack = module.find("stack")
                    self.assertIsNotNone(module_stack)
                    module_layers = list(module_stack)
                    self.assertEqual(len(module_layers), expected_layers)
                    self.assertTrue(all(layer.attrib["visibility"] in {"visible", "hidden"} for layer in module_layers))
                    for layer in module_layers:
                        with Image.open(BytesIO(archive.read(layer.attrib["src"]))) as bitmap:
                            self.assertEqual(bitmap.size, (800, 900))
            with ZipFile(output_dir / "character.ora") as archive:
                character_layers = {layer.attrib["name"]: layer.attrib["visibility"] for layer in ElementTree.fromstring(archive.read("stack.xml")).find("stack")}
                self.assertEqual(character_layers["Brazos · pose inicial"], "visible")
                self.assertEqual(character_layers["Brazos · pose de jalón"], "hidden")
            with ZipFile(output_dir / "machine.ora") as archive:
                machine_layers = {layer.attrib["name"]: layer.attrib["visibility"] for layer in ElementTree.fromstring(archive.read("stack.xml")).find("stack")}
                self.assertEqual(machine_layers["Barra · posición elevada"], "visible")
                self.assertEqual(machine_layers["Barra · posición al pecho"], "hidden")

            with Image.open(start_preview) as start, Image.open(finish_preview) as finish:
                self.assertEqual(start.size, (800, 900))
                self.assertIsNotNone(ImageChops.difference(start, finish).getbbox())

            editable_part = output_dir / "parts" / "arms-start.svg"
            authored = editable_part.read_text(encoding="utf-8")
            editable_part.write_text(authored.replace("</svg>", "<!-- edición conservada -->\n</svg>"), encoding="utf-8")
            build_project(output_dir)
            self.assertIn("edición conservada", editable_part.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
