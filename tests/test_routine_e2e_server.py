import sys
import threading
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from e2e_routine_activity_check import PORT, assert_image_inventory, create_isolated_server  # noqa: E402


class RoutineE2EServerTests(unittest.TestCase):
    def test_synthetic_server_uses_an_isolated_loopback_port(self):
        server = create_isolated_server()
        try:
            address, port = server.server_address
            self.assertEqual(address, "127.0.0.1")
            self.assertGreater(port, 0)
            self.assertNotEqual(port, PORT)
        finally:
            server.server_close()

    def test_image_inventory_skips_decode_for_unrendered_lazy_images(self):
        from playwright.sync_api import sync_playwright

        server = create_isolated_server()
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="msedge", headless=True)
                try:
                    page = browser.new_page()
                    page.goto(f"http://127.0.0.1:{server.server_address[1]}/")
                    page.set_content(f"""
                      <img alt="visible fixture" width="24" height="24"
                        src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24'%3E%3Crect width='24' height='24' fill='teal'/%3E%3C/svg%3E">
                      <img id="lazy-hidden" alt="hidden lazy fixture" hidden loading="lazy"
                        src="http://127.0.0.1:{server.server_address[1]}/pending.jpg">
                      <script>
                        window.__hiddenDecodeCalls = 0;
                        document.querySelector('#lazy-hidden').decode = () => {{
                          window.__hiddenDecodeCalls += 1;
                          return Promise.resolve();
                        }};
                      </script>
                    """)
                    result = assert_image_inventory(page, "fixture de imagen diferida")
                    self.assertEqual(page.evaluate("window.__hiddenDecodeCalls"), 0)
                    self.assertEqual(result["images"], 2)
                    self.assertEqual(result["rendered"], 1)
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
