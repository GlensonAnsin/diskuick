import os
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cleanup
import diskscan


def write(path, size):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"x" * size)


class ScanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        write(os.path.join(self.root, "a", "big.bin"), 2_000_000)
        write(os.path.join(self.root, "a", "small.txt"), 10)
        write(os.path.join(self.root, "a", "b", "clip.mp4"), 3_000_000)
        write(os.path.join(self.root, "c", "note.txt"), 500)
        write(os.path.join(self.root, "top.txt"), 7)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sizes_roll_up(self):
        tree, _ = diskscan.scan(self.root)
        self.assertEqual(tree.size, 2_000_000 + 10 + 3_000_000 + 500 + 7)
        self.assertEqual(tree.files, 5)
        self.assertEqual(tree.folders, 3)
        names = [c.name for c in tree.children]
        self.assertEqual(names[0], "a")                      # biggest first
        a = tree.children[0]
        self.assertEqual(a.size, 5_000_010)
        self.assertEqual(a.folders, 1)

    def test_small_files_are_lumped(self):
        tree, _ = diskscan.scan(self.root)
        lump = [c for c in tree.children if c.lump]
        self.assertEqual(len(lump), 1)
        self.assertEqual((lump[0].size, lump[0].files), (7, 1))
        a = next(c for c in tree.children if c.name == "a")
        self.assertIn("big.bin", [c.name for c in a.children])   # big file keeps its own node

    def test_extension_summary(self):
        _, exts = diskscan.scan(self.root)
        top = diskscan.top_extensions(exts, 2)
        self.assertEqual(top[0][0], ".mp4")
        self.assertEqual(top[1][:2], (".bin", 2_000_000))
        self.assertEqual(exts[".txt"], [517, 3])

    def test_cancel_returns_partial_tree(self):
        cancel = threading.Event()
        cancel.set()
        tree, _ = diskscan.scan(self.root, cancel)
        self.assertEqual(tree.size, 0)

    def test_missing_folder_is_empty(self):
        tree, exts = diskscan.scan(os.path.join(self.root, "nope"))
        self.assertEqual((tree.size, exts), (0, {}))

    def test_remove_node_updates_every_folder_above(self):
        tree, _ = diskscan.scan(self.root)
        a = next(c for c in tree.children if c.name == "a")
        b = next(c for c in a.children if c.name == "b")
        before = (tree.size, tree.files, tree.folders)
        diskscan.remove_node(b)
        self.assertEqual((tree.size, tree.files, tree.folders), (before[0] - 3_000_000, before[1] - 1, before[2] - 1))
        self.assertEqual((a.size, a.files, a.folders), (2_000_010, 2, 0))
        self.assertNotIn(b, a.children)
        big = next(c for c in a.children if c.name == "big.bin")
        diskscan.remove_node(big)
        self.assertEqual((tree.size, tree.files), (before[0] - 5_000_000, before[1] - 2))

    def test_remove_lump_and_root(self):
        tree, _ = diskscan.scan(self.root)
        lump = next(c for c in tree.children if c.lump)
        diskscan.remove_node(lump)
        self.assertEqual(tree.files, 4)
        diskscan.remove_node(tree)       # the scan root has no parent: nothing happens
        self.assertEqual(tree.files, 4)

    def test_fmt_size(self):
        self.assertEqual(diskscan.fmt_size(0), "0 B")
        self.assertEqual(diskscan.fmt_size(1500), "1.5 KB")
        self.assertEqual(diskscan.fmt_size(45_800_000_000), "45.8 GB")
        self.assertEqual(diskscan.fmt_size(250_000_000), "250 MB")


