#!/usr/bin/env python3
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))

from project_results_jsonl import jsonl_lines, project_scan


def scan_doc():
    return {
        "scan_result": {
            "result_schema_version": "0.1.0",
            "run_id": "run-1",
            "started_at": "2026-10-01T22:00:00Z",
            "completed_at": "2026-10-01T22:01:00Z",
            "scanner": {"name": "scanner", "version": "1"},
            "targets": [{
                "id": "target-1",
                "identifiers": [{"scheme": "asset_uuid", "value": "asset-1"}],
                "hostname": "host.example",
                "addresses": ["192.0.2.1"],
            }],
            "benchmark_results": [{
                "benchmark_result_ref": "benchmark-results/example.json",
                "benchmark_id": "benchmark-1",
                "benchmark_version": "1",
                "target_ref": "target-1",
                "profile_id": "stig",
                "tailoring_id": None,
                "summary": {"total": 1, "pass": 0, "fail": 1},
            }],
            "assessment_result_refs": ["assessment-results/a1.json"],
            "signature_status": "verified",
        }
    }


def benchmark_doc():
    return {
        "benchmark_result": {
            "result_schema_version": "0.1.0",
            "run_id": "run-1",
            "started_at": "2026-10-01T22:00:00Z",
            "completed_at": "2026-10-01T22:01:00Z",
            "scanner": {
                "name": "scanner",
                "version": "1",
                "capabilities": {"organizational_input": True},
            },
            "target": {
                "identifiers": [{"scheme": "asset_uuid", "value": "asset-1"}],
                "hostname": "host.example",
                "addresses": ["192.0.2.1"],
            },
            "benchmark": {"id": "benchmark-1", "version": "1", "package_digest": "sha256:abc"},
            "effective_policy": {
                "profile": "stig",
                "tailoring": None,
                "selected_rules": ["rule-1"],
                "disabled_rules": [],
                "check_selectors": {"rule-1": "automated"},
                "parameters": {},
                "organizational_inputs": {},
            },
            "summary": {
                "total": 1,
                "pass": 0,
                "fail": 1,
                "not_applicable": 0,
                "not_evaluated": 0,
                "error": 0,
                "unknown": 0,
            },
            "rule_results": [{
                "rule_id": "rule-1",
                "title": "Example requirement",
                "severity": "high",
                "outcome": "fail",
                "assessment": {"id": "assessment-1"},
                "message": "Observed mode 0666; expected 0644.",
                "reason": {"code": "value_mismatch"},
                "expected_state": [{
                    "state_slot": "mode",
                    "datatype": "string",
                    "operation": "equals",
                    "value": "0644",
                    "source": "publisher",
                }],
                "instances": [{
                    "id": "instance-1",
                    "outcome": "fail",
                    "assessment_result_ref": "assessment-results/a1.json",
                    "assessment_invocation_id": "invocation-1",
                }],
                "evidence_refs": ["evidence-1"],
            }],
        }
    }


class ProjectionTests(unittest.TestCase):
    def test_summary_then_independent_rule_event(self):
        events=project_scan(
            scan_doc(),
            {"benchmark-results/example.json": benchmark_doc()},
        )
        self.assertEqual(2, len(events))
        self.assertEqual("scan_summary", events[0]["event_type"])
        rule=events[1]
        self.assertEqual("rule_result", rule["event_type"])
        self.assertEqual("run-1", rule["run_id"])
        self.assertEqual("target-1", rule["target_ref"])
        self.assertEqual("host.example", rule["target"]["hostname"])
        self.assertEqual("benchmark-1", rule["benchmark"]["id"])
        self.assertEqual("rule-1", rule["rule_id"])
        self.assertEqual("fail", rule["outcome"])
        self.assertEqual("assessment-results/a1.json", rule["instances"][0]["assessment_result_ref"])
        self.assertNotIn("tests", rule)
        self.assertNotIn("items", rule)

    def test_jsonl_is_deterministic(self):
        events=project_scan(
            scan_doc(),
            {"benchmark-results/example.json": benchmark_doc()},
        )
        first=jsonl_lines(events)
        second=jsonl_lines(events)
        self.assertEqual(first, second)
        for line in first:
            json.loads(line)

    def test_missing_benchmark_result_is_rejected(self):
        with self.assertRaises(KeyError):
            project_scan(scan_doc(), {})

    def test_run_mismatch_is_rejected(self):
        wrong=benchmark_doc()
        wrong["benchmark_result"]["run_id"]="run-other"
        with self.assertRaises(ValueError):
            project_scan(
                scan_doc(),
                {"benchmark-results/example.json": wrong},
            )

    def test_benchmark_identity_mismatch_is_rejected(self):
        wrong=benchmark_doc()
        wrong["benchmark_result"]["benchmark"]["id"]="different"
        with self.assertRaises(ValueError):
            project_scan(
                scan_doc(),
                {"benchmark-results/example.json": wrong},
            )


if __name__=="__main__":
    unittest.main()
