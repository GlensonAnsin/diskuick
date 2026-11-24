"""Tests for the 1.3 features: smart intensity, network check, reports, marks, alerts, game mode."""
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DISKUICK_PROBE_DIR", tempfile.mkdtemp(prefix="diskuick-test-"))

import alerts
import config
import controller
import gamemode
import lagcheck
import netcheck
import stats
from adaptive import Adaptive


class AdaptiveTests(unittest.TestCase):
    def test_starts_light_and_stays_when_calm(self):
        a = Adaptive(now=0)
        self.assertEqual(a.update(1), "random")
        self.assertEqual(a.update(300), "random")

    def test_steps_up_after_repeated_stalls_then_to_heavy_max(self):
        a = Adaptive(now=0)
        for t in (10, 20, 30):
            a.note_stall(t)
        self.assertEqual(a.update(31), "seq")
        for t in (40, 41, 42):
            a.note_stall(t)
        self.assertEqual(a.update(43), "heavy")
        for t in (50, 51, 52, 53):
            a.note_stall(t)
        self.assertEqual(a.update(54), "heavy")  # never above Heavy

    def test_two_stalls_are_not_enough(self):
        a = Adaptive(now=0)
        a.note_stall(10)
        a.note_stall(20)
        self.assertEqual(a.update(21), "random")

    def test_old_stalls_expire(self):
        a = Adaptive(now=0)
        for t in (1, 2):
            a.note_stall(t)
        a.note_stall(100)  # first two are > 60 s old by now
        self.assertEqual(a.update(101), "random")

    def test_steps_down_when_calm_and_backs_off_if_it_flips_back(self):
        a = Adaptive(now=0, calm=600)
        for t in (1, 2, 3):
            a.note_stall(t)
        self.assertEqual(a.update(4), "seq")
        self.assertEqual(a.update(300), "seq")          # not calm long enough
        self.assertEqual(a.update(700), "random")       # 600 s without a stall
        for t in (710, 711, 712):                       # stalls right after stepping down
            a.note_stall(t)
        self.assertEqual(a.update(713), "seq")
        self.assertEqual(a.calm, 1200)                  # back-off doubled


class NetcheckTests(unittest.TestCase):
    def test_parse_target(self):
        self.assertEqual(netcheck.parse_target("1.1.1.1"), ("1.1.1.1", 443))
        self.assertEqual(netcheck.parse_target(" game.example.com:27015 "), ("game.example.com", 27015))
        for bad in ("", "  ", "bad host", "a:b", "x:0", "x:70000", "-bad.com", "a" * 300):
            self.assertIsNone(netcheck.parse_target(bad), bad)

    def test_rtt_local_listener_and_closed_port(self):
        import socket
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        try:
            ms = netcheck.rtt_ms("127.0.0.1", port, timeout=2)
            self.assertIsNotNone(ms)
            self.assertLess(ms, 500)
        finally:
            srv.close()
        self.assertIsNone(netcheck.rtt_ms("127.0.0.1", port, timeout=0.5))


class LagAnalyzeTests(unittest.TestCase):
    def lv(self, **kw):
        base = dict(disk_ms=[2, 3], cpu=[10, 10], ram=[40, 40])
        base.update(kw)
        return lagcheck.analyze(base["disk_ms"], base["cpu"], base["ram"], base.get("gpu"),
                                base.get("net"), base.get("hogs"))

    def test_packet_loss_is_bad(self):
        net = [20.0] * 8 + [None, None]
        self.assertIn("bad", [l for l, _ in self.lv(net=net)])

    def test_ping_spikes_warn(self):
        net = [20.0, 150.0, 200.0, 180.0, 20.0]
        self.assertIn("warn", [l for l, _ in self.lv(net=net)])

    def test_good_network_ok(self):
        out = self.lv(net=[20.0] * 10)
        self.assertTrue(any(l == "ok" and "Network was fine" in m for l, m in out))

    def test_unreachable_target(self):
        out = self.lv(net=[None] * 5)
        self.assertTrue(any(l == "bad" and "never answered" in m for l, m in out))

    def test_hogs_reported(self):
        out = self.lv(hogs=[("onedrive.exe", 42.0)])
        self.assertTrue(any("onedrive.exe" in m for _, m in out))

    def test_final_message_lists_what_was_not_measured(self):
        msgs = [m for l, m in self.lv() if l == "warn"]
        self.assertTrue(any("GPU and network weren't measured" in m for m in msgs))

    def test_mark_verdicts(self):
        v = lambda **k: lagcheck.mark_verdict({"drives": {}, "cpu": 10, "ram": 40, **k})["level"]
        self.assertEqual(v(drives={"C": 120.0}), "bad")
        self.assertEqual(v(gpu=99), "bad")
        self.assertEqual(v(cpu=95), "bad")
        self.assertEqual(v(ram=95), "warn")
        self.assertEqual(v(net_checked=True, net_ms=None), "bad")
        self.assertEqual(v(hogs=[("x.exe", 50.0)]), "warn")
        self.assertEqual(v(drives={"C": 3.0}), "ok")


