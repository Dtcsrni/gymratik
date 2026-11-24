from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from build_day4_barbell_rdl_media import pose_points  # noqa: E402


class RomanianDeadliftKinematicsTests(unittest.TestCase):
    def test_knees_keep_a_small_bend_through_the_hip_hinge(self) -> None:
        for hinge in (0, 0.25, 0.5, 0.75, 1):
            with self.subTest(hinge=hinge):
                points = pose_points(hinge)
                knee_to_hip = (points["hip"][0] - points["knee"][0], points["hip"][1] - points["knee"][1])
                knee_to_ankle = (points["ankle"][0] - points["knee"][0], points["ankle"][1] - points["knee"][1])
                cosine = sum(a * b for a, b in zip(knee_to_hip, knee_to_ankle)) / (
                    math.hypot(*knee_to_hip) * math.hypot(*knee_to_ankle)
                )
                angle = math.degrees(math.acos(max(-1, min(1, cosine))))
                self.assertGreaterEqual(angle, 155)
                self.assertLess(angle, 180)

    def test_hip_moves_back_more_than_the_knee_and_feet_stay_planted(self) -> None:
        start = pose_points(0)
        bottom = pose_points(1)

        self.assertEqual(start["ankle"], bottom["ankle"])
        self.assertGreater(start["hip"][0] - bottom["hip"][0], start["knee"][0] - bottom["knee"][0])


if __name__ == "__main__":
    unittest.main()
