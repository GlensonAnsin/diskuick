"""Disk cleanup: remove only well-known, regenerable junk.

Deliberately limited to fixed categories (temp files, caches, crash dumps, the Recycle Bin). Nothing the
user chose by hand is deleted here, and every delete is confined to its category's folder.
"""
import ctypes
import glob
import os
import stat
import threading
import time
from dataclasses import dataclass, field

REPARSE = 0x400
MIN_AGE = 3600  # leave temp files touched in the last hour alone: an installer may be using them


def _local(*parts: str) -> str:
    return os.path.join(os.environ.get("LOCALAPPDATA", ""), *parts)


def _browser_dirs() -> list[str]:
    out = []
    for base in (_local("Google", "Chrome", "User Data"), _local("Microsoft", "Edge", "User Data"),
                 _local("BraveSoftware", "Brave-Browser", "User Data")):
        for profile in ("Default", "Profile 1", "Profile 2"):
            for sub in ("Cache", "Code Cache", "GPUCache"):
                out.append(os.path.join(base, profile, sub))
    return out


@dataclass
class Category:
    key: str
    title: str
    hint: str
    dirs: list[str] = field(default_factory=list)      # folders whose contents are removed
    globs: list[str] = field(default_factory=list)     # individual files matched by a pattern
    min_age: int = 0
    default: bool = False
    recycle_bin: bool = False
    needs_admin: bool = False


def categories() -> list[Category]:
    win = os.environ.get("SystemRoot", r"C:\Windows")
    return [
        Category("user_temp", "Temporary files", "Left behind by programs in your Temp folder.",
                 dirs=[os.environ.get("TEMP", "")], min_age=MIN_AGE, default=True),
        Category("win_temp", "Windows temporary files", "Windows' own Temp folder. Run as admin to clear all of it.",
                 dirs=[os.path.join(win, "Temp")], min_age=MIN_AGE, default=True, needs_admin=True),
        Category("thumbs", "Thumbnail cache", "Explorer rebuilds the picture previews when needed.",
                 globs=[_local("Microsoft", "Windows", "Explorer", "thumbcache_*.db"),
                        _local("Microsoft", "Windows", "Explorer", "iconcache_*.db")], default=True),
        Category("crash", "Crash dumps and error reports", "Diagnostic files from programs that crashed.",
                 dirs=[_local("CrashDumps"), _local("Microsoft", "Windows", "WER")], default=True),
        Category("browser", "Browser caches", "Chrome, Edge and Brave caches. Sites load a little slower once.",
                 dirs=_browser_dirs(), globs=[_local("Mozilla", "Firefox", "Profiles", "*", "cache2", "entries", "*")]),
        Category("shader", "Shader caches", "GPU shader caches. Games may stutter briefly the next time they start "
                 "while these are rebuilt.",
                 dirs=[_local("D3DSCache"), _local("NVIDIA", "DXCache"), _local("NVIDIA", "GLCache"),
                       _local("AMD", "DxCache")]),
        Category("recycle", "Recycle Bin", "Permanently deletes what is in the Recycle Bin.", recycle_bin=True),
    ]


# ------------------------------------------------------------------ sizing ----
def _is_reparse(st) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & REPARSE)


def dir_size(root: str, min_age: int = 0, now: float | None = None) -> tuple[int, int]:
    """(bytes, files) under root that a cleanup would remove."""
    now = time.time() if now is None else now
    total = files = 0
    stack = [root]
    while stack:
        d = stack.pop()
        try:
            it = os.scandir(d)
        except OSError:
            continue
        with it:
            for e in it:
                try:
                    st = e.stat(follow_symlinks=False)
                    if e.is_dir(follow_symlinks=False):
                        if not _is_reparse(st):
                            stack.append(e.path)
                    elif now - st.st_mtime >= min_age:
                        total += st.st_size
                        files += 1
                except OSError:
                    continue
    return total, files


def _recycle_info() -> tuple[int, int]:
    class RBInfo(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_ulong), ("size", ctypes.c_longlong), ("items", ctypes.c_longlong)]
    info = RBInfo()
    info.cbSize = ctypes.sizeof(RBInfo)
    try:
        if ctypes.windll.shell32.SHQueryRecycleBinW(None, ctypes.byref(info)) == 0:
            return int(info.size), int(info.items)
    except (OSError, AttributeError):
        pass
    return 0, 0


def measure(cat: Category, now: float | None = None) -> tuple[int, int]:
    """(bytes, files) this category would free."""
    if cat.recycle_bin:
        return _recycle_info()
    total = files = 0
    for d in cat.dirs:
        if d and os.path.isdir(d):
            b, n = dir_size(d, cat.min_age, now)
            total, files = total + b, files + n
    for pattern in cat.globs:
        for p in glob.glob(pattern):
            try:
                st = os.lstat(p)
                if stat.S_ISREG(st.st_mode):
                    total, files = total + st.st_size, files + 1
            except OSError:
                continue
    return total, files


# ---------------------------------------------------------------- cleaning ----
def _remove_file(path: str) -> int | None:
    """Delete one file; return its size, or None if it could not be removed (e.g. in use)."""
    try:
        size = os.lstat(path).st_size
        try:
            os.remove(path)
        except PermissionError:
            os.chmod(path, stat.S_IWRITE)
            os.remove(path)
        return size
    except OSError:
        return None


