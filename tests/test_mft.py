import os
import struct
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import diskscan
import mftscan

RL = 1024
USN = b"\x07\x00"


def attr_filename(name, parent, ns=1, fattr=0, real=0):
    nm = name.encode("utf-16-le")
    content = struct.pack("<Q", parent | (1 << 48)) + bytes(0x20) + struct.pack("<QQIIBB", 0, real, fattr, 0, len(name), ns) + nm
    head = struct.pack("<IIBBHHHIHBB", 0x30, 0, 0, 0, 0x18, 0, 0, len(content), 0x18, 0, 0)
    body = head + content
    body += bytes(-len(body) % 8)
    return body[:4] + struct.pack("<I", len(body)) + body[8:]


def attr_data_resident(n):
    content = b"x" * n
    head = struct.pack("<IIBBHHHIHBB", 0x80, 0, 0, 0, 0x18, 0, 0, n, 0x18, 0, 0)
    body = head + content
    body += bytes(-len(body) % 8)
    return body[:4] + struct.pack("<I", len(body)) + body[8:]


def attr_data_nonres(real, runs=b"\x11\x01\x10\x00"):
    head = struct.pack("<IIBBHHHQQHHIQQQ", 0x80, 0, 1, 0, 0x40, 0, 0, 0, 0, 0x40, 0, 0, real, real, real)
    body = head + runs
    body += bytes(-len(body) % 8)
    return body[:4] + struct.pack("<I", len(body)) + body[8:]


def record(attrs, flags=1, base=0, torn=False):
    rec = bytearray(RL)
    count = RL // 512 + 1
    rec[0:4] = b"FILE"
    struct.pack_into("<HH", rec, 4, 0x30, count)
    struct.pack_into("<H", rec, 0x14, 0x38)
    struct.pack_into("<H", rec, 0x16, flags)
    struct.pack_into("<Q", rec, 0x20, base)
    off = 0x38
    for a in attrs:
        rec[off:off + len(a)] = a
        off += len(a)
    rec[off:off + 4] = b"\xff\xff\xff\xff"
    rec[0x30:0x32] = USN
    for i in range(1, count):                  # NTFS update-sequence protection
        end = i * 512
        rec[0x30 + 2 * i:0x32 + 2 * i] = rec[end - 2:end]
        rec[end - 2:end] = b"\x00\x00" if torn else USN
    return bytes(rec)


def file_rec(name, parent, size, ns=1, resident=True, extra=(), **kw):
    data = attr_data_resident(size) if resident else attr_data_nonres(size)
    return record([attr_filename(name, parent, ns)] + list(extra) + [data], **kw)


def attr_reparse():
    head = struct.pack("<IIBBHHHIHBB", 0xC0, 0, 0, 0, 0x18, 0, 0, 8, 0x18, 0, 0)
    body = head + bytes(8)
    return body[:4] + struct.pack("<I", len(body)) + body[8:]


def dir_rec(name, parent, fattr=0, extra=()):
    return record([attr_filename(name, parent, 1, fattr)] + list(extra), flags=3)


def image(records: dict[int, bytes], total=64):
    out = bytearray(total * RL)
    for i, r in records.items():
        out[i * RL:(i + 1) * RL] = r
    return bytes(out), total


