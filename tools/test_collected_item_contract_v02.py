#!/usr/bin/env python3
"""Known-result structural/relationship cases, not target collector conformance."""
import copy
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from collected_item_contract_v02 import ROOT, NAMES, capability_schema, context_errors, shared
from generate_capability_schema import generate


class CollectedItemContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        item, types = shared()
        cls.registry = Registry().with_resources((s["$id"], Resource.from_contents(s)) for s in [item, types])
        cls.schemas = {}
        cls.original = {}
        for path in sorted((ROOT / "schema/v0.1.0/capability-mappings").glob("*.json")):
            mapping = json.loads(path.read_text())
            if "capability" in mapping:
                cls.schemas[mapping["capability"]] = capability_schema(mapping)
                cls.original[mapping["capability"]] = generate(mapping, ROOT)

    def errors(self, item):
        validator = jsonschema.Draft202012Validator(self.schemas[item["capability"]], registry=self.registry,
                                                  format_checker=jsonschema.FormatChecker())
        errors = list(validator.iter_errors(item))
        return errors or context_errors(item)

    def sample(self, capability="unix.file"):
        return {"id": "item-1", "capability": capability, "status": "exists", "fields": {},
                "provenance": {"target_ref": "fixture-target", "source_execution_ref": "collect-1"}}

    def resolved(self, capability, name, source, status="exists"):
        item = self.sample(capability)
        item["fields"][source] = {"datatype": "integer", "value": 1001}
        item["fields"][name] = {"datatype": "string", "status": status}
        if status == "exists":
            item["fields"][name]["value"] = "fixture-name"
        item["context"] = {"name_resolution": {name: {
            "source_field": source, "target_context_ref": "fixture-target/accounts",
            "source_ref": "fixture-nss-snapshot", "observed_at": "2026-10-03T00:00:00Z"}}}
        return item

    def test_all_mappings_generate_and_meta_validate(self):
        self.assertEqual(len(self.schemas), 100)
        self.assertEqual(sum(s is not None for s in self.schemas.values()), 99)
        for schema in [*shared(), *[s for s in self.schemas.values() if s is not None]]:
            jsonschema.Draft202012Validator.check_schema(schema)

    def test_extensions_are_only_result_fields(self):
        for capability, names in NAMES.items():
            old = self.original[capability]
            state = json.dumps(old["$defs"]["state"])
            obj = json.dumps(old["$defs"].get("object", {}))
            for name in names:
                self.assertNotIn('"' + name + '"', state)
                self.assertNotIn('"' + name + '"', obj)
            fields = self.schemas[capability]["allOf"][1]["properties"]["fields"]["properties"]
            for name, source in names.items():
                self.assertIn(name, fields)
                self.assertIn(source, fields)

    def test_each_resolved_name_and_failure_status(self):
        for capability, names in NAMES.items():
            for name, source in names.items():
                for status in ["exists", "does_not_exist", "error", "not_collected"]:
                    with self.subTest(capability=capability, name=name, status=status):
                        item = self.resolved(capability, name, source, status)
                        before = copy.deepcopy(item["fields"][source])
                        self.assertFalse(self.errors(item))
                        self.assertEqual(item["fields"][source], before)

    def test_names_optional(self):
        item = self.sample()
        item["fields"]["owner_uid"] = {"datatype": "integer", "value": 1001}
        self.assertFalse(self.errors(item))

    def test_name_requires_original_identity_and_correct_provenance(self):
        baseline = self.resolved("unix.file", "owner_user_name", "owner_uid")
        for change in ["missing-id", "missing-context", "wrong-source", "unavailable-id", "redacted-id"]:
            item = copy.deepcopy(baseline)
            if change == "missing-id":
                del item["fields"]["owner_uid"]
            elif change == "missing-context":
                del item["context"]
            elif change == "wrong-source":
                item["context"]["name_resolution"]["owner_user_name"]["source_field"] = "owner_gid"
            elif change == "unavailable-id":
                item["fields"]["owner_uid"] = {"datatype": "integer", "status": "not_collected"}
            else:
                item["fields"]["owner_uid"] = {"datatype": "integer", "redacted": True}
            with self.subTest(change=change):
                self.assertTrue(self.errors(item))

    def test_redaction_and_absence_never_contain_values(self):
        item = self.resolved("unix.file", "owner_user_name", "owner_uid")
        item["fields"]["owner_user_name"]["redacted"] = True
        self.assertTrue(self.errors(item))
        del item["fields"]["owner_user_name"]["value"]
        self.assertFalse(self.errors(item))
        for status in ["error", "not_collected", "does_not_exist"]:
            item["fields"]["owner_user_name"] = {"datatype": "string", "status": status, "value": None}
            self.assertTrue(self.errors(item))

    def test_item_and_entity_status_domains(self):
        for status in ["exists", "does_not_exist", "error", "not_collected"]:
            item = self.sample()
            item["status"] = status
            # Partial nonexistent Items may retain an observed directory.
            item["fields"]["directory"] = {"datatype": "string", "value": "/fixture"}
            self.assertFalse(self.errors(item))
        for status in ["complete", "incomplete", "unknown", "not_applicable", "true"]:
            item = self.sample()
            item["status"] = status
            self.assertTrue(self.errors(item))

    def test_locators_have_explicit_units_and_field_relationships(self):
        locators = [
            {"kind": "text", "source_ref": "resource-1", "line": 3, "column": 2},
            {"kind": "structured", "source_ref": "resource-1", "path_language": "JSON Pointer", "path": "/settings/0"},
            {"kind": "record", "source_ref": "query-result-1", "index": 0, "field": "owner_uid"},
        ]
        item = self.sample()
        item["fields"]["owner_uid"] = {"datatype": "integer", "value": 1001}
        for locator in locators:
            item["context"] = {"locators": [locator]}
            self.assertFalse(self.errors(item))
        for locator in [dict(locators[0], line=0), dict(locators[1], column=1),
                        dict(locators[2], index=-1), dict(locators[2], field="missing")]:
            item["context"] = {"locators": [locator]}
            self.assertTrue(self.errors(item))

    def test_import_preserves_origin_and_resolution_context(self):
        item = self.resolved("unix.file", "owner_user_name", "owner_uid")
        item["imported"] = True
        self.assertTrue(self.errors(item))
        item["context"]["origin"] = {"result_ref": "original-result", "item_ref": "original-item"}
        self.assertFalse(self.errors(item))

    def test_closed_fields_do_not_restore_registry_view(self):
        for capability in ["windows.registry", "windows.ntuser"]:
            item = self.sample(capability)
            item["fields"]["registry_view"] = {"datatype": "string", "value": "64-bit"}
            self.assertTrue(self.errors(item))

    def test_published_known_result_fixtures(self):
        cases = json.loads((ROOT / "tests/collected-items-0.2.0/cases.json").read_text())
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(not bool(self.errors(case["item"])), case["expected_valid"])

    def test_resolution_types_and_timestamps(self):
        item = self.resolved("unix.file", "owner_user_name", "owner_uid")
        item["fields"]["owner_user_name"]["value"] = 1001
        self.assertTrue(self.errors(item))
        item["fields"]["owner_user_name"]["value"] = "fixture-user"
        item["context"]["name_resolution"]["owner_user_name"]["observed_at"] = "2026-10-03"
        self.assertTrue(self.errors(item))

    def test_record_absence_and_nested_redaction(self):
        item = self.sample("windows.wmi.query")
        for status in ["error", "does_not_exist", "not_collected"]:
            item["fields"]["result"] = [{"datatype": "record", "status": status}]
            self.assertFalse(self.errors(item))
        item["fields"]["result"] = [{"datatype": "record", "value": {
            "secret": {"datatype": "string", "redacted": True}}}]
        self.assertFalse(self.errors(item))
        item["fields"]["result"][0]["value"]["secret"]["value"] = "secret"
        self.assertTrue(self.errors(item))

    def test_record_property_and_value_index_relationships(self):
        item = self.sample("windows.wmi.query")
        item["fields"]["result"] = [{"datatype": "record", "value": {
            "Caption": {"datatype": "string", "value": "Fixture"}}}]
        locator = {"kind": "record", "source_ref": "query-1", "index": 0,
                   "field": "result", "value_index": 0, "property": "Caption"}
        item["context"] = {"locators": [locator]}
        self.assertFalse(self.errors(item))
        locator["value_index"] = 1
        self.assertTrue(self.errors(item))
        locator["value_index"] = 0
        locator["property"] = "Missing"
        self.assertTrue(self.errors(item))


if __name__ == "__main__":
    unittest.main()
