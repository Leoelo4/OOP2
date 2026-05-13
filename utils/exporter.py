"""
Export utilities – write inventory data to external file formats.
"""

import csv
import json
import os
from typing import List

from models.product import Product


def export_to_csv(products: List[Product], filepath: str) -> None:
    """Write a list of products to a CSV file at the given path."""
    if not products:
        raise ValueError("No products to export.")

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    fieldnames = [
        "ID", "Type", "Name", "Category", "Supplier",
        "Price (£)", "Quantity", "Stock Value (£)",
        "Low Stock", "Extra Info",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow({
                "ID": p.product_id,
                "Type": p.get_type(),
                "Name": p.name,
                "Category": p.category,
                "Supplier": p.supplier,
                "Price (£)": f"{p.price:.2f}",
                "Quantity": p.quantity,
                "Stock Value (£)": f"{p.calculate_value():.2f}",
                "Low Stock": "Yes" if p.is_low_stock else "No",
                "Extra Info": p.get_display_info(),
            })


def export_to_json(products: List[Product], filepath: str) -> None:
    """Write products as a pretty-printed JSON array."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    data = [p.to_dict() for p in products]
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
