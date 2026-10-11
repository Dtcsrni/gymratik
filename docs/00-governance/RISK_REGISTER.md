# Registro de riesgos

Escala histórica: probabilidad e impacto de 1 a 5; exposición = producto. Los riesgos de dominios diferidos se conservan para trazabilidad, pero no generan trabajo activo.

| ID | Riesgo | P | I | Exposición | Tratamiento dentro de PWA | Evidencia | Estado |
|---|---|---:|---:|---:|---|---|---|
| RISK-001 | Compatibilidad del Amazfit Active | 4 | 5 | 20 | Sin tratamiento en el alcance actual | PoC futura | Diferido |
| RISK-002 | Estimación de alimentos inexacta | 5 | 5 | 25 | Sin tratamiento en el alcance actual | Evaluación futura | Diferido |
| RISK-003 | Tezkatli inaccesible desde el gimnasio | 3 | 5 | 15 | No aplica: no hay servicio remoto PWA | Prueba futura | Diferido |
| RISK-004 | Pérdida o duplicación de sesiones/series locales | 3 | 5 | 15 | Persistencia idempotente, migración no destructiva y respaldo manual | Pruebas de almacenamiento y restauración | Activo |
| RISK-005 | Saturación de VRAM/RAM de inferencia | 4 | 4 | 16 | Sin tratamiento en el alcance actual | Benchmark futuro | Diferido |
| RISK-006 | Catálogo nutricional incorrecto | 4 | 4 | 16 | Sin tratamiento en el alcance actual | Casos futuros | Diferido |
| RISK-007 | Falsos positivos de llegada al gimnasio | 3 | 3 | 9 | Sin detección geográfica en la PWA | Prueba futura | Diferido |
| RISK-008 | Consumo de batería por ubicación | 3 | 4 | 12 | No hay captura de ubicación en la PWA | Perfil futuro | Diferido |
| RISK-009 | IA modifica información confirmada | 2 | 5 | 10 | No existe IA en el alcance activo | Pruebas futuras | Diferido |
| RISK-010 | Datos sensibles aparecen en Git o logs | 3 | 5 | 15 | Datos sintéticos, exclusión de contenido personal y validación de importación | Validación del repo y revisión de código | Activo |
| RISK-011 | Crecimiento descontrolado del alcance | 4 | 4 | 16 | SRS PWA y registro explícito de elementos diferidos | Revisión de alcance | Activo |
| RISK-012 | Regresión de calidad de modelo | 4 | 4 | 16 | No se ejecutan modelos en el alcance activo | Evaluación futura | Diferido |
| RISK-013 | Duplicación en Health Connect | 3 | 3 | 9 | Sin integración en el alcance actual | Prueba futura | Diferido |
| RISK-014 | Respaldo local no restaurable | 2 | 5 | 10 | Esquema v3, validación antes de reemplazo y restauración de fixture | Pruebas de round-trip/archivo inválido | Activo |

## Revisión

Revisar los riesgos activos ante cambios de almacenamiento, importación, Service Worker o alcance. Una mitigación no cierra un riesgo sin evidencia ejecutada. Los diferidos solo se revisan si el usuario amplía el alcance.
