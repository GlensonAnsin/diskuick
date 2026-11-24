"""Background brain: decides which drives need keep-alive right now and runs it."""
import os
import threading
import time

import psutil

import alerts as alerts_mod
import diskuick as dk
import gamemode
import health as health_mod
import sysutil
from adaptive import Adaptive

POLL_SECONDS = 2.0


def strongest(a: str, b: str) -> str:
    return a if dk.PATTERN_RANK[a] >= dk.PATTERN_RANK[b] else b


def decide(cfg: dict, running: set, foreground: str | None, battery: bool):
    """Pure decision function.

    Returns (want, games, reason):
      want   = {drive_letter: pattern} that should be kept awake now
      games  = the game dicts that are currently active (for notifications/status)
      reason = human-readable explanation when `want` is empty
    """
    if not cfg["enabled"]:
        return {}, [], "Disabled"
    if cfg["pause_on_battery"] and battery:
        return {}, [], "Paused while on battery"
    default = cfg["default_pattern"]
    want, active = {}, []
    if cfg["mode"] == "always":
        for d in cfg["always_drives"]:
            want[d] = default
        if not want:
            return {}, [], "Choose a drive in Settings"
        return want, [], ""
    games = [g for g in cfg["games"] if g["enabled"]]
    if not games:
        return {}, [], "Add games in the Games tab"
    for g in games:
        if g["exe"] in running:
            if cfg["only_when_focused"] and foreground != g["exe"]:
                continue
            active.append(g)
            p = g["pattern"] or default
            want[g["drive"]] = strongest(want[g["drive"]], p) if g["drive"] in want else p
    if not want:
        why = ("Waiting for a game window to be in focus"
               if cfg["only_when_focused"] and any(g["exe"] in running for g in games)
               else "Waiting for a game to start")
        return {}, [], why
    return want, active, ""


MIN_REPORT_S = 30  # shorter sessions aren't worth a report


def verdict(rep: dict) -> dict:
    """Plain-language answer to 'was my lag the drive?' for one finished session."""
    if rep["stalls"] >= 3:
        return {"level": "bad", "text": f"The drive stalled {rep['stalls']} times (worst {rep['worst_ms']:.0f} ms). "
                                         "It is a likely cause of lag."}
    if rep.get("gpu_avg") is not None and rep["gpu_avg"] >= 95:
        return {"level": "bad", "text": f"The GPU was maxed out (average {rep['gpu_avg']:.0f}%). "
                                         "Lower graphics settings may help."}
    if rep["cpu_avg"] >= 90:
        return {"level": "bad", "text": f"The CPU was maxed out (average {rep['cpu_avg']:.0f}%)."}
    if rep["ram_peak"] >= 92:
        return {"level": "warn", "text": f"Memory was nearly full (peak {rep['ram_peak']:.0f}%). Windows may have "
                                          "been swapping to disk."}
    if rep["stalls"]:
        return {"level": "warn", "text": f"{rep['stalls']} short drive stall(s), worst {rep['worst_ms']:.0f} ms."}
    return {"level": "ok", "text": "No drive stalls. If you felt lag, the cause is probably not the drive."}


def make_report(s: dict, end: float) -> dict:
    n, cn, gn = max(s["n"], 1), max(s["cpu_n"], 1), s["gpu_n"]
    rep = {"drive": s["drive"], "start": s["start"], "end": end, "seconds": round(end - s["start"]),
           "games": sorted(s["games"]), "worst_ms": round(s["worst"], 1), "avg_ms": round(s["avg_sum"] / n, 2),
           "stalls": s["stalls"], "cpu_avg": round(s["cpu_sum"] / cn, 1), "cpu_peak": round(s["cpu_peak"], 1),
           "ram_peak": round(s["ram_peak"], 1),
           "gpu_avg": round(s["gpu_sum"] / gn, 1) if gn else None,
           "gpu_peak": round(s["gpu_peak"], 1) if gn else None}
    rep["verdict"] = verdict(rep)
    return rep


