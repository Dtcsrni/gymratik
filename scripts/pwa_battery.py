"""Ahorro de batería para animaciones y cronómetros de la PWA de rutinas."""

import re


BATTERY_MOTION_STYLE = r'''<style data-enhancement="battery-aware-motion-v1">
html.is-document-hidden,html.is-document-hidden *,html.is-document-hidden::before,html.is-document-hidden::after,html.is-document-hidden *::before,html.is-document-hidden *::after,
[data-motion-paused="true"],[data-motion-paused="true"] *,[data-motion-paused="true"]::before,[data-motion-paused="true"]::after,[data-motion-paused="true"] *::before,[data-motion-paused="true"] *::after{
  animation-play-state:paused!important
}
</style>'''

BATTERY_MOTION_SCRIPT = r'''<script data-enhancement="battery-aware-motion-v1">
(() => {
  const root = document.documentElement;
  const motionImages = new Set();
  const motionSources = new WeakMap();
  const intersecting = new WeakMap();
  const frameVisibility = new WeakMap();
  const imagesByFrame = new WeakMap();
  const posterFor = image => image.parentElement?.querySelector('.warmupFallback,.gifFallback');
  const posterSourceFor = image => posterFor(image)?.getAttribute('src') || image.dataset.staticSrc || image.getAttribute('data-static-src') || '';
  const sourceFor = image => motionSources.get(image) || image.dataset.batteryMotionSrc || image.getAttribute('src');
  const pauseImage = image => {
    if (image.closest('.warmupVisual,.gifFrame')?.dataset.mediaState === 'FALLBACK_STATIC') return;
    const posterSrc = posterSourceFor(image);
    image.dataset.batteryPaused = 'true';
    image.setAttribute('data-motion-paused', 'true');
    if (posterSrc && image.getAttribute('src') !== posterSrc) image.setAttribute('src', posterSrc);
  };
  const resumeImage = image => {
    if (image.closest('.warmupVisual,.gifFrame')?.dataset.mediaState === 'FALLBACK_STATIC') return;
    const source = sourceFor(image);
    if (!source) return;
    delete image.dataset.batteryPaused;
    image.setAttribute('data-motion-paused', 'false');
    if (image.getAttribute('src') !== source) image.setAttribute('src', source);
  };
  const syncImage = image => {
    if (document.hidden || !intersecting.get(image)) pauseImage(image);
    else resumeImage(image);
  };
  const syncVisibility = () => root.classList.toggle('is-document-hidden', document.hidden);
  const syncAllMotion = () => {
    syncVisibility();
    motionImages.forEach(syncImage);
  };
  document.addEventListener('visibilitychange', syncAllMotion, { passive: true });
  syncVisibility();

  if (!('IntersectionObserver' in window)) return;
  const sections = document.querySelectorAll('.hero,.quickRules,.prep,.routineSummary,.sessionGamification,.sessionDashboard,.notePanel,.cards>.card,.sessionFooter');
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) entry.target.setAttribute('data-motion-paused', String(!entry.isIntersecting));
  }, { rootMargin: '96px 0px' });
  sections.forEach(section => observer.observe(section));
  const mediaObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
      frameVisibility.set(entry.target, entry.isIntersecting);
      for (const image of imagesByFrame.get(entry.target) || []) {
        intersecting.set(image, entry.isIntersecting);
        syncImage(image);
      }
    }
  }, { rootMargin: '96px 0px' });
  const observeMotionImage = image => {
    if (!(image instanceof HTMLImageElement) || !image.matches('img.gifMotion,img.warmupGif,img.day3ExerciseGif,img.day4ExerciseGif') || motionImages.has(image)) return;
    const source = image.getAttribute('src');
    if (!source) return;
    const frame = image.closest('.warmupVisual,.gifFrame') || image;
    motionSources.set(image, source);
    image.dataset.batteryMotionSrc = source;
    motionImages.add(image);
    const frameImages = imagesByFrame.get(frame) || [];
    frameImages.push(image);
    imagesByFrame.set(frame, frameImages);
    if (frameVisibility.has(frame)) intersecting.set(image, frameVisibility.get(frame));
    else mediaObserver.observe(frame);
  };
  document.querySelectorAll('img.gifMotion,img.warmupGif,img.day3ExerciseGif,img.day4ExerciseGif').forEach(observeMotionImage);
  const mediaMutationObserver = new MutationObserver(records => {
    records.forEach(record => record.addedNodes.forEach(node => {
      if (!(node instanceof Element)) return;
      if (node.matches('img.gifMotion,img.warmupGif,img.day3ExerciseGif,img.day4ExerciseGif')) observeMotionImage(node);
      node.querySelectorAll('img.gifMotion,img.warmupGif,img.day3ExerciseGif,img.day4ExerciseGif').forEach(observeMotionImage);
    }));
  });
  mediaMutationObserver.observe(document.documentElement, { childList: true, subtree: true });
  window.GymratikBatteryMotion = {
    setSource(image, source) {
      if (!(image instanceof HTMLImageElement) || !image.matches('.gifMotion,.warmupGif,.day3ExerciseGif,.day4ExerciseGif') || !source) return;
      motionSources.set(image, source);
      image.dataset.batteryMotionSrc = source;
      syncImage(image);
    }
  };
})();
</script>'''

