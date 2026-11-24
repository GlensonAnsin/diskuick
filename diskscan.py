"""Disk space analyzer: scan a drive into a size tree, summarise by file type, lay out a treemap.

Plain multi-threaded directory walk, no admin rights needed (about 100k+ files/s on an SSD). Junctions/symlinks are skipped so nothing is counted twice. To keep memory low only
files of at least BIG_FILE bytes get their own node; the rest of a folder's files are lumped into one
"[N files]" node.
"""
import colorsys
import os
import queue
import threading

BIG_FILE = 1_000_000
MAX_BIG_PER_DIR = 300
REPARSE = 0x400  # FILE_ATTRIBUTE_REPARSE_POINT: junctions, symlinks, mount points


class Node:
    __slots__ = ("name", "path", "size", "files", "folders", "children", "parent", "is_dir", "lump")

    def __init__(self, name: str, path: str, is_dir: bool, parent=None, lump: bool = False):
        self.name, self.path, self.is_dir, self.parent, self.lump = name, path, is_dir, parent, lump
        self.size = 0
        self.files = 0
        self.folders = 0
        self.children: list[Node] = []

    def depth(self) -> int:
        n, d = self, 0
        while n.parent is not None:
            n, d = n.parent, d + 1
        return d


def fmt_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1000 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else (f"{n:.1f} {unit}" if n < 100 else f"{n:.0f} {unit}")
        n /= 1000
    return f"{n:.0f} TB"


def ext_of(name: str) -> str:
    i = name.rfind(".")
    return name[i:].lower() if i > 0 else "(none)"


def add_file_nodes(node: Node, big: list[Node], lump_size: int, lump_n: int):
    """Give a folder its big files as nodes and lump everything else into one "[N files]" node."""
    big.sort(key=lambda n: -n.size)
    node.children.extend(big[:MAX_BIG_PER_DIR])
    rest = big[MAX_BIG_PER_DIR:]
    lump_size += sum(f.size for f in rest)
    lump_n += len(rest)
    if lump_n:
        lump = Node(f"[{lump_n:,} files]", node.path, False, node, lump=True)
        lump.size, lump.files = lump_size, lump_n
        node.children.append(lump)


def finalize(order: list[Node]):
    """Roll sizes up to parents and sort children. `order` must list every folder after its parent."""
    for node in reversed(order):
        p = node.parent
        if p is not None:
            p.size += node.size
            p.files += node.files
            p.folders += node.folders
    for node in order:
        node.children.sort(key=lambda n: -n.size)


def remove_node(node: Node):
    """Take a deleted file/folder out of the tree and subtract it from every folder above it."""
    p = node.parent
    if p is None:
        return
    if node in p.children:
        p.children.remove(node)
    q = p
    while q is not None:
        q.size -= node.size
        q.files -= node.files
        q.folders -= node.folders + (1 if node.is_dir else 0)
        q = q.parent


