"""
LowStockWindow – dedicated view for products running low on stock.

Allows the manager to quickly spot items that need reordering and
update quantities without leaving this window.
"""

import tkinter as tk
from tkinter import messagebox, ttk

from utils.validators import validate_quantity
from views.theme import COLOURS, FONTS, PADDING


class LowStockWindow:
    """Modal window listing all low-stock products with a quick-restock action."""

    def __init__(self, parent, controller, on_close=None) -> None:
        self._ctrl     = controller
        self._on_close = on_close   # callback so MainWindow can refresh

        self.window = tk.Toplevel(parent)
        self.window.title("Low Stock Alerts")
        self.window.geometry("700x460")
        self.window.configure(bg=COLOURS["bg_main"])
        self.window.transient(parent)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self._close)

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
        hdr = tk.Frame(self.window, bg="#7C2D12", height=45)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text="⚠  Low Stock Alerts",
            bg="#7C2D12", fg="#FEF3C7",
            font=FONTS["subheading"], padx=PADDING["window"],
        ).pack(side="left", pady=8)

        # Info label
        self._info_label = tk.Label(
            self.window,
            text="",
            bg=COLOURS["bg_main"], fg="#7C2D12",
            font=FONTS["body_bold"],
        )
        self._info_label.pack(anchor="w", padx=PADDING["window"], pady=(8, 0))

        # Treeview
        table_frame = tk.Frame(self.window, bg=COLOURS["bg_main"])
        table_frame.pack(fill="both", expand=True, padx=PADDING["window"], pady=PADDING["section"])

        cols = ("ID", "Name", "Type", "Category", "Current Qty", "Threshold", "Supplier")
        self._tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=12)

        col_widths = {"ID": 45, "Name": 180, "Type": 90, "Category": 100,
                      "Current Qty": 90, "Threshold": 80, "Supplier": 130}
        for col in cols:
            self._tree.heading(col, text=col)
            self._tree.column(col, width=col_widths.get(col, 100),
                              anchor="center" if col in ("ID", "Current Qty", "Threshold") else "w")

        self._tree.tag_configure("low",  background=COLOURS["low_stock_bg"], foreground=COLOURS["low_stock_fg"])
        self._tree.tag_configure("zero", background="#FECACA", foreground="#7F1D1D")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        # Action row at bottom
        action_frame = tk.Frame(self.window, bg=COLOURS["bg_main"])
        action_frame.pack(fill="x", padx=PADDING["window"], pady=PADDING["section"])

        tk.Label(action_frame, text="New Quantity:",
                 bg=COLOURS["bg_main"], fg="#0F172A", font=FONTS["body_bold"]).pack(side="left")

        self._new_qty_var = tk.StringVar()
        ttk.Entry(action_frame, textvariable=self._new_qty_var, width=8, font=FONTS["body"]).pack(side="left", padx=6)

        tk.Button(
            action_frame, text="Restock Selected",
            command=self._restock,
            bg=COLOURS["btn_primary"], fg=COLOURS["btn_fg"],
            font=FONTS["body_bold"], relief="flat",
            padx=12, pady=5, cursor="hand2",
        ).pack(side="left", padx=4)

        tk.Button(
            action_frame, text="Close",
            command=self._close,
            bg=COLOURS["btn_neutral"], fg=COLOURS["btn_fg"],
            font=FONTS["body_bold"], relief="flat",
            padx=12, pady=5, cursor="hand2",
        ).pack(side="right")

    # ------------------------------------------------------------------ #
    #  Data population                                                      #
    # ------------------------------------------------------------------ #

    def _load_data(self) -> None:
        self._tree.delete(*self._tree.get_children())
        products = self._ctrl.get_low_stock_products()

        self._info_label.config(
            text=f"{len(products)} product(s) require attention."
            if products else "✓ All products are adequately stocked."
        )

        for p in products:
            tag = "zero" if p.quantity == 0 else "low"
            self._tree.insert("", "end", iid=str(p.product_id), values=(
                p.product_id, p.name, p.get_type(),
                p.category, p.quantity, p.low_stock_threshold, p.supplier,
            ), tags=(tag,))

    # ------------------------------------------------------------------ #
    #  Restock action                                                       #
    # ------------------------------------------------------------------ #

    def _restock(self) -> None:
        selected = self._tree.selection()
        if not selected:
            messagebox.showwarning("Nothing selected", "Please select a product to restock.", parent=self.window)
            return

        new_qty_str = self._new_qty_var.get().strip()
        ok, msg = validate_quantity(new_qty_str)
        if not ok:
            messagebox.showerror("Invalid quantity", msg, parent=self.window)
            return

        product_id = int(selected[0])
        try:
            self._ctrl.update_product(product_id, quantity=int(new_qty_str))
            self._new_qty_var.set("")
            self._load_data()
            messagebox.showinfo("Updated", "Quantity updated successfully.", parent=self.window)
        except (KeyError, ValueError) as exc:
            messagebox.showerror("Error", str(exc), parent=self.window)

    # ------------------------------------------------------------------ #
    #  Close                                                                #
    # ------------------------------------------------------------------ #

    def _close(self) -> None:
        if self._on_close:
            self._on_close()
        self.window.destroy()
