"""Find installed games from Steam, Epic Games Launcher and GOG Galaxy.

Each result: {"name", "exe", "drive", "source", "path"}. The exe is a best guess (the largest
non-installer .exe in the game folder); the user can remove/replace it in the Games tab.
"""
import glob
import json
import os
import re
import winreg

SKIP_EXE = re.compile(r"(unins|crash|redist|vcredist|dxsetup|setup|install|dotnet|ue4prereq|"
                      r"easyanticheat|beservice|helper|updater|cef|webhelper|notif|report|"
                      r"launcherpatcher|vc_|oalinst|physx)", re.I)
SKIP_DIR = re.compile(r"(redist|directx|_commonredist|engine[\\/]extras|support|__installer|"
                      r"prerequisites|dotnet|vcredist)", re.I)
SKIP_NAMES = ("Steamworks Common Redistributables", "Steam Linux Runtime", "Proton", "Steam Controller")


def guess_exe(folder: str, max_depth: int = 3, max_files: int = 4000) -> str | None:
    """Largest plausible game .exe under `folder` (by file size)."""
    best, best_size, seen = None, -1, 0
    base_depth = folder.rstrip("\\/").count(os.sep)
    for root, dirs, files in os.walk(folder):
        if root.count(os.sep) - base_depth >= max_depth:
            dirs[:] = []
        dirs[:] = [d for d in dirs if not SKIP_DIR.search(d)]
        for f in files:
            seen += 1
            if seen > max_files:
                return best
            if f.lower().endswith(".exe") and not SKIP_EXE.search(f):
                try:
                    size = os.path.getsize(os.path.join(root, f))
                except OSError:
                    continue
                if size > best_size:
                    best, best_size = f, size
    return best


def _game(name, folder, exe, source):
    return {"name": name, "exe": exe.lower(), "drive": folder[:1].upper(), "source": source,
            "path": folder}


# ---------------------------------------------------------------- Steam -----
def steam_libraries() -> list[str]:
    roots = []
    for hive, key, val in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                           (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath")):
        try:
            with winreg.OpenKey(hive, key) as k:
                roots.append(os.path.normpath(winreg.QueryValueEx(k, val)[0]))
        except OSError:
            pass
    libs = []
    for root in roots:
        if root not in libs and os.path.isdir(root):
            libs.append(root)
        vdf = os.path.join(root, "steamapps", "libraryfolders.vdf")
        try:
            with open(vdf, encoding="utf-8", errors="ignore") as f:
                for m in re.finditer(r'"path"\s+"([^"]+)"', f.read()):
                    p = os.path.normpath(m.group(1).replace("\\\\", "\\"))
                    if p not in libs and os.path.isdir(p):
                        libs.append(p)
        except OSError:
            pass
    return libs


def scan_steam_library(lib: str) -> list[dict]:
    out = []
    for acf in glob.glob(os.path.join(lib, "steamapps", "appmanifest_*.acf")):
        try:
            with open(acf, encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            name = re.search(r'"name"\s+"([^"]*)"', txt).group(1)
            inst = re.search(r'"installdir"\s+"([^"]*)"', txt).group(1)
        except (OSError, AttributeError):
            continue
        if name.startswith(SKIP_NAMES):
            continue
        folder = os.path.join(lib, "steamapps", "common", inst)
        if os.path.isdir(folder):
            exe = guess_exe(folder)
            if exe:
                out.append(_game(name, folder, exe, "Steam"))
    return out


# ----------------------------------------------------------------- Epic -----
def scan_epic(manifest_dir: str | None = None) -> list[dict]:
    manifest_dir = manifest_dir or os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"),
                                                "Epic", "EpicGamesLauncher", "Data", "Manifests")
    out = []
    for item in glob.glob(os.path.join(manifest_dir, "*.item")):
        try:
            with open(item, encoding="utf-8") as f:
                d = json.load(f)
            name, folder, launch = d["DisplayName"], d["InstallLocation"], d.get("LaunchExecutable", "")
        except (OSError, ValueError, KeyError):
            continue
        if not name or not os.path.isdir(folder):
            continue
        exe = os.path.basename(launch) if launch else guess_exe(folder)
        if exe:
            out.append(_game(name, folder, exe, "Epic"))
    return out


# ------------------------------------------------------------------ GOG -----
def scan_gog() -> list[dict]:
    out = []
    try:
        base = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\GOG.com\Games")
    except OSError:
        return out
    with base:
        i = 0
        while True:
            try:
                sub = winreg.EnumKey(base, i)
            except OSError:
                break
            i += 1
            try:
                with winreg.OpenKey(base, sub) as k:
                    name = winreg.QueryValueEx(k, "gameName")[0]
                    folder = winreg.QueryValueEx(k, "path")[0]
                    try:
                        exe = os.path.basename(winreg.QueryValueEx(k, "exe")[0])
                    except OSError:
                        exe = guess_exe(folder)
            except OSError:
                continue
            if exe and os.path.isdir(folder):
                out.append(_game(name, folder, exe, "GOG"))
    return out


def scan_all() -> list[dict]:
    """All detected games, de-duplicated by exe name, sorted by name."""
    found = []
    for lib in steam_libraries():
        found += scan_steam_library(lib)
    found += scan_epic()
    found += scan_gog()
    seen, uniq = set(), []
    for g in sorted(found, key=lambda g: g["name"].lower()):
        if g["exe"] not in seen:
            seen.add(g["exe"])
            uniq.append(g)
    return uniq
