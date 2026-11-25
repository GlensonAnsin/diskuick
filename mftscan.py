"""Fast disk scan by reading the NTFS Master File Table (MFT) straight from the volume, like WizTree.

Read-only. It needs administrator rights (raw volume access) and an NTFS drive; otherwise, or if anything
looks wrong (read error, odd layout, results that don't match the real filesystem on a spot check),
`scan_drive` quietly falls back to the normal folder walk in diskscan.py.

Only the unnamed data stream of each file is counted (alternate data streams are ignored) and a file with
several hard links is counted once. Names/sizes come from each file's base MFT record.
"""
import collections
import concurrent.futures
import concurrent.futures.process
import ctypes
import os
import random
import struct
import threading
import time
from array import array
from collections import defaultdict
from multiprocessing import shared_memory

import diskscan
from diskscan import BIG_FILE, Node, add_file_nodes, ext_of, finalize

MASK48 = (1 << 48) - 1
ROOT_RECORD = 5
CHUNK = 4 * 1024 * 1024
REPARSE = 0x400

u16 = struct.Struct("<H").unpack_from
u32 = struct.Struct("<I").unpack_from
u64 = struct.Struct("<Q").unpack_from


class MftError(Exception):
    pass


# ------------------------------------------------------------------ helpers ----
def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (OSError, AttributeError):
        return False


def filesystem(letter: str) -> str:
    buf = ctypes.create_unicode_buffer(32)
    try:
        ok = ctypes.windll.kernel32.GetVolumeInformationW(f"{letter}:\\", None, 0, None, None, None, buf, 32)
    except (OSError, AttributeError):
        return ""
    return buf.value if ok else ""


def available(letter: str) -> bool:
    return is_admin() and filesystem(letter).upper() == "NTFS"


def apply_fixups(rec: bytearray) -> bool:
    """Undo NTFS' update-sequence protection: the last 2 bytes of every 512-byte block were swapped for a
    check value. Returns False if the record looks torn."""
    off, count = u16(rec, 4)[0], u16(rec, 6)[0]
    if count < 2 or off + 2 * count > len(rec):
        return False
    usn = rec[off:off + 2]
    for i in range(1, count):
        end = i * 512
        if end > len(rec) or rec[end - 2:end] != usn:
            return False
        rec[end - 2:end] = rec[off + 2 * i:off + 2 * i + 2]
    return True


def parse_runs(data: bytes) -> list[tuple[int | None, int]]:
    """Decode an NTFS data-run list into [(first cluster or None if sparse, cluster count)]."""
    runs, pos, lcn = [], 0, 0
    while pos < len(data) and data[pos]:
        head = data[pos]
        n_len, n_off = head & 0xF, head >> 4
        pos += 1
        length = int.from_bytes(data[pos:pos + n_len], "little")
        pos += n_len
        if n_off == 0:
            runs.append((None, length))
        else:
            lcn += int.from_bytes(data[pos:pos + n_off], "little", signed=True)
            runs.append((lcn, length))
        pos += n_off
    return runs


class Boot:
    def __init__(self, sector: bytes):
        if sector[3:11] != b"NTFS    ":
            raise MftError("not an NTFS volume")
        self.sector_size = u16(sector, 0x0B)[0]
        self.cluster = self.sector_size * sector[0x0D]
        self.mft_lcn = u64(sector, 0x30)[0]
        n = struct.unpack_from("<b", sector, 0x40)[0]
        self.record = n * self.cluster if n > 0 else 1 << -n
        if self.sector_size not in (512, 1024, 2048, 4096) or self.cluster < 512 or self.record < 512:
            raise MftError("unexpected NTFS geometry")


