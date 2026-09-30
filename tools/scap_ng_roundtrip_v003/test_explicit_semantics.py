#!/usr/bin/env python3
"""Regression checks for explicitly supplied OVAL cardinality/assertion settings."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parent / "ng_to_oval.py"
spec = importlib.util.spec_from_file_location("ng_to_oval", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

NS = module.NS["unix"]
Q = lambda name: f"{{{NS}}}{name}"

class ExplicitSemanticsTests(unittest.TestCase):
    def test_emits_state_and_entity_quantifiers(self):
        fixture = {
            "id": "quantifier-001",
            "ng_semantics": {
                "checks": [{
                    "id": "c1", "type": "unix.file",
                    "check_existence": "at_least_one_exists",
                    "check": "all", "state_operator": "OR",
                    "collection": "o1", "states": ["s1"]
                }],
                "collections": [{
                    "id": "o1", "type": "unix.file",
                    "selectors": {"path": "/tmp", "filename": "fixture"}
                }],
                "states": [{
                    "id": "s1", "type": "unix.file", "operator": "OR",
                    "predicates": {
                        "path": {"value": "/tmp", "entity_check": "at least one",
                                 "check_existence": "none_exist"},
                        "filename": {"variable": "v1", "var_check": "all",
                                     "entity_check": "all"}
                    }
                }],
                "variables": [{
                    "id": "v1", "kind": "constant", "datatype": "string",
                    "values": ["fixture"]
                }]
            }
        }
        root = module.build(fixture).getroot()
        test = root.find(f".//{Q('file_test')}")
        state = root.find(f".//{Q('file_state')}")
        self.assertIsNotNone(test)
        self.assertIsNotNone(state)
        self.assertEqual(test.get("check_existence"), "at_least_one_exists")
        self.assertEqual(test.get("check"), "all")
        self.assertEqual(test.get("state_operator"), "OR")
        self.assertEqual(state.get("operator"), "OR")
        path = state.find(Q("path"))
        filename = state.find(Q("filename"))
        self.assertEqual(path.get("entity_check"), "at least one")
        self.assertEqual(path.get("check_existence"), "none_exist")
        self.assertEqual(filename.get("var_check"), "all")
        self.assertEqual(filename.get("entity_check"), "all")

    def test_entity_assertions_are_not_allowed_on_object_selectors(self):
        fixture = {"id": "invalid-object", "ng_semantics": {
            "collections": [{"id": "o1", "type": "unix.file",
                             "selectors": {"path": {
                                 "value": "/tmp", "check_existence": "none_exist"
                             }}}]}}
        with self.assertRaisesRegex(ValueError, "State entity assertion"):
            module.build(fixture)

    def test_var_check_requires_variable_reference(self):
        fixture = {"id": "invalid-state", "ng_semantics": {
            "states": [{"id": "s1", "type": "unix.file",
                        "predicates": {"path": {
                            "value": "/tmp", "var_check": "all"
                        }}}]}}
        with self.assertRaisesRegex(ValueError, "requires a variable"):
            module.build(fixture)

    def test_missing_required_existence_is_not_silently_guessed(self):
        fixture = {"id": "missing-001", "ng_semantics": {
            "checks": [{"id": "c1", "type": "unix.file", "check": "all",
                        "collection": "o1"}]}}
        with self.assertRaises(KeyError):
            module.build(fixture)

if __name__ == "__main__":
    unittest.main()
