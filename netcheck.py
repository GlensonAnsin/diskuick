"""Optional network latency check (off unless the user types a host in Settings).

Measures TCP connect time to host:port, so it works without admin rights, doesn't depend on the
language of Windows (unlike parsing ping.exe) and sends nothing but a normal connection attempt.
"""
import re
import socket
import time

DEFAULT_PORT = 443
_HOST_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")


def parse_target(raw: str) -> tuple[str, int] | None:
    """'host' or 'host:port' -> (host, port); None if empty/invalid."""
    raw = (raw or "").strip()
    if not raw:
        return None
    host, port = raw, DEFAULT_PORT
    if raw.count(":") == 1:
        host, p = raw.rsplit(":", 1)
        if not p.isdigit() or not 0 < int(p) < 65536:
            return None
        port = int(p)
    if not _HOST_RE.match(host):
        return None
    return host, port


def rtt_ms(host: str, port: int = DEFAULT_PORT, timeout: float = 1.0) -> float | None:
    """Milliseconds to open a TCP connection, or None on timeout/failure (counts as loss)."""
    t0 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (time.perf_counter() - t0) * 1000.0
    except OSError:
        return None
