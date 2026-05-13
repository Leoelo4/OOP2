"""
main.py – application entry point.

Creates the controller, seeds sample data if the inventory is empty,
then launches the GUI.
"""

import os
import sys

# Make sure all modules are importable from the project root
sys.path.insert(0, os.path.dirname(__file__))

from controllers.inventory_controller import InventoryController
from views.main_window import MainWindow


def seed_sample_data(controller: InventoryController) -> None:
    """
    Populate the inventory with realistic sample products so the application
    has meaningful data on first run.  Skips seeding if data already exists.
    """
    if controller.get_product_count() > 0:
        return   # Already seeded or loaded from file

    samples = [
        {
            "product_type": "Electronics",
            "name": "Sony WH-1000XM5 Headphones",
            "price": 279.99, "quantity": 12,
            "category": "Audio", "supplier": "Sony UK",
            "warranty_years": 2, "low_stock_threshold": 4,
        },
        {
            "product_type": "Electronics",
            "name": "Samsung 65\" QLED TV",
            "price": 1199.99, "quantity": 5,
            "category": "Televisions", "supplier": "Samsung Direct",
            "warranty_years": 3, "low_stock_threshold": 2,
        },
        {
            "product_type": "Electronics",
            "name": "USB-C Fast Charge Cable 2m",
            "price": 12.99, "quantity": 3,
            "category": "Accessories", "supplier": "Anker",
            "warranty_years": 1, "low_stock_threshold": 10,
        },
        {
            "product_type": "Perishable",
            "name": "Coca-Cola 500ml",
            "price": 1.25, "quantity": 240,
            "category": "Soft Drinks", "supplier": "Coca-Cola HBC",
            "expiry_date": "2027-03-01", "low_stock_threshold": 50,
        },
        {
            "product_type": "Perishable",
            "name": "Activia Strawberry Yogurt",
            "price": 0.89, "quantity": 48,
            "category": "Dairy", "supplier": "Danone",
            "expiry_date": "2026-05-25", "low_stock_threshold": 20,
        },
        {
            "product_type": "Perishable",
            "name": "Highland Spring Water 1.5L",
            "price": 0.79, "quantity": 180,
            "category": "Water", "supplier": "Highland Spring",
            "expiry_date": "2027-12-01", "low_stock_threshold": 30,
        },
        {
            "product_type": "General",
            "name": "A4 Ruled Notepad (80 sheets)",
            "price": 2.49, "quantity": 75,
            "category": "Stationery", "supplier": "Ryman",
            "low_stock_threshold": 15,
        },
        {
            "product_type": "General",
            "name": "Ballpoint Pen 10-Pack (Blue)",
            "price": 3.99, "quantity": 60,
            "category": "Stationery", "supplier": "Bic",
            "low_stock_threshold": 10,
        },
        {
            "product_type": "General",
            "name": "Phone Case – Universal 6.5\"",
            "price": 8.99, "quantity": 2,
            "category": "Accessories", "supplier": "Generic",
            "low_stock_threshold": 5,
        },
        {
            "product_type": "General",
            "name": "Aluminium Laptop Stand",
            "price": 24.99, "quantity": 9,
            "category": "Accessories", "supplier": "Nexstand",
            "low_stock_threshold": 3,
        },
    ]

    for item in samples:
        controller.add_product(**item)


def main() -> None:
    controller = InventoryController()
    seed_sample_data(controller)
    app = MainWindow(controller)
    app.run()


if __name__ == "__main__":
    main()
