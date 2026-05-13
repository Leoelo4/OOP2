"""
Unit tests for the ProductFactory (patterns/factory.py).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest

from models.product import Electronics, GeneralGoods, PerishableGoods, Product
from patterns.factory import ProductFactory


class TestProductFactory(unittest.TestCase):

    def setUp(self):
        Product._id_counter = 0

    def test_create_electronics(self):
        p = ProductFactory.create(
            "Electronics", name="TV", price=499.0, quantity=8,
            warranty_years=3,
        )
        self.assertIsInstance(p, Electronics)
        self.assertEqual(p.warranty_years, 3)

    def test_create_perishable(self):
        p = ProductFactory.create(
            "Perishable", name="Milk", price=0.89, quantity=50,
            expiry_date="2027-01-01",
        )
        self.assertIsInstance(p, PerishableGoods)

    def test_create_general(self):
        p = ProductFactory.create(
            "General", name="Pen", price=0.50, quantity=200,
        )
        self.assertIsInstance(p, GeneralGoods)

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            ProductFactory.create("Unknown", name="X", price=1.0, quantity=1)

    def test_from_dict_electronics(self):
        data = {
            "type": "Electronics",
            "name": "Keyboard",
            "price": 49.99,
            "quantity": 15,
            "warranty_years": 1,
            "product_id": 42,
        }
        p = ProductFactory.from_dict(data)
        self.assertIsInstance(p, Electronics)
        self.assertEqual(p.name, "Keyboard")
        self.assertEqual(p.product_id, 42)

    def test_from_dict_does_not_mutate_input(self):
        data = {
            "type": "General",
            "name": "Eraser",
            "price": 0.99,
            "quantity": 50,
        }
        original_keys = set(data.keys())
        ProductFactory.from_dict(data)
        self.assertEqual(set(data.keys()), original_keys)   # dict unchanged

    def test_get_types_returns_list(self):
        types = ProductFactory.get_types()
        self.assertIn("Electronics", types)
        self.assertIn("Perishable",  types)
        self.assertIn("General",     types)

    def test_register_custom_type(self):
        class CustomProduct(GeneralGoods):
            def get_type(self): return "Custom"
            def get_display_info(self): return "Custom product"

        ProductFactory.register("Custom", CustomProduct)
        p = ProductFactory.create("Custom", name="Special Item", price=1.0, quantity=1)
        self.assertIsInstance(p, CustomProduct)
        self.assertEqual(p.get_type(), "Custom")

    def test_register_non_product_raises(self):
        with self.assertRaises(TypeError):
            ProductFactory.register("Bad", str)   # str is not a Product subclass


if __name__ == "__main__":
    unittest.main(verbosity=2)