def mft_extents(rec0: bytes, boot: Boot) -> tuple[list, int]:
    """Where the MFT itself lives on disk: ([(lcn, clusters)], size in bytes), from its own record 0."""
    rec = bytearray(rec0)
    if rec[:4] != b"FILE" or not apply_fixups(rec):
        raise MftError("bad MFT record 0")
    off = u16(rec, 0x14)[0]
    while off + 8 <= len(rec):
        atype, alen = u32(rec, off)[0], u32(rec, off + 4)[0]
        if atype == 0xFFFFFFFF or alen == 0:
            break
        if atype == 0x80 and rec[off + 9] == 0:
            if rec[off + 8] == 0:
                raise MftError("MFT data is resident")
            size = u64(rec, off + 0x30)[0]
            runs = parse_runs(bytes(rec[off + u16(rec, off + 0x20)[0]:off + alen]))
            if any(lcn is None for lcn, _ in runs) or sum(n for _, n in runs) * boot.cluster < size:
                raise MftError("MFT layout not supported (fragmented beyond its first record)")
            return runs, size
        off += alen
    raise MftError("MFT data attribute not found")


# ------------------------------------------------------------------ parsing ----
class _Sink:
    """What parse_chunk fills in. Catalog is the whole-volume one; Partial is what a worker process builds
    for one chunk (plain dicts, cheap to send back) and Catalog.merge folds it in."""

    def __init__(self, total: int):
        self.total = total
        self.big: dict[int, list[tuple[str, int]]] = defaultdict(list)    # parent -> [(name, size)]
        self.exts: dict[str, list[int]] = {}
        self.files = 0
        self.bytes = 0
        # Heavily fragmented files keep their data attribute in a separate "extension" record, possibly
        # stored after the file's own record, so those files are settled once every record has been read.
        self.pending: list[tuple[int, int, str, int]] = []     # (record, parent, name, size from the name)
        self.ext_data: dict[int, int] = {}                     # record -> real size from its extension record

    def add_file(self, parent: int, name: str, size: int):
        self.files += 1
        self.bytes += size
        ext = ext_of(name)
        slot = self.exts.get(ext)
        if slot is None:
            self.exts[ext] = [size, 1]
        else:
            slot[0] += size
            slot[1] += 1
        if size >= BIG_FILE:
            self.big[parent].append((name, size))
        else:
            self.lump_size[parent] += size
            self.lump_n[parent] += 1

    def note_extension(self, rec: bytearray, base: int):
        off = u16(rec, 0x14)[0]
        while off + 8 <= len(rec):
            atype = u32(rec, off)[0]
            if atype == 0xFFFFFFFF:
                break
            alen = u32(rec, off + 4)[0]
            if alen < 8 or off + alen > len(rec):
                break
            if atype == 0x80 and rec[off + 9] == 0 and rec[off + 8] == 1 and u64(rec, off + 0x10)[0] == 0:
                self.ext_data[base] = u64(rec, off + 0x30)[0]    # first fragment of the data attribute
            off += alen



class Partial(_Sink):
    def __init__(self, total: int):
        super().__init__(total)
        self.is_dir: dict[int, int] = {}
        self.parent: dict[int, int] = {}
        self.names: dict[int, str] = {}
        self.lump_size: dict[int, int] = defaultdict(int)
        self.lump_n: dict[int, int] = defaultdict(int)


class Catalog(_Sink):
    """Everything learned about the volume from the MFT records, indexed by record number."""

    def __init__(self, total: int):
        super().__init__(total)
        self.parent = array("I", bytes(4 * total))
        self.is_dir = bytearray(total)
        self.lump_size = array("Q", bytes(8 * total))
        self.lump_n = array("I", bytes(4 * total))
        self.names: dict[int, str] = {}                                   # directories only

    def merge(self, part: Partial):
        for idx, name in part.names.items():
            self.names[idx] = name
            self.is_dir[idx] = 1
            self.parent[idx] = part.parent[idx]
        for p, v in part.lump_size.items():
            self.lump_size[p] += v
        for p, v in part.lump_n.items():
            self.lump_n[p] += v
        for p, lst in part.big.items():
            self.big[p].extend(lst)
        for k, (size, n) in part.exts.items():
            slot = self.exts.get(k)
            if slot is None:
                self.exts[k] = [size, n]
            else:
                slot[0] += size
                slot[1] += n
        self.files += part.files
        self.bytes += part.bytes
        self.pending.extend(part.pending)
        self.ext_data.update(part.ext_data)

    def resolve(self):
        for idx, parent, name, size in self.pending:
            self.add_file(parent, name, self.ext_data.get(idx, size))
        self.pending.clear()


