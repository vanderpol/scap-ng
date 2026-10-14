#!/usr/bin/env python3
"""Self-contained, non-normative 0.4 lowering tests."""
import unittest
from copy import deepcopy

from research_04_self_contained_inline import (
    inline_variable, inline_object, lower_inline, analyze_chain,
)

def fixture():
    return {"assessment": {
        "id": "example",
        "variables": {
            "path-variable": {
                "kind": "local", "datatype": "string",
                "expression": {"concat": [
                    {"literal": "/srv/"}, {"object": "user-object"}]},
                "provenance": {"source": "OVAL fixture"},
            },
        },
        "shared_objects": {
            "user-object": {"capability": "unix.password", "select": {}},
            "foreach-user-object": {"capability": "unix.password", "select": {}},
            "directory-object": {"capability": "unix.file",
                "for_each": {"item": "user", "in": "foreach-user-object"},
                "select": {"directory": {"from": "user.home_dir"}}},
        },
        "tests": {
            "check-test": {"object": {"capability":"unix.file", "select": {
                "path": {"value": {"variable":"path-variable"}}
            }}}
        },
    }}

class ResearchInlineTest(unittest.TestCase):
    def test_inline_variable_independently_reconstructs(self):
        doc=fixture()
        inline, info=inline_variable(doc, "path-variable")
        self.assertNotIn("path-variable", inline["assessment"].get("variables", {}))
        self.assertEqual(lower_inline(inline), doc)
        self.assertEqual(info["kind"], "variable")

    def test_inline_foreach_source_independently_reconstructs(self):
        doc=fixture()
        inline, info=inline_object(doc, "foreach-user-object")
        self.assertNotIn("foreach-user-object", inline["assessment"]["shared_objects"])
        self.assertEqual(lower_inline(inline), doc)

    def test_reject_reused_variable(self):
        doc=fixture()
        doc["assessment"]["tests"]["second-test"]={
            "object": {"select": {"path": {"value": {"variable":"path-variable"}}}}}
        with self.assertRaisesRegex(ValueError, "not private"):
            inline_variable(doc, "path-variable")

    def test_reject_variable_chain_without_explicit_option(self):
        doc=fixture()
        doc["assessment"]["variables"]["outer-variable"]={
            "kind":"local", "datatype":"string",
            "expression":{"variable":"path-variable"}}
        doc["assessment"]["tests"]["check-test"]["object"]["select"]["path"]["value"]={"variable":"outer-variable"}
        with self.assertRaisesRegex(ValueError, "chain"):
            inline_variable(doc, "path-variable")
        inline, info=inline_variable(doc, "path-variable", allow_chain=True)
        self.assertTrue(info["consumer_is_variable"])
        self.assertEqual(lower_inline(inline), doc)

    def test_reject_reused_object(self):
        doc=fixture()
        doc["assessment"]["tests"]["reuser"]={"object":"foreach-user-object"}
        with self.assertRaisesRegex(ValueError, "exactly one"):
            inline_object(doc, "foreach-user-object")

    def test_reject_tampered_type(self):
        doc=fixture()
        inline,_=inline_variable(doc, "path-variable")
        node=inline["assessment"]["tests"]["check-test"]["object"]["select"]["path"]["value"]
        node["research_inline_variable"]["definition"]["datatype"]="boolean"
        self.assertNotEqual(lower_inline(inline),doc)

    def test_missing_metadata_rejected_by_exact_equality(self):
        doc=fixture()
        inline,_=inline_variable(doc, "path-variable")
        node=inline["assessment"]["tests"]["check-test"]["object"]["select"]["path"]["value"]
        node["research_inline_variable"]["definition"].pop("provenance")
        self.assertNotEqual(lower_inline(inline),doc)

    def test_duplicate_inline_declaration_rejected(self):
        doc=fixture()
        inline,_=inline_variable(doc, "path-variable")
        node=inline["assessment"]["tests"]["check-test"]["object"]["select"]["path"]["value"]
        inline["assessment"]["tests"]["second-test"]={"object": {"select":{"path":{"value":deepcopy(node)}}}}
        with self.assertRaisesRegex(ValueError, "Duplicate private declaration"):
            lower_inline(inline)

    def test_explicit_reject_input_kind(self):
        doc=fixture()
        doc["assessment"]["variables"]["path-variable"]["kind"]="external"
        with self.assertRaises(ValueError):
            inline_variable(doc, "path-variable")

    def test_chains_count_without_claim(self):
        doc=fixture()
        doc["assessment"]["variables"]["source-variable"]={
            "kind":"local","datatype":"string",
            "expression":{"literal":"abc"}}
        doc["assessment"]["variables"]["path-variable"]["expression"]={
            "variable":"source-variable"}
        a=analyze_chain(doc["assessment"])
        self.assertEqual(a["dependency_edges"],1)
        self.assertEqual(a["variable_producers_used_once_in_chains"],1)

if __name__=="__main__":
    unittest.main()
