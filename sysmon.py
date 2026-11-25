"""Live system readings used by the overlay, lag marks and the lag check: GPU load and disk users."""
import csv
import io
import os
import subprocess
import threading
import time

import psutil

import lagcheck

NO_WINDOW = 0x08000000
GPU_COUNTER = r"\GPU Engine(*)\Utilization Percentage"


def gpu_once(timeout: float = 8.0) -> float | None:
    """One GPU load reading (0-100) right now, or None if Windows has no GPU counters."""
    try:
        out = subprocess.run(["typeperf", GPU_COUNTER, "-sc", "2"], capture_output=True, text=True,
                             timeout=timeout, creationflags=NO_WINDOW).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    vals = lagcheck.parse_gpu(out)
    return vals[-1] if vals else None


class CpuMeter:
    """CPU load since the last reading, with private state.

    psutil.cpu_percent(interval=None) shares one global "last reading" across the whole program, so every
    caller shrinks everyone else's measuring window (giving tiny, jumpy numbers that don't match Task
    Manager). This keeps its own baseline and only moves it once at least `min_span` seconds have passed.
    """

    def __init__(self, min_span: float = 1.0):
        self.min_span = min_span
        self._lock = threading.Lock()
        self._base = psutil.cpu_times()
        self._t = time.monotonic()
        self._last = 0.0

    def read(self) -> float:
        with self._lock:
            now, cur = time.monotonic(), psutil.cpu_times()
            if now - self._t >= self.min_span:
                total = sum(cur) - sum(self._base)
                idle = (cur.idle + getattr(cur, "iowait", 0.0)) - (self._base.idle + getattr(self._base, "iowait", 0.0))
                if total > 0:
                    self._last = max(0.0, min(100.0, 100.0 * (total - idle) / total))
                self._base, self._t = cur, now
            return self._last


CPU = CpuMeter()


class GpuMonitor:
    """Keeps one `typeperf` running and exposes the latest GPU load.

    typeperf fixes its list of GPU engines when it starts, so a game launched later wouldn't be
    counted; we therefore restart it every `refresh` seconds (the previous value is kept until the
    new process reports).
    """

    def __init__(self, refresh: float = 20.0):
        self.refresh = refresh
        self.latest: float | None = None
        self.unavailable = False  # this PC has no GPU counters: don't keep retrying
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        if self.unavailable:
            return
        self._stop.clear()
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _run(self):
        while not self._stop.is_set():
            try:
                proc = subprocess.Popen(["typeperf", GPU_COUNTER, "-si", "1"], stdout=subprocess.PIPE,
                                        stderr=subprocess.DEVNULL, text=True, creationflags=NO_WINDOW)
            except OSError:
                return
            started, cols = time.time(), None
            try:
                for line in proc.stdout:
                    if self._stop.is_set() or time.time() - started > self.refresh:
                        break
                    row = next(csv.reader(io.StringIO(line)), None)
                    if not row or len(row) < 2:
                        continue
                    if cols is None:
                        cols = lagcheck.gpu_columns(row)
                        continue
                    load = lagcheck.gpu_load(cols, row)
                    if load is not None:
                        self.latest = load
            finally:
                proc.kill()
            if not cols and not self._stop.is_set():
                self.latest = None
                self.unavailable = True
                return  # no GPU counters on this PC: stop trying


class DiskUsers:
    """Which programs are reading/writing the disk. Call snapshot(), wait, then top()."""

    def __init__(self):
        # ourselves, and our parent (a PyInstaller exe is a bootloader process plus the real one)
        self.me = {os.getpid(), os.getppid()}
        self._base: dict[int, tuple[str, int]] = {}
        self._t0 = 0.0

    @staticmethod
    def _read() -> dict[int, tuple[str, int]]:
        out = {}
        for p in psutil.process_iter(["name"]):
            try:
                io_ = p.io_counters()
                out[p.pid] = (p.info["name"] or "?", io_.read_bytes + io_.write_bytes)
            except (psutil.Error, OSError):
                continue  # protected process: needs admin, skip
        return out

    def snapshot(self):
        self._base, self._t0 = self._read(), time.time()

    def top(self, n: int = 3, min_mb_s: float = 5.0) -> list[tuple[str, float]]:
        """[(program, MB/s)] busiest first, summed per program name, ignoring ourselves."""
        dt = max(time.time() - self._t0, 0.1)
        now = self._read()
        per: dict[str, float] = {}
        for pid, (name, total) in now.items():
            if pid in self.me or pid not in self._base:
                continue
            delta = total - self._base[pid][1]
            if delta > 0:
                per[name] = per.get(name, 0.0) + delta / dt / 1e6
        ranked = sorted(((k, v) for k, v in per.items() if v >= min_mb_s), key=lambda kv: -kv[1])
        return ranked[:n]
