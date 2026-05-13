"""
Unit tests for input validation utilities (utils/validators.py).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest

from utils.validators import (
    collect_errors,
    validate_date,
    validate_name,
    validate_price,
    validate_quantity,
    validate_threshold,
    validate_warranty_years,
)


class TestValidateName(unittest.TestCase):

    def test_valid_name(self):
        ok, msg = validate_name("Sony Headphones")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_empty_string(self):
        ok, _ = validate_name("")
        self.assertFalse(ok)

    def test_whitespace_only(self):
        ok, _ = validate_name("   ")
        self.assertFalse(ok)

    def test_single_character(self):
        ok, _ = validate_name("A")
        self.assertFalse(ok)

    def test_name_too_long(self):
        ok, _ = validate_name("X" * 101)
        self.assertFalse(ok)

    def test_exactly_two_chars_valid(self):
        ok, _ = validate_name("AB")
        self.assertTrue(ok)


class TestValidatePrice(unittest.TestCase):

    def test_valid_price(self):
        ok, msg = validate_price("9.99")
        self.assertTrue(ok)
        self.assertEqual(msg, "")

    def test_zero_price_valid(self):
        ok, _ = validate_price("0")
        self.assertTrue(ok)

    def test_negative_price(self):
        ok, _ = validate_price("-5.00")
        self.assertFalse(ok)

    def test_non_numeric(self):
        ok, _ = validate_price("not_a_price")
        self.assertFalse(ok)

    def test_price_too_large(self):
        ok, _ = validate_price("2000000")
        self.assertFalse(ok)


class TestValidateQuantity(unittest.TestCase):

    def test_valid_quantity(self):
        ok, _ = validate_quantity("50")
        self.assertTrue(ok)

    def test_zero_valid(self):
        ok, _ = validate_quantity("0")
        self.assertTrue(ok)

    def test_negative(self):
        ok, _ = validate_quantity("-1")
        self.assertFalse(ok)

    def test_float_string(self):
        ok, _ = validate_quantity("3.5")
        self.assertFalse(ok)

    def test_empty(self):
        ok, _ = validate_quantity("")
        self.assertFalse(ok)


class TestValidateWarrantyYears(unittest.TestCase):

    def test_valid(self):
        ok, _ = validate_warranty_years("2")
        self.assertTrue(ok)

    def test_zero_valid(self):
        ok, _ = validate_warranty_years("0")
        self.assertTrue(ok)

    def test_negative(self):
        ok, _ = validate_warranty_years("-1")
        self.assertFalse(ok)

    def test_too_large(self):
        ok, _ = validate_warranty_years("26")
        self.assertFalse(ok)


class TestValidateDate(unittest.TestCase):

    def test_valid_date(self):
        ok, _ = validate_date("2027-12-31")
        self.assertTrue(ok)

    def test_invalid_format(self):
        ok, _ = validate_date("31/12/2027")
        self.assertFalse(ok)

    def test_invalid_date_values(self):
        ok, _ = validate_date("2027-13-01")   # month 13
        self.assertFalse(ok)

    def test_partial_date(self):
        ok, _ = validate_date("2027-06")
        self.assertFalse(ok)


class TestCollectErrors(unittest.TestCase):

    def test_all_valid(self):
        errors = collect_errors(name="Widget", price="5.99", quantity="100")
        self.assertEqual(errors, [])

    def test_multiple_errors(self):
        errors = collect_errors(name="", price="-1", quantity="bad")
        self.assertGreater(len(errors), 0)

    def test_unknown_field_is_ignored(self):
        # collect_errors should not fail on unrecognised fields
        errors = collect_errors(unknown_field="anything")
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
