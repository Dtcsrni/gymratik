# Gymratik PWA: rutinas y progreso

Gymratik es una PWA para consultar cuatro rutinas canónicas, registrar sesiones y conservar perfil e historial localmente. Los recursos declarados esenciales pueden prepararse para uso offline. El avance personal no se sincroniza con otros dispositivos.

## Alcance activo

- PWA instalable, portada, Service Worker y paquete offline.
- Rutinas canónicas, progreso semanal, perfil e historial local.
- Exportación/restauración manual de respaldo JSON v3.
- Seguridad y operación del origen PWA.

Nutrición, suplementos, gimnasio/equipo, IA, app Android nativa, integraciones, backend y sincronización multi-dispositivo están fuera del alcance actual. Consulta [el acta](docs/00-governance/PROJECT_CHARTER.md) y [los requisitos diferidos](docs/01-requirements/DEFERRED_SCOPE.md).

## Estado

El repositorio contiene una PWA y rutinas canónicas; cada capacidad tiene cobertura y evidencia distintas. La validación local no acredita la publicación, instalación, comportamiento offline en un teléfono ni pruebas físicas. Revisa [la matriz de trazabilidad](docs/00-governance/TRACEABILITY.md) y [la estrategia de prueba](docs/05-quality/TEST_STRATEGY.md).

## Documentación principal

- [Requisitos activos](docs/01-requirements/SRS.md)
- [Alcance diferido](docs/01-requirements/DEFERRED_SCOPE.md)
- [Casos de uso PWA](docs/01-requirements/USE_CASES.md)
- [Arquitectura PWA](docs/03-architecture/ARCHITECTURE.md)
- [Datos locales y respaldo](docs/03-architecture/DATA_MODEL.md)
- [Diseño de generación y publicación](docs/03-architecture/SDD-004-generacion-validacion-publicacion-pwa.md)
- [ADRs](docs/03-architecture/adr/README.md)
- [Estrategia de pruebas](docs/05-quality/TEST_STRATEGY.md)
- [Amenazas y privacidad](docs/06-security/THREAT_MODEL.md)
- [Runbook PWA](docs/08-operations/RUNBOOK.md)
- [Uso de PWA en Android](docs/08-operations/PWA_ANDROID.md)

## Componentes actuales

```text
index.html                 Portada y perfil local
progress-store.js          Persistencia local de perfil, sesiones y avance
manifest.webmanifest       Metadatos e iconos de instalación
sw.js                      Service Worker generado
data/rutinas_autocontenidas/ Rutinas canónicas y medios
scripts/                   Generación y validación
tests/                     Pruebas automatizadas
```

## Validación local

```powershell
python scripts/validate_repository.py
python -m unittest discover -s tests -p "test_*.py"
node --check sw.js
```

Al modificar un recurso precargado, regenera el worker con `python scripts/build_pwa_service_worker.py` y valida que el fingerprint coincida. Ejecuta las pruebas específicas de rutina/medios cuando corresponda.

## Privacidad

Los datos de usuario residen en IndexedDB `entrenamiento-progress` v3 del origen/perfil del navegador; el fallback `entrenamiento-progress-fallback-v3`, snapshots `fitlovers-dayN-series-v1` y archivo `gymratik-legacy-progress-archive-v1` residen en localStorage. La exportación manual es JSON `gymratik-backup`, esquema 3. La PWA no borra datos al instalar o actualizar; la limpieza del origen por el navegador/sistema operativo y algunos flujos de desinstalación quedan bajo control externo. No incorpores secretos ni datos personales reales al repositorio.
