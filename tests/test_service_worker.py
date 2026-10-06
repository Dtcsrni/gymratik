import re
import unittest
import json
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
        self.assertTrue(all("gymratik-pwa-icon-v7-" in path for path in icon_paths))
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

    def test_every_runtime_quote_portrait_is_precached_offline(self):
        portraits = quote_portrait_resources()
        resources = set(build_precache())
        self.assertEqual(len(portraits), 58)
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
                self.assertIn("Math.min(6, PRECACHE.length)", source)
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
        self.assertIn('id="appVersion"', self.homepage)
        self.assertIn('class="brand-version" aria-label="Versión 0.4.4">v0.4.4', self.homepage)
        self.assertIn("event.data?.type === 'VERSION_STATUS'", self.homepage)
        self.assertIn("postMessage({ type: 'GET_VERSION_STATUS' })", self.homepage)
        self.assertIn("cacheName: CACHE_NAME", self.service_worker)
        self.assertIn("appVersion.textContent = `v${version.slice(0, 8)}`", self.homepage)

    def test_deep_offline_navigation_fallback_anchors_shell_to_registration_scope(self):
        for source in (self.service_worker, self.generator):
            with self.subTest(source=source[:40]):
                self.assertIn("new URL('./', self.registration.scope).href", source)
                self.assertIn("<base href=", source)
                self.assertIn("headers.delete('content-length')", source)


if __name__ == "__main__":
    unittest.main()