class Controller(threading.Thread):
    def __init__(self, cfg: dict, stats, on_status=None, on_event=None):
        super().__init__(daemon=True)
        self.cfg, self.stats = dict(cfg), stats
        self.on_status, self.on_event = on_status or (lambda *_: None), on_event or (lambda *_: None)
        self._lock = threading.Lock()
        self._quit = threading.Event()
        self._poke = threading.Event()
        self.state, self.text = "off", "Starting"
        self.kas: dict[str, tuple] = {}          # drive -> (KeepAlive, key)
        self.errors: dict[str, str] = {}
        self._retry_at: dict[str, float] = {}
        self.suspended: set[str] = set()
        self._prev_games: set[str] = set()
        self._adapt: dict[str, Adaptive] = {}
        self._sess: dict[str, dict] = {}
        self.gpu_source = lambda: None           # set by the app: latest GPU load or None
        self._alerts = alerts_mod.Alerts()
        self._alert_t = self._health_t = 0.0
        self._health_busy = False
        self._gm_active = False
        self._closed: list[str] = []

    # ---- public API (thread-safe)
    def update_cfg(self, cfg: dict):
        with self._lock:
            self.cfg = dict(cfg)
        self._poke.set()

    def suspend(self, drive: str):
        """Stop keep-alive on a drive right now and keep it stopped (used while benchmarking)."""
        with self._lock:
            self.suspended.add(drive)
            ka = self.kas.pop(drive, None)
        if ka:
            ka[0].stop()

    def resume(self, drive: str):
        with self._lock:
            self.suspended.discard(drive)
        self._poke.set()

    def active_drives(self) -> list[str]:
        with self._lock:
            return sorted(self.kas)

    def running_games(self) -> list[str]:
        """Exe names of the configured games that are running right now."""
        return sorted(self._prev_games)

    def history(self, drive: str) -> list:
        with self._lock:
            ka = self.kas.get(drive)
        return list(ka[0].history) if ka else []

    def stall_threshold(self, drive: str) -> float:
        with self._lock:
            ka = self.kas.get(drive)
        return ka[0].stall_ms if ka else dk.STALL_MS["random"]

    def shutdown(self):
        self._quit.set()
        self._poke.set()

    # ---- internals
    def _status(self, state: str, text: str):
        if (state, text) != (self.state, self.text):
            self.state, self.text = state, text
            self.on_status(state, text)

    def _on_stall(self, drive: str, ts: float, ms: float):
        self.stats.add_stall(drive, ts, ms)
        ad = self._adapt.get(drive)
        if ad:
            ad.note_stall(ts)

    def current_level(self, drive: str) -> str | None:
        """Pattern chosen by smart intensity for a drive (None when it isn't in use)."""
        ad = self._adapt.get(drive)
        return ad.pattern if ad else None

    def _apply_adaptive(self, cfg: dict, want: dict, games: list) -> dict:
        if not cfg["adaptive"]:
            self._adapt.clear()
            return want
        now = time.time()
        out = {}
        for d, p in want.items():
            if any(g["drive"] == d and g["pattern"] for g in games):
                out[d] = p                      # a game on this drive asked for a specific intensity
                self._adapt.pop(d, None)
                continue
            ad = self._adapt.get(d)
            if ad is None:
                ad = self._adapt[d] = Adaptive(now)
            out[d] = ad.update(now)
        for d in list(self._adapt):
            if d not in want:
                del self._adapt[d]
        return out

    def _track_sessions(self, games: list):
        now = time.time()
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        gpu = self.gpu_source()
        for d in self.active_drives():
            s = self._sess.get(d)
            if s is None:
                s = self._sess[d] = {"drive": d, "start": now, "games": set(), "worst": 0.0, "avg_sum": 0.0,
                                     "n": 0, "stalls": 0, "cpu_sum": 0.0, "cpu_n": 0, "cpu_peak": 0.0,
                                     "ram_peak": 0.0, "gpu_sum": 0.0, "gpu_n": 0, "gpu_peak": 0.0, "seen": 0}
            s["games"].update(g["name"] for g in games if g["drive"] == d)
            thr = self.stall_threshold(d)
            for sec, mx, av in self.history(d):
                if sec > s["seen"]:
                    s["seen"] = sec
                    s["worst"] = max(s["worst"], mx)
                    s["avg_sum"] += av
                    s["n"] += 1
                    s["stalls"] += mx > thr
            s["cpu_sum"] += cpu
            s["cpu_n"] += 1
            s["cpu_peak"] = max(s["cpu_peak"], cpu)
            s["ram_peak"] = max(s["ram_peak"], ram)
            if gpu is not None:
                s["gpu_sum"] += gpu
                s["gpu_n"] += 1
                s["gpu_peak"] = max(s["gpu_peak"], gpu)
        with self._lock:
            idle = [d for d in self._sess if d not in self.kas and d not in self.suspended]
        for d in idle:
            s = self._sess.pop(d)
            if now - s["start"] >= MIN_REPORT_S and s["n"] > 0:
                rep = make_report(s, now)
                self.stats.add_report(rep)
                self.on_event("session_end", rep)

    def _game_mode(self, cfg: dict, names: set):
        if names and not self._gm_active:
            self._gm_active = True
            if cfg["game_close"]:
                def work(exes=list(cfg["game_close"])):
                    closed = gamemode.close_programs(exes)
                    with self._lock:
                        self._closed = closed
                    if closed:
                        self.on_event("game_mode", {"closed": [os.path.basename(p) for p in closed]})
                threading.Thread(target=work, daemon=True).start()
        elif not names and self._gm_active:
            self._gm_active = False
            with self._lock:
                paths, self._closed = self._closed, []
            if paths and cfg["game_restore"]:
                threading.Thread(target=gamemode.reopen, args=(paths,), daemon=True).start()

    def _check_alerts(self, cfg: dict):
        if not cfg["alerts"]:
            return
        now, drives = time.time(), self.active_drives()
        if not drives:
            return
        if now - self._alert_t >= 60:
            self._alert_t = now
            for d in drives:
                free, total = alerts_mod.usage(d)
                for m in self._alerts.free_space(d, free, total, now):
                    self.on_event("alert", {"text": m})
        if now - self._health_t >= 1800 and not self._health_busy:
            self._health_t, self._health_busy = now, True

            def work():
                try:
                    for d in drives:
                        info = health_mod.get_health(d)
                        for m in self._alerts.health(d, info.get("health")):
                            self.on_event("alert", {"text": m})
                except Exception:
                    pass
                finally:
                    self._health_busy = False
            threading.Thread(target=work, daemon=True).start()

    def _reconcile(self, cfg: dict, want: dict):
        with self._lock:
            suspended = set(self.suspended)
        want = {d: p for d, p in want.items() if d not in suspended}
        for d in list(self.kas):
            ka, key = self.kas[d]
            if d not in want or ka.error or not ka.is_alive():
                if ka.error:
                    self.errors[d] = ka.error
                    self._retry_at[d] = time.time() + 10
                with self._lock:
                    self.kas.pop(d, None)
                ka.stop()
        for d, pat in want.items():
            key = (pat, cfg["interval"], cfg["size_mb"])
            cur = self.kas.get(d)
            if cur and cur[1] != key:
                with self._lock:
                    self.kas.pop(d, None)
                cur[0].stop()
                cur = None
            if cur is None and time.time() >= self._retry_at.get(d, 0):
                try:
                    path = dk.ensure_probe(d, cfg["size_mb"])
                    ka = dk.KeepAlive(path, pat, cfg["interval"], d, self._on_stall)
                    ka.start()
                    with self._lock:
                        self.kas[d] = (ka, key)
                    self.errors.pop(d, None)
                    self.stats.add_session()
                except Exception as e:
                    self.errors[d] = str(e)
                    self._retry_at[d] = time.time() + 10
        for d in list(self.errors):
            if d not in want:
                self.errors.pop(d, None)

    def run(self):
        last, last_save = time.monotonic(), time.monotonic()
        while not self._quit.is_set():
            with self._lock:
                cfg = dict(self.cfg)
            try:
                running = sysutil.running_exes() if cfg["mode"] == "games" else set()
                fg = sysutil.foreground_exe() if cfg["only_when_focused"] else None
                bat = sysutil.on_battery() if cfg["pause_on_battery"] else False
                want, games, reason = decide(cfg, running, fg, bat)
                want = self._apply_adaptive(cfg, want, games)
                self._reconcile(cfg, want)
                self._track_sessions(games)
                self._check_alerts(cfg)

                names = {g["exe"] for g in games}
                if cfg["notify"]:
                    for g in games:
                        if g["exe"] not in self._prev_games:
                            self.on_event("game_start", g)
                self._prev_games = names
                self._game_mode(cfg, names)

                drives = self.active_drives()
                if drives:
                    who = f" · {', '.join(g['name'] for g in games)}" if games else ""
                    if cfg["adaptive"]:
                        lv = {"random": "Light", "seq": "Balanced", "heavy": "Heavy"}
                        who += " · " + ", ".join(lv[self.current_level(d)] for d in drives
                                                 if self.current_level(d))
                    self._status("active", f"Active on {', '.join(d + ':' for d in drives)}{who}")
                elif self.errors:
                    d, msg = next(iter(self.errors.items()))
                    self._status("error", f"Error on {d}: {msg}"[:140])
                else:
                    state = "waiting" if reason.startswith("Waiting") else "off"
                    self._status(state, reason or "Idle")
            except Exception as e:  # never let the loop die
                self._status("error", f"Error: {e}"[:140])

            now = time.monotonic()
            if self.kas:
                self.stats.add_active(now - last)
            last = now
            if now - last_save > 30:
                self.stats.save()
                last_save = now
            self._poke.wait(POLL_SECONDS)
            self._poke.clear()

        for d in list(self.kas):
            self.kas.pop(d)[0].stop()
        self.stats.save()
