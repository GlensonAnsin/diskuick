"""diskuick core - keep a storage drive "awake" to avoid idle-wake latency spikes.

Idea: some SSDs (esp. budget DRAM-less SATA ones) stall when they sit idle and then get
a burst of reads (games streaming assets). A light, steady, read-only load keeps the drive
in its active state. This module has the engine (used by the tray app) and a small CLI:

  python diskuick.py bench D     measure read latency after idle gaps, with/without keep-alive
  python diskuick.py run D       keep a drive awake (optionally only while processes run)
  python diskuick.py clean D     delete the probe file

Reads bypass the OS cache (FILE_FLAG_NO_BUFFERING) so they really hit the disk and cause no
flash wear. A probe file is written ONCE (default 256 MB) to <drive>:\\.diskuick\\probe.bin.
Windows only. Standard library only.
"""
import argparse
import collections
import ctypes
import ctypes.wintypes as wt
import mmap
import os
import random
import statistics
import sys
import threading
import time

import sysutil

GENERIC_READ = 0x80000000
FILE_SHARE_ALL = 0x7
OPEN_EXISTING = 3
FILE_FLAG_NO_BUFFERING = 0x20000000
INVALID_HANDLE = wt.HANDLE(-1).value

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, wt.LPVOID, wt.DWORD, wt.DWORD, wt.HANDLE]
k32.CreateFileW.restype = wt.HANDLE
k32.ReadFile.argtypes = [wt.HANDLE, wt.LPVOID, wt.DWORD, ctypes.POINTER(wt.DWORD), wt.LPVOID]
k32.ReadFile.restype = wt.BOOL
k32.SetFilePointerEx.argtypes = [wt.HANDLE, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong), wt.DWORD]
k32.SetFilePointerEx.restype = wt.BOOL
k32.CloseHandle.argtypes = [wt.HANDLE]

ALIGN = 4096
MAX_READ = 1024 * 1024
MB = 1024 * 1024


def normalize_drive(drive: str) -> str:
    letter = drive.strip().rstrip(":\\/").upper()
    if len(letter) != 1 or not letter.isalpha():
        raise ValueError(f"Invalid drive '{drive}'. Use a letter like D or D:")
    return letter


def probe_path(drive: str) -> str:
    return f"{normalize_drive(drive)}:\\.diskuick\\probe.bin"


def ensure_probe(drive: str, size_mb: int) -> str:
    path = probe_path(drive)
    if os.path.exists(path) and os.path.getsize(path) >= size_mb * MB:
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        for _ in range(size_mb):
            f.write(os.urandom(MB))  # random data: can't be compressed away by the controller
        f.flush()
        os.fsync(f.fileno())
    return path


