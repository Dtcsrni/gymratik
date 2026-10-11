from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

from PIL import Image, ImageDraw

from scripts.build_krita_pose_source import create_project


class KritaPoseSourceTests(unittest.TestCase):
    def test_builds_standard_layered_openraster_document(self) -> None:
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as temp_dir:
            root = Path(temp_dir)
            sheet_path = root / "day9-exercise02-test-sheet.png"
            output_path = root / "editable" / "test.ora"
            sheet = Image.new("RGB", (40, 40), "white")
            draw = ImageDraw.Draw(sheet)
            draw.rectangle((0, 0, 19, 19), fill="red")
            draw.rectangle((20, 0, 39, 19), fill="green")
            draw.rectangle((0, 20, 19, 39), fill="blue")
            draw.rectangle((20, 20, 39, 39), fill="yellow")
            sheet.save(sheet_path)

            result = create_project(sheet_path, output_path)

            self.assertEqual(result, output_path)
            with ZipFile(result) as archive:
                self.assertIsNone(archive.testzip())
                stack = ElementTree.fromstring(archive.read("stack.xml"))
                layer_stack = stack.find("stack")
                self.assertIsNotNone(layer_stack)
                layers = list(layer_stack)
                poses = [layer for layer in layers if layer.attrib["name"].startswith("Pose ")]
                visible = [layer for layer in poses if layer.attrib["visibility"] == "visible"]
                self.assertEqual((stack.attrib["w"], stack.attrib["h"]), ("20", "20"))
                self.assertEqual(len(poses), 4)
                self.assertEqual(len(visible), 1)
                self.assertEqual(layers[0].attrib["visibility"], "hidden")


if __name__ == "__main__":
    unittest.main()