class ParserTests(unittest.TestCase):
    def build(self):
        recs = {
            5: dir_rec(".", 5),
            30: dir_rec("Users", 5),
            31: dir_rec("Games", 5),
            40: file_rec("a.txt", 30, 10),
            41: record([attr_filename("BIGISO~1.ISO", 31, ns=2), attr_filename("big.iso", 31, ns=1),
                        attr_data_nonres(5_000_000)]),
            43: dir_rec("Link", 5, fattr=0x400),                        # junction: must not be followed
            42: dir_rec("Settings", 5, extra=[attr_reparse()]),         # ...even when only $REPARSE_POINT says so
            44: file_rec("lost.dat", 60, 77),                           # parent folder is gone
            45: file_rec("deleted.txt", 30, 999, flags=0),              # not in use
            46: file_rec("ext.txt", 30, 999, base=40 | (1 << 48)),      # extension record of another file
            47: file_rec("torn.txt", 30, 999, torn=True),               # failed the update-sequence check
            48: file_rec("b.TXT", 30, 500),
        }
        buf, total = image(recs)
        cat = mftscan.Catalog(total)
        used = mftscan.parse_chunk(buf, RL, 0, cat)
        self.assertEqual(used, total * RL)
        return cat, mftscan.build_tree(cat, "D:\\")

    def test_tree_shape_and_sizes(self):
        cat, tree = self.build()
        self.assertEqual((tree.size, tree.files, tree.folders), (5_000_510, 3, 2))
        users = next(c for c in tree.children if c.name == "Users")
        games = next(c for c in tree.children if c.name == "Games")
        self.assertEqual((users.size, users.files), (510, 2))
        self.assertEqual((games.size, games.files), (5_000_000, 1))
        self.assertEqual(games.path, "D:\\Games")
        iso = next(c for c in games.children if not c.lump)
        self.assertEqual((iso.name, iso.size, iso.path), ("big.iso", 5_000_000, "D:\\Games\\big.iso"))  # long name, not 8.3
        self.assertNotIn("Link", [c.name for c in tree.children])
        self.assertNotIn("Settings", [c.name for c in tree.children])

    def test_pieces_parsed_separately_and_merged_match_one_pass(self):
        recs = {
            5: dir_rec(".", 5), 30: dir_rec("Users", 5), 31: dir_rec("Games", 5),
            40: file_rec("a.txt", 30, 10), 48: file_rec("b.TXT", 30, 500),
            50: record([attr_filename("huge.rpf", 31, 1, real=0)]),
            60: record([attr_data_nonres(3_000_000_000)], base=50 | (1 << 48)),   # extension lands in a later piece
            61: record([attr_filename("big.iso", 31, 1), attr_data_nonres(5_000_000)]),
        }
        buf, total = image(recs)
        whole = mftscan.Catalog(total)
        mftscan.parse_chunk(buf, RL, 0, whole)
        merged = mftscan.Catalog(total)
        step = 16                                              # records per piece
        for first in range(0, total, step):
            piece = buf[first * RL:(first + step) * RL]
            merged.merge(mftscan.parse_in_worker_local(piece, RL, first, total))
        a, b = mftscan.build_tree(whole, "D:\\"), mftscan.build_tree(merged, "D:\\")
        self.assertEqual((a.size, a.files, a.folders), (b.size, b.files, b.folders))
        self.assertEqual(whole.exts, merged.exts)
        self.assertEqual(b.size, 3_005_000_510)

    def test_plan_pieces_covers_the_mft_in_whole_records(self):
        boot = mftscan.Boot.__new__(mftscan.Boot)
        boot.record, boot.cluster = 1024, 4096
        pieces = mftscan.plan_pieces([(10, 5), (100, 3)], boot, 8 * 4096, piece=8192)
        self.assertEqual(sum(n for _, _, n in pieces), 8 * 4096)
        self.assertEqual(pieces[0], (0, 10 * 4096, 8192))
        self.assertEqual(pieces[-1][0] * 1024 + pieces[-1][2], 8 * 4096)
        self.assertIsNone(mftscan.plan_pieces([(10, 1)], boot, 1000, piece=8192))   # not whole records

    def test_fragmented_file_size_comes_from_its_extension_record(self):
        recs = {
            5: dir_rec(".", 5),
            31: dir_rec("Games", 5),
            50: record([attr_filename("huge.rpf", 31, 1, real=0)]),             # no data attribute in its own record
            51: record([attr_data_nonres(3_000_000_000)], base=50 | (1 << 48)),   # ...it lives here instead
            52: record([attr_filename("empty.dat", 31, 1)] + [attr_data_resident(0)]),
        }
        buf, total = image(recs)
        cat = mftscan.Catalog(total)
        mftscan.parse_chunk(buf, RL, 0, cat)
        tree = mftscan.build_tree(cat, "D:\\")
        games = tree.children[0]
        self.assertEqual((games.size, games.files), (3_000_000_000, 2))
        self.assertEqual(cat.exts[".rpf"], [3_000_000_000, 1])

    def test_extension_stats_and_order(self):
        cat, tree = self.build()
        self.assertEqual(cat.exts[".txt"], [510, 2])        # .TXT and .txt are one type
        self.assertEqual(cat.exts[".iso"], [5_000_000, 1])
        self.assertEqual([c.name for c in tree.children][0], "Games")   # biggest first

    def test_matches_the_folder_walk(self):
        with tempfile.TemporaryDirectory() as d:
            for rel, size in (("Users/a.txt", 10), ("Users/b.TXT", 500), ("Games/big.iso", 5_000_000)):
                p = os.path.join(d, *rel.split("/"))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "wb") as f:
                    f.write(b"x" * size)
            walk, _ = diskscan.scan(d)
        _, mft = self.build()
        self.assertEqual((mft.size, mft.files, mft.folders), (walk.size, walk.files, walk.folders))


