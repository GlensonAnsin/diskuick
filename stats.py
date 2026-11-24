"""Session statistics + stall log (stored in %APPDATA%\\diskuick)."""
import collections
import json
import os
import threading
import time

import config

STATS_PATH = os.path.join(config.APP_DIR, "stats.json")
LOG_PATH = os.path.join(config.APP_DIR, "stalls.log")
MAX_LOG_BYTES = 256 * 1024


class Stats:
    def __init__(self, stats_path: str = STATS_PATH, log_path: str = LOG_PATH):
        self.stats_path, self.log_path = stats_path, log_path
        self._lock = threading.Lock()
        self.data = {"active_seconds": 0.0, "sessions": 0, "stalls": 0}
        self.recent = collections.deque(maxlen=50)  # (ts, drive, ms)
        try:
            with open(stats_path, encoding="utf-8") as f:
                self.data.update(json.load(f))
        except (OSError, ValueError):
            pass
        self._load_recent()

    def _load_recent(self):
        try:
            with open(self.log_path, encoding="utf-8") as f:
                for line in f.readlines()[-50:]:
                    ts, drive, ms = line.rstrip("\n").split("\t")
                    self.recent.append((float(ts), drive, float(ms)))
        except (OSError, ValueError):
            pass

    def add_active(self, seconds: float):
        with self._lock:
            self.data["active_seconds"] += seconds

    def add_session(self):
        with self._lock:
            self.data["sessions"] += 1

    def add_stall(self, drive: str, ts: float, ms: float):
        with self._lock:
            self.data["stalls"] += 1
            self.recent.append((ts, drive, ms))
            try:
                os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(f"{ts:.0f}\t{drive}\t{ms:.0f}\n")
                if os.path.getsize(self.log_path) > MAX_LOG_BYTES:
                    with open(self.log_path, encoding="utf-8") as f:
                        keep = f.readlines()[-500:]
                    with open(self.log_path, "w", encoding="utf-8") as f:
                        f.writelines(keep)
            except OSError:
                pass

    def recent_stalls(self, n: int = 5):
        with self._lock:
            return list(self.recent)[-n:][::-1]

    def save(self):
        with self._lock:
            snap = dict(self.data)
        try:
            os.makedirs(os.path.dirname(self.stats_path), exist_ok=True)
            with open(self.stats_path, "w", encoding="utf-8") as f:
                json.dump(snap, f)
        except OSError:
            pass


def fmt_duration(seconds: float) -> str:
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    m = s // 60
    if m < 60:
        return f"{m}m"
    return f"{m // 60}h {m % 60:02d}m"


def fmt_clock(ts: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(ts))
