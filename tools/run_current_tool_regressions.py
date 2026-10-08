#!/usr/bin/env python3
"""Run maintained tool regressions without rebuilding frozen 0.2 Board content.

Historical 0.2 schemas are preserved under schema/v0.2.0. Their Board-pilot
conversion and sample-reproduction tests are deliberately excluded from active
0.3 CI. Shared SCAP 1.4 / OVAL semantic regressions are still included.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ARCHIVED_CONTENT_MODULES = frozenset({
    "test_board_conversion_v02",
    "test_board_samples_v02",
})


def iter_tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from iter_tests(item)
        else:
            yield item


def main():
    directory = Path(__file__).resolve().parent
    suite = unittest.TestLoader().discover(str(directory), pattern="test_*.py")
    all_tests = list(iter_tests(suite))
    current = [item for item in all_tests
               if item.__class__.__module__ not in ARCHIVED_CONTENT_MODULES]
    archived = len(all_tests) - len(current)
    print(f"Current regressions: {len(current)}; archived Board-pilot tests omitted: {archived}",
          file=sys.stderr)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(current))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
