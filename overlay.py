"""Optional on-screen latency readout (off by default).

A tiny always-on-top, click-through, never-focused window in a screen corner. It is a *separate*
window: it does not hook, inject into, or read from the game, so it does not interact with
anti-cheat. Like any overlay window it shows over windowed/borderless games but not over
exclusive-fullscreen ones.
"""
import ctypes
import time
import tkinter as tk

CORNERS = ("top-left", "top-right", "bottom-left", "bottom-right")
MARGIN = 18
BG, OK, BAD = "#101216", "#2ECC71", "#E5534B"

GWL_EXSTYLE = -20
WS_EX_TRANSPARENT, WS_EX_LAYERED, WS_EX_TOOLWINDOW, WS_EX_NOACTIVATE = 0x20, 0x80000, 0x80, 0x08000000


def latency_items(ctrl, now: float | None = None) -> list[tuple[str, float | None, bool]]:
    """[(drive, worst latency ms over the last 3 s | None, is_stall)] for every active drive."""
    now = time.time() if now is None else now
    out = []
    for d in ctrl.active_drives():
        recent = [h for h in ctrl.history(d) if h[0] >= now - 3]
        ms = max((h[1] for h in recent), default=None)
        out.append((d, ms, ms is not None and ms > ctrl.stall_threshold(d)))
    return out


def format_items(items) -> str:
    lines = []
    for d, ms, stall in items:
        val = "…" if ms is None else (f"{ms:.0f} ms" if ms >= 10 else f"{ms:.1f} ms")
        lines.append(f"{d}:  {val}" + ("  ⚠" if stall else ""))
    return "\n".join(lines)


def place(corner: str, screen_w: int, screen_h: int, w: int, h: int, margin: int = MARGIN):
    x = margin if corner.endswith("left") else screen_w - w - margin
    y = margin if corner.startswith("top") else screen_h - h - margin - 40  # clear the taskbar
    return max(0, x), max(0, y)


class Overlay:
    def __init__(self, root: tk.Misc):
        self.root = root
        self.win: tk.Toplevel | None = None
        self.label: tk.Label | None = None
        self._preview_until = 0.0

    # -- lifecycle
    def _create(self):
        w = tk.Toplevel(self.root)
        w.overrideredirect(True)
        w.attributes("-topmost", True)
        w.attributes("-alpha", 0.85)
        w.configure(bg=BG)
        self.label = tk.Label(w, text="", bg=BG, fg=OK, font=("Consolas", 12, "bold"),
                              justify="left", padx=12, pady=8)
        self.label.pack()
        w.update_idletasks()
        self._click_through(w)
        self.win = w

    @staticmethod
    def _click_through(w: tk.Toplevel):
        u32 = ctypes.windll.user32
        hwnd = u32.GetParent(w.winfo_id()) or w.winfo_id()
        style = u32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        u32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT
                           | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE)

    def hide(self):
        if self.win is not None:
            try:
                self.win.destroy()
            except tk.TclError:
                pass
            self.win = self.label = None

    def preview(self, seconds: float = 4.0):
        self._preview_until = time.time() + seconds

    # -- called ~once a second on the UI thread
    def update(self, enabled: bool, corner: str, ctrl):
        previewing = time.time() < self._preview_until
        items = latency_items(ctrl) if enabled else []
        if previewing and not items:
            items = [("E", 0.6, False)]  # sample reading so the user can see position/size
        if not items:
            self.hide()
            return
        if self.win is None or not self.win.winfo_exists():
            self._create()
        self.label.configure(text=format_items(items),
                             fg=BAD if any(s for _, _, s in items) else OK)
        self.win.update_idletasks()
        w, h = self.win.winfo_reqwidth(), self.win.winfo_reqheight()
        x, y = place(corner if corner in CORNERS else "top-right",
                     self.win.winfo_screenwidth(), self.win.winfo_screenheight(), w, h)
        self.win.geometry(f"+{x}+{y}")
        self.win.attributes("-topmost", True)  # stay above borderless games that re-assert topmost
