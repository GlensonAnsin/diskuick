"""Theme + reusable widgets for the Diskuick UI (CustomTkinter)."""
import time
import tkinter as tk

import customtkinter as ctk

import games as games_mod
import sysutil
from i18n import T

# colours are (light, dark) pairs - CustomTkinter picks the right one for the current theme
BG = ("#F3F5F8", "#0F1115")
CARD = ("#FFFFFF", "#171A20")
FIELD = ("#EAEEF3", "#20242C")
BORDER = ("#D9DFE7", "#262B34")
TEXT = ("#141922", "#E8EAED")
MUTED = ("#5E6A7A", "#8B93A1")
ACCENT = ("#22B866", "#2ECC71")
ACCENT_HOVER = ("#1C9E58", "#27AE60")
ON_ACCENT = "#06210F"
DANGER = ("#D93F36", "#E5534B")
WARN = ("#B7791F", "#F1C40F")
FONT = "Segoe UI"
STATE_COLORS = {"active": "#2ECC71", "waiting": "#F1C40F", "off": "#7F8C8D", "error": "#E5534B"}
LEVEL_COLORS = {"ok": ACCENT, "warn": WARN, "bad": DANGER}
LEVEL_ICONS = {"ok": "✔", "warn": "!", "bad": "✖"}


def is_dark() -> bool:
    return ctk.get_appearance_mode() == "Dark"


def pick(c) -> str:
    return c[1] if is_dark() else c[0]


# ------------------------------------------------------------- builders -----
def card(parent, title: str | None = None, subtitle: str | None = None, wrap: int = 520):
    f = ctk.CTkFrame(parent, fg_color=CARD, corner_radius=14, border_width=1, border_color=BORDER)
    f.pack(fill="x", pady=(0, 10))
    if title:
        ctk.CTkLabel(f, text=title, font=(FONT, 14, "bold"), text_color=TEXT, anchor="w").pack(
            fill="x", padx=16, pady=(14, 0))
    if subtitle:
        ctk.CTkLabel(f, text=subtitle, font=(FONT, 12), text_color=MUTED, anchor="w",
                     justify="left", wraplength=wrap).pack(fill="x", padx=16, pady=(1, 0))
    return f


def btn_primary(parent, text, command, **kw):
    return ctk.CTkButton(parent, text=text, command=command, height=kw.pop("height", 38),
                         corner_radius=10, fg_color=ACCENT, hover_color=ACCENT_HOVER,
                         text_color=ON_ACCENT, font=(FONT, 13, "bold"), **kw)


def btn_secondary(parent, text, command, **kw):
    return ctk.CTkButton(parent, text=text, command=command, height=kw.pop("height", 36),
                         corner_radius=10, fg_color=FIELD, hover_color=BORDER, text_color=TEXT,
                         font=(FONT, 13), **kw)


def btn_ghost(parent, text, command, **kw):
    return ctk.CTkButton(parent, text=text, command=command, height=kw.pop("height", 34),
                         corner_radius=10, fg_color="transparent", border_width=1,
                         border_color=BORDER, hover_color=FIELD, text_color=ACCENT,
                         font=(FONT, 13), **kw)


def option_menu(parent, variable, values, command=None, **kw):
    return ctk.CTkOptionMenu(parent, variable=variable, values=values, command=command,
                             height=kw.pop("height", 34), corner_radius=10, fg_color=FIELD,
                             button_color=BORDER, button_hover_color=("#C9D1DB", "#313744"),
                             dropdown_fg_color=CARD, dropdown_hover_color=FIELD, text_color=TEXT,
                             font=(FONT, 13), dropdown_font=(FONT, 13), anchor="w", **kw)


def segmented(parent, values, variable, command=None, **kw):
    return ctk.CTkSegmentedButton(parent, values=values, variable=variable, command=command,
                                  height=kw.pop("height", 34), corner_radius=10, fg_color=FIELD,
                                  selected_color=ACCENT, selected_hover_color=ACCENT_HOVER,
                                  unselected_color=FIELD, unselected_hover_color=BORDER,
                                  text_color=TEXT, font=(FONT, 13), **kw)


