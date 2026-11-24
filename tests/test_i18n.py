"""Every UI string passed through T() must have a Filipino translation (and placeholders must match)."""
import ast
import os
import re
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)

import i18n
import i18n_fil  # noqa: F401

# strings that are intentionally not translated (identical in Filipino or brand/technical)
SAME_OK = {"Dashboard", "Error", "Drive", "Default", "Keep-alive", "avg ms", "p95 ms", "max ms", "default"}
# dynamic strings that reach T() through variables (controller/health text, pattern labels)
EXTRA = ["Light", "Balanced", "Heavy", "Active", "Waiting", "Off", "Disabled", "Idle", "Starting",
         "Paused while on battery", "Choose a drive in Settings", "Add games in the Games tab",
         "Waiting for a game to start", "Waiting for a game window to be in focus",
         "Tiny random reads, about 10 per second. Least overhead - try this first.",
         "Light sequential reads, about 20 per second. For drives that need a bit more.",
         "Non-stop reads, like HD Tune. Strongest effect, but the drive is always busy."]


def ui_strings():
    out = set(EXTRA)
    for f in ("app_ui.py", "widgets.py", "diskuick_tray.py"):
        with open(os.path.join(ROOT, f), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "T" and n.args:
                try:
                    out.add(ast.literal_eval(n.args[0]))
                except Exception:
                    pass
    return out


class I18nTests(unittest.TestCase):
    def test_all_strings_translated(self):
        missing = sorted(s for s in ui_strings() if s not in i18n.FIL and s not in SAME_OK)
        self.assertEqual(missing, [], f"{len(missing)} untranslated UI strings")

    def test_placeholders_preserved(self):
        for en, fil in i18n.FIL.items():
            self.assertEqual(sorted(re.findall(r"\{\w+\}", en)), sorted(re.findall(r"\{\w+\}", fil)), en)

    def test_fallback_to_english(self):
        i18n.set_lang("fil")
        try:
            self.assertEqual(i18n.T("not a real string"), "not a real string")
            self.assertNotEqual(i18n.T("Games"), "Games")
        finally:
            i18n.set_lang("en")


if __name__ == "__main__":
    unittest.main()
