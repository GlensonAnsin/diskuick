"""Diskuick tray app: keeps drives awake while you game. Entry point of Diskuick.exe."""
import ctypes
import os
import queue
import sys
import threading
import winreg
from tkinter import messagebox

import customtkinter as ctk
import pystray
from PIL import Image

import config
import i18n
import i18n_fil  # noqa: F401  (registers the Filipino strings)
import updater
from app_ui import MainWindow
from controller import Controller
from i18n import T
from logo import render_logo
from overlay import Overlay
from stats import Stats
from version import APP_NAME, UPDATE_REPO, VERSION

APP = APP_NAME
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


# ------------------------------------------------------------- autostart ----
def _autostart_cmd() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pyw = sys.executable.replace("python.exe", "pythonw.exe")
    return f'"{pyw}" "{os.path.abspath(__file__)}"'


def autostart_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as k:
            winreg.QueryValueEx(k, APP)
            return True
    except OSError:
        return False


def set_autostart(on: bool):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as k:
        if on:
            winreg.SetValueEx(k, APP, 0, winreg.REG_SZ, _autostart_cmd())
        else:
            try:
                winreg.DeleteValue(k, APP)
            except OSError:
                pass


def make_icon(state: str) -> Image.Image:
    """Tray icon: the Diskuick logo plus a small status badge."""
    return render_logo(64, state)


# ------------------------------------------------------------------- app ----
class App:
    def __init__(self):
        self.cfg, existed = config.load()
        self.first_run = not existed
        i18n.set_lang(self.cfg["language"])
        ctk.set_appearance_mode(self.cfg["theme"])
        self.stats = Stats()
        self.update_info = None
        self.ui_q: queue.Queue = queue.Queue()
        self.root = ctk.CTk()
        self.root.withdraw()
        self.root.protocol("WM_DELETE_WINDOW", self._quit)  # be closable by installers / shutdown
        self.win = None
        self.overlay = Overlay(self.root)
        self.ctrl = Controller(self.cfg, self.stats, self._on_status, self._on_event)
        self.icon = pystray.Icon(APP, make_icon("off"), APP, self._menu())

    # ---- settings API used by the window
    def autostart_enabled(self) -> bool:
        return autostart_enabled()

    def set_autostart(self, on: bool):
        try:
            set_autostart(on)
        except OSError as e:
            self.ui(lambda: messagebox.showerror(APP, f"{T('Could not change startup setting')}:\n{e}"))

    def apply(self, updates: dict):
        self.cfg.update(updates)
        config.save(self.cfg)
        self.ctrl.update_cfg(self.cfg)
        rebuild = False
        if "theme" in updates:
            ctk.set_appearance_mode(self.cfg["theme"])
            rebuild = True  # live theme switches leave stale corners; rebuild for a clean repaint
        if "language" in updates:
            i18n.set_lang(self.cfg["language"])
            self.icon.menu = self._menu()
            self.icon.update_menu()
            rebuild = True
        if rebuild and self.win is not None and self.win.winfo_exists():
            tab = self.win.current_key()
            self.ui(lambda: self.open_window(tab, force_new=True))

    # ---- UI-thread plumbing
    def ui(self, fn):
        self.ui_q.put(fn)

    def _pump(self):
        try:
            while True:
                self.ui_q.get_nowait()()
        except queue.Empty:
            pass
        self.root.after(150, self._pump)

    def _overlay_tick(self):
        try:
            self.overlay.update(self.cfg["overlay"], self.cfg["overlay_corner"], self.ctrl)
        except Exception:
            self.overlay.hide()
        self.root.after(1000, self._overlay_tick)

    def open_window(self, tab: str | None = None, force_new: bool = False):
        w = self.win
        if w is not None and w.winfo_exists():
            if not force_new:
                w.deiconify()
                w.lift()
                w.focus_force()
                return
            w.destroy()
        self.win = MainWindow(self.root, self, tab)

    # ---- tray
    def _menu(self):
        return pystray.Menu(
            pystray.MenuItem(lambda _: self.ctrl.text, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(T("Open Diskuick"), lambda: self.ui(self.open_window), default=True),
            pystray.MenuItem(T("Enabled"), lambda: self.apply({"enabled": not self.cfg["enabled"]}),
                             checked=lambda _: self.cfg["enabled"]),
            pystray.MenuItem(T("Start with Windows"),
                             lambda: self.set_autostart(not autostart_enabled()),
                             checked=lambda _: autostart_enabled()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(T("Quit"), self._quit),
        )

    def _on_status(self, state: str, text: str):
        self.icon.icon = make_icon(state)
        self.icon.title = f"{APP} - {text}"[:127]
        try:
            self.icon.update_menu()
        except Exception:
            pass

    def _on_event(self, kind: str, g: dict):
        if kind == "game_start":
            try:
                self.icon.notify(T("Keeping drive {d}: awake").format(d=g["drive"]), g["name"])
            except Exception:
                pass

    def _quit(self):
        self.ctrl.shutdown()
        self.icon.stop()
        self.ui(self.overlay.hide)
        self.ui(self.root.quit)

    def _check_updates(self):
        info = updater.check(UPDATE_REPO, VERSION) if (UPDATE_REPO and self.cfg["check_updates"]) else None
        if info:
            self.ui(lambda: self._update_found(info))

    def _update_found(self, info: dict):
        self.update_info = info
        if self.win is not None and self.win.winfo_exists():
            self.win.show_update(info)
        try:
            self.icon.notify(T("Update available: {v}").format(v=info["tag"]), APP)
        except Exception:
            pass

    def install_update(self, installer_path: str):
        """Runs the already-verified installer (it closes and relaunches us), then exits."""
        try:
            updater.launch_installer(installer_path)
        except OSError as e:
            messagebox.showerror(APP, f"{T('Update failed')}: {e}")
            return
        self._quit()

    def run(self):
        self.icon.run_detached()
        self.ctrl.start()
        threading.Thread(target=self._check_updates, daemon=True).start()
        if self.first_run:
            self.ui(lambda: self.open_window("games"))
        self._pump()
        self._overlay_tick()
        self.root.mainloop()


def single_instance() -> bool:
    k32 = ctypes.windll.kernel32
    k32.CreateMutexW(None, False, "Local\\DiskuickTray")
    return k32.GetLastError() != 183  # ERROR_ALREADY_EXISTS


def main():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    if not single_instance():
        import tkinter as tk
        r = tk.Tk()
        r.withdraw()
        messagebox.showinfo(APP, "Diskuick is already running (check the system tray).")
        return
    App().run()


if __name__ == "__main__":
    main()
