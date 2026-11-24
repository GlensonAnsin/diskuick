"""'Why is my game lagging?' - samples real disk latency, CPU and RAM for a short while.

Disk latency comes from Windows' own performance counter (\\PhysicalDisk\\Avg. Disk sec/Read),
i.e. what your *game* actually experiences - not our probe file. CPU/RAM come from psutil.
GPU load comes from Windows' "GPU Engine" counters (all vendors). Network is only checked when
the user sets a target host.
Results are indicative, not a diagnosis.
"""
import csv
import io
import re
import subprocess
import threading
import time

NO_WINDOW = 0x08000000
DISK_STALL_MS = 50.0
NET_SPIKE_MS = 100.0


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


_GPU_RE = re.compile(r"GPU Engine\(pid_\d+_(luid_\w+?)_phys_\d+_(eng_\d+)_engtype_(\w+?)\)")


def gpu_columns(header: list[str]) -> dict[int, tuple[str, str]]:
    """typeperf header row -> {column: (gpu id, engine id)} for the 3D/Compute engines only."""
    cols = {}
    for i, name in enumerate(header):
        m = _GPU_RE.search(name)
        if m and (m.group(3).startswith("3D") or m.group(3).startswith("Compute")):
            cols[i] = (m.group(1), m.group(2))
    return cols


def gpu_loads(cols: dict, row: list[str]) -> dict[str, float]:
    """One data row -> {gpu id: load 0-100}: summed over processes per engine, busiest engine wins."""
    engines: dict[tuple, float] = {}
    for i, key in cols.items():
        try:
            engines[key] = engines.get(key, 0.0) + float(row[i])
        except (ValueError, IndexError):
            continue
    out: dict[str, float] = {}
    for (gpu, _), v in engines.items():
        out[gpu] = max(out.get(gpu, 0.0), min(v, 100.0))
    return out


def gpu_load(cols: dict, row: list[str]) -> float | None:
    """Like gpu_loads but a single number: the busiest GPU right now (None if the row had no data)."""
    loads = gpu_loads(cols, row)
    return max(loads.values()) if loads else None


def parse_gpu(text: str) -> list[float] | None:
    """typeperf CSV of the GPU Engine counters -> per-second load (0-100) of the busiest GPU.

    Instances look like pid_<pid>_luid_<luid>_phys_<n>_eng_<i>_engtype_<type>. Load is summed over
    processes per engine and the busiest 3D/Compute engine counts as the GPU's load (like Task
    Manager). With several GPUs we report the one that worked hardest.
    """
    rows = [r for r in csv.reader(io.StringIO(text)) if r and len(r) > 1]
    if len(rows) < 2:
        return None
    cols = gpu_columns(rows[0])
    if not cols:
        return None
    per_gpu: dict[str, list[float]] = {}
    for r in rows[1:]:
        for gpu, v in gpu_loads(cols, r).items():
            per_gpu.setdefault(gpu, []).append(v)
    if not per_gpu:
        return None
    return max(per_gpu.values(), key=lambda xs: sum(xs) / len(xs))


def analyze(disk_ms, cpu, ram, gpu=None, net=None, hogs=None) -> list[tuple[str, str]]:
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
    if gpu:
        avg = sum(gpu) / len(gpu)
        if avg >= 95:
            f.append(("bad", f"GPU was maxed out (average {avg:.0f}%). The graphics card is probably your "
                             "bottleneck: try lower graphics settings or resolution."))
        elif avg >= 85:
            f.append(("warn", f"GPU was very busy (average {avg:.0f}%)."))
        else:
            f.append(("ok", f"GPU was fine (average {avg:.0f}%)."))
    if net:
        got = [v for v in net if v is not None]
        loss = 100.0 * (len(net) - len(got)) / len(net)
        avg = sum(got) / len(got) if got else 0.0
        spikes = sum(1 for v in got if v >= NET_SPIKE_MS)
        if not got:
            f.append(("bad", "The network target never answered, so network lag couldn't be measured. "
                             "Check the host name in Settings."))
        elif loss >= 5:
            f.append(("bad", f"Network packet loss {loss:.0f}% (average ping {avg:.0f} ms). "
                             "That causes rubber-banding and lag in online games."))
        elif spikes >= 3 or avg >= NET_SPIKE_MS:
            f.append(("warn", f"Network ping spikes: average {avg:.0f} ms, worst {max(got):.0f} ms."))
        else:
            f.append(("ok", f"Network was fine (average ping {avg:.0f} ms, {loss:.0f}% loss)."))
    if hogs:
        names = ", ".join(f"{n} ({mb:.0f} MB/s)" for n, mb in hogs)
        f.append(("warn", f"Other programs were using the drive heavily: {names}. "
                          "Closing or pausing them while you play may help."))
    if all(lv == "ok" for lv, _ in f):
        measured = ["disk", "CPU", "RAM"] + (["GPU"] if gpu else []) + (["network"] if net else [])
        unmeasured = [x for x, have in (("GPU", gpu), ("network", net)) if not have]
        causes = unmeasured + ["the game itself"]
        cause_txt = causes[0] if len(causes) == 1 else ", ".join(causes[:-1]) + " or " + causes[-1]
        note = f" ({' and '.join(unmeasured)} {'wasn' if len(unmeasured) == 1 else 'weren'}'t measured here)"             if unmeasured else ""
        f.append(("warn", f"Nothing wrong with {', '.join(measured[:-1])} or {measured[-1]}. "
                          f"The lag may come from {cause_txt}{note}."))
    return f


