(() => {
  if (!('serviceWorker' in navigator) || window.__gymratikPageUpdateClient) return;
  window.__gymratikPageUpdateClient = true;

  const activationKey = 'gymratik-update-activation-pending-v1';
  const toastId = 'gymratikStartupRetryToast';
  const toastDurationMs = 10000;
  let activationPending = false;
  let startupCheckRunning = false;
  let rollbackRequested = false;
  let retryToast = null;
  let readinessTimer = 0;
  let dismissTimer = 0;

  try {
    const activatedAt = Number(sessionStorage.getItem(activationKey)) || 0;
    activationPending = activatedAt > 0 && Date.now() - activatedAt < 5 * 60 * 1000;
  } catch (_) {}

  function dismissRetryToast() {
    window.clearTimeout(dismissTimer);
    retryToast?.remove();
    retryToast = null;
  }

  function offerRetry(cause = 'timeout') {
    if (retryToast) return;
    window.clearTimeout(readinessTimer);
    retryToast = document.createElement('aside');
    retryToast.id = toastId;
    retryToast.className = 'startup-retry-toast';
    retryToast.dataset.sessionBar = String(Boolean(document.querySelector('#floatingSessionSummary')));
    retryToast.setAttribute('role', 'alert');
    retryToast.setAttribute('aria-live', 'assertive');
    const copy = document.createElement('span');
    copy.textContent = cause === 'error'
      ? 'La versión nueva no pudo validar el inicio. Tus registros locales siguen intactos.'
      : 'La versión nueva no terminó de iniciar. Tus registros locales siguen intactos.';
    const retry = document.createElement('button');
    retry.type = 'button';
    retry.className = 'startup-retry-action';
    retry.textContent = 'Reintentar';
    retry.setAttribute('aria-label', 'Reintentar Gymratik');
    retry.addEventListener('click', () => {
      navigator.serviceWorker.controller?.postMessage({ type: 'RETRY_CANDIDATE' });
      try { sessionStorage.removeItem(activationKey); } catch (_) {}
      window.location.reload();
    });
    retryToast.append(copy, retry);
    document.body?.append(retryToast);
    requestAnimationFrame(() => retryToast?.classList.add('is-visible'));
    dismissTimer = window.setTimeout(dismissRetryToast, toastDurationMs);
  }

  function requestRollback(code) {
    if (rollbackRequested || !navigator.serviceWorker.controller) return;
    rollbackRequested = true;
    window.clearTimeout(readinessTimer);
    navigator.serviceWorker.controller.postMessage({ type: 'GYMRATIK_STARTUP_FAILED', code });
    window.setTimeout(() => { if (rollbackRequested) offerRetry('error'); }, 3000);
  }

  async function validateStartup() {
    if (!activationPending) return;
    if (startupCheckRunning) return;
    startupCheckRunning = true;
    try {
      const store = window.TrainingProgressStore;
      if (!store?.checkStorage) throw new Error('No está disponible la comprobación de almacenamiento');
      await store.checkStorage();
      await Promise.all([store.getHistory(1), store.getProfile()]);
      window.clearTimeout(readinessTimer);
      try { sessionStorage.removeItem(activationKey); } catch (_) {}
      activationPending = false;
      dismissRetryToast();
      navigator.serviceWorker.controller?.postMessage({ type: 'GYMRATIK_HEALTHY' });
    } catch (error) {
      console.error('Gymratik startup health check failed', error);
      window.dispatchEvent(new CustomEvent('gymratik-startup-failed', { detail: { code: 'local-storage-health' } }));
      requestRollback('local-storage-health');
      if (!rollbackRequested) offerRetry('error');
    } finally {
      startupCheckRunning = false;
    }
  }

  window.addEventListener('error', () => {
    if (activationPending) requestRollback('uncaught-error');
  }, { once: true });
  window.addEventListener('unhandledrejection', () => {
    if (activationPending) requestRollback('unhandled-rejection');
  }, { once: true });
  window.addEventListener('gymratik-startup-ready', validateStartup, { once: true });
  window.addEventListener('gymratik-startup-failed', event => requestRollback(event.detail?.code || 'startup-failure'));
  window.addEventListener('training-storage-error', event => {
    if (event.detail?.fallback !== true) {
      navigator.serviceWorker.controller?.postMessage({ type: 'GYMRATIK_STORAGE_FAILED', code: 'training-storage-error' });
    }
  });
  navigator.serviceWorker.addEventListener('message', event => {
    if (event.data?.type === 'GYMRATIK_ROLLBACK_READY') window.location.reload();
    if (event.data?.type === 'GYMRATIK_ROLLBACK_UNAVAILABLE' && activationPending) {
      rollbackRequested = false;
      offerRetry('error');
    }
  });

  if (activationPending) readinessTimer = window.setTimeout(() => requestRollback('startup-timeout'), 30000);
  window.addEventListener('load', () => {
    if (document.querySelector('.exerciseTracker') && window.GymratikInstallGate?.isInstalled()) validateStartup();
  }, { once: true });

  let reloadRequested = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (reloadRequested) return;
    reloadRequested = true;
    try { sessionStorage.setItem(activationKey, String(Date.now())); } catch (_) {}
    window.location.reload();
  });
})();
