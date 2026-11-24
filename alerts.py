"""Heads-up alerts about the game drive: low free space, health no longer 'Healthy'."""
import shutil
import time

LOW_FREE_PCT = 10.0
REPEAT_S = 24 * 3600  # remind about the same problem at most once a day


class Alerts:
    """Pure-ish: feed it readings, it returns the messages that are new. No UI, no threads."""

    def __init__(self):
        self._sent: dict[tuple, float] = {}
        self._health: dict[str, str] = {}

    def _once(self, key: tuple, now: float) -> bool:
        if now - self._sent.get(key, -REPEAT_S) < REPEAT_S:
            return False
        self._sent[key] = now
        return True

    def free_space(self, drive: str, free: int, total: int, now: float | None = None) -> list[str]:
        now = time.time() if now is None else now
        if total <= 0:
            return []
        pct = 100.0 * free / total
        if pct < LOW_FREE_PCT:
            if self._once((drive, "space"), now):
                return [f"Drive {drive}: is almost full ({pct:.0f}% free). A nearly full SSD slows down "
                        "and can cause game stutter."]
        else:
            self._sent.pop((drive, "space"), None)  # recovered: warn again if it fills up again
        return []

    def health(self, drive: str, status: str | None, now: float | None = None) -> list[str]:
        now = time.time() if now is None else now
        if not status:
            return []
        prev = self._health.get(drive)
        self._health[drive] = status
        if status.lower() != "healthy" and (prev is None or prev.lower() == "healthy") \
                and self._once((drive, "health"), now):
            return [f"Windows now reports drive {drive}: as '{status}'. Back up important files."]
        if status.lower() == "healthy":
            self._sent.pop((drive, "health"), None)
        return []


def usage(drive: str):
    try:
        u = shutil.disk_usage(f"{drive}:\\")
        return u.free, u.total
    except OSError:
        return 0, 0
