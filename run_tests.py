"""
run_tests.py – convenience script to execute the full test suite and
print a formatted summary.

Usage:
    python run_tests.py
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))


def main():
    loader = unittest.TestLoader()
    suite  = loader.discover(start_dir="tests", pattern="test_*.py")

    print("=" * 65)
    print("  RetailPro – Unit Test Suite")
    print("=" * 65)

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 65)
    if result.wasSuccessful():
        print(f"  ALL TESTS PASSED  ({result.testsRun} tests run)")
    else:
        print(f"  FAILURES: {len(result.failures)}   ERRORS: {len(result.errors)}")
        print(f"  Tests run: {result.testsRun}")
    print("=" * 65)

    sys.exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
