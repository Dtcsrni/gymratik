import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SRS = ROOT / "docs" / "01-requirements" / "SRS.md"
TDD = ROOT / "docs" / "05-quality" / "TDD-005-pwa-perfil-e2e.md"
TRACEABILITY = ROOT / "docs" / "00-governance" / "TRACEABILITY.md"

APPLICABLE_NFR = {
    "NFR-REL-001", "NFR-REL-002", "NFR-AVA-001", "NFR-REC-001",
    "NFR-SEC-002", "NFR-SEC-003", "NFR-PRI-001", "NFR-PRI-002",
    "NFR-PRI-003", "NFR-USA-001", "NFR-USA-002", "NFR-MAI-002",
    "NFR-COM-001",
}


class PwaTraceabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srs = SRS.read_text(encoding="utf-8")
        cls.tdd = TDD.read_text(encoding="utf-8")
        cls.traceability = TRACEABILITY.read_text(encoding="utf-8")

    def test_every_pwa_and_profile_functional_requirement_has_a_tdd_case(self):
        scope = self.srs.split("## 5. Requisitos no funcionales", 1)[0]
        required = set(re.findall(r"\bFUN-(?:PWA|PRO)-\d{3}\b", scope))
        documented = set(re.findall(r"\bFUN-(?:PWA|PRO)-\d{3}\b", self.tdd))
        self.assertEqual(required, documented)
        for requirement in sorted(required):
            self.assertRegex(self.tdd, rf"\| {requirement} \| TST-(?:PWA|PRO)-\d{{3}}\b")

    def test_each_applicable_nonfunctional_requirement_is_traced(self):
        documented = set(re.findall(r"\bNFR-[A-Z]+-\d{3}\b", self.tdd))
        self.assertTrue(APPLICABLE_NFR.issubset(documented), sorted(APPLICABLE_NFR - documented))
        for requirement in sorted(APPLICABLE_NFR):
            self.assertRegex(self.tdd, rf"\| {requirement} \| TST-PWA-\d{{3}}\b")

    def test_traceability_register_links_sdd_tdd_and_pwa_requirements(self):
        for marker in (
            "SDD-004", "TDD-005", "FUN-PWA-001", "FUN-PWA-006",
            "FUN-PRO-001", "FUN-PRO-011", "NFR-USA-001", "NFR-COM-001",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, self.traceability)
        for requirement in re.findall(r"\bFUN-(?:PWA|PRO)-\d{3}\b", self.srs.split("## 5. Requisitos no funcionales", 1)[0]):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, self.traceability)


if __name__ == "__main__":
    unittest.main()
