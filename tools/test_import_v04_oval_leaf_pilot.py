#!/usr/bin/env python3
"""Adversarial true original OVAL->0.4 fresh import and canonical parity tests."""
from copy import deepcopy
import unittest
import xml.etree.ElementTree as ET

from import_v04_oval_leaf_pilot import convert,OD
from compare_v04_fresh_oval_import import compare
from test_audit_v04_original_oval_forward import (
    shell_source,registry_source,shell_native,registry_native,
)


class FreshSourceConversionTests(unittest.TestCase):
    def test_original_shellcommand_import_matches_independent_native_fixture(self):
        fresh=convert(shell_source(),"oval:a:def:1")
        r=compare(fresh,shell_native())
        self.assertEqual(r["status"],"TRUE_FRESH_OVAL_IMPORT_MATCHES_CANONICAL_040_TEST")
        self.assertFalse(r["full_converter_coverage_claim"])

    def test_original_registry_import_matches_independent_native_fixture(self):
        fresh=convert(registry_source(),"oval:b:def:1")
        r=compare(fresh,registry_native())
        self.assertEqual(r["capability"],"windows.registry")
        test=next(iter(fresh["assessment"]["tests"].values()))
        self.assertEqual(test["states"][0]["value"]["equals"],"0")

    def test_malformed_source_or_unsupported_construction_fails_closed(self):
        for source,definition,change in (
            (shell_source(),"oval:a:def:1",
             lambda root: next(n for n in root.iter() if n.tag=="{"+OD+"}filter").set("action","exclude")),
            (shell_source(),"oval:a:def:1",
             lambda root: next(n for n in root.iter() if n.tag=="{"+OD+"}criteria").set("negate","true")),
            (shell_source(),"oval:a:def:1",
             lambda root: next(n for n in root.iter() if n.tag.endswith("}shellcommand_test")).set("check","only one")),
            (registry_source(),"oval:b:def:1",
             lambda root: next(n for n in root.iter() if n.tag.endswith("}registry_test")).set("check","none satisfy")),
            (registry_source(),"oval:b:def:1",
             lambda root: next(n for n in root.iter() if n.tag.endswith("}registry_state")).set("datatype","int")),
        ):
            root=ET.fromstring(source)
            with self.subTest(source=definition,change=str(change)),self.assertRaises(ValueError):
                change(root)
                convert(ET.tostring(root),definition)

    def test_canonical_subtle_predicate_change_is_rejected(self):
        fresh=convert(shell_source(),"oval:a:def:1")
        native=shell_native()
        native["assessment"]["tests"]["bluetooth-test"]["object"]["filters"][0]["include"]["stdout_line"]["case_insensitive_equals"]="Camera"
        with self.assertRaisesRegex(ValueError,"differs"):
            compare(fresh,native)

    def test_empty_and_mutated_require_are_rejected(self):
        fresh=convert(registry_source(),"oval:b:def:1")
        current=registry_native()
        current["assessment"]["tests"]["bluetooth-registry-test"]["require"]="at_least_one_exists_and_all_match"
        with self.assertRaisesRegex(ValueError,"differs"):
            compare(fresh,current)


if __name__=="__main__":
    unittest.main()
