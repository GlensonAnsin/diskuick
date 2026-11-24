"""Smart intensity: start light, step up only while the drive keeps stalling, step back down when calm."""
import collections

LEVELS = ("random", "seq", "heavy")  # Light -> Balanced -> Heavy


class Adaptive:
    """Pure state machine (no threads, no clock of its own) so it is easy to test.

    * `up_stalls` stalls within `window` seconds  -> one level up (never above Heavy)
    * `calm` seconds without a stall at that level -> one level down (never below Light)
    * If stepping down is followed by stalls again within 2 minutes, the next calm period doubles
      (up to an hour) so it doesn't flip-flop forever.
    """

    def __init__(self, now: float = 0.0, up_stalls: int = 3, window: float = 60.0, calm: float = 600.0):
        self.level = 0
        self.up_stalls, self.window = up_stalls, window
        self.base_calm = self.calm = calm
        self.since = now            # when the current level began
        self.last_stall = None
        self.last_down = None
        self.stalls: collections.deque = collections.deque()

    @property
    def pattern(self) -> str:
        return LEVELS[self.level]

    def note_stall(self, ts: float):
        self.stalls.append(ts)
        self.last_stall = ts

    def update(self, now: float) -> str:
        while self.stalls and self.stalls[0] < now - self.window:
            self.stalls.popleft()
        if len(self.stalls) >= self.up_stalls and self.level < len(LEVELS) - 1:
            self.level += 1
            if self.last_down is not None and now - self.last_down < 120:
                self.calm = min(self.calm * 2, 3600.0)
            self.since = now
            self.stalls.clear()
        elif self.level > 0 and now - max(self.since, self.last_stall or 0.0) >= self.calm:
            self.level -= 1
            self.since = self.last_down = now
            self.stalls.clear()
        elif self.level == 0 and now - self.since > 1800:
            self.calm = self.base_calm  # long quiet spell: forget the back-off
        return self.pattern