class LayoutTests(unittest.TestCase):
    def test_fixups(self):
        rec = bytearray(file_rec("a", 5, 1))
        self.assertTrue(mftscan.apply_fixups(rec))
        self.assertEqual(rec[510:512], b"\x00\x00")
        self.assertFalse(mftscan.apply_fixups(bytearray(file_rec("a", 5, 1, torn=True))))

    def test_data_runs(self):
        self.assertEqual(mftscan.parse_runs(b"\x21\x03\x64\x00\x11\x02\xf0\x00"), [(100, 3), (84, 2)])
        self.assertEqual(mftscan.parse_runs(b"\x01\x05\x00"), [(None, 5)])    # sparse
        self.assertEqual(mftscan.parse_runs(b"\x00"), [])

    def sector(self, cluster_byte=8, per_record=0xF6):
        s = bytearray(512)
        s[3:11] = b"NTFS    "
        struct.pack_into("<H", s, 0x0B, 512)
        s[0x0D] = cluster_byte
        struct.pack_into("<Q", s, 0x30, 786432)
        s[0x40] = per_record            # -10 as a signed byte: 2**10 = 1024-byte records
        return bytes(s)

    def test_boot_sector(self):
        b = mftscan.Boot(self.sector())
        self.assertEqual((b.cluster, b.mft_lcn, b.record), (4096, 786432, 1024))
        self.assertEqual(mftscan.Boot(self.sector(per_record=1)).record, 4096)   # positive = clusters per record
        with self.assertRaises(mftscan.MftError):
            mftscan.Boot(bytes(512))

    def test_mft_extents(self):
        boot = mftscan.Boot(self.sector())
        rec0 = record([attr_filename("$MFT", 5), attr_data_nonres(4096 * 3, runs=b"\x21\x03\x00\x10\x00")])
        runs, size = mftscan.mft_extents(rec0, boot)
        self.assertEqual((runs, size), ([(4096, 3)], 4096 * 3))
        short = record([attr_filename("$MFT", 5), attr_data_nonres(4096 * 9, runs=b"\x21\x03\x00\x10\x00")])
        with self.assertRaises(mftscan.MftError):
            mftscan.mft_extents(short, boot)


class FallbackTests(unittest.TestCase):
    def test_not_admin_uses_walk(self):
        sentinel = (object(), {})
        with mock.patch.object(mftscan, "available", return_value=False), \
                mock.patch.object(diskscan, "scan", return_value=sentinel) as walk:
            tree, exts, method = mftscan.scan_drive("D")
        self.assertEqual(method, "walk")
        walk.assert_called_once()

    def test_mft_failure_uses_walk(self):
        sentinel = (object(), {})
        with mock.patch.object(mftscan, "available", return_value=True), \
                mock.patch.object(mftscan, "scan_mft", side_effect=mftscan.MftError("odd layout")), \
                mock.patch.object(diskscan, "scan", return_value=sentinel):
            self.assertEqual(mftscan.scan_drive("D")[2], "walk")

    def test_spot_check_rejects_wrong_results(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(10):
                with open(os.path.join(d, f"f{i}.bin"), "wb") as f:
                    f.write(b"x" * 1_100_000)
            tree, _ = diskscan.scan(d)
            self.assertTrue(mftscan.spot_check(tree))
            for c in tree.children:
                c.size += 5                       # the "MFT" disagrees with the real files
            self.assertFalse(mftscan.spot_check(tree))

    def test_wrong_results_fall_back(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "f.bin"), "wb") as f:
                f.write(b"x" * 1_100_000)
            bogus, exts = diskscan.scan(d)
            bogus.children[0].size = 1
            real = (object(), {})
            with mock.patch.object(mftscan, "available", return_value=True), \
                    mock.patch.object(mftscan, "scan_mft", return_value=(bogus, exts)), \
                    mock.patch.object(diskscan, "scan", return_value=real):
                self.assertEqual(mftscan.scan_drive("D")[2], "walk")


if __name__ == "__main__":
    unittest.main()
