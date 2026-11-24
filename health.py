"""Drive health info + plain-language tips.

Uses Windows' Storage cmdlets via PowerShell. Temperature / wear / power-on hours often need
Administrator rights; when missing they come back as None and we say so instead of guessing.
"""
import json
import shutil
import subprocess

NO_WINDOW = 0x08000000

_PS = r"""
$ErrorActionPreference = 'SilentlyContinue'
$l = '%s'
$disk = Get-Partition -DriveLetter $l | Get-Disk
$pd = Get-PhysicalDisk | Where-Object { [string]$_.DeviceId -eq [string]$disk.Number } | Select-Object -First 1
$rel = $pd | Get-StorageReliabilityCounter
[pscustomobject]@{
  model = $pd.FriendlyName; media = [string]$pd.MediaType; bus = [string]$pd.BusType
  health = [string]$pd.HealthStatus; size = $pd.Size
  temp = $rel.Temperature; wear = $rel.Wear; hours = $rel.PowerOnHours; read_errors = $rel.ReadErrorsTotal
} | ConvertTo-Json -Compress
"""


def get_health(drive: str, timeout: float = 30.0) -> dict:
    """Returns a dict (some values may be None). Never raises."""
    drive = drive.strip().rstrip(":\\/").upper()[:1]
    info = {"drive": drive, "model": None, "media": None, "bus": None, "health": None, "size": None,
            "temp": None, "wear": None, "hours": None, "read_errors": None,
            "free": None, "total": None, "error": None}
    try:
        du = shutil.disk_usage(f"{drive}:\\")
        info["free"], info["total"] = du.free, du.total
    except OSError as e:
        info["error"] = str(e)
        return info
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", _PS % drive],
                             capture_output=True, text=True, timeout=timeout,
                             creationflags=NO_WINDOW).stdout.strip()
        if out:
            data = json.loads(out)
            for k in ("model", "media", "bus", "health", "size", "temp", "wear", "hours", "read_errors"):
                v = data.get(k)
                info[k] = None if v in ("", None) else v
    except (subprocess.SubprocessError, ValueError, OSError) as e:
        info["error"] = str(e)
    return info


def health_tips(info: dict) -> list[tuple[str, str]]:
    """[(level, text)], level in 'ok' | 'warn' | 'bad'. Plain-language and conservative."""
    tips = []
    if info.get("total"):
        pct = info["free"] / info["total"] * 100
        if pct < 10:
            tips.append(("bad", f"Only {pct:.0f}% free space. SSDs slow down a lot when nearly full - "
                                "free up space (aim for 15-20%)."))
        elif pct < 15:
            tips.append(("warn", f"{pct:.0f}% free space. Below 15-20% can make an SSD slower."))
        else:
            tips.append(("ok", f"{pct:.0f}% free space - plenty of room."))
    h = (info.get("health") or "").lower()
    if h and h != "healthy":
        tips.append(("bad", f"Windows reports the drive health as '{info['health']}'. Back up your data."))
    elif h == "healthy":
        tips.append(("ok", "Windows reports the drive as Healthy."))
    t = info.get("temp")
    if isinstance(t, (int, float)) and t:
        if t >= 70:
            tips.append(("bad", f"Drive is hot ({t:.0f}°C). Improve airflow; hot drives throttle."))
        elif t >= 60:
            tips.append(("warn", f"Drive is warm ({t:.0f}°C)."))
    w = info.get("wear")
    if isinstance(w, (int, float)) and w >= 80:
        tips.append(("bad", f"SSD wear is {w:.0f}%. Plan to replace it soon."))
    if info.get("read_errors"):
        tips.append(("warn", f"The drive has logged {info['read_errors']} read errors."))
    if (info.get("media") or "").upper() == "HDD":
        tips.append(("warn", "This is a hard disk (HDD). Keep-alive helps with spin-down/sleep but "
                             "an SSD would help far more."))
    if info.get("temp") is None and info.get("wear") is None and not info.get("error"):
        tips.append(("warn", "Temperature and wear aren't available. Running Diskuick as "
                             "Administrator can unlock them."))
    if info.get("error") and not info.get("model"):
        tips.append(("warn", "Couldn't read detailed drive info from Windows."))
    return tips
