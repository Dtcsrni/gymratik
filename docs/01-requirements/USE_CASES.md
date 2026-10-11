# Casos de uso activos de Gymratik PWA

## Consultar rutinas sin conexión

**Actor:** usuario.

1. El usuario abre Gymratik en navegador compatible.
2. La PWA muestra por separado el estado de lectura local y preparación de recursos.
3. Cuando el paquete requerido está guardado, el usuario abre cualquiera de las cuatro rutinas sin red.
4. Si un recurso falta, la PWA identifica el error y permite reintentar al recuperar conexión.

## Registrar y continuar una sesión

**Actor:** usuario con PWA instalada.

1. La portada propone continuar la sesión de hoy o el siguiente día de la rotación.
2. El usuario registra calentamiento y series en la rutina elegida.
3. Cada cambio confirmado se guarda en el almacenamiento local.
4. Si el usuario vuelve a portada, recarga o actualiza, puede continuar la sesión activa.
5. Una semana nueva renueva el avance operativo sin eliminar sesiones terminadas del historial.

## Exportar respaldo

**Actor:** usuario.

1. El usuario solicita exportación desde la interfaz.
2. La PWA valida el estado local y genera un archivo JSON v3.
3. El usuario guarda el archivo en una ubicación fuera del almacenamiento del sitio.

## Restaurar respaldo

**Actor:** usuario.

1. El usuario elige un archivo de respaldo.
2. La PWA valida tipo, versión y contenido antes de modificar los datos.
3. Si es válido, presenta confirmación de reemplazo.
4. Tras confirmar, importa el archivo y presenta el resultado.
5. Si falla la validación, se conserva intacto el estado previo.

## Instalar y actualizar

**Actor:** usuario.

1. El usuario abre la URL publicada y sigue la opción de instalación que ofrece el navegador.
2. La PWA prepara el inventario offline según la preferencia de red.
3. Una nueva versión se guarda completa antes de reemplazar la activa.
4. Si el usuario continúa sin descargar, la actualización queda pendiente.

No se definen casos de uso de nutrición, suplementos, IA, gimnasio/equipo, integraciones ni sincronización entre dispositivos dentro del alcance vigente.
