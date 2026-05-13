"""
Inventory – the central data store for all products.

Implemented as a Singleton (via SingletonMeta) so the entire application
always works against the same in-memory state.  Persistence is handled
by serialising to/from a JSON file in the /data directory.

Observers can be attached to receive notifications whenever the inventory
changes (see patterns/observer.py).
"""

import json
import os
from typing import List, Optional

from models.product import Product
from patterns.factory import ProductFactory
from patterns.observer import InventoryObserver
from patterns.singleton import SingletonMeta

# Path to the persistent data file – sits inside the repo's /data folder
_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "stock.json")


class Inventory(metaclass=SingletonMeta):
    """
    Manages the collection of all products.

    Responsibilities:
      - CRUD operations on products
      - Notifying attached observers on every state change
      - Persisting data to disk after every mutation
      - Providing query helpers (search, filter, aggregates)
    """

    def __init__(self) -> None:
        self._products: dict[int, Product] = {}
        self._observers: list[InventoryObserver] = []
        self._load()

    # ------------------------------------------------------------------ #
    #  Observer management                                                  #
    # ------------------------------------------------------------------ #

    def attach(self, observer: InventoryObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: InventoryObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, event_type: str, product: Product) -> None:
        for obs in self._observers:
            obs.update(event_type, product)

    # ------------------------------------------------------------------ #
    #  CRUD                                                                 #
    # ------------------------------------------------------------------ #

    def add_product(self, product: Product) -> None:
        if product.product_id in self._products:
            raise ValueError(
                f"A product with ID {product.product_id} already exists."
            )
        self._products[product.product_id] = product
        self._notify("added", product)
        self._save()

    def get_product(self, product_id: int) -> Optional[Product]:
        return self._products.get(product_id)

    def get_all_products(self) -> List[Product]:
        return list(self._products.values())

    def update_product(self, product_id: int, **kwargs) -> Product:
        product = self._products.get(product_id)
        if product is None:
            raise KeyError(f"No product found with ID {product_id}.")
        for key, value in kwargs.items():
            setattr(product, key, value)
        self._notify("updated", product)
        self._save()
        return product

    def delete_product(self, product_id: int) -> Product:
        product = self._products.pop(product_id, None)
        if product is None:
            raise KeyError(f"No product found with ID {product_id}.")
        self._notify("deleted", product)
        self._save()
        return product

    # ------------------------------------------------------------------ #
    #  Query helpers                                                        #
    # ------------------------------------------------------------------ #

    def search(self, query: str) -> List[Product]:
        """Case-insensitive search across name, category and supplier."""
        q = query.lower().strip()
        return [
            p for p in self._products.values()
            if q in p.name.lower()
            or q in p.category.lower()
            or q in p.supplier.lower()
        ]

    def filter_by_category(self, category: str) -> List[Product]:
        return [p for p in self._products.values() if p.category == category]

    def filter_by_type(self, product_type: str) -> List[Product]:
        return [p for p in self._products.values() if p.get_type() == product_type]

    def get_low_stock_products(self) -> List[Product]:
        return [p for p in self._products.values() if p.is_low_stock]

    def get_categories(self) -> List[str]:
        return sorted({p.category for p in self._products.values()})

    def total_stock_value(self) -> float:
        return round(sum(p.calculate_value() for p in self._products.values()), 2)

    def count(self) -> int:
        return len(self._products)

    # ------------------------------------------------------------------ #
    #  Persistence                                                          #
    # ------------------------------------------------------------------ #

    def _save(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(_DATA_FILE)), exist_ok=True)
        data = [p.to_dict() for p in self._products.values()]
        with open(_DATA_FILE, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)

    def _load(self) -> None:
        if not os.path.exists(_DATA_FILE):
            return
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for item in data:
                product = ProductFactory.from_dict(item)
                self._products[product.product_id] = product
        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupt or incompatible data file – start with an empty inventory
            self._products = {}

    # ------------------------------------------------------------------ #
    #  Test utility                                                         #
    # ------------------------------------------------------------------ #

    def _clear_for_testing(self) -> None:
        """
        Wipes all products from memory WITHOUT writing to disk.
        Should only be called from unit-test setUp/tearDown.
        """
        self._products.clear()
        Product._id_counter = 0
