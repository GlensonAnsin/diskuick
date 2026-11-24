"""'Why is my game lagging?' - samples real disk latency, CPU and RAM for a short while.

Disk latency comes from Windows' own performance counter (\\PhysicalDisk\\Avg. Disk sec/Read),
i.e. what your *game* actually experiences - not our probe file. CPU/RAM come from psutil.
GPU is not measured. Results are indicative, not a diagnosis.
"""
import csv
import io
import re
import subprocess
import threading

NO_WINDOW = 0x08000000
DISK_STALL_MS = 50.0


def _column_for_drive(header: list[str], drive: str):
    for i, name in enumerate(header):
        m = re.search(r"PhysicalDisk\(([^)]*)\)", name)
        if m and f"{drive}:" in m.group(1).split():
            return i
    return None


def parse_typeperf(text: str, drive: str) -> list[float] | None:
    """typeperf CSV -> per-second read latency in ms for the disk holding `drive` (reads only)."""
    rows = [r for r in csv.reader(io.StringIO(text)) if r and len(r) > 1]
    if len(rows) < 2:
        return None
    col = _column_for_drive(rows[0], drive)
    if col is None:
        return None
    out = []
    for r in rows[1:]:
        try:
            out.append(float(r[col]) * 1000.0)
        except (ValueError, IndexError):
            continue
    return out


def analyze(disk_ms, cpu, ram) -> list[tuple[str, str]]:
    """Pure function: [(level, message)] from the sampled series."""
    f = []
    if disk_ms is None:
        f.append(("warn", "Couldn't read Windows disk counters (they can be missing on non-English "
                          "Windows), so disk latency wasn't measured."))
    else:
        busy = [v for v in disk_ms if v > 0]
        stalls = sum(1 for v in busy if v >= DISK_STALL_MS)
        if not busy:
            f.append(("warn", "The drive did almost no reads during the test. Make sure the game was "
                              "running and loading things while you tested."))
        elif stalls >= 2:
            f.append(("bad", f"Disk stalls: {stalls} second(s) where reads took over {DISK_STALL_MS:.0f} ms "
                             f"(worst {max(busy):.0f} ms). Your drive is a likely cause of lag."))
        elif stalls == 1:
            f.append(("warn", f"One disk hiccup ({max(busy):.0f} ms). Mostly fine, but worth re-testing."))
        else:
            f.append(("ok", f"Disk looks fine: worst read latency {max(busy):.0f} ms."))
    if cpu:
        avg = sum(cpu) / len(cpu)
        if avg >= 90:
            f.append(("bad", f"CPU was maxed out (average {avg:.0f}%). The CPU is probably your bottleneck."))
        elif avg >= 75:
            f.append(("warn", f"CPU was busy (average {avg:.0f}%)."))
        else:
            f.append(("ok", f"CPU was fine (average {avg:.0f}%)."))
    if ram:
        peak = max(ram)
        if peak >= 92:
            f.append(("bad", f"Memory was nearly full ({peak:.0f}%). Windows may be swapping to disk, "
                             "which looks like disk lag. Close other programs."))
        elif peak >= 85:
            f.append(("warn", f"Memory use was high ({peak:.0f}%)."))
        else:
            f.append(("ok", f"Memory was fine (peak {peak:.0f}%)."))
    if all(lv == "ok" for lv, _ in f):
        f.append(("warn", "Nothing wrong with disk, CPU or RAM. The lag may come from the GPU, "
                          "network or the game itself (GPU isn't measured here)."))
    return f


def run_lagcheck(drive: str, seconds: int = 30, on_tick=None, cancel: threading.Event | None = None):
    """Blocks for `seconds`. Returns {'disk_ms','cpu','ram','findings'} or None if cancelled."""
    import psutil
    drive = drive.strip().rstrip(":\\/").upper()[:1]
    try:
        proc = subprocess.Popen(["typeperf", r"\PhysicalDisk(*)\Avg. Disk sec/Read",
                                 "-si", "1", "-sc", str(seconds)],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                creationflags=NO_WINDOW)
    except OSError:
        proc = None
    cpu, ram = [], []
    psutil.cpu_percent(interval=None)
    for i in range(seconds):
        if cancel is not None and cancel.is_set():
            if proc:
                proc.kill()
            return None
        cpu.append(psutil.cpu_percent(interval=1.0))
        ram.append(psutil.virtual_memory().percent)
        if on_tick:
            on_tick((i + 1) / seconds)
    disk = None
    if proc:
        try:
            out, _ = proc.communicate(timeout=10)
            disk = parse_typeperf(out, drive)
        except subprocess.TimeoutExpired:
            proc.kill()
    return {"disk_ms": disk, "cpu": cpu, "ram": ram, "findings": analyze(disk, cpu, ram)}
