const CACHE_NAME = 'entrenamiento-pwa-e7a758d36dea';
const PREVIOUS_CACHE_NAME = 'entrenamiento-pwa-71bcc639adfb';
const PRECACHE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon.png',
  './install-gate.js',
  './data/profile/mascot-install-phone.webp',
  './progress-store.js',
  './routine-liquid-glass-v13.css',
  './data/profile/mouse-female-effort.webp',
  './data/profile/mouse-male-effort.webp',
  './data/profile/gymratik-machine-sprite.webp',
  './data/profile/mascot-motion/female-exercise-25fps.gif',
  './data/profile/mascot-motion/female-rest-25fps.gif',
  './data/profile/mascot-motion/male-exercise-25fps.gif',
  './data/profile/mascot-motion/male-rest-25fps.gif',
  './data/profile/mascot-motion/neutral-exercise-25fps.gif',
  './data/profile/mascot-motion/neutral-rest-25fps.gif',
  './data/profile/mascot-motion/female-exercise-still.webp',
  './data/profile/mascot-motion/female-rest-still.webp',
  './data/profile/mascot-motion/male-exercise-still.webp',
  './data/profile/mascot-motion/male-rest-still.webp',
  './data/profile/mascot-motion/neutral-exercise-still.webp',
  './data/profile/mascot-motion/neutral-rest-still.webp',
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html',
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html',
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html',
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_4_Pierna_Equilibrio_V1.html',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0194-2IxROQ1-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0194-2IxROQ1-machine-only.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0194-2IxROQ1-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0197-qdRxqCj.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0200-dU605di-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0200-dU605di-machine-only.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0200-dU605di-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0257-X7jbxra.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0575-q6y3OhV.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-machine-only.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0584-dRTfGZT-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0584-dRTfGZT-machine-only.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0584-dRTfGZT-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0585-my33uHU.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0592-b6hQYMb-final.png',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0592-b6hQYMb-machine-only.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0592-b6hQYMb.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0596-v3xmPAR-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0596-v3xmPAR-machine-only.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0596-v3xmPAR-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0599-Zg3XY7P.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0602-myfUsKf-final.png',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0602-myfUsKf.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0605-ykUOVze.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0739-10Z2DXU.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0743-Qa55kX1.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0798-a8VDgLw.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1299-jHAnWmT-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1299-jHAnWmT-machine-only.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1299-jHAnWmT-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1350-7I6LNUG-final.png',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1350-7I6LNUG.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1356-OIFMAp1.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1512-qBcKorM.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/2141-rjtuP6X.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/2318-dNFYIU1-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/2318-dNFYIU1-machine-only.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/2318-dNFYIU1-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/3025-butterfly-reverse-front.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/3666-rjiM4L3.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/panatta-super-high-row-unilateral-final.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/panatta-super-high-row-unilateral-start.webp',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/warmup-arm-circles-filmed.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/warmup-shoulder-rolls-filmed.jpg',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0194-2IxROQ1.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0197-qdRxqCj.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0200-dU605di.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0257-X7jbxra.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0575-q6y3OhV.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0577-T0yTjgW.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0578-GUT8I22.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0584-dRTfGZT.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0585-my33uHU.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0586-17lJ1kr.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0592-b6hQYMb.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0594-bOOdeyc.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0596-v3xmPAR.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0597-CHpahtl.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0598-oHsrypV.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0599-Zg3XY7P.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0600-PQ2AtC3.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0602-myfUsKf.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0605-ykUOVze.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0739-10Z2DXU.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0743-Qa55kX1.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0798-a8VDgLw.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/1299-jHAnWmT.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/1350-7I6LNUG.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/1356-OIFMAp1.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/1512-qBcKorM.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/2141-rjtuP6X.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/2287-V07qpXy.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/2318-dNFYIU1.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/3666-rjiM4L3.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/warmup-arm-circles-filmed.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/warmup-shoulder-rolls-filmed.gif',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.gif',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/hip_thrust_machine_booty_builder_correct_form.gif',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/hip_thrust_machine_booty_builder_correct_form.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/hip_thrust_machine_booty_builder_correct_form_final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/hip_thrust_machine_booty_builder_correct_form_inicio.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0578-GUT8I22-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0578-GUT8I22-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0578-GUT8I22-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0586-17lJ1kr-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0586-17lJ1kr-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0586-17lJ1kr-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0594-bOOdeyc-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0594-bOOdeyc-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0594-bOOdeyc-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0597-CHpahtl-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0597-CHpahtl-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0597-CHpahtl-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0598-oHsrypV-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0598-oHsrypV-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0598-oHsrypV-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0600-PQ2AtC3-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0600-PQ2AtC3-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0600-PQ2AtC3-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/2287-V07qpXy-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/2287-V07qpXy-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/2287-V07qpXy-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp',
  './data/rutinas_autocontenidas/recursos_embebidos/b963bc266356a83bea4fe9909f0516c0c3a1543c06c8a17d24ca9d674fe3c759.png'
];
const RESOURCE_BYTES = {
  './': 95424,
  './index.html': 95424,
  './manifest.webmanifest': 456,
  './icon.png': 2204485,
  './install-gate.js': 8459,
  './data/profile/mascot-install-phone.webp': 1006568,
  './progress-store.js': 36660,
  './routine-liquid-glass-v13.css': 8250,
  './data/profile/mouse-female-effort.webp': 1212010,
  './data/profile/mouse-male-effort.webp': 1072538,
  './data/profile/gymratik-machine-sprite.webp': 1001880,
  './data/profile/mascot-motion/female-exercise-25fps.gif': 530477,
  './data/profile/mascot-motion/female-rest-25fps.gif': 503783,
  './data/profile/mascot-motion/male-exercise-25fps.gif': 427464,
  './data/profile/mascot-motion/male-rest-25fps.gif': 432117,
  './data/profile/mascot-motion/neutral-exercise-25fps.gif': 621067,
  './data/profile/mascot-motion/neutral-rest-25fps.gif': 661412,
  './data/profile/mascot-motion/female-exercise-still.webp': 7994,
  './data/profile/mascot-motion/female-rest-still.webp': 8344,
  './data/profile/mascot-motion/male-exercise-still.webp': 7136,
  './data/profile/mascot-motion/male-rest-still.webp': 7480,
  './data/profile/mascot-motion/neutral-exercise-still.webp': 11634,
  './data/profile/mascot-motion/neutral-rest-still.webp': 10150,
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html': 815810,
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html': 2415994,
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html': 387469,
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_4_Pierna_Equilibrio_V1.html': 390848,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0194-2IxROQ1-final.jpg': 4361,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0194-2IxROQ1-machine-only.webp': 504122,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0194-2IxROQ1-start.jpg': 4746,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0197-qdRxqCj.jpg': 6207,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0200-dU605di-final.jpg': 6100,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0200-dU605di-machine-only.webp': 502652,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0200-dU605di-start.jpg': 6036,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0257-X7jbxra.jpg': 4760,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0575-q6y3OhV.jpg': 8525,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-final.jpg': 9550,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-machine-only.webp': 654094,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0577-T0yTjgW-start.jpg': 9193,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0584-dRTfGZT-final.jpg': 9390,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0584-dRTfGZT-machine-only.webp': 643284,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0584-dRTfGZT-start.jpg': 9036,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0585-my33uHU.jpg': 7423,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0592-b6hQYMb-final.png': 9570,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0592-b6hQYMb-machine-only.jpg': 35953,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0592-b6hQYMb.jpg': 8398,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0596-v3xmPAR-final.jpg': 8263,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0596-v3xmPAR-machine-only.webp': 641338,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0596-v3xmPAR-start.jpg': 9065,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0599-Zg3XY7P.jpg': 8799,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0602-myfUsKf-final.png': 20260,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0602-myfUsKf.jpg': 7623,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0605-ykUOVze.jpg': 6823,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0739-10Z2DXU.jpg': 7617,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0743-Qa55kX1.jpg': 7332,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/0798-a8VDgLw.jpg': 5835,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1299-jHAnWmT-final.jpg': 9640,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1299-jHAnWmT-machine-only.webp': 639442,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1299-jHAnWmT-start.jpg': 9027,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1350-7I6LNUG-final.png': 9585,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1350-7I6LNUG.jpg': 9506,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1356-OIFMAp1.jpg': 8136,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/1512-qBcKorM.jpg': 5011,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/2141-rjtuP6X.jpg': 8865,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/2318-dNFYIU1-final.jpg': 10759,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/2318-dNFYIU1-machine-only.webp': 703002,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/2318-dNFYIU1-start.jpg': 9172,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/3025-butterfly-reverse-front.jpg': 128204,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/3666-rjiM4L3.jpg': 8489,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/panatta-super-high-row-unilateral-final.webp': 125430,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/panatta-super-high-row-unilateral-start.webp': 121068,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/warmup-arm-circles-filmed.jpg': 37581,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/images/warmup-shoulder-rolls-filmed.jpg': 20133,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0194-2IxROQ1.gif': 61224,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0197-qdRxqCj.gif': 79512,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0200-dU605di.gif': 79897,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0257-X7jbxra.gif': 73202,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0575-q6y3OhV.gif': 151545,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0577-T0yTjgW.gif': 128680,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0578-GUT8I22.gif': 105444,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0584-dRTfGZT.gif': 146548,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0585-my33uHU.gif': 134615,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0586-17lJ1kr.gif': 107408,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0592-b6hQYMb.gif': 142830,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0594-bOOdeyc.gif': 108148,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0596-v3xmPAR.gif': 115639,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0597-CHpahtl.gif': 173053,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0598-oHsrypV.gif': 134395,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0599-Zg3XY7P.gif': 134618,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0600-PQ2AtC3.gif': 152450,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0602-myfUsKf.gif': 137477,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0605-ykUOVze.gif': 106314,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0739-10Z2DXU.gif': 111122,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0743-Qa55kX1.gif': 108943,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/0798-a8VDgLw.gif': 67702,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/1299-jHAnWmT.gif': 139906,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/1350-7I6LNUG.gif': 129100,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/1356-OIFMAp1.gif': 125741,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/1512-qBcKorM.gif': 86664,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/2141-rjtuP6X.gif': 115045,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/2287-V07qpXy.gif': 175325,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/2318-dNFYIU1.gif': 130298,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/3666-rjiM4L3.gif': 199540,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/warmup-arm-circles-filmed.gif': 586753,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/warmup-shoulder-rolls-filmed.gif': 1849783,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-final.jpg': 8241,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-machine-reference.png': 19668,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-start.jpg': 8351,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.gif': 7123900,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.jpg': 22250,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/hip_thrust_machine_booty_builder_correct_form.gif': 4339552,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/hip_thrust_machine_booty_builder_correct_form.jpg': 16439,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/hip_thrust_machine_booty_builder_correct_form_final.jpg': 22937,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/hip_thrust_machine_booty_builder_correct_form_inicio.jpg': 20873,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0578-GUT8I22-final.jpg': 6898,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0578-GUT8I22-machine-reference.png': 17662,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0578-GUT8I22-start.jpg': 6343,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0586-17lJ1kr-final.jpg': 7178,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0586-17lJ1kr-machine-reference.png': 18771,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0586-17lJ1kr-start.jpg': 7160,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0594-bOOdeyc-final.jpg': 6184,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0594-bOOdeyc-machine-reference.png': 16831,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0594-bOOdeyc-start.jpg': 6406,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0597-CHpahtl-final.jpg': 9403,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0597-CHpahtl-machine-reference.png': 23680,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0597-CHpahtl-start.jpg': 9727,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0598-oHsrypV-final.jpg': 6323,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0598-oHsrypV-machine-reference.png': 18090,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0598-oHsrypV-start.jpg': 6562,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0600-PQ2AtC3-final.jpg': 8137,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0600-PQ2AtC3-machine-reference.png': 19775,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/0600-PQ2AtC3-start.jpg': 8085,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/2287-V07qpXy-final.jpg': 7455,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/2287-V07qpXy-machine-reference.png': 19402,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/2287-V07qpXy-start.jpg': 7725,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp': 1107534,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp': 1106086,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp': 1701482,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp': 1597412,
  './data/rutinas_autocontenidas/recursos_embebidos/b963bc266356a83bea4fe9909f0516c0c3a1543c06c8a17d24ca9d674fe3c759.png': 36398
};
const CACHE_COMPLETE_KEY = new URL('./__gymratik_complete__', self.registration.scope).href;

