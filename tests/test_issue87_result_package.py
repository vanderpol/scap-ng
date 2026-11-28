"""Local checks of the canonical unsigned Result package fixture."""
from collections import Counter
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json
import unittest

from jsonschema import FormatChecker

from conformance.tools.runner import CONFORMANCE, load, schema_validator

FIXTURE = CONFORMANCE / "result-package"


def fixture_link_errors(manifest, payloads):
    """Check exact member bytes and the fixture's declared invocation links."""
    members = {}
    for row in manifest["members"]:
        raw = payloads[row["path"]]
        if sha256(raw).hexdigest() != row["sha256"] or len(raw) != row["size"]:
            return {"member_digest_mismatch"}
        members[row["id"]] = json.loads(raw)[row["kind"]]

    scan = members[manifest["scan_result_ref"]]
    target_ids = {target["id"] for target in scan["targets"]}
    errors = set()
    for group in manifest["evaluation_groups"]:
        for execution in group["execution_ids"]:
            if execution not in members:
                errors.add("unresolved_execution")
                continue
            if members[execution]["target_ref"] != group["target_ref"]:
                errors.add("cross_target_invocation")

    for index in scan["benchmark_results"]:
        benchmark = members[index["benchmark_result_ref"]]
        target = index["target_ref"]
        if target not in target_ids or benchmark["target_ref"] != target:
            errors.add("cross_target_invocation")
        for rule in benchmark["rule_results"]:
            for instance in rule["instances"]:
                execution = instance["assessment_result_ref"]
                if execution is None:
                    continue
                if execution not in scan["assessment_result_refs"] or execution not in members:
                    errors.add("unresolved_execution")
                elif members[execution]["target_ref"] != target:
                    errors.add("cross_target_invocation")
    return errors


