"""Main Diskuick window: Dashboard / Games / Tools / Disk / Settings. Changes apply instantly."""
import os
import queue
import threading
import time
import webbrowser

import customtkinter as ctk
from PIL import ImageTk

import config
import diskuick as dk
from disk_ui import DiskTab
import gamemode
import games as games_mod
import health as health_mod
import icons
import lagcheck as lag_mod
import netcheck
import stats as stats_mod
import sysutil
import updater
from i18n import LANGS, T
from logo import render_logo
from version import UPDATE_REPO, VERSION
from widgets import (ACCENT, ACCENT_HOVER, BG, BORDER, CARD, DANGER, FIELD, FONT, LEVEL_COLORS, MUTED,
                     STATE_COLORS, TEXT, DetectDialog, LatencyGraph, ProcessPicker, btn_ghost,
                     btn_primary, btn_secondary, card, level_line, option_menu, segmented,
                     switch_row)

TAB_KEYS = ["dashboard", "games", "tools", "disk", "settings"]
PATTERN_LABELS = [("random", "Light"), ("seq", "Balanced"), ("heavy", "Heavy")]
PATTERN_DESC = {
    "random": "Tiny random reads, about 10 per second. Least overhead - try this first.",
    "seq": "Light sequential reads, about 20 per second. For drives that need a bit more.",
    "heavy": "Non-stop reads. Strongest effect, but the drive is always busy.",
}
STATE_NAMES = {"active": "Active", "waiting": "Waiting", "off": "Off", "error": "Error"}


def pat_label(p):  # config value -> translated label
    return T(dict(PATTERN_LABELS).get(p, "Default"))


def pat_value(label):  # translated label -> config value
    for v, l in PATTERN_LABELS:
        if T(l) == label:
            return v
    return None


