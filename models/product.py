"""
Product model – defines the abstract Product base class and its three concrete
subclasses (Electronics, PerishableGoods, GeneralGoods).

OOP principles demonstrated here:
  - Abstraction  : Product is an ABC with abstract methods that force subclasses
                   to provide a consistent interface.
  - Encapsulation: All attributes are stored as private name-mangled fields;
                   access is controlled through property descriptors with
                   validation in the setters.
  - Inheritance  : Electronics, PerishableGoods and GeneralGoods each extend
                   Product, reusing common logic while adding type-specific state.
  - Polymorphism : calculate_value() and get_display_info() behave differently
                   for each subclass without the caller needing to know the type.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime


class Product(ABC):
    """
    Abstract base class for all products in the stock management system.

    Subclasses must implement:
      - get_type()         -> str   short type label
      - get_display_info() -> str   human-readable extra attributes
      - calculate_value()  -> float total stock value for this product
    """

    # Class-level counter so every new product gets a unique integer ID.
    # Loaded products can override this via the product_id parameter and the
    # counter will be bumped up accordingly (see __init__).
    _id_counter: int = 0

    def __init__(
        self,
        name: str,
        price: float,
        quantity: int,
        category: str,
        supplier: str = "Unknown",
        product_id: int = None,
        low_stock_threshold: int = 5,
        created_at=None,
        **kwargs,          # absorb any extra keys when loading from JSON
    ) -> None:

        # Assign ID – if one is given (e.g. when loading from file) use it
        # and make sure the counter stays ahead of the highest seen value.
        if product_id is not None:
            self.__product_id = int(product_id)
            if self.__product_id > Product._id_counter:
                Product._id_counter = self.__product_id
        else:
            Product._id_counter += 1
            self.__product_id = Product._id_counter

        # Use setters so validation runs even during construction
        self.name = name
        self.price = price
        self.quantity = quantity
        self.__category = str(category)
        self.__supplier = str(supplier) if supplier else "Unknown"
        self.__low_stock_threshold = max(0, int(low_stock_threshold))

        if created_at is not None:
            self.__created_at = (
                datetime.fromisoformat(created_at)
                if isinstance(created_at, str)
                else created_at
            )
        else:
            self.__created_at = datetime.now()

    # ------------------------------------------------------------------ #
    #  Properties (encapsulation – controlled read/write access)           #
    # ------------------------------------------------------------------ #

    @property
    def product_id(self) -> int:
        return self.__product_id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Product name must be a non-empty string.")
        if len(value.strip()) < 2:
            raise ValueError("Product name must be at least 2 characters.")
        if len(value.strip()) > 100:
            raise ValueError("Product name cannot exceed 100 characters.")
        self.__name = value.strip()

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, value) -> None:
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("Price must be a numeric value.")
        if value < 0:
            raise ValueError("Price cannot be negative.")
        self.__price = round(value, 2)

    @property
    def quantity(self) -> int:
        return self.__quantity

    @quantity.setter
    def quantity(self, value) -> None:
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("Quantity must be a whole number.")
        if value < 0:
            raise ValueError("Quantity cannot be negative.")
        self.__quantity = value

    @property
    def category(self) -> str:
        return self.__category

    @category.setter
    def category(self, value: str) -> None:
        self.__category = str(value)

    @property
    def supplier(self) -> str:
        return self.__supplier

    @supplier.setter
    def supplier(self, value: str) -> None:
        self.__supplier = str(value) if value else "Unknown"

    @property
    def created_at(self) -> datetime:
        return self.__created_at

    @property
    def low_stock_threshold(self) -> int:
        return self.__low_stock_threshold

    @low_stock_threshold.setter
    def low_stock_threshold(self, value) -> None:
        value = int(value)
        if value < 0:
            raise ValueError("Threshold cannot be negative.")
        self.__low_stock_threshold = value

    @property
    def is_low_stock(self) -> bool:
        """True when quantity is at or below the configured threshold."""
        return self.__quantity <= self.__low_stock_threshold

    # ------------------------------------------------------------------ #
    #  Abstract methods – polymorphic behaviour defined in subclasses       #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def get_type(self) -> str:
        """Return a short string identifying the product type."""

    @abstractmethod
    def get_display_info(self) -> str:
        """Return a formatted string describing type-specific attributes."""

    @abstractmethod
    def calculate_value(self) -> float:
        """Return total stock value (price × quantity)."""

    # ------------------------------------------------------------------ #
    #  Serialisation – used by Inventory to persist data as JSON           #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> dict:
        return {
            "product_id": self.__product_id,
            "type": self.get_type(),
            "name": self.__name,
            "price": self.__price,
            "quantity": self.__quantity,
            "category": self.__category,
            "supplier": self.__supplier,
            "low_stock_threshold": self.__low_stock_threshold,
            "created_at": self.__created_at.isoformat(),
        }

    # ------------------------------------------------------------------ #
    #  Dunder helpers                                                       #
    # ------------------------------------------------------------------ #

    def __str__(self) -> str:
        return f"[{self.__product_id}] {self.__name} – £{self.__price:.2f} (qty: {self.__quantity})"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self.__product_id}, name={self.__name!r}, "
            f"price={self.__price}, qty={self.__quantity})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Product):
            return NotImplemented
        return self.__product_id == other.product_id

    def __hash__(self) -> int:
        return hash(self.__product_id)


# ======================================================================= #
#  Concrete subclasses – each adds type-specific state and behaviour        #
# ======================================================================= #


class Electronics(Product):
    """
    Represents electronic goods.  Extends Product with a warranty period.
    Demonstrates inheritance – reuses all base behaviour and adds one extra
    attribute alongside a polymorphic override of calculate_value().
    """

    def __init__(
        self,
        name: str,
        price: float,
        quantity: int,
        category: str = "Electronics",
        supplier: str = "Unknown",
        warranty_years: int = 1,
        product_id: int = None,
        low_stock_threshold: int = 5,
        created_at=None,
        **kwargs,
    ) -> None:
        super().__init__(
            name, price, quantity, category, supplier,
            product_id, low_stock_threshold, created_at,
        )
        self.warranty_years = warranty_years

    @property
    def warranty_years(self) -> int:
        return self.__warranty_years

    @warranty_years.setter
    def warranty_years(self, value) -> None:
        value = int(value)
        if value < 0:
            raise ValueError("Warranty years cannot be negative.")
        self.__warranty_years = value

    # --- Polymorphic overrides ---

    def get_type(self) -> str:
        return "Electronics"

    def get_display_info(self) -> str:
        return f"Warranty: {self.__warranty_years} yr(s)"

    def calculate_value(self) -> float:
        return round(self.price * self.quantity, 2)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["warranty_years"] = self.__warranty_years
        return data


class PerishableGoods(Product):
    """
    Represents perishable items (food, drinks, etc.).
    Adds an expiry date and overrides calculate_value() so that expired
    stock is counted as £0 – a real-world business rule.
    """

    def __init__(
        self,
        name: str,
        price: float,
        quantity: int,
        category: str = "Perishable",
        supplier: str = "Unknown",
        expiry_date=None,
        product_id: int = None,
        low_stock_threshold: int = 5,
        created_at=None,
        **kwargs,
    ) -> None:
        super().__init__(
            name, price, quantity, category, supplier,
            product_id, low_stock_threshold, created_at,
        )
        if expiry_date is None:
            from datetime import timedelta
            self.__expiry_date = date.today() + timedelta(days=30)
        elif isinstance(expiry_date, str):
            self.__expiry_date = date.fromisoformat(expiry_date)
        else:
            self.__expiry_date = expiry_date

    @property
    def expiry_date(self) -> date:
        return self.__expiry_date

    @expiry_date.setter
    def expiry_date(self, value) -> None:
        if isinstance(value, str):
            value = date.fromisoformat(value)
        self.__expiry_date = value

    @property
    def is_expired(self) -> bool:
        return self.__expiry_date < date.today()

    @property
    def days_until_expiry(self) -> int:
        return (self.__expiry_date - date.today()).days

    def get_type(self) -> str:
        return "Perishable"

    def get_display_info(self) -> str:
        if self.is_expired:
            status = "EXPIRED"
        else:
            status = f"{self.days_until_expiry}d left"
        return f"Expiry: {self.__expiry_date.isoformat()} ({status})"

    def calculate_value(self) -> float:
        # Expired stock has no commercial value
        if self.is_expired:
            return 0.0
        return round(self.price * self.quantity, 2)

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["expiry_date"] = self.__expiry_date.isoformat()
        return data


class GeneralGoods(Product):
    """
    Catch-all product type for general/miscellaneous items.
    Demonstrates how the factory can always fall back to a concrete class
    without any additional attributes.
    """

    def __init__(
        self,
        name: str,
        price: float,
        quantity: int,
        category: str = "General",
        supplier: str = "Unknown",
        product_id: int = None,
        low_stock_threshold: int = 5,
        created_at=None,
        **kwargs,
    ) -> None:
        super().__init__(
            name, price, quantity, category, supplier,
            product_id, low_stock_threshold, created_at,
        )

    def get_type(self) -> str:
        return "General"

    def get_display_info(self) -> str:
        return "General product – no additional attributes."

    def calculate_value(self) -> float:
        return round(self.price * self.quantity, 2)
