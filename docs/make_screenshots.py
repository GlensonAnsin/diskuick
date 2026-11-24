"""Regenerates the README screenshots from the real app (with sample data).

    python docs/make_screenshots.py

Uses a throw-away config folder (your real settings are untouched) and Win32 PrintWindow, so it
also works while the screen is locked. Sample games/stats are made up; latency and drive health
are measured live from this PC. Review the output before committing (drive names, hardware, ...).
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import sys
import tempfile
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "docs", "screenshots")
tmp = tempfile.mkdtemp()
os.environ["APPDATA"] = tmp  # throw-away config
sys.path.insert(0, ROOT)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass
os.makedirs(os.path.join(tmp, "diskuick"))
SYS = os.environ.get("SystemDrive", "C:")[0]
json.dump({"mode": "always", "always_drives": [SYS], "size_mb": 8, "theme": "dark",
           "games": [{"name": "Cyberpunk 2077", "exe": "cyberpunk2077.exe", "drive": SYS, "pattern": None, "enabled": True},
                     {"name": "Elden Ring", "exe": "eldenring.exe", "drive": SYS, "pattern": "seq", "enabled": True},
                     {"name": "Counter-Strike 2", "exe": "cs2.exe", "drive": SYS, "pattern": None, "enabled": True},
                     {"name": "Old Favourite", "exe": "oldgame.exe", "drive": SYS, "pattern": "heavy", "enabled": False}]},
          open(os.path.join(tmp, "diskuick", "config.json"), "w"))

import diskuick as dk  # noqa: E402
import diskuick_tray as t  # noqa: E402
from PIL import Image  # noqa: E402

u32, g32 = ctypes.windll.user32, ctypes.windll.gdi32


def printwindow(w) -> Image.Image:
    hwnd = u32.GetParent(w.winfo_id()) or w.winfo_id()
    r = wt.RECT()
    u32.GetWindowRect(hwnd, ctypes.byref(r))
    W, H = r.right - r.left, r.bottom - r.top
    hdc = u32.GetDC(0)
    mdc = g32.CreateCompatibleDC(hdc)
    bmp = g32.CreateCompatibleBitmap(hdc, W, H)
    g32.SelectObject(mdc, bmp)
    u32.PrintWindow(hwnd, mdc, 2)

    class BI(ctypes.Structure):
        _fields_ = [("a", wt.DWORD), ("w", wt.LONG), ("h", wt.LONG), ("p", wt.WORD), ("b", wt.WORD),
                    ("c", wt.DWORD), ("s", wt.DWORD), ("x", wt.LONG), ("y", wt.LONG), ("u", wt.DWORD),
                    ("i", wt.DWORD)]

    bi = BI(ctypes.sizeof(BI), W, -H, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(W * H * 4)
    g32.GetDIBits(mdc, bmp, 0, H, buf, ctypes.byref(bi), 0)
    g32.DeleteObject(bmp)
    g32.DeleteDC(mdc)
    u32.ReleaseDC(0, hdc)
    return Image.frombuffer("RGBA", (W, H), buf, "raw", "BGRA", 0, 1).convert("RGB")


app = t.App()
app.ctrl.start()
app._pump()
app._overlay_tick()


def pump(sec):
    end = time.time() + sec
    while time.time() < end:
        app.root.update()
        time.sleep(0.05)


def tab(i):
    app.win.tabs.set(app.win.tab_names[i])
    app.win._on_tab()
    pump(1.5)


def scroll_to(frac):
    def find(wd):
        for c in wd.winfo_children():
            if hasattr(c, "_parent_canvas"):
                return c
            r = find(c)
            if r:
                return r
    sc = find(app.win.tabs.tab(app.win.tab_names[app.win.tab_names.index(app.win.tabs.get())]))
    sc._parent_canvas.yview_moveto(frac)
    pump(0.8)


def save(img, name, box=None):
    os.makedirs(OUT, exist_ok=True)
    img = img.crop(box) if box else img
    img.save(os.path.join(OUT, name), optimize=True)
    print("saved", name, img.size)


app.stats.data.update(active_seconds=2 * 3600 + 37 * 60, sessions=14, stalls=0)
app.open_window("dashboard")
pump(14)  # let live latency accumulate past the warm-up period
save(printwindow(app.win), "dashboard.png", (0, 30, 656, 760))

tab(1)
save(printwindow(app.win), "games.png", (0, 30, 656, 600))

# Tools: real drive health + a quick real auto-tune (shortened) so the results card is filled
tab(2)
pump(4)
orig = dk.run_bench
dk.run_bench = lambda path, reads=14, gap=2.0, **kw: orig(path, reads=4, gap=0.5, **kw)
app.win._run_tune()
end = time.time() + 60
while getattr(app.win, "_tuning", False) and time.time() < end:
    pump(0.3)
pump(1)
scroll_to(0.045)
save(printwindow(app.win), "tools.png", (0, 30, 656, 899))

app.apply({"mode": "games"})  # hides the per-drive list (no volume names in the screenshot)
app.open_window("settings", force_new=True)  # rebuild so the window reflects the new mode
pump(2)
save(printwindow(app.win), "settings.png", (0, 30, 656, 899))

app.apply({"theme": "light"})
pump(2)
tab(0)
pump(6)
save(printwindow(app.win), "dashboard-light.png", (0, 30, 656, 760))

app.apply({"theme": "dark", "mode": "always", "overlay": True, "overlay_corner": "top-right"})
pump(5)
if app.overlay.win is not None:
    img = printwindow(app.overlay.win)
    save(img.resize((img.width * 3, img.height * 3), Image.LANCZOS), "overlay.png")

app.ctrl.shutdown()
app.ctrl.join(6)
p = dk.probe_path(SYS)
if os.path.exists(p):
    os.remove(p)
    os.rmdir(os.path.dirname(p))
app.overlay.hide()
app.root.destroy()
