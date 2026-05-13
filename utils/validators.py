"""
Input validation utilities.

All validation functions return a (is_valid: bool, error_message: str) tuple.
An empty error string means the value is valid.  This pattern keeps
validation logic outside of the GUI and makes it easy to unit-test.
"""

from datetime import date


def validate_name(value: str) -> tuple[bool, str]:
    if not value or not value.strip():
        return False, "Name cannot be empty."
    if len(value.strip()) < 2:
        return False, "Name must be at least 2 characters."
    if len(value.strip()) > 100:
        return False, "Name cannot exceed 100 characters."
    return True, ""


def validate_price(value: str) -> tuple[bool, str]:
    try:
        price = float(value)
    except (TypeError, ValueError):
        return False, "Price must be a valid number (e.g. 9.99)."
    if price < 0:
        return False, "Price cannot be negative."
    if price > 1_000_000:
        return False, "Price cannot exceed £1,000,000."
    return True, ""


def validate_quantity(value: str) -> tuple[bool, str]:
    try:
        qty = int(value)
    except (TypeError, ValueError):
        return False, "Quantity must be a whole number."
    if qty < 0:
        return False, "Quantity cannot be negative."
    if qty > 1_000_000:
        return False, "Quantity cannot exceed 1,000,000."
    return True, ""


def validate_threshold(value: str) -> tuple[bool, str]:
    try:
        t = int(value)
    except (TypeError, ValueError):
        return False, "Threshold must be a whole number."
    if t < 0:
        return False, "Threshold cannot be negative."
    return True, ""


def validate_warranty_years(value: str) -> tuple[bool, str]:
    try:
        years = int(value)
    except (TypeError, ValueError):
        return False, "Warranty years must be a whole number."
    if years < 0:
        return False, "Warranty years cannot be negative."
    if years > 25:
        return False, "Warranty period cannot exceed 25 years."
    return True, ""


def validate_date(value: str) -> tuple[bool, str]:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format (e.g. 2026-12-31)."
    return True, ""


def validate_non_empty(value: str, field_name: str = "Field") -> tuple[bool, str]:
    if not value or not str(value).strip():
        return False, f"{field_name} cannot be empty."
    return True, ""


def collect_errors(**fields) -> list[str]:
    """
    Convenience helper – validates multiple fields at once using the
    appropriate validator for each field name.

    Usage:
        errors = collect_errors(name="Widget", price="bad", quantity="5")
    """
    validator_map = {
        "name": validate_name,
        "price": validate_price,
        "quantity": validate_quantity,
        "low_stock_threshold": validate_threshold,
        "warranty_years": validate_warranty_years,
        "expiry_date": validate_date,
    }
    errors = []
    for field, value in fields.items():
        validator = validator_map.get(field)
        if validator:
            ok, msg = validator(str(value))
            if not ok:
                errors.append(msg)
    return errors
