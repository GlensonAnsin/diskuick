"""Small Windows helpers (ctypes only): processes, focus, power, drives."""
import ctypes
import ctypes.wintypes as wt
import os

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_u32 = ctypes.WinDLL("user32", use_last_error=True)
_INVALID = wt.HANDLE(-1).value


class _PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t), ("th32ModuleID", wt.DWORD),
                ("cntThreads", wt.DWORD), ("th32ParentProcessID", wt.DWORD),
                ("pcPriClassBase", ctypes.c_long), ("dwFlags", wt.DWORD),
                ("szExeFile", ctypes.c_wchar * 260)]


_k32.CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]
_k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
for _fn in (_k32.Process32FirstW, _k32.Process32NextW):
    _fn.argtypes = [wt.HANDLE, ctypes.POINTER(_PROCESSENTRY32W)]
    _fn.restype = wt.BOOL
_k32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
_k32.OpenProcess.restype = wt.HANDLE
_k32.QueryFullProcessImageNameW.argtypes = [wt.HANDLE, wt.DWORD, wt.LPWSTR, ctypes.POINTER(wt.DWORD)]
_k32.QueryFullProcessImageNameW.restype = wt.BOOL
_k32.CloseHandle.argtypes = [wt.HANDLE]


def running_exes() -> set[str]:
    """Lower-case names of all running processes (fast, no subprocess)."""
    snap = _k32.CreateToolhelp32Snapshot(0x2, 0)
    if snap in (None, _INVALID):
        return set()
    out = set()
    try:
        e = _PROCESSENTRY32W()
        e.dwSize = ctypes.sizeof(e)
        ok = _k32.Process32FirstW(snap, ctypes.byref(e))
        while ok:
            out.add(e.szExeFile.lower())
            ok = _k32.Process32NextW(snap, ctypes.byref(e))
    finally:
        _k32.CloseHandle(snap)
    return out


def _exe_of_pid(pid: int) -> str | None:
    h = _k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return None
    try:
        buf, n = ctypes.create_unicode_buffer(520), wt.DWORD(520)
        if _k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
            return os.path.basename(buf.value).lower()
    finally:
        _k32.CloseHandle(h)
    return None


def foreground_exe() -> str | None:
    """Exe name of the window that currently has focus."""
    hwnd = _u32.GetForegroundWindow()
    if not hwnd:
        return None
    pid = wt.DWORD(0)
    _u32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return _exe_of_pid(pid.value) if pid.value else None


class _SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [("ACLineStatus", ctypes.c_ubyte), ("BatteryFlag", ctypes.c_ubyte),
                ("BatteryLifePercent", ctypes.c_ubyte), ("SystemStatusFlag", ctypes.c_ubyte),
                ("BatteryLifeTime", wt.DWORD), ("BatteryFullLifeTime", wt.DWORD)]


def on_battery() -> bool:
    """True only when definitely running on battery (desktops always return False)."""
    s = _SYSTEM_POWER_STATUS()
    if not _k32.GetSystemPowerStatus(ctypes.byref(s)):
        return False
    return s.ACLineStatus == 0


HIDDEN_EXES = {"explorer.exe", "applicationframehost.exe", "textinputhost.exe", "systemsettings.exe",
               "searchhost.exe", "startmenuexperiencehost.exe", "shellexperiencehost.exe",
               "diskuick.exe", "python.exe", "pythonw.exe", "taskmgr.exe", "dwm.exe"}


def visible_window_exes() -> list[str]:
    """Programs that currently have a visible window (likely games/apps)."""
    names: set[str] = set()

    @ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        if _u32.IsWindowVisible(hwnd) and _u32.GetWindowTextLengthW(hwnd) > 0:
            pid = wt.DWORD(0)
            _u32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            n = _exe_of_pid(pid.value)
            if n:
                names.add(n)
        return True

    _u32.EnumWindows(cb, 0)
    return sorted(names - HIDDEN_EXES)


def drive_choices() -> dict[str, str]:
    """{display text: letter} for fixed/removable drives, e.g. 'E:  ·  Games  ·  465 GB'."""
    out, mask = {}, _k32.GetLogicalDrives()
    for i in range(26):
        if not mask & (1 << i):
            continue
        letter, root = chr(65 + i), f"{chr(65 + i)}:\\"
        if _k32.GetDriveTypeW(root) not in (2, 3):
            continue
        buf = ctypes.create_unicode_buffer(261)
        _k32.GetVolumeInformationW(root, buf, 261, None, None, None, None, 0)
        total = ctypes.c_ulonglong(0)
        _k32.GetDiskFreeSpaceExW(root, None, ctypes.byref(total), None)
        parts = [f"{letter}:", buf.value or "Local Disk"]
        if total.value:
            parts.append(f"{total.value / 1e9:.0f} GB")
        out["  ·  ".join(parts)] = letter
    return out
