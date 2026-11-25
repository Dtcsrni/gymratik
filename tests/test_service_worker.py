import re
import unittest
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.build_pwa_service_worker import (
    CANONICAL_DIR,
    HTML_ATTR_PATTERN,
    ROUTINE_FILES,
    build_precache,
    fingerprint_content,
    homepage_resources,
    manifest_icon_resources,
    quote_portrait_resources,
    render,
    release_manifest,
    resource_size,
    routine_resources,
)


ROOT = Path(__file__).parents[1]
SW = ROOT / "sw.js"
GENERATOR = ROOT / "scripts" / "build_pwa_service_worker.py"


class ServiceWorkerContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service_worker = SW.read_text(encoding="utf-8")
        cls.generator = GENERATOR.read_text(encoding="utf-8")
        cls.homepage = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_local_resources_are_cache_first_with_offline_fallback(self):
        for source in (self.service_worker, self.generator):
            self.assertIn("progress-store.js", source)
            self.assertIn("if (cached && !bypassCache) return cached", source)
            self.assertIn("if (cached) return cached", source)

    def test_shared_update_client_is_in_the_complete_version_cache(self):
        self.assertIn("./page-update-client.js", set(build_precache()))
        self.assertIn("./page-update-client.js", self.service_worker)

    def test_resource_scanner_ignores_original_source_provenance_metadata(self):
        snippet = '<img data-original-src="https://example.test/source.jpg" src="./image.jpg">'
        self.assertEqual(HTML_ATTR_PATTERN.findall(snippet), ["./image.jpg"])

    def test_manifest_icon_inventory_rejects_nonlocal_missing_and_traversal_paths(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "icon-192.png").write_bytes(b"png")
            self.assertEqual(manifest_icon_resources({"icons": [{"src": "./icon-192.png"}]}, root), ["./icon-192.png"])
            for source in ("https://example.test/icon.png", "../outside.png", "..\\outside.png", "./missing.png"):
                with self.subTest(source=source), self.assertRaises(SystemExit):
                    manifest_icon_resources({"icons": [{"src": source}]}, root)
        with self.assertRaises(SystemExit):
            manifest_icon_resources({"icons": []})

    def test_profile_mascots_are_part_of_the_offline_precache(self):
        for asset in ("mouse-female-effort.webp", "mouse-male-effort.webp", "mascot-install-phone.webp"):
            self.assertIn(f"data/profile/{asset}", self.service_worker)
            self.assertIn(f"data/profile/{asset}", self.generator)

    def test_page_brand_mark_is_precached_but_pwa_icons_are_manifest_owned(self):
        page_asset = "assets/branding/gymratik-mascots-mark-v2.png"
        self.assertIn(f"./{page_asset}", homepage_resources())
        self.assertIn(f"./{page_asset}", set(build_precache()))
        self.assertIn("manifest_icon_resources(manifest)", self.generator)
        manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))
        icon_paths = {icon["src"] for icon in manifest["icons"]}
        self.assertEqual(len(icon_paths), 4)
        self.assertTrue(all("gymratik-pwa-icon-v8-" in path for path in icon_paths))
        self.assertNotIn(f"./{page_asset}", icon_paths)
        self.assertIn(f'src="./{page_asset}"', self.homepage)

    def test_pose_loop_and_static_fallback_are_precached_offline(self):
        resources = set(build_precache())
        for asset in (
            "./assets/branding/gymratik-cover-seated-breath-30fps.webp",
            "./assets/branding/gymratik-cover-seated-v1-poster.webp",
        ):
            with self.subTest(asset=asset):
                self.assertIn(asset, resources)
                self.assertIn(asset.removeprefix("./"), self.service_worker)

    def test_only_runtime_quote_portraits_are_precached_offline(self):
        portraits = quote_portrait_resources()
        resources = set(build_precache())
        self.assertEqual(len(portraits), 1)
        self.assertTrue(portraits <= resources)
        self.assertTrue(all((ROOT / resource.removeprefix("./")).is_file() for resource in portraits))
        self.assertTrue(all(resource.removeprefix("./") in self.service_worker for resource in portraits))

    def test_all_routine_covers_are_offline_precached(self):
        resources = set(build_precache())
        for day in range(1, 5):
            asset = f"./assets/branding/routine-covers/day{day}.webp"
            with self.subTest(day=day):
                self.assertIn(asset, resources)
                self.assertTrue((ROOT / asset.removeprefix("./")).is_file())

    def test_worker_fingerprint_normalizes_text_line_endings_only(self):
        with TemporaryDirectory() as temp_dir:
            text_asset = Path(temp_dir) / "routine.css"
            binary_asset = Path(temp_dir) / "image.png"
            text_asset.write_bytes(b"a\r\nb\rc")
            binary_asset.write_bytes(b"a\r\nb\rc")

            self.assertEqual(fingerprint_content(text_asset), b"a\nb\nc")
            self.assertEqual(fingerprint_content(binary_asset), b"a\r\nb\rc")
            self.assertEqual(resource_size(text_asset), len(b"a\nb\nc"))
            self.assertEqual(resource_size(binary_asset), len(b"a\r\nb\rc"))

    def test_generated_worker_cache_fingerprint_matches_current_precache(self):
        generated = render(build_precache())
        generated_name = re.search(r"const CACHE_NAME = '([^']+)';", generated)
        checked_in_name = re.search(r"const CACHE_NAME = '([^']+)';", self.service_worker)

        self.assertIsNotNone(generated_name)
        self.assertIsNotNone(checked_in_name)
        self.assertEqual(
            checked_in_name.group(1),
            generated_name.group(1),
            "sw.js está obsoleto: ejecuta python scripts/build_pwa_service_worker.py",
        )

    def test_shared_routine_stylesheet_is_part_of_the_offline_precache(self):
        for source in (self.service_worker, self.generator):
            self.assertIn("routine-liquid-glass-v13.css", source)

    def test_worker_downloads_complete_package_before_activating_updates(self):
        for source in (self.service_worker, self.generator):
            with self.subTest(source=source[:40]):
                self.assertIn("PRECACHE_PROGRESS", source)
                self.assertIn("Math.min(6, installResources.length)", source)
                self.assertIn("await Promise.all(Array.from", source)
                self.assertIn("if (firstError) throw firstError", source)
                self.assertIn("if (!self.registration.active) await self.skipWaiting()", source)
                self.assertLess(source.index("await cache.put(CACHE_COMPLETE_KEY"), source.index("if (!self.registration.active) await self.skipWaiting()"))
                self.assertIn("event.waitUntil(self.skipWaiting())", source)
                self.assertIn("self.clients.claim()", source)
                self.assertIn("notifyClientsAppUpdated()", source)
                self.assertIn("QuotaExceededError", source)
                self.assertIn("key.startsWith('entrenamiento-pwa-')", source)
                self.assertNotIn("cache.addAll(PRECACHE)", source)

    def test_updates_are_staged_until_the_application_authorizes_activation(self):
        for source in (self.service_worker, self.generator):
            with self.subTest(source=source[:40]):
                install = source.split("self.addEventListener('install'", 1)[1].split("self.addEventListener('message'", 1)[0]
                message = source.split("self.addEventListener('message'", 1)[1].split("self.addEventListener('activate'", 1)[0]
                self.assertIn("if (!self.registration.active) await self.skipWaiting()", install)
                self.assertNotIn("await self.skipWaiting()", install.replace("if (!self.registration.active) await self.skipWaiting()", ""))
                self.assertIn("event.data?.type === 'ACTIVATE_UPDATE'", message)
                self.assertIn("event.waitUntil(self.skipWaiting())", message)
                self.assertNotIn("self.registration.waiting === self", message)
                self.assertRegex(
                    message,
                    r"if \(event\.data\?\.type === 'ACTIVATE_UPDATE'\) event\.waitUntil\(self\.skipWaiting\(\)\)",
                )

    def test_runtime_cache_is_bounded_to_precache_resources_and_revalidates_http_cache(self):
        for source in (self.service_worker, self.generator):
            with self.subTest(source=source[:40]):
                self.assertIn("new Set(PRECACHE.map", source)
                self.assertIn("PRECACHE_URLS.has", source)
                self.assertIn("cache: 'no-cache'", source)
                self.assertIn("ignoreSearch: true", source)

    def test_exercise_gifs_and_session_mascots_are_precached(self):
        resources = build_precache()
        exercise_gifs = [resource for resource in resources if "/videos/" in resource and resource.lower().endswith(".gif")]
        self.assertGreaterEqual(len(exercise_gifs), 32)
        self.assertTrue(all((ROOT / resource.removeprefix("./")).is_file() for resource in exercise_gifs))
        for resource in exercise_gifs:
            self.assertIn(resource, self.service_worker)
        for variant in ("female", "male", "neutral"):
            for state in ("exercise", "rest"):
                with self.subTest(variant=variant, state=state):
                    self.assertIn(f"{variant}-{state}-25fps.gif", self.service_worker)
                    self.assertIn(f"{variant}-{state}-still.webp", self.service_worker)
        for variant in ("female", "male"):
            atlas = f"./data/profile/mascot-motion/states-v1/{variant}-pose-atlas.png"
            with self.subTest(atlas=atlas):
                self.assertIn(atlas, build_precache())
                self.assertTrue((ROOT / atlas.removeprefix("./")).is_file())
                self.assertIn(atlas, self.service_worker)

    def test_every_warmup_choice_gif_and_poster_is_in_the_offline_precache(self):
        resources = set(build_precache())
        for routine_name in ROUTINE_FILES:
            routine = CANONICAL_DIR / routine_name
            with self.subTest(routine=routine_name):
                html = routine.read_text(encoding="utf-8")
                self.assertIn("data-gif-src=", html)
                self.assertIn("data-poster-src=", html)
                referenced = routine_resources(routine)
                alternatives = {
                    resource for resource in referenced
                    if "/videos/" in resource and resource.lower().endswith((".gif", ".webp"))
                }
                self.assertTrue(alternatives)
                self.assertTrue(alternatives <= resources, sorted(alternatives - resources))

    def test_complete_cache_marker_is_written_after_download(self):
        for source in (self.service_worker, self.generator):
            with self.subTest(source=source[:40]):
                self.assertIn("__gymratik_complete__", source)
                self.assertIn("PREVIOUS_CACHE_NAME", source)

    def test_homepage_shows_the_active_service_worker_version(self):
        release = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
        version = json.loads((ROOT / "app-version.json").read_text(encoding="utf-8"))["version"]
        self.assertIn('id="appVersion"', self.homepage)
        self.assertIn(f'class="brand-version" aria-label="Versión {version}">v{version}', self.homepage)
        self.assertIn("event.data?.type === 'VERSION_STATUS'", self.homepage)
        self.assertIn("postMessage({ type: 'GET_VERSION_STATUS' })", self.homepage)
        self.assertIn("cacheName: CACHE_NAME", self.service_worker)
        self.assertIn("appVersion.textContent = `v${version}`", self.homepage)
        self.assertEqual(release["version"], version)
        self.assertEqual(release["buildId"], re.search(r'const BUILD_ID = "([^"]+)"', self.service_worker).group(1))
        self.assertEqual(release, release_manifest(build_precache()))

    def test_release_manifest_verifies_integrity_and_reuses_unchanged_resources(self):
        manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
        resources = {entry["url"]: entry for entry in manifest["resources"]}
        self.assertNotIn("./release-manifest.json", resources)
        self.assertEqual(set(resources), set(build_precache()) - {"./release-manifest.json"})
        for entry in resources.values():
            self.assertRegex(entry["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(entry["size"], 0)
        for marker in (
            "crypto.subtle.digest('SHA-256'",
            "const previousComplete = Boolean(previousMarker)",
            "if (bytes.byteLength === entry.size && hex === entry.sha256)",
            "const manifestMatches = manifest?.schemaVersion === 1",
            "self.__gymratikTransferTotalBytes ??",
        ):
            self.assertIn(marker, self.service_worker)

    def test_new_version_startup_failure_rolls_back_to_complete_previous_cache_and_offers_retry(self):
        client = (ROOT / "page-update-client.js").read_text(encoding="utf-8")
        self.assertIn("activationKey", client)
        self.assertIn("La versión nueva no pudo validar el inicio", client)
        self.assertIn("retryToast", client)
        self.assertIn("setTimeout(dismissRetryToast, toastDurationMs)", client)
        self.assertIn("setTimeout(() => requestRollback('startup-timeout'), 30000)", client)
        self.assertIn("GYMRATIK_STARTUP_FAILED", client)
        self.assertIn("GYMRATIK_STORAGE_FAILED", client)
        self.assertIn("GYMRATIK_ROLLBACK_READY", client)
        self.assertIn("gymratik-startup-ready", client)
        self.assertNotIn("unregister()", client)
        for source in (self.service_worker, self.generator):
            self.assertIn("ROLLBACK_WINDOW_MS = 24 * 60 * 60 * 1000", source)
            self.assertIn("GYMRATIK_ROLLBACK_UNAVAILABLE", source)
            self.assertIn("ROLLBACK_KEY", source)
            self.assertIn("serveStableVersion(request, stable)", source)
            self.assertIn("Reintentar versión nueva", source)
            self.assertIn("!keep.has(key)", source)
            self.assertIn("RETRY_CANDIDATE", source)

    def test_update_health_check_is_non_destructive_and_requires_indexeddb_round_trip(self):
        store = (ROOT / "progress-store.js").read_text(encoding="utf-8")
        client = (ROOT / "page-update-client.js").read_text(encoding="utf-8")
        self.assertIn("async function checkStorage()", store)
        self.assertIn("transaction(db, [META_STORE], 'readwrite'", store)
        self.assertIn("store.put(probe)", store)
        self.assertIn("store.get(probeKey)", store)
        self.assertIn("store.delete(probeKey)", store)
        self.assertNotIn("PROGRESS_STORE], 'readwrite'", store.split("async function checkStorage()", 1)[1].split("window.TrainingProgressStore", 1)[0])
        self.assertIn("await Promise.all([store.getHistory(1), store.getProfile()])", client)

    def test_service_worker_serves_stable_cache_after_critical_failure_and_can_retry_candidate(self):
        script = r"""
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const source = fs.readFileSync(process.argv[1], 'utf8');
const scope = 'https://gymratik.test/';
const activeName = source.match(/const CACHE_NAME = '([^']+)'/)[1];
const previousName = source.match(/const PREVIOUS_CACHE_NAME = '([^']+)'/)[1];
const completeKey = new URL('./__gymratik_complete__', scope).href;
class TestCache {
  constructor() { this.entries = new Map(); }
  key(value) { return value instanceof Request ? value.url : new URL(String(value), scope).href; }
  async match(value) { const direct = this.entries.get(this.key(value)); return direct?.clone(); }
  async put(value, response) { this.entries.set(this.key(value), response.clone()); }
  async delete(value) { return this.entries.delete(this.key(value)); }
  async keys() { return [...this.entries.keys()].map(url => new Request(url)); }
}
const cacheMap = new Map([[activeName, new TestCache()], [previousName, new TestCache()]]);
const caches = {
  async open(name) { if (!cacheMap.has(name)) cacheMap.set(name, new TestCache()); return cacheMap.get(name); },
  async keys() { return [...cacheMap.keys()]; }, async delete(name) { return cacheMap.delete(name); }
};
const active = cacheMap.get(activeName), stable = cacheMap.get(previousName);
const rollbackKey = new URL('./__gymratik_rollback__', scope).href;
const probationKey = new URL('./__gymratik_probation__', scope).href;
active.entries.set(probationKey, new Response(JSON.stringify({ activatedAt: Date.now() })));
stable.entries.set(completeKey, new Response(JSON.stringify({ version: '0.7.27' })));
stable.entries.set(new URL('./index.html', scope).href, new Response('<html><head></head><body>Versión estable</body></html>', { headers: { 'content-type': 'text/html' } }));
const handlers = {};
const self = { registration: { scope, active: {} }, clients: { async claim() {}, async matchAll() { return []; } }, skipWaiting() {}, addEventListener(name, callback) { handlers[name] = callback; } };
vm.runInNewContext(source, { self, caches, URL, Map, Set, Request, Response, Headers, fetch: async () => { throw new Error('offline'); }, crypto: { subtle: {} }, console, Date, Promise, Uint8Array, Array, Object, Number, Error, Math });
async function send(type) {
  const tasks = [], replies = [];
  handlers.message({ data: { type, code: 'test-critical-error' }, source: { postMessage(reply) { replies.push(reply); } }, waitUntil(task) { tasks.push(task); } });
  await Promise.all(tasks);
  return replies;
}
(async () => {
  const replies = await send('GYMRATIK_STARTUP_FAILED');
  assert.strictEqual(replies[0].type, 'GYMRATIK_ROLLBACK_READY');
  assert.strictEqual(replies[0].stableVersion, '0.7.27');
  const request = { url: new URL('./index.html', scope).href, method: 'GET', mode: 'navigate', cache: 'default', headers: new Headers({ accept: 'text/html' }) };
  let responsePromise;
  handlers.fetch({ request, respondWith(value) { responsePromise = value; } });
  const response = await responsePromise;
  const html = await response.text();
  assert.match(html, /Versión estable/);
  assert.match(html, /Reintentar versión nueva/);
  assert.strictEqual(response.headers.get('content-type'), 'text/html; charset=utf-8');
  await send('RETRY_CANDIDATE');
  assert.strictEqual(await active.match(rollbackKey), undefined, 'manual retry clears rollback mode without changing training storage');
  active.entries.set(probationKey, new Response(JSON.stringify({ activatedAt: Date.now() - 25 * 60 * 60 * 1000 })));
  const expired = await send('GYMRATIK_STORAGE_FAILED');
  assert.strictEqual(expired[0].type, 'GYMRATIK_ROLLBACK_UNAVAILABLE', 'rollback is limited to the 24-hour stabilization window');
  assert.strictEqual(await active.match(rollbackKey), undefined);
  console.log(JSON.stringify({ ok: true }));
})().catch(error => { console.error(error); process.exit(1); });
"""
        result = subprocess.run(["node", "-e", script, str(ROOT / "sw.js")], cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"ok": True})

    def test_deep_offline_navigation_fallback_anchors_shell_to_registration_scope(self):
        for source in (self.service_worker, self.generator):
            with self.subTest(source=source[:40]):
                self.assertIn("new URL('./', self.registration.scope).href", source)
                self.assertIn("<base href=", source)
                self.assertIn("headers.delete('content-length')", source)


if __name__ == "__main__":
    unittest.main()