def mark_verdict(m: dict) -> dict:
    """Plain-language reading of a hotkey 'lag mark' snapshot (disk/CPU/RAM/GPU/net at that moment)."""
    worst = max((v for v in m.get("drives", {}).values() if v is not None), default=None)
    if worst is not None and worst >= DISK_STALL_MS:
        return {"level": "bad", "text": f"The drive was slow right then (a read took {worst:.0f} ms)."}
    if (m.get("gpu") or 0) >= 95:
        return {"level": "bad", "text": f"The GPU was maxed out ({m['gpu']:.0f}%)."}
    if m.get("cpu", 0) >= 90:
        return {"level": "bad", "text": f"The CPU was maxed out ({m['cpu']:.0f}%)."}
    if m.get("ram", 0) >= 92:
        return {"level": "warn", "text": f"Memory was nearly full ({m['ram']:.0f}%)."}
    if m.get("net_checked") and m.get("net_ms") is None:
        return {"level": "bad", "text": "The network target didn't answer."}
    if (m.get("net_ms") or 0) >= NET_SPIKE_MS:
        return {"level": "warn", "text": f"Network ping was high ({m['net_ms']:.0f} ms)."}
    if m.get("hogs"):
        n, mb = m["hogs"][0]
        return {"level": "warn", "text": f"{n} was using the drive heavily ({mb:.0f} MB/s)."}
    return {"level": "ok", "text": "Nothing stood out at that moment, so the cause is probably the game itself."}


def run_lagcheck(drive: str, seconds: int = 30, on_tick=None, cancel: threading.Event | None = None,
                 net_host: str | None = None):
    """Blocks for `seconds`. Returns {'disk_ms','cpu','ram','gpu','net','hogs','findings'} or None if
    cancelled. `net_host` ("host" or "host:port") turns on the optional network check."""
    import psutil
    import netcheck
    import sysmon
    drive = drive.strip().rstrip(":\\/").upper()[:1]

    def start(counter):
        try:
            return subprocess.Popen(["typeperf", counter, "-si", "1", "-sc", str(seconds)],
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                    creationflags=NO_WINDOW)
        except OSError:
            return None

    proc = start(r"\PhysicalDisk(*)\Avg. Disk sec/Read")
    gproc = start(r"\GPU Engine(*)\Utilization Percentage")
    target = netcheck.parse_target(net_host or "")
    net: list = []
    users = sysmon.DiskUsers()
    users.snapshot()
    cpu, ram = [], []
    psutil.cpu_percent(interval=None)
    for i in range(seconds):
        if cancel is not None and cancel.is_set():
            for p_ in (proc, gproc):
                if p_:
                    p_.kill()
            return None
        t0 = time.time()
        if target:
            net.append(netcheck.rtt_ms(*target, timeout=1.0))
        cpu.append(psutil.cpu_percent(interval=max(0.05, 1.0 - (time.time() - t0))))
        ram.append(psutil.virtual_memory().percent)
        if on_tick:
            on_tick((i + 1) / seconds)
    hogs = users.top()
    disk = gpu = None
    if proc:
        try:
            out, _ = proc.communicate(timeout=10)
            disk = parse_typeperf(out, drive)
        except subprocess.TimeoutExpired:
            proc.kill()
    if gproc:
        try:
            out, _ = gproc.communicate(timeout=10)
            gpu = parse_gpu(out)
        except subprocess.TimeoutExpired:
            gproc.kill()
    net_series = net if target else None
    return {"disk_ms": disk, "cpu": cpu, "ram": ram, "gpu": gpu, "net": net_series, "hogs": hogs,
            "findings": analyze(disk, cpu, ram, gpu, net_series, hogs)}
