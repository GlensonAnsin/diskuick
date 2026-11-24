"""Global hotkeys (Win32 RegisterHotKey). They work while a game has focus and need no admin rights.

Each hotkey runs its callback on the hotkey thread; callbacks must hand work to the UI thread.
If another program already owns a combination, registration fails quietly and that one is skipped.
"""
import ctypes
import ctypes.wintypes as wt
import threading

MOD_ALT, MOD_CONTROL, MOD_NOREPEAT = 0x1, 0x2, 0x4000
WM_HOTKEY, WM_QUIT = 0x0312, 0x0012
VK_L, VK_O = 0x4C, 0x4F

_u32 = ctypes.windll.user32
_k32 = ctypes.windll.kernel32

# id -> (label shown in the UI, virtual-key)
KEYS = {1: ("Ctrl+Alt+L", VK_L), 2: ("Ctrl+Alt+O", VK_O)}


class Hotkeys(threading.Thread):
    def __init__(self, handlers: dict[int, callable]):
        super().__init__(daemon=True)
        self.handlers = handlers
        self.registered: list[int] = []
        self.failed: list[int] = []
        self._tid = 0
        self._ready = threading.Event()

    def run(self):
        self._tid = _k32.GetCurrentThreadId()
        for hid, (_, vk) in KEYS.items():
            if hid in self.handlers:
                ok = _u32.RegisterHotKey(None, hid, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, vk)
                (self.registered if ok else self.failed).append(hid)
        self._ready.set()
        msg = wt.MSG()
        while _u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY and msg.wParam in self.handlers:
                try:
                    self.handlers[msg.wParam]()
                except Exception:
                    pass
        for hid in self.registered:
            _u32.UnregisterHotKey(None, hid)

    def wait_ready(self, timeout: float = 2.0) -> bool:
        return self._ready.wait(timeout)

    def stop(self):
        if self._tid:
            _u32.PostThreadMessageW(self._tid, WM_QUIT, 0, 0)