def scan(root: str, cancel: threading.Event | None = None, progress=None,
         workers: int = 4) -> tuple[Node, dict[str, list[int]]]:
    """Walk `root` with a few threads (folder reads wait on the disk, so they overlap well). Returns
    (tree, {extension: [bytes, file count]}). `progress(files, bytes)` is called now and then. A cancelled
    scan returns whatever was read so far."""
    root = os.path.abspath(root)
    top = Node(root, root, True)
    exts: dict[str, list[int]] = {}
    order = [top]
    lock = threading.Lock()
    totals = [0, 0, 0]          # files, bytes, files at last progress call
    todo: queue.Queue = queue.Queue()
    todo.put(top)

    def process(node: Node):
        lump_size = lump_n = size_sum = 0
        big: list[Node] = []
        dirs: list[Node] = []
        local: dict[str, list[int]] = {}
        try:
            it = os.scandir(node.path)
        except OSError:
            return
        with it:
            for e in it:
                try:
                    st = e.stat(follow_symlinks=False)
                    if e.is_dir(follow_symlinks=False):
                        if getattr(st, "st_file_attributes", 0) & REPARSE:
                            continue
                        dirs.append(Node(e.name, e.path, True, node))
                        continue
                    size = st.st_size
                except OSError:
                    continue
                rec = local.get(ext := ext_of(e.name))
                if rec is None:
                    local[ext] = [size, 1]
                else:
                    rec[0] += size
                    rec[1] += 1
                size_sum += size
                if size >= BIG_FILE:
                    f = Node(e.name, e.path, False, node)
                    f.size, f.files = size, 1
                    big.append(f)
                else:
                    lump_size += size
                    lump_n += 1
        nfiles = lump_n + len(big)
        node.size, node.files, node.folders = size_sum, nfiles, len(dirs)
        node.children.extend(dirs)
        add_file_nodes(node, big, lump_size, lump_n)
        for d in dirs:
            todo.put(d)
        with lock:
            order.extend(dirs)
            for k, v in local.items():
                rec = exts.get(k)
                if rec is None:
                    exts[k] = v
                else:
                    rec[0] += v[0]
                    rec[1] += v[1]
            totals[0] += nfiles
            totals[1] += size_sum
            if progress is not None and totals[0] - totals[2] >= 2000:
                totals[2] = totals[0]
                progress(totals[0], totals[1])

    def worker():
        while True:
            node = todo.get()
            try:
                if node is None:
                    return
                if cancel is None or not cancel.is_set():
                    process(node)
            except Exception:
                pass   # one unreadable folder must not stop the scan or hang the join below
            finally:
                todo.task_done()

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(max(1, workers))]
    for t in threads:
        t.start()
    todo.join()
    for _ in threads:
        todo.put(None)
    for t in threads:
        t.join()
    finalize(order)
    if progress is not None:
        progress(totals[0], totals[1])
    return top, exts


def top_extensions(exts: dict[str, list[int]], n: int = 12) -> list[tuple[str, int, int]]:
    """[(extension, bytes, file count)] biggest first."""
    return [(k, v[0], v[1]) for k, v in sorted(exts.items(), key=lambda kv: -kv[1][0])[:n]]


def squarify(items: list[tuple[object, float]], x: float, y: float, w: float, h: float):
    """Squarified treemap. items = [(key, size)] sorted biggest first. Returns [(key, x, y, w, h)]."""
    items = [(k, s) for k, s in items if s > 0]
    total = sum(s for _, s in items)
    if not items or w <= 0 or h <= 0 or total <= 0:
        return []
    scale = w * h / total
    areas = [(k, s * scale) for k, s in items]
    out = []

    def worst(row, side):
        s = sum(a for _, a in row)
        return max(max(side * side * a / (s * s), s * s / (side * side * a)) for _, a in row)

    i = 0
    while i < len(areas):
        side = min(w, h)
        row = [areas[i]]
        i += 1
        while i < len(areas) and worst(row + [areas[i]], side) <= worst(row, side):
            row.append(areas[i])
            i += 1
        s = sum(a for _, a in row)
        if w >= h:                       # lay the row as a column on the left
            cw = s / h
            cy = y
            for k, a in row:
                rh = a / cw
                out.append((k, x, cy, cw, rh))
                cy += rh
            x, w = x + cw, w - cw
        else:                            # lay the row along the top
            rh = s / w
            cx = x
            for k, a in row:
                cw = a / rh
                out.append((k, cx, y, cw, rh))
                cx += cw
            y, h = y + rh, h - rh
    return out


def color_for(name: str, is_dir: bool, depth: int = 0) -> str:
    """Stable colour per name, so the same folder keeps its colour; deeper levels are a bit darker."""
    hue = (sum(ord(c) * (i + 7) for i, c in enumerate(name.lower())) % 360) / 360
    sat = 0.55 if is_dir else 0.75
    val = max(0.35, 0.82 - 0.12 * depth)
    r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
