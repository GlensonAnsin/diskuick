"""Optional 'game mode': politely close chosen programs when a game starts, reopen them afterwards.

Safety rules: only programs the user listed; only by asking their windows to close (WM_CLOSE), so
they can show their normal "save changes?" prompt; never force-killed; a built-in block list of
system programs; and only programs that actually closed are reopened later.
"""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import time

import psutil

WM_CLOSE = 0x0010
DETACHED = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
NEVER_CLOSE = {
    "explorer.exe", "csrss.exe", "winlogon.exe", "services.exe", "lsass.exe", "svchost.exe", "system",
    "smss.exe", "wininit.exe", "dwm.exe", "taskmgr.exe", "diskuick.exe", "python.exe", "pythonw.exe",
    "searchhost.exe", "sihost.exe", "ctfmon.exe", "fontdrvhost.exe", "conhost.exe", "cmd.exe",
    "powershell.exe", "windowsterminal.exe", "audiodg.exe",
}
_u32 = ctypes.windll.user32
_WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)


def allowed(exe: str) -> bool:
    exe = (exe or "").strip().lower()
    return bool(exe) and exe not in NEVER_CLOSE


def _find(exes: set[str]) -> list[tuple[int, str, str]]:
    """[(pid, exe name, full path)] of running processes whose name is in `exes`."""
    out = []
    for p in psutil.process_iter(["name", "exe"]):
        try:
            if (p.info["name"] or "").lower() in exes and p.info["exe"]:
                out.append((p.pid, p.info["name"].lower(), p.info["exe"]))
        except (psutil.Error, OSError):
            continue
    return out


def _post_close(pids: set[int]):
    @_WNDENUMPROC
    def cb(hwnd, _):
        pid = wt.DWORD(0)
        _u32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in pids and _u32.IsWindowVisible(hwnd):
            _u32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        return True
    _u32.EnumWindows(cb, 0)


def close_programs(exes, wait: float = 6.0) -> list[str]:
    """Asks the listed programs to close. Returns full paths of those that really exited."""
    wanted = {e.strip().lower() for e in exes if allowed(e)}
    if not wanted:
        return []
    found = _find(wanted)
    if not found:
        return []
    _post_close({pid for pid, _, _ in found})
    deadline = time.time() + wait
    while time.time() < deadline and any(psutil.pid_exists(pid) for pid, _, _ in found):
        time.sleep(0.25)
    closed, seen = [], set()
    for pid, _, path in found:
        if not psutil.pid_exists(pid) and path.lower() not in seen:
            seen.add(path.lower())
            closed.append(path)
    # a program with several processes only counts as closed when none of its processes remain
    still = {name for _, name, _ in _find(wanted)}
    return [p for p in closed if os.path.basename(p).lower() not in still]


def reopen(paths) -> None:
    for path in paths:
        if os.path.isfile(path):
            try:
                subprocess.Popen([path], creationflags=DETACHED, close_fds=True,
                                 cwd=os.path.dirname(path))
            except OSError:
                pass
