#!/usr/bin/env python3
"""Structural losslessness tests for the embedded predicate migration."""
import copy
import unittest

from scap_upconvert_v003.embed_predicates import (
    embed_predicates, reexpand_predicates,
)


def example():
    expected = {
        "field": "owner_uid",
        "operation": "equals",
        "value": {"variable": "root-uid-variable"},
        "datatype": "integer",
        "match": "all",
        "existence": "one_or_more",
        "value_match": "one",
    }
    return {"assessment": {
        "id": "source-assessment",
        "mode": "automated",
        "variables": {"root-uid-variable": {"kind": "constant", "value": 0}},
        "objects": {
            "root-files-object": {
                "capability": "unix.file",
                "select": {"directory": "/usr/bin"},
            },
            "filtered-files-object": {
                "capability": "unix.file",
                "set": {"operator": "union", "operands": [{
                    "object": "root-files-object",
                    "filters": [
                        {"action": "exclude", "state": "root-owner-state"},
                        {"action": "include", "state": {
                            "capability": "unix.file", "state_title": "Config files",
                            "state": {"field": "name", "operation": "pattern_match",
                                      "value": ".*[.]conf", "datatype": "string",
                                      "match": "one_or_more", "existence": "one_or_more"},
                        }},
                    ],
                }]},
            },
        },
        "states": {
            "root-owner-state": {
                "capability": "unix.file",
                "state_title": "Root ownership",
                "state": expected,
            },
            "unused-state": {
                "capability": "unix.file",
                "state_title": "Unreferenced source residue",
                "state": {"field": "size", "value": 1},
            },
        },
        "tests": {
            "owner-test": {
                "capability": "unix.file",
                "object": "filtered-files-object",
                "states": ["root-owner-state"],
                "existence": "none", "match": "all",
            },
            "second-test": {
                "capability": "unix.file",
                "object": "root-files-object",
                "states": ["root-owner-state", {
                    "capability": "unix.file",
                    "state_title": "Record condition",
                    "state": {"all": [
                        {"field": "name", "datatype": "string", "value": "x",
                         "operation": "equals", "match": "all", "existence": "one_or_more"},
                        {"field": "owner_uid", "datatype": "integer", "value": 0,
                         "operation": "equals", "match": "all", "existence": "one_or_more"},
                    ]},
                }],
                "states_match": "all",
            },
        },
        "evaluate": {"all": [{"test": "owner-test"}, {"test": "second-test"}]},
    }}


class EmbeddedPredicates(unittest.TestCase):
    def test_reused_state_across_tests_and_filter_is_inlined(self):
        old = example()
        saved = copy.deepcopy(old)
        new, ledger = embed_predicates(old)
        assessment = new["assessment"]
        self.assertNotIn("states", assessment)
        predicate = saved["assessment"]["states"]["root-owner-state"]["state"]
        self.assertEqual(assessment["tests"]["owner-test"]["states"][0], predicate)
        self.assertEqual(assessment["tests"]["second-test"]["states"][0], predicate)
        filters = assessment["objects"]["filtered-files-object"]["set"]["operands"][0]["filters"]
        self.assertEqual(filters[0], {"action": "exclude", **predicate})
        self.assertEqual(filters[1]["field"], "name")
        self.assertNotIn("state", filters[1])
        self.assertNotIn("state_title", filters[1])
        self.assertNotIn("filter_title", filters[1])
        self.assertNotIn("capability", filters[1])
        self.assertEqual(ledger["changes"][0]["original"], "root-owner-state")
        self.assertEqual(assessment["tests"]["second-test"]["states"][1]["all"][0]["field"], "name")
        self.assertEqual(assessment["tests"]["owner-test"]["existence"], "none")
        self.assertEqual(assessment["evaluate"], saved["assessment"]["evaluate"])
        self.assertEqual(reexpand_predicates(new, ledger), saved)
        self.assertEqual(old, saved)

    def test_no_change_to_collected_object_or_set_semantics(self):
        old = example()
        new, _ = embed_predicates(old)
        operand_before = old["assessment"]["objects"]["filtered-files-object"]["set"]["operands"][0]
        operand_after = new["assessment"]["objects"]["filtered-files-object"]["set"]["operands"][0]
        self.assertEqual(operand_before["object"], operand_after["object"])
        self.assertEqual([f["action"] for f in operand_before["filters"]],
                         [f["action"] for f in operand_after["filters"]])
        self.assertEqual(old["assessment"]["objects"]["root-files-object"],
                         new["assessment"]["objects"]["root-files-object"])

    def test_orphan_named_state_is_ledger_only(self):
        new, ledger = embed_predicates(example())
        self.assertNotIn("unused-state", str(new))
        self.assertIn("unused-state", ledger["named_states"])

    def test_idempotent_normalization(self):
        new, _ = embed_predicates(example())
        again, ledger = embed_predicates(new)
        self.assertEqual(again, new)
        self.assertEqual(ledger["changes"], [])

    def test_capability_mismatch_is_fatal(self):
        old = example()
        old["assessment"]["tests"]["owner-test"]["capability"] = "windows.registry"
        with self.assertRaisesRegex(ValueError, "capability mismatch"):
            embed_predicates(old)

    def test_filter_capability_mismatch_is_fatal(self):
        old = example()
        old["assessment"]["tests"]["owner-test"]["states"] = []
        old["assessment"]["tests"]["second-test"]["states"] = []
        old["assessment"]["states"]["root-owner-state"]["capability"] = "windows.registry"
        with self.assertRaisesRegex(ValueError, "capability mismatch"):
            embed_predicates(old)

    def test_missing_named_state_is_fatal(self):
        old = example()
        old["assessment"]["tests"]["owner-test"]["states"] = ["not-present"]
        with self.assertRaisesRegex(ValueError, "missing named State"):
            embed_predicates(old)

    def test_unsupported_wrapper_metadata_is_fatal(self):
        old = example()
        old["assessment"]["states"]["root-owner-state"]["unknown"] = "x"
        with self.assertRaisesRegex(ValueError, "unsupported State wrapper"):
            embed_predicates(old)

    def test_action_field_collision_is_fatal(self):
        old = example()
        old["assessment"]["states"]["root-owner-state"]["state"]["action"] = "surprise"
        with self.assertRaisesRegex(ValueError, "action would collide"):
            embed_predicates(old)

    def test_missing_set_operand_object_is_fatal(self):
        old = example()
        old["assessment"]["objects"]["filtered-files-object"]["set"]["operands"][0]["object"] = "no-object"
        with self.assertRaisesRegex(ValueError, "unresolved Filter Object"):
            embed_predicates(old)

    def test_unconverted_state_use_is_fatal(self):
        old = example()
        old["assessment"]["unexpected"] = {"state": "root-owner-state"}
        with self.assertRaisesRegex(ValueError, "unconverted reference"):
            embed_predicates(old)

    def test_tampered_native_comparison_invalidates_ledger(self):
        new, ledger = embed_predicates(example())
        new["assessment"]["tests"]["owner-test"]["states"][0]["value"] = 1000
        with self.assertRaisesRegex(ValueError, "changed migrated predicate"):
            reexpand_predicates(new, ledger)

    def test_manual_untouched(self):
        manual = {"assessment": {"mode": "manual", "response": {"type": "compliance"}}}
        new, ledger = embed_predicates(manual)
        self.assertEqual(new, manual)
        self.assertEqual(reexpand_predicates(new, ledger), manual)


if __name__ == "__main__":
    unittest.main()
