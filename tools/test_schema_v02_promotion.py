#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from capability_registry import mappings
from generate_capability_schema import generate
from reported_elements import generate_reporting_capability
from validate_native_json_schemas import build_validators, diagnostic_value, document_errors

ROOT = Path(__file__).resolve().parents[1]
V02 = ROOT / "schema/v0.2.0"

REQUIRED_AUTHORING_SCHEMAS = {
    "applicability.schema.json",
    "assessment.schema.json",
    "benchmark.schema.json",
    "capability-common.schema.json",
    "manual-assessment.schema.json",
    "organizational-input.schema.json",
    "package-manifest.schema.json",
    "rule.schema.json",
    "tailoring.schema.json",
}

class Version020PromotionTests(unittest.TestCase):
    def test_authoring_surface_is_self_contained(self):
        self.assertEqual(
            sorted(name for name in REQUIRED_AUTHORING_SCHEMAS if not (V02 / name).is_file()),
            [],
        )
        for path in V02.glob("*.schema.json"):
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
            Draft202012Validator.check_schema(data)
            self.assertNotIn("https://scap-ng.dev/schema/v0.1.0/", text, path.name)
            self.assertEqual(data.get("x-scap-ng-version"), "0.2.0", path.name)
            self.assertRegex(data.get("x-last-modified", ""), r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", path.name)
            self.assertIn("/schema/v0.2.0/", data.get("$id", ""), path.name)

    def test_versioned_schema_metadata_is_complete(self):
        for path in sorted(V02.glob("*.schema.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data.get("x-scap-ng-version"), "0.2.0", path.name)
            self.assertRegex(data.get("x-last-modified", ""), r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", path.name)

        mapping_paths = sorted((V02 / "capability-mappings" / "supported").glob("*.json"))
        mapping_paths += sorted((V02 / "capability-mappings" / "experimental").glob("*.json"))
        self.assertGreaterEqual(len(mapping_paths), 104)
        for path in mapping_paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data.get("specification_version"), "0.2.0", path.name)
            self.assertRegex(data.get("last_modified", ""), r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", path.name)

        for name in ("capability-scope.json", "result-field-extensions.json"):
            data = json.loads((V02 / name).read_text(encoding="utf-8"))
            self.assertEqual(data.get("specification_version"), "0.2.0", name)
            self.assertRegex(data.get("last_modified", ""), r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", name)

    def test_all_supported_capabilities_generate_from_020(self):
        inherited = mappings("0.2.0")
        self.assertGreaterEqual(len(inherited), 100)
        for mapping in inherited:
            with self.subTest(capability=mapping["capability"]):
                generated = generate(mapping, ROOT, schema_version="0.2.0")
                text = json.dumps(generated, sort_keys=True)
                self.assertIn("/schema/v0.2.0/", text)
                self.assertNotIn("/schema/v0.1.0/", text)
                overlay = generate_reporting_capability(mapping)
                overlay_text = json.dumps(overlay, sort_keys=True)
                self.assertIn("/schema/v0.2.0/", overlay_text)
                self.assertNotIn("/schema/v0.1.0/", overlay_text)
                self.assertIn("reported_elements", overlay["$defs"]["test"]["properties"])
                if mapping.get("native", {}).get("fixed_result") is None:
                    self.assertIn("check_existence", generated["$defs"]["test"]["required"])
                    self.assertIn("check", generated["$defs"]["test"]["required"])
                self.assertNotIn("existence", generated["$defs"]["test"]["properties"])
                self.assertNotIn("match", generated["$defs"]["test"]["properties"])

    def test_capability_scope_separates_supported_from_experimental(self):
        scope = json.loads((V02 / "capability-scope.json").read_text(encoding="utf-8"))
        experimental = set(scope["experimental"])
        supported = {m["capability"] for m in mappings("0.2.0") if m["capability"] not in experimental}
        self.assertEqual(len(supported), scope["supported"]["expected_count"])
        self.assertFalse(supported & experimental)
        actual_experimental = {
            p.stem for p in (V02 / "capability-mappings" / "experimental").glob("*.json")
            if p.name != "README.md"
        }
        self.assertEqual(actual_experimental, experimental)
        self.assertEqual({row.get("source_test") for row in scope["deferred"] if row.get("source_test")},
                         {"kubepsp_test", "kubectl_test"})

    def test_inherited_capability_is_deep_validated_under_020(self):
        import yaml
        validators = build_validators(V02)
        fixture = ROOT / "tests/reported-elements-0.2.0/ownership.assessment.yaml"
        valid = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        errors = list(document_errors(validators["assessment.schema.json"], valid))
        self.assertEqual(errors, [], [e.message for e in errors])

        invalid = json.loads(json.dumps(valid))
        first_object = next(iter(invalid["assessment"]["objects"].values()))
        first_object["select"]["invented"] = {
            "value": "x", "operation": "equal", "datatype": "string"
        }
        self.assertTrue(list(document_errors(validators["assessment.schema.json"], invalid)))


    def test_single_operand_difference_preserves_oval_set_semantics(self):
        common = json.loads((V02 / "capability-common.schema.json").read_text(encoding="utf-8"))
        set_expression = common["$defs"]["set_expression"]
        self.assertEqual(set_expression["properties"]["operands"]["minItems"], 1)
        difference = set_expression["allOf"][0]["then"]["properties"]["operands"]
        self.assertEqual(difference.get("maxItems"), 2)
        self.assertNotIn("minItems", difference)

    def test_schema_diagnostics_are_json_safe(self):
        class Sentinel:
            def __str__(self):
                return "<unset>"

        payload = {
            "validator": diagnostic_value(Sentinel()),
            "nested": diagnostic_value([Sentinel()]),
        }
        self.assertEqual(
            json.loads(json.dumps(payload)),
            {"validator": "<unset>", "nested": ["<unset>"]},
        )

if __name__ == "__main__":
    unittest.main()