def switch_row(parent, title, subtitle, variable, command):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", padx=16, pady=8)
    t = ctk.CTkFrame(f, fg_color="transparent")
    t.pack(side="left", fill="x", expand=True)
    ctk.CTkLabel(t, text=title, font=(FONT, 13, "bold"), text_color=TEXT, anchor="w").pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(t, text=subtitle, font=(FONT, 12), text_color=MUTED, anchor="w", justify="left",
                     wraplength=400).pack(anchor="w")
    ctk.CTkSwitch(f, text="", variable=variable, command=command, progress_color=ACCENT,
                  fg_color=BORDER, width=46).pack(side="right")
    return f


def level_line(parent, level: str, text: str, wrap: int = 500):
    r = ctk.CTkFrame(parent, fg_color="transparent")
    r.pack(fill="x", padx=16, pady=2)
    ctk.CTkLabel(r, text=LEVEL_ICONS[level], width=20, font=(FONT, 13, "bold"),
                 text_color=LEVEL_COLORS[level]).pack(side="left", anchor="n", pady=1)
    ctk.CTkLabel(r, text=text, font=(FONT, 12), text_color=TEXT, anchor="w", justify="left",
                 wraplength=wrap).pack(side="left", fill="x", expand=True, padx=(4, 0))


# ----------------------------------------------------------- latency graph --
class LatencyGraph(tk.Canvas):
    """Per-second worst read latency over the last couple of minutes, with a stall line."""

    def __init__(self, master, height: int = 150):
        super().__init__(master, height=height, highlightthickness=0, bd=0)

    def draw(self, points, threshold: float, window: int = 120, placeholder: str = ""):
        self.delete("all")
        self.configure(bg=pick(FIELD))
        w, h = max(self.winfo_width(), 100), max(self.winfo_height(), 60)
        l, r, t, b = 52, 8, 10, 18
        muted, accent, danger = pick(MUTED), pick(ACCENT), pick(DANGER)
        now = time.time()
        pts = [(ts, mx) for ts, mx, _avg in points if ts >= now - window]
        if len(pts) < 2:
            self.create_text(w / 2, h / 2, text=placeholder or T("Waiting for data..."), fill=muted,
                             font=(FONT, 11))
            return
        ymax = max(threshold * 1.25, max(p[1] for p in pts) * 1.1)

        def X(ts):
            return l + (1 - (now - ts) / window) * (w - l - r)

        def Y(ms):
            return t + (1 - min(ms, ymax) / ymax) * (h - t - b)

        for v in (0, ymax):
            self.create_line(l, Y(v), w - r, Y(v), fill=pick(BORDER))
            self.create_text(l - 6, Y(v), text=f"{v:.0f} ms", anchor="e", fill=muted, font=(FONT, 9))
        ty = Y(threshold)
        self.create_line(l, ty, w - r, ty, fill=danger, dash=(4, 3))
        self.create_text(w - r - 2, ty - 7, text=T("stall"), anchor="e", fill=danger, font=(FONT, 9))
        poly = [(l, Y(0))] + [(X(ts), Y(mx)) for ts, mx in pts] + [(X(pts[-1][0]), Y(0))]
        self.create_polygon(*[c for p in poly for c in p], fill=pick(("#CFEFDD", "#16382A")), outline="")
        self.create_line(*[c for ts, mx in pts for c in (X(ts), Y(mx))], fill=accent, width=2,
                         smooth=False)
        for ts, mx in pts:
            if mx > threshold:
                self.create_oval(X(ts) - 3, Y(mx) - 3, X(ts) + 3, Y(mx) + 3, fill=danger, outline="")
        self.create_text(l, h - 6, text=f"-{window}s", anchor="w", fill=muted, font=(FONT, 9))
        self.create_text(w - r, h - 6, text=T("now"), anchor="e", fill=muted, font=(FONT, 9))


# ----------------------------------------------------------------- dialogs --
class _Dialog(ctk.CTkToplevel):
    def __init__(self, master, title, size):
        super().__init__(master, fg_color=BG)
        self.title(title)
        self.geometry(size)
        self.resizable(False, False)
        self.transient(master)
        self.after(150, self._focus)

    def _focus(self):
        try:
            self.lift()
            self.focus_force()
        except Exception:
            pass


