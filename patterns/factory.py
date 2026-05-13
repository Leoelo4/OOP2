"""
Factory pattern – ProductFactory.

The Factory pattern centralises object creation so the rest of the application
never needs to import or instantiate concrete product classes directly.
Adding a new product type only requires registering it here; no other code
changes are needed (Open/Closed Principle).
"""

from models.product import Electronics, GeneralGoods, PerishableGoods, Product


class ProductFactory:
    """
    Creates Product instances by type name.

    The internal registry maps string keys to concrete classes.  The
    register() classmethod allows new types to be plugged in at runtime
    without modifying this file.
    """

    _registry: dict = {
        "Electronics": Electronics,
        "Perishable": PerishableGoods,
        "General": GeneralGoods,
    }

    @classmethod
    def create(cls, product_type: str, **kwargs) -> Product:
        """
        Instantiate and return a Product of the given type.

        Raises
        ------
        ValueError
            If product_type is not in the registry.
        """
        if product_type not in cls._registry:
            raise ValueError(
                f"Unknown product type: {product_type!r}. "
                f"Valid options: {list(cls._registry.keys())}"
            )
        return cls._registry[product_type](**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> Product:
        """Reconstruct a Product from a dictionary (e.g. loaded from JSON)."""
        data = data.copy()
        product_type = data.pop("type", "General")
        return cls.create(product_type, **data)

    @classmethod
    def get_types(cls) -> list[str]:
        return list(cls._registry.keys())

    @classmethod
    def register(cls, type_name: str, product_class: type) -> None:
        """Extend the factory with a new concrete product type."""
        if not issubclass(product_class, Product):
            raise TypeError("product_class must be a subclass of Product.")
        cls._registry[type_name] = product_class
