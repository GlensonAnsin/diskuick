import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fps


class FpsTests(unittest.TestCase):
    def test_slow_frames_give_low_fps(self):
        self.assertAlmostEqual(fps.fps_from_frames([(1.0, 47.6)] * 30, 1.0), 21.0, places=1)

    def test_frame_column_names(self):
        self.assertEqual(fps.frame_column(["Application", "ProcessID", "FrameTime"]), 2)
        self.assertEqual(fps.frame_column(["Application", "msBetweenPresents"]), 1)
        self.assertIsNone(fps.frame_column(["Application", "ProcessID"]))

    def test_format(self):
        self.assertEqual(fps.format_fps(143.6), "FPS  144")
        self.assertEqual(fps.format_fps(None), "FPS  …")

    def test_monitor_goes_quiet_when_frames_stop(self):
        m = fps.FpsMonitor(exe_path="x")
        m.frames.extend([(100.0, 50.0)] * 20)   # 20 frames of 50 ms = 1 s -> 20 FPS, however they arrived
        self.assertAlmostEqual(m.fps(now=101.0), 20.0)
        self.assertIsNone(m.fps(now=120.0))

    def test_fps_uses_frame_times_not_arrival(self):
        burst = [(100.0, 16.67)] * 60            # all 60 lines delivered at the same instant
        self.assertAlmostEqual(fps.fps_from_frames(burst, 100.0), 60.0, places=1)
        self.assertIsNone(fps.fps_from_frames([], 100.0))

    def test_unavailable_without_presentmon(self):
        m = fps.FpsMonitor(exe_path="")
        m.exe_path = None
        self.assertFalse(m.available)
        m.track("game.exe")
        self.assertIsNone(m.target)


if __name__ == "__main__":
    unittest.main()