async function reportProgress(completed, bytesCompleted, current = '') {
  const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
  const totalBytes = Object.values(RESOURCE_BYTES).reduce((sum, size) => sum + size, 0);
  clients.forEach((client) => client.postMessage({
    type: 'PRECACHE_PROGRESS', cacheName: CACHE_NAME, completed,
    total: PRECACHE.length, bytesCompleted, totalBytes, current
  }));
}

async function refresh(request, cache) {
  const response = await fetch(request, { cache: 'no-store' });
  if (response.ok) await cache.put(request, response.clone());
  return response;
}

async function preserveOneCompleteCache() {
  const keys = (await caches.keys()).filter((key) => key.startsWith('entrenamiento-pwa-') && key !== CACHE_NAME);
  const core = PRECACHE.filter((path) => path === './index.html' || path.includes('/canonicas/'));
  const candidates = [];
  for (const key of keys) {
    const cache = await caches.open(key);
    if (await cache.match(CACHE_COMPLETE_KEY)) {
      candidates.push({ key, size: (await cache.keys()).length, markedComplete: true });
      continue;
    }
    const hasCore = await Promise.all(core.map((path) => cache.match(new URL(path, self.registration.scope))));
    if (hasCore.every(Boolean)) candidates.push({ key, size: (await cache.keys()).length, markedComplete: key === PREVIOUS_CACHE_NAME });
  }
  candidates.sort((left, right) => Number(right.markedComplete) - Number(left.markedComplete) || right.size - left.size);
  const keep = candidates[0]?.key;
  await Promise.all(keys.filter((key) => key !== keep).map((key) => caches.delete(key)));
}

