"""Tiny translation layer: UI strings are written in English and looked up here.

Add a language by adding a dict to LANGS. Missing strings fall back to English.
The Filipino strings are a best-effort translation and would benefit from a native review.
"""
LANG = "en"

LANGS = {
    "en": "English",
    "fil": "Filipino",
}

FIL = {}  # filled in by i18n_fil.py (kept separate so it is easy to review/edit)

_TABLES = {"fil": FIL}


def set_lang(code: str):
    global LANG
    LANG = code if code in LANGS else "en"


def T(s: str) -> str:
    return _TABLES.get(LANG, {}).get(s, s) if LANG != "en" else s
