#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema


ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/"schema/v0.1.0/benchmark-result.schema.json").read_text())


def base_result():
    return {
        "benchmark_result": {
            "result_schema_version": "0.1.0",
            "run_id": "run-1",
            "started_at": "2026-10-01T22:00:00Z",
            "completed_at": "2026-10-01T22:00:01Z",
            "scanner": {"capabilities": {"organizational_input": True}},
            "target": {"identifiers": []},
            "benchmark": {"id": "example", "version": "1"},
            "effective_policy": {
                "profile": None,
                "tailoring": None,
                "selected_rules": ["rule-1"],
                "disabled_rules": [],
                "check_selectors": {},
                "parameters": {},
                "organizational_inputs": {},
            },
            "summary": {
                "total": 1,
                "pass": 1,
                "fail": 0,
                "not_applicable": 0,
                "not_evaluated": 0,
                "error": 0,
                "unknown": 0,
            },
            "rule_results": [{
                "rule_id": "rule-1",
                "outcome": "pass",
                "assessment": {"id": "assessment-1"},
                "message": "compliant",
                "expected_state": [],
                "instances": [{
                    "id": "instance-1",
                    "outcome": "pass",
                    "assessment_result_ref": "assessment-results/instance-1.json",
                    "assessment_invocation_id": "invocation-1",
                }],
            }],
        }
    }


class BenchmarkResultInstanceTests(unittest.TestCase):
    def test_single_invocation_uses_one_instance(self):
        jsonschema.validate(base_result(), SCHEMA)

    def test_fanout_uses_multiple_instances_under_one_rule(self):
        doc=base_result()
        rr=doc["benchmark_result"]["rule_results"][0]
        rr["outcome"]="fail"
        rr["instances"].append({
            "id":"instance-2",
            "outcome":"fail",
            "assessment_result_ref":"assessment-results/instance-2.json",
            "assessment_invocation_id":"invocation-2",
            "target_instance":"account:example",
        })
        jsonschema.validate(doc, SCHEMA)

    def test_empty_instances_is_invalid(self):
        doc=base_result()
        doc["benchmark_result"]["rule_results"][0]["instances"]=[]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(doc, SCHEMA)

    def test_old_top_level_assessment_result_ref_does_not_replace_instances(self):
        doc=base_result()
        rr=doc["benchmark_result"]["rule_results"][0]
        rr.pop("instances")
        rr["assessment_result_ref"]="legacy-direct-ref"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(doc, SCHEMA)


if __name__=="__main__":
    unittest.main()
