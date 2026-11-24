"""Update check + one-click update from GitHub Releases. Disabled unless version.UPDATE_REPO is set.

Privacy: only the repository name is contacted (api.github.com and GitHub's release download
hosts). Nothing about the user or PC is sent.

Safety: an update is only ever installed if
  * the download comes over HTTPS from GitHub's own hosts,
  * the release provides a SHA-256 checksum (GitHub's asset digest, or a `<asset>.sha256` file), and
  * the downloaded file matches that checksum.
Otherwise the app just offers to open the release page.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

API_BASE = "https://api.github.com"
DOWNLOAD_HOST_SUFFIXES = ("github.com", "githubusercontent.com")
SETUP_RE = re.compile(r"^Diskuick-Setup-[\w.\-]+\.exe$", re.I)
NO_WINDOW = 0x08000000
DETACHED = 0x00000008


class UpdateError(Exception):
    pass


def parse_version(tag: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", tag)[:3]) or (0,)


def is_newer(latest: str, current: str) -> bool:
    return parse_version(latest) > parse_version(current)


def _allowed(url: str) -> bool:
    if url.startswith(API_BASE + "/") or url == API_BASE:
        return True
    u = urllib.parse.urlparse(url)
    return u.scheme == "https" and any(u.hostname == s or (u.hostname or "").endswith("." + s)
                                       for s in DOWNLOAD_HOST_SUFFIXES)


def _open(url: str, timeout: float):
    if not _allowed(url):
        raise UpdateError(f"Refusing to contact {urllib.parse.urlparse(url).hostname}")
    req = urllib.request.Request(url, headers={"User-Agent": "Diskuick-updater",
                                               "Accept": "application/vnd.github+json, */*"})
    resp = urllib.request.urlopen(req, timeout=timeout)
    if not _allowed(resp.geturl()):  # a redirect must not leave GitHub
        resp.close()
        raise UpdateError("Download redirected to an untrusted host")
    return resp


def _get_json(url: str, timeout: float = 8.0):
    with _open(url, timeout) as r:
        return json.load(r)


def _sha256_from_text(text: str) -> str | None:
    m = re.search(r"\b([0-9a-fA-F]{64})\b", text)
    return m.group(1).lower() if m else None


def check(repo: str, current: str, timeout: float = 8.0):
    """Returns info for a newer release, else None. Never raises.

    info = {tag, url (release page), asset_url, asset_name, sha256 (or None), size (or None)}
    asset_url is None when the release has no installer.
    """
    if not repo or "/" not in repo:
        return None
    try:
        data = _get_json(f"{API_BASE}/repos/{repo}/releases/latest", timeout)
        tag = data.get("tag_name", "")
        if not tag or not is_newer(tag, current):
            return None
        info = {"tag": tag, "url": data.get("html_url") or f"https://github.com/{repo}/releases",
                "asset_url": None, "asset_name": None, "sha256": None, "size": None}
        assets = data.get("assets") or []
        setup = next((a for a in assets if SETUP_RE.match(a.get("name", ""))), None)
        if setup:
            info.update(asset_url=setup.get("browser_download_url"), asset_name=setup["name"],
                        size=setup.get("size"))
            digest = setup.get("digest") or ""
            if digest.lower().startswith("sha256:"):
                info["sha256"] = digest.split(":", 1)[1].strip().lower()
            else:
                side = next((a for a in assets if a.get("name") == setup["name"] + ".sha256"), None)
                if side and side.get("browser_download_url"):
                    try:
                        with _open(side["browser_download_url"], timeout) as r:
                            info["sha256"] = _sha256_from_text(r.read(4096).decode("utf-8", "ignore"))
                    except Exception:
                        pass
        return info
    except Exception:
        return None


def can_self_update(info: dict | None) -> bool:
    return bool(info and info.get("asset_url") and info.get("sha256") and is_installed_copy())


def is_installed_copy() -> bool:
    """True when running the exe installed by Diskuick-Setup (an uninstaller sits beside it)."""
    if not getattr(sys, "frozen", False):
        return False
    return os.path.exists(os.path.join(os.path.dirname(sys.executable), "unins000.exe"))


def download(info: dict, dest_dir: str | None = None, progress=None, cancel=None,
             timeout: float = 20.0) -> str:
    """Downloads and verifies the installer. Returns its path; raises UpdateError otherwise."""
    if not info.get("asset_url") or not info.get("sha256"):
        raise UpdateError("This release has no verifiable installer.")
    name = info.get("asset_name") or "Diskuick-Setup.exe"
    if not SETUP_RE.match(name):
        raise UpdateError("Unexpected installer name.")
    dest_dir = dest_dir or tempfile.mkdtemp(prefix="diskuick_update_")
    path = os.path.join(dest_dir, name)
    h = hashlib.sha256()
    try:
        with _open(info["asset_url"], timeout) as r, open(path, "wb") as f:
            total = int(r.headers.get("Content-Length") or info.get("size") or 0)
            got = 0
            while True:
                if cancel is not None and cancel.is_set():
                    raise UpdateError("Cancelled")
                chunk = r.read(256 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                h.update(chunk)
                got += len(chunk)
                if progress and total:
                    progress(min(1.0, got / total))
    except UpdateError:
        _rm(path)
        raise
    except Exception as e:
        _rm(path)
        raise UpdateError(f"Download failed: {e}") from e
    if h.hexdigest().lower() != info["sha256"].lower():
        _rm(path)
        raise UpdateError("The download didn't match its checksum, so it was discarded.")
    return path


def _rm(path: str):
    try:
        os.remove(path)
    except OSError:
        pass


def installer_args(pid: int | None = None) -> list[str]:
    """Silent upgrade in place, then relaunch Diskuick (see installer.iss).

    /WAITPID makes the installer wait for this app to exit before touching any files; the
    installer then stops any leftover Diskuick process itself.
    """
    return ["/SILENT", "/NORESTART", "/RELAUNCH=1", f"/WAITPID={os.getpid() if pid is None else pid}"]


# Set by PyInstaller's one-file bootloader in the running app. If a new copy of the app inherits them (the
# installer relaunches Diskuick after an update) it believes the old, already-exited process is its parent
# and stops with "Security validation failure: invalid originating onefile parent process".
PYINSTALLER_ENV = ("_PYI_APPLICATION_HOME_DIR", "_PYI_ARCHIVE_FILE", "_PYI_PARENT_PROCESS_LEVEL",
                   "_PYI_SPLASH_IPC", "_MEIPASS2")


def clean_env(env=None) -> dict[str, str]:
    """A copy of the environment without PyInstaller's bookkeeping variables."""
    return {k: v for k, v in (os.environ if env is None else env).items() if k.upper() not in PYINSTALLER_ENV}


def launch_installer(path: str):
    """Starts the verified installer detached; the caller should quit the app right after."""
    subprocess.Popen([path, *installer_args()], close_fds=True, creationflags=DETACHED | NO_WINDOW,
                     env=clean_env())
