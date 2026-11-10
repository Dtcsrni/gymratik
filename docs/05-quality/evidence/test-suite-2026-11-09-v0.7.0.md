# Evidencia de pruebas — Gymratik 0.7.0

- **Fecha:** 2026-11-09
- **Commit probado:** `b703f4009d5b5b32da150ab98619f67d6960cbcb`
- **Entorno:** Windows local; Playwright requirió ejecutar el proceso fuera del sandbox para iniciar su driver y Chromium.

## Resultados

- `python -m unittest tests.routines.test_canonical_routines tests.test_homepage tests.test_service_worker`: 129 pruebas, OK.
- `python scripts/validate_repository.py`: `VALIDATION_OK markdown=87`.
- `node --check sw.js`: OK.
- `python -u -m unittest discover -s tests -p 'test_*.py'` (fuera del sandbox): 229 pruebas en 22.064 s, OK.

La suite completa no se considera fallida por el bloqueo observado en el sandbox: `tests.test_modular_krita_source` pasó por separado y la suite pasó completa fuera del sandbox. Estas comprobaciones locales no prueban la PWA publicada ni su funcionamiento en un dispositivo físico.
