import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import i18n
import i18n_langs
from i18n_keys import KEYS

SEQ_LANGS = [c for c in i18n.LANGS if c not in ("en", "fil")]


def holes(s):
    return sorted(re.findall(r"\{\w*\}", s))


class LanguageTests(unittest.TestCase):
    def test_all_languages_are_registered(self):
        self.assertGreaterEqual(len(SEQ_LANGS), 13)

    def test_every_language_translates_every_string(self):
        for code in SEQ_LANGS:
            t = i18n._TABLES[code]
            self.assertEqual(len(t), len(KEYS), code)
            for k in KEYS:
                self.assertTrue(t[k].strip(), (code, k))

    def test_placeholders_and_newlines_survive(self):
        for code in SEQ_LANGS:
            for k, v in i18n._TABLES[code].items():
                self.assertEqual(holes(k), holes(v), (code, k))
                self.assertEqual(k.count(chr(10)), v.count(chr(10)), (code, k))

    def test_unknown_strings_fall_back_to_english(self):
        i18n.set_lang(SEQ_LANGS[0])
        try:
            self.assertEqual(i18n.T("not a real string"), "not a real string")
        finally:
            i18n.set_lang("en")


if __name__ == "__main__":
    unittest.main()
