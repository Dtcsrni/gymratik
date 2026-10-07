const CACHE_NAME = 'entrenamiento-pwa-c75bf41c7a5b';
const PREVIOUS_CACHE_NAME = 'entrenamiento-pwa-b4e625c3d592';
const PRECACHE = [
  './',
  './index.html',
  './manifest.webmanifest',
  './assets/branding/gymratik-pwa-icon-v7-192.png',
  './assets/branding/gymratik-pwa-icon-v7-512.png',
  './assets/branding/gymratik-pwa-icon-v7-maskable-192.png',
  './assets/branding/gymratik-pwa-icon-v7-maskable-512.png',
  './assets/branding/gymratik-cover-seated-breath-30fps.webp',
  './assets/branding/gymratik-cover-seated-v1-poster.webp',
  './assets/branding/routine-covers/day1.webp',
  './assets/branding/routine-covers/day2.webp',
  './assets/branding/routine-covers/day3.webp',
  './assets/branding/routine-covers/day4.webp',
  './install-gate.js',
  './data/profile/mascot-install-phone.webp',
  './progress-store.js',
  './routine-liquid-glass-v13.css',
  './data/profile/mouse-female-effort.webp',
  './data/profile/mouse-male-effort.webp',
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
  './data/profile/mascot-motion/states-v1/female-idle.png',
  './data/profile/mascot-motion/states-v1/female-ready.png',
  './data/profile/mascot-motion/states-v1/female-preparing.png',
  './data/profile/mascot-motion/states-v1/female-warmup.png',
  './data/profile/mascot-motion/states-v1/female-strength.png',
  './data/profile/mascot-motion/states-v1/female-cardio.png',
  './data/profile/mascot-motion/states-v1/female-mobility.png',
  './data/profile/mascot-motion/states-v1/female-rest.png',
  './data/profile/mascot-motion/states-v1/female-approval.png',
  './data/profile/mascot-motion/states-v1/male-idle.png',
  './data/profile/mascot-motion/states-v1/male-ready.png',
  './data/profile/mascot-motion/states-v1/male-preparing.png',
  './data/profile/mascot-motion/states-v1/male-warmup.png',
  './data/profile/mascot-motion/states-v1/male-strength.png',
  './data/profile/mascot-motion/states-v1/male-cardio.png',
  './data/profile/mascot-motion/states-v1/male-mobility.png',
  './data/profile/mascot-motion/states-v1/male-rest.png',
  './data/profile/mascot-motion/states-v1/male-approval.png',
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html',
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html',
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html',
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_4_Pierna_Equilibrio_V1.html',
  './assets/branding/gymratik-mascots-mark-v2.png',
  './data/rutinas_autocontenidas/frases_fitness/fitness_quotes.js',
  './data/rutinas_autocontenidas/frases_fitness/retratos/allyson-felix.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/ana-ivanovic.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/anton-du-beke.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/arnold-schwarzenegger-eu-2026.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/ashton-eaton.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/bethany-hamilton.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/bill-gates.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/bo-jackson.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/bob-feller.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/carmen-electra.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/christopher-morley.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/clare-balding.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/colbie-caillat.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/dan-gable.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/dick-ebersol.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/donovan-bailey.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/eduardo-galeano.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/edward-stanley.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/eric-bana.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/eric-cantona.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/eric-idle.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/fergie.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/freema-agyeman.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/hank-aaron.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/james-caan.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jason-earles.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jason-isaacs.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jean-claude-van-damme.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jeff-garlin.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jennette-mccurdy.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jerry-ferrara.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jesse-tyler-ferguson.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/john-f-kennedy.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jon-hamm.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/jose-canseco.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/julio-iglesias.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/kevin-garnett.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/kimberly-elise.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/larry-hagman.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/mark-gatiss.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/muhammad-ali.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/oksana-baiul.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/paula-abdul.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/pauly-d.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/robert-irvine.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/ron-fairly.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/sammy-hagar.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/satchel-paige.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/scott-hamilton.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/sean-faris.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/shannon-elizabeth.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/sigrid-agren.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/stephen-covey.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/thomas-jefferson.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/tony-danza.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/tyler-hamilton.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/vicente-del-bosque.jpg',
  './data/rutinas_autocontenidas/frases_fitness/retratos/william-baldwin.jpg',
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
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/barbell-rdl-v1.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/warmup-arm-circles-filmed.gif',
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/warmup-shoulder-rolls-filmed.gif',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0197-qdRxqCj-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0197-qdRxqCj-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.gif',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.jpg',
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
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/barbell-rdl-v1-final.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/barbell-rdl-v1-machine-reference.png',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/barbell-rdl-v1-start.jpg',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/lower_anterior_anatomy_v1.webp',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/lower_posterior_anatomy_v1.webp',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_anterior_anatomy_v1.webp',
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/musculos_generados/upper_posterior_anatomy_v1.webp',
  './data/rutinas_autocontenidas/recursos_embebidos/b963bc266356a83bea4fe9909f0516c0c3a1543c06c8a17d24ca9d674fe3c759.png'
];
const PRECACHE_URLS = new Set(PRECACHE.map((path) => new URL(path, self.registration.scope).href));
const RESOURCE_BYTES = {
  './': 108175,
  './index.html': 108175,
  './manifest.webmanifest': 971,
  './assets/branding/gymratik-pwa-icon-v7-192.png': 51237,
  './assets/branding/gymratik-pwa-icon-v7-512.png': 272058,
  './assets/branding/gymratik-pwa-icon-v7-maskable-192.png': 33306,
  './assets/branding/gymratik-pwa-icon-v7-maskable-512.png': 178008,
  './assets/branding/gymratik-cover-seated-breath-30fps.webp': 2813316,
  './assets/branding/gymratik-cover-seated-v1-poster.webp': 33354,
  './assets/branding/routine-covers/day1.webp': 212296,
  './assets/branding/routine-covers/day2.webp': 144640,
  './assets/branding/routine-covers/day3.webp': 201068,
  './assets/branding/routine-covers/day4.webp': 403468,
  './install-gate.js': 8459,
  './data/profile/mascot-install-phone.webp': 1006568,
  './progress-store.js': 39550,
  './routine-liquid-glass-v13.css': 8250,
  './data/profile/mouse-female-effort.webp': 1212010,
  './data/profile/mouse-male-effort.webp': 1072538,
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
  './data/profile/mascot-motion/states-v1/female-idle.png': 16720,
  './data/profile/mascot-motion/states-v1/female-ready.png': 13872,
  './data/profile/mascot-motion/states-v1/female-preparing.png': 13563,
  './data/profile/mascot-motion/states-v1/female-warmup.png': 13232,
  './data/profile/mascot-motion/states-v1/female-strength.png': 13432,
  './data/profile/mascot-motion/states-v1/female-cardio.png': 11809,
  './data/profile/mascot-motion/states-v1/female-mobility.png': 13739,
  './data/profile/mascot-motion/states-v1/female-rest.png': 15821,
  './data/profile/mascot-motion/states-v1/female-approval.png': 13340,
  './data/profile/mascot-motion/states-v1/male-idle.png': 16440,
  './data/profile/mascot-motion/states-v1/male-ready.png': 12461,
  './data/profile/mascot-motion/states-v1/male-preparing.png': 13216,
  './data/profile/mascot-motion/states-v1/male-warmup.png': 11900,
  './data/profile/mascot-motion/states-v1/male-strength.png': 12537,
  './data/profile/mascot-motion/states-v1/male-cardio.png': 11741,
  './data/profile/mascot-motion/states-v1/male-mobility.png': 12451,
  './data/profile/mascot-motion/states-v1/male-rest.png': 15701,
  './data/profile/mascot-motion/states-v1/male-approval.png': 12307,
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_1_Espalda_Biceps_V1.html': 1059576,
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_2_Pierna_Gluteo_V1.html': 2655038,
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html': 642176,
  './data/rutinas_autocontenidas/canonicas/Rutina_Dia_4_Pierna_Equilibrio_V1.html': 645177,
  './assets/branding/gymratik-mascots-mark-v2.png': 338005,
  './data/rutinas_autocontenidas/frases_fitness/fitness_quotes.js': 14218,
  './data/rutinas_autocontenidas/frases_fitness/retratos/allyson-felix.jpg': 28818,
  './data/rutinas_autocontenidas/frases_fitness/retratos/ana-ivanovic.jpg': 32454,
  './data/rutinas_autocontenidas/frases_fitness/retratos/anton-du-beke.jpg': 18756,
  './data/rutinas_autocontenidas/frases_fitness/retratos/arnold-schwarzenegger-eu-2026.jpg': 278839,
  './data/rutinas_autocontenidas/frases_fitness/retratos/ashton-eaton.jpg': 21482,
  './data/rutinas_autocontenidas/frases_fitness/retratos/bethany-hamilton.jpg': 34454,
  './data/rutinas_autocontenidas/frases_fitness/retratos/bill-gates.jpg': 43707,
  './data/rutinas_autocontenidas/frases_fitness/retratos/bo-jackson.jpg': 28041,
  './data/rutinas_autocontenidas/frases_fitness/retratos/bob-feller.jpg': 26246,
  './data/rutinas_autocontenidas/frases_fitness/retratos/carmen-electra.jpg': 49006,
  './data/rutinas_autocontenidas/frases_fitness/retratos/christopher-morley.jpg': 23117,
  './data/rutinas_autocontenidas/frases_fitness/retratos/clare-balding.jpg': 32368,
  './data/rutinas_autocontenidas/frases_fitness/retratos/colbie-caillat.jpg': 35298,
  './data/rutinas_autocontenidas/frases_fitness/retratos/dan-gable.jpg': 18037,
  './data/rutinas_autocontenidas/frases_fitness/retratos/dick-ebersol.jpg': 25477,
  './data/rutinas_autocontenidas/frases_fitness/retratos/donovan-bailey.jpg': 8506,
  './data/rutinas_autocontenidas/frases_fitness/retratos/eduardo-galeano.jpg': 11370,
  './data/rutinas_autocontenidas/frases_fitness/retratos/edward-stanley.jpg': 14631,
  './data/rutinas_autocontenidas/frases_fitness/retratos/eric-bana.jpg': 25316,
  './data/rutinas_autocontenidas/frases_fitness/retratos/eric-cantona.jpg': 36807,
  './data/rutinas_autocontenidas/frases_fitness/retratos/eric-idle.jpg': 22908,
  './data/rutinas_autocontenidas/frases_fitness/retratos/fergie.jpg': 37329,
  './data/rutinas_autocontenidas/frases_fitness/retratos/freema-agyeman.jpg': 38356,
  './data/rutinas_autocontenidas/frases_fitness/retratos/hank-aaron.jpg': 43516,
  './data/rutinas_autocontenidas/frases_fitness/retratos/james-caan.jpg': 32833,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jason-earles.jpg': 41683,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jason-isaacs.jpg': 25708,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jean-claude-van-damme.jpg': 31283,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jeff-garlin.jpg': 22208,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jennette-mccurdy.jpg': 38573,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jerry-ferrara.jpg': 23341,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jesse-tyler-ferguson.jpg': 28801,
  './data/rutinas_autocontenidas/frases_fitness/retratos/john-f-kennedy.jpg': 21858,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jon-hamm.jpg': 42046,
  './data/rutinas_autocontenidas/frases_fitness/retratos/jose-canseco.jpg': 35853,
  './data/rutinas_autocontenidas/frases_fitness/retratos/julio-iglesias.jpg': 32818,
  './data/rutinas_autocontenidas/frases_fitness/retratos/kevin-garnett.jpg': 38826,
  './data/rutinas_autocontenidas/frases_fitness/retratos/kimberly-elise.jpg': 31784,
  './data/rutinas_autocontenidas/frases_fitness/retratos/larry-hagman.jpg': 27787,
  './data/rutinas_autocontenidas/frases_fitness/retratos/mark-gatiss.jpg': 33657,
  './data/rutinas_autocontenidas/frases_fitness/retratos/muhammad-ali.jpg': 23085,
  './data/rutinas_autocontenidas/frases_fitness/retratos/oksana-baiul.jpg': 31768,
  './data/rutinas_autocontenidas/frases_fitness/retratos/paula-abdul.jpg': 34573,
  './data/rutinas_autocontenidas/frases_fitness/retratos/pauly-d.jpg': 31934,
  './data/rutinas_autocontenidas/frases_fitness/retratos/robert-irvine.jpg': 14606,
  './data/rutinas_autocontenidas/frases_fitness/retratos/ron-fairly.jpg': 26303,
  './data/rutinas_autocontenidas/frases_fitness/retratos/sammy-hagar.jpg': 34245,
  './data/rutinas_autocontenidas/frases_fitness/retratos/satchel-paige.jpg': 29380,
  './data/rutinas_autocontenidas/frases_fitness/retratos/scott-hamilton.jpg': 43921,
  './data/rutinas_autocontenidas/frases_fitness/retratos/sean-faris.jpg': 18409,
  './data/rutinas_autocontenidas/frases_fitness/retratos/shannon-elizabeth.jpg': 34920,
  './data/rutinas_autocontenidas/frases_fitness/retratos/sigrid-agren.jpg': 33148,
  './data/rutinas_autocontenidas/frases_fitness/retratos/stephen-covey.jpg': 24682,
  './data/rutinas_autocontenidas/frases_fitness/retratos/thomas-jefferson.jpg': 22959,
  './data/rutinas_autocontenidas/frases_fitness/retratos/tony-danza.jpg': 24766,
  './data/rutinas_autocontenidas/frases_fitness/retratos/tyler-hamilton.jpg': 49656,
  './data/rutinas_autocontenidas/frases_fitness/retratos/vicente-del-bosque.jpg': 32986,
  './data/rutinas_autocontenidas/frases_fitness/retratos/william-baldwin.jpg': 11888,
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
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/barbell-rdl-v1.gif': 1264623,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/warmup-arm-circles-filmed.gif': 586753,
  './data/rutinas_autocontenidas/medios_publicados/ejercicios-compartido/videos/warmup-shoulder-rolls-filmed.gif': 1849783,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0197-qdRxqCj-final.jpg': 6225,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0197-qdRxqCj-start.jpg': 6438,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-final.jpg': 8241,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-machine-reference.png': 19668,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia1_media_generated/0575-q6y3OhV-start.jpg': 8351,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.gif': 7123900,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia2_media_generated/ankle_circles_real_mymichigan.jpg': 22250,
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
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/barbell-rdl-v1-final.jpg': 22450,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/barbell-rdl-v1-machine-reference.png': 9416,
  './data/rutinas_autocontenidas/medios_publicados/rutinas_autocontenidas/dia4_media_generated/barbell-rdl-v1-start.jpg': 20425,
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
  const response = await fetch(new Request(request, { cache: 'no-cache' }));
  const cacheKey = new URL(request.url);
  cacheKey.search = '';
  cacheKey.hash = '';
  if (response.ok && !new URL(request.url).search && PRECACHE_URLS.has(cacheKey.href)) {
    await cache.put(cacheKey.href, response.clone());
  }
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
    // La primera instalación toma control al completar el paquete. Una versión
    // posterior espera la autorización de la portada y se activa en otra apertura.
    // El progreso permanece en IndexedDB/localStorage, fuera de Cache API.
    if (!self.registration.active) await self.skipWaiting();
  })());
});

self.addEventListener('message', (event) => {
  // El mensaje se envía directamente al worker en espera; `self` aquí es el global, no un objeto ServiceWorker.
  if (event.data?.type === 'ACTIVATE_UPDATE') event.waitUntil(self.skipWaiting());
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
  const scopeUrl = new URL(self.registration.scope);
  if (request.method !== 'GET' || url.origin !== scopeUrl.origin || !url.pathname.startsWith(scopeUrl.pathname)) return;

  event.respondWith((async () => {
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request, { ignoreSearch: true });
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
