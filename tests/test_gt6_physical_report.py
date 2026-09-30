import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from e2e_gt6_physical import ReusablePhysicalContext, bring_android_page_to_foreground, require_installed_webapk_foreground, resolve_cdp_websocket_url, resolve_device_metrics, snapshot_installed_user_data, summarize_day  # noqa: E402
from e2e_routine_activity_check import click_control, dispatch_touch_hold, select_valid_performance  # noqa: E402


class PhysicalE2EReportTests(unittest.TestCase):
    def test_routine_controls_use_physical_touch_when_a_gt6_tap_adapter_is_attached(self):
        class FakeLocator:
            def __init__(self, page):
                self.page = page
                self.mouse_clicks = 0

            def click(self):
                self.mouse_clicks += 1

        physical_calls = []
        page = SimpleNamespace(_gt6_physical_tap=physical_calls.append)
        locator = FakeLocator(page)
        click_control(locator)
        self.assertEqual(physical_calls, [locator])
        self.assertEqual(locator.mouse_clicks, 0)

    def test_routine_controls_keep_browser_clicks_in_synthetic_contexts(self):
        locator = SimpleNamespace(page=SimpleNamespace(), mouse_clicks=0)
        locator.click = lambda: setattr(locator, "mouse_clicks", locator.mouse_clicks + 1)
        click_control(locator)
        self.assertEqual(locator.mouse_clicks, 1)

    def test_routine_hold_controls_delegate_to_real_physical_touch_adapter(self):
        calls = []
        page = SimpleNamespace(_gt6_physical_hold=lambda *args, **kwargs: calls.append((args, kwargs)))
        button = object()
        dispatch_touch_hold(page, button, 5_150, virtual_clock=False)
        self.assertEqual(calls, [((page, button, 5_150), {"release_click": True, "virtual_clock": False})])

    def test_performance_sliders_delegate_to_real_physical_touch_adapter(self):
        calls = []
        card = SimpleNamespace(page=SimpleNamespace(_gt6_physical_select_performance=calls.append))
        select_valid_performance(card)
        self.assertEqual(calls, [card])

    def test_taps_use_complete_touch_gesture_not_unreleased_manual_touchstart(self):
        source = (ROOT / "scripts" / "e2e_gt6_physical.py").read_text(encoding="utf-8")
        tap = source.split("def android_tap", 1)[1].split("def android_touch_hold", 1)[0]
        self.assertIn("Input.synthesizeTapGesture", tap)
        self.assertIn("event.composedPath().includes(element)", tap)
        self.assertNotIn('"type": "touchStart"', tap)

    def test_long_press_release_synthesizes_missing_android_click_once(self):
        source = (ROOT / "scripts" / "e2e_gt6_physical.py").read_text(encoding="utf-8")
        hold = source.split("def android_touch_hold", 1)[1].split("def android_select_valid_performance", 1)[0]
        self.assertIn("__gt6HoldReleaseClick", hold)
        self.assertIn("window.__gt6HoldButton = element", hold)
        self.assertIn('"type": "touchEnd"', hold)
        self.assertIn("if release_click", hold)
        self.assertIn("window.__gt6HoldButton.click()", hold)
        self.assertNotIn("document.elementFromPoint", hold)
        self.assertIn("mismo nodo presionado", hold)
        self.assertIn("No se entregó el click de liberación al botón mantenido", hold)
        self.assertIn('release_target["connected"] and not release_target["disabled"]', hold)
        self.assertNotIn("document.elementFromPoint", hold)
        self.assertIn('release_target["connected"] and not release_target["disabled"]', hold)

    def test_reusable_context_never_creates_or_closes_a_chrome_profile(self):
        class FakePage:
            def __init__(self):
                self.url = "http://localhost:8768/routine.html"
                self.context = SimpleNamespace(add_init_script=lambda script: setattr(self, "init_script", script))
                self.evaluated = []
                self.routes = []

            def evaluate(self, script):
                self.evaluated.append(script)

            def route(self, pattern, handler):
                self.routes.append((pattern, handler))

            def unroute(self, pattern, handler):
                self.routes.remove((pattern, handler))

        page = FakePage()
        navigations = []
        context = ReusablePhysicalContext(
            page, "http://localhost:8768", "http://127.0.0.1:8768/",
            lambda target, url, **options: navigations.append((target, url, options)),
        )
        context.add_init_script("sessionStorage.setItem('test-only', '1')")
        self.assertIn("location.origin === \"http://localhost:8768\"", page.init_script)
        self.assertIs(context.new_page(), page)

        context.close()

        self.assertEqual(len(page.evaluated), 1)
        self.assertIn("localStorage.clear()", page.evaluated[0])
        self.assertEqual(navigations[0][1], "http://127.0.0.1:8768/")

    def test_visible_device_motion_reactivates_android_target_and_requires_advancing_timeline(self):
        class FakePage:
            def __init__(self, advances=True):
                self.front = False
                self.timeline = 1000
                self.advances = advances

            def bring_to_front(self):
                self.front = True

            def wait_for_function(self, _condition, timeout):
                self.asserted_visible_timeout = timeout

            def evaluate(self, _expression):
                return self.timeline

            def wait_for_timeout(self, milliseconds):
                if self.advances:
                    self.timeline += milliseconds

        page = FakePage()
        with patch("e2e_gt6_physical.require_installed_webapk_foreground", return_value="test-device"):
            evidence = bring_android_page_to_foreground(page)
        self.assertTrue(page.front)
        self.assertEqual(page.asserted_visible_timeout, 15_000)
        self.assertGreater(evidence["timelineAfterMs"], evidence["timelineBeforeMs"])

        with patch("e2e_gt6_physical.require_installed_webapk_foreground", return_value="test-device"):
            with self.assertRaisesRegex(RuntimeError, "timeline visual"):
                bring_android_page_to_foreground(FakePage(advances=False))

    def test_native_foreground_guard_requires_the_installed_webapk(self):
        successful = [
            SimpleNamespace(returncode=0, stdout="List of devices attached\n192.0.2.1:5555 device product:RMX3851\n", stderr=""),
            SimpleNamespace(returncode=0, stdout="topResumedActivity=ActivityRecord{a u0 org.chromium.webapk.a39848fce9cad1fb0_v2/org.chromium.chrome.browser.webapps.SameTaskWebApkActivity t31}\n", stderr=""),
            SimpleNamespace(returncode=0, stdout="isKeyguardShowing=false\n", stderr=""),
            SimpleNamespace(returncode=0, stdout="mWakefulness=Awake\n", stderr=""),
        ]
        with patch("e2e_gt6_physical.subprocess.run", side_effect=successful) as run:
            self.assertEqual(require_installed_webapk_foreground(), "192.0.2.1:5555")
        self.assertEqual(run.call_count, 4)
        self.assertEqual(run.call_args_list[1].args[0][2:4], ["192.0.2.1:5555", "shell"])

    def test_native_foreground_guard_rejects_a_locked_or_dozing_phone(self):
        outputs = [
            SimpleNamespace(returncode=0, stdout="List of devices attached\n192.0.2.1:5555 device\n", stderr=""),
            SimpleNamespace(returncode=0, stdout="topResumedActivity=org.chromium.chrome.browser.webapps.SameTaskWebApkActivity\n", stderr=""),
            SimpleNamespace(returncode=0, stdout="isKeyguardShowing=true\n", stderr=""),
            SimpleNamespace(returncode=0, stdout="mWakefulness=Dozing\n", stderr=""),
        ]
        with patch("e2e_gt6_physical.subprocess.run", side_effect=outputs):
            with self.assertRaisesRegex(RuntimeError, "dormido o bloqueado"):
                require_installed_webapk_foreground()

    def test_native_foreground_guard_stops_when_another_app_is_visible(self):
        outputs = [
            SimpleNamespace(returncode=0, stdout="List of devices attached\n192.0.2.1:5555 device\n", stderr=""),
            SimpleNamespace(returncode=0, stdout="topResumedActivity=ActivityRecord{a u0 com.facebook.katana/.MainActivity t31}\n", stderr=""),
        ]
        with patch("e2e_gt6_physical.subprocess.run", side_effect=outputs):
            with self.assertRaisesRegex(RuntimeError, "no está confirmada"):
                require_installed_webapk_foreground()

    def test_visible_mascot_audit_uses_installed_page_and_restores_home_without_set_actions(self):
        source = (ROOT / "scripts" / "e2e_gt6_physical.py").read_text(encoding="utf-8")
        motion_audit = source.split("def verify_visible_installed_mascot_motion", 1)[1].split("def verify_visible_installed_home", 1)[0]
        self.assertIn("page.url != home_url", motion_audit)
        self.assertIn("page.goto(routine_url", motion_audit)
        self.assertIn("page.goto(home_url", motion_audit)
        self.assertNotIn("context.new_page()", motion_audit)
        self.assertNotIn("get_by_role('button'", motion_audit)
        self.assertNotIn("dataset.motion = motion", motion_audit)
        self.assertIn("#gt6PhysicalGifProbe", motion_audit)
        self.assertIn('state["activity"] == "complete"', motion_audit)
        self.assertIn("verify_visible_installed_mascot_motion(installed_page", source)
        self.assertIn("connect_over_cdp(cdp_websocket_url, no_defaults=True)", source)

    def test_cdp_http_discovery_resolves_a_same_origin_websocket_endpoint(self):
        from io import BytesIO

        response = BytesIO(b'{"webSocketDebuggerUrl":"ws://127.0.0.1:9222/devtools/browser"}')
        with patch("e2e_gt6_physical.urlopen", return_value=response) as open_url:
            resolved = resolve_cdp_websocket_url("http://127.0.0.1:9222/")
        self.assertEqual(resolved, "ws://127.0.0.1:9222/devtools/browser")
        open_url.assert_called_once_with("http://127.0.0.1:9222/json/version", timeout=5)

    def test_cdp_direct_websocket_endpoint_is_used_without_http_discovery(self):
        with patch("e2e_gt6_physical.urlopen") as open_url:
            resolved = resolve_cdp_websocket_url("ws://127.0.0.1:9222/devtools/browser")
        self.assertEqual(resolved, "ws://127.0.0.1:9222/devtools/browser")
        open_url.assert_not_called()

    def test_cdp_discovery_rejects_a_websocket_endpoint_on_an_unexpected_host(self):
        from io import BytesIO

        response = BytesIO(b'{"webSocketDebuggerUrl":"ws://example.invalid/devtools/browser"}')
        with patch("e2e_gt6_physical.urlopen", return_value=response):
            with self.assertRaisesRegex(RuntimeError, "inesperada"):
                resolve_cdp_websocket_url("http://127.0.0.1:9222")

    def test_physical_viewport_defaults_to_live_measurements(self):
        self.assertEqual(resolve_device_metrics([425, 831, 2.975]), (425, 831, 2.975))

    def test_physical_viewport_allows_explicit_diagnostic_overrides(self):
        self.assertEqual(
            resolve_device_metrics([425, 831, 2.975], width=390, device_scale_factor=3),
            (390, 831, 3.0),
        )

    def make_result(self):
        return {
            "routine": "Día 1",
            "exercises": 6,
            "images": {"broken": 0},
            "primarySetButtonsTested": 6,
            "exerciseSkipButtonsTested": 6,
            "exerciseCompletionRestTested": True,
            "mascotAnimation": "mascotCelebration",
            "batteryGifPauseResume": {"warmup": {
                "pausedOffscreen": True,
                "posterShown": True,
                "resumedOnscreen": True,
            }},
            "backgroundTimer": {"paused": True, "resumed": True},
        }

    def test_report_derives_motion_claims_from_observed_results(self):
        result = self.make_result()

        report = summarize_day(result)

        self.assertTrue(report["batteryGifPauseResume"])
        self.assertTrue(report["backgroundTimerPauseResume"])

    def test_report_does_not_claim_unobserved_motion_behavior(self):
        result = self.make_result()
        result["batteryGifPauseResume"]["warmup"]["resumedOnscreen"] = False
        result["backgroundTimer"]["paused"] = False

        report = summarize_day(result)

        self.assertFalse(report["batteryGifPauseResume"])
        self.assertFalse(report["backgroundTimerPauseResume"])

    def test_user_state_snapshot_is_stable_and_does_not_return_personal_values(self):
        class ReadOnlyFakePage:
            def evaluate(self, _script):
                return {
                    "localStorageState": [["profile", "synthetic-profile-value"]],
                    "sessionStorageState": [],
                    "indexedDbState": {"sessions": [{"sessionId": "synthetic-session"}]},
                }

        first = snapshot_installed_user_data(ReadOnlyFakePage())
        second = snapshot_installed_user_data(ReadOnlyFakePage())

        self.assertEqual(first, second)
        self.assertEqual(first["indexedDbRecords"], {"sessions": 1})
        self.assertEqual(set(first["fingerprints"]), {"localStorage", "sessionStorage", "indexedDB"})
        self.assertEqual(set(first["fingerprints"]["localStorage"]), {"profile"})
        self.assertNotIn("synthetic-profile-value", repr(first))
        self.assertNotIn("synthetic-session", repr(first))


if __name__ == "__main__":
    unittest.main()
