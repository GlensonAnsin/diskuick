import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Tests must never touch the real probe file of an installed/running Diskuick.
os.environ["DISKUICK_PROBE_DIR"] = tempfile.mkdtemp(prefix="diskuick-test-")

import config
import controller
import diskuick as dk
import games
import health
import lagcheck
import stats
import sysutil
import updater


def cfg(**kw):
    c = config.migrate({})
    c.update(kw)
    return c


def game(exe, drive="E", pattern=None, enabled=True, name=None):
    return {"name": name or exe, "exe": exe, "drive": drive, "pattern": pattern, "enabled": enabled}


class ConfigTests(unittest.TestCase):
    def test_defaults(self):
        c = config.migrate({})
        self.assertEqual(c["mode"], "games")
        self.assertEqual(c["games"], [])

    def test_migrate_v1(self):
        c = config.migrate({"drive": "e", "pattern": "seq", "processes": ["Game.exe", "b.exe"],
                            "mode": "always", "interval": 0.5})
        self.assertEqual(c["always_drives"], ["E"])
        self.assertEqual(c["default_pattern"], "seq")
        self.assertEqual([g["exe"] for g in c["games"]], ["game.exe", "b.exe"])
        self.assertTrue(all(g["drive"] == "E" for g in c["games"]))
        self.assertEqual(c["mode"], "always")

    def test_garbage_is_repaired(self):
        c = config.migrate({"default_pattern": "bogus", "mode": "x",
                            "games": [{"exe": ""}, {"exe": "A.EXE", "drive": "d:", "pattern": "nope"}]})
        self.assertEqual(c["default_pattern"], "random")
        self.assertEqual(c["mode"], "games")
        self.assertEqual(c["games"], [game("a.exe", "D", None, True, "A.EXE")])

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "c.json")
            c = cfg(games=[game("x.exe")])
            config.save(c, p)
            loaded, existed = config.load(p)
            self.assertTrue(existed)
            self.assertEqual(loaded["games"][0]["exe"], "x.exe")
            self.assertFalse(config.load(os.path.join(d, "nope.json"))[1])


class DecideTests(unittest.TestCase):
    def test_disabled(self):
        self.assertEqual(controller.decide(cfg(enabled=False), set(), None, False)[0], {})

    def test_battery_pause_and_override(self):
        c = cfg(mode="always", always_drives=["D"])
        self.assertEqual(controller.decide(c, set(), None, True)[0], {})
        self.assertEqual(controller.decide(dict(c, pause_on_battery=False), set(), None, True)[0],
                         {"D": "random"})

    def test_always_multi_drive(self):
        c = cfg(mode="always", always_drives=["D", "E"], default_pattern="seq")
        self.assertEqual(controller.decide(c, set(), None, False)[0], {"D": "seq", "E": "seq"})

    def test_games_waiting_and_running(self):
        c = cfg(games=[game("a.exe", "E"), game("b.exe", "F", "heavy")])
        want, active, reason = controller.decide(c, {"explorer.exe"}, None, False)
        self.assertEqual(want, {})
        self.assertTrue(reason.startswith("Waiting"))
        want, active, _ = controller.decide(c, {"a.exe", "b.exe"}, None, False)
        self.assertEqual(want, {"E": "random", "F": "heavy"})
        self.assertEqual(len(active), 2)

    def test_same_drive_uses_strongest(self):
        c = cfg(games=[game("a.exe", "E", "seq"), game("b.exe", "E", "heavy"), game("c.exe", "E")])
        want, _, _ = controller.decide(c, {"a.exe", "b.exe", "c.exe"}, None, False)
        self.assertEqual(want, {"E": "heavy"})

    def test_disabled_game_ignored(self):
        c = cfg(games=[game("a.exe", enabled=False)])
        self.assertEqual(controller.decide(c, {"a.exe"}, None, False)[0], {})

    def test_focus_rule(self):
        c = cfg(games=[game("a.exe")], only_when_focused=True)
        self.assertEqual(controller.decide(c, {"a.exe"}, "chrome.exe", False)[0], {})
        self.assertEqual(controller.decide(c, {"a.exe"}, "a.exe", False)[0], {"E": "random"})

    def test_empty_states(self):
        self.assertIn("Add games", controller.decide(cfg(), set(), None, False)[2])
        self.assertIn("Choose a drive", controller.decide(cfg(mode="always"), set(), None, False)[2])


