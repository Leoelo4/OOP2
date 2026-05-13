"""
Observer pattern implementation.

The Observer (also called Publish-Subscribe) pattern defines a one-to-many
dependency so that when one object (the subject) changes state, all its
dependants (observers) are notified automatically.

Here the Inventory acts as the subject.  Two concrete observers are provided:
  - LowStockObserver  : flags products that fall below their threshold
  - AuditLogObserver  : keeps a timestamped record of every inventory event
"""

from abc import ABC, abstractmethod
from datetime import datetime


class InventoryObserver(ABC):
    """Abstract base for all inventory observers."""

    @abstractmethod
    def update(self, event_type: str, product) -> None:
        """
        Called by the Inventory whenever a product is added, updated or deleted.

        Parameters
        ----------
        event_type : str
            One of: 'added', 'updated', 'deleted'
        product    : Product
            The product that triggered the event.
        """


class LowStockObserver(InventoryObserver):
    """
    Watches for products whose quantity falls to or below their threshold.
    Alerts are accumulated in a list so the GUI can collect and display them.
    """

    def __init__(self) -> None:
        self._alerts: list[str] = []

    def update(self, event_type: str, product) -> None:
        # Only relevant when stock is being added or changed, not deleted
        if event_type in ("added", "updated") and product.is_low_stock:
            msg = (
                f"LOW STOCK – '{product.name}' has only "
                f"{product.quantity} unit(s) remaining "
                f"(threshold: {product.low_stock_threshold})."
            )
            # Avoid duplicate alerts for the same product in a session
            if msg not in self._alerts:
                self._alerts.append(msg)

    def get_alerts(self) -> list[str]:
        return list(self._alerts)

    def clear_alerts(self) -> None:
        self._alerts.clear()

    def has_alerts(self) -> bool:
        return len(self._alerts) > 0


class AuditLogObserver(InventoryObserver):
    """
    Maintains a timestamped audit trail of every operation performed on
    the inventory.  Useful for accountability and debugging.
    """

    def __init__(self) -> None:
        self._log: list[str] = []

    def update(self, event_type: str, product) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {event_type.upper():8s} | {product}"
        self._log.append(entry)

    def get_log(self) -> list[str]:
        return list(self._log)

    def save_to_file(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as fh:
            fh.write("\n".join(self._log))
