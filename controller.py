"""Background brain: decides which drives need keep-alive right now and runs it."""
import threading
import time

import diskuick as dk
import sysutil

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
                    ka = dk.KeepAlive(path, pat, cfg["interval"], d, self.stats.add_stall)
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
                self._reconcile(cfg, want)

                names = {g["exe"] for g in games}
                if cfg["notify"]:
                    for g in games:
                        if g["exe"] not in self._prev_games:
                            self.on_event("game_start", g)
                self._prev_games = names

                drives = self.active_drives()
                if drives:
                    who = f" · {', '.join(g['name'] for g in games)}" if games else ""
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
