# RetailPro – Stock Management System

**Module:** Object Oriented Programming | Year 2, Semester 2  
**Assignment:** Create a GUI-Based Object-Oriented Application  

---

## Overview

A desktop stock management application for a small retail outlet, built with Python 3 and tkinter.  
Demonstrates all four OOP principles (Encapsulation, Inheritance, Polymorphism, Abstraction) and four design patterns (Singleton, Observer, Factory, MVC).

---

## Project Structure

```
OOP2/
├── main.py                          # Entry point – run this to start the app
├── run_tests.py                     # Runs the full unit test suite
├── generate_presentation.py         # Generates RetailPro_Presentation.pptx
├── requirements.txt                 # python-pptx (tkinter is stdlib)
│
├── models/
│   ├── product.py                   # Abstract Product + Electronics, Perishable, General
│   └── inventory.py                 # Singleton inventory with JSON persistence
│
├── patterns/
│   ├── singleton.py                 # SingletonMeta metaclass
│   ├── observer.py                  # InventoryObserver, LowStockObserver, AuditLogObserver
│   └── factory.py                   # ProductFactory (registry-based)
│
├── controllers/
│   └── inventory_controller.py      # MVC controller – mediates between views and model
│
├── views/
│   ├── theme.py                     # Colour palette, fonts, ttk styles
│   ├── main_window.py               # Primary application window
│   ├── product_dialog.py            # Add / Edit product modal dialog
│   ├── reports_window.py            # Reports & analytics (3 tabs)
│   └── low_stock_window.py          # Low stock alert + quick-restock window
│
├── utils/
│   ├── validators.py                # Input validation functions
│   └── exporter.py                  # CSV and JSON export utilities
│
├── tests/
│   ├── test_product.py
│   ├── test_inventory.py
│   ├── test_validators.py
│   └── test_factory.py
│
└── data/
    └── stock.json                   # Auto-created on first run
```

---

## Running the Application

```bash
python main.py
```

No additional packages needed – tkinter ships with Python 3.

---

## Running the Tests

```bash
python run_tests.py
```

81 tests across 4 test files. Expected output: `ALL TESTS PASSED (81 tests run)`

---

## Generating the Presentation

```bash
pip install python-pptx
python generate_presentation.py
```

Produces `RetailPro_Presentation.pptx` (15 slides) in the project root.

---

## OOP Principles

| Principle | Where Applied |
|---|---|
| Encapsulation | Private `__fields` with property descriptors and validated setters in `Product` |
| Inheritance | `Electronics`, `PerishableGoods`, `GeneralGoods` extend abstract `Product` |
| Polymorphism | `calculate_value()` and `get_display_info()` behave differently per subclass |
| Abstraction | `Product` is an ABC; concrete types must implement three abstract methods |

## Design Patterns

| Pattern | Location | Purpose |
|---|---|---|
| Singleton | `patterns/singleton.py` + `Inventory` | Single source of truth for all stock data |
| Observer | `patterns/observer.py` | Decoupled low-stock alerts and audit logging |
| Factory | `patterns/factory.py` | Centralised, extensible product creation |
| MVC | `controllers/` + `views/` | Separation of GUI from business logic |

---

## Key Features

- Full CRUD operations on three product types
- Persistent JSON storage (survives restarts)
- Real-time low-stock alerts via the Observer pattern
- Inventory reports with category/type breakdown and audit trail
- CSV export
- Search and filter across name, category, and supplier
- Keyboard shortcuts: `Ctrl+N` Add · `Ctrl+E` Edit · `Del` Delete · `F5` Refresh · `Ctrl+R` Reports

---

## References

- Gamma, E. et al. (1994) *Design Patterns*. Addison-Wesley.
- Nielsen, J. (1994) *Usability Engineering*. Morgan Kaufmann.
- Lutz, M. (2013) *Learning Python*, 5th edn. O'Reilly Media.
- Freeman, E. and Robson, E. (2020) *Head First Design Patterns*, 2nd edn. O'Reilly Media.
