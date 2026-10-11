import unittest

from scripts.validate_repository import validate_requirement_traceability


class RequirementTraceabilityTests(unittest.TestCase):
    def test_valid_requirement_matrix_has_no_errors(self):
        srs = "- **FUN-PRO-001 · P0:** requirement\n- **NFR-REL-001 · P0:** requirement"
        matrix = """| Requisito | Riesgo | Diseño/ADR | Prueba prevista | Estado |
|---|---|---|---|---|
| FUN-PRO-001 | RISK-001 | SDD-001 | TST-PRO-001 | Planned |
| NFR-REL-001 | RISK-001 | SDD-001 | TST-REL-001 | Planned |
"""
        errors = []
        validate_requirement_traceability(errors, srs, matrix)
        self.assertEqual(errors, [])

    def test_missing_and_duplicate_matrix_rows_are_rejected(self):
        srs = "- **FUN-PRO-001 · P0:** requirement\n- **FUN-PRO-002 · P1:** requirement"
        matrix = """| Requisito | Riesgo | Diseño/ADR | Prueba prevista | Estado |
|---|---|---|---|---|
| FUN-PRO-001 | RISK-001 | SDD-001 | TST-PRO-001 | Partial |
| FUN-PRO-001 | RISK-001 | SDD-001 | TST-PRO-001 | Planned |
"""
        errors = []
        validate_requirement_traceability(errors, srs, matrix)
        self.assertIn("Requisito duplicado en TRACEABILITY.md: FUN-PRO-001 (2 filas)", errors)
        self.assertIn("Requisito SRS sin fila en TRACEABILITY.md: FUN-PRO-002", errors)

    def test_duplicate_srs_requirement_is_rejected(self):
        srs = "- **FUN-PRO-001 · P0:** first\n- **FUN-PRO-001 · P0:** duplicate"
        matrix = "| FUN-PRO-001 | RISK-001 | SDD-001 | TST-PRO-001 | Planned |"
        errors = []
        validate_requirement_traceability(errors, srs, matrix)
        self.assertIn("Requisito SRS definido 2 veces: FUN-PRO-001", errors)


if __name__ == "__main__":
    unittest.main()
