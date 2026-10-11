# Seguridad y privacidad de Gymratik PWA

## Alcance

Esta política cubre la PWA estática, sus recursos, el origen del navegador y los archivos locales de respaldo. No hay backend, cuentas ni integraciones en el alcance vigente.

## Reglas

- No incluir secretos, datos personales reales, historiales reales ni respaldos de usuarios en Git, fixtures o logs.
- Tratar texto, nombres, enlaces y archivos importados como entradas no confiables; validar antes de representar o persistir.
- Mostrar contenido del usuario como texto y evitar inserción HTML insegura.
- Validar versión, tipo, tamaño y esquema de los respaldos antes de cambiar datos.
- No guardar tokens ni credenciales: la PWA no implementa autenticación.
- Mantener dependencias y avisos de licencia identificados; revisar cambios del Service Worker y su inventario.
- Mantener el perfil, historial y backups locales; no transmitirlos a servicios remotos.
- Limitar los diagnósticos a información técnica sin contenido personal.

## Límites

El almacenamiento del navegador no equivale a una cuenta ni a cifrado integral. Un XSS o dispositivo comprometido puede exponer datos locales. La PWA conserva datos durante instalación, actualización y migración; el borrado de datos del origen y los efectos de desinstalación dependen del navegador/sistema operativo y quedan fuera de su control. La interfaz identifica el origen y formatos de almacenamiento.

El modelo de amenazas PWA está en [docs/06-security/THREAT_MODEL.md](docs/06-security/THREAT_MODEL.md). Reporta vulnerabilidades sin publicar datos sensibles ni archivos de usuario.