class ProcessPicker(_Dialog):
    """Pick from programs that currently have a window open."""

    def __init__(self, master, on_pick):
        super().__init__(master, T("Pick a running program"), "380x460")
        self.on_pick, self.exes = on_pick, sysutil.visible_window_exes()
        ctk.CTkLabel(self, text=T("Open your game first, then pick it here."), font=(FONT, 12),
                     text_color=MUTED).pack(padx=16, pady=(14, 6), anchor="w")
        self.q = ctk.CTkEntry(self, placeholder_text=T("Search..."), height=36, fg_color=FIELD,
                              border_color=BORDER, corner_radius=10, font=(FONT, 13))
        self.q.pack(fill="x", padx=16, pady=(0, 8))
        self.q.bind("<KeyRelease>", lambda _: self.render())
        self.list = ctk.CTkScrollableFrame(self, fg_color=CARD, corner_radius=12)
        self.list.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.render()

    def render(self):
        for w in self.list.winfo_children():
            w.destroy()
        q = self.q.get().strip().lower()
        shown = [e for e in self.exes if q in e]
        if not shown:
            ctk.CTkLabel(self.list, text=T("Nothing found"), text_color=MUTED).pack(pady=20)
        for e in shown:
            ctk.CTkButton(self.list, text=e, anchor="w", height=34, fg_color="transparent",
                          hover_color=FIELD, text_color=TEXT, font=(FONT, 13),
                          command=lambda e=e: self._pick(e)).pack(fill="x", pady=1)

    def _pick(self, exe):
        self.on_pick(exe)
        self.destroy()


class DetectDialog(_Dialog):
    """Shows games found on this PC with checkboxes; returns the chosen ones via on_add."""

    def __init__(self, master, found: list[dict], existing_exes: set, on_add):
        super().__init__(master, T("Detected games"), "520x560")
        self.on_add = on_add
        self.items = [g for g in found if g["exe"] not in existing_exes]
        self.vars: list[tuple[ctk.BooleanVar, dict]] = []
        if not self.items:
            msg = (T("No new games found.") + "\n\n" +
                   T("Looked in Steam, Epic Games and GOG. You can still add a game with "
                     "“Add running program” or by typing its exe name."))
            ctk.CTkLabel(self, text=msg, font=(FONT, 13), text_color=MUTED, justify="left",
                         wraplength=440).pack(padx=24, pady=40)
            btn_secondary(self, T("Close"), self.destroy, width=120).pack()
            return
        ctk.CTkLabel(self, text=T("Choose the games to keep your drive awake for."), font=(FONT, 12),
                     text_color=MUTED).pack(padx=16, pady=(14, 2), anchor="w")
        ctk.CTkLabel(self, text=T("The program name is a best guess - check it if a game doesn't trigger."),
                     font=(FONT, 11), text_color=MUTED).pack(padx=16, pady=(0, 8), anchor="w")
        lst = ctk.CTkScrollableFrame(self, fg_color=CARD, corner_radius=12)
        lst.pack(fill="both", expand=True, padx=16)
        for g in self.items:
            v = ctk.BooleanVar(value=False)
            self.vars.append((v, g))
            ctk.CTkCheckBox(lst, text=f"{g['name']}   ·   {g['exe']}   ·   {g['drive']}:  [{g['source']}]",
                            variable=v, font=(FONT, 12), text_color=TEXT, fg_color=ACCENT,
                            hover_color=ACCENT_HOVER, checkmark_color=ON_ACCENT,
                            border_color=BORDER).pack(anchor="w", padx=10, pady=5)
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=16, pady=12)
        btn_secondary(bar, T("Select all"), self._all, width=100).pack(side="left")
        btn_primary(bar, T("Add selected"), self._add, width=140).pack(side="right")

    def _all(self):
        for v, _ in self.vars:
            v.set(True)

    def _add(self):
        chosen = [g for v, g in self.vars if v.get()]
        if chosen:
            self.on_add(chosen)
        self.destroy()
