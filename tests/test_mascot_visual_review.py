from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PIL import Image

from scripts import build_pwa_service_worker as worker


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/mascot_exercise_motion/visual-review.json"


class MascotVisualReviewTests(unittest.TestCase):
    def test_generic_status_mascots_have_distinct_gendered_pose_assets(self) -> None:
        root = ROOT / "data/profile/mascot-motion/states-v1"
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
        states = manifest["states"]
        self.assertEqual(len(states), 9)
        self.assertEqual(manifest["atlasLayout"]["outputSize"], [128, 128])
        for variant in ("male", "female"):
            for state in states:
                path = root / f"{variant}-{state}.png"
                with self.subTest(variant=variant, state=state):
                    self.assertTrue(path.is_file(), f"Falta pose de estado: {path}")
                    with Image.open(path) as image:
                        self.assertEqual(image.size, (128, 128))
                        self.assertEqual(image.mode, "RGBA")
                        self.assertEqual(image.getchannel("A").getextrema()[0], 0)

    def test_rejected_pose_cannot_be_precached(self) -> None:
        review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
        self.assertEqual(review["requiredExerciseCount"], 26)
        self.assertEqual(review["reviews"]["day1-exercise01"]["status"], "rejected")
        self.assertFalse(review["reviews"]["day1-exercise01"]["bodyOrientationVerified"])
        self.assertEqual(review["reviews"]["day1-exercise02"]["status"], "rejected")
        self.assertFalse(review["reviews"]["day1-exercise02"]["gripAndContactVerified"])
        resource = "./data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/mascot_exercise_motion/day1-exercise01-lat-pulldown-25fps.gif"
        with self.assertRaisesRegex(SystemExit, "sin aprobación visual estricta"):
            worker.validate_mascot_motion_reviews({resource})

    def test_precache_requires_every_machine_pose_and_loop_check(self) -> None:
        resource = "./data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/mascot_exercise_motion/day1-exercise02-row-25fps.gif"
        entry = {
            "status": "approved",
            "angle": "three-quarter side",
            "machineReference": "canonical routine and exact machine photos",
            **{field: True for field in worker.MOTION_REVIEW_FIELDS},
        }
        with TemporaryDirectory() as temporary:
            review_path = Path(temporary) / "visual-review.json"
            review_path.write_text(json.dumps({"reviews": {"day1-exercise02": entry}}), encoding="utf-8")
            with patch.object(worker, "MOTION_REVIEW", review_path):
                worker.validate_mascot_motion_reviews({resource})
                entry["bodyOrientationVerified"] = False
                review_path.write_text(json.dumps({"reviews": {"day1-exercise02": entry}}), encoding="utf-8")
                with self.assertRaisesRegex(SystemExit, "sin aprobación visual estricta"):
                    worker.validate_mascot_motion_reviews({resource})

    def test_unapproved_prototypes_are_not_referenced_by_any_canonical_routine(self) -> None:
        routines = (ROOT / "data/rutinas_autocontenidas/canonicas").glob("Rutina_Dia_*_V1.html")
        for path in routines:
            with self.subTest(routine=path.name):
                self.assertNotIn("mascot_exercise_motion/", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
