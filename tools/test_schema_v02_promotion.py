#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from capability_registry import mappings
from generate_capability_schema import generate
from reported_elements import generate_reporting_capability
from validate_native_json_schemas import build_validators, document_errors

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

    def test_all_inherited_capabilities_generate_as_020(self):
        inherited = mappings("0.1.0")
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

    def test_inherited_capability_is_deep_validated_under_020(self):
        validators = build_validators(V02)
        valid = {
            "assessment": {
                "id": "promotion.unix.file",
                "version": 1,
                "assessment_title": "Promotion regression",
                "mode": "automated",
                "class": "compliance",
                "purpose": "assessment",
                "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.2.0"},
                "objects": {
                    "passwd": {
                        "object_title": "passwd",
                        "capability": "unix.file",
                        "select": {
                            "full_path": {"value": "/etc/passwd", "operation": "equal", "datatype": "string"}
                        }
                    }
                },
                "states": {
                    "owner": {
                        "state_title": "root owner",
                        "capability": "unix.file",
                        "state": {
                            "field": "user_id",
                            "value": 0,
                            "operation": "equal",
                            "datatype": "integer",
                            "match": "all",
                            "existence": "some"
                        }
                    }
                },
                "tests": {
                    "check": {
                        "test_title": "owner",
                        "capability": "unix.file",
                        "object": "passwd",
                        "states": ["owner"],
                        "existence": "some",
                        "match": "all",
                        "states_match": "all",
                        "reported_elements": "compared"
                    }
                },
                "evaluate": {"test": "check"}
            }
        }
        errors = list(document_errors(validators["assessment.schema.json"], valid))
        self.assertEqual(errors, [], [e.message for e in errors])

        invalid = json.loads(json.dumps(valid))
        invalid["assessment"]["objects"]["passwd"]["select"]["invented"] = {
            "value": "x", "operation": "equal", "datatype": "string"
        }
        self.assertTrue(list(document_errors(validators["assessment.schema.json"], invalid)))

if __name__ == "__main__":
    unittest.main()
