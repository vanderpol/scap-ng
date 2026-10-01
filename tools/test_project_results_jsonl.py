#!/usr/bin/env python3
import json
from pathlib import Path
import sys
import unittest

from lxml import etree

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


    def test_compact_rule_context_is_projected(self):
        scan=scan_doc()
        benchmark=benchmark_doc()
        rule=benchmark["benchmark_result"]["rule_results"][0]
        rule.update({
            "weight": 1.5,
            "check_selector": "automated",
            "parameters": {"example_parameter": 42},
            "applicability": {"outcome": "applicable", "conditions": []},
        })
        event=project_scan(scan, {"benchmark-results/example.json": benchmark})[1]
        self.assertEqual(1.5, event["weight"])
        self.assertEqual("automated", event["check_selector"])
        self.assertEqual({"example_parameter": 42}, event["parameters"])
        self.assertEqual("applicable", event["applicability"]["outcome"])
        rule["observed_state"]=[{
            "item_ref":"item-1",
            "state_slot":"mode",
            "datatype":"string",
            "value":"0666",
            "status":"exists",
        }]
        event=project_scan(scan, {"benchmark-results/example.json": benchmark})[1]
        self.assertEqual("0666", event["observed_state"][0]["value"])

    def test_non_boolean_rule_outcomes_are_preserved(self):
        for outcome in ("error", "unknown", "not_evaluated", "not_applicable"):
            with self.subTest(outcome=outcome):
                scan=scan_doc()
                benchmark=benchmark_doc()
                rule=benchmark["benchmark_result"]["rule_results"][0]
                rule["outcome"]=outcome
                rule["instances"][0]["outcome"]=outcome
                event=project_scan(
                    scan,
                    {"benchmark-results/example.json": benchmark},
                )[1]
                self.assertEqual(outcome, event["outcome"])
                self.assertEqual(outcome, event["instances"][0]["outcome"])


    def test_bounded_evidence_and_early_stop_are_preserved(self):
        scan=scan_doc()
        benchmark=benchmark_doc()
        rule=benchmark["benchmark_result"]["rule_results"][0]
        rule["evidence_summary"]={
            "observed_failures":20,
            "actual_failures":"unknown",
            "maximum":20,
            "returned":2,
            "truncated_population":True,
            "stop_reason":"evidence_maximum_reached",
        }
        event=project_scan(scan, {"benchmark-results/example.json": benchmark})[1]
        summary=event["evidence_summary"]
        self.assertEqual(20, summary["observed_failures"])
        self.assertEqual("unknown", summary["actual_failures"])
        self.assertTrue(summary["truncated_population"])
        self.assertEqual("evidence_maximum_reached", summary["stop_reason"])

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


    def test_checked_in_projection_matches_exact_jsonl(self):
        fixture=ROOT/"research/iterations/003/results/issue21"
        scan=json.loads((fixture/"scan-result.json").read_text())
        benchmark=json.loads((fixture/"benchmark-result.json").read_text())
        events=project_scan(scan, {"benchmark-result.json": benchmark})
        actual="\n".join(jsonl_lines(events))+"\n"
        expected=(fixture/"expected.jsonl").read_text()
        self.assertEqual(expected, actual)


    def test_matched_scap14_arf_is_schema_valid(self):
        fixture=ROOT/"research/iterations/003/results/issue21"
        schema_path=ROOT/"third_party/scap-1.4-schemas/asset-reporting-format_1.1.0.xsd"
        schema=etree.XMLSchema(etree.parse(str(schema_path)))
        doc=etree.parse(str(fixture/"matched-scap14.arf.xml"))
        schema.assertValid(doc)

        ns={
            "arf":"http://scap.nist.gov/schema/asset-reporting-format/1.1",
            "xccdf":"http://checklists.nist.gov/xccdf/1.2",
        }
        rules=doc.xpath("//xccdf:rule-result", namespaces=ns)
        self.assertEqual(1, len(rules))
        self.assertEqual("rule-file-mode", rules[0].get("idref"))
        self.assertEqual("fail", rules[0].find("xccdf:result", ns).text)

    def test_size_comparison_inputs_exist(self):
        fixture=ROOT/"research/iterations/003/results/issue21"
        paths=[
            fixture/"matched-scap14.arf.xml",
            fixture/"matched-scap14-detailed.arf.xml",
            fixture/"scan-result.json",
            fixture/"benchmark-result.json",
            fixture/"expected.jsonl",
            ROOT/"research/iterations/003/results/issue40/rhel9-file-mode-fail.result.json",
        ]
        for path in paths:
            with self.subTest(path=path.name):
                self.assertGreater(path.stat().st_size, 0)

    def test_matched_detailed_scap14_arf_and_oval_are_schema_valid(self):
        fixture=ROOT/"research/iterations/003/results/issue21"
        schema_dir=ROOT/"third_party/scap-1.4-schemas"
        arf_path=fixture/"matched-scap14-detailed.arf.xml"
        doc=etree.parse(str(arf_path))

        arf_schema=etree.XMLSchema(etree.parse(str(schema_dir/"asset-reporting-format_1.1.0.xsd")))
        arf_schema.assertValid(doc)

        oval_schema_dir=schema_dir/"oval_5.12.3"
        wrapper=f"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
          <xs:import namespace="http://oval.mitre.org/XMLSchema/oval-results-5"
                     schemaLocation="oval-results-schema.xsd"/>
          <xs:import namespace="http://oval.mitre.org/XMLSchema/oval-system-characteristics-5#unix"
                     schemaLocation="unix-system-characteristics-schema.xsd"/>
          <xs:import namespace="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix"
                     schemaLocation="unix-definitions-schema.xsd"/>
        </xs:schema>"""
        wrapper_doc=etree.fromstring(
            wrapper.encode("utf-8"),
            base_url=(oval_schema_dir/"issue21-validation-wrapper.xsd").as_uri(),
        )
        oval_schema=etree.XMLSchema(etree.ElementTree(wrapper_doc))
        oval_nodes=doc.xpath(
            "//oval-res:oval_results",
            namespaces={"oval-res":"http://oval.mitre.org/XMLSchema/oval-results-5"},
        )
        self.assertEqual(1, len(oval_nodes))
        oval_schema.assertValid(etree.ElementTree(oval_nodes[0]))

        ns={
            "oval-res":"http://oval.mitre.org/XMLSchema/oval-results-5",
            "oval-sc":"http://oval.mitre.org/XMLSchema/oval-system-characteristics-5",
            "unix-sc":"http://oval.mitre.org/XMLSchema/oval-system-characteristics-5#unix",
            "unix-def":"http://oval.mitre.org/XMLSchema/oval-definitions-5#unix",
        }
        self.assertEqual(
            "false",
            oval_nodes[0].xpath("string(.//oval-res:test/@result)", namespaces=ns),
        )
        self.assertEqual(
            "complete",
            oval_nodes[0].xpath("string(.//oval-sc:object/@flag)", namespaces=ns),
        )
        self.assertEqual(
            "0",
            oval_nodes[0].xpath("string(.//unix-sc:file_item/unix-sc:user_id)", namespaces=ns),
        )
        expected_permissions={
            "uread":"true","uwrite":"true","uexec":"false",
            "gread":"true","gwrite":"true","gexec":"false",
            "oread":"true","owrite":"true","oexec":"false",
        }
        for name, expected in expected_permissions.items():
            with self.subTest(permission=name):
                actual=oval_nodes[0].xpath(
                    f"string(.//unix-sc:file_item/unix-sc:{name})",
                    namespaces=ns,
                )
                self.assertEqual(expected, actual)

        required_permissions={
            "uread":"true","uwrite":"true","uexec":"false",
            "gread":"true","gwrite":"false","gexec":"false",
            "oread":"true","owrite":"false","oexec":"false",
        }
        for name, expected in required_permissions.items():
            with self.subTest(required_permission=name):
                actual=oval_nodes[0].xpath(
                    f"string(.//unix-def:file_state/unix-def:{name})",
                    namespaces=ns,
                )
                self.assertEqual(expected, actual)
        self.assertEqual(
            "0",
            oval_nodes[0].xpath(
                "string(.//unix-def:file_state/unix-def:user_id)",
                namespaces=ns,
            ),
        )


    def test_issue21_rule_message_matches_detailed_observation(self):
        fixture=ROOT/"research/iterations/003/results/issue21"
        benchmark=json.loads((fixture/"benchmark-result.json").read_text())
        assessment=json.loads(
            (ROOT/"research/iterations/003/results/issue40/rhel9-file-mode-fail.result.json").read_text()
        )
        rule=benchmark["benchmark_result"]["rule_results"][0]
        observed=assessment["assessment_result"]["items"][0]["fields"]["mode"]["value"]
        expected=rule["expected_state"][0]["value"]
        compact_observed=rule["observed_state"][0]["value"]
        self.assertEqual("0666", observed)
        self.assertEqual(observed, compact_observed)
        self.assertEqual("0644", expected)
        self.assertIn(observed, rule["message"])
        self.assertIn(expected, rule["message"])
        self.assertNotEqual(observed, expected)


if __name__=="__main__":
    unittest.main()
