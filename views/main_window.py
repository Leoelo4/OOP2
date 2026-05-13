"""
MainWindow – the primary application window.

Layout (top to bottom):
  1. Header bar    – application title + search box
  2. Toolbar       – action buttons (Add / Edit / Delete / Reports / Export)
  3. Product table – scrollable Treeview listing all products
  4. Status bar    – live counts and total stock value

HCI considerations applied (Nielsen, 2013):
  - Keyboard shortcuts so power users never need the mouse (Ctrl+N, Del, F5…)
  - Colour-coded rows  : low-stock rows highlighted in red
  - Confirmation dialog before any destructive delete
  - Immediate feedback after every action via the status bar
  - Tooltips on all toolbar buttons
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from controllers.inventory_controller import InventoryController
from utils.exporter import export_to_csv
from views import product_dialog, reports_window, low_stock_window
from views.theme import COLOURS, FONTS, PADDING, apply_styles


class Tooltip:
    """Lightweight tooltip that appears on mouse-over."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        self._widget = widget
        self._text = text
        self._tip_window: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _event=None) -> None:
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tip_window = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        lbl = tk.Label(
            tw, text=self._text, background="#FFFBCC",
            relief="solid", borderwidth=1, font=FONTS["small"],
            padx=4, pady=2,
        )
        lbl.pack()

    def _hide(self, _event=None) -> None:
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None