class RecommendTests(unittest.TestCase):
    def row(self, name, p95):
        return (name, (p95, p95, p95, p95))

    def test_light_helps(self):
        rows = [self.row("none", 120), self.row("random", 5), self.row("seq", 4), self.row("heavy", 3)]
        self.assertEqual(dk.recommend(rows)["pattern"], "random")

    def test_needs_heavy(self):
        rows = [self.row("none", 120), self.row("random", 110), self.row("seq", 100), self.row("heavy", 8)]
        self.assertEqual(dk.recommend(rows)["pattern"], "heavy")

    def test_no_stalls(self):
        rows = [self.row("none", 2), self.row("random", 1.5), self.row("seq", 1.2), self.row("heavy", 1)]
        r = dk.recommend(rows)
        self.assertIsNone(r["pattern"])
        self.assertEqual(r["message_key"], "no_stalls")

    def test_no_help(self):
        rows = [self.row("none", 100), self.row("random", 95), self.row("seq", 90), self.row("heavy", 99)]
        self.assertEqual(dk.recommend(rows)["message_key"], "no_help")


class GamesTests(unittest.TestCase):
    def test_guess_exe_picks_largest_real_exe(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "bin"))
            os.makedirs(os.path.join(d, "_CommonRedist"))
            for rel, size in (("bin/game.exe", 5000), ("launcher.exe", 100), ("unins000.exe", 9999),
                              ("_CommonRedist/vc.exe", 99999), ("UnityCrashHandler64.exe", 8000)):
                with open(os.path.join(d, rel), "wb") as f:
                    f.write(b"x" * size)
            self.assertEqual(games.guess_exe(d), "game.exe")

    def test_steam_library_scan(self):
        with tempfile.TemporaryDirectory() as lib:
            os.makedirs(os.path.join(lib, "steamapps", "common", "Cool Game"))
            with open(os.path.join(lib, "steamapps", "common", "Cool Game", "CoolGame.exe"), "wb") as f:
                f.write(b"x" * 1000)
            os.makedirs(os.path.join(lib, "steamapps", "common", "Steamworks Shared"))
            with open(os.path.join(lib, "steamapps", "appmanifest_1.acf"), "w") as f:
                f.write('"AppState"\n{\n"name"\t\t"Cool Game"\n"installdir"\t\t"Cool Game"\n}')
            with open(os.path.join(lib, "steamapps", "appmanifest_2.acf"), "w") as f:
                f.write('"AppState"\n{\n"name"\t\t"Steamworks Common Redistributables"\n'
                        '"installdir"\t\t"Steamworks Shared"\n}')
            found = games.scan_steam_library(lib)
            self.assertEqual([(g["name"], g["exe"], g["source"]) for g in found],
                             [("Cool Game", "coolgame.exe", "Steam")])

    def test_epic_manifest(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as inst:
            with open(os.path.join(d, "a.item"), "w") as f:
                json.dump({"DisplayName": "Epic Thing", "InstallLocation": inst,
                           "LaunchExecutable": "Bin/Win64/Epic.EXE"}, f)
            with open(os.path.join(d, "bad.item"), "w") as f:
                f.write("{not json")
            found = games.scan_epic(d)
            self.assertEqual([(g["name"], g["exe"]) for g in found], [("Epic Thing", "epic.exe")])

    def test_scan_all_runs_on_this_machine(self):
        res = games.scan_all()
        self.assertIsInstance(res, list)
        for g in res:
            self.assertTrue(g["exe"].endswith(".exe"))
            self.assertEqual(len(g["drive"]), 1)


class HealthTests(unittest.TestCase):
    def lv(self, info):
        return {lv for lv, _ in health.health_tips(info)}

    def test_low_space(self):
        self.assertIn("bad", self.lv({"free": 5, "total": 100, "model": "x"}))
        self.assertIn("warn", self.lv({"free": 12, "total": 100, "model": "x"}))
        self.assertNotIn("bad", self.lv({"free": 60, "total": 100, "model": "x", "temp": 40, "wear": 5}))

    def test_hot_and_worn(self):
        self.assertIn("bad", self.lv({"free": 60, "total": 100, "temp": 75}))
        self.assertIn("bad", self.lv({"free": 60, "total": 100, "wear": 90}))

    def test_unhealthy(self):
        self.assertIn("bad", self.lv({"free": 60, "total": 100, "health": "Warning"}))

    def test_real_drive_does_not_crash(self):
        info = health.get_health("C")
        self.assertIsNotNone(info["total"])
        self.assertIsInstance(health.health_tips(info), list)


class LagcheckTests(unittest.TestCase):
    CSV = ('"(PDH-CSV 4.0)","\\\\PC\\PhysicalDisk(0 C:)\\Avg. Disk sec/Read",'
           '"\\\\PC\\PhysicalDisk(1 D: E:)\\Avg. Disk sec/Read","\\\\PC\\PhysicalDisk(_Total)\\Avg. Disk sec/Read"\n'
           '"11/24/2026 10:00:00.1","0.001","0.120","0.05"\n'
           '"11/24/2026 10:00:01.1","0.002","0.000","0.01"\n')

    def test_parse_picks_right_disk(self):
        self.assertEqual(lagcheck.parse_typeperf(self.CSV, "C"), [1.0, 2.0])
        self.assertEqual(lagcheck.parse_typeperf(self.CSV, "E"), [120.0, 0.0])
        self.assertIsNone(lagcheck.parse_typeperf(self.CSV, "Z"))
        self.assertIsNone(lagcheck.parse_typeperf("", "C"))

    def levels(self, disk, cpu, ram):
        return [lv for lv, _ in lagcheck.analyze(disk, cpu, ram)]

    def test_disk_stalls(self):
        self.assertIn("bad", self.levels([5, 200, 90, 3], [30] * 4, [50] * 4))

    def test_cpu_bound(self):
        lv = self.levels([2, 3, 2], [98, 97, 99], [50] * 3)
        self.assertIn("bad", lv)

    def test_ram_pressure(self):
        self.assertIn("bad", self.levels([2, 3], [20, 20], [95, 96]))

    def test_all_fine_mentions_other_causes(self):
        msgs = [m for _, m in lagcheck.analyze([2, 3, 2], [20] * 3, [40] * 3)]
        self.assertTrue(any("GPU" in m for m in msgs))

    def test_no_counters(self):
        self.assertIn("warn", self.levels(None, [10], [10]))

    GPU_CSV = ('"t","\\\\PC\\GPU Engine(pid_1_luid_0x0_0xA_phys_0_eng_0_engtype_3D)\\Utilization Percentage",'
               '"\\\\PC\\GPU Engine(pid_2_luid_0x0_0xA_phys_0_eng_0_engtype_3D)\\Utilization Percentage",'
               '"\\\\PC\\GPU Engine(pid_1_luid_0x0_0xA_phys_0_eng_3_engtype_VideoDecode)\\Utilization Percentage",'
               '"\\\\PC\\GPU Engine(pid_1_luid_0x0_0xB_phys_0_eng_0_engtype_3D)\\Utilization Percentage"\n'
               '"x","60","30","99","5"\n"x","80","40","99","5"\n')

    def test_parse_gpu_sums_processes_ignores_video_picks_busiest_gpu(self):
        # GPU A: 60+30=90, 80+40=120 -> capped at 100. VideoDecode ignored. GPU B only 5.
        self.assertEqual(lagcheck.parse_gpu(self.GPU_CSV), [90.0, 100.0])
        self.assertIsNone(lagcheck.parse_gpu(""))
        self.assertIsNone(lagcheck.parse_gpu('"t","\\\\PC\\Processor(_Total)\\% Processor Time"\n"x","1"\n'))

    def test_gpu_bound(self):
        lv = [l for l, _ in lagcheck.analyze([2, 3], [20, 20], [40, 40], [99, 98])]
        self.assertIn("bad", lv)

    def test_gpu_fine_points_at_network(self):
        msgs = [m for _, m in lagcheck.analyze([2, 3], [20, 20], [40, 40], [30, 40])]
        self.assertTrue(any("GPU was fine" in m for m in msgs))
        self.assertTrue(any("network" in m for m in msgs))


class StatsTests(unittest.TestCase):
    def test_persist_and_log(self):
        with tempfile.TemporaryDirectory() as d:
            sp, lp = os.path.join(d, "s.json"), os.path.join(d, "l.log")
            s = stats.Stats(sp, lp)
            s.add_active(90)
            s.add_session()
            s.add_stall("E", time.time(), 123.4)
            s.save()
            s2 = stats.Stats(sp, lp)
            self.assertEqual(s2.data["sessions"], 1)
            self.assertEqual(s2.data["stalls"], 1)
            self.assertEqual(s2.recent_stalls(1)[0][1], "E")

    def test_format(self):
        self.assertEqual(stats.fmt_duration(30), "30s")
        self.assertEqual(stats.fmt_duration(3 * 60), "3m")
        self.assertEqual(stats.fmt_duration(3600 + 5 * 60), "1h 05m")


class UpdaterTests(unittest.TestCase):
    def test_versions(self):
        self.assertTrue(updater.is_newer("v1.2.0", "1.1.9"))
        self.assertFalse(updater.is_newer("1.1.0", "1.1.0"))
        self.assertFalse(updater.is_newer("v0.9", "1.0.0"))

    def test_disabled_without_repo(self):
        self.assertIsNone(updater.check("", "1.0.0"))


class SysutilTests(unittest.TestCase):
    def test_running_exes_contains_self(self):
        self.assertIn(os.path.basename(sys.executable).lower(), sysutil.running_exes())

    def test_misc_do_not_crash(self):
        self.assertIsInstance(sysutil.on_battery(), bool)
        sysutil.foreground_exe()
        self.assertIsInstance(sysutil.drive_choices(), dict)


class WarmupTests(unittest.TestCase):
    def test_slow_reads_ignored_during_warmup_then_counted(self):
        drive = os.environ.get("SystemDrive", "C:")[0]
        path = dk.ensure_probe(drive, 8)
        stalls = []
        old = dk.WARMUP_S
        dk.WARMUP_S = 1.0
        ka = dk.KeepAlive(path, "random", 0.05, drive, lambda d, ts, ms: stalls.append(ms))
        ka.fn = lambda r: 999.0  # every read "stalls"
        try:
            ka.start()
            time.sleep(0.7)
            self.assertEqual(stalls, [])          # still warming up
            self.assertEqual(list(ka.history), [])
            time.sleep(1.2)
            self.assertGreater(len(stalls), 0)    # counted once warm-up is over
        finally:
            dk.WARMUP_S = old
            ka.stop()
            p = dk.probe_path(drive)
            if os.path.exists(p):
                os.remove(p)
                os.rmdir(os.path.dirname(p))


class IntegrationTests(unittest.TestCase):
    """Real keep-alive on the system drive with a tiny probe file."""

    def test_controller_always_mode_and_suspend(self):
        drive = os.environ.get("SystemDrive", "C:")[0]
        st = stats.Stats(os.path.join(tempfile.mkdtemp(), "s.json"), os.path.join(tempfile.mkdtemp(), "l"))
        c = cfg(mode="always", always_drives=[drive], size_mb=8)
        ctrl = controller.Controller(c, st)
        ctrl.start()
        try:
            for _ in range(40):
                if ctrl.active_drives():
                    break
                time.sleep(0.25)
            self.assertEqual(ctrl.active_drives(), [drive])
            time.sleep(dk.WARMUP_S + 2.5)
            self.assertGreater(len(ctrl.history(drive)), 0)
            ctrl.suspend(drive)
            self.assertEqual(ctrl.active_drives(), [])
            time.sleep(2.5)
            self.assertEqual(ctrl.active_drives(), [])  # stays stopped
            ctrl.resume(drive)
            for _ in range(40):
                if ctrl.active_drives():
                    break
                time.sleep(0.25)
            self.assertEqual(ctrl.active_drives(), [drive])
            ctrl.update_cfg(dict(c, enabled=False))
            for _ in range(40):
                if not ctrl.active_drives():
                    break
                time.sleep(0.25)
            self.assertEqual(ctrl.active_drives(), [])
        finally:
            ctrl.shutdown()
            ctrl.join(8)
            p = dk.probe_path(drive)
            if os.path.exists(p):
                os.remove(p)
                os.rmdir(os.path.dirname(p))

    def test_bad_drive_reports_error(self):
        st = stats.Stats(os.path.join(tempfile.mkdtemp(), "s.json"), os.path.join(tempfile.mkdtemp(), "l"))
        saved = os.environ.pop("DISKUICK_PROBE_DIR")  # needs a really missing drive, not a temp dir
        ctrl = controller.Controller(cfg(mode="always", always_drives=["Q"], size_mb=8), st)
        ctrl.start()
        try:
            time.sleep(3)
            self.assertEqual(ctrl.state, "error")
        finally:
            ctrl.shutdown()
            ctrl.join(8)
            os.environ["DISKUICK_PROBE_DIR"] = saved


if __name__ == "__main__":
    unittest.main(verbosity=1)
