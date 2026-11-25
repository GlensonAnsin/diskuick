"""Tiny translation layer: UI strings are written in English and looked up here.

Add a language: create i18n_<code>.py that calls register("<code>", "<native name>", {english: translated, ...})
and import it in i18n_langs.py. Missing strings fall back to English.
The translations are best-effort and would benefit from native-speaker review.
"""
LANG = "en"

LANGS = {
    "en": "English",
    "fil": "Filipino",
}

FIL = {}  # filled in by i18n_fil.py (kept separate so it is easy to review/edit)

_TABLES = {"fil": FIL}


def register(code: str, name: str, table: dict):
    """Add a language (its name is shown in Settings in its own language)."""
    LANGS[code] = name
    _TABLES[code] = table


def register_seq(code: str, name: str, values):
    """Like register, but `values` are the translations in the order of i18n_keys.KEYS."""
    from i18n_keys import KEYS
    register(code, name, dict(zip(KEYS, values)))


def set_lang(code: str):
    global LANG
    LANG = code if code in LANGS else "en"


def T(s: str) -> str:
    return _TABLES.get(LANG, {}).get(s, s) if LANG != "en" else s