def clean_dir(root: str, min_age: int = 0, cancel: threading.Event | None = None,
              now: float | None = None) -> tuple[int, int]:
    """Delete everything inside `root` (never `root` itself, never through a junction/symlink).
    Returns (bytes freed, files removed). Files that are in use are skipped silently."""
    now = time.time() if now is None else now
    freed = removed = 0
    dirs: list[str] = []
    stack = [root]
    while stack:
        if cancel is not None and cancel.is_set():
            break
        d = stack.pop()
        try:
            it = os.scandir(d)
        except OSError:
            continue
        with it:
            for e in it:
                try:
                    st = e.stat(follow_symlinks=False)
                    if e.is_dir(follow_symlinks=False):
                        if not _is_reparse(st):
                            stack.append(e.path)
                            dirs.append(e.path)
                    elif now - st.st_mtime >= min_age:
                        got = _remove_file(e.path)
                        if got is not None:
                            freed += got
                            removed += 1
                except OSError:
                    continue
    for d in sorted(dirs, key=len, reverse=True):   # empty folders, deepest first; non-empty ones just fail
        try:
            os.rmdir(d)
        except OSError:
            pass
    return freed, removed


def _empty_recycle_bin() -> tuple[int, int]:
    size, items = _recycle_info()
    try:
        # SHERB_NOCONFIRMATION | SHERB_NOPROGRESSUI | SHERB_NOSOUND
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x7)
    except (OSError, AttributeError):
        return 0, 0
    return size, items


def clean(cat: Category, cancel: threading.Event | None = None) -> tuple[int, int]:
    """Clean one category; returns (bytes freed, files removed)."""
    if cat.recycle_bin:
        return _empty_recycle_bin()
    freed = removed = 0
    for d in cat.dirs:
        if d and os.path.isdir(d):
            b, n = clean_dir(d, cat.min_age, cancel)
            freed, removed = freed + b, removed + n
    for pattern in cat.globs:
        for p in glob.glob(pattern):
            got = _remove_file(p)
            if got is not None:
                freed, removed = freed + got, removed + 1
    return freed, removed


# ------------------------------------------------- delete one chosen item ----
FOF_NOCONFIRMATION, FOF_ALLOWUNDO, FOF_NOERRORUI, FOF_WANTNUKEWARNING = 0x10, 0x40, 0x400, 0x4000
_ROOT_FILES = {"pagefile.sys", "hiberfil.sys", "swapfile.sys"}
_SYSTEM_TOP = {"windows", "recovery", "system volume information", "$recycle.bin", "boot", "efi"}


def protected_reason(path: str) -> str | None:
    """Why this path must never be deleted from the analyzer, or None if it is fine to offer."""
    norm = lambda s: os.path.normcase(os.path.abspath(s)).rstrip("\\/")
    if not os.path.splitdrive(path)[1].strip("\\/"):     # "C:" or "C:\": a whole drive (abspath("C:") is the cwd)
        return "a whole drive"
    p = norm(path)
    drive, rest = os.path.splitdrive(p)
    parts = [x for x in rest.replace("/", "\\").split("\\") if x]
    if not parts:
        return "a whole drive"
    if parts[0] in _SYSTEM_TOP or parts[0].startswith("$"):
        return "a Windows system folder"
    sysroot = norm(os.environ.get("SystemRoot", r"C:\Windows"))
    if p == sysroot or p.startswith(sysroot + "\\"):
        return "a Windows system folder"
    if len(parts) == 1 and parts[0] in _ROOT_FILES:
        return "a Windows system file"
    keep = {norm(os.environ.get(v, "")) for v in ("ProgramFiles", "ProgramFiles(x86)", "ProgramW6432", "ProgramData",
                                                  "USERPROFILE", "PUBLIC", "ALLUSERSPROFILE") if os.environ.get(v)}
    users = norm(os.path.join(os.environ.get("SystemDrive", "C:") + "\\", "Users"))
    if p == users or p in keep or os.path.dirname(p) == users:   # also each user's profile folder itself
        return "a system or user-profile folder"
    pf = norm(os.environ.get("ProgramFiles", r"C:\Program Files"))
    if p.startswith(os.path.join(pf, "windowsapps")):
        return "a Windows system folder"
    return None


class _ShFileOp(ctypes.Structure):
    _fields_ = [("hwnd", ctypes.c_void_p), ("wFunc", ctypes.c_uint), ("pFrom", ctypes.c_void_p),
                ("pTo", ctypes.c_void_p), ("fFlags", ctypes.c_ushort), ("aborted", ctypes.c_int),
                ("mappings", ctypes.c_void_p), ("title", ctypes.c_void_p)]


def recycle(path: str) -> bool:
    """Move one file or folder to the Recycle Bin (restorable). Windows warns if it is too big for the
    bin and would be deleted for good. Refuses protected paths. Returns True if the item is gone."""
    if protected_reason(path) or not os.path.lexists(path):
        return False
    buf = ctypes.create_unicode_buffer(os.path.abspath(path) + "\0\0")   # the API wants a double-NUL list
    op = _ShFileOp()
    op.wFunc = 3  # FO_DELETE
    op.pFrom = ctypes.addressof(buf)
    op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_NOERRORUI | FOF_WANTNUKEWARNING
    try:
        rc = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    except (OSError, AttributeError):
        return False
    return rc == 0 and not op.aborted and not os.path.lexists(path)