BATTERY_TIMING_INTERVAL = '''  const refreshTimingDisplays = () => {
    if (document.hidden) return;
    renderTimingDisplays();
    renderWarmupTiming();
    exerciseItems.forEach(updateCompleteButton);
  };
  let timingInterval = 0;
  const syncTimingInterval = () => {
    if (document.hidden) {
      window.clearInterval(timingInterval);
      timingInterval = 0;
      return;
    }
    refreshTimingDisplays();
    if (!timingInterval) timingInterval = window.setInterval(refreshTimingDisplays, 1000);
  };
  document.addEventListener('visibilitychange', syncTimingInterval, { passive: true });
  timingInterval = window.setInterval(refreshTimingDisplays, 1000);'''


def apply_battery_motion(source: str, newline: str = "\n") -> str:
    """Pausa medios fuera de vista y cronómetros en segundo plano; conserva EOL."""
    source = source.replace("\r\n", "\n")
    style_tag = '<style data-enhancement="battery-aware-motion-v1">'
    if style_tag in source:
        source = re.sub(
            r'<style data-enhancement="battery-aware-motion-v1">.*?</style>',
            BATTERY_MOTION_STYLE,
            source,
            count=1,
            flags=re.S,
        )
    else:
        source = source.replace("</head>", BATTERY_MOTION_STYLE + "\n</head>", 1)
    script_tag = '<script data-enhancement="battery-aware-motion-v1">'
    if script_tag in source:
        source = re.sub(
            r'<script data-enhancement="battery-aware-motion-v1">.*?</script>',
            BATTERY_MOTION_SCRIPT,
            source,
            count=1,
            flags=re.S,
        )
    else:
        source = source.replace("</body>", BATTERY_MOTION_SCRIPT + "\n</body>", 1)
    if "if (image.dataset.batteryPaused === 'true') return;" not in source:
        source = source.replace(
            "const showLoadedImage = expectedSrc => {\n",
            "const showLoadedImage = expectedSrc => {\n      if (image.dataset.batteryPaused === 'true') return;\n",
            1,
        )
    source = source.replace(
        "      image.src = gifSrc;",
        "      if (window.GymratikBatteryMotion) window.GymratikBatteryMotion.setSource(image, gifSrc);\n      else image.src = gifSrc;",
        1,
    )
    source = re.sub(
        r"(?m)^  const timingInterval = window\.setInterval\(\(\) => \{.*?\}, 1000\);$",
        BATTERY_TIMING_INTERVAL,
        source,
        count=1,
    )
    source = source.replace("  document.addEventListener('visibilitychange', () => renderTimingDisplays());\n", "")
    return source.replace("\n", newline) if newline == "\r\n" else source
