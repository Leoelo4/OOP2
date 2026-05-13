"""
InventoryController – the 'C' in the MVC architecture.

The controller sits between the GUI views and the domain model.  Views call
controller methods; the controller translates those calls into model operations
and returns results the view can render.  This keeps models free of GUI code
and views free of business logic.
"""

from models.inventory import Inventory
from models.product import Product
from patterns.factory import ProductFactory
from patterns.observer import AuditLogObserver, LowStockObserver


class InventoryController:
    """
    Mediates between GUI views and the Inventory model.

    Creates and wires up the two standard observers so every change is
    automatically tracked for low-stock alerts and auditing.
    """

    def __init__(self) -> None:
        self._inventory = Inventory()

        # Wire up the observers once at startup
        self._low_stock_obs = LowStockObserver()
        self._audit_obs = AuditLogObserver()
        self._inventory.attach(self._low_stock_obs)
        self._inventory.attach(self._audit_obs)

    # ------------------------------------------------------------------ #
    #  Product CRUD                                                         #
    # ------------------------------------------------------------------ #

    def add_product(self, product_type: str, **kwargs) -> Product:
        product = ProductFactory.create(product_type, **kwargs)
        self._inventory.add_product(product)
        return product

    def get_all_products(self) -> list[Product]:
        return self._inventory.get_all_products()

    def get_product(self, product_id: int) -> Product | None:
        return self._inventory.get_product(product_id)

    def update_product(self, product_id: int, **kwargs) -> Product:
        return self._inventory.update_product(product_id, **kwargs)

    def delete_product(self, product_id: int) -> Product:
        return self._inventory.delete_product(product_id)

    # ------------------------------------------------------------------ #
    #  Search & filter                                                      #
    # ------------------------------------------------------------------ #

    def search_products(self, query: str) -> list[Product]:
        return self._inventory.search(query)

    def get_low_stock_products(self) -> list[Product]:
        return self._inventory.get_low_stock_products()

    def get_categories(self) -> list[str]:
        return self._inventory.get_categories()

    def get_product_types(self) -> list[str]:
        return ProductFactory.get_types()

    # ------------------------------------------------------------------ #
    #  Aggregates                                                           #
    # ------------------------------------------------------------------ #

    def get_total_stock_value(self) -> float:
        return self._inventory.total_stock_value()

    def get_product_count(self) -> int:
        return self._inventory.count()

    def get_inventory_summary(self) -> dict:
        """
        Returns a summary dict used by the Reports window.

        Structure:
            {
                'total_products': int,
                'total_value'   : float,
                'low_stock_count': int,
                'by_category'   : { category: {'count': int, 'value': float} },
                'by_type'       : { type: {'count': int, 'value': float} },
            }
        """
        products = self._inventory.get_all_products()
        by_category: dict = {}
        by_type: dict = {}

        for p in products:
            # Aggregate by category
            if p.category not in by_category:
                by_category[p.category] = {"count": 0, "value": 0.0}
            by_category[p.category]["count"] += 1
            by_category[p.category]["value"] += p.calculate_value()

            # Aggregate by product type
            t = p.get_type()
            if t not in by_type:
                by_type[t] = {"count": 0, "value": 0.0}
            by_type[t]["count"] += 1
            by_type[t]["value"] += p.calculate_value()

        return {
            "total_products": len(products),
            "total_value": self._inventory.total_stock_value(),
            "low_stock_count": len(self._inventory.get_low_stock_products()),
            "by_category": by_category,
            "by_type": by_type,
        }

    # ------------------------------------------------------------------ #
    #  Observer data                                                        #
    # ------------------------------------------------------------------ #

    def get_low_stock_alerts(self) -> list[str]:
        alerts = self._low_stock_obs.get_alerts()
        self._low_stock_obs.clear_alerts()
        return alerts

    def peek_low_stock_alerts(self) -> list[str]:
        """Return alerts without clearing them."""
        return self._low_stock_obs.get_alerts()

    def has_low_stock_alerts(self) -> bool:
        return self._low_stock_obs.has_alerts()

    def get_audit_log(self) -> list[str]:
        return self._audit_obs.get_log()

    def export_audit_log(self, filepath: str) -> None:
        self._audit_obs.save_to_file(filepath)