class ReportTests(unittest.TestCase):
    def sess(self, **kw):
        s = {"drive": "C", "start": 1000.0, "games": {"Game"}, "worst": 10.0, "avg_sum": 5.0, "n": 10,
             "stalls": 0, "cpu_sum": 200.0, "cpu_n": 10, "cpu_peak": 40.0, "ram_peak": 50.0,
             "gpu_sum": 0.0, "gpu_n": 0, "gpu_peak": 0.0, "seen": 0}
        s.update(kw)
        return s

    def test_report_fields_and_ok_verdict(self):
        r = controller.make_report(self.sess(), 1600.0)
        self.assertEqual(r["seconds"], 600)
        self.assertEqual(r["games"], ["Game"])
        self.assertEqual(r["cpu_avg"], 20.0)
        self.assertIsNone(r["gpu_avg"])
        self.assertEqual(r["verdict"]["level"], "ok")

    def test_verdicts(self):
        self.assertEqual(controller.make_report(self.sess(stalls=5, worst=300.0), 2000.0)["verdict"]["level"], "bad")
        self.assertEqual(controller.make_report(self.sess(stalls=1), 2000.0)["verdict"]["level"], "warn")
        self.assertEqual(controller.make_report(self.sess(gpu_sum=980.0, gpu_n=10, gpu_peak=100.0), 2000.0)
                         ["verdict"]["level"], "bad")
        self.assertEqual(controller.make_report(self.sess(cpu_sum=950.0), 2000.0)["verdict"]["level"], "bad")

    def test_stats_persist_reports_and_marks(self):
        with tempfile.TemporaryDirectory() as d:
            sp, lp = os.path.join(d, "s.json"), os.path.join(d, "l.log")
            st = stats.Stats(sp, lp)
            for i in range(35):
                st.add_report({"end": i, "verdict": {"level": "ok", "text": "x"}})
            st.add_mark({"ts": 5.0})
            st2 = stats.Stats(sp, lp)
            self.assertEqual(len(st2.reports), stats.MAX_REPORTS)
            self.assertEqual(st2.recent_reports(1)[0]["end"], 34)  # newest first
            self.assertEqual(st2.recent_marks(1)[0]["ts"], 5.0)


class ControllerAdaptiveTests(unittest.TestCase):
    def make(self, **cfg):
        with tempfile.TemporaryDirectory() as d:
            st = stats.Stats(os.path.join(d, "s.json"), os.path.join(d, "l.log"))
        c = config.migrate({"mode": "always", "always_drives": ["C"], **cfg})
        return controller.Controller(c, st), c

    def test_adaptive_overrides_default_pattern(self):
        ctrl, c = self.make(adaptive=True, default_pattern="heavy")
        out = ctrl._apply_adaptive(c, {"C": "heavy"}, [])
        self.assertEqual(out, {"C": "random"})

    def test_game_specific_pattern_wins(self):
        ctrl, c = self.make(adaptive=True)
        g = {"name": "G", "exe": "g.exe", "drive": "C", "pattern": "seq", "enabled": True}
        self.assertEqual(ctrl._apply_adaptive(c, {"C": "seq"}, [g]), {"C": "seq"})

    def test_off_leaves_want_unchanged(self):
        ctrl, c = self.make(adaptive=False)
        self.assertEqual(ctrl._apply_adaptive(c, {"C": "heavy"}, []), {"C": "heavy"})

    def test_stalls_escalate_through_on_stall(self):
        ctrl, c = self.make(adaptive=True)
        ctrl._apply_adaptive(c, {"C": "random"}, [])
        now = time.time()
        for i in range(3):
            ctrl._on_stall("C", now + i, 90.0)
        self.assertEqual(ctrl._apply_adaptive(c, {"C": "random"}, []), {"C": "seq"})
        self.assertEqual(ctrl.current_level("C"), "seq")


class AlertsTests(unittest.TestCase):
    def test_low_space_once_per_day_and_rearms(self):
        a = alerts.Alerts()
        first = a.free_space("C", 50, 1000, now=0)
        self.assertEqual(len(first), 1)
        self.assertEqual(a.free_space("C", 50, 1000, now=100), [])                  # same day: quiet
        self.assertEqual(len(a.free_space("C", 50, 1000, now=alerts.REPEAT_S + 1)), 1)
        a.free_space("C", 500, 1000, now=10)                                        # recovered
        self.assertEqual(len(a.free_space("C", 50, 1000, now=20)), 1)               # fills up again

    def test_plenty_of_space_is_quiet(self):
        self.assertEqual(alerts.Alerts().free_space("C", 500, 1000), [])
        self.assertEqual(alerts.Alerts().free_space("C", 0, 0), [])

    def test_health_change_alerts_once(self):
        a = alerts.Alerts()
        self.assertEqual(a.health("C", "Healthy", now=0), [])
        self.assertEqual(len(a.health("C", "Warning", now=1)), 1)
        self.assertEqual(a.health("C", "Warning", now=2), [])
        self.assertEqual(a.health("C", None, now=3), [])


class GameModeTests(unittest.TestCase):
    def test_protected_programs_refused(self):
        for exe in ("explorer.exe", "EXPLORER.EXE", "diskuick.exe", "svchost.exe", "", "  "):
            self.assertFalse(gamemode.allowed(exe), exe)
        self.assertTrue(gamemode.allowed("chrome.exe"))

    def test_close_programs_ignores_blocked_and_missing(self):
        self.assertEqual(gamemode.close_programs(["explorer.exe"]), [])
        self.assertEqual(gamemode.close_programs(["definitely-not-running-xyz.exe"], wait=0.2), [])

    # Closing a real window is deliberately not unit-tested: it would act on the developer's own
    # programs. Try it by hand with a throw-away program (see README, "Game mode").


class ConfigNewKeysTests(unittest.TestCase):
    def test_defaults_and_normalising(self):
        c = config.migrate({})
        self.assertFalse(c["adaptive"])
        self.assertTrue(c["alerts"] and c["hotkeys"])
        self.assertEqual(c["net_host"], "")
        c = config.migrate({"game_close": ["Chrome.EXE", "chrome.exe", " ", 5], "net_host": None})
        self.assertEqual(c["game_close"], ["chrome.exe"])
        self.assertEqual(c["net_host"], "")


if __name__ == "__main__":
    unittest.main(verbosity=1)
