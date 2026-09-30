#!/usr/bin/env python3
"""Focused forward-importer tests for effective OVAL defaults and provenance."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from lxml import etree

FILE = Path(__file__).resolve().parent / "oval_semantic_ir.py"
spec = importlib.util.spec_from_file_location("oval_semantic_ir", FILE)
ir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ir)

OVAL = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
UNIX = OVAL + "#unix"


def element(source):
    return etree.fromstring(source.encode("utf-8"))


class EffectiveAttributeTests(unittest.TestCase):
    def test_state_entity_default_and_explicit_are_semantically_equal(self):
        omitted = element("<path>/tmp</path>")
        explicit = element(
            '<path check_existence="at_least_one_exists" entity_check="all">/tmp</path>'
        )
        a = ir.effective_attributes(omitted, "state_entity")
        b = ir.effective_attributes(explicit, "state_entity")
        self.assertEqual(
            {k: v["value"] for k, v in a.items()},
            {k: v["value"] for k, v in b.items()},
        )
        self.assertEqual(a["check_existence"]["origin"], "xsd_default")
        self.assertEqual(b["check_existence"]["origin"], "explicit")
        self.assertEqual(a["entity_check"]["value"], "all")

    def test_nondefault_existence_remains_distinct(self):
        omitted = ir.effective_attributes(element("<path/>"), "state_entity")
        different = ir.effective_attributes(
            element('<path check_existence="none_exist"/>'), "state_entity"
        )
        self.assertNotEqual(
            omitted["check_existence"]["value"],
            different["check_existence"]["value"],
        )

    def test_documented_variable_default_only_with_reference(self):
        no_variable = ir.effective_attributes(element("<path/>"), "state_entity")
        with_variable = ir.effective_attributes(
            element('<path var_ref="oval:example:var:1"/>'), "state_entity"
        )
        self.assertNotIn("var_check", no_variable)
        self.assertEqual(with_variable["var_check"], {
            "value": "all", "origin": "documented_implicit"
        })
        explicit = ir.effective_attributes(
            element('<path var_ref="oval:example:var:1" var_check="at least one"/>'),
            "state_entity",
        )
        self.assertEqual(explicit["var_check"], {
            "value": "at least one", "origin": "explicit"
        })

    def test_forward_state_ir_keeps_original_xml_and_effective_values(self):
        state = element(
            f'<unix:file_state xmlns:unix="{UNIX}" '
            'id="oval:example:ste:1" version="1">'
            '<unix:path var_ref="oval:example:var:1"/>'
            '</unix:file_state>'
        )
        parsed = ir.parse_state(state)
        self.assertEqual(parsed["operator"], "AND")
        self.assertEqual(
            parsed["effective_attributes"]["operator"]["origin"], "xsd_default"
        )
        entity = parsed["entities"][0]
        self.assertEqual(entity["attributes"], {
            "var_ref": "oval:example:var:1"
        })
        self.assertEqual(
            entity["effective_attributes"]["check_existence"]["value"],
            "at_least_one_exists",
        )
        self.assertEqual(
            entity["effective_attributes"]["var_check"]["origin"],
            "documented_implicit",
        )

    def test_test_level_defaults_are_independent(self):
        test = element(
            f'<unix:file_test xmlns:unix="{UNIX}" '
            'id="oval:example:tst:1" version="1" check="all"/>'
        )
        parsed = ir.parse_test(test)
        self.assertEqual(parsed["check_existence"], "at_least_one_exists")
        self.assertEqual(
            parsed["effective_attributes"]["check_existence"]["origin"],
            "xsd_default",
        )
        self.assertEqual(
            parsed["effective_attributes"]["state_operator"]["value"], "AND"
        )

    def test_missing_required_check_is_not_defaulted(self):
        # The upstream OVAL 5.12.3 TestType requires check; unlike
        # check_existence, it has no XSD default.
        invalid = element(
            f'<unix:file_test xmlns:unix="{UNIX}" '
            'id="oval:example:tst:1" version="1" comment="invalid"/>'
        )
        parsed = ir.parse_test(invalid)
        self.assertIsNone(parsed["check"])
        self.assertIn("check", parsed["missing_required_attributes"])
        self.assertEqual(
            parsed["effective_attributes"]["check_existence"]["value"],
            "at_least_one_exists",
        )

    def test_unknown_scope_fails_closed(self):
        with self.assertRaises(ValueError):
            ir.effective_attributes(element("<path/>"), "behavior")


if __name__ == "__main__":
    unittest.main()
