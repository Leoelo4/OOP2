"""
Unit tests for the Product model (models/product.py).

Tests cover:
  - Construction of all three concrete subclasses
  - Property setters and their validation rules
  - calculate_value() polymorphism (including expired perishables)
  - Serialisation (to_dict) and __str__ / __eq__ / __hash__
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from datetime import date, timedelta

from models.product import Electronics, GeneralGoods, PerishableGoods


class TestElectronics(unittest.TestCase):

    def setUp(self):
        # Reset the ID counter so tests are deterministic
        from models.product import Product
        Product._id_counter = 0
        self.item = Electronics(
            name="Test Headphones",
            price=99.99,
            quantity=10,
            category="Audio",
            supplier="Sony",
            warranty_years=2,
        )

    def test_creation(self):
        self.assertEqual(self.item.name, "Test Headphones")
        self.assertEqual(self.item.price, 99.99)
        self.assertEqual(self.item.quantity, 10)
        self.assertEqual(self.item.warranty_years, 2)
        self.assertEqual(self.item.get_type(), "Electronics")

    def test_calculate_value(self):
        self.assertAlmostEqual(self.item.calculate_value(), 999.90, places=2)

    def test_display_info_contains_warranty(self):
        self.assertIn("2", self.item.get_display_info())

    def test_name_setter_strips_whitespace(self):
        self.item.name = "  Cleaned Name  "
        self.assertEqual(self.item.name, "Cleaned Name")

    def test_name_empty_raises(self):
        with self.assertRaises(ValueError):
            self.item.name = ""

    def test_name_too_short_raises(self):
        with self.assertRaises(ValueError):
            self.item.name = "X"

    def test_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.item.price = -10.0

    def test_negative_quantity_raises(self):
        with self.assertRaises(ValueError):
            self.item.quantity = -1

    def test_negative_warranty_raises(self):
        with self.assertRaises(ValueError):
            self.item.warranty_years = -1

    def test_is_low_stock_false_initially(self):
        # threshold defaults to 5, quantity is 10
        self.assertFalse(self.item.is_low_stock)

    def test_is_low_stock_true_when_at_threshold(self):
        self.item.quantity = 5
        self.assertTrue(self.item.is_low_stock)

    def test_to_dict_contains_warranty(self):
        d = self.item.to_dict()
        self.assertIn("warranty_years", d)
        self.assertEqual(d["warranty_years"], 2)
        self.assertEqual(d["type"], "Electronics")

    def test_equality(self):
        # Two objects with the same ID should be equal
        other = Electronics(name="Other", price=1.0, quantity=1, product_id=self.item.product_id)
        self.assertEqual(self.item, other)

    def test_str_representation(self):
        s = str(self.item)
        self.assertIn("Test Headphones", s)
        self.assertIn("£99.99", s)


class TestPerishableGoods(unittest.TestCase):

    def setUp(self):
        from models.product import Product
        Product._id_counter = 0

    def test_creation_with_future_expiry(self):
        future = (date.today() + timedelta(days=60)).isoformat()
        item = PerishableGoods(name="Yogurt", price=0.89, quantity=50, expiry_date=future)
        self.assertFalse(item.is_expired)
        self.assertEqual(item.get_type(), "Perishable")

    def test_calculate_value_normal(self):
        future = (date.today() + timedelta(days=30)).isoformat()
        item = PerishableGoods(name="Milk", price=1.00, quantity=10, expiry_date=future)
        self.assertAlmostEqual(item.calculate_value(), 10.0, places=2)

    def test_expired_product_value_is_zero(self):
        past = (date.today() - timedelta(days=1)).isoformat()
        item = PerishableGoods(name="Old Bread", price=1.50, quantity=5, expiry_date=past)
        self.assertTrue(item.is_expired)
        self.assertEqual(item.calculate_value(), 0.0)

    def test_display_info_shows_expired(self):
        past = (date.today() - timedelta(days=5)).isoformat()
        item = PerishableGoods(name="Stale Item", price=1.0, quantity=1, expiry_date=past)
        self.assertIn("EXPIRED", item.get_display_info())

    def test_default_expiry_is_30_days(self):
        item = PerishableGoods(name="Fresh Item", price=0.50, quantity=20)
        expected = date.today() + timedelta(days=30)
        self.assertEqual(item.expiry_date, expected)

    def test_days_until_expiry(self):
        future = (date.today() + timedelta(days=15)).isoformat()
        item = PerishableGoods(name="Juice", price=1.0, quantity=5, expiry_date=future)
        self.assertEqual(item.days_until_expiry, 15)

    def test_to_dict_contains_expiry_date(self):
        future = "2027-06-01"
        item = PerishableGoods(name="Water", price=0.79, quantity=100, expiry_date=future)
        d = item.to_dict()
        self.assertIn("expiry_date", d)
        self.assertEqual(d["expiry_date"], future)


class TestGeneralGoods(unittest.TestCase):

    def setUp(self):
        from models.product import Product
        Product._id_counter = 0

    def test_creation(self):
        item = GeneralGoods(name="A4 Notepad", price=2.49, quantity=30)
        self.assertEqual(item.get_type(), "General")
        self.assertAlmostEqual(item.calculate_value(), 74.70, places=2)

    def test_explicit_product_id(self):
        item = GeneralGoods(name="Pen", price=0.50, quantity=100, product_id=999)
        self.assertEqual(item.product_id, 999)

    def test_price_rounds_to_two_decimal_places(self):
        item = GeneralGoods(name="Thing", price=1.999, quantity=1)
        self.assertEqual(item.price, 2.0)

    def test_quantity_zero_is_valid(self):
        item = GeneralGoods(name="Out of Stock Item", price=5.0, quantity=0)
        self.assertEqual(item.quantity, 0)
        self.assertTrue(item.is_low_stock)   # 0 <= threshold(5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
