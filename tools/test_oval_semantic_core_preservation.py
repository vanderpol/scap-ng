#!/usr/bin/env python3
"""Cross-version OVAL core regression: preserve v0.3-proven semantics for v0.4.

These are parser/semantic-IR checks, not claims that every shape already lowers
to native 0.4 source or executes correctly in a scanner.
"""
from pathlib import Path
import tempfile
import unittest

from oval_semantic_ir import parse


ROOT = Path(__file__).resolve().parents[1]


class CrossVersionOvalCore(unittest.TestCase):
    def test_original_set_filter_default_and_var_check(self):
        ir = parse(ROOT / "board/review-content/0.2.0/sources/filter.xml")
        self.assertEqual(ir["unresolved_references"], [])
        self.assertEqual((len(ir["definitions"]), len(ir["tests"]),
                          len(ir["objects"]), len(ir["states"]), len(ir["variables"])),
                         (1, 1, 2, 2, 1))
        obj = next(x for x in ir["objects"] if x["id"].endswith(":obj:373"))
        collection_set = obj["children"][0]
        self.assertEqual(collection_set["operator"], "UNION")
        self.assertFalse(collection_set["operator_explicit"])
        filter_node = next(x for x in collection_set["children"] if x["kind"] == "filter")
        self.assertEqual(filter_node["action"], "exclude")
        self.assertFalse(filter_node["action_explicit"])
        self.assertTrue(collection_set["evaluation_semantics"]["filters_apply_before_set_operator"])
        state = next(x for x in ir["states"] if x["id"].endswith(":ste:746"))
        self.assertEqual(state["entities"][0]["attributes"]["var_check"], "only one")

    def test_old_variable_function_and_cardinality_handling(self):
        ir = parse(ROOT / "research/iterations/003/evidence/roundtrip-source-oval/"
                   "cartesian-variable-chain.source.xml")
        self.assertEqual(ir["unresolved_references"], [])
        values = ir["variable_resolution"]
        self.assertEqual(values["oval:scap-ng.stress:var:3"]["status"], "exact_static")
        self.assertEqual(values["oval:scap-ng.stress:var:3"]["values"],
                         ["4", "5", "6", "5", "6", "7"])
        self.assertEqual(values["oval:scap-ng.stress:var:4"]["values"], ["6"])

    def test_current_original_oval_boolean_scope_and_missing_reference(self):
        path = ROOT / "tests/v04-oval-operator-scopes/oval-independent-operators.xml"
        ir = parse(path)
        self.assertEqual(ir["unresolved_references"], [])
        self.assertEqual(len(ir["definitions"]), 6)
        self.assertEqual([test["state_operator"] for test in ir["tests"]],
                         ["OR", "ONE", "XOR", "AND", "AND", "AND"])
        source = path.read_text(encoding="utf-8")
        modified = source.replace("state_ref=\"oval:scap-ng.logic-scope:ste:1\"",
                                  "state_ref=\"oval:scap-ng.logic-scope:ste:999\"", 1)
        self.assertNotEqual(source, modified)
        with tempfile.TemporaryDirectory() as folder:
            mutant = Path(folder) / "invalid-ref.xml"
            mutant.write_text(modified, encoding="utf-8")
            bad_ir = parse(mutant)
            self.assertIn("oval:scap-ng.logic-scope:ste:999", bad_ir["unresolved_references"])


if __name__ == "__main__":
    unittest.main()
