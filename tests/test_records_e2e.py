from __future__ import annotations

import functools
import threading
import time
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class QuietStaticHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass

    def guess_type(self, path: str) -> str:
        return {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".png": "image/png",
            ".webp": "image/webp",
            ".jpg": "image/jpeg",
            ".gif": "image/gif",
            ".json": "application/json",
        }.get(Path(path).suffix.lower(), "application/octet-stream")


def milestone_fixture() -> dict:
    now = int(time.time() * 1000)
    day = 24 * 60 * 60 * 1000

    def session(session_id: str, days_ago: int, load: float, reps: int = 8, extra: list[dict] | None = None) -> dict:
        started_at = now - days_ago * day
        performance = [{
            "exerciseId": "row",
            "exerciseName": "Remo horizontal en máquina",
            "setKey": "e1s1",
            "setNumber": 1,
            "reps": reps,
            "load": load,
            "loadUnit": "kg",
            "loadKg": load,
            "updatedAt": started_at + 1_000,
        }]
        performance.extend(extra or [])
        return {
            "sessionId": session_id,
            "routineId": "day1",
            "label": "Día 1 · Tirón",
            "startedAt": started_at,
            "endedAt": started_at + 60 * 60 * 1000,
            "updatedAt": started_at + 60 * 60 * 1000,
            "status": "completed",
            "completionKind": "complete",
            "completedSeries": 2,
            "totalSeries": 3,
            "performance": performance,
        }

    return {
        "format": "gymratik-backup",
        "schemaVersion": 3,
        "exportedAt": now,
        "profile": {"profileId": "local-default", "units": "metric", "sex": "female", "schemaVersion": 3},
        "data": {
            "progress": [],
            "activity": [],
            "sessions": [
                session("fixture-1", 20, 20, extra=[{
                    "exerciseId": "row", "exerciseName": "Remo horizontal en máquina", "setKey": "e1s2",
                    "setNumber": 2, "reps": 10, "load": 2, "loadUnit": "kg", "loadKg": 2,
                }]),
                session("fixture-2", 15, 22.5, reps=7),
                session("fixture-3", 10, 80),
                session("fixture-4", 5, 20),
                session("fixture-5", 1, 12.5),
            ],
        },
    }


class RecordsMilestoneE2ETests(unittest.TestCase):
    def test_installed_records_flow_filters_and_excludes_implausible_loads(self) -> None:
        handler = functools.partial(QuietStaticHandler, directory=str(ROOT))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="msedge", headless=True)
                try:
                    context = browser.new_context(viewport={"width": 1280, "height": 1000})
                    context.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1','true')")
                    page = context.new_page()
                    page_errors: list[str] = []
                    page.on("pageerror", lambda error: page_errors.append(str(error)))
                    page.goto(f"http://127.0.0.1:{server.server_address[1]}/records.html", wait_until="domcontentloaded")
                    page.wait_for_function("Boolean(window.TrainingProgressStore?.importData)")
                    page.evaluate("payload => window.TrainingProgressStore.importData(payload)", milestone_fixture())
                    page.wait_for_function("document.querySelector('#heroLoad')?.textContent.includes('22.5 kg')")

                    self.assertEqual(page.locator("#heroLoad").inner_text(), "22.5 kg · 49.6 lb")
                    self.assertEqual(page.locator("#milestoneExercises").inner_text(), "1")
                    self.assertEqual(page.locator("#milestonePrs").inner_text(), "1")
                    self.assertEqual(page.locator("#milestoneCorrections").inner_text(), "3")
                    self.assertIn("3 sesiones válidas", page.locator("#milestoneList").inner_text())
                    self.assertEqual(page.locator("#milestoneList .milestone-sparkline").count(), 1)
                    self.assertRegex(page.locator("#milestoneList .milestone-delta").inner_text(), r"Δ última captura −2\.5 kg \(-11[,.]1 %\)")
                    self.assertRegex(page.locator("#milestoneList .milestone-gain").inner_text(), r"\+12[,.]5 % desde tu primera sesión válida")
                    self.assertIn("máximos de sesión validados", page.locator("#milestoneList .milestone-sparkline").get_attribute("aria-label"))
                    self.assertEqual(page.locator(".record-review-flag").count(), 3)
                    self.assertTrue(page.locator("#reviewDetails").is_visible())
                    page.locator("#reviewDetails > summary").click()
                    self.assertEqual(page.locator("#reviewList .review-item").count(), 3)
                    self.assertEqual(page.locator(".hero-art").get_attribute("data-sex"), "female")
                    self.assertEqual(page.locator(".hero-mascot--male").evaluate("element => getComputedStyle(element).display"), "none")
                    self.assertEqual(page.locator(".hero-mascot--female").evaluate("element => getComputedStyle(element).animationName"), "mascot-bob")

                    page.locator("#periodFilter").select_option("7")
                    self.assertEqual(page.locator("#statSessions").inner_text(), "2")
                    page.locator("#periodFilter").select_option("all")
                    self.assertEqual(page.locator("#statSessions").inner_text(), "5")
                    self.assertIn("5 de 5 sesiones", page.locator("#dataStatus").inner_text())
                    stored = page.evaluate("window.TrainingProgressStore.exportData()")
                    self.assertEqual(len(stored["data"]["sessions"]), 5)
                    raw_loads = [record["load"] for session in stored["data"]["sessions"] for record in session["performance"]]
                    self.assertIn(80, raw_loads)
                    self.assertIn(2, raw_loads)
                    self.assertIn(12.5, raw_loads)

                    for width in (320, 390, 1280):
                        page.set_viewport_size({"width": width, "height": 900})
                        geometry = page.evaluate("""() => {
                          const hero = document.querySelector('.milestone-hero').getBoundingClientRect();
                          const title = document.querySelector('#pageTitle').getBoundingClientRect();
                          const art = document.querySelector('.hero-art').getBoundingClientRect();
                          return {width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
                            hero: [hero.left, hero.right], title: [title.left, title.right], art: [art.left, art.right]};
                        }""")
                        self.assertLessEqual(geometry["scrollWidth"], width, geometry)
                        self.assertGreaterEqual(geometry["title"][0], geometry["hero"][0] - 1, geometry)
                        self.assertLessEqual(geometry["title"][1], geometry["hero"][1] + 1, geometry)

                    reduced = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
                    reduced.add_init_script("sessionStorage.setItem('gymratik-install-confirmed-v1','true')")
                    reduced_page = reduced.new_page()
                    reduced_page.goto(f"http://127.0.0.1:{server.server_address[1]}/records.html", wait_until="domcontentloaded")
                    self.assertEqual(reduced_page.locator(".hero-mascot--female").evaluate("element => getComputedStyle(element).animationName"), "none")
                    reduced.close()
                    context.close()
                    self.assertEqual(page_errors, [])
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
