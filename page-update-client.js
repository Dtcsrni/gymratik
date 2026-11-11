(() => {
  if (!('serviceWorker' in navigator) || window.__gymratikPageUpdateClient) return;
  window.__gymratikPageUpdateClient = true;

  let reloadRequested = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (reloadRequested) return;
    reloadRequested = true;
    window.location.reload();
  });
})();
