#!/usr/bin/env python3
import json
import copy
from pathlib import Path
import unittest

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v0.1.0"


def schema(name):
    return json.loads((SCHEMA_DIR / name).read_text())


def properties(name):
    return schema(name)["properties"]


class ResultSchemaScopeTests(unittest.TestCase):
    def test_rule_result_stays_policy_facing(self):
        props = properties("rule-result.schema.json")
        forbidden = {
            "organizational_inputs",
            "consumed_organizational_inputs",
            "expected_state",
            "observed_state",
            "evidence_summary",
            "tests",
            "objects",
            "items",
            "variables",
            "diagnostics",
            "scanner",
            "target",
        }
        self.assertTrue(forbidden.isdisjoint(props), forbidden & set(props))
        self.assertFalse(schema("rule-result.schema.json").get("additionalProperties", True))

    def test_benchmark_result_does_not_own_scan_identity_or_assessment_graph(self):
        root = properties("benchmark-result.schema.json")["benchmark_result"]
        props = root["properties"]
        forbidden = {
            "scanner",
            "target",
            "tests",
            "objects",
            "items",
            "variables",
            "diagnostics",
            "evidence_summary",
        }
        self.assertTrue(forbidden.isdisjoint(props), forbidden & set(props))
        self.assertIn("target_ref", props)
        self.assertIn("target_ref", root["required"])
        self.assertFalse(root.get("additionalProperties", True))

    def test_scan_result_is_index_not_policy_or_execution_container(self):
        root = properties("scan-result.schema.json")["scan_result"]
        props = root["properties"]
        forbidden = {
            "effective_policy",
            "rule_results",
            "tests",
            "objects",
            "items",
            "variables",
            "diagnostics",
            "evidence_summary",
        }
        self.assertTrue(forbidden.isdisjoint(props), forbidden & set(props))
        self.assertFalse(root.get("additionalProperties", True))

    def test_assessment_result_owns_execution_detail(self):
        root = properties("assessment-result.schema.json")["assessment_result"]
        props = root["properties"]
        expected = {
            "tests",
            "objects",
            "items",
            "variables",
            "diagnostics",
            "input_bindings",
            "consumed_organizational_inputs",
            "evidence_summary",
        }
        self.assertTrue(expected.issubset(props), expected - set(props))
        self.assertFalse(root.get("additionalProperties", True))
        self.assertNotIn("selected_branch", props)
        self.assertFalse(
            props["consumed_organizational_inputs"]["items"].get("additionalProperties", True)
        )
        self.assertFalse(
            props["input_bindings"]["items"].get("additionalProperties", True)
        )
        self.assertFalse(
            props["reason"]["oneOf"][2].get("additionalProperties", True)
        )

    def test_scan_index_records_are_closed(self):
        props = properties("scan-result.schema.json")["scan_result"]["properties"]
        self.assertFalse(props["targets"]["items"].get("additionalProperties", True))
        self.assertFalse(props["benchmark_results"]["items"].get("additionalProperties", True))

    def test_source_policy_records_with_complete_shapes_are_closed(self):
        benchmark = properties("benchmark.schema.json")["benchmark"]["properties"]
        self.assertFalse(benchmark["platform"].get("additionalProperties", True))
        org = properties("organizational-input.schema.json")["organizational_input"]["properties"]
        self.assertFalse(org["intended_scope"].get("additionalProperties", True))

    def test_rule_organizational_input_requiredness_is_explicit(self):
        rule = properties("rule.schema.json")["rule"]["properties"]
        item = rule["organizational_input_requirements"]["additionalProperties"]["items"]
        self.assertIn("required", item["required"])
        self.assertNotIn("default", item["properties"]["required"])

    def test_typed_values_are_closed(self):
        typed = schema("result-types.schema.json")["$defs"]["typed_value"]
        self.assertFalse(typed.get("additionalProperties", True))

    def test_authored_assessment_does_not_embed_runtime_results(self):
        assessment = properties("assessment.schema.json")["assessment"]["properties"]
        test_props = assessment["tests"]["additionalProperties"]["properties"]
        self.assertNotIn("result", test_props)

    def test_runtime_result_is_rejected_even_on_extensible_authored_nodes(self):
        document = {"assessment": {
            "id": "scope.example", "version": 1, "assessment_title": None,
            "mode": "automated", "class": "compliance", "purpose": "assessment",
            "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.1.0"},
            "objects": {"o": {"capability": "windows.wmi.query", "collect": {"query": "example"}}},
            "variables": {"v": {"kind": "constant", "value": "example"}},
            "states": {"s": {"capability": "windows.wmi.query", "state": {"field": "result"}}},
            "tests": {"t": {"test_title": None, "capability": "windows.wmi.query", "object": "o"}},
            "evaluate": {"test": "t"},
        }}
        validator = jsonschema.Draft202012Validator(schema("assessment.schema.json"))
        # A collected field named result is legitimate authored WMI data.
        validator.validate(document)
        for family in ("objects", "variables", "states", "tests"):
            for runtime_value in ("true", None, {"outcome": "false"}):
                with self.subTest(family=family, runtime_value=runtime_value):
                    leaked = copy.deepcopy(document)
                    node = next(iter(leaked["assessment"][family].values()))
                    node["result"] = runtime_value
                    with self.assertRaises(jsonschema.ValidationError):
                        validator.validate(leaked)

    def test_detailed_component_roots_are_closed(self):
        for name in (
            "test-result.schema.json",
            "collection-result.schema.json",
            "collected-item.schema.json",
            "state-result.schema.json",
            "entity-result.schema.json",
            "variable-result.schema.json",
        ):
            with self.subTest(schema=name):
                self.assertFalse(schema(name).get("additionalProperties", True))


if __name__ == "__main__":
    unittest.main()
