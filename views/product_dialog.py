"""
ProductDialog – Add / Edit product modal dialog.

Works in two modes:
  - 'add'  : all fields blank, creates a new product on confirm
  - 'edit' : pre-populated from an existing Product instance

The form dynamically shows or hides type-specific fields when the user
changes the product type dropdown (Electronics → warranty; Perishable → expiry date).

Input validation is delegated to utils/validators.py so validation logic
stays independent of the GUI.
"""

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from utils.validators import (
    collect_errors,
    validate_date,
    validate_name,
    validate_price,
    validate_quantity,
    validate_threshold,
    validate_warranty_years,
)
from views.theme import COLOURS, FONTS, PADDING


class ProductDialog:
    """
    Modal dialog for adding or editing a product.

    After the dialog closes, inspect `self.result`:
      - None   : user cancelled
      - dict   : field values ready to pass to the controller
    """

    def __init__(
        self,
        parent: tk.Tk | tk.Toplevel,
        controller,
        mode: str = "add",
        product=None,
    ) -> None:
        self._parent = parent
        self._ctrl   = controller
        self._mode   = mode
        self._product = product
        self.result   = None

        self.window = tk.Toplevel(parent)
        self.window.title("Add Product" if mode == "add" else "Edit Product")
        self.window.geometry("480x560")
        self.window.resizable(False, False)
        self.window.configure(bg=COLOURS["bg_main"])
        self.window.transient(parent)
        self.window.grab_set()   # make it modal

        self._build_form()

        if mode == "edit" and product:
            self._populate(product)

        # Centre the dialog over the parent window
        self.window.update_idletasks()
        px, py = parent.winfo_x(), parent.winfo_y()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        dw, dh = self.window.winfo_width(), self.window.winfo_height()
        self.window.geometry(f"+{px + (pw - dw)//2}+{py + (ph - dh)//2}")

    # ------------------------------------------------------------------ #
    #  Form construction                                                    #
    # ------------------------------------------------------------------ #

    def _build_form(self) -> None:
        # Title bar
        title_bar = tk.Frame(self.window, bg=COLOURS["header_bg"], height=45)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        tk.Label(
            title_bar,
            text="Add New Product" if self._mode == "add" else "Edit Product",
            bg=COLOURS["header_bg"], fg=COLOURS["header_fg"],
            font=FONTS["subheading"], padx=PADDING["window"],
        ).pack(side="left", pady=8)

        # Scrollable content frame
        outer = tk.Frame(self.window, bg=COLOURS["bg_main"])
        outer.pack(fill="both", expand=True, padx=PADDING["window"], pady=PADDING["section"])

        # --- Product Type ---
        self._add_label(outer, "Product Type *")
        self._type_var = tk.StringVar(value="General")
        type_combo = ttk.Combobox(
            outer, textvariable=self._type_var,
            values=self._ctrl.get_product_types(), state="readonly",
            font=FONTS["body"], width=28,
        )
        type_combo.pack(anchor="w", pady=(0, PADDING["widget"]))
        type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        # --- Common fields ---
        self._name_var     = self._add_entry(outer, "Product Name *",         "e.g. Sony Headphones XM5")
        self._price_var    = self._add_entry(outer, "Price (£) *",            "e.g. 89.99")
        self._qty_var      = self._add_entry(outer, "Quantity *",             "e.g. 50")
        self._category_var = self._add_entry(outer, "Category *",             "e.g. Audio, Food, Clothing")
        self._supplier_var = self._add_entry(outer, "Supplier",               "e.g. Sony UK")
        self._threshold_var= self._add_entry(outer, "Low Stock Threshold",    "Default: 5")

        # --- Type-specific panels (shown/hidden based on type selection) ---
        self._electronics_frame = tk.Frame(outer, bg=COLOURS["bg_main"])
        self._warranty_var = self._add_entry(self._electronics_frame, "Warranty (years)", "e.g. 2")

        self._perishable_frame = tk.Frame(outer, bg=COLOURS["bg_main"])
        self._expiry_var = self._add_entry(self._perishable_frame, "Expiry Date (YYYY-MM-DD)", "e.g. 2027-06-30")

        # Show the initial type-specific panel
        self._on_type_change()

        # --- Buttons ---
        btn_frame = tk.Frame(self.window, bg=COLOURS["bg_main"])
        btn_frame.pack(fill="x", padx=PADDING["window"], pady=PADDING["section"])

        label = "Add Product" if self._mode == "add" else "Save Changes"
        tk.Button(
            btn_frame, text=label, command=self._submit,
            bg=COLOURS["btn_primary"], fg=COLOURS["btn_fg"],
            font=FONTS["body_bold"], relief="flat",
            padx=14, pady=7, cursor="hand2",
        ).pack(side="right", padx=(4, 0))

        tk.Button(
            btn_frame, text="Cancel", command=self.window.destroy,
            bg=COLOURS["btn_neutral"], fg=COLOURS["btn_fg"],
            font=FONTS["body_bold"], relief="flat",
            padx=14, pady=7, cursor="hand2",
        ).pack(side="right")

        # Bind Enter key to submit
        self.window.bind("<Return>", lambda _e: self._submit())
        self.window.bind("<Escape>", lambda _e: self.window.destroy())

    def _add_label(self, parent: tk.Frame, text: str) -> None:
        tk.Label(
            parent, text=text,
            bg=COLOURS["bg_main"], fg="#0F172A",
            font=FONTS["body_bold"], anchor="w",
        ).pack(fill="x", pady=(PADDING["widget"], 0))

    def _add_entry(self, parent: tk.Frame, label: str, placeholder: str = "") -> tk.StringVar:
        """Create a labelled text entry and return its StringVar."""
        self._add_label(parent, label)
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var, font=FONTS["body"], width=40)
        entry.pack(anchor="w", pady=(0, PADDING["widget"]))

        # Placeholder text behaviour
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(foreground="#94A3B8")

            def on_focus_in(_e, e=entry, p=placeholder):
                if e.get() == p:
                    e.delete(0, "end")
                    e.config(foreground="#0F172A")

            def on_focus_out(_e, e=entry, p=placeholder):
                if not e.get():
                    e.insert(0, p)
                    e.config(foreground="#94A3B8")

            entry.bind("<FocusIn>",  on_focus_in)
            entry.bind("<FocusOut>", on_focus_out)

        return var

    # ------------------------------------------------------------------ #
    #  Dynamic panel switching                                             #
    # ------------------------------------------------------------------ #

    def _on_type_change(self, _event=None) -> None:
        self._electronics_frame.pack_forget()
        self._perishable_frame.pack_forget()

        selected = self._type_var.get()
        if selected == "Electronics":
            self._electronics_frame.pack(fill="x")
        elif selected == "Perishable":
            self._perishable_frame.pack(fill="x")

        self.window.update_idletasks()

    # ------------------------------------------------------------------ #
    #  Pre-populate for edit mode                                          #
    # ------------------------------------------------------------------ #

    def _populate(self, product) -> None:
        self._type_var.set(product.get_type())
        self._on_type_change()

        self._set_var(self._name_var,     product.name)
        self._set_var(self._price_var,    str(product.price))
        self._set_var(self._qty_var,      str(product.quantity))
        self._set_var(self._category_var, product.category)
        self._set_var(self._supplier_var, product.supplier)
        self._set_var(self._threshold_var, str(product.low_stock_threshold))

        if product.get_type() == "Electronics":
            self._set_var(self._warranty_var, str(product.warranty_years))
        elif product.get_type() == "Perishable":
            self._set_var(self._expiry_var, product.expiry_date.isoformat())

    @staticmethod
    def _set_var(var: tk.StringVar, value: str) -> None:
        var.set(value)

    # ------------------------------------------------------------------ #
    #  Validation & submission                                              #
    # ------------------------------------------------------------------ #

    def _get_value(self, var: tk.StringVar, placeholder: str = "") -> str:
        """Return the variable value, stripping away any placeholder text."""
        v = var.get().strip()
        return "" if v == placeholder else v

    def _submit(self) -> None:
        product_type = self._type_var.get()

        name      = self._get_value(self._name_var,     "e.g. Sony Headphones XM5")
        price     = self._get_value(self._price_var,    "e.g. 89.99")
        quantity  = self._get_value(self._qty_var,      "e.g. 50")
        category  = self._get_value(self._category_var, "e.g. Audio, Food, Clothing")
        supplier  = self._get_value(self._supplier_var, "e.g. Sony UK") or "Unknown"
        threshold = self._get_value(self._threshold_var, "Default: 5") or "5"

        # Collect validation errors across common fields
        errors = collect_errors(
            name=name, price=price, quantity=quantity, low_stock_threshold=threshold
        )
        if not category:
            errors.append("Category cannot be empty.")

        # Type-specific validation
        warranty_years = None
        expiry_date    = None

        if product_type == "Electronics":
            warranty_raw = self._get_value(self._warranty_var, "e.g. 2") or "1"
            ok, msg = validate_warranty_years(warranty_raw)
            if not ok:
                errors.append(msg)
            else:
                warranty_years = int(warranty_raw)

        elif product_type == "Perishable":
            expiry_raw = self._get_value(self._expiry_var, "e.g. 2027-06-30")
            ok, msg = validate_date(expiry_raw)
            if not ok:
                errors.append(msg)
            else:
                expiry_date = expiry_raw

        if errors:
            messagebox.showerror(
                "Validation Error",
                "\n".join(f"• {e}" for e in errors),
                parent=self.window,
            )
            return

        # Build the result dict for the controller
        result = {
            "product_type": product_type,
            "name":         name,
            "price":        float(price),
            "quantity":     int(quantity),
            "category":     category,
            "supplier":     supplier,
            "low_stock_threshold": int(threshold),
        }

        if warranty_years is not None:
            result["warranty_years"] = warranty_years
        if expiry_date is not None:
            result["expiry_date"] = expiry_date

        if self._mode == "edit":
            # The controller expects kwargs without 'product_type' for update
            result.pop("product_type")

        self.result = result
        self.window.destroy()
