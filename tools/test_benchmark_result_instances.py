#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from jsonschema import RefResolver


ROOT=Path(__file__).resolve().parents[1]
SCHEMA_DIR=ROOT/"schema/v0.1.0"
SCHEMA=json.loads((SCHEMA_DIR/"benchmark-result.schema.json").read_text())
LOCAL_SCHEMAS={}
for path in SCHEMA_DIR.glob("*.schema.json"):
    doc=json.loads(path.read_text())
    LOCAL_SCHEMAS[path.name]=doc
    if doc.get("$id"):
        LOCAL_SCHEMAS[doc["$id"]]=doc
RESOLVER=RefResolver.from_schema(SCHEMA, store=LOCAL_SCHEMAS)
ASSESSMENT_SCHEMA=LOCAL_SCHEMAS["assessment-result.schema.json"]


def validate(doc, schema=SCHEMA):
    resolver=RefResolver.from_schema(schema, store=LOCAL_SCHEMAS)
    jsonschema.Draft202012Validator(schema, resolver=resolver).validate(doc)


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
        validate(base_result())

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
        validate(doc)

    def test_empty_instances_is_invalid(self):
        doc=base_result()
        doc["benchmark_result"]["rule_results"][0]["instances"]=[]
        with self.assertRaises(jsonschema.ValidationError):
            validate(doc)

    def test_old_top_level_assessment_result_ref_does_not_replace_instances(self):
        doc=base_result()
        rr=doc["benchmark_result"]["rule_results"][0]
        rr.pop("instances")
        rr["assessment_result_ref"]="legacy-direct-ref"
        with self.assertRaises(jsonschema.ValidationError):
            validate(doc)


def base_assessment_result():
    return {
        "assessment_result": {
            "result_schema_version": "0.1.0",
            "execution_id": "invocation-1",
            "assessment": {"id": "assessment-1", "version": 1},
            "purpose": "assessment",
            "class": "compliance",
            "outcome": "true",
            "logical_complete": True,
            "population_complete": True,
            "evidence_complete": True,
            "tests": [],
            "objects": [],
            "items": [],
            "variables": [],
            "diagnostics": [],
        }
    }


class AssessmentResultComponentTests(unittest.TestCase):
    def test_reusable_refs_resolve_offline(self):
        validate(base_assessment_result(), ASSESSMENT_SCHEMA)

    def test_informational_is_not_technical_truth(self):
        doc=base_assessment_result()
        doc["assessment_result"]["outcome"]="informational"
        with self.assertRaises(jsonschema.ValidationError):
            validate(doc, ASSESSMENT_SCHEMA)

    def test_collected_item_uses_reusable_schema(self):
        doc=base_assessment_result()
        doc["assessment_result"]["items"].append({
            "id":"item-1",
            "capability":"unix.file",
            "status":"exists",
            "fields":{
                "path":{"datatype":"string","value":"/etc/example"}
            },
            "provenance":{"object_ref":"object-1"},
        })
        validate(doc, ASSESSMENT_SCHEMA)


    def test_issue40_worked_result_fixtures_validate(self):
        fixture_dir=ROOT/"research/iterations/003/results/issue40"
        for path in sorted(fixture_dir.glob("*.result.json")):
            with self.subTest(path=path.name):
                validate(json.loads(path.read_text()), ASSESSMENT_SCHEMA)


if __name__=="__main__":
    unittest.main()