async function notifyClientsAppUpdated() {
  const updatedAt = Date.now();
  const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
  clients.forEach((client) => client.postMessage({ type: 'APP_UPDATED', updatedAt, cacheName: CACHE_NAME }));
}

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    for (let attempt = 0; attempt < 2; attempt += 1) {
      const cache = await caches.open(CACHE_NAME);
      let completed = 0;
      let bytesCompleted = 0;
      try {
        await reportProgress(completed, bytesCompleted);
        let nextIndex = 0;
        let firstError = null;
        const downloadNext = async () => {
          while (!firstError) {
            const index = nextIndex++;
            if (index >= PRECACHE.length) return;
            const path = PRECACHE[index];
            try {
              const request = new Request(path, { cache: 'reload' });
              const response = await fetch(request);
              if (!response.ok) throw new Error(`No se pudo descargar ${path} (${response.status})`);
              await cache.put(request, response);
              completed += 1;
              bytesCompleted += RESOURCE_BYTES[path] || 0;
              await reportProgress(completed, bytesCompleted, path);
            } catch (error) { firstError = firstError || error; }
          }
        };
        await Promise.all(Array.from({ length: Math.min(6, PRECACHE.length) }, downloadNext));
        if (firstError) throw firstError;
        await cache.put(CACHE_COMPLETE_KEY, new Response(JSON.stringify({ cacheName: CACHE_NAME, completedAt: Date.now() }), { headers: { 'content-type': 'application/json' } }));
        break;
      } catch (error) {
        await caches.delete(CACHE_NAME);
        if (attempt !== 0 || error?.name !== 'QuotaExceededError') throw error;
        await preserveOneCompleteCache();
      }
    }
    // Activar solo después de descargar y marcar completo todo el paquete.
    // El progreso de entrenamiento vive en IndexedDB/localStorage, fuera de Cache API.
    await self.skipWaiting();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data?.type === 'ACTIVATE_UPDATE' && self.registration.waiting === self) self.skipWaiting();
  if (event.data?.type === 'GET_VERSION_STATUS') {
    event.source?.postMessage({ type: 'VERSION_STATUS', cacheName: CACHE_NAME, total: PRECACHE.length });
  }
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key.startsWith('entrenamiento-pwa-') && key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
      .then(() => notifyClientsAppUpdated())
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);
    const isNavigation = request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html');
    const bypassCache = ['no-cache', 'no-store', 'reload'].includes(request.cache);

    if (cached && !bypassCache) return cached;
    try {
      return await refresh(request, cache);
    } catch (error) {
      if (cached) return cached;
      if (isNavigation) {
        const shell = await cache.match(new URL('./index.html', self.registration.scope));
        if (!shell) return undefined;
        const baseUrl = new URL('./', self.registration.scope).href;
        let html = await shell.text();
        if (/<base\b/i.test(html)) html = html.replace(/<base\b[^>]*>/i, `<base href="${baseUrl}">`);
        else html = html.replace(/<head(?:\s[^>]*)?>/i, (head) => `${head}<base href="${baseUrl}">`);
        const headers = new Headers(shell.headers);
        headers.delete('content-length');
        headers.delete('content-encoding');
        return new Response(html, { status: shell.status, statusText: shell.statusText, headers });
      }
      throw error;
    }
  })());
});
