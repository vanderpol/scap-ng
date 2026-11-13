"""SCAP-NG 0.4.1 SIEM GUID correlation contract.

Tests the exact flat canonical schema, not an alternate results schema.
GUIDs are metadata only: no effect on Item/status/cardinality outcomes.
"""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT/"schema"/"scan-result.schema.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((ROOT/"examples"/"results"/"scan-siem-correlation.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())
UUID = "f181206b-6966-4841-a7bb-78f7660120d8"


class ScanCorrelationGuids(unittest.TestCase):
    def valid(self, doc):
        errors = list(VALIDATOR.iter_errors(doc))
        self.assertEqual(errors, [], [f"{list(e.path)}: {e.message}" for e in errors])

    def invalid(self, doc):
        self.assertTrue(list(VALIDATOR.iter_errors(doc)), "expected invalid 0.4.1 scan result")

    def test_stable_lowercase_guids_and_versioned_example(self):
        self.assertEqual(SCHEMA["$id"], "https://scap-ng.dev/schema/v0.4.1/scan-result.schema.json")
        self.valid(SAMPLE)
        self.assertEqual(SAMPLE["scan_result"]["result_schema_version"], "0.4.1")

    def test_all_three_fields_are_pure_metadata_and_optional(self):
        item = copy.deepcopy(SAMPLE)
        result = item["scan_result"]
        result.pop("scan_session_guid")
        result["scanner"].pop("app_guid")
        result["targets"][0].pop("machine_guid")
        self.valid(item)
        self.assertEqual(result["run_id"], SAMPLE["scan_result"]["run_id"])
        self.assertEqual(result["benchmark_results"], SAMPLE["scan_result"]["benchmark_results"])

    def test_per_target_identity_not_a_scan_wide_machine_id(self):
        item = copy.deepcopy(SAMPLE)
        item["scan_result"]["targets"].append({"id":"target-002", "machine_guid": UUID})
        self.valid(item)
        item["scan_result"]["machine_guid"] = UUID
        self.invalid(item)

    def test_guids_use_canonical_lowercase_uuid_syntax(self):
        for field in ("machine_guid", "app_guid", "scan_session_guid"):
            for invalid in ("", "not-a-guid", "D9728D09-D34C-4D99-9AE3-87CE76C44577",
                            "d9728d09d34c4d999ae387ce76c44577", "123"):
                with self.subTest(field=field, value=invalid):
                    item = copy.deepcopy(SAMPLE)
                    if field == "machine_guid":
                        item["scan_result"]["targets"][0][field] = invalid
                    elif field == "app_guid":
                        item["scan_result"]["scanner"][field] = invalid
                    else:
                        item["scan_result"][field] = invalid
                    self.invalid(item)

    def test_scanner_existing_metadata_is_not_disallowed(self):
        item = copy.deepcopy(SAMPLE)
        item["scan_result"]["scanner"]["vendor"] = "enterprise"
        item["scan_result"]["scanner"]["extensions"] = {"tenant": "sample"}
        self.valid(item)

    def test_version_is_not_0_4_0(self):
        item = copy.deepcopy(SAMPLE)
        item["scan_result"]["result_schema_version"] = "0.4.0"
        self.invalid(item)

    def test_guid_is_not_a_technical_outcome_or_result_digest(self):
        self.assertNotIn("machine_guid", SCHEMA["properties"]["scan_result"]["properties"])
        self.assertEqual(
            SCHEMA["properties"]["scan_result"]["properties"]["benchmark_results"]["type"],
            "array",
        )


if __name__ == "__main__":
    unittest.main()