class ResultPackageCases(unittest.TestCase):
    def setUp(self):
        self.manifest = load(FIXTURE / "manifest.json")
        self.expected = load(FIXTURE / "expected.json")
        self.payloads = {
            path.relative_to(FIXTURE).as_posix(): path.read_bytes()
            for path in (FIXTURE / "members").glob("*.json")
        }

    def test_source_and_result_documents_follow_pinned_contracts(self):
        corpus_pin = load(CONFORMANCE / "manifest.json")["schema_commit"]
        self.assertEqual(corpus_pin, self.expected["schema_pin"])
        schema_validator("result-package-manifest.schema.json").validate(self.manifest)
        rows = self.manifest["members"]
        self.assertEqual(len(rows), self.expected["members"])
        self.assertEqual({row["path"] for row in rows}, self.payloads.keys())
        self.assertEqual(len({row["id"] for row in rows}), len(rows))
        self.assertEqual(fixture_link_errors(self.manifest, self.payloads), set())
        members = {}
        for row in rows:
            doc = json.loads(self.payloads[row["path"]])
            schema = schema_validator(row["kind"].replace("_", "-") + ".schema.json")
            schema.evolve(format_checker=FormatChecker()).validate(doc)
            members[row["id"]] = doc[row["kind"]]

        assessment = load(FIXTURE / self.expected["authored_assessment"])["assessment"]
        fallback = load(FIXTURE / self.expected["expected_assessment"])["variants"]["fallback"]
        oracle = self.expected["expectations"]
        scan = members[self.manifest["scan_result_ref"]]
        self.assertEqual(scan["run_id"], self.manifest["run_id"])
        self.assertEqual(scan["signature_status"], self.manifest["signature_status"])
        self.assertEqual({row["id"] for row in scan["targets"]}, self.expected["targets"].keys())
        for target, ids in self.expected["targets"].items():
            benchmark = members[ids["benchmark"]]
            result = members[ids["invocation"]]
            self.assertEqual(benchmark["target_ref"], target)
            self.assertEqual(benchmark["run_id"], scan["run_id"])
            timeline = (scan["started_at"], benchmark["started_at"],
                        benchmark["completed_at"], scan["completed_at"])
            samples = list(map(datetime.fromisoformat, timeline))
            self.assertEqual(samples, sorted(samples))
            self.assertEqual(benchmark["effective_policy"]["selected_rules"], [oracle["selected_rule"]])
            self.assertEqual(benchmark["effective_policy"]["disabled_rules"], [oracle["disabled_rule"]])
            self.assertEqual(result["assessment"], {"id": assessment["id"], "version": assessment["version"]})
            self.assertEqual(result["outcome"], fallback["assessment_outcome"])
            self.assertEqual(result["outcome"], oracle["technical_outcome"])
            self.assertEqual(result["expression_execution"]["invocation_ref"], ids["invocation"])
            self.assertEqual(result["expression_execution"]["executed_tests"], oracle["executed_tests"])
            trace, = result["expression_execution"]["trace"]
            self.assertEqual(trace["reason"], assessment["evaluate"]["else"]["not_evaluated"]["reason"])
            self.assertEqual(result["tests"], [])
            self.assertEqual(result["objects"], [])
            rules = {rule["rule_id"]: rule for rule in benchmark["rule_results"]}
            self.assertEqual(rules[oracle["selected_rule"]]["instances"][0]["assessment_result_ref"],
                             ids["invocation"])
            self.assertIsNone(rules[oracle["disabled_rule"]]["instances"][0]["assessment_result_ref"])
            self.assertEqual(benchmark["summary"]["total"], oracle["rule_count"])
            counts = Counter(rule["outcome"] for rule in rules.values())
            self.assertEqual(sum(counts.values()), benchmark["summary"]["total"])
            for outcome in ("pass", "fail", "not_applicable", "not_evaluated", "error", "unknown"):
                self.assertEqual(benchmark["summary"][outcome], counts[outcome])

    def test_byte_changes_and_link_failures_are_distinct(self):
        variants = self.expected["negative_variants"]
        path = "members/benchmark-a.json"

        # JSON meaning survives whitespace, while exact package bytes change.
        tampered = self.payloads | {path: self.payloads[path] + b" "}
        self.assertEqual(json.loads(tampered[path]), json.loads(self.payloads[path]))
        self.assertEqual(fixture_link_errors(self.manifest, tampered), {variants["changed_member_bytes"]})

        # An internally valid digest cannot excuse a cross-target reference.
        doc = json.loads(self.payloads[path])
        doc["benchmark_result"]["rule_results"][0]["instances"][0]["assessment_result_ref"] = "invocation-b"
        schema_validator("benchmark-result.schema.json").validate(doc)
        raw = json.dumps(doc).encode()
        relinked = deepcopy(self.manifest)
        row = next(row for row in relinked["members"] if row["path"] == path)
        row.update(sha256=sha256(raw).hexdigest(), size=len(raw))
        self.assertEqual(
            fixture_link_errors(relinked, self.payloads | {path: raw}),
            {variants["cross_target_rule_reference"]},
        )

        dangling = deepcopy(self.manifest)
        dangling["evaluation_groups"][0]["execution_ids"].append("missing-invocation")
        schema_validator("result-package-manifest.schema.json").validate(dangling)
        self.assertEqual(fixture_link_errors(dangling, self.payloads), {variants["unknown_execution_in_group"]})

    def test_result_redaction_retention_and_format_invalidity(self):
        schema = schema_validator("assessment-result.schema.json")
        doc = json.loads(self.payloads["members/invocation-a.json"])
        doc["assessment_result"]["input_bindings"] = [
            {"input": "primary-input", "source": "organizational_input", "redacted": True},
        ]
        schema.validate(doc)
        doc["assessment_result"]["input_bindings"][0]["value"] = "fixture-value"
        self.assertFalse(schema.is_valid(doc))

        doc = json.loads(self.payloads["members/invocation-a.json"])
        retention = doc["assessment_result"]["evidence_retention"]
        retention["source"] = "operator_override"
        self.assertFalse(schema.is_valid(doc))
        retention["override_reason"] = "Fixture reporting limit"
        schema.validate(doc)

        benchmark = json.loads(self.payloads["members/benchmark-a.json"])
        assertions = benchmark["benchmark_result"]["effective_policy"]["organizational_inputs"]
        assertions["test-assertion"] = {
            "parameter": "approved-route", "source": "organizational_input",
            "provenance": {}, "redacted": True,
        }
        benchmark_schema = schema_validator("benchmark-result.schema.json")
        benchmark_schema.validate(benchmark)
        assertions["test-assertion"]["value"] = "fixture-value"
        self.assertFalse(benchmark_schema.is_valid(benchmark))
        assertions["test-assertion"]["redacted"] = False
        benchmark_schema.validate(benchmark)

        manifest = self.manifest | {"signature_status": "signed"}
        self.assertFalse(schema_validator("result-package-manifest.schema.json").is_valid(manifest))

    def test_conditional_trace_keeps_guard_outcome_separate_from_body(self):
        cases = load(FIXTURE / "guard-trace.json")["cases"]
        self.assertEqual(
            {case["condition_outcome"] for case in cases},
            {"true", "false", "error", "unknown", "not_evaluated", "not_applicable"},
        )
        schema = schema_validator("expression-invocation.schema.json")
        for case in cases:
            with self.subTest(guard=case["condition_outcome"]):
                doc = {
                    "assessment": "trace-fixture",
                    "invocation_ref": "guard-invocation",
                    "outcome": case["outcome"],
                    "executed_tests": [],
                    "trace": [{
                        "path": "/evaluate",
                        "kind": "conditional",
                        "owner_invocation_ref": "guard-invocation",
                        "branch_index": 0,
                        **case,
                    }],
                    "diagnostics": [],
                }
                schema.validate(doc)
                changed = deepcopy(doc)
                trace = changed["trace"][0]
                trace["selected_branch"] = "else" if case["selected_branch"] == "then" else "then"
                self.assertFalse(schema.is_valid(changed))
                if case["selected_branch"] is None:
                    trace["selected_branch"] = None
                    trace["outcome"] = "true"
                    self.assertFalse(schema.is_valid(changed))