def parse_chunk(buf: bytes, rl: int, first: int, cat: Catalog) -> int:
    """Read every whole record in `buf` (the first one is record number `first`) into `cat`.
    Returns how many bytes of `buf` were consumed (a multiple of the record size)."""
    n_total = cat.total
    count = len(buf) // rl
    for k in range(count):
        idx, pos = first + k, k * rl
        if idx >= n_total or buf[pos:pos + 4] != b"FILE":
            continue
        flags = u16(buf, pos + 0x16)[0]
        if not flags & 1:
            continue
        rec = bytearray(buf[pos:pos + rl])
        if not apply_fixups(rec):
            continue
        base = u64(rec, 0x20)[0] & MASK48
        if base:                                                  # an extension of another file's record
            cat.note_extension(rec, base)
            continue
        name = None
        ns_cur = 9
        parent = fattr = fsize = 0
        dsize = None
        reparse = False
        off = u16(rec, 0x14)[0]
        while off + 8 <= rl:
            atype = u32(rec, off)[0]
            if atype == 0xFFFFFFFF:
                break
            alen = u32(rec, off + 4)[0]
            if alen < 8 or off + alen > rl:
                break
            if atype == 0x30 and rec[off + 8] == 0:
                c = off + u16(rec, off + 0x14)[0]
                ns = rec[c + 0x41]
                if name is None or (ns_cur == 2 and ns != 2):      # prefer the long name over the 8.3 one
                    ns_cur = ns
                    parent = u64(rec, c)[0] & MASK48
                    fsize = u64(rec, c + 0x30)[0]
                    fattr = u32(rec, c + 0x38)[0]
                    name = rec[c + 0x42:c + 0x42 + 2 * rec[c + 0x40]].decode("utf-16-le", "replace")
            elif atype == 0x80 and rec[off + 9] == 0:
                dsize = u32(rec, off + 0x10)[0] if rec[off + 8] == 0 else u64(rec, off + 0x30)[0]
            elif atype == 0xC0:                                   # $REPARSE_POINT
                reparse = True
            off += alen
        if name is None:
            continue
        if flags & 2:
            if (reparse or fattr & REPARSE) and idx != ROOT_RECORD:   # junction / symlink / mount point
                continue
            cat.is_dir[idx] = 1
            cat.parent[idx] = parent
            cat.names[idx] = name
            continue
        if parent >= n_total:
            continue
        if dsize is None:
            cat.pending.append((idx, parent, name, fsize))
        else:
            cat.add_file(parent, name, dsize)
    return count * rl


def build_tree(cat: Catalog, root_path: str) -> Node:
    """Turn the catalog into the same Node tree diskscan.scan produces, starting from the root folder."""
    cat.resolve()
    kids: dict[int, list[int]] = defaultdict(list)
    for d in cat.names:
        if d != ROOT_RECORD:
            kids[cat.parent[d]].append(d)
    top = Node(root_path, root_path, True)
    order, stack = [top], [(ROOT_RECORD, top)]
    while stack:
        rec_no, node = stack.pop()
        bigs = []
        for name, size in cat.big.get(rec_no, ()):
            f = Node(name, os.path.join(node.path, name), False, node)
            f.size, f.files = size, 1
            bigs.append(f)
        lump_n = cat.lump_n[rec_no]
        node.size = cat.lump_size[rec_no] + sum(f.size for f in bigs)
        node.files = lump_n + len(bigs)
        child_dirs = [(d, Node(cat.names[d], os.path.join(node.path, cat.names[d]), True, node))
                      for d in kids.get(rec_no, ())]
        node.children.extend(c for _, c in child_dirs)
        node.folders = len(child_dirs)
        add_file_nodes(node, bigs, cat.lump_size[rec_no], lump_n)
        for d, child in child_dirs:
            order.append(child)
            stack.append((d, child))
    finalize(order)
    return top


