(() => {
  if (!('serviceWorker' in navigator) || window.__gymratikPageUpdateClient) return;
  window.__gymratikPageUpdateClient = true;

  const activationKey = 'gymratik-update-activation-pending-v1';
  const toastId = 'gymratikStartupRetryToast';
  const toastDurationMs = 8000;
  let activationPending = false;
  let startupReady = false;
  let retryToast = null;
  let readinessTimer = 0;
  let dismissTimer = 0;

  try {
    const activatedAt = Number(sessionStorage.getItem(activationKey)) || 0;
    activationPending = activatedAt > 0 && Date.now() - activatedAt < 5 * 60 * 1000;
  } catch (_) {}

  function dismissRetryToast() {
    window.clearTimeout(dismissTimer);
    if (!retryToast) return;
    retryToast.classList.remove('is-visible');
    window.setTimeout(() => {
      retryToast?.remove();
      retryToast = null;
    }, 220);
  }

  function offerRetry(cause = 'timeout') {
    if (!activationPending || startupReady || retryToast) return;
    window.clearTimeout(readinessTimer);
    retryToast = document.createElement('aside');
    retryToast.id = toastId;
    retryToast.className = 'startup-retry-toast';
    retryToast.dataset.sessionBar = String(Boolean(document.querySelector('#floatingSessionSummary')));
    retryToast.setAttribute('role', 'alert');
    retryToast.setAttribute('aria-live', 'assertive');

    const copy = document.createElement('span');
    copy.textContent = cause === 'error'
      ? 'La versión nueva encontró un error al iniciar. Tu avance local sigue guardado.'
      : 'La versión nueva tarda en iniciar. Tu avance local sigue guardado.';
    const retry = document.createElement('button');
    retry.type = 'button';
    retry.className = 'startup-retry-action';
    retry.textContent = 'Reintentar';
    retry.setAttribute('aria-label', 'Volver a cargar Gymratik');
    retry.addEventListener('click', () => window.location.reload());

    retryToast.append(copy, retry);
    document.body?.append(retryToast);
    requestAnimationFrame(() => retryToast?.classList.add('is-visible'));
    dismissTimer = window.setTimeout(dismissRetryToast, toastDurationMs);
  }

  function markStartupReady() {
    if (!activationPending) return;
    startupReady = true;
    activationPending = false;
    window.clearTimeout(readinessTimer);
    try { sessionStorage.removeItem(activationKey); } catch (_) {}
    dismissRetryToast();
  }

  if (activationPending) {
    window.addEventListener('error', () => offerRetry('error'), { once: true });
    window.addEventListener('unhandledrejection', () => offerRetry('error'), { once: true });
    readinessTimer = window.setTimeout(() => offerRetry('timeout'), 12000);
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
