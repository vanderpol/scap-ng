#!/usr/bin/env python3
"""ESX schema/graph and synthetic known-result evidence, not a live collector."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import yaml
from jsonschema import Draft202012Validator, ValidationError
from capability_registry import ROOT, load_mapping, mappings, mapping_path, draft_capabilities
from generate_capability_schema import generate
from assessment_results_v02 import item_validator
from reported_elements import generate_reporting_capability, project_items
from validate_native_json_schemas import build_validators, document_errors
from validate_generated_capability_semantics import validate_assessment_capability_semantics
from scap_ng_content_compiler import validate_draft_expression_assessments, compile_benchmark, write_bundle, verify_bundle
from oval_result_truth_tables import evaluate_collected_object_test, aggregate_check

SUITE = ROOT / "tests/esx-host-0.2.0"


class EsxHostCapabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {kind: yaml.safe_load((SUITE / "content" / (kind + ".assessment.yaml")).read_text())
                         for kind in ["service", "advancedsetting"]}
        cls.validators = build_validators(ROOT / "schema/v0.2.0")
        cls.oracle = json.loads((SUITE / "expected-results/cases.json").read_text())

    def errors(self, doc):
        return list(document_errors(self.validators["assessment.schema.json"], doc))

    def item(self, kind):
        return json.loads((SUITE / (kind + "-item.json")).read_text())

    def test_versioned_registration_does_not_expand_stable_catalog(self):
        self.assertEqual(len(mappings("0.1.0")), 100)
        self.assertEqual(len(mappings("0.2.0")), 100 + len(draft_capabilities()))
        for kind in self.documents:
            cap = "esx.host_" + kind
            with self.assertRaises(ValueError):
                load_mapping(cap, "0.1.0")
            schema = generate(load_mapping(cap), ROOT)
            self.assertIn("/v0.2.0/", schema["$id"])
            Draft202012Validator.check_schema(schema)
            Draft202012Validator.check_schema(generate_reporting_capability(load_mapping(cap)))
        for cap in ["../unix.file", "esx/host_service", "", None]:
            with self.assertRaises(ValueError):
                mapping_path(cap)

    def test_registry_rejects_shadowing_and_mapping_identity_mismatch(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            stable = root / "schema/v0.2.0/capability-mappings/supported"
            experimental = root / "schema/v0.2.0/capability-mappings/experimental"
            stable.mkdir(parents=True)
            experimental.mkdir(parents=True)
            (stable / "esx.host_service.json").write_text('{}')
            (experimental / "esx.host_service.json").write_text('{}')
            with self.assertRaises(ValueError):
                mapping_path("esx.host_service", root=root)
            (stable / "esx.host_service.json").unlink()
            with self.assertRaises(ValueError):
                load_mapping("esx.host_service", root=root)

    def test_standalone_content_and_compiler_preflight(self):
        for doc in self.documents.values():
            self.assertFalse(self.errors(doc))
            self.assertFalse(validate_assessment_capability_semantics(doc))
            a = doc["assessment"]
            validate_draft_expression_assessments({a["id"]: a})

    def test_node_contracts_reject_malformed_unexecuted_test(self):
        doc = copy.deepcopy(self.documents["service"])
        a = doc["assessment"]
        a["tests"]["test-unused"] = copy.deepcopy(a["tests"]["test-check"])
        a["tests"]["test-unused"]["reported_elements"] = ["invented"]
        errors = self.errors(doc)
        self.assertTrue(errors)
        self.assertTrue(any(list(e.absolute_path)[:3] == ["assessment", "tests", "test-unused"] for e in errors))
        with self.assertRaises(ValueError):
            validate_draft_expression_assessments({a["id"]: a})

    def test_real_compilation_retains_both_draft_capabilities(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bench = root / "benchmark"
            def dump(path, data):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
            dump(bench / "benchmark.yaml", {"benchmark": {"id": "esx.fixture.benchmark",
                 "version": {"value": "1"}, "rules": ["service", "advancedsetting"], "profiles": []}})
            for kind, doc in self.documents.items():
                dump(bench / "assessments" / (kind + ".assessment.yaml"), doc)
                dump(bench / "rules" / (kind + ".rule.yaml"), {"rule": {"id": kind,
                     "assessment_choices": {"automated": {"assessment": "../assessments/" + kind + ".assessment.yaml"}},
                     "default_assessment_choice": "automated"}})
            benchmark, members, index = compile_benchmark(root, bench)
            packaged = {json.loads(members[row["path"]])["assessment"]["tests"]["test-check"]["capability"]
                        for row in index.values() if row["type"] == "assessment"}
            self.assertEqual(packaged, {"esx.host_service", "esx.host_advancedsetting"})
            package = root / "esx.scapng"
            write_bundle(package, benchmark, members, index, sign_self_signed=False, provenance={})
            self.assertEqual(verify_bundle(package)["benchmark_id"], "esx.fixture.benchmark")

    def test_new_capability_requires_v02_even_without_reporting(self):
        doc = copy.deepcopy(self.documents["service"])
        a = doc["assessment"]
        a["tests"]["test-check"].pop("reported_elements")
        a["specification"]["version"] = "0.1.0"
        self.assertTrue(any("requires specification 0.2.0" in e.message for e in self.errors(doc)))
        with self.assertRaises(ValueError):
            validate_draft_expression_assessments({a["id"]: a})

    def test_selector_and_state_shapes(self):
        for mutation in ["missing-selector", "null-selector", "invented-field", "wrong-boolean-type", "fake-variable-source"]:
            doc = copy.deepcopy(self.documents["service"])
            a = doc["assessment"]
            if mutation == "missing-selector":
                a["objects"]["selected"]["select"] = {}
            elif mutation == "null-selector":
                a["objects"]["selected"]["select"]["service_name"] = None
            elif mutation == "invented-field":
                a["states"]["expected"]["state"]["field"] = "invented"
            elif mutation == "wrong-boolean-type":
                a["states"]["expected"]["state"]["datatype"] = "string"
            else:
                a["tests"]["test-check"].pop("object")
                a["tests"]["test-check"]["variable"] = "imaginary"
            with self.subTest(mutation=mutation):
                self.assertTrue(self.errors(doc))

    def test_cross_capability_references_are_rejected(self):
        doc = copy.deepcopy(self.documents["service"])
        doc["assessment"]["objects"]["selected"] = copy.deepcopy(self.documents["advancedsetting"]["assessment"]["objects"]["selected"])
        codes = {e["code"] for e in validate_assessment_capability_semantics(doc)}
        self.assertIn("test.object_capability", codes)
        a = doc["assessment"]
        with self.assertRaises(ValueError):
            validate_draft_expression_assessments({a["id"]: a})
        doc["assessment"]["states"]["expected"] = copy.deepcopy(self.documents["advancedsetting"]["assessment"]["states"]["expected"])
        codes = {e["code"] for e in validate_assessment_capability_semantics(doc)}
        self.assertIn("test.state_capability", codes)
        with self.assertRaises(ValueError):
            validate_draft_expression_assessments({a["id"]: a})

    def test_typed_items_preserve_multiplicity_and_status(self):
        for kind in self.documents:
            item = self.item(kind)
            v = item_validator(item["capability"])
            v.validate(item)
            for status in ["does_not_exist", "error", "not_collected"]:
                changed = copy.deepcopy(item)
                field = "service_running" if kind == "service" else "advanced_setting_value"
                value = {"datatype": "boolean" if kind == "service" else "integer", "status": status}
                changed["fields"][field] = value if kind == "service" else [value]
                v.validate(changed)
            bad = copy.deepcopy(item)
            bad["fields"]["invented"] = {"datatype": "string", "value": "x"}
            with self.assertRaises(ValidationError):
                v.validate(bad)
        item = self.item("advancedsetting")
        item["fields"]["advanced_setting_value"].append({"datatype": "integer", "value": 300, "status": "exists"})
        item_validator(item["capability"]).validate(item)
        item["fields"]["advanced_setting_value"] = {"datatype": "integer", "value": 600, "status": "exists"}
        with self.assertRaises(ValidationError):
            item_validator(item["capability"]).validate(item)

    def test_synthetic_scalar_oracle_and_collection_statuses(self):
        for case in self.oracle["comparisons"]:
            state = self.documents[case["content"]]["assessment"]["states"]["expected"]["state"]
            self.assertEqual(state["value"], case["expected"])
            actual = "true" if case["observed"] == case["expected"] else "false"
            self.assertEqual(actual, case["outcome"])
        # This demonstrates why two observed setting values must not collapse.
        self.assertEqual(aggregate_check("all", ["true", "false"]), "false")
        for case in self.oracle["collection_statuses"]:
            outcome = evaluate_collected_object_test(case["flag"].replace("_", " "),
                                                    existence="at_least_one_exists", has_state=False)
            self.assertEqual(outcome.replace(" ", "_"), case["outcome"])

    def test_reporting_uses_new_fields_and_preserves_redaction(self):
        for kind, names in self.oracle["report_fields"].items():
            a = self.documents[kind]["assessment"]
            item = self.item(kind)
            report = project_items(a, [item], [{"test_ref": "test-check", "item_ref": item["id"],
                                  "used_elements": names, "required_elements": [names[0]]}],
                                  source_execution_ref="fixture-execution", source_completeness={
                                      "logical_complete": True, "population_complete": True, "evidence_complete": True})
            self.assertEqual(sorted(report["item_report"]["items"][0]["item"]["fields"]), sorted(names))
        a = copy.deepcopy(self.documents["advancedsetting"]["assessment"])
        a["tests"]["test-check"]["reported_elements"] = ["advanced_setting_value"]
        item = self.item("advancedsetting")
        item["fields"]["advanced_setting_value"] = [{"datatype": "integer", "redacted": True}]
        report = project_items(a, [item], [{"test_ref": "test-check", "item_ref": item["id"],
                               "used_elements": ["advanced_setting_value"], "required_elements": ["advanced_setting_name"]}],
                               source_execution_ref="fixture-execution", source_completeness={
                                   "logical_complete": True, "population_complete": True, "evidence_complete": True})
        value = report["item_report"]["items"][0]["item"]["fields"]["advanced_setting_value"][0]
        self.assertTrue(value["redacted"])
        self.assertNotIn("value", value)

    def test_new_annotations_retain_field_meanings(self):
        for cap in ["esx.host_service", "esx.host_advancedsetting"]:
            mapping = load_mapping(cap)
            fields = generate(mapping, ROOT)["$defs"]["collected_item"]["allOf"][1]["properties"]["fields"]["properties"]
            for name, description in mapping["native"]["field_documentation"].items():
                self.assertEqual(fields[name]["description"], description)

    def test_pinned_source_bytes_and_original_licenses(self):
        pins = json.loads((ROOT / "third_party/oval-6.0-new-tests/source-pins.json").read_text())
        self.assertEqual(pins["commit"], "5afcf590fb5d334687bfdc47f98716424cdb7f3d")
        for row in pins["files"]:
            path = "third_party/oval-6.0-new-tests/" + row["path"]
            data = subprocess.check_output(["git", "show", "HEAD:" + path], cwd=ROOT)
            self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])
            self.assertIn(b"<terms_of_use>", data)


if __name__ == "__main__":
    unittest.main()
