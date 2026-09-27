"""Genera el service worker con el inventario offline de las rutinas canónicas."""

from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DIR = ROOT / "data" / "rutinas_autocontenidas" / "canonicas"
OUTPUT = ROOT / "sw.js"
ROUTINE_FILES = (
    "Rutina_Dia_1_Espalda_Biceps_V1.html",
    "Rutina_Dia_2_Pierna_Gluteo_V1.html",
    "Rutina_Dia_3_Pecho_Hombro_Triceps_V1.html",
    "Rutina_Dia_4_Pierna_Equilibrio_V1.html",
)
HTML_ATTR_PATTERN = re.compile(r"(?:src|data-static-src|gif|thumbnail)\s*[:=]\s*[\"']([^\"']+)")
TEXT_RESOURCE_SUFFIXES = {".css", ".html", ".js", ".json", ".svg", ".txt", ".webmanifest", ".xml"}
IMAGE_SUFFIXES = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
ESTIMATE_META = re.compile(r"<meta name=\"gymratik-resource-estimate\" content='[^']*'>")


class ResourceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if value and name in {"src", "data-static-src"}:
                self.references.add(value)


def resolve_reference(canonical: Path, reference: str) -> str | None:
    if reference.startswith(("http://", "https://", "data:", "#", "/")):
        return None
    canonical_url = PurePosixPath(canonical.relative_to(ROOT).as_posix())
    resolved = PurePosixPath(*canonical_url.parent.parts, reference).as_posix()
    normalized = PurePosixPath(resolved)
    parts: list[str] = []
    for part in normalized.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    path = "/".join(parts)
    target = ROOT / Path(*parts)
    if not target.is_file():
        raise SystemExit(f"Recurso offline no encontrado: {canonical.relative_to(ROOT)} -> {reference}")
    return f"./{path}"


def routine_resources(canonical: Path) -> set[str]:
    text = canonical.read_text(encoding="utf-8")
    parser = ResourceParser()
    parser.feed(text)
    parser.references.update(match.group(1) for match in HTML_ATTR_PATTERN.finditer(text))
    resources = set()
    for reference in parser.references:
        resolved = resolve_reference(canonical, reference)
        if resolved:
            resources.add(resolved)
    return resources


def build_precache() -> list[str]:
    base = [
        "./",
        "./index.html",
        "./manifest.webmanifest",
        "./icon.png",
        "./install-gate.js",
        "./data/profile/mascot-install-phone.webp",
        "./progress-store.js",
        "./routine-liquid-glass-v13.css",
        "./data/profile/mouse-female-effort.webp",
        "./data/profile/mouse-male-effort.webp",
        "./data/profile/gymratik-machine-sprite.webp",
        *[
            f"./data/profile/mascot-motion/{variant}-{state}-25fps.gif"
            for variant in ("female", "male", "neutral")
            for state in ("exercise", "rest")
        ],
        *[
            f"./data/profile/mascot-motion/{variant}-{state}-still.webp"
            for variant in ("female", "male", "neutral")
            for state in ("exercise", "rest")
        ],
    ]
    routines = [f"./data/rutinas_autocontenidas/canonicas/{name}" for name in ROUTINE_FILES]
    resources = set(base + routines)
    for name in ROUTINE_FILES:
        resources.update(routine_resources(CANONICAL_DIR / name))
    # Incluir GIF didácticos para que la técnica también funcione sin conexión.
    return base + routines + sorted(resources - set(base + routines))


def fingerprint_content(target: Path) -> bytes:
    content = target.read_bytes()
    if target.suffix.lower() in TEXT_RESOURCE_SUFFIXES:
        return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return content


def resource_size(target: Path) -> int:
    """Calcula el tamaño estable del archivo tal como se versiona en Git."""
    if target.is_dir():
        target = target / "index.html"
    return len(fingerprint_content(target))


