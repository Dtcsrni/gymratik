(() => {
  if (!('serviceWorker' in navigator) || window.__gymratikPageUpdateClient) return;
  window.__gymratikPageUpdateClient = true;

  const activationKey = 'gymratik-update-activation-pending-v1';
  const updateNotice = document.querySelector('#updateNotice');
  const updateTitle = document.querySelector('#updateNoticeTitle');
  const updateText = document.querySelector('#updateNoticeText');
  const retryButton = document.querySelector('#manualUpdateButton');
  let activationPending = false;
  let startupError = false;
  let retryPanel = null;

  try {
    const activatedAt = Number(sessionStorage.getItem(activationKey)) || 0;
    activationPending = activatedAt > 0 && Date.now() - activatedAt < 5 * 60 * 1000;
  } catch (_) {}

  function offerRetry() {
    if (!activationPending) return;
    startupError = true;
    if (!updateNotice || !updateTitle || !updateText || !retryButton) {
      if (retryPanel) return;
      retryPanel = document.createElement('aside');
      retryPanel.setAttribute('role', 'alert');
      retryPanel.style.cssText = 'position:fixed;inset:auto 1rem 1rem;z-index:2147483000;display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:1rem;border:1px solid #ffd166;border-radius:1rem;background:#102235;color:#fff;font:600 1rem/1.4 system-ui,sans-serif;box-shadow:0 12px 36px #0008';
      const copy = document.createElement('span');
      copy.textContent = 'La versión nueva encontró un error al iniciar. Tu avance local sigue guardado.';
      const retry = document.createElement('button');
      retry.type = 'button';
      retry.textContent = 'Reintentar';
      retry.style.cssText = 'flex:none;padding:.7rem 1rem;border:0;border-radius:.7rem;background:#ffd166;color:#102235;font:700 1rem system-ui,sans-serif';
      retry.addEventListener('click', () => window.location.reload());
      retryPanel.append(copy, retry);
      document.body?.append(retryPanel);
      return;
    }
    updateTitle.textContent = 'La versión nueva encontró un error al iniciar';
    updateText.textContent = 'Tu avance local sigue guardado. Puedes volver a cargar la versión activa para reintentar.';
    retryButton.textContent = 'Reintentar Gymratik';
    retryButton.hidden = false;
    updateNotice.hidden = false;
  }

  function markStartupReady() {
    if (!activationPending || startupError) return;
    activationPending = false;
    try { sessionStorage.removeItem(activationKey); } catch (_) {}
    if (retryButton?.textContent === 'Reintentar Gymratik' && updateNotice) updateNotice.hidden = true;
  }

  if (activationPending) {
    offerRetry();
    window.addEventListener('error', offerRetry, { once: true });
    window.addEventListener('unhandledrejection', offerRetry, { once: true });
  }
  window.addEventListener('gymratik-startup-ready', markStartupReady, { once: true });
  if (!document.querySelector('#appSplash')) window.addEventListener('load', markStartupReady, { once: true });

  let reloadRequested = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (reloadRequested) return;
    reloadRequested = true;
    try { sessionStorage.setItem(activationKey, String(Date.now())); } catch (_) {}
    window.location.reload();
  });
})();