class Reader:
    """Unbuffered reader. One instance per thread (owns its handle + buffer)."""

    def __init__(self, path: str):
        self.h = k32.CreateFileW(path, GENERIC_READ, FILE_SHARE_ALL, None,
                                 OPEN_EXISTING, FILE_FLAG_NO_BUFFERING, None)
        if self.h == INVALID_HANDLE or self.h is None:
            raise OSError(f"Cannot open {path}: error {ctypes.get_last_error()}")
        self.size = os.path.getsize(path) // ALIGN * ALIGN
        self._buf = mmap.mmap(-1, MAX_READ)  # page-aligned, as NO_BUFFERING requires
        self._addr = ctypes.addressof(ctypes.c_char.from_buffer(self._buf))
        self._pos = 0

    def read_at(self, offset: int, length: int) -> float:
        """Read `length` bytes at `offset`; returns latency in ms."""
        t0 = time.perf_counter()
        if not k32.SetFilePointerEx(self.h, offset, None, 0):
            raise OSError(f"seek failed: {ctypes.get_last_error()}")
        got = wt.DWORD(0)
        if not k32.ReadFile(self.h, self._addr, length, ctypes.byref(got), None):
            raise OSError(f"read failed: {ctypes.get_last_error()}")
        return (time.perf_counter() - t0) * 1000

    def random_read(self, length=ALIGN) -> float:
        off = random.randrange(0, (self.size - length) // ALIGN) * ALIGN
        return self.read_at(off, length)

    def seq_read(self, length) -> float:
        if self._pos + length > self.size:
            self._pos = 0
        lat = self.read_at(self._pos, length)
        self._pos += length
        return lat

    def close(self):
        k32.CloseHandle(self.h)


# pattern name -> (read function, default sleep interval seconds)
PATTERNS = {
    "random": (lambda r: r.random_read(ALIGN), 0.10),      # tiny 4K random read ~10/s
    "seq": (lambda r: r.seq_read(128 * 1024), 0.05),       # 128K sequential ~20/s
    "heavy": (lambda r: r.seq_read(MAX_READ), 0.0),        # continuous, HD Tune-like
}
PATTERN_RANK = {"random": 0, "seq": 1, "heavy": 2}
# a single read slower than this counts as a "stall" (ms), per pattern
STALL_MS = {"random": 60.0, "seq": 80.0, "heavy": 200.0}
# The first reads after start-up often compete with the probe file's own flush to disk, so
# they're ignored (not graphed, not counted as stalls) for this long.
WARMUP_S = 3.0


class KeepAlive(threading.Thread):
    """Reads from the probe file in the background and records per-second latency."""

    def __init__(self, path: str, pattern: str, interval: float | None,
                 label: str = "", on_stall=None):
        super().__init__(daemon=True)
        self.path, self.pattern, self.label, self.on_stall = path, pattern, label, on_stall
        fn, default = PATTERNS[pattern]
        self.fn, self.interval = fn, default if interval is None else interval
        self.stall_ms = STALL_MS[pattern]
        self._halt = threading.Event()
        self.reads = 0
        self.error: str | None = None
        self.history = collections.deque(maxlen=600)  # (second, max_ms, avg_ms)
        self._b = [0, 0.0, 0.0, 0]  # bucket: second, max, sum, n

    def _record(self, now: float, lat: float):
        sec = int(now)
        b = self._b
        if sec != b[0]:
            if b[3]:
                self.history.append((b[0], b[1], b[2] / b[3]))
            self._b = b = [sec, 0.0, 0.0, 0]
        b[1] = max(b[1], lat)
        b[2] += lat
        b[3] += 1

    def run(self):
        try:
            r = Reader(self.path)
        except OSError as e:
            self.error = str(e)
            return
        started = time.time()
        try:
            while not self._halt.is_set():
                lat = self.fn(r)
                now = time.time()
                self.reads += 1
                if now - started >= WARMUP_S:
                    self._record(now, lat)
                    if lat > self.stall_ms and self.on_stall:
                        self.on_stall(self.label, now, lat)
                if self.interval:
                    self._halt.wait(self.interval)
        except OSError as e:
            self.error = str(e)
        finally:
            r.close()

    def stop(self):
        self._halt.set()
        self.join(timeout=3)


# ------------------------------------------------------------ benchmark -----
def stats(lat):
    s = sorted(lat)
    p95 = s[min(len(s) - 1, int(len(s) * 0.95))]
    return statistics.mean(s), statistics.median(s), p95, s[-1]


def measure(path: str, n: int, gap: float, on_tick=None, cancel: threading.Event | None = None):
    """n random 4K reads, each preceded by `gap` seconds of idle. Returns latencies (ms)."""
    r = Reader(path)
    try:
        lat = []
        for i in range(n):
            if cancel is not None:
                if cancel.wait(gap):
                    return lat
            else:
                time.sleep(gap)
            lat.append(r.random_read())
            if on_tick:
                on_tick((i + 1) / n)
        return lat
    finally:
        r.close()


def run_bench(path: str, reads: int = 15, gap: float = 2.0, patterns=None,
              progress=None, cancel: threading.Event | None = None):
    """Idle-latency test without and with each keep-alive pattern.

    Returns [(name, (avg, median, p95, max)), ...] (first row is 'none'), or None if cancelled.
    progress(fraction, text) is called as it goes.
    """
    steps = [None] + list(patterns or PATTERNS)
    rows = []
    for i, pat in enumerate(steps):
        if cancel is not None and cancel.is_set():
            return None
        label = "no keep-alive" if pat is None else f"keep-alive '{pat}'"
        if progress:
            progress(i / len(steps), f"Testing {label}...")
        ka = None
        if pat:
            ka = KeepAlive(path, pat, None)
            ka.start()
            time.sleep(1.5)  # let it ramp up
        try:
            lat = measure(path, reads, gap,
                          on_tick=(lambda f, i=i: progress((i + f) / len(steps), f"Testing {label}...")
                                   if progress else None),
                          cancel=cancel)
        finally:
            if ka:
                ka.stop()
        if cancel is not None and cancel.is_set():
            return None
        rows.append((pat or "none", stats(lat)))
    if progress:
        progress(1.0, "Done")
    return rows


def recommend(rows) -> dict:
    """Pick the lightest pattern that clearly helps.

    Returns {'pattern': str|None, 'baseline_p95': float, 'message_key': str}
    message_key is one of: 'helps', 'no_stalls', 'no_help'.
    """
    base = rows[0][1][2]  # p95 of 'none'
    for name, (_avg, _med, p95, _mx) in rows[1:]:  # ordered light -> heavy
        if base - p95 >= 3.0 and p95 <= base * 0.6:
            return {"pattern": name, "baseline_p95": base, "message_key": "helps"}
    if base < 10.0:
        return {"pattern": None, "baseline_p95": base, "message_key": "no_stalls"}
    return {"pattern": None, "baseline_p95": base, "message_key": "no_help"}


# ----------------------------------------------------------------- CLI ------
def cmd_bench(a):
    drive = normalize_drive(a.drive)
    print(f"Preparing probe file on {drive}: ...")
    path = ensure_probe(drive, a.size)
    print(f"Measuring 4K random-read latency: {a.reads} reads, {a.gap}s idle before each.\n")
    last = [""]

    def progress(_frac, text):
        if text != last[0]:
            last[0] = text
            print(f"  {text}", flush=True)

    rows = run_bench(path, a.reads, a.gap, a.patterns, progress=progress)
    print(f"{'keep-alive':<12}{'avg ms':>9}{'median':>9}{'p95':>9}{'max':>9}")
    for name, (avg, med, p95, mx) in rows:
        print(f"{name:<12}{avg:>9.2f}{med:>9.2f}{p95:>9.2f}{mx:>9.2f}")
    rec = recommend(rows)
    print({"helps": f"\nRecommended: '{rec['pattern']}'.",
           "no_stalls": "\nNo idle stalls detected on this drive.",
           "no_help": "\nStalls found but keep-alive did not clearly help."}[rec["message_key"]])


def cmd_run(a):
    drive = normalize_drive(a.drive)
    path = ensure_probe(drive, a.size)
    targets = {p.lower() for p in a.process}
    ka = None
    print(f"diskuick running on {drive}: pattern={a.pattern}"
          + (f", watching: {', '.join(sorted(targets))}" if targets else ", always on")
          + ". Ctrl+C to quit.")
    try:
        while True:
            want = not targets or bool(targets & sysutil.running_exes())
            if want and ka is None:
                ka = KeepAlive(path, a.pattern, a.interval, drive)
                ka.start()
                print(time.strftime("[%H:%M:%S]"), "keep-alive ON")
            elif not want and ka is not None:
                ka.stop()
                ka = None
                print(time.strftime("[%H:%M:%S]"), "keep-alive OFF")
            time.sleep(3 if targets else 1)
    except KeyboardInterrupt:
        pass
    finally:
        if ka:
            ka.stop()


def cmd_clean(a):
    path = probe_path(a.drive)
    if os.path.exists(path):
        os.remove(path)
        try:
            os.rmdir(os.path.dirname(path))
        except OSError:
            pass
        print("Removed", path)
    else:
        print("Nothing to remove.")


def main():
    p = argparse.ArgumentParser(description="Keep a drive awake to avoid idle latency spikes.")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("drive", help="drive letter, e.g. D")
        sp.add_argument("--size", type=int, default=256, help="probe file size in MB (default 256)")

    b = sub.add_parser("bench", help="measure latency with/without keep-alive")
    common(b)
    b.add_argument("--reads", type=int, default=15)
    b.add_argument("--gap", type=float, default=2.0, help="idle seconds before each measured read")
    b.add_argument("--patterns", nargs="+", default=list(PATTERNS), choices=list(PATTERNS))
    b.set_defaults(fn=cmd_bench)

    r = sub.add_parser("run", help="keep the drive awake")
    common(r)
    r.add_argument("--pattern", default="random", choices=list(PATTERNS))
    r.add_argument("--interval", type=float, default=None, help="seconds between reads (override)")
    r.add_argument("--process", nargs="*", default=[], help="only run while these exes run")
    r.set_defaults(fn=cmd_run)

    c = sub.add_parser("clean", help="delete the probe file")
    c.add_argument("drive")
    c.set_defaults(fn=cmd_clean)

    a = p.parse_args()
    try:
        a.fn(a)
    except ValueError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