# -------------------------------------------------------------------- volume ----
def _read_exact(f, offset: int, size: int) -> bytes:
    f.seek(offset)
    data = f.read(size)
    if len(data) != size:
        raise MftError("short read from the volume")
    return data


last_timing: dict = {}      # seconds spent in the last scan_mft, for diagnosing slow scans


_attached = {}      # per worker process: shared-memory blocks it has opened


def parse_in_worker(shm_name: str, nbytes: int, rl: int, first: int, total: int) -> Partial:
    """Runs in a worker process: parse one piece of the MFT that the main process left in shared memory."""
    shm = _attached.get(shm_name)
    if shm is None:
        shm = _attached[shm_name] = shared_memory.SharedMemory(name=shm_name)
    part = Partial(total)
    parse_chunk(bytes(shm.buf[:nbytes]), rl, first, part)
    return part


def parse_in_worker_local(buf: bytes, rl: int, first: int, total: int) -> Partial:
    """Same as parse_in_worker, but for bytes already in hand (used by tests)."""
    part = Partial(total)
    parse_chunk(buf, rl, first, part)
    return part


def plan_pieces(runs, boot: Boot, data_size: int, piece: int = 8 * 1024 * 1024):
    """Split the MFT into [(first record number, disk offset, bytes)] pieces of whole records, or None if the
    layout doesn't allow that (then the scan reads it in this process instead)."""
    rl = boot.record
    pieces, number, remaining = [], 0, data_size
    for lcn, clusters in runs:
        pos, length = lcn * boot.cluster, min(clusters * boot.cluster, remaining)
        if length % rl:
            return None
        while length > 0:
            n = min(piece // rl * rl, length)
            pieces.append((number, pos, n))
            number, pos, length, remaining = number + n // rl, pos + n, length - n, remaining - n
    return pieces if remaining == 0 else None


def _chunks(f, boot: Boot, runs, data_size: int, cancel):
    """Yield (first record number, bytes of whole records) reading the MFT in big sequential pieces."""
    number, leftover, remaining = 0, b"", data_size
    for lcn, clusters in runs:
        pos, length = lcn * boot.cluster, clusters * boot.cluster
        while length > 0 and remaining > 0:
            if cancel is not None and cancel.is_set():
                return
            want = min(CHUNK, length)
            data = _read_exact(f, pos, want)[:remaining]
            pos, length, remaining = pos + want, length - want, remaining - len(data)
            buf = leftover + data if leftover else data
            used = len(buf) // boot.record * boot.record
            yield number, buf[:used]
            number += used // boot.record
            leftover = buf[used:]


def _parse_parallel(f, pieces, rl: int, cat: Catalog, cancel, progress, workers: int):
    """One reader goes through the MFT in order (a disk likes that) and drops each piece into shared memory;
    several processes parse pieces on their own CPU cores meanwhile, so reading is the only waiting left."""
    timing = last_timing
    timing.update(disk_read=0.0, waiting_for_parsers=0.0, merging=0.0, started=time.perf_counter())
    slot_size = max(n for _, _, n in pieces)
    blocks = [shared_memory.SharedMemory(create=True, size=slot_size) for _ in range(workers * 2 + 2)]
    free = collections.deque(range(len(blocks)))
    inflight: collections.deque = collections.deque()       # (future, slot)
    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
            def finish_oldest():
                fut, slot = inflight.popleft()
                t = time.perf_counter()
                res = fut.result()
                timing["waiting_for_parsers"] += time.perf_counter() - t
                t = time.perf_counter()
                cat.merge(res)
                timing["merging"] = timing.get("merging", 0.0) + time.perf_counter() - t
                free.append(slot)
                if progress is not None:
                    progress(cat.files, cat.bytes)
            try:
                for number, offset, nbytes in pieces:
                    if cancel is not None and cancel.is_set():
                        break
                    while not free:
                        finish_oldest()
                    slot = free.popleft()
                    f.seek(offset)
                    t = time.perf_counter()
                    if f.readinto(blocks[slot].buf[:nbytes]) != nbytes:
                        raise MftError("short read from the volume")
                    timing["disk_read"] += time.perf_counter() - t
                    inflight.append((pool.submit(parse_in_worker, blocks[slot].name, nbytes, rl, number, cat.total),
                                     slot))
                while inflight:
                    finish_oldest()
            except BaseException:
                for fut, _ in inflight:
                    fut.cancel()
                raise
    finally:
        timing['loop_done'] = round(time.perf_counter() - timing['started'], 1)
        for b in blocks:
            b.close()
            try:
                b.unlink()
            except FileNotFoundError:
                pass


def scan_mft(letter: str, cancel: threading.Event | None = None, progress=None, workers: int | None = None):
    """Scan drive `letter` via its MFT. Returns (tree, {extension: [bytes, files]}). Raises MftError/OSError
    when this isn't possible; callers fall back to diskscan.scan.

    Parsing is the slow part, so it is spread over several processes (`workers`; 1 = in this process)."""
    if workers is None:
        workers = max(1, min(os.cpu_count() or 1, 8))
    t0 = time.perf_counter()
    with open(rf"\\.\{letter}:", "rb", buffering=0) as f:
        boot = Boot(_read_exact(f, 0, 512))
        rec0 = _read_exact(f, boot.mft_lcn * boot.cluster, boot.record)
        runs, data_size = mft_extents(rec0, boot)
        cat = Catalog(data_size // boot.record)
        done = False
        pieces = plan_pieces(runs, boot, data_size) if workers > 1 else None
        if pieces:
            try:
                _parse_parallel(f, pieces, boot.record, cat, cancel, progress, workers)
                done = True
            except (concurrent.futures.process.BrokenProcessPool, OSError, RuntimeError, ImportError):
                cat = Catalog(data_size // boot.record)     # workers unavailable here: redo it in this process
        if not done:
            for number, buf in _chunks(f, boot, runs, data_size, cancel):
                parse_chunk(buf, boot.record, number, cat)
                if progress is not None:
                    progress(cat.files, cat.bytes)
    t1 = time.perf_counter()
    tree = build_tree(cat, f"{letter}:\\")
    last_timing.update(workers=workers, read_and_parse=round(t1 - t0, 1), build=round(time.perf_counter() - t1, 1))
    if progress is not None:
        progress(cat.files, cat.bytes)
    return tree, cat.exts


def spot_check(tree: Node, samples: int = 60) -> bool:
    """Compare a random sample of what the MFT said against the real filesystem."""
    files, dirs, stack = [], [], [tree]
    while stack:
        n = stack.pop()
        for c in n.children:
            if c.is_dir:
                dirs.append(c)
                if len(dirs) < 5000:
                    stack.append(c)
            elif not c.lump:
                files.append(c)
    rng = random.Random(1)
    bad = checked = 0
    for n in rng.sample(files, min(samples, len(files))) + rng.sample(dirs, min(samples // 2, len(dirs))):
        checked += 1
        try:
            ok = os.path.isdir(n.path) if n.is_dir else os.stat(n.path).st_size == n.size
        except OSError:
            ok = False
        bad += not ok
    return checked > 0 and bad <= checked * 0.15      # a few files may have changed since the scan


def scan_drive(letter: str, cancel: threading.Event | None = None, progress=None):
    """Best scan available for a drive: the MFT if we're admin on NTFS and it checks out, else the folder
    walk. Returns (tree, extensions, method) where method is "mft" or "walk"."""
    if available(letter):
        try:
            tree, exts = scan_mft(letter, cancel, progress)
            if (cancel is not None and cancel.is_set()) or (tree.files > 0 and spot_check(tree)):
                return tree, exts, "mft"
        except (MftError, OSError, struct.error, MemoryError, ValueError, IndexError):
            pass
    tree, exts = diskscan.scan(f"{letter}:\\", cancel, progress)
    return tree, exts, "walk"
