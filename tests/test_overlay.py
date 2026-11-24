import ctypes
import os
import sys
import time
import tkinter as tk
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import overlay


class FakeCtrl:
    def __init__(self, hist=None, threshold=60.0):
        self.hist, self.threshold = hist or {}, threshold

    def active_drives(self):
        return sorted(self.hist)

    def history(self, d):
        return self.hist[d]

    def stall_threshold(self, d):
        return self.threshold


class PureTests(unittest.TestCase):
    def test_items_use_worst_of_last_3s(self):
        now = 1000.0
        c = FakeCtrl({"E": [(990, 500.0, 1), (998, 0.7, 0.5), (999, 2.4, 1.0)]})
        self.assertEqual(overlay.latency_items(c, now), [("E", 2.4, False)])

    def test_stall_flag_and_no_data(self):
        now = 1000.0
        c = FakeCtrl({"D": [(999, 180.0, 10)], "E": [(900, 1.0, 1)]})
        self.assertEqual(overlay.latency_items(c, now), [("D", 180.0, True), ("E", None, False)])

    def test_format(self):
        self.assertEqual(overlay.format_items([("E", 0.64, False), ("D", 180.0, True), ("F", None, False)]),
                         "E:  0.6 ms\nD:  180 ms  ⚠\nF:  …")

    def test_placement_in_every_corner(self):
        sw, sh, w, h = 1920, 1080, 120, 60
        for corner in overlay.CORNERS:
            x, y = overlay.place(corner, sw, sh, w, h)
            self.assertTrue(0 <= x <= sw - w and 0 <= y <= sh - h, corner)
        self.assertLess(overlay.place("top-left", sw, sh, w, h)[0], overlay.place("top-right", sw, sh, w, h)[0])
        self.assertLess(overlay.place("top-left", sw, sh, w, h)[1], overlay.place("bottom-left", sw, sh, w, h)[1])


class WindowTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.ov = overlay.Overlay(self.root)

    def tearDown(self):
        self.ov.hide()
        self.root.destroy()

    def style(self):
        u32 = ctypes.windll.user32
        hwnd = u32.GetParent(self.ov.win.winfo_id()) or self.ov.win.winfo_id()
        return u32.GetWindowLongW(hwnd, overlay.GWL_EXSTYLE)

    def test_hidden_when_disabled_or_inactive(self):
        self.ov.update(False, "top-right", FakeCtrl({"E": [(time.time(), 1.0, 1.0)]}))
        self.assertIsNone(self.ov.win)
        self.ov.update(True, "top-right", FakeCtrl({}))
        self.assertIsNone(self.ov.win)

    def test_shows_click_through_topmost_window(self):
        self.ov.update(True, "bottom-left", FakeCtrl({"E": [(time.time(), 1.5, 1.0)]}))
        self.root.update()
        self.assertIsNotNone(self.ov.win)
        st = self.style()
        for flag in (overlay.WS_EX_TRANSPARENT, overlay.WS_EX_NOACTIVATE, overlay.WS_EX_TOOLWINDOW,
                     overlay.WS_EX_LAYERED):
            self.assertTrue(st & flag, hex(flag))
        self.assertTrue(self.ov.win.attributes("-topmost"))
        self.assertIn("E:", self.ov.label.cget("text"))
        x, y = self.ov.win.winfo_x(), self.ov.win.winfo_y()
        self.assertTrue(0 <= x < self.ov.win.winfo_screenwidth() and 0 <= y < self.ov.win.winfo_screenheight())

    def test_turns_red_on_stall_and_hides_after(self):
        self.ov.update(True, "top-right", FakeCtrl({"E": [(time.time(), 150.0, 150.0)]}))
        self.assertEqual(self.ov.label.cget("fg"), overlay.BAD)
        self.ov.update(True, "top-right", FakeCtrl({"E": [(time.time(), 1.0, 1.0)]}))
        self.assertEqual(self.ov.label.cget("fg"), overlay.OK)
        self.ov.update(True, "top-right", FakeCtrl({}))
        self.assertIsNone(self.ov.win)

    def test_preview_shows_even_when_idle_then_expires(self):
        self.ov.preview(0.4)
        self.ov.update(False, "top-left", FakeCtrl({}))
        self.assertIsNotNone(self.ov.win)
        time.sleep(0.5)
        self.ov.update(False, "top-left", FakeCtrl({}))
        self.assertIsNone(self.ov.win)


if __name__ == "__main__":
    unittest.main()
