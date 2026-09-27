import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.build_pwa_service_worker import (
    CANONICAL_DIR,
    ROUTINE_FILES,
    build_precache,
    fingerprint_content,
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

    def test_profile_mascots_are_part_of_the_offline_precache(self):
        for asset in ("mouse-female-effort.webp", "mouse-male-effort.webp", "mascot-install-phone.webp"):
            self.assertIn(f"data/profile/{asset}", self.service_worker)
            self.assertIn(f"data/profile/{asset}", self.generator)

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
                self.assertIn("await self.skipWaiting()", source)
                self.assertLess(source.index("await cache.put(CACHE_COMPLETE_KEY"), source.index("await self.skipWaiting()"))
                self.assertIn("ACTIVATE_UPDATE", source)
                self.assertIn("self.clients.claim()", source)
                self.assertIn("notifyClientsAppUpdated()", source)
                self.assertIn("QuotaExceededError", source)
                self.assertIn("key.startsWith('entrenamiento-pwa-')", source)
                self.assertNotIn("cache.addAll(PRECACHE)", source)

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
