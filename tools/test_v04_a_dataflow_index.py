#!/usr/bin/env python3
"""#240: adversarial source-dataflow indexing, NOT collection execution."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from v04_a_dataflow_index import index_assessment_dataflow


def source():
    return {
        "id": "ng.synthetic.dataflow", "mode": "automated",
        "shared_objects": {
            "users-object": {"capability": "unix.password",
                             "select": {"username": {"equals": "bob"}}},
            "files-object": {"capability": "unix.file",
                             "for_each": {"item": "user", "in": "users-object"},
                             "select": {"directory": {"from": "user.home_dir"}}},
            "filtered-object": {"capability": "unix.file",
                                "set": {"operator": "union", "operands": [
                                    {"object": "files-object",
                                     "filters": [
                                         {"include": {"owner_uid": {"equals": 0}}},
                                         {"exclude": {"owner_uid": {"equals": 1234}}}]},
                                    {"object": "files-object", "filters": []}]}}
        },
        "variables": {
            "files-variable": {"kind": "local", "expression": {
                "object": "filtered-object"}},
            "owners-variable": {"kind": "local", "expression": {
                "concat": [{"variable": "files-variable"}, " /tmp"]}}},
        "tests": {"check-test": {
            "capability": "unix.file", "object": "filtered-object",
            "states": [{"owner_uid": {"equals": {"variable": "owners-variable"}}}]}}
    }


class DataflowTests(unittest.TestCase):
    def test_dependency_first_no_execution_or_test_cardinality_rewrite(self):
        doc = source()
        before = deepcopy(doc)
        result = index_assessment_dataflow(doc)
        self.assertEqual(doc, before)
        self.assertEqual(result["status"], "SOURCE_DATAFLOW_ONLY_NOT_EXECUTABLE")
        self.assertEqual(len(result["nodes"]), 6)
        self.assertEqual(len([s for s in result["sites"] if s["kind"] == "filter"]), 2)
        self.assertEqual(len([s for s in result["sites"] if s["kind"] == "for_each"]), 1)
        self.assertEqual(len([s for s in result["sites"] if s["kind"] == "projection"]), 1)
        self.assertEqual(len([s for s in result["sites"] if s["kind"] == "set"]), 1)
        self.assertEqual([x["id"] for x in result["dependency_first_source_order"]],
                         ["users-object", "files-object", "filtered-object",
                          "files-variable", "owners-variable"])
        self.assertEqual(len([e for e in result["edges"]
                              if e["role"] == "object_acquisition" and
                              e["to_id"] == "files-object"]), 2)
        self.assertEqual(len([e for e in result["edges"]
                              if e["role"] == "for_each_source"]), 1)
        self.assertEqual(result["edge_count"], len(result["edges"]))

    def test_variable_reference_missing_fails_closed(self):
        d = source()
        d["variables"]["owners-variable"]["expression"]["concat"][0]["variable"] = "missing-variable"
        with self.assertRaisesRegex(ValueError, "unresolved variable"):
            index_assessment_dataflow(d)

    def test_nested_set_reference_missing_fails_closed(self):
        d = source()
        d["shared_objects"]["filtered-object"]["set"]["operands"][0]["object"] = "missing-object"
        with self.assertRaisesRegex(ValueError, "unresolved object"):
            index_assessment_dataflow(d)

    def test_foreach_object_reference_missing_fails_closed(self):
        d = source()
        d["shared_objects"]["files-object"]["for_each"]["in"] = "missing-object"
        with self.assertRaisesRegex(ValueError, "unresolved for_each Object"):
            index_assessment_dataflow(d)

    def test_foreach_source_requires_explicit_item_and_in(self):
        d = source()
        d["shared_objects"]["files-object"]["for_each"].pop("item")
        with self.assertRaisesRegex(ValueError, "invalid for_each source"):
            index_assessment_dataflow(d)

    def test_cyclic_variables_fail(self):
        d = source()
        d["variables"]["files-variable"]["expression"] = {
            "variable": "owners-variable"}
        with self.assertRaisesRegex(ValueError, "cyclic source dataflow"):
            index_assessment_dataflow(d)

    def test_cyclic_objects_fail(self):
        d = source()
        d["shared_objects"]["users-object"]["for_each"] = {
            "item": "file", "in": "files-object"}
        with self.assertRaisesRegex(ValueError, "cyclic source dataflow"):
            index_assessment_dataflow(d)

    def test_cross_kind_cycle_fails(self):
        d = source()
        d["shared_objects"]["users-object"]["select"]["username"] = {
            "equals": {"variable": "owners-variable"}}
        with self.assertRaisesRegex(ValueError, "cyclic source dataflow"):
            index_assessment_dataflow(d)

    def test_filter_requires_explicit_single_action(self):
        d = source()
        d["shared_objects"]["filtered-object"]["set"]["operands"][0]["filters"] = [
            {"include": {"a": {"equals": 1}},
             "exclude": {"b": {"equals": 2}}}]
        with self.assertRaisesRegex(ValueError, "Filter action missing or ambiguous"):
            index_assessment_dataflow(d)

    def test_nested_foreach_inherits_outer_alias_without_shadowing(self):
        d = source()
        d["shared_objects"]["inner-object"] = {
            "capability": "unix.file",
            "for_each": {"item": "file", "in": "files-object"},
            "select": {"file_path": {"from": "file.name"},
                       "user_home": {"from": "user.home_dir"}}}
        out = index_assessment_dataflow(d)
        self.assertEqual(len([s for s in out["sites"] if s["kind"] == "for_each"]), 2)

    def test_foreach_alias_shadowing_rejected(self):
        d = source()
        d["shared_objects"]["inner-object"] = {
            "capability": "unix.file",
            "for_each": {"item": "user", "in": "files-object"},
            "select": {"directory": {"from": "user.home_dir"}}}
        with self.assertRaisesRegex(ValueError, "shadows inherited"):
            index_assessment_dataflow(d)

    def test_flat_040_foreach_projection_preserves_dependency_graph(self):
        old = index_assessment_dataflow(source())
        d = source()
        obj = d["shared_objects"]["files-object"]
        obj.update(obj.pop("select"))
        current = index_assessment_dataflow(d)
        self.assertEqual(current["edges"], old["edges"])
        self.assertEqual(current["dependency_first_source_order"],
                         old["dependency_first_source_order"])
        projections = [s for s in current["sites"] if s["kind"] == "projection"]
        self.assertEqual(len(projections), 1)
        self.assertEqual(projections[0]["path"],
                         ["shared_objects", "files-object", "directory", "from"])

    def test_flat_040_foreach_rejects_bad_alias_and_shadowing(self):
        d = source()
        obj = d["shared_objects"]["files-object"]
        obj.update(obj.pop("select"))
        obj["directory"]["from"] = "other.home_dir"
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            index_assessment_dataflow(d)
        obj["directory"]["from"] = "user.home_dir"
        d["shared_objects"]["inner-object"] = {
            "capability": "unix.file",
            "for_each": {"item": "user", "in": "files-object"},
            "directory": {"from": "user.home_dir"},
        }
        with self.assertRaisesRegex(ValueError, "shadows inherited"):
            index_assessment_dataflow(d)

    def test_mixed_flat_and_wrapped_projection_rejected(self):
        d = source()
        d["shared_objects"]["files-object"]["name"] = {"from": "user.username"}
        with self.assertRaisesRegex(ValueError, "conflicting wrapped and flat"):
            index_assessment_dataflow(d)

    def test_foreach_projection_requires_current_alias(self):
        d = source()
        d["shared_objects"]["inner-object"] = {
            "capability": "unix.file",
            "for_each": {"item": "file", "in": "files-object"},
            "select": {"directory": {"from": "user.home_dir"}}}
        with self.assertRaisesRegex(ValueError, "must project from current alias"):
            index_assessment_dataflow(d)

    def test_foreach_projection_out_of_scope_rejected(self):
        d = source()
        d["shared_objects"]["files-object"]["select"]["directory"]["from"] = "other.home_dir"
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            index_assessment_dataflow(d)

    def test_source_order_independent_of_definition_order(self):
        d = source()
        a = index_assessment_dataflow(d)
        d["variables"] = dict(reversed(list(d["variables"].items())))
        d["shared_objects"] = dict(reversed(list(d["shared_objects"].items())))
        self.assertEqual(a, index_assessment_dataflow(d))


if __name__ == "__main__":
    unittest.main()