class MainWindow:
    """
    Primary window of the RetailPro Stock Management System.

    Receives an InventoryController instance so it never talks to the
    model layer directly (MVC separation of concerns).
    """

    def __init__(self, controller: InventoryController) -> None:
        self._ctrl = controller

        self._root = tk.Tk()
        self._root.title("RetailPro – Stock Management System")
        self._root.geometry("1100x680")
        self._root.minsize(900, 550)
        self._root.configure(bg=COLOURS["bg_main"])

        apply_styles(self._root)
        self._build_ui()
        self._bind_shortcuts()
        self.refresh_table()
        self._check_low_stock_on_startup()

    # ------------------------------------------------------------------ #
    #  UI construction                                                      #
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        self._create_header()
        self._create_toolbar()
        self._create_table()
        self._create_status_bar()

    def _create_header(self) -> None:
        header = tk.Frame(self._root, bg=COLOURS["header_bg"], height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Title
        tk.Label(
            header, text="📦 RetailPro",
            bg=COLOURS["header_bg"], fg=COLOURS["header_fg"],
            font=FONTS["title"], padx=PADDING["window"],
        ).pack(side="left", pady=8)

        tk.Label(
            header, text="Stock Management System",
            bg=COLOURS["header_bg"], fg="#94A3B8",
            font=FONTS["subheading"],
        ).pack(side="left", pady=8)

        # Search section (right-aligned in header)
        search_frame = tk.Frame(header, bg=COLOURS["header_bg"])
        search_frame.pack(side="right", padx=PADDING["window"], pady=10)

        tk.Label(
            search_frame, text="Search:",
            bg=COLOURS["header_bg"], fg=COLOURS["header_fg"],
            font=FONTS["body"],
        ).pack(side="left", padx=(0, 4))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)

        self._search_entry = tk.Entry(
            search_frame, textvariable=self._search_var,
            font=FONTS["body"], width=22,
            relief="flat", bd=2,
        )
        self._search_entry.pack(side="left", padx=(0, 4))

        clear_btn = tk.Button(
            search_frame, text="✕", command=self._clear_search,
            bg=COLOURS["header_bg"], fg=COLOURS["header_fg"],
            relief="flat", font=FONTS["body"], cursor="hand2",
        )
        clear_btn.pack(side="left")

        # Category filter dropdown
        tk.Label(
            search_frame, text="  Filter:",
            bg=COLOURS["header_bg"], fg=COLOURS["header_fg"],
            font=FONTS["body"],
        ).pack(side="left", padx=(8, 4))

        self._filter_var = tk.StringVar(value="All")
        self._filter_combo = ttk.Combobox(
            search_frame, textvariable=self._filter_var,
            state="readonly", width=14, font=FONTS["body"],
        )
        self._filter_combo.pack(side="left")
        self._filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

    def _create_toolbar(self) -> None:
        toolbar = tk.Frame(self._root, bg=COLOURS["bg_card"], pady=6, padx=8)
        toolbar.pack(fill="x")

        # Helper so each button is styled consistently
        def make_btn(parent, text, cmd, colour, tip):
            btn = tk.Button(
                parent, text=text, command=cmd,
                bg=colour, fg=COLOURS["btn_fg"],
                font=FONTS["body_bold"],
                relief="flat", padx=10, pady=5,
                cursor="hand2", bd=0,
                activebackground=COLOURS["btn_neutral_hover"],
                activeforeground=COLOURS["btn_fg"],
            )
            btn.pack(side="left", padx=3)
            Tooltip(btn, tip)
            return btn

        make_btn(toolbar, "＋ Add",    self._add_product,    COLOURS["btn_primary"],  "Add a new product  [Ctrl+N]")
        make_btn(toolbar, "✎ Edit",    self._edit_product,   COLOURS["btn_neutral"],  "Edit selected product  [Ctrl+E]")
        make_btn(toolbar, "✖ Delete",  self._delete_product, COLOURS["btn_danger"],   "Delete selected product  [Delete]")

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8, pady=2)

        make_btn(toolbar, "📊 Reports",    self._open_reports,    "#7C3AED", "View inventory reports  [Ctrl+R]")
        make_btn(toolbar, "⚠ Low Stock",  self._open_low_stock,  "#D97706", "View low stock items  [Ctrl+L]")

        ttk.Separator(toolbar, orient="vertical").pack(side="left", fill="y", padx=8, pady=2)

        make_btn(toolbar, "⬇ Export CSV", self._export_csv, "#0F766E", "Export all products to CSV")

        # Refresh button on the far right
        refresh_btn = tk.Button(
            toolbar, text="⟳ Refresh", command=self.refresh_table,
            bg=COLOURS["btn_neutral"], fg=COLOURS["btn_fg"],
            font=FONTS["body_bold"], relief="flat",
            padx=10, pady=5, cursor="hand2",
        )
        refresh_btn.pack(side="right", padx=3)
        Tooltip(refresh_btn, "Reload product list  [F5]")

    def _create_table(self) -> None:
        table_frame = tk.Frame(self._root, bg=COLOURS["bg_main"])
        table_frame.pack(fill="both", expand=True, padx=PADDING["window"], pady=PADDING["section"])

        columns = ("ID", "Name", "Type", "Category", "Supplier", "Price", "Qty", "Value", "Status")
        self._tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Column widths and alignments
        col_config = {
            "ID":       (45,  "center"),
            "Name":     (200, "w"),
            "Type":     (90,  "center"),
            "Category": (110, "w"),
            "Supplier": (130, "w"),
            "Price":    (75,  "e"),
            "Qty":      (55,  "center"),
            "Value":    (90,  "e"),
            "Status":   (100, "center"),
        }
        for col, (width, anchor) in col_config.items():
            self._tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self._tree.column(col, width=width, anchor=anchor, minwidth=40)

        # Row colour tags
        self._tree.tag_configure("low_stock",   background=COLOURS["low_stock_bg"], foreground=COLOURS["low_stock_fg"])
        self._tree.tag_configure("out_of_stock", background="#FECACA",              foreground="#7F1D1D")
        self._tree.tag_configure("odd_row",      background=COLOURS["row_odd"])
        self._tree.tag_configure("even_row",     background=COLOURS["row_even"])

        # Scrollbars
        v_scroll = ttk.Scrollbar(table_frame, orient="vertical",   command=self._tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient="horizontal",  command=self._tree.xview)
        self._tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right",  fill="y")
        h_scroll.pack(side="bottom", fill="x")
        self._tree.pack(fill="both", expand=True)

        # Bind events
        self._tree.bind("<Double-1>",         self._on_double_click)
        self._tree.bind("<<TreeviewSelect>>", self._on_row_select)

        # Sort state tracker
        self._sort_col = "ID"
        self._sort_asc = True

    def _create_status_bar(self) -> None:
        bar = tk.Frame(self._root, bg=COLOURS["status_bg"], height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._status_products   = tk.Label(bar, text="", bg=COLOURS["status_bg"], fg=COLOURS["status_fg"], font=FONTS["status"])
        self._status_value      = tk.Label(bar, text="", bg=COLOURS["status_bg"], fg=COLOURS["status_fg"], font=FONTS["status"])
        self._status_low_stock  = tk.Label(bar, text="", bg=COLOURS["status_bg"], fg=COLOURS["status_fg"], font=FONTS["status"])

        self._status_products.pack(side="left",  padx=12)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", pady=4)
        self._status_value.pack(side="left", padx=12)
        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", pady=4)
        self._status_low_stock.pack(side="left", padx=12)

        # Version label on right
        tk.Label(
            bar, text="RetailPro v1.0  |  PETR2134",
            bg=COLOURS["status_bg"], fg="#475569", font=FONTS["status"],
        ).pack(side="right", padx=12)

    # ------------------------------------------------------------------ #
    #  Data population                                                      #
    # ------------------------------------------------------------------ #

    def refresh_table(self, products=None) -> None:
        """Repopulate the Treeview.  If products is None, load everything."""
        self._tree.delete(*self._tree.get_children())

        if products is None:
            products = self._ctrl.get_all_products()

        for i, p in enumerate(products):
            if p.quantity == 0:
                tag = "out_of_stock"
                status = "OUT OF STOCK"
            elif p.is_low_stock:
                tag = "low_stock"
                status = f"LOW ({p.quantity})"
            else:
                tag = "even_row" if i % 2 == 0 else "odd_row"
                status = "OK"

            self._tree.insert(
                "", "end",
                iid=str(p.product_id),
                values=(
                    p.product_id,
                    p.name,
                    p.get_type(),
                    p.category,
                    p.supplier,
                    f"£{p.price:.2f}",
                    p.quantity,
                    f"£{p.calculate_value():.2f}",
                    status,
                ),
                tags=(tag,),
            )

        self._update_status()
        self._refresh_filter_options()

    def _update_status(self) -> None:
        count      = self._ctrl.get_product_count()
        total_val  = self._ctrl.get_total_stock_value()
        low_count  = len(self._ctrl.get_low_stock_products())

        self._status_products.config(text=f"Products: {count}")
        self._status_value.config(text=f"Total Value: £{total_val:,.2f}")

        colour = COLOURS["danger"] if low_count > 0 else COLOURS["status_fg"]
        self._status_low_stock.config(
            text=f"⚠ Low Stock: {low_count}" if low_count > 0 else "All stock levels OK",
            fg=colour,
        )

    def _refresh_filter_options(self) -> None:
        categories = ["All"] + self._ctrl.get_categories()
        self._filter_combo["values"] = categories
        if self._filter_var.get() not in categories:
            self._filter_var.set("All")

    # ------------------------------------------------------------------ #
    #  CRUD actions                                                         #
    # ------------------------------------------------------------------ #

    def _add_product(self, _event=None) -> None:
        dlg = product_dialog.ProductDialog(self._root, self._ctrl, mode="add")
        self._root.wait_window(dlg.window)
        if dlg.result:
            try:
                self._ctrl.add_product(**dlg.result)
                self.refresh_table()
                messagebox.showinfo("Success", "Product added successfully.", parent=self._root)
            except (ValueError, KeyError) as exc:
                messagebox.showerror("Error", str(exc), parent=self._root)

    def _edit_product(self, _event=None) -> None:
        product_id = self._get_selected_id()
        if product_id is None:
            messagebox.showwarning("Nothing selected", "Please select a product to edit.", parent=self._root)
            return
        product = self._ctrl.get_product(product_id)
        dlg = product_dialog.ProductDialog(self._root, self._ctrl, mode="edit", product=product)
        self._root.wait_window(dlg.window)
        if dlg.result:
            try:
                self._ctrl.update_product(product_id, **dlg.result)
                self.refresh_table()
            except (ValueError, KeyError) as exc:
                messagebox.showerror("Error", str(exc), parent=self._root)

    def _delete_product(self, _event=None) -> None:
        product_id = self._get_selected_id()
        if product_id is None:
            messagebox.showwarning("Nothing selected", "Please select a product to delete.", parent=self._root)
            return
        product = self._ctrl.get_product(product_id)
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n\n  {product.name} (ID: {product_id})\n\nThis cannot be undone.",
            parent=self._root,
            icon="warning",
        )
        if confirmed:
            self._ctrl.delete_product(product_id)
            self.refresh_table()

    # ------------------------------------------------------------------ #
    #  Secondary windows                                                    #
    # ------------------------------------------------------------------ #

    def _open_reports(self, _event=None) -> None:
        reports_window.ReportsWindow(self._root, self._ctrl)

    def _open_low_stock(self, _event=None) -> None:
        low_stock_window.LowStockWindow(self._root, self._ctrl, on_close=self.refresh_table)

    # ------------------------------------------------------------------ #
    #  Search & filter                                                      #
    # ------------------------------------------------------------------ #

    def _on_search_change(self, *_args) -> None:
        self._apply_filters()

    def _on_filter_change(self, _event=None) -> None:
        self._apply_filters()

    def _apply_filters(self) -> None:
        query    = self._search_var.get().strip()
        category = self._filter_var.get()

        all_products = (
            self._ctrl.search_products(query) if query
            else self._ctrl.get_all_products()
        )

        if category and category != "All":
            all_products = [p for p in all_products if p.category == category]

        self.refresh_table(all_products)

    def _clear_search(self) -> None:
        self._search_var.set("")
        self._filter_var.set("All")
        self.refresh_table()

    # ------------------------------------------------------------------ #
    #  Sort                                                                 #
    # ------------------------------------------------------------------ #

    def _sort_by(self, column: str) -> None:
        if self._sort_col == column:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = column
            self._sort_asc = True

        sort_map = {
            "ID":       lambda p: p.product_id,
            "Name":     lambda p: p.name.lower(),
            "Type":     lambda p: p.get_type(),
            "Category": lambda p: p.category.lower(),
            "Supplier": lambda p: p.supplier.lower(),
            "Price":    lambda p: p.price,
            "Qty":      lambda p: p.quantity,
            "Value":    lambda p: p.calculate_value(),
            "Status":   lambda p: p.quantity,
        }
        key_fn = sort_map.get(column, lambda p: p.product_id)
        products = sorted(self._ctrl.get_all_products(), key=key_fn, reverse=not self._sort_asc)
        self.refresh_table(products)

    # ------------------------------------------------------------------ #
    #  Export                                                               #
    # ------------------------------------------------------------------ #

    def _export_csv(self) -> None:
        products = self._ctrl.get_all_products()
        if not products:
            messagebox.showinfo("No data", "There are no products to export.", parent=self._root)
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export products to CSV",
            parent=self._root,
        )
        if filepath:
            try:
                export_to_csv(products, filepath)
                messagebox.showinfo("Exported", f"Products exported to:\n{filepath}", parent=self._root)
            except Exception as exc:
                messagebox.showerror("Export failed", str(exc), parent=self._root)

    # ------------------------------------------------------------------ #
    #  Event helpers                                                        #
    # ------------------------------------------------------------------ #

    def _on_double_click(self, _event=None) -> None:
        self._edit_product()

    def _on_row_select(self, _event=None) -> None:
        pass   # could update a detail panel in future

    def _get_selected_id(self) -> int | None:
        selected = self._tree.selection()
        if not selected:
            return None
        return int(selected[0])

    def _check_low_stock_on_startup(self) -> None:
        alerts = self._ctrl.peek_low_stock_alerts()
        if alerts:
            self._root.after(
                500,
                lambda: messagebox.showwarning(
                    "Low Stock Alert",
                    f"{len(alerts)} product(s) are low on stock.\n\n"
                    "Click 'Low Stock' in the toolbar to review them.",
                    parent=self._root,
                ),
            )

    # ------------------------------------------------------------------ #
    #  Keyboard shortcuts (HCI: flexibility and efficiency of use)         #
    # ------------------------------------------------------------------ #

    def _bind_shortcuts(self) -> None:
        self._root.bind("<Control-n>", self._add_product)
        self._root.bind("<Control-N>", self._add_product)
        self._root.bind("<Control-e>", self._edit_product)
        self._root.bind("<Control-E>", self._edit_product)
        self._root.bind("<Delete>",    self._delete_product)
        self._root.bind("<F5>",        lambda _e: self.refresh_table())
        self._root.bind("<Control-r>", self._open_reports)
        self._root.bind("<Control-R>", self._open_reports)
        self._root.bind("<Control-l>", self._open_low_stock)
        self._root.bind("<Control-L>", self._open_low_stock)
        self._root.bind("<Control-f>", lambda _e: self._search_entry.focus())
        self._root.bind("<Control-F>", lambda _e: self._search_entry.focus())

    # ------------------------------------------------------------------ #
    #  Run                                                                  #
    # ------------------------------------------------------------------ #

    def run(self) -> None:
        self._root.mainloop()
