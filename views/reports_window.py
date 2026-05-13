"""
ReportsWindow – inventory statistics and audit log viewer.

Uses a ttk.Notebook with three tabs:
  1. Summary     – headline stats + per-category and per-type breakdowns
  2. Low Stock   – all products currently at/below their threshold
  3. Audit Log   – timestamped record of every inventory operation
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from views.theme import COLOURS, FONTS, PADDING


class ReportsWindow:
    """Standalone reports window – opens on top of the main window."""

    def __init__(self, parent: tk.Tk | tk.Toplevel, controller) -> None:
        self._ctrl = controller

        self.window = tk.Toplevel(parent)
        self.window.title("Reports & Analytics")
        self.window.geometry("750x540")
        self.window.minsize(650, 480)
        self.window.configure(bg=COLOURS["bg_main"])
        self.window.transient(parent)
        self.window.grab_set()

        self._build_ui()
        self._load_data()

        # Centre over parent
        self.window.update_idletasks()
        px, py = parent.winfo_x(), parent.winfo_y()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        dw, dh = self.window.winfo_width(), self.window.winfo_height()
        self.window.geometry(f"+{px + (pw - dw)//2}+{py + (ph - dh)//2}")

    # ------------------------------------------------------------------ #
    #  UI construction                                                      #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        # Header
        hdr = tk.Frame(self.window, bg=COLOURS["header_bg"], height=45)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="📊  Reports & Analytics",
            bg=COLOURS["header_bg"], fg=COLOURS["header_fg"],
            font=FONTS["subheading"], padx=PADDING["window"],
        ).pack(side="left", pady=8)

        # Refresh button in header
        tk.Button(
            hdr, text="⟳ Refresh", command=self._load_data,
            bg=COLOURS["btn_neutral"], fg=COLOURS["btn_fg"],
            font=FONTS["small"], relief="flat", padx=8, pady=3, cursor="hand2",
        ).pack(side="right", padx=PADDING["window"], pady=8)

        # Notebook
        self._notebook = ttk.Notebook(self.window)
        self._notebook.pack(fill="both", expand=True, padx=PADDING["window"], pady=PADDING["section"])

        self._summary_frame  = tk.Frame(self._notebook, bg=COLOURS["bg_main"])
        self._low_stock_frame = tk.Frame(self._notebook, bg=COLOURS["bg_main"])
        self._audit_frame    = tk.Frame(self._notebook, bg=COLOURS["bg_main"])

        self._notebook.add(self._summary_frame,   text="  Summary  ")
        self._notebook.add(self._low_stock_frame,  text="  Low Stock  ")
        self._notebook.add(self._audit_frame,      text="  Audit Log  ")

        self._build_summary_tab()
        self._build_low_stock_tab()
        self._build_audit_tab()

    def _build_summary_tab(self) -> None:
        f = self._summary_frame

        # Headline stats row
        stats_frame = tk.Frame(f, bg=COLOURS["bg_main"])
        stats_frame.pack(fill="x", padx=8, pady=8)

        self._stat_labels: dict[str, tk.Label] = {}
        for title in ("Total Products", "Total Stock Value", "Low Stock Items"):
            card = tk.Frame(stats_frame, bg=COLOURS["bg_card"], relief="flat", bd=1)
            card.pack(side="left", expand=True, fill="both", padx=4, pady=4, ipadx=12, ipady=10)
            tk.Label(card, text=title, bg=COLOURS["bg_card"], fg="#64748B", font=FONTS["small"]).pack()
            lbl = tk.Label(card, text="–", bg=COLOURS["bg_card"], fg="#0F172A", font=FONTS["heading"])
            lbl.pack()
            self._stat_labels[title] = lbl

        # Category breakdown table
        tk.Label(f, text="Breakdown by Category", bg=COLOURS["bg_main"],
                 fg="#0F172A", font=FONTS["body_bold"]).pack(anchor="w", padx=8, pady=(8, 2))

        cols = ("Category", "Products", "Stock Value (£)")
        self._cat_tree = ttk.Treeview(f, columns=cols, show="headings", height=6)
        for col in cols:
            self._cat_tree.heading(col, text=col)
            self._cat_tree.column(col, width=220, anchor="w")
        self._cat_tree.pack(fill="x", padx=8)

        # Type breakdown table
        tk.Label(f, text="Breakdown by Product Type", bg=COLOURS["bg_main"],
                 fg="#0F172A", font=FONTS["body_bold"]).pack(anchor="w", padx=8, pady=(12, 2))

        cols2 = ("Type", "Products", "Stock Value (£)")
        self._type_tree = ttk.Treeview(f, columns=cols2, show="headings", height=4)
        for col in cols2:
            self._type_tree.heading(col, text=col)
            self._type_tree.column(col, width=220, anchor="w")
        self._type_tree.pack(fill="x", padx=8, pady=(0, 8))

    def _build_low_stock_tab(self) -> None:
        f = self._low_stock_frame

        tk.Label(
            f, text="Products at or below their low stock threshold:",
            bg=COLOURS["bg_main"], fg="#0F172A", font=FONTS["body_bold"],
        ).pack(anchor="w", padx=8, pady=8)

        cols = ("ID", "Name", "Type", "Category", "Qty", "Threshold", "Value (£)")
        self._ls_tree = ttk.Treeview(f, columns=cols, show="headings", height=14)
        col_widths = {"ID": 45, "Name": 180, "Type": 90, "Category": 110, "Qty": 55, "Threshold": 75, "Value (£)": 90}
        for col in cols:
            self._ls_tree.heading(col, text=col)
            self._ls_tree.column(col, width=col_widths.get(col, 100), anchor="center" if col in ("ID", "Qty", "Threshold") else "w")

        self._ls_tree.tag_configure("low",  background=COLOURS["low_stock_bg"], foreground=COLOURS["low_stock_fg"])
        self._ls_tree.tag_configure("zero", background="#FECACA", foreground="#7F1D1D")

        vsb = ttk.Scrollbar(f, orient="vertical", command=self._ls_tree.yview)
        self._ls_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y", padx=(0, 8))
        self._ls_tree.pack(fill="both", expand=True, padx=8)

    def _build_audit_tab(self) -> None:
        f = self._audit_frame

        toolbar = tk.Frame(f, bg=COLOURS["bg_main"])
        toolbar.pack(fill="x", padx=8, pady=(8, 2))

        tk.Label(toolbar, text="Audit trail of all inventory operations:",
                 bg=COLOURS["bg_main"], fg="#0F172A", font=FONTS["body_bold"]).pack(side="left")

        tk.Button(
            toolbar, text="Save Log…", command=self._save_audit,
            bg=COLOURS["btn_neutral"], fg=COLOURS["btn_fg"],
            font=FONTS["small"], relief="flat", padx=8, pady=3, cursor="hand2",
        ).pack(side="right")

        self._audit_text = tk.Text(
            f, font=FONTS["mono"], bg="#0F172A", fg="#E2E8F0",
            relief="flat", wrap="none", state="disabled",
        )
        vsb = ttk.Scrollbar(f, orient="vertical",   command=self._audit_text.yview)
        hsb = ttk.Scrollbar(f, orient="horizontal", command=self._audit_text.xview)
        self._audit_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right",  fill="y",  padx=(0, 8))
        hsb.pack(side="bottom", fill="x",  padx=8)
        self._audit_text.pack(fill="both", expand=True, padx=8, pady=4)

    # ------------------------------------------------------------------ #
    #  Data population                                                      #
    # ------------------------------------------------------------------ #

    def _load_data(self) -> None:
        summary = self._ctrl.get_inventory_summary()

        # Headline stats
        self._stat_labels["Total Products"].config(text=str(summary["total_products"]))
        self._stat_labels["Total Stock Value"].config(text=f"£{summary['total_value']:,.2f}")
        low_count = summary["low_stock_count"]
        colour = COLOURS["danger"] if low_count > 0 else COLOURS["success"]
        self._stat_labels["Low Stock Items"].config(text=str(low_count), fg=colour)

        # Category breakdown
        self._cat_tree.delete(*self._cat_tree.get_children())
        for cat, data in sorted(summary["by_category"].items()):
            self._cat_tree.insert("", "end", values=(cat, data["count"], f"{data['value']:.2f}"))

        # Type breakdown
        self._type_tree.delete(*self._type_tree.get_children())
        for ptype, data in sorted(summary["by_type"].items()):
            self._type_tree.insert("", "end", values=(ptype, data["count"], f"{data['value']:.2f}"))

        # Low stock tab
        self._ls_tree.delete(*self._ls_tree.get_children())
        for p in self._ctrl.get_low_stock_products():
            tag = "zero" if p.quantity == 0 else "low"
            self._ls_tree.insert("", "end", values=(
                p.product_id, p.name, p.get_type(), p.category,
                p.quantity, p.low_stock_threshold, f"{p.calculate_value():.2f}",
            ), tags=(tag,))

        # Audit log
        log = self._ctrl.get_audit_log()
        self._audit_text.config(state="normal")
        self._audit_text.delete("1.0", "end")
        self._audit_text.insert("end", "\n".join(log) if log else "No activity recorded yet.")
        self._audit_text.config(state="disabled")
        self._audit_text.see("end")

    def _save_audit(self) -> None:
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save audit log",
            parent=self.window,
        )
        if filepath:
            try:
                self._ctrl.export_audit_log(filepath)
                messagebox.showinfo("Saved", f"Audit log saved to:\n{filepath}", parent=self.window)
            except Exception as exc:
                messagebox.showerror("Error", str(exc), parent=self.window)
