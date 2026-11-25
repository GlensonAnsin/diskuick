"""The Disk tab: a WizTree-style space analyzer (folder tree, treemap, file types) and a safe cleanup."""
import os
import shutil
import subprocess
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

import cleanup
import diskscan
import mftscan
import sysutil
from i18n import T
from widgets import (ACCENT, BORDER, CARD, FIELD, FONT, MUTED, TEXT, btn_primary, btn_secondary, card,
                     option_menu, pick)

TREEMAP_H = 340
WARN = ("#D98E04", "#F0B232")      # drive getting full
DANGER = ("#D63B3B", "#F26B6B")    # drive nearly full
STRIPE = ("#F6F8FA", "#1B1F26")
LUMP_COLOR = "#59616e"


class DiskTab:
    def __init__(self, win, body):
        self.win, self.body = win, body
        self.tree: diskscan.Node | None = None
        self.cur: diskscan.Node | None = None
        self.exts: dict = {}
        self._cancel = threading.Event()
        self._scanning = False
        self._rects: list = []
        self.selected: diskscan.Node | None = None
        self._sizes: dict[str, tuple[int, int]] = {}
        self._busy = False
        self._build_analyzer()
        self._build_cleanup()

    # ------------------------------------------------------------ analyzer ----
    def _build_analyzer(self):
        body = self.body
        self.choices = sysutil.drive_choices() or {"C:": "C"}
        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(top, text=T("Drive to analyze"), font=(FONT, 13, "bold"), text_color=TEXT).pack(side="left")
        self.scan_btn = btn_primary(top, T("Scan"), self._toggle_scan, width=90, height=34)
        self.scan_btn.pack(side="right")
        self.drive_var = ctk.StringVar(value=next(iter(self.choices)))
        option_menu(top, self.drive_var, list(self.choices), width=230).pack(side="right", padx=(0, 8))

        a = card(body, T("Disk space analyzer"),
                 T("Shows what is taking up space, biggest first. Nothing is changed or deleted here. Running as "
                   "administrator reads the drive's file table directly (like WizTree), which takes seconds; "
                   "otherwise it reads folders one by one, which can take a minute or two."))
        self.status = ctk.CTkLabel(a, text=T("Press Scan to start."), font=(FONT, 12), text_color=MUTED,
                                   anchor="w", justify="left", wraplength=520)
        self.status.pack(fill="x", padx=16, pady=(8, 0))
        self.stats = ctk.CTkFrame(a, fg_color="transparent")      # size / files / folders / free tiles, after a scan
        self.stats.pack(fill="x", padx=16)
        self.bar = ctk.CTkProgressBar(a, progress_color=ACCENT, fg_color=FIELD, height=8, mode="indeterminate")
        if not mftscan.is_admin():
            row = ctk.CTkFrame(a, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=(8, 0))
            btn_secondary(row, T("Restart as administrator for a fast scan"), self.win.app.restart_as_admin,
                          height=30).pack(side="left")

        nav = ctk.CTkFrame(a, fg_color="transparent")
        nav.pack(fill="x", padx=16, pady=(8, 4))
        self.up_btn = btn_secondary(nav, T("Up"), self._up, width=60, height=28)
        self.up_btn.pack(side="left")
        self.open_btn = btn_secondary(nav, T("Open in Explorer"), self._open_current, width=130, height=28)
        self.open_btn.pack(side="right")
        self.del_btn = btn_secondary(nav, T("Move to Recycle Bin"), self._delete_selected, width=150, height=28,
                                     state="disabled", text_color_disabled=MUTED)
        self.del_btn.pack(side="right", padx=(0, 6))
        self.crumb = ctk.CTkLabel(nav, text="", font=(FONT, 12, "bold"), text_color=TEXT, anchor="w")
        self.crumb.pack(side="left", fill="x", expand=True, padx=10)

        self.canvas = tk.Canvas(a, height=TREEMAP_H, bg=pick(CARD), highlightthickness=0, cursor="hand2")
        self.canvas.pack(fill="x", padx=12, pady=(2, 4))
        self.canvas.bind("<Button-1>", self._tm_click)
        self.canvas.bind("<Double-Button-1>", self._tm_double)
        self.canvas.bind("<Button-3>", self._tm_menu)
        self.canvas.bind("<Configure>", lambda e: self._draw())
        self.canvas.bind("<Motion>", self._tm_move)
        self.canvas.bind("<Leave>", lambda e: self._set_hover(None))
        self._hover_node = None
        self.hover = ctk.CTkLabel(a, text="", font=(FONT, 11), text_color=MUTED, anchor="w")
        self.hover.pack(fill="x", padx=16)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Disk.Treeview", background=pick(CARD), fieldbackground=pick(CARD), foreground=pick(TEXT),
                        rowheight=24, borderwidth=0, font=(FONT, 10))
        style.configure("Disk.Treeview.Heading", background=pick(FIELD), foreground=pick(TEXT), relief="flat",
                        font=(FONT, 10, "bold"))
        style.map("Disk.Treeview", background=[("selected", pick(ACCENT))], foreground=[("selected", "#06210F")])
        holder = ctk.CTkFrame(a, fg_color="transparent")
        holder.pack(fill="x", padx=12, pady=(4, 14))
        self.table = ttk.Treeview(holder, columns=("pct", "size", "files"), height=14, style="Disk.Treeview")
        self.table.tag_configure("odd", background=pick(STRIPE))
        self._sort = ("size", True)                       # (column, biggest first)
        self._titles = {"#0": T("Name"), "pct": T("% of parent"), "size": T("Size"), "files": T("Files")}
        for col, w, anchor in (("#0", 230, "w"), ("pct", 90, "e"), ("size", 90, "e"), ("files", 80, "e")):
            self.table.heading(col, command=lambda c=col: self._sort_by(c))
            self.table.column(col, width=w, anchor=anchor, stretch=(col == "#0"))
        self._heading_text()
        sb = ttk.Scrollbar(holder, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=sb.set)
        self.table.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.table.bind("<Double-Button-1>", self._table_double)
        self.table.bind("<<TreeviewSelect>>", self._table_select)
        self._row_nodes: dict[str, diskscan.Node] = {}

        self.types_card = card(body, T("File types"), T("Which kinds of files use the most space on this drive."))
        self.types_box = ctk.CTkFrame(self.types_card, fg_color="transparent")
        self.types_box.pack(fill="x", padx=16, pady=(6, 12))
        self._draw()

    def _toggle_scan(self):
        if self._scanning:
            self._cancel.set()
            self.scan_btn.configure(text=T("Stopping..."), state="disabled")
            return
        letter = self.choices.get(self.drive_var.get(), "C")
        self._t_scan = time.time()
        self._cancel = threading.Event()
        cancel = self._cancel
        self._scanning = True
        self.scan_btn.configure(text=T("Stop"))
        self.bar.pack(fill="x", padx=16, pady=(6, 0), after=self.status)
        self.bar.start()
        self.status.configure(text=T("Scanning {drive}: ...").format(drive=letter))

        def progress(files, size):
            self.win.post(lambda: self._scanning and self.status.configure(
                text=T("Scanning {drive}: {files} files, {size} so far").format(
                    drive=letter, files=f"{files:,}", size=diskscan.fmt_size(size))))

        def work():
            tree, exts, method = mftscan.scan_drive(letter, cancel, progress)
            self.win.post(lambda: self._scan_done(tree, exts, letter, cancel.is_set(), method))

        threading.Thread(target=work, daemon=True).start()

    def _scan_done(self, tree, exts, letter, cancelled, method="walk"):
        self._scanning = False
        try:
            self.bar.stop()
            self.bar.pack_forget()
            self.scan_btn.configure(text=T("Scan"), state="normal")
        except tk.TclError:
            return  # window was closed mid-scan
        self.tree, self.exts = tree, exts
        try:
            du = shutil.disk_usage(f"{letter}:\\")
            used = f"{diskscan.fmt_size(du.used)} / {diskscan.fmt_size(du.total)}"
        except OSError:
            used = ""
        self._show_stats(tree, letter)
        msg = T("Took {s} s.").format(s=f"{time.time() - self._t_scan:.0f}")
        if cancelled:
            msg += "  " + T("Stopped early, so this is partial.")
        elif method == "mft":
            msg += "  " + T("Fast scan (NTFS file table).")
        elif tree.size < (du.used * 0.6 if used else 0):
            msg += "  " + T("Some folders are protected; run as administrator to include them.")
        elif not mftscan.is_admin() and mftscan.filesystem(letter).upper() == "NTFS":
            msg += "  " + T("Run Diskuick as administrator for a much faster scan.")
        self.status.configure(text=msg)
        self._navigate(tree)
        self._show_types()

    def _show_types(self):
        for w in self.types_box.winfo_children():
            w.destroy()
        total = max(sum(v[0] for v in self.exts.values()), 1)
        for ext, size, n in diskscan.top_extensions(self.exts, 12):
            r = ctk.CTkFrame(self.types_box, fg_color="transparent")
            r.pack(fill="x", pady=2)
            color = diskscan.color_for(ext, False)
            ctk.CTkLabel(r, text="●", width=16, font=(FONT, 12), text_color=color).pack(side="left")
            ctk.CTkLabel(r, text=ext, width=72, anchor="w", font=(FONT, 12, "bold"), text_color=TEXT).pack(side="left")
            ctk.CTkLabel(r, text=f"{size / total * 100:.1f}%  ·  {diskscan.fmt_size(size)}  ·  {n:,}", width=190,
                         font=(FONT, 11), text_color=MUTED, anchor="e").pack(side="right")
            b = ctk.CTkProgressBar(r, height=10, fg_color=FIELD, progress_color=color, corner_radius=5)
            b.set(size / total)
            b.pack(side="left", fill="x", expand=True, padx=8)

    def _tile(self, parent, col, value, caption):
        f = ctk.CTkFrame(parent, fg_color=FIELD, corner_radius=10)
        f.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 6, 0))
        parent.columnconfigure(col, weight=1, uniform="tile")
        ctk.CTkLabel(f, text=value, font=(FONT, 16, "bold"), text_color=TEXT, anchor="w").pack(
            anchor="w", padx=12, pady=(8, 0))
        ctk.CTkLabel(f, text=caption, font=(FONT, 11), text_color=MUTED, anchor="w").pack(
            anchor="w", padx=12, pady=(0, 8))

    def _show_stats(self, tree, letter):
        """Size / files / folders / free tiles plus a bar of how full the drive is."""
        for w in self.stats.winfo_children():
            w.destroy()
        try:
            du = shutil.disk_usage(f"{letter}:\\")
        except OSError:
            du = None
        tiles = ctk.CTkFrame(self.stats, fg_color="transparent")
        tiles.pack(fill="x", pady=(10, 0))
        self._tile(tiles, 0, diskscan.fmt_size(tree.size), T("Size"))
        self._tile(tiles, 1, f"{tree.files:,}", T("Files"))
        self._tile(tiles, 2, f"{tree.folders:,}", T("Folders"))
        if du:
            self._tile(tiles, 3, diskscan.fmt_size(du.free), T("Free"))
            frac = du.used / du.total if du.total else 0
            color = DANGER if frac >= 0.95 else WARN if frac >= 0.85 else ACCENT
            row = ctk.CTkFrame(self.stats, fg_color="transparent")
            row.pack(fill="x", pady=(8, 0))
            ctk.CTkLabel(row, text=T("Drive used: {used}.").format(
                used=f"{diskscan.fmt_size(du.used)} / {diskscan.fmt_size(du.total)}  ({frac * 100:.0f}%)"),
                font=(FONT, 11), text_color=MUTED, anchor="w").pack(anchor="w")
            bar = ctk.CTkProgressBar(row, height=10, corner_radius=5, fg_color=FIELD, progress_color=color)
            bar.set(min(frac, 1))
            bar.pack(fill="x", pady=(3, 0))

    # navigation
    def _navigate(self, node):
        self.cur = node
        self._select(None)
        self.crumb.configure(text=node.path)
        self.up_btn.configure(state="normal" if node.parent is not None else "disabled")
        self._fill_table()
        self._draw()

    def _up(self):
        if self.cur is not None and self.cur.parent is not None:
            self._navigate(self.cur.parent)

    def _heading_text(self):
        col, desc = self._sort
        for c, title in self._titles.items():
            arrow = (" ▼" if desc else " ▲") if c == col else ""
            self.table.heading(c, text=title + arrow)

    def _sort_by(self, col):
        """Click a column heading: sort by it; click again to flip the order."""
        c, desc = self._sort
        self._sort = (col, not desc) if col == c else (col, col != "#0")
        self._heading_text()
        self._fill_table()

    def _fill_table(self):
        self.table.delete(*self.table.get_children())
        self._row_nodes.clear()
        node = self.cur
        if node is None:
            return
        col, desc = self._sort
        self.table.configure(height=max(4, min(14, len(node.children))))   # no big empty block for small folders
        key = {"#0": lambda n: n.name.lower(), "files": lambda n: n.files}.get(col, lambda n: n.size)
        for i, ch in enumerate(sorted(node.children, key=key, reverse=desc)[:500]):
            pct = f"{ch.size / node.size * 100:.1f} %" if node.size else ""
            name = ("📁 " if ch.is_dir else "📄 " if not ch.lump else "🗂 ") + ch.name
            iid = str(i)
            self.table.insert("", "end", iid=iid, text=name, tags=("odd",) if i % 2 else (),
                              values=(pct, diskscan.fmt_size(ch.size), f"{ch.files:,}"))
            self._row_nodes[iid] = ch

    def _select(self, node):
        """Remember the clicked item and enable the delete button only where deleting is allowed."""
        self.selected = node
        ok = node is not None and not node.lump and node.parent is not None and not cleanup.protected_reason(node.path)
        self.del_btn.configure(state="normal" if ok else "disabled")

    def _table_select(self, _e):
        sel = self.table.selection()
        self._select(self._row_nodes.get(sel[0]) if sel else None)

    def _delete_selected(self):
        node = self.selected
        if node is None or node.lump or cleanup.protected_reason(node.path):
            return
        kind = T("folder") if node.is_dir else T("file")
        if not messagebox.askyesno("Diskuick", T("Move this {kind} to the Recycle Bin?\n\n{path}\n{size}\n\n"
                                                  "You can restore it from the Recycle Bin.").format(
                kind=kind, path=node.path, size=diskscan.fmt_size(node.size)), parent=self.win):
            return
        self.del_btn.configure(state="disabled")
        self.status.configure(text=T("Moving to the Recycle Bin..."))

        def work():
            ok = cleanup.recycle(node.path)
            self.win.post(lambda: self._deleted(node, ok))

        threading.Thread(target=work, daemon=True).start()

    def _deleted(self, node, ok):
        if not ok:
            self.status.configure(text=T("Could not move it to the Recycle Bin (in use, protected or cancelled)."))
            self._select(node)
            return
        diskscan.remove_node(node)
        self.status.configure(text=T("Moved {size} to the Recycle Bin. Scan again to refresh the file types.").format(
            size=diskscan.fmt_size(node.size)))
        self._navigate(self.cur)

    def _table_double(self, _e):
        sel = self.table.selection()
        node = self._row_nodes.get(sel[0]) if sel else None
        if node is not None and node.is_dir:
            self._navigate(node)

    # treemap
    def _draw(self):
        c = self.canvas
        c.delete("all")
        self._rects = []
        self._hover_node = None
        node = self.cur
        if node is None or node.size <= 0:
            c.create_text(c.winfo_width() / 2 or 250, TREEMAP_H / 2, fill=pick(MUTED), font=(FONT, 11),
                          text=T("Scan a drive to see its map here."))
            return
        self._layout(node, 1, 1, max(c.winfo_width(), 300) - 2, TREEMAP_H - 2, 0)

    def _layout(self, node, x, y, w, h, depth):
        c, bg = self.canvas, pick(CARD)
        for child, cx, cy, cw, ch in diskscan.squarify([(n, n.size) for n in node.children], x, y, w, h):
            if cw < 3 or ch < 3:
                continue
            color = LUMP_COLOR if child.lump else diskscan.color_for(child.name, child.is_dir, depth)
            c.create_rectangle(cx, cy, cx + cw, cy + ch, fill=color, outline=bg, width=1)
            self._rects.append((cx, cy, cx + cw, cy + ch, child))
            nested = child.is_dir and depth < 2 and cw > 46 and ch > 34 and child.children
            if cw > 56 and ch > 15:
                label = f"{child.name}  ({diskscan.fmt_size(child.size)})" if ch > 30 or nested else child.name
                c.create_text(cx + 4, cy + 2, anchor="nw", text=label, fill="#ffffff", font=(FONT, 8, "bold"),
                              width=cw - 6)
            if nested:
                self._layout(child, cx + 2, cy + 15, cw - 4, ch - 17, depth + 1)

    def _hit(self, x, y):
        for x0, y0, x1, y1, node in reversed(self._rects):
            if x0 <= x <= x1 and y0 <= y <= y1:
                return node
        return None

    def _outline(self, node, tag, color, width):
        self.canvas.delete(tag)
        for x0, y0, x1, y1, n in self._rects:
            if n is node:
                self.canvas.create_rectangle(x0 + 1, y0 + 1, x1 - 1, y1 - 1, outline=color, width=width, tags=tag)
                return

    def _describe(self, n):
        return (f"{n.path if not n.lump else n.name}   ·   {diskscan.fmt_size(n.size)}"
                f"   ·   {n.files:,} {T('Files').lower()}")

    def _set_hover(self, n):
        """Outline the block under the mouse and describe it (or the selection once the mouse leaves)."""
        if n is self._hover_node:
            return
        self._hover_node = n
        self.canvas.delete("hl")
        if n is not None:
            self._outline(n, "hl", "#FFFFFF", 2)
            self.hover.configure(text=self._describe(n))
        elif self.selected is not None:
            self.hover.configure(text=self._describe(self.selected))
        else:
            self.hover.configure(text="")

    def _tm_move(self, e):
        self._set_hover(self._hit(e.x, e.y))

    def _tm_click(self, e):
        n = self._hit(e.x, e.y)
        if n is not None:
            self._select(n)
            self._outline(n, "sel", pick(ACCENT), 3)
            self.hover.configure(text=self._describe(n))

    def _tm_double(self, e):
        n = self._hit(e.x, e.y)
        if n is not None and n.is_dir:
            self._navigate(n)

    def _tm_menu(self, e):
        n = self._hit(e.x, e.y)
        if n is None:
            return
        m = tk.Menu(self.canvas, tearoff=0)
        m.add_command(label=T("Open in Explorer"), command=lambda: self._explore(n))
        if n.is_dir and n is not self.cur:
            m.add_command(label=T("Open this folder here"), command=lambda: self._navigate(n))
        m.tk_popup(e.x_root, e.y_root)

    def _open_current(self):
        if self.cur is not None:
            self._explore(self.cur)

    @staticmethod
    def _explore(node):
        try:
            if node.is_dir or node.lump:
                os.startfile(node.path)
            else:
                subprocess.Popen(f'explorer /select,"{node.path}"')
        except OSError:
            pass

    # -------------------------------------------------------------- cleanup ----
    def _build_cleanup(self):
        c = card(self.body, T("Disk cleanup"),
                 T("Removes only safe, regenerable leftovers: temporary files, caches and crash reports. Your own "
                   "files are never touched. Tick what you want, check the sizes, then clean."))
        self.cats = cleanup.categories()
        self.cat_vars: dict[str, ctk.BooleanVar] = {}
        self.cat_labels: dict[str, ctk.CTkLabel] = {}
        for cat in self.cats:
            row = ctk.CTkFrame(c, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=3)
            var = ctk.BooleanVar(value=cat.default)
            self.cat_vars[cat.key] = var
            ctk.CTkCheckBox(row, text="", variable=var, width=24, checkbox_width=20, checkbox_height=20,
                            fg_color=ACCENT, border_color=BORDER).pack(side="left", anchor="n", pady=2)
            txt = ctk.CTkFrame(row, fg_color="transparent")
            txt.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(txt, text=T(cat.title), font=(FONT, 13, "bold"), text_color=TEXT, anchor="w").pack(anchor="w")
            ctk.CTkLabel(txt, text=T(cat.hint), font=(FONT, 11), text_color=MUTED, anchor="w", justify="left",
                         wraplength=400).pack(anchor="w")
            lbl = ctk.CTkLabel(row, text="", font=(FONT, 12, "bold"), text_color=TEXT, width=90, anchor="e")
            lbl.pack(side="right")
            self.cat_labels[cat.key] = lbl
        self.clean_status = ctk.CTkLabel(c, text="", font=(FONT, 12), text_color=MUTED, anchor="w",
                                         justify="left", wraplength=520)
        self.clean_status.pack(fill="x", padx=16, pady=(8, 0))
        btns = ctk.CTkFrame(c, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(8, 14))
        self.check_btn = btn_secondary(btns, T("Check sizes"), self._check_sizes, width=120)
        self.check_btn.pack(side="left")
        self.clean_btn = btn_primary(btns, T("Clean selected"), self._clean, width=140)
        self.clean_btn.pack(side="left", padx=8)

    def _set_busy(self, busy: bool, text: str = ""):
        self._busy = busy
        state = "disabled" if busy else "normal"
        try:
            self.check_btn.configure(state=state)
            self.clean_btn.configure(state=state)
            self.clean_status.configure(text=text)
        except tk.TclError:
            pass

    def _check_sizes(self, then=None):
        if self._busy:
            return
        self._set_busy(True, T("Checking sizes..."))

        def work():
            sizes = {c.key: cleanup.measure(c) for c in self.cats}
            self.win.post(lambda: self._sizes_done(sizes, then))

        threading.Thread(target=work, daemon=True).start()

    def _sizes_done(self, sizes, then):
        self._update_labels(sizes)
        total = sum(sizes[k][0] for k, v in self.cat_vars.items() if v.get())
        self._set_busy(False, T("Ticked items would free about {size}.").format(size=diskscan.fmt_size(total)))
        if then:
            then()

    def _selected(self) -> list[cleanup.Category]:
        return [c for c in self.cats if self.cat_vars[c.key].get()]

    def _clean(self):
        if self._busy:
            return
        picked = self._selected()
        if not picked:
            self.clean_status.configure(text=T("Tick at least one item first."))
            return
        if not self._sizes:
            self._check_sizes(then=self._clean)   # show sizes first, then ask
            return
        total = sum(self._sizes.get(c.key, (0, 0))[0] for c in picked)
        names = "\n".join("• " + T(c.title) for c in picked)
        note = ""
        if any(c.recycle_bin for c in picked):
            note = "\n\n" + T("The Recycle Bin is emptied permanently.")
        if not messagebox.askyesno("Diskuick", T("Remove about {size} from:\n\n{names}{note}\n\nContinue?").format(
                size=diskscan.fmt_size(total), names=names, note=note), parent=self.win):
            return
        self._set_busy(True, T("Cleaning..."))

        def work():
            freed = removed = 0
            try:
                for i, cat in enumerate(picked, 1):
                    head = f"{T('Cleaning...')} {T(cat.title)} ({i}/{len(picked)})"
                    self.win.post(lambda h=head: self.clean_status.configure(text=h))

                    def prog(f, n, h=head, base=(freed, removed)):
                        self.win.post(lambda: self.clean_status.configure(
                            text=f"{h} - {diskscan.fmt_size(base[0] + f)}"))
                    try:
                        b, n = cleanup.clean(cat, progress=prog)
                    except Exception:
                        b = n = 0        # one failing category must not leave the screen stuck
                    freed, removed = freed + b, removed + n
            finally:
                self.win.post(lambda: self._clean_done(freed, removed))

        threading.Thread(target=work, daemon=True).start()

    def _clean_done(self, freed, removed):
        self._set_busy(False, T("Freed {size} ({files} files). Items in use were skipped.").format(
            size=diskscan.fmt_size(freed), files=f"{removed:,}"))
        self._sizes = {}
        for lbl in self.cat_labels.values():
            lbl.configure(text="")
        self._check_sizes_quiet()

    def _check_sizes_quiet(self):
        def work():
            sizes = {c.key: cleanup.measure(c) for c in self.cats}
            self.win.post(lambda: self._update_labels(sizes))

        threading.Thread(target=work, daemon=True).start()

    def _update_labels(self, sizes):
        self._sizes = sizes
        for key, (b, n) in sizes.items():
            self.cat_labels[key].configure(text=diskscan.fmt_size(b) if n or b else "—")

    def cancel(self):
        self._cancel.set()
