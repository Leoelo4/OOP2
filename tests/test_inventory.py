"""
Unit tests for Inventory (models/inventory.py).

The Inventory is a Singleton, so each test must reset it via SingletonMeta._reset()
followed by a fresh instantiation to ensure test isolation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest

from models.inventory import Inventory
from models.product import Electronics, GeneralGoods, PerishableGoods, Product
from patterns.singleton import SingletonMeta


def _fresh_inventory() -> Inventory:
    """Reset the Singleton and the ID counter, return a clean Inventory."""
    SingletonMeta._reset(Inventory)
    Product._id_counter = 0
    inv = Inventory()
    inv._clear_for_testing()
    return inv


class TestInventoryCRUD(unittest.TestCase):

    def setUp(self):
        self.inv = _fresh_inventory()

    def _make_product(self, name="Widget", price=10.0, qty=20):
        return GeneralGoods(name=name, price=price, quantity=qty)

    # --- Create ---

    def test_add_product_increases_count(self):
        p = self._make_product()
        self.inv.add_product(p)
        self.assertEqual(self.inv.count(), 1)

    def test_add_duplicate_id_raises(self):
        p = self._make_product()
        self.inv.add_product(p)
        with self.assertRaises(ValueError):
            self.inv.add_product(p)   # same object / same ID

    # --- Read ---

    def test_get_product_returns_correct_item(self):
        p = self._make_product("Gadget", 5.0, 10)
        self.inv.add_product(p)
        retrieved = self.inv.get_product(p.product_id)
        self.assertEqual(retrieved, p)

    def test_get_product_unknown_id_returns_none(self):
        self.assertIsNone(self.inv.get_product(9999))

    def test_get_all_products_returns_list(self):
        for i in range(3):
            self.inv.add_product(self._make_product(f"Item {i}"))
        self.assertEqual(len(self.inv.get_all_products()), 3)

    # --- Update ---

    def test_update_product_name(self):
        p = self._make_product("Original Name")
        self.inv.add_product(p)
        self.inv.update_product(p.product_id, name="Updated Name")
        self.assertEqual(self.inv.get_product(p.product_id).name, "Updated Name")

    def test_update_product_price_and_quantity(self):
        p = self._make_product(qty=10)
        self.inv.add_product(p)
        self.inv.update_product(p.product_id, price=25.0, quantity=50)
        updated = self.inv.get_product(p.product_id)
        self.assertEqual(updated.price, 25.0)
        self.assertEqual(updated.quantity, 50)

    def test_update_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            self.inv.update_product(9999, name="Ghost")

    # --- Delete ---

    def test_delete_reduces_count(self):
        p = self._make_product()
        self.inv.add_product(p)
        self.inv.delete_product(p.product_id)
        self.assertEqual(self.inv.count(), 0)

    def test_delete_returns_removed_product(self):
        p = self._make_product("RemoveMe")
        self.inv.add_product(p)
        removed = self.inv.delete_product(p.product_id)
        self.assertEqual(removed.name, "RemoveMe")

    def test_delete_unknown_id_raises(self):
        with self.assertRaises(KeyError):
            self.inv.delete_product(9999)


class TestInventoryQuery(unittest.TestCase):

    def setUp(self):
        self.inv = _fresh_inventory()
        self.inv.add_product(Electronics("Laptop",        999.0, 5,  "Computers",  "Dell"))
        self.inv.add_product(Electronics("USB Hub",       19.99, 3,  "Accessories","Anker", low_stock_threshold=5))
        self.inv.add_product(GeneralGoods("Notepad",       2.49, 80, "Stationery", "Ryman"))
        self.inv.add_product(GeneralGoods("Pen Pack",      3.99, 60, "Stationery", "Bic"))

    def test_search_by_name(self):
        results = self.inv.search("laptop")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Laptop")

    def test_search_case_insensitive(self):
        self.assertEqual(len(self.inv.search("NOTEPAD")), 1)

    def test_search_no_match_returns_empty(self):
        self.assertEqual(len(self.inv.search("xyznotexist")), 0)

    def test_search_by_supplier(self):
        results = self.inv.search("ryman")
        self.assertEqual(len(results), 1)

    def test_filter_by_category(self):
        results = self.inv.filter_by_category("Stationery")
        self.assertEqual(len(results), 2)

    def test_get_low_stock_products(self):
        # USB Hub has qty=3, threshold=5 → low stock
        low = self.inv.get_low_stock_products()
        names = [p.name for p in low]
        self.assertIn("USB Hub", names)

    def test_total_stock_value(self):
        # 999*5 + 19.99*3 + 2.49*80 + 3.99*60
        expected = round(999*5 + 19.99*3 + 2.49*80 + 3.99*60, 2)
        self.assertAlmostEqual(self.inv.total_stock_value(), expected, places=2)

    def test_get_categories(self):
        cats = self.inv.get_categories()
        self.assertIn("Stationery", cats)
        self.assertIn("Accessories", cats)
        self.assertIn("Computers", cats)


class TestInventorySingleton(unittest.TestCase):

    def test_singleton_returns_same_instance(self):
        inv1 = Inventory()
        inv2 = Inventory()
        self.assertIs(inv1, inv2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
