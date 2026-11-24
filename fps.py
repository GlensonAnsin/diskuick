"""Live FPS for the overlay, measured from outside the game.

Uses Intel's PresentMon console tool (2.x), which listens to Windows' own frame-present events (ETW).
Nothing is injected into or hooked inside the game, so it does not interact with anti-cheat. Windows only
lets administrators listen to those events, and PresentMon.exe is not bundled: put it next to Diskuick.exe
(or in an `assets` folder, or on PATH).
"""
import collections
import csv
import io
import os
import shutil
import subprocess
import sys
import threading
import time

NO_WINDOW = 0x08000000
FRAME_COLUMNS = ("msbetweenpresents", "frametime")   # PresentMon 1.x / 2.x name for the frame time (ms)
WINDOW = 1.0                                         # seconds of frames averaged into one reading
STALE = 2.0                                          # no frames for this long = not rendering (menu, alt-tab)


def find_presentmon() -> str | None:
    base = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
    for folder in (base, os.path.join(base, "assets")):
        try:
            for name in sorted(os.listdir(folder)):
                if name.lower().startswith("presentmon") and name.lower().endswith(".exe"):
                    return os.path.join(folder, name)
        except OSError:
            continue
    return shutil.which("PresentMon.exe") or shutil.which("PresentMon")


def frame_column(header: list[str]) -> int | None:
    for i, name in enumerate(header):
        if name.strip().lower() in FRAME_COLUMNS:
            return i
    return None


def fps_from_arrivals(arrivals, now: float) -> float | None:
    """Frames per second from the times (seconds) frames were reported, looking at the last WINDOW s."""
    recent = [t for t in arrivals if t >= now - WINDOW]
    if not recent:
        return None
    return len(recent) / WINDOW


def format_fps(fps: float | None) -> str:
    return "FPS  …" if fps is None else f"FPS  {fps:.0f}"


class FpsMonitor:
    """Runs PresentMon for one game process and exposes the latest FPS (None until frames arrive)."""

    def __init__(self, exe_path: str | None = None):
        self.exe_path = exe_path if exe_path is not None else find_presentmon()
        self.target: str | None = None
        self.frames: collections.deque = collections.deque(maxlen=2000)
        self.error: str | None = None
        self._proc: subprocess.Popen | None = None
        self._thread: threading.Thread | None = None

    @property
    def available(self) -> bool:
        return self.exe_path is not None

    def fps(self, now: float | None = None) -> float | None:
        now = time.monotonic() if now is None else now
        if not self.frames or now - self.frames[-1] > STALE:
            return None
        return fps_from_arrivals(list(self.frames), now)

    def track(self, exe: str | None):
        """Measure this game's exe (e.g. "game.exe"); None stops measuring."""
        if exe == self.target and (exe is None or self._alive()):
            return
        self.stop()
        if exe is None or not self.available:
            return
        self.target, self.error = exe, None
        self.frames.clear()
        self._thread = threading.Thread(target=self._run, args=(exe,), daemon=True)
        self._thread.start()

    def _alive(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def stop(self):
        self.target = None
        proc, self._proc = self._proc, None
        if proc is not None:
            try:
                proc.kill()
            except OSError:
                pass
        self.frames.clear()

    def _run(self, exe: str):
        try:
            proc = subprocess.Popen(
                [self.exe_path, "--process_name", exe, "--output_stdout", "--stop_existing_session",
                 "--no_console_stats"],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, text=True,
                creationflags=NO_WINDOW)
        except OSError as e:
            self.error = str(e)
            return
        self._proc = proc
        col = None
        for line in proc.stdout:
            if self.target != exe:
                break
            row = next(csv.reader(io.StringIO(line)), None)
            if not row or len(row) < 2:
                continue
            if col is None:
                col = frame_column(row)
                continue
            self.frames.append(time.monotonic())
        proc.kill()
        if self.target == exe and col is None:
            self.error = "PresentMon produced no output (it needs administrator rights)"
