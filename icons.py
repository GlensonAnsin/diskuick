"""Game icons: finds a game's .exe on disk and pulls the icon Windows shows for it (no extra files)."""
import ctypes
import ctypes.wintypes as wt
import os

import psutil
from PIL import Image

_u32 = ctypes.WinDLL("user32", use_last_error=True)
_g32 = ctypes.WinDLL("gdi32", use_last_error=True)

_cache: dict[tuple[str, int], Image.Image | None] = {}


class _ICONINFO(ctypes.Structure):
    _fields_ = [("fIcon", wt.BOOL), ("xHotspot", wt.DWORD), ("yHotspot", wt.DWORD),
                ("hbmMask", wt.HBITMAP), ("hbmColor", wt.HBITMAP)]


class _BMIH(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG), ("biPlanes", wt.WORD),
                ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                ("biClrImportant", wt.DWORD)]


_u32.PrivateExtractIconsW.argtypes = [wt.LPCWSTR, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.POINTER(wt.HICON), ctypes.POINTER(wt.UINT), wt.UINT, wt.UINT]
_u32.PrivateExtractIconsW.restype = wt.UINT
_u32.GetIconInfo.argtypes = [wt.HICON, ctypes.POINTER(_ICONINFO)]
_u32.GetDC.argtypes = [wt.HWND]
_u32.GetDC.restype = wt.HDC
_u32.ReleaseDC.argtypes = [wt.HWND, wt.HDC]
_u32.DestroyIcon.argtypes = [wt.HICON]
_g32.GetDIBits.argtypes = [wt.HDC, wt.HBITMAP, wt.UINT, wt.UINT, ctypes.c_void_p, ctypes.c_void_p, wt.UINT]
_g32.DeleteObject.argtypes = [wt.HGDIOBJ]


def _bits(hdc, hbm, w: int, h: int) -> bytes:
    bmi = _BMIH(ctypes.sizeof(_BMIH), w, -h, 1, 32, 0, 0, 0, 0, 0, 0)  # negative height = top-down
    buf = ctypes.create_string_buffer(w * h * 4)
    _g32.GetDIBits(hdc, hbm, 0, h, buf, ctypes.byref(bmi), 0)
    return buf.raw


def extract(path: str, size: int = 48) -> Image.Image | None:
    """The icon of an .exe as an RGBA image, or None if it has none / can't be read."""
    key = (path.lower(), size)
    if key not in _cache:
        try:
            _cache[key] = _extract(path, size)
        except Exception:
            _cache[key] = None
    return _cache[key]


def _extract(path: str, size: int) -> Image.Image | None:
    if not os.path.isfile(path):
        return None
    hicon = wt.HICON()
    if _u32.PrivateExtractIconsW(path, 0, size, size, ctypes.byref(hicon), None, 1, 0) < 1 or not hicon:
        return None
    info = _ICONINFO()
    hdc = _u32.GetDC(None)
    try:
        if not _u32.GetIconInfo(hicon, ctypes.byref(info)) or not info.hbmColor:
            return None
        color = _bits(hdc, info.hbmColor, size, size)
        img = Image.frombuffer("RGBA", (size, size), color, "raw", "BGRA", 0, 1)
        if not any(color[3::4]):          # old-style icon without alpha: use its mask for transparency
            if not info.hbmMask:
                return img.convert("RGB").convert("RGBA")
            mask = _bits(hdc, info.hbmMask, size, size)
            alpha = bytes(0 if mask[i] else 255 for i in range(0, len(mask), 4))
            img.putalpha(Image.frombytes("L", (size, size), alpha))
        return img
    finally:
        for hb in (info.hbmColor, info.hbmMask):
            if hb:
                _g32.DeleteObject(hb)
        _u32.ReleaseDC(None, hdc)
        _u32.DestroyIcon(hicon)


def running_path(exe: str) -> str | None:
    """Full path of a currently running program with this exe name."""
    for p in psutil.process_iter(["name", "exe"]):
        try:
            if (p.info["name"] or "").lower() == exe.lower() and p.info["exe"]:
                return p.info["exe"]
        except (psutil.Error, OSError):
            continue
    return None


def find_in_folder(folder: str, exe: str, max_depth: int = 4) -> str | None:
    """Look for exe somewhere under a game's install folder (a few levels deep)."""
    if not folder or not os.path.isdir(folder):
        return None
    base = folder.rstrip("\\/").count(os.sep)
    for root, dirs, files in os.walk(folder):
        if root.count(os.sep) - base >= max_depth:
            dirs[:] = []
        for f in files:
            if f.lower() == exe.lower():
                return os.path.join(root, f)
    return None


def locate(game: dict) -> str | None:
    """Best known full path of a game's exe: remembered, in its folder, or from the running process."""
    known = game.get("exe_path")
    if known and os.path.isfile(known):
        return known
    return find_in_folder(game.get("path") or "", game["exe"]) or running_path(game["exe"])