class TreemapTests(unittest.TestCase):
    def test_areas_proportional_and_inside(self):
        items = [("a", 60), ("b", 25), ("c", 10), ("d", 5)]
        rects = diskscan.squarify(items, 0, 0, 200, 100)
        self.assertEqual(len(rects), 4)
        total = 200 * 100
        for (k, x, y, w, h), (_, size) in zip(rects, items):
            self.assertAlmostEqual(w * h, total * size / 100, places=3)
            self.assertGreaterEqual(x, -1e-6)
            self.assertGreaterEqual(y, -1e-6)
            self.assertLessEqual(x + w, 200 + 1e-6)
            self.assertLessEqual(y + h, 100 + 1e-6)

    def test_degenerate(self):
        self.assertEqual(diskscan.squarify([], 0, 0, 10, 10), [])
        self.assertEqual(diskscan.squarify([("a", 0)], 0, 0, 10, 10), [])
        self.assertEqual(diskscan.squarify([("a", 5)], 0, 0, 0, 10), [])

    def test_colour_is_stable_hex(self):
        c = diskscan.color_for("Windows", True)
        self.assertRegex(c, r"^#[0-9a-f]{6}$")
        self.assertEqual(c, diskscan.color_for("windows", True))


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "Temp")
        write(os.path.join(self.root, "old.tmp"), 1000)
        write(os.path.join(self.root, "sub", "deep", "old2.tmp"), 500)
        write(os.path.join(self.root, "new.tmp"), 100)
        old = time.time() - 7200
        for p in ("old.tmp", os.path.join("sub", "deep", "old2.tmp")):
            os.utime(os.path.join(self.root, p), (old, old))

    def tearDown(self):
        self.tmp.cleanup()

    def test_measure_matches_what_clean_removes(self):
        self.assertEqual(cleanup.dir_size(self.root, min_age=3600), (1500, 2))
        freed, n = cleanup.clean_dir(self.root, min_age=3600)
        self.assertEqual((freed, n), (1500, 2))

    def test_recent_files_and_root_are_kept(self):
        cleanup.clean_dir(self.root, min_age=3600)
        self.assertTrue(os.path.isdir(self.root))
        self.assertTrue(os.path.exists(os.path.join(self.root, "new.tmp")))
        self.assertFalse(os.path.exists(os.path.join(self.root, "old.tmp")))
        self.assertFalse(os.path.exists(os.path.join(self.root, "sub")))   # emptied folders go too

    def test_readonly_file_is_removed(self):
        p = os.path.join(self.root, "ro.tmp")
        write(p, 10)
        os.chmod(p, 0o444)
        cleanup.clean_dir(self.root)
        self.assertFalse(os.path.exists(p))

    def test_category_cleans_only_its_own_folder(self):
        outside = os.path.join(self.tmp.name, "Documents", "keep.docx")
        write(outside, 50)
        cat = cleanup.Category("t", "t", "", dirs=[self.root])
        cleanup.clean(cat)
        self.assertTrue(os.path.exists(outside))

    def test_missing_folder_and_globs(self):
        write(os.path.join(self.tmp.name, "thumbcache_32.db"), 40)
        write(os.path.join(self.tmp.name, "other.db"), 40)
        cat = cleanup.Category("t", "t", "", dirs=[os.path.join(self.tmp.name, "gone")],
                               globs=[os.path.join(self.tmp.name, "thumbcache_*.db")])
        self.assertEqual(cleanup.measure(cat), (40, 1))
        self.assertEqual(cleanup.clean(cat), (40, 1))
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "other.db")))

    def test_protected_paths_cannot_be_deleted(self):
        drive = os.environ.get("SystemDrive", "C:")
        for p in (drive + "\\", drive, drive + "\\Windows", drive + "\\Windows\\System32\\cmd.exe",
                  drive + "\\Program Files", drive + "\\ProgramData", drive + "\\Users",
                  os.environ["USERPROFILE"], drive + "\\pagefile.sys", drive + "\\$Recycle.Bin",
                  drive + "\\System Volume Information", "D:\\"):
            self.assertIsNotNone(cleanup.protected_reason(p), p)
        for p in (os.path.join(os.environ["USERPROFILE"], "Downloads", "old.iso"),
                  drive + "\\Games\\Old", "D:\\source-codes\\x", self.root):
            self.assertIsNone(cleanup.protected_reason(p), p)

    def test_recycle_refuses_protected_and_missing(self):
        self.assertFalse(cleanup.recycle(os.environ.get("SystemRoot", "C:\\Windows")))
        self.assertFalse(cleanup.recycle(os.path.join(self.root, "does-not-exist")))
        self.assertTrue(os.path.exists(os.path.join(self.root, "old.tmp")))

    def test_default_categories_are_safe(self):
        cats = {c.key: c for c in cleanup.categories()}
        self.assertFalse(cats["recycle"].default)      # irreversible, so opt-in
        self.assertFalse(cats["browser"].default)
        self.assertFalse(cats["shader"].default)
        self.assertTrue(cats["user_temp"].default)
        for c in cats.values():
            for d in c.dirs:
                self.assertNotIn(d, ("", os.sep, "C:\\"))


if __name__ == "__main__":
    unittest.main()
