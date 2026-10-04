#!/usr/bin/env python3
"""Regression checks for explicitly supplied OVAL cardinality/assertion settings."""
import importlib.util
from pathlib import Path
import unittest
import tempfile

SCRIPT = Path(__file__).resolve().parent / "ng_to_oval.py"
spec = importlib.util.spec_from_file_location("ng_to_oval", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

COMPARE = Path(__file__).resolve().parent / "compare_oval_semantics.py"
compare_spec = importlib.util.spec_from_file_location("compare_oval_semantics", COMPARE)
comparator = importlib.util.module_from_spec(compare_spec)
compare_spec.loader.exec_module(comparator)

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

    def test_comparator_resolves_state_existence_defaults(self):
        ns = module.NS["unix"]
        template = (
            '<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5" '
            'xmlns:unix="' + ns + '">'
            '<states><unix:file_state id="oval:example:ste:1" version="1">'
            '<unix:path {attribute} >/tmp</unix:path>'
            '</unix:file_state></states></oval_definitions>'
        )
        with tempfile.TemporaryDirectory() as directory:
            def semantic_state(attribute):
                filename = Path(directory) / "state.xml"
                filename.write_text(template.format(attribute=attribute), encoding="utf-8")
                return comparator.Model(filename).state("oval:example:ste:1")
            omitted = semantic_state("")
            explicit_default = semantic_state('check_existence="at_least_one_exists"')
            explicit_different = semantic_state('check_existence="none_exist"')
            self.assertEqual(omitted, explicit_default)
            self.assertNotEqual(omitted, explicit_different)

    def test_missing_required_existence_is_not_silently_guessed(self):
        fixture = {"id": "missing-001", "ng_semantics": {
            "checks": [{"id": "c1", "type": "unix.file", "check": "all",
                        "collection": "o1"}]}}
        with self.assertRaises(KeyError):
            module.build(fixture)

    def test_float_lexical_forms_compare_by_value(self):
        self.assertEqual(
            comparator.semantic_scalar("float", "-12432.559e-3"),
            comparator.semantic_scalar("float", "-12.432559"),
        )
        self.assertEqual(
            comparator.semantic_scalar("float", "0.0"),
            comparator.semantic_scalar("float", "-0"),
        )
        self.assertNotEqual(
            comparator.semantic_scalar("float", "1.0"),
            comparator.semantic_scalar("float", "1.0001"),
        )

if __name__ == "__main__":
    unittest.main()
