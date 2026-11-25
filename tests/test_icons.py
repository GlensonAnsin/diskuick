import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import icons


class IconTests(unittest.TestCase):
    def test_extracts_an_exe_icon(self):
        img = icons.extract(os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "explorer.exe"), 48)
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (48, 48))
        self.assertTrue(img.getchannel("A").getbbox())   # not fully transparent

    def test_missing_exe_gives_none(self):
        self.assertIsNone(icons.extract(r"C:\nope\missing.exe"))

    def test_locate_uses_remembered_path_and_folder(self):
        exp = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "explorer.exe")
        self.assertEqual(icons.locate({"exe": "explorer.exe", "exe_path": exp}), exp)
        self.assertEqual(icons.find_in_folder(os.path.dirname(exp), "EXPLORER.EXE", 1).lower(), exp.lower())

    def test_game_keeps_name_and_paths(self):
        g = config.norm_game({"exe": "RDR2.exe", "name": "Red Dead Redemption 2", "path": "D:/g", "exe_path": "D:/g/RDR2.exe"})
        self.assertEqual((g["name"], g["exe"], g["path"], g["exe_path"]),
                         ("Red Dead Redemption 2", "rdr2.exe", "D:/g", "D:/g/RDR2.exe"))


if __name__ == "__main__":
    unittest.main()
