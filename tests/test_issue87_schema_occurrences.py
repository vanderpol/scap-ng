"""Check exact schema value locations and corpus witness scopes."""
from collections import Counter
from hashlib import sha256
import unittest

from conformance.tools.runner import CONFORMANCE, load

REPORT = CONFORMANCE / "qualification/schema-value-occurrences.json"


class SchemaOccurrenceCases(unittest.TestCase):
    def test_reachable_occurrences_keep_unmatched_values_and_draft_scopes(self):
        report = load(REPORT)
        index = load(CONFORMANCE / "schema-coverage.json")
        self.assertEqual(report["schema_commit"], index["schema_commit"])
        self.assertEqual(report["schema_family_sha256"], index["schema_family_sha256"])
        computed = Counter()
        occurrences = report["occurrences"]
        for row in occurrences.values():
            reachable = bool(row["entry_points"])
            computed["reachable_occurrences" if reachable else "unreachable_occurrences"] += 1
            for value in row["values"]:
                computed["declared_values"] += 1
                if reachable:
                    computed["reachable_values"] += 1
                    if not value["matches"]:
                        computed["without_match"] += 1
                    for scope, path in value["matches"].items():
                        computed[f"matched_by_{scope}"] += 1
                        case = report["cases"][path]
                        self.assertEqual((case["scope"], case["valid"]), (scope, True))
                        if value["value"] == "esx.host_account":
                            self.assertEqual(scope, "experimental")
            for scope, path in row["rejections"].items():
                case = report["cases"][path]
                self.assertEqual((case["scope"], case["valid"]), (scope, False))
        self.assertEqual(report["coverage"], computed)
        self.assertGreater(computed["without_match"], 0)
        self.assertGreater(computed["matched_by_experimental"], 0)
        self.assertGreater(computed["matched_by_draft-transport"], 0)

    def test_manual_result_outcomes_and_provenance_are_witnessed_at_exact_locations(self):
        report = load(REPORT)
        manual_schema = "schema/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties"
        rows = report["occurrences"]
        expected = load(CONFORMANCE / "manual-lifecycle/expected.json")
        outcomes = rows[f"{manual_schema}/outcome/enum"]["values"]
        self.assertEqual({row["value"] for row in outcomes}, set(expected["completed"]))
        self.assertEqual({row["matches"]["active"] for row in outcomes}, set(expected["standalone_results"].values()))
        sources = rows[f"{manual_schema}/response_source/enum"]["values"]
        self.assertEqual({row["value"] for row in sources if "active" in row["matches"]},
                         {"direct", "imported", "delegated"})
        for row in outcomes:
            path = row["matches"]["active"]
            source = CONFORMANCE / path
            self.assertEqual(sha256(source.read_bytes()).hexdigest(), report["cases"][path]["sha256"])
            self.assertEqual(load(source)["manual_assessment_result"]["outcome"], row["value"])


if __name__ == "__main__":
    unittest.main()