def update_resource_estimate(resources: list[str]) -> None:
    sizes = {
        resource: resource_size(ROOT / Path(resource.removeprefix("./")))
        for resource in resources
    }
    if OUTPUT.is_file():
        sizes["./sw.js"] = resource_size(OUTPUT)
    image_bytes = sum(size for resource, size in sizes.items() if Path(resource).suffix.lower() in IMAGE_SUFFIXES)
    total_bytes = sum(sizes.values())
    estimate = {
        "applicationBytes": f"{total_bytes - image_bytes:015d}",
        "imageBytes": f"{image_bytes:015d}",
        "totalBytes": f"{total_bytes:015d}",
    }
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")
    updated, count = ESTIMATE_META.subn(
        f"<meta name=\"gymratik-resource-estimate\" content='{json.dumps(estimate, separators=(',', ':'))}'>",
        html,
    )
    if count != 1:
        raise SystemExit("Se esperaba exactamente un meta de estimación de recursos en index.html")
    html_path.write_text(updated, encoding="utf-8", newline="\n")


def render(resources: list[str]) -> str:
    material = []
    for resource in resources:
        target = ROOT / Path(resource.removeprefix("./"))
        material.append(resource.encode("utf-8"))
        if target.is_file():
            material.append(fingerprint_content(target))
    fingerprint = hashlib.sha256(b"\n".join(material)).hexdigest()[:12]
    previous_source = OUTPUT.read_text(encoding="utf-8") if OUTPUT.is_file() else ""
    previous_match = re.search(r"const CACHE_NAME = '([^']+)';", previous_source)
    stored_previous_match = re.search(r"const PREVIOUS_CACHE_NAME = '([^']*)';", previous_source)
    previous_cache = previous_match.group(1) if previous_match else ""
    if previous_cache == f"entrenamiento-pwa-{fingerprint}" and stored_previous_match:
        previous_cache = stored_previous_match.group(1)
    precache = ",\n  ".join(f"{resource!r}" for resource in resources)
    sizes = {
        resource: resource_size(ROOT / Path(resource.removeprefix("./")))
        for resource in resources
    }
    size_map = ",\n  ".join(f"{resource!r}: {size}" for resource, size in sizes.items())
    return rf"""const CACHE_NAME = 'entrenamiento-pwa-{fingerprint}';
const PREVIOUS_CACHE_NAME = '{previous_cache}';
const PRECACHE = [
  {precache}
];
const RESOURCE_BYTES = {{
  {size_map}
}};
const CACHE_COMPLETE_KEY = new URL('./__gymratik_complete__', self.registration.scope).href;

async function reportProgress(completed, bytesCompleted, current = '') {{
  const clients = await self.clients.matchAll({{ type: 'window', includeUncontrolled: true }});
  const totalBytes = Object.values(RESOURCE_BYTES).reduce((sum, size) => sum + size, 0);
  clients.forEach((client) => client.postMessage({{
    type: 'PRECACHE_PROGRESS', cacheName: CACHE_NAME, completed,
    total: PRECACHE.length, bytesCompleted, totalBytes, current
  }}));
}}

async function refresh(request, cache) {{
  const response = await fetch(request, {{ cache: 'no-store' }});
  if (response.ok) await cache.put(request, response.clone());
  return response;
}}

async function preserveOneCompleteCache() {{
  const keys = (await caches.keys()).filter((key) => key.startsWith('entrenamiento-pwa-') && key !== CACHE_NAME);
  const core = PRECACHE.filter((path) => path === './index.html' || path.includes('/canonicas/'));
  const candidates = [];
  for (const key of keys) {{
    const cache = await caches.open(key);
    if (await cache.match(CACHE_COMPLETE_KEY)) {{
      candidates.push({{ key, size: (await cache.keys()).length, markedComplete: true }});
      continue;
    }}
    const hasCore = await Promise.all(core.map((path) => cache.match(new URL(path, self.registration.scope))));
    if (hasCore.every(Boolean)) candidates.push({{ key, size: (await cache.keys()).length, markedComplete: key === PREVIOUS_CACHE_NAME }});
  }}
  candidates.sort((left, right) => Number(right.markedComplete) - Number(left.markedComplete) || right.size - left.size);
  const keep = candidates[0]?.key;
  await Promise.all(keys.filter((key) => key !== keep).map((key) => caches.delete(key)));
}}

async function notifyClientsAppUpdated() {{
  const updatedAt = Date.now();
  const clients = await self.clients.matchAll({{ type: 'window', includeUncontrolled: true }});
  clients.forEach((client) => client.postMessage({{ type: 'APP_UPDATED', updatedAt, cacheName: CACHE_NAME }}));
}}

self.addEventListener('install', (event) => {{
  event.waitUntil((async () => {{
    for (let attempt = 0; attempt < 2; attempt += 1) {{
      const cache = await caches.open(CACHE_NAME);
      let completed = 0;
      let bytesCompleted = 0;
      try {{
        await reportProgress(completed, bytesCompleted);
        let nextIndex = 0;
        let firstError = null;
        const downloadNext = async () => {{
          while (!firstError) {{
            const index = nextIndex++;
            if (index >= PRECACHE.length) return;
            const path = PRECACHE[index];
            try {{
              const request = new Request(path, {{ cache: 'reload' }});
              const response = await fetch(request);
              if (!response.ok) throw new Error(`No se pudo descargar ${{path}} (${{response.status}})`);
              await cache.put(request, response);
              completed += 1;
              bytesCompleted += RESOURCE_BYTES[path] || 0;
              await reportProgress(completed, bytesCompleted, path);
            }} catch (error) {{ firstError = firstError || error; }}
          }}
        }};
        await Promise.all(Array.from({{ length: Math.min(6, PRECACHE.length) }}, downloadNext));
        if (firstError) throw firstError;
        await cache.put(CACHE_COMPLETE_KEY, new Response(JSON.stringify({{ cacheName: CACHE_NAME, completedAt: Date.now() }}), {{ headers: {{ 'content-type': 'application/json' }} }}));
        break;
      }} catch (error) {{
        await caches.delete(CACHE_NAME);
        if (attempt !== 0 || error?.name !== 'QuotaExceededError') throw error;
        await preserveOneCompleteCache();
      }}
    }}
    // Activar solo después de descargar y marcar completo todo el paquete.
    // El progreso de entrenamiento vive en IndexedDB/localStorage, fuera de Cache API.
    await self.skipWaiting();
  }})());
}});

self.addEventListener('message', (event) => {{
  if (event.data?.type === 'ACTIVATE_UPDATE' && self.registration.waiting === self) self.skipWaiting();
  if (event.data?.type === 'GET_VERSION_STATUS') {{
    event.source?.postMessage({{ type: 'VERSION_STATUS', cacheName: CACHE_NAME, total: PRECACHE.length }});
  }}
}});

self.addEventListener('activate', (event) => {{
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key.startsWith('entrenamiento-pwa-') && key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
      .then(() => notifyClientsAppUpdated())
  );
}});

self.addEventListener('fetch', (event) => {{
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  event.respondWith((async () => {{
    const cache = await caches.open(CACHE_NAME);
    const cached = await cache.match(request);
    const isNavigation = request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html');
    const bypassCache = ['no-cache', 'no-store', 'reload'].includes(request.cache);

    if (cached && !bypassCache) return cached;
    try {{
      return await refresh(request, cache);
    }} catch (error) {{
      if (cached) return cached;
      if (isNavigation) {{
        const shell = await cache.match(new URL('./index.html', self.registration.scope));
        if (!shell) return undefined;
        const baseUrl = new URL('./', self.registration.scope).href;
        let html = await shell.text();
        if (/<base\b/i.test(html)) html = html.replace(/<base\b[^>]*>/i, `<base href="${{baseUrl}}">`);
        else html = html.replace(/<head(?:\s[^>]*)?>/i, (head) => `${{head}}<base href="${{baseUrl}}">`);
        const headers = new Headers(shell.headers);
        headers.delete('content-length');
        headers.delete('content-encoding');
        return new Response(html, {{ status: shell.status, statusText: shell.statusText, headers }});
      }}
      throw error;
    }}
  }})());
}});
"""


def main() -> None:
    resources = build_precache()
    for _ in range(5):
        previous_size = OUTPUT.stat().st_size if OUTPUT.is_file() else -1
        update_resource_estimate(resources)
        generated = render(resources)
        OUTPUT.write_text(generated, encoding="utf-8", newline="\n")
        if len(generated.encode("utf-8")) == previous_size:
            break
    else:
        raise SystemExit("No se estabilizó el tamaño estimado del paquete PWA en 5 iteraciones")
    print(f"PWA_SERVICE_WORKER_OK resources={len(resources)} cache={resources[0]}")


if __name__ == "__main__":
    main()
