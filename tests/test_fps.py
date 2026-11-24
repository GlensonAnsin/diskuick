import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fps


class FpsTests(unittest.TestCase):
    def test_counts_frames_in_last_second(self):
        arrivals = [98.0, 99.2, 99.3, 99.5, 99.9, 100.0]
        self.assertEqual(fps.fps_from_arrivals(arrivals, 100.0), 5.0)

    def test_no_recent_frames(self):
        self.assertIsNone(fps.fps_from_arrivals([90.0], 100.0))
        self.assertIsNone(fps.fps_from_arrivals([], 100.0))

    def test_frame_column_names(self):
        self.assertEqual(fps.frame_column(["Application", "ProcessID", "FrameTime"]), 2)
        self.assertEqual(fps.frame_column(["Application", "msBetweenPresents"]), 1)
        self.assertIsNone(fps.frame_column(["Application", "ProcessID"]))

    def test_format(self):
        self.assertEqual(fps.format_fps(143.6), "FPS  144")
        self.assertEqual(fps.format_fps(None), "FPS  …")

    def test_monitor_goes_quiet_when_frames_stop(self):
        m = fps.FpsMonitor(exe_path="x")
        m.frames.extend([100.0, 100.5, 101.0])
        self.assertEqual(m.fps(now=101.2), 2.0)  # 100.5 and 101.0 fall inside the last second
        self.assertIsNone(m.fps(now=110.0))

    def test_unavailable_without_presentmon(self):
        m = fps.FpsMonitor(exe_path="")
        m.exe_path = None
        self.assertFalse(m.available)
        m.track("game.exe")
        self.assertIsNone(m.target)


if __name__ == "__main__":
    unittest.main()
