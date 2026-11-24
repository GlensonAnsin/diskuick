"""Settings storage + migration from the v1 config format."""
import json
import os

APP_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "diskuick")
CFG_PATH = os.path.join(APP_DIR, "config.json")
PATTERNS = ("random", "seq", "heavy")

DEFAULTS = {
    "enabled": True,
    "mode": "games",             # "games" = only while a listed game runs, "always"
    "always_drives": [],         # drive letters kept awake in "always" mode
    "default_pattern": "random",
    "interval": None,            # seconds between reads; None = pattern default
    "games": [],                 # [{name, exe, drive, pattern|None, enabled}]
    "size_mb": 256,
    "pause_on_battery": True,
    "only_when_focused": False,  # only keep awake while the game window is focused
    "notify": True,
    "overlay": False,            # small latency readout in a screen corner while a game runs
    "overlay_corner": "top-right",
    "theme": "system",           # system | dark | light
    "language": "en",            # en | fil
    "check_updates": True,       # only does anything if version.UPDATE_REPO is set
}


def norm_game(g: dict) -> dict:
    pat = g.get("pattern")
    return {
        "name": str(g.get("name") or g.get("exe") or "Game"),
        "exe": str(g.get("exe", "")).strip().lower(),
        "drive": str(g.get("drive", "C")).strip().rstrip(":\\/").upper()[:1] or "C",
        "pattern": pat if pat in PATTERNS else None,
        "enabled": bool(g.get("enabled", True)),
    }


def migrate(raw: dict) -> dict:
    """Accepts a config of any version and returns a complete, valid v2 config."""
    raw = dict(raw)
    if "games" not in raw and ("processes" in raw or "drive" in raw):  # v1 format
        drive = (raw.get("drive") or "C").upper()
        raw["games"] = [{"name": p, "exe": p, "drive": drive} for p in raw.get("processes", [])]
        raw["always_drives"] = [drive] if raw.get("drive") else []
        raw["default_pattern"] = raw.get("pattern", "random")
    cfg = dict(DEFAULTS)
    cfg.update({k: v for k, v in raw.items() if k in DEFAULTS})
    cfg["games"] = [norm_game(g) for g in cfg["games"] if g.get("exe") or g.get("name")]
    cfg["games"] = [g for g in cfg["games"] if g["exe"]]
    if cfg["default_pattern"] not in PATTERNS:
        cfg["default_pattern"] = "random"
    if cfg["overlay_corner"] not in ("top-left", "top-right", "bottom-left", "bottom-right"):
        cfg["overlay_corner"] = "top-right"
    if cfg["mode"] not in ("games", "always"):
        cfg["mode"] = "games"
    cfg["always_drives"] = sorted({str(d).upper()[:1] for d in cfg["always_drives"] if d})
    return cfg


def load(path: str = CFG_PATH):
    """Returns (config, existed)."""
    try:
        with open(path, encoding="utf-8") as f:
            return migrate(json.load(f)), True
    except (OSError, ValueError):
        return migrate({}), False


def save(cfg: dict, path: str = CFG_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    os.replace(tmp, path)
