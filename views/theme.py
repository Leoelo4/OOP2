"""
Application-wide colour palette, font definitions, and ttk style helpers.

Applying HCI principles (Nielsen, 2013):
  - Consistency    : one palette used across all windows
  - Aesthetic design: a neutral, professional colour scheme avoids distraction
  - Visibility     : high-contrast text/background ratios (WCAG AA standard)
"""

import tkinter as tk
from tkinter import ttk

# ------------------------------------------------------------------ #
#  Colour palette                                                       #
# ------------------------------------------------------------------ #

COLOURS = {
    # Layout
    "bg_main":     "#F1F5F9",   # light grey-blue – main content area
    "bg_card":     "#FFFFFF",   # white card surfaces
    "header_bg":   "#1E3A5F",   # dark navy header / sidebar
    "header_fg":   "#F8FAFC",   # near-white text on header

    # Toolbar / buttons
    "btn_primary":       "#2563EB",  # blue – primary actions (Add)
    "btn_primary_hover":  "#1D4ED8",
    "btn_danger":        "#DC2626",  # red – destructive actions (Delete)
    "btn_danger_hover":   "#B91C1C",
    "btn_neutral":       "#475569",  # slate – secondary actions
    "btn_neutral_hover":  "#334155",
    "btn_fg":            "#FFFFFF",

    # Table
    "row_odd":      "#FFFFFF",
    "row_even":     "#F8FAFC",
    "row_selected": "#DBEAFE",  # light blue selection
    "low_stock_bg": "#FEE2E2",  # light red rows
    "low_stock_fg": "#991B1B",

    # Status bar
    "status_bg":   "#1E3A5F",
    "status_fg":   "#94A3B8",

    # Borders / separators
    "border":      "#CBD5E1",

    # Feedback
    "success":     "#16A34A",
    "warning":     "#D97706",
    "danger":      "#DC2626",
    "info":        "#2563EB",
}

FONTS = {
    "heading":    ("Segoe UI", 14, "bold"),
    "subheading": ("Segoe UI", 11, "bold"),
    "body":       ("Segoe UI", 10),
    "body_bold":  ("Segoe UI", 10, "bold"),
    "mono":       ("Consolas", 9),
    "small":      ("Segoe UI", 9),
    "status":     ("Segoe UI", 9),
    "title":      ("Segoe UI", 18, "bold"),
}

PADDING = {
    "window":  12,
    "section": 8,
    "widget":  4,
}


def apply_styles(root: tk.Tk) -> None:
    """
    Configure ttk styles to match the application palette.
    Called once during MainWindow initialisation.
    """
    style = ttk.Style(root)
    style.theme_use("clam")   # 'clam' gives us the cleanest base to build on

    # ---- Treeview (product table) ----
    style.configure(
        "Treeview",
        background=COLOURS["bg_card"],
        fieldbackground=COLOURS["bg_card"],
        foreground="#0F172A",
        rowheight=26,
        font=FONTS["body"],
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=COLOURS["header_bg"],
        foreground=COLOURS["header_fg"],
        font=FONTS["body_bold"],
        relief="flat",
        padding=(6, 4),
    )
    style.map(
        "Treeview",
        background=[("selected", COLOURS["row_selected"])],
        foreground=[("selected", "#1E3A5F")],
    )

    # ---- Notebook (tabs in Reports window) ----
    style.configure(
        "TNotebook",
        background=COLOURS["bg_main"],
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        font=FONTS["body_bold"],
        padding=(12, 6),
        background=COLOURS["bg_card"],
        foreground=COLOURS["btn_neutral"],
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLOURS["header_bg"])],
        foreground=[("selected", COLOURS["header_fg"])],
    )

    # ---- Scrollbar ----
    style.configure(
        "Vertical.TScrollbar",
        background=COLOURS["border"],
        troughcolor=COLOURS["bg_main"],
        borderwidth=0,
        arrowsize=12,
    )

    # ---- Labels ----
    style.configure(
        "TLabel",
        background=COLOURS["bg_main"],
        foreground="#0F172A",
        font=FONTS["body"],
    )
    style.configure(
        "Header.TLabel",
        background=COLOURS["header_bg"],
        foreground=COLOURS["header_fg"],
        font=FONTS["heading"],
    )
    style.configure(
        "Status.TLabel",
        background=COLOURS["status_bg"],
        foreground=COLOURS["status_fg"],
        font=FONTS["status"],
    )

    # ---- Separator ----
    style.configure("TSeparator", background=COLOURS["border"])

    # ---- Frame ----
    style.configure("TFrame", background=COLOURS["bg_main"])
    style.configure("Card.TFrame", background=COLOURS["bg_card"])
