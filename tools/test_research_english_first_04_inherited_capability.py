#!/usr/bin/env python3
"""Fail-closed fixtures for source-owned inspector research (#235)."""
import copy
import unittest

from research_english_first_04_inherited_capability import Unsupported, restore, transform


BASE = {
    "metadata": {"id": "fixture"},
    "sources": {
        "role": {
            "inspect": "windows.wmi.query",
            "collect": {"query": "SELECT DomainRole FROM win32_computersystem"},
        }
    },
    "checks": {
        "read-role": {
            "check": "Determine Windows domain role",
            "inspect": "windows.wmi.query",
            "from": "role",
            "require": {"items": "at_least_one"},
        },
        "builtin": {
            "check": "Minimum password length",
            "inspect": "windows.passwordpolicy",
            "require": {"min_passwd_len": {"at_least": 14}},
        },
    },
    "evaluate": {"test": "read-role"},
}


class SourceTypeInheritanceTests(unittest.TestCase):
    def test_exact_roundtrip_and_builtin_unchanged(self):
        compact, changed = transform(BASE)
        self.assertEqual(changed, 1)
        self.assertNotIn("inspect", compact["checks"]["read-role"])
        self.assertIn("inspect", compact["checks"]["builtin"])
        self.assertEqual(restore(compact), BASE)

    def test_inconsistent_source_type_rejected(self):
        bad = copy.deepcopy(BASE)
        bad["checks"]["read-role"]["inspect"] = "unix.file"
        with self.assertRaises(Unsupported):
            transform(bad)

    def test_undeclared_source_rejected(self):
        bad = copy.deepcopy(BASE)
        bad["checks"]["read-role"]["from"] = "missing"
        with self.assertRaises(Unsupported):
            transform(bad)

    def test_untyped_source_rejected(self):
        bad = copy.deepcopy(BASE)
        del bad["sources"]["role"]["inspect"]
        with self.assertRaises(Unsupported):
            transform(bad)

    def test_from_with_extra_selector_rejected(self):
        bad = copy.deepcopy(BASE)
        bad["checks"]["read-role"]["where"] = {"name": {"is": "foo"}}
        with self.assertRaises(Unsupported):
            transform(bad)

    def test_from_with_extra_collection_rejected(self):
        bad = copy.deepcopy(BASE)
        bad["checks"]["read-role"]["collect"] = {"query": "SELECT * FROM foo"}
        with self.assertRaises(Unsupported):
            transform(bad)


if __name__ == "__main__":
    unittest.main()