class MainWindow(ctk.CTkToplevel):
    W, H = 820, 860
    MIN_W, MIN_H = 560, 520

    def __init__(self, master, app, tab: str | None = None):
        super().__init__(master, fg_color=BG)
        self.app, self.cfg = app, app.cfg
        self.title("Diskuick")
        self.resizable(True, True)         # drag the edges, or use the maximize button for fullscreen
        self.minsize(self.MIN_W, self.MIN_H)
        self.q: queue.Queue = queue.Queue()
        self._icon = ImageTk.PhotoImage(render_logo(64))
        self.after(250, lambda: self._safe(lambda: self.iconphoto(False, self._icon)))
        self._tune_cancel = threading.Event()
        self._lag_cancel = threading.Event()
        self._health_loaded = False
        self._stall_sig = None
        self._tune_rec = None

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        scale = self._get_window_scaling()
        hh = min(self.H, int(sh / scale) - 90)
        self.geometry(f"{self.W}x{hh}+{max(0, (sw - int(self.W * scale)) // 2)}+{max(10, (sh - int(hh * scale)) // 2 - 20)}")

        self._build_header()
        self.banner = None

        self.tab_names = [T("Dashboard"), T("Games"), T("Tools"), T("Disk"), T("Settings")]
        self.tabs = ctk.CTkTabview(
            self, fg_color="transparent", corner_radius=14, command=self._on_tab,
            segmented_button_fg_color=FIELD, segmented_button_selected_color=ACCENT,
            segmented_button_selected_hover_color=ACCENT_HOVER, segmented_button_unselected_color=FIELD,
            segmented_button_unselected_hover_color=BORDER, text_color=TEXT)
        self.tabs._segmented_button.configure(font=(FONT, 13), height=34)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        if app.update_info:
            self.show_update(app.update_info)
        frames = [self.tabs.add(n) for n in self.tab_names]
        self._build_dashboard(self._scroll(frames[0]))
        self._build_games(self._scroll(frames[1]))
        self._build_tools(self._scroll(frames[2]))
        self.disk = DiskTab(self, self._scroll(frames[3]))
        self._build_settings(self._scroll(frames[4]))
        if tab:
            self.tabs.set(self.tab_names[TAB_KEYS.index(tab)])
        self._pump()
        self._tick()
        self._on_tab()  # load health right away if the Tools tab was pre-selected
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._wrap_job = None
        self.bind("<Configure>", self._on_resize)

    # ------------------------------------------------------------ plumbing --
    def _on_resize(self, e):
        if e.widget is not self:
            return
        if self._wrap_job:
            self.after_cancel(self._wrap_job)
        self._wrap_job = self.after(120, lambda: self._safe(self._rewrap))

    def _rewrap(self):
        """Let long description text use the width of a resized window instead of staying at a fixed wrap."""
        self._wrap_job = None
        width = max(self.winfo_width() / self._get_window_scaling() - 120, 300)
        stack = [self]
        while stack:
            w = stack.pop()
            stack.extend(w.winfo_children())
            if isinstance(w, ctk.CTkLabel) and getattr(w, "_wrap_base", None) is None:
                try:
                    base = int(w.cget("wraplength") or 0)
                except Exception:
                    base = 0
                w._wrap_base = base if base >= 500 else 0     # only long paragraphs; banners/dialogs keep theirs
            if isinstance(w, ctk.CTkLabel) and w._wrap_base:
                if abs(int(w.cget("wraplength")) - width) > 4:
                    w.configure(wraplength=int(width))

    @staticmethod
    def _safe(fn):
        try:
            fn()
        except Exception:
            pass

    @staticmethod
    def _scroll(parent):
        s = ctk.CTkScrollableFrame(parent, fg_color="transparent", corner_radius=0)
        s.pack(fill="both", expand=True)
        return s

    def post(self, fn):
        """Run fn on the UI thread (safe to call from worker threads)."""
        self.q.put(fn)

    def _pump(self):
        if not self.winfo_exists():
            return
        try:
            while True:
                self.q.get_nowait()()
        except queue.Empty:
            pass
        except Exception:
            pass
        self.after(100, self._pump)

    def _close(self):
        self._tune_cancel.set()
        self._lag_cancel.set()
        self.disk.cancel()
        self.destroy()

    def current_key(self) -> str:
        try:
            return TAB_KEYS[self.tab_names.index(self.tabs.get())]
        except (ValueError, AttributeError):
            return "dashboard"

    def _on_tab(self):
        if self.tabs.get() == self.tab_names[2] and not self._health_loaded:
            self._health_loaded = True
            self._refresh_health()

    def _letters(self) -> list[str]:
        return list(sysutil.drive_choices().values()) or ["C"]

    def _default_drive(self) -> str:
        if self.cfg["games"]:
            return self.cfg["games"][-1]["drive"]
        letters = self._letters()
        non_sys = [d for d in letters if d != os.environ.get("SystemDrive", "C:")[0]]
        return non_sys[-1] if non_sys else letters[0]

    # ----------------------------------------------------------- header -----
    def _build_header(self):
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.pack(fill="x", padx=22, pady=(16, 8))
        self._logo = ctk.CTkImage(render_logo(128), size=(46, 46))
        ctk.CTkLabel(h, image=self._logo, text="").pack(side="left", padx=(0, 12))
        t = ctk.CTkFrame(h, fg_color="transparent")
        t.pack(side="left")
        ctk.CTkLabel(t, text="Diskuick", font=(FONT, 24, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(t, text=T("Keeps your drive awake while you play"), font=(FONT, 12),
                     text_color=MUTED).pack(anchor="w")
        self.pill = ctk.CTkFrame(h, fg_color=CARD, corner_radius=20, border_width=1, border_color=BORDER)
        self.pill.pack(side="right", anchor="n", pady=6)
        self.dot = ctk.CTkLabel(self.pill, text="●", font=(FONT, 14), text_color=MUTED, width=18)
        self.dot.pack(side="left", padx=(12, 0), pady=5)
        self.pill_text = ctk.CTkLabel(self.pill, text="", font=(FONT, 12), text_color=TEXT)
        self.pill_text.pack(side="left", padx=(2, 12))

    def show_update(self, info: dict):
        """Green banner above the tabs: 'Update now' (installed copy) or 'Download' (release page)."""
        if self.banner is not None and self.banner.winfo_exists():
            self.banner.destroy()
        b = self.banner = ctk.CTkFrame(self, fg_color=ACCENT, corner_radius=10)
        b.pack(fill="x", padx=22, pady=(0, 8), before=self.tabs)
        self.upd_text = ctk.CTkLabel(b, text=f"{T('Update available')}: {info['tag']}",
                                     font=(FONT, 12, "bold"), text_color="#06210F", wraplength=400,
                                     justify="left", anchor="w")
        self.upd_text.pack(side="left", padx=12, pady=7)
        self._upd_info = info
        self.upd_btn = ctk.CTkButton(
            b, text=T("Update now") if updater.can_self_update(info) else T("Download"), width=100,
            height=26, corner_radius=8, fg_color="#06210F", hover_color="#0B3A1F", text_color="white",
            font=(FONT, 12), command=self._do_update)
        self.upd_btn.pack(side="right", padx=8)

    def _do_update(self):
        info = self._upd_info
        if not updater.can_self_update(info):
            webbrowser.open(info["url"])
            return
        self.upd_btn.configure(state="disabled", text=T("Downloading… {p}%").format(p=0))

        def progress(f):
            self.post(lambda: self.upd_btn.configure(text=T("Downloading… {p}%").format(p=int(f * 100))))

        def work():
            try:
                path = updater.download(info, progress=progress)
            except Exception as e:
                msg = f"{T('Update failed')}: {e}"
                self.post(lambda: (self.upd_text.configure(text=msg[:160]),
                                   self.upd_btn.configure(state="normal", text=T("Retry"))))
                return
            self.post(lambda: self.app.install_update(path))

        threading.Thread(target=work, daemon=True).start()

    def _check_now(self):
        self.upd_label.configure(text=T("Checking…"))
        self.check_btn.configure(state="disabled")

        def work():
            info = updater.check(UPDATE_REPO, VERSION)
            self.post(lambda: self._checked(info))

        threading.Thread(target=work, daemon=True).start()

    def _checked(self, info):
        self.check_btn.configure(state="normal")
        if info:
            self.app.update_info = info
            self.upd_label.configure(text=T("Update available: {v}").format(v=info["tag"]))
            self.show_update(info)
        else:
            self.upd_label.configure(text=T("You're up to date."))

    # ------------------------------------------------------- dashboard ------
    def _build_dashboard(self, body):
        c = card(body)
        row = ctk.CTkFrame(c, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=14)
        self.d_dot = ctk.CTkLabel(row, text="●", font=(FONT, 26), text_color=MUTED, width=30)
        self.d_dot.pack(side="left", anchor="n")
        mid = ctk.CTkFrame(row, fg_color="transparent")
        mid.pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.d_state = ctk.CTkLabel(mid, text="", font=(FONT, 20, "bold"), text_color=TEXT, anchor="w")
        self.d_state.pack(anchor="w")
        self.d_text = ctk.CTkLabel(mid, text="", font=(FONT, 12), text_color=MUTED, anchor="w",
                                   justify="left", wraplength=360)
        self.d_text.pack(anchor="w")
        self.en_var = ctk.BooleanVar(value=self.cfg["enabled"])
        sw = ctk.CTkFrame(row, fg_color="transparent")
        sw.pack(side="right")
        ctk.CTkSwitch(sw, text=T("Enabled"), variable=self.en_var, font=(FONT, 12), text_color=TEXT,
                      progress_color=ACCENT, fg_color=BORDER,
                      command=lambda: self.app.apply({"enabled": self.en_var.get()})).pack()

        tiles = ctk.CTkFrame(body, fg_color="transparent")
        tiles.pack(fill="x", pady=(0, 10))
        tiles.columnconfigure((0, 1, 2), weight=1, uniform="t")
        self.tile_vals = []
        for i, cap in enumerate((T("Kept awake"), T("Sessions"), T("Stalls logged"))):
            t = ctk.CTkFrame(tiles, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
            t.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 5, 0 if i == 2 else 5))
            v = ctk.CTkLabel(t, text="-", font=(FONT, 20, "bold"), text_color=TEXT)
            v.pack(pady=(10, 0))
            ctk.CTkLabel(t, text=cap, font=(FONT, 11), text_color=MUTED).pack(pady=(0, 10))
            self.tile_vals.append(v)

        g = card(body)
        top = ctk.CTkFrame(g, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(top, text=T("Live read latency"), font=(FONT, 14, "bold"), text_color=TEXT).pack(side="left")
        self.g_var = ctk.StringVar(value="")
        self.g_menu = option_menu(top, self.g_var, [""], width=80, height=28)
        self.graph = LatencyGraph(g, height=160)
        self.graph.pack(fill="x", padx=14, pady=(8, 4))
        ctk.CTkLabel(g, text=T("Each point is the slowest read in that second. Spikes above the red line "
                               "are stalls - moments the drive hesitated."),
                     font=(FONT, 11), text_color=MUTED, wraplength=520, justify="left", anchor="w").pack(
            fill="x", padx=16, pady=(0, 12))

        s = card(body, T("Recent stalls"))
        self.stall_box = ctk.CTkFrame(s, fg_color="transparent")
        self.stall_box.pack(fill="x", padx=16, pady=(6, 12))

        r = card(body, T("Last sessions"), T("Was it the drive? A summary of your last play sessions."))
        self.sess_box = ctk.CTkFrame(r, fg_color="transparent")
        self.sess_box.pack(fill="x", padx=16, pady=(6, 12))
        self._sess_sig = None

        m = card(body, T("Lag marks"),
                 T("Press Ctrl+Alt+L (or use the tray menu) the moment a game lags. Diskuick saves what "
                   "the PC was doing right then."))
        self.mark_box = ctk.CTkFrame(m, fg_color="transparent")
        self.mark_box.pack(fill="x", padx=16, pady=(6, 12))
        self._mark_sig = None

    def _refresh_dashboard(self):
        ctrl, st = self.app.ctrl, self.app.stats
        state, text = ctrl.state, ctrl.text
        col = STATE_COLORS.get(state, "#7F8C8D")
        self.dot.configure(text_color=col)
        self.pill_text.configure(text=T(STATE_NAMES.get(state, state)))
        self.d_dot.configure(text_color=col)
        self.d_state.configure(text=T(STATE_NAMES.get(state, state)))
        self.d_text.configure(text=T(text))
        self.en_var.set(self.cfg["enabled"])
        d = st.data
        self.tile_vals[0].configure(text=stats_mod.fmt_duration(d["active_seconds"]))
        self.tile_vals[1].configure(text=str(d["sessions"]))
        self.tile_vals[2].configure(text=str(d["stalls"]))

        drives = ctrl.active_drives()
        if drives:
            if self.g_var.get() not in drives:
                self.g_var.set(drives[0])
            self.g_menu.configure(values=drives)
            if len(drives) > 1:
                self.g_menu.pack(side="right")
            else:
                self.g_menu.pack_forget()
            sel = self.g_var.get()
            self.graph.draw(ctrl.history(sel), ctrl.stall_threshold(sel))
        else:
            self.g_menu.pack_forget()
            self.graph.draw([], dk.STALL_MS["random"],
                            placeholder=T("Start a game (or choose “Always on”) to see live latency."))

        recent = st.recent_stalls(5)
        sig = tuple(recent)
        if sig != self._stall_sig:
            self._stall_sig = sig
            for w in self.stall_box.winfo_children():
                w.destroy()
            if not recent:
                ctk.CTkLabel(self.stall_box, text=T("No stalls recorded yet."), font=(FONT, 12),
                             text_color=MUTED).pack(anchor="w")
            for ts, drv, ms in recent:
                ctk.CTkLabel(self.stall_box, text=f"{stats_mod.fmt_clock(ts)}    {drv}:    {ms:.0f} ms",
                             font=("Consolas", 12), text_color=TEXT, anchor="w").pack(anchor="w")

        self._refresh_reports()

    def _refresh_reports(self):
        st = self.app.stats
        reports, marks = st.recent_reports(3), st.recent_marks(3)
        rsig = tuple(r["end"] for r in reports)
        if rsig != self._sess_sig:
            self._sess_sig = rsig
            self._clear(self.sess_box)
            if not reports:
                ctk.CTkLabel(self.sess_box, text=T("No sessions recorded yet. A report appears when a game closes."),
                             font=(FONT, 12), text_color=MUTED, wraplength=500, justify="left",
                             anchor="w").pack(anchor="w")
            for r in reports:
                names = ", ".join(r["games"]) or f"{r['drive']}:"
                when = time.strftime("%d %b %H:%M", time.localtime(r["start"]))
                ctk.CTkLabel(self.sess_box, text=f"{when}   {names}   ·   {stats_mod.fmt_duration(r['seconds'])}",
                             font=(FONT, 13, "bold"), text_color=TEXT, anchor="w").pack(fill="x", pady=(6, 0))
                level_line(self.sess_box, r["verdict"]["level"], T(r["verdict"]["text"]))
                bits = [f"{T('Worst read')} {r['worst_ms']:.0f} ms", f"{r['stalls']} {T('stalls')}",
                        f"CPU {r['cpu_avg']:.0f}%"]
                if r.get("gpu_avg") is not None:
                    bits.append(f"GPU {r['gpu_avg']:.0f}%")
                bits.append(f"RAM {T('peak')} {r['ram_peak']:.0f}%")
                ctk.CTkLabel(self.sess_box, text="   ·   ".join(bits), font=(FONT, 11), text_color=MUTED,
                             anchor="w").pack(fill="x", padx=(0, 0))
        msig = tuple(m["ts"] for m in marks)
        if msig != self._mark_sig:
            self._mark_sig = msig
            self._clear(self.mark_box)
            if not marks:
                ctk.CTkLabel(self.mark_box, text=T("No lag marked yet."), font=(FONT, 12),
                             text_color=MUTED).pack(anchor="w")
            for m in marks:
                ctk.CTkLabel(self.mark_box, text=stats_mod.fmt_clock(m["ts"]), font=("Consolas", 12, "bold"),
                             text_color=TEXT, anchor="w").pack(fill="x", pady=(6, 0))
                level_line(self.mark_box, m["verdict"]["level"], T(m["verdict"]["text"]))
                bits = [f"{d}: {v:.0f} ms" for d, v in m.get("drives", {}).items() if v is not None]
                bits.append(f"CPU {m['cpu']:.0f}%")
                if m.get("gpu") is not None:
                    bits.append(f"GPU {m['gpu']:.0f}%")
                bits.append(f"RAM {m['ram']:.0f}%")
                if m.get("net_ms") is not None:
                    bits.append(f"{T('ping')} {m['net_ms']:.0f} ms")
                ctk.CTkLabel(self.mark_box, text="   ·   ".join(bits), font=(FONT, 11), text_color=MUTED,
                             anchor="w").pack(fill="x")

    def _tick(self):
        if not self.winfo_exists():
            return
        try:
            self._refresh_dashboard()
        except Exception:
            pass
        self.after(1000, self._tick)

    # ----------------------------------------------------------- games ------
    def _build_games(self, body):
        bar = ctk.CTkFrame(body, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 8))
        self.det_btn = btn_primary(bar, T("Detect installed games"), self._detect)
        self.det_btn.pack(side="left")
        btn_ghost(bar, T("Add running program…"), lambda: ProcessPicker(self, self._add_exe)).pack(
            side="left", padx=8)
        add = ctk.CTkFrame(body, fg_color="transparent")
        add.pack(fill="x", pady=(0, 10))
        self.game_entry = ctk.CTkEntry(add, height=36, fg_color=FIELD, border_color=BORDER,
                                       corner_radius=10, placeholder_text=T("or type a program name, e.g. game.exe"),
                                       font=(FONT, 13))
        self.game_entry.pack(side="left", fill="x", expand=True)
        self.game_entry.bind("<Return>", lambda _: self._add_typed())
        btn_secondary(add, T("Add"), self._add_typed, width=70, height=36).pack(side="left", padx=(6, 0))
        self.games_box = ctk.CTkFrame(body, fg_color="transparent")
        self.games_box.pack(fill="x")
        self._render_games()

    def _save_games(self):
        self.app.apply({"games": self.cfg["games"]})

    def _add_exe(self, exe: str, name: str | None = None, drive: str | None = None, path: str | None = None):
        exe = exe.strip().lower()
        if not exe:
            return
        if "." not in exe:
            exe += ".exe"
        if any(g["exe"] == exe for g in self.cfg["games"]):
            return
        game = {"name": name or exe, "exe": exe, "drive": drive, "path": path}
        if not drive:                    # work out the drive from where the game really is
            found = icons.locate({"exe": exe, "path": path})
            if found:
                game["drive"], game["exe_path"] = os.path.splitdrive(found)[0][:1].upper(), found
            else:                        # not running / not found yet: guess now, correct it when it's seen
                game["drive"], game["auto_drive"] = self._default_drive(), True
        self.cfg["games"].append(config.norm_game(game))
        self._save_games()
        self._render_games()

    def _add_typed(self):
        self._add_exe(self.game_entry.get())
        self.game_entry.delete(0, "end")

    def _detect(self):
        self.det_btn.configure(state="disabled", text=T("Scanning..."))

        def work():
            found = games_mod.scan_all()
            self.post(lambda: self._detected(found))

        threading.Thread(target=work, daemon=True).start()

    def _detected(self, found):
        self.det_btn.configure(state="normal", text=T("Detect installed games"))
        DetectDialog(self, found, {g["exe"] for g in self.cfg["games"]}, self._add_detected)

    def _add_detected(self, chosen):
        for g in chosen:
            self._add_exe(g["exe"], g["name"], g["drive"], g.get("path"))

    def _render_games(self):
        for w in self.games_box.winfo_children():
            w.destroy()
        if not self.cfg["games"]:
            ctk.CTkLabel(self.games_box, text=T("No games yet.\nClick “Detect installed games” to find them "
                                               "automatically."), font=(FONT, 13), text_color=MUTED,
                         justify="center").pack(pady=40)
            return
        letters = self._letters()
        # a game left on "no override" follows the global setting: Smart intensity if that's on
        follow = T("Smart") if self.cfg["adaptive"] else T("Default")
        labels = [follow] + [T(l) for _, l in PATTERN_LABELS]
        for g in self.cfg["games"]:
            r = ctk.CTkFrame(self.games_box, fg_color=CARD, corner_radius=12, border_width=1, border_color=BORDER)
            r.pack(fill="x", pady=(0, 8))
            top = ctk.CTkFrame(r, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(10, 0))
            ico = self._game_icon(g)
            if ico is not None:
                ctk.CTkLabel(top, text="", image=ico).pack(side="left", padx=(0, 10))
            else:
                ctk.CTkLabel(top, text="🎮", font=(FONT, 18), text_color=MUTED, width=28).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(top, text=g["name"], font=(FONT, 14, "bold"), text_color=TEXT,
                         anchor="w").pack(side="left")
            ctk.CTkButton(top, text="✎", width=28, height=26, corner_radius=8, fg_color="transparent",
                          hover_color=BORDER, text_color=MUTED, font=(FONT, 13),
                          command=lambda g=g: self._rename_game(g)).pack(side="left", padx=(4, 0))
            ctk.CTkButton(top, text="✕", width=28, height=26, corner_radius=8, fg_color="transparent",
                          hover_color=BORDER, text_color=MUTED, font=(FONT, 12),
                          command=lambda g=g: self._remove_game(g)).pack(side="right")
            sv = ctk.BooleanVar(value=g["enabled"])
            ctk.CTkSwitch(top, text="", variable=sv, progress_color=ACCENT, fg_color=BORDER, width=44,
                          command=lambda g=g, v=sv: self._set_game(g, enabled=v.get())).pack(side="right", padx=6)
            bot = ctk.CTkFrame(r, fg_color="transparent")
            bot.pack(fill="x", padx=14, pady=(2, 12))
            ctk.CTkLabel(bot, text=g["exe"], font=(FONT, 12), text_color=MUTED).pack(side="left")
            pv = ctk.StringVar(value=pat_label(g["pattern"]) if g["pattern"] else follow)
            option_menu(bot, pv, labels, width=110, height=30,
                        command=lambda v, g=g: self._set_game(g, pattern=pat_value(v))).pack(side="right")
            ctk.CTkLabel(bot, text=T("Intensity"), font=(FONT, 11), text_color=MUTED).pack(side="right", padx=(0, 6))
            dv = ctk.StringVar(value=f"{g['drive']}:")
            vals = sorted({f"{d}:" for d in letters} | {f"{g['drive']}:"})
            option_menu(bot, dv, vals, width=72, height=30,
                        command=lambda v, g=g: self._set_game(g, drive=v[0])).pack(side="right", padx=(0, 14))
            ctk.CTkLabel(bot, text=T("Drive"), font=(FONT, 11), text_color=MUTED).pack(side="right", padx=(0, 6))

    def _game_icon(self, g):
        """The game's own icon as a CTkImage (None if its exe can't be found yet: it is retried each redraw)."""
        if not hasattr(self, "_icon_imgs"):
            self._icon_imgs = {}
        if g["exe"] in self._icon_imgs:
            return self._icon_imgs[g["exe"]]
        miss = getattr(self, "_icon_miss", None)
        if miss is None:
            miss = self._icon_miss = {}
        if time.time() - miss.get(g["exe"], 0) < 30:   # not found a moment ago: don't rescan every redraw
            return None
        path = icons.locate(g)
        if not path:
            miss[g["exe"]] = time.time()
        img = icons.extract(path, 48) if path else None
        if path and g.get("exe_path") != path:
            g["exe_path"] = path
            letter = os.path.splitdrive(path)[0][:1].upper()
            if g.pop("auto_drive", False) and letter and letter != g["drive"]:
                g["drive"] = letter
                self.after(0, self._render_games)    # redraw so the Drive box shows the real drive
            self._save_games()
        out = ctk.CTkImage(light_image=img, dark_image=img, size=(28, 28)) if img is not None else None
        if out is not None:
            self._icon_imgs[g["exe"]] = out
        return out

    def _rename_game(self, g):
        dlg = ctk.CTkInputDialog(text=T("Name to show for") + f" {g['exe']}:", title=T("Rename game"))
        new = dlg.get_input()
        if new is None:
            return
        new = new.strip()
        self._set_game(g, name=new or g["exe"])
        self._render_games()

    def _set_game(self, g, **kw):
        if "drive" in kw:
            g.pop("auto_drive", None)   # the user chose it: never override
        g.update(kw)
        self._save_games()

    def _remove_game(self, g):
        self.cfg["games"].remove(g)
        self._save_games()
        self._render_games()

    # ----------------------------------------------------------- tools ------
    def _build_tools(self, body):
        choices = sysutil.drive_choices() or {"C:": "C"}
        self.tool_choices = choices
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(top, text=T("Drive to inspect"), font=(FONT, 13, "bold"), text_color=TEXT).pack(side="left")
        first = self._default_drive()
        start = next((k for k, v in choices.items() if v == first), next(iter(choices)))
        self.t_drive = ctk.StringVar(value=start)
        option_menu(top, self.t_drive, list(choices), width=260,
                    command=lambda _: self._refresh_health()).pack(side="right")

        # --- health
        h = card(body, T("Drive health"), T("What Windows knows about this drive, with plain-language advice."))
        self.h_box = ctk.CTkFrame(h, fg_color="transparent", height=1)
        self.h_box.pack(fill="x", pady=(8, 10))
        btn_secondary(h, T("Refresh"), self._refresh_health, width=100, height=30).pack(
            anchor="w", padx=16, pady=(0, 14))

        # --- auto-tune
        t = card(body, T("Benchmark & auto-tune"),
                 T("Measures how long the first read takes after the drive has been idle, with and "
                   "without keep-alive, then picks the lightest setting that helps. Takes about 2 minutes. "
                   "Don't run a game meanwhile."))
        self.tune_bar = ctk.CTkProgressBar(t, progress_color=ACCENT, fg_color=FIELD, height=8)
        self.tune_bar.set(0)
        self.tune_status = ctk.CTkLabel(t, text="", font=(FONT, 12), text_color=MUTED, anchor="w")
        self.tune_box = ctk.CTkFrame(t, fg_color="transparent")
        self.tune_btn = btn_primary(t, T("Run auto-tune"), self._run_tune)
        self.tune_btn.pack(anchor="w", padx=16, pady=(10, 14))

        # --- lag check
        lg = card(body, T("Lag check"),
                  T("Switch to your game right after pressing Start. After 10 seconds Diskuick watches your "
                    "real disk, CPU and memory for 30 seconds and tells you what looks wrong."))
        self.lag_bar = ctk.CTkProgressBar(lg, progress_color=ACCENT, fg_color=FIELD, height=8)
        self.lag_bar.set(0)
        self.lag_status = ctk.CTkLabel(lg, text="", font=(FONT, 12), text_color=MUTED, anchor="w")
        self.lag_box = ctk.CTkFrame(lg, fg_color="transparent")
        self.lag_btn = btn_primary(lg, T("Start lag check"), self._run_lag)
        self.lag_btn.pack(anchor="w", padx=16, pady=(10, 14))

    def _tool_letter(self) -> str:
        return self.tool_choices.get(self.t_drive.get(), "C")

    @staticmethod
    def _clear(f):
        for w in f.winfo_children():
            w.destroy()

    # health
    def _refresh_health(self):
        self._health_loaded = True
        self._clear(self.h_box)
        ctk.CTkLabel(self.h_box, text=T("Reading drive info..."), font=(FONT, 12), text_color=MUTED).pack(
            anchor="w", padx=16)
        letter = self._tool_letter()

        def work():
            info = health_mod.get_health(letter)
            self.post(lambda: self._show_health(info, letter))

        threading.Thread(target=work, daemon=True).start()

    def _show_health(self, info, letter):
        if letter != self._tool_letter():
            return
        self._clear(self.h_box)
        fmt = lambda v, s="": T("n/a") if v is None else f"{v}{s}"
        title = " · ".join(str(x) for x in (info["model"], info["media"], info["bus"]) if x) or f"{letter}:"
        ctk.CTkLabel(self.h_box, text=title, font=(FONT, 13, "bold"), text_color=TEXT, anchor="w").pack(
            fill="x", padx=16)
        grid = ctk.CTkFrame(self.h_box, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(4, 6))
        rows = [(T("Health"), fmt(info["health"])), (T("Temperature"), fmt(info["temp"], " °C")),
                (T("Wear"), fmt(info["wear"], " %")), (T("Powered on"), fmt(info["hours"], " h"))]
        for i, (k, v) in enumerate(rows):
            grid.columnconfigure(i, weight=1, uniform="h")
            ctk.CTkLabel(grid, text=k, font=(FONT, 11), text_color=MUTED).grid(row=0, column=i, sticky="w")
            ctk.CTkLabel(grid, text=v, font=(FONT, 13, "bold"), text_color=TEXT).grid(row=1, column=i, sticky="w")
        if info["total"]:
            used = 1 - info["free"] / info["total"]
            bar = ctk.CTkProgressBar(self.h_box, height=8, fg_color=FIELD,
                                     progress_color=DANGER if used > 0.9 else ACCENT)
            bar.set(used)
            bar.pack(fill="x", padx=16, pady=(4, 0))
            ctk.CTkLabel(self.h_box, text=T("{free} GB free of {total} GB").format(
                free=f"{info['free'] / 1e9:.0f}", total=f"{info['total'] / 1e9:.0f}"),
                font=(FONT, 11), text_color=MUTED, anchor="w").pack(fill="x", padx=16, pady=(2, 6))
        for lv, msg in health_mod.health_tips(info):
            level_line(self.h_box, lv, T(msg))
        if None in (info["temp"], info["wear"], info["hours"]) and not self.app.is_admin():
            btn_secondary(self.h_box, T("Restart as administrator"), self.app.restart_as_admin,
                          width=200, height=30).pack(anchor="w", padx=16, pady=(6, 0))

    # auto-tune
    def _run_tune(self):
        if getattr(self, "_tuning", False):
            self._tune_cancel.set()
            return
        letter = self._tool_letter()
        self._tuning = True
        self._tune_cancel.clear()
        self.tune_btn.configure(text=T("Cancel"), fg_color=FIELD, hover_color=BORDER, text_color=TEXT)
        self._clear(self.tune_box)
        self.tune_bar.pack(fill="x", padx=16, pady=(10, 2), before=self.tune_btn)
        self.tune_status.pack(fill="x", padx=16, before=self.tune_btn)
        self.tune_status.configure(text=T("Preparing…"))
        ctrl = self.app.ctrl

        def progress(frac, text):
            self.post(lambda: (self.tune_bar.set(frac), self.tune_status.configure(text=T(text))))

        def work():
            rows, err = None, None
            ctrl.suspend(letter)
            try:
                for attempt in (1, 2):
                    path = dk.ensure_probe(letter, self.cfg["size_mb"])
                    time.sleep(1.0)
                    try:
                        rows = dk.run_bench(path, reads=14, gap=2.0, progress=progress,
                                            cancel=self._tune_cancel)
                        break
                    except OSError:
                        if attempt == 2 or os.path.exists(path):
                            raise  # only retry when the probe file vanished underneath us
            except Exception as e:
                err = str(e)
            finally:
                ctrl.resume(letter)
            self.post(lambda: self._tune_done(rows, err))

        threading.Thread(target=work, daemon=True).start()

    def _tune_done(self, rows, err):
        self._tuning = False
        self.tune_btn.configure(text=T("Run auto-tune"), fg_color=ACCENT, hover_color=ACCENT_HOVER,
                                text_color="#06210F")
        self.tune_bar.pack_forget()
        self.tune_status.pack_forget()
        self._clear(self.tune_box)
        self.tune_box.pack(fill="x", before=self.tune_btn)
        if err:
            level_line(self.tune_box, "bad", f"{T('Test failed')}: {err}")
            return
        if rows is None:
            level_line(self.tune_box, "warn", T("Cancelled."))
            return
        grid = ctk.CTkFrame(self.tune_box, fg_color=FIELD, corner_radius=10)
        grid.pack(fill="x", padx=16, pady=(10, 8))
        heads = [T("Keep-alive"), T("avg ms"), T("p95 ms"), T("max ms")]
        names = {"none": T("None"), "random": T("Light"), "seq": T("Balanced"), "heavy": T("Heavy")}
        for c, hd in enumerate(heads):
            grid.columnconfigure(c, weight=1, uniform="b")
            ctk.CTkLabel(grid, text=hd, font=(FONT, 11), text_color=MUTED).grid(row=0, column=c, sticky="w", padx=10, pady=(8, 2))
        for r, (name, (avg, _med, p95, mx)) in enumerate(rows, start=1):
            for c, v in enumerate((names[name], f"{avg:.1f}", f"{p95:.1f}", f"{mx:.1f}")):
                ctk.CTkLabel(grid, text=v, font=(FONT, 12, "bold" if c == 0 else "normal"),
                             text_color=TEXT).grid(row=r, column=c, sticky="w", padx=10, pady=(2, 8 if r == len(rows) else 2))
        rec = dk.recommend(rows)
        msgs = {"helps": ("ok", T("Keep-alive removes the idle stalls. Recommended setting: {p}.")
                          .format(p=names[rec["pattern"]] if rec["pattern"] else "")),
                "no_stalls": ("ok", T("No idle stalls detected on this drive - it wakes up fast. "
                                      "Keep-alive probably won't help here.")),
                "no_help": ("warn", T("This drive hesitates after idling, but keep-alive didn't clearly "
                                      "help. The cause may be elsewhere - try the Lag check."))}
        lv, msg = msgs[rec["message_key"]]
        level_line(self.tune_box, lv, msg)
        if rec["pattern"]:
            btn_primary(self.tune_box, T("Use {p} as default").format(p=names[rec["pattern"]]),
                        lambda p=rec["pattern"]: self._apply_rec(p), height=34).pack(
                anchor="w", padx=16, pady=(8, 0))

    def _apply_rec(self, pattern):
        self.app.apply({"default_pattern": pattern})
        self.int_var.set(pat_label(pattern))
        self._int_changed(save=False)
        level_line(self.tune_box, "ok", T("Saved."))

    # lag check
    def _run_lag(self):
        if getattr(self, "_lagging", False):
            self._lag_cancel.set()
            return
        letter = self._tool_letter()
        self._lagging = True
        self._lag_cancel.clear()
        self.lag_btn.configure(text=T("Cancel"), fg_color=FIELD, hover_color=BORDER, text_color=TEXT)
        self._clear(self.lag_box)
        self.lag_bar.set(0)
        self.lag_bar.pack(fill="x", padx=16, pady=(10, 2), before=self.lag_btn)
        self.lag_status.pack(fill="x", padx=16, before=self.lag_btn)

        def work():
            cancelled = False
            for s in range(10, 0, -1):  # time to alt-tab into the game
                if self._lag_cancel.wait(1.0):
                    cancelled = True
                    break
                self.post(lambda s=s: self.lag_status.configure(
                    text=T("Starting in {s}s - switch to your game now…").format(s=s - 1)))
            res = None
            if not cancelled:
                self.post(lambda: self.lag_status.configure(text=T("Measuring… keep playing")))
                try:
                    res = lag_mod.run_lagcheck(letter, 30, on_tick=lambda f: self.post(lambda: self.lag_bar.set(f)),
                                               cancel=self._lag_cancel, net_host=self.cfg["net_host"])
                except Exception as e:
                    res = {"findings": [("bad", f"{T('Test failed')}: {e}")]}
            self.post(lambda: self._lag_done(res))

        threading.Thread(target=work, daemon=True).start()

    def _lag_done(self, res):
        self._lagging = False
        self.lag_btn.configure(text=T("Start lag check"), fg_color=ACCENT, hover_color=ACCENT_HOVER,
                               text_color="#06210F")
        self.lag_bar.pack_forget()
        self.lag_status.pack_forget()
        self._clear(self.lag_box)
        self.lag_box.pack(fill="x", before=self.lag_btn)
        if res is None:
            level_line(self.lag_box, "warn", T("Cancelled."))
            return
        for lv, msg in res["findings"]:
            level_line(self.lag_box, lv, msg)
        note = "Indicative only." if res.get("net") else "Indicative only - network isn't measured."
        ctk.CTkLabel(self.lag_box, text=T(note),
                     font=(FONT, 11), text_color=MUTED).pack(anchor="w", padx=16, pady=(6, 0))

    # -------------------------------------------------------- settings ------
    def _build_settings(self, body):
        c = self.cfg
        # when to run
        w = card(body, T("When to run"))
        self.mode_var = ctk.StringVar(value=T("Only while gaming") if c["mode"] == "games" else T("Always on"))
        segmented(w, [T("Only while gaming"), T("Always on")], self.mode_var, self._mode_changed).pack(
            fill="x", padx=16, pady=(10, 6))
        self.mode_hint = ctk.CTkLabel(w, text="", font=(FONT, 12), text_color=MUTED, anchor="w",
                                      justify="left", wraplength=500)
        self.mode_hint.pack(fill="x", padx=16)
        self.always_box = ctk.CTkFrame(w, fg_color="transparent")
        ctk.CTkLabel(self.always_box, text=T("Drives to keep awake"), font=(FONT, 12), text_color=MUTED).pack(
            anchor="w", pady=(6, 2))
        self.drive_vars = {}
        for disp, letter in sysutil.drive_choices().items():
            v = ctk.BooleanVar(value=letter in c["always_drives"])
            self.drive_vars[letter] = v
            ctk.CTkCheckBox(self.always_box, text=disp, variable=v, font=(FONT, 12), text_color=TEXT,
                            fg_color=ACCENT, hover_color=ACCENT_HOVER, checkmark_color="#06210F",
                            border_color=BORDER, command=self._drives_changed).pack(anchor="w", pady=3)
        self.mode_pad = ctk.CTkFrame(w, fg_color="transparent", height=10)
        self.mode_pad.pack()
        self._mode_changed(save=False)

        # intensity
        i = card(body, T("Default intensity"), T("How hard to nudge the drive. Games can override this."))
        self.int_var = ctk.StringVar(value=pat_label(c["default_pattern"]))
        self.int_seg = segmented(i, [T(l) for _, l in PATTERN_LABELS], self.int_var,
                                 lambda _: self._int_changed())
        self.int_seg.pack(fill="x", padx=16, pady=(10, 6))
        self.int_desc = ctk.CTkLabel(i, text="", font=(FONT, 12), text_color=MUTED, anchor="w",
                                     justify="left", wraplength=500)
        self.int_desc.pack(fill="x", padx=16)
        self.v_adapt = ctk.BooleanVar(value=c["adaptive"])
        switch_row(i, T("Smart intensity"),
                   T("Starts Light and steps up only while the drive keeps stalling, then steps back down "
                     "when it's calm. Ignores the choice above (a game's own setting still wins)."),
                   self.v_adapt, self._adapt_changed)
        self._int_changed(save=False)
        adv = ctk.CTkFrame(i, fg_color="transparent")
        adv.pack(fill="x", padx=16, pady=(8, 4))
        ctk.CTkLabel(adv, text=T("Seconds between reads (advanced)"), font=(FONT, 12), text_color=MUTED).pack(side="left")
        self.interval = ctk.CTkEntry(adv, width=90, height=30, fg_color=FIELD, border_color=BORDER,
                                     corner_radius=8, placeholder_text=T("default"))
        self.interval.pack(side="right")
        if c["interval"] is not None:
            self.interval.insert(0, str(c["interval"]))
        for ev in ("<Return>", "<FocusOut>"):
            self.interval.bind(ev, lambda _e: self._interval_changed())
        self.int_err = ctk.CTkLabel(i, text="", font=(FONT, 11), text_color=DANGER, anchor="w")
        self.int_err.pack(fill="x", padx=16, pady=(0, 10))
        self._int_changed(save=False)

        # behaviour
        b = card(body, T("Behaviour"))
        self.v_bat = ctk.BooleanVar(value=c["pause_on_battery"])
        self.v_focus = ctk.BooleanVar(value=c["only_when_focused"])
        self.v_notify = ctk.BooleanVar(value=c["notify"])
        self.v_auto = ctk.BooleanVar(value=self.app.autostart_enabled())
        switch_row(b, T("Pause on battery"), T("Laptops: don't keep the drive busy when unplugged."),
                   self.v_bat, lambda: self.app.apply({"pause_on_battery": self.v_bat.get()}))
        switch_row(b, T("Only while the game is focused"), T("Pauses when you alt-tab away from the game."),
                   self.v_focus, lambda: self.app.apply({"only_when_focused": self.v_focus.get()}))
        switch_row(b, T("Notify when a game starts"), T("A small tray notification."),
                   self.v_notify, lambda: self.app.apply({"notify": self.v_notify.get()}))
        self.v_alerts = ctk.BooleanVar(value=c["alerts"])
        self.v_keys = ctk.BooleanVar(value=c["hotkeys"])
        switch_row(b, T("Drive alerts"), T("Tell me when the game drive is nearly full or no longer healthy."),
                   self.v_alerts, lambda: self.app.apply({"alerts": self.v_alerts.get()}))
        switch_row(b, T("Keyboard shortcuts"),
                   T("Ctrl+Alt+L marks a lag moment. Ctrl+Alt+O shows or hides the overlay."),
                   self.v_keys, lambda: self.app.apply({"hotkeys": self.v_keys.get()}))
        switch_row(b, T("Start with Windows"), T("Runs quietly in the tray at login."),
                   self.v_auto, lambda: self.app.set_autostart(self.v_auto.get()))
        ctk.CTkFrame(b, fg_color="transparent", height=6).pack()

        # overlay
        o = card(body, T("Latency overlay"),
                 T("A small live readout in a screen corner while the drive is being kept awake (a game is "
                   "running, or Always on). It's a separate window that never touches the game, and shows "
                   "over windowed and borderless games. It can't show over exclusive fullscreen (for example Battlefield 3): "
                   "switch that game to borderless or windowed."))
        self.v_overlay = ctk.BooleanVar(value=c["overlay"])
        switch_row(o, T("Show overlay while the drive is kept awake"), None, self.v_overlay,
                   lambda: self.app.apply({"overlay": self.v_overlay.get()}))
        self.v_extra = ctk.BooleanVar(value=c["overlay_extra"])
        switch_row(o, T("Also show CPU and GPU load"), None, self.v_extra,
                   lambda: self.app.apply({"overlay_extra": self.v_extra.get()}))
        self.v_fps = ctk.BooleanVar(value=c["overlay_fps"])
        switch_row(o, T("Also show FPS"),
                   T("Needs PresentMon.exe next to Diskuick.exe and Diskuick running as administrator."),
                   self.v_fps, lambda: self.app.apply({"overlay_fps": self.v_fps.get()}))
        orow = ctk.CTkFrame(o, fg_color="transparent")
        orow.pack(fill="x", padx=16, pady=(0, 14))
        corners = {"top-left": T("Top left"), "top-right": T("Top right"),
                   "bottom-left": T("Bottom left"), "bottom-right": T("Bottom right")}
        self.corner_var = ctk.StringVar(value=corners[c["overlay_corner"]])
        ctk.CTkLabel(orow, text=T("Position"), font=(FONT, 13), text_color=TEXT).pack(side="left")
        btn_secondary(orow, T("Preview"), lambda: self.app.overlay.preview(4), width=90, height=32).pack(side="right")
        option_menu(orow, self.corner_var, list(corners.values()), width=140, height=32,
                    command=lambda v: self.app.apply({"overlay_corner": next(k for k, t in corners.items() if t == v)})
                    ).pack(side="right", padx=(0, 8))

        # network check
        n = card(body, T("Network check (optional)"),
                 T("Checks whether your internet could be behind the lag. Type 1.1.1.1 to check your "
                   "general connection, or the address of a server you play on (the :port is optional and "
                   "defaults to 443). During a Lag check (and when you mark a lag) Diskuick measures ping "
                   "(how long the server takes to answer) and packet loss (answers that never arrive), so "
                   "you can tell a network problem from a drive problem. Only a normal connection is "
                   "opened, a few times a second, and nothing about you is sent. Leave empty to keep it "
                   "off."))
        nrow = ctk.CTkFrame(n, fg_color="transparent")
        nrow.pack(fill="x", padx=16, pady=(8, 2))
        ctk.CTkLabel(nrow, text=T("Host"), font=(FONT, 13), text_color=TEXT).pack(side="left")
        self.net_entry = ctk.CTkEntry(nrow, width=240, height=32, fg_color=FIELD, border_color=BORDER,
                                      corner_radius=8, placeholder_text=T("e.g. 1.1.1.1"))
        self.net_entry.pack(side="right")
        if c["net_host"]:
            self.net_entry.insert(0, c["net_host"])
        for ev in ("<Return>", "<FocusOut>"):
            self.net_entry.bind(ev, lambda _e: self._net_changed())
        self.net_err = ctk.CTkLabel(n, text="", font=(FONT, 11), text_color=DANGER, anchor="w")
        self.net_err.pack(fill="x", padx=16, pady=(0, 10))

        # game mode
        gm = card(body, T("Game mode (optional)"),
                  T("When one of your games starts, politely ask these programs to close (they can still ask "
                    "you to save), and reopen them when the game ends. Nothing is force-closed."))
        self.gm_box = ctk.CTkFrame(gm, fg_color="transparent")
        self.gm_box.pack(fill="x", padx=16, pady=(6, 0))
        self.gm_err = ctk.CTkLabel(gm, text="", font=(FONT, 11), text_color=DANGER, anchor="w")
        self.gm_err.pack(fill="x", padx=16)
        btn_secondary(gm, T("Add running program…"), lambda: ProcessPicker(self, self._gm_add),
                      height=30).pack(anchor="w", padx=16, pady=(4, 6))
        self.v_restore = ctk.BooleanVar(value=c["game_restore"])
        switch_row(gm, T("Reopen them afterwards"), None, self.v_restore,
                   lambda: self.app.apply({"game_restore": self.v_restore.get()}))
        self._render_gm()

        # appearance
        a = card(body, T("Appearance"))
        row = ctk.CTkFrame(a, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(10, 14))
        themes = {"system": T("System"), "dark": T("Dark"), "light": T("Light theme")}
        self.theme_var = ctk.StringVar(value=themes[c["theme"]])
        ctk.CTkLabel(row, text=T("Theme"), font=(FONT, 13), text_color=TEXT).grid(row=0, column=0, sticky="w")
        segmented(row, list(themes.values()), self.theme_var,
                  lambda v: self.app.apply({"theme": next(k for k, t in themes.items() if t == v)})
                  ).grid(row=0, column=1, sticky="e", padx=(14, 0))
        ctk.CTkLabel(row, text=T("Language"), font=(FONT, 13), text_color=TEXT).grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.lang_var = ctk.StringVar(value=LANGS[c["language"]])
        option_menu(row, self.lang_var, list(LANGS.values()), width=200,
                    command=lambda v: self.app.apply({"language": next(k for k, n in LANGS.items() if n == v)})
                    ).grid(row=1, column=1, sticky="e", padx=(14, 0), pady=(10, 0))
        row.columnconfigure(1, weight=1)

        # about
        ab = card(body, f"Diskuick {VERSION}")
        self.upd_label = ctk.CTkLabel(ab, text="", font=(FONT, 12), text_color=MUTED, anchor="w",
                                      wraplength=500, justify="left")
        self.upd_label.pack(fill="x", padx=16, pady=(2, 0))
        self.v_upd = ctk.BooleanVar(value=c["check_updates"])
        switch_row(ab, T("Check for updates"), T("Only the repository name is contacted; nothing about you is sent."),
                   self.v_upd, lambda: self.app.apply({"check_updates": self.v_upd.get()}))
        links = ctk.CTkFrame(ab, fg_color="transparent")
        links.pack(fill="x", padx=16, pady=(0, 14))
        self.check_btn = btn_secondary(links, T("Check now"), self._check_now, height=30)
        self.check_btn.pack(side="left", padx=(0, 8))
        btn_secondary(links, T("Open data folder"), lambda: os.startfile(config.APP_DIR) if os.path.isdir(config.APP_DIR) else None,
                      height=30).pack(side="left")
        btn_secondary(links, T("Open stall log"), self._open_log, height=30).pack(side="left", padx=8)
        if not UPDATE_REPO:
            self.upd_label.configure(text=T("Update checks are off until a release repository is set."))
            self.check_btn.configure(state="disabled")

    def _net_changed(self):
        raw = self.net_entry.get().strip()
        if raw and netcheck.parse_target(raw) is None:
            self.net_err.configure(text=T("Enter a host name or address, optionally with :port."))
            return
        self.net_err.configure(text="")
        if raw != self.cfg["net_host"]:
            self.app.apply({"net_host": raw})

    def _render_gm(self):
        self._clear(self.gm_box)
        exes = self.cfg["game_close"]
        if not exes:
            ctk.CTkLabel(self.gm_box, text=T("No programs chosen."), font=(FONT, 12),
                         text_color=MUTED).pack(anchor="w")
        for e in exes:
            row = ctk.CTkFrame(self.gm_box, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=e, font=(FONT, 13), text_color=TEXT).pack(side="left")
            btn_ghost(row, T("Remove"), lambda e=e: self._gm_remove(e), width=70, height=26).pack(side="right")

    def _gm_add(self, exe: str):
        exe = exe.strip().lower()
        if not gamemode.allowed(exe):
            self.gm_err.configure(text=T("That program is protected and can't be closed."))
            return
        self.gm_err.configure(text="")
        if exe not in self.cfg["game_close"]:
            self.app.apply({"game_close": sorted(self.cfg["game_close"] + [exe])})
        self._render_gm()

    def _gm_remove(self, exe: str):
        self.app.apply({"game_close": [e for e in self.cfg["game_close"] if e != exe]})
        self._render_gm()

    def _open_log(self):
        if os.path.exists(stats_mod.LOG_PATH):
            os.startfile(stats_mod.LOG_PATH)

    def _mode_changed(self, _v=None, save=True):
        games = self.mode_var.get() == T("Only while gaming")
        if games:
            self.always_box.pack_forget()
            self.mode_hint.configure(text=T("Starts automatically when one of your games opens and stops "
                                            "when it closes. Add games in the Games tab."))
        else:
            self.always_box.pack(fill="x", padx=16, before=self.mode_pad)
            self.mode_hint.configure(text=T("Runs the whole time Diskuick is open. Simple, but keeps "
                                            "the drive busy even when idle."))
        if save:
            self.app.apply({"mode": "games" if games else "always"})

    def _drives_changed(self):
        self.app.apply({"always_drives": [d for d, v in self.drive_vars.items() if v.get()]})

    def _int_changed(self, save=True):
        p = pat_value(self.int_var.get()) or "random"
        smart = self.v_adapt.get()
        # Smart intensity picks the level itself, so the manual choice is greyed out while it's on
        self.int_seg.configure(state="disabled" if smart else "normal")
        self.int_desc.configure(text=T("Smart intensity is on: it picks the level for you. Turn it off to choose "
                                       "one yourself.") if smart else T(PATTERN_DESC[p]))
        if save:
            self.app.apply({"default_pattern": p})

    def _adapt_changed(self):
        self.app.apply({"adaptive": self.v_adapt.get()})
        self._int_changed(save=False)
        if hasattr(self, "games_box"):
            self._render_games()       # games on "no override" are labelled Smart/Default to match

    def _interval_changed(self):
        raw = self.interval.get().strip()
        if not raw:
            val = None
        else:
            try:
                val = float(raw)
                if val < 0:
                    raise ValueError
            except ValueError:
                self.int_err.configure(text=T("Enter a positive number, or leave empty for the default."))
                return
        self.int_err.configure(text="")
        if val != self.cfg["interval"]:
            self.app.apply({"interval": val})
