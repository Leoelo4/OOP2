"""
Singleton metaclass.

The Singleton pattern guarantees that a class has only one instance
throughout the application's lifetime.  Here it is implemented as a
metaclass so any class can opt in by simply declaring
    class MyClass(metaclass=SingletonMeta): ...

Using a metaclass rather than a decorator or base class keeps the pattern
transparent – it does not pollute the class's own __init__ or MRO.
"""


class SingletonMeta(type):
    """
    Metaclass that intercepts __call__ on the class it governs.
    On first instantiation the real object is created and cached.
    Subsequent calls return that same cached object.
    """

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def _reset(cls) -> None:
        """
        Remove the cached instance so the next __call__ creates a fresh one.
        Only ever used in unit-test tearDown – not for production code.
        """
        cls._instances.pop(cls, None)
