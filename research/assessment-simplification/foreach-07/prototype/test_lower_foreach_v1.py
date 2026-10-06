#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "lower_foreach_v1", HERE / "lower_foreach_v1.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


class ForeachV1Prototype(unittest.TestCase):
    def test_simple_binding_lowers_to_faithful_graph(self):
        lowered = MOD.lower_foreach_v1(
            "initialization-files",
            {
                "for_each": {
                    "item": "user",
                    "in": "non-system-users",
                },
                "select": {
                    "directory": {
                        "from": "user.home_dir",
                    },
                    "name": {
                        "value": r"^\.[^\s\.]+",
                        "operation": "pattern_match",
                        "datatype": "string",
                    },
                },
            },
        )
        self.assertEqual(
            lowered["synthetic_variable"]["expression"],
            {
                "object_component": {
                    "object": "non-system-users",
                    "item_field": "home_dir",
                }
            },
        )
        path = lowered["target_object"]["select"]["directory"]
        self.assertEqual(path["var_check"], "at least one")
        self.assertEqual(path["operation"], "equals")
        self.assertEqual(path["datatype"], "source-compatible")
        self.assertEqual(
            lowered["aggregation_boundary"],
            "target_object_population",
        )
        self.assertEqual(lowered["collection_combination"], "union")

    def test_rejects_redundant_comparison_on_from(self):
        with self.assertRaises(MOD.ForeachV1Error):
            MOD.lower_foreach_v1(
                "files",
                {
                    "for_each": {"item": "user", "in": "users"},
                    "select": {
                        "directory": {
                            "from": "user.home_dir",
                            "operation": "equals",
                        }
                    },
                },
            )

    def test_rejects_wrong_binding_alias(self):
        with self.assertRaises(MOD.ForeachV1Error):
            MOD.lower_foreach_v1(
                "files",
                {
                    "for_each": {"item": "user", "in": "users"},
                    "select": {
                        "directory": {"from": "account.home_dir"},
                    },
                },
            )

    def test_v1_rejects_multiple_bound_selectors(self):
        with self.assertRaises(MOD.ForeachV1Error):
            MOD.lower_foreach_v1(
                "files",
                {
                    "for_each": {"item": "user", "in": "users"},
                    "select": {
                        "directory": {"from": "user.home_dir"},
                        "owner": {"from": "user.username"},
                    },
                },
            )


if __name__ == "__main__":
    unittest.main()
