"""Check supplied evidence and its authored Result against the native contract."""
from copy import deepcopy
import re
import unittest

from conformance.tools.runner import CONFORMANCE, load, schema_validator
from conformance.tools.semantic import validate

SUITE = CONFORMANCE / "result-evidence"


def source_projection(assessment, supplied):
    """Compute this singleton-field comparison over complete supplied evidence."""
    test_id = assessment["evaluate"]["test"]
    test = assessment["tests"][test_id]
    shared = assessment["shared_objects"][test["object"]]
    selector = shared["full_path"]["matches_regex"]
    selected = [row for row in supplied["items"] if re.search(selector, row["path"])]
    population = [row["owner"] for row in selected]
    matches = [
        any(type(observed) is type(expected) and observed == expected for expected in population)
        for observed in population
    ]
    return {
        "outcome": str(bool(matches) and all(matches)).lower(),
        "variable_values": population,
        "item_order": [row["id"] for row in selected],
        "test_items_observed": len(selected),
        "test_items_evaluated": len(matches),
        "test_mismatches": matches.count(False),
    }


class ResultEvidenceCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load(SUITE / "expected.json")
        cls.source = load(SUITE / cls.manifest["source"])
        cls.supplied = load(SUITE / cls.manifest["fixture"])
        cls.result_document = load(SUITE / "owner.result.yaml")
        cls.report_document = load(SUITE / "owner.item-report.yaml")

    def test_result_agrees_with_independent_observations(self):
        schema_validator("assessment.schema.json").validate(self.source)
        self.assertEqual(validate(self.source), [])
        for path, schema in self.manifest["documents"].items():
            schema_validator(schema).validate(load(SUITE / path))
        manifest = load(CONFORMANCE / "manifest.json")
        self.assertEqual(manifest["schema_commit"], self.manifest["schema_commit"])

        assessment = self.source["assessment"]
        test_id = assessment["evaluate"]["test"]
        authored_test = assessment["tests"][test_id]
        variable_id = authored_test["require"]["fields"]["owner_uid"]["equals"]["variable"]
        self.assertEqual(
            assessment["variables"][variable_id]["expression"]["values"],
            {"object": {"object_ref": authored_test["object"]}, "field": "owner_uid"},
        )
        self.assertEqual(authored_test["require"]["fields"]["owner_uid"]["value_match"], "one_or_more")
        expected = self.manifest["observations"]
        self.assertEqual(source_projection(assessment, self.supplied), expected)
        result = self.result_document["assessment_result"]
        self.assertEqual(result["outcome"], expected["outcome"])
        self.assertEqual(result["target_ref"], self.supplied["target"])
        self.assertEqual(result["execution_id"], self.supplied["execution"])
        self.assertEqual(result["assessment"], {"id": assessment["id"], "version": assessment["version"]})
        test, = result["tests"]
        collection, = result["objects"]
        variable, = result["variables"]
        self.assertEqual(test["id"], test_id)
        self.assertEqual(test["invocation_ref"], result["execution_id"])
        self.assertEqual(test["outcome"], expected["outcome"])
        self.assertEqual(test["object_refs"], [authored_test["object"]])
        self.assertEqual(collection["id"], self.supplied["object"])
        self.assertEqual(collection["source_execution_ref"], result["execution_id"])
        self.assertEqual(collection["status"], "complete")
        self.assertEqual(variable["id"], variable_id)
        self.assertEqual(variable["status"], "complete")
        self.assertEqual(variable["cardinality"], "many")
        self.assertEqual([entry["value"] for entry in variable["values"]], expected["variable_values"])
        for entry in variable["values"]:
            self.assertEqual((entry["datatype"], entry["status"]), ("integer", "exists"))
        self.assertEqual(collection["item_refs"], expected["item_order"])
        self.assertEqual(variable["item_refs"], expected["item_order"])
        self.assertEqual(test["item_refs"], expected["item_order"])
        self.assertEqual(test["items_observed"], expected["test_items_observed"])
        per_item = test["per_item_results"]
        summary = test["item_summary"]
        self.assertEqual(
            summary,
            {"evaluated_items": expected["test_items_evaluated"],
             "observed_mismatches": expected["test_mismatches"],
             "actual_mismatches": expected["test_mismatches"],
             "returned_items": len(per_item), "truncated_evidence": False},
        )
        refs = [item["item_ref"] for item in per_item]
        self.assertEqual(refs, expected["item_order"])
        self.assertEqual([item["item"]["id"] for item in per_item], refs)
        self.assertEqual([item["outcome"] for item in per_item], ["true"] * len(refs))
        for observed, supplied in zip(per_item, self.supplied["items"], strict=True):
            item = observed["item"]
            self.assertEqual(item["capability"], authored_test["capability"])
            self.assertEqual(item["fields"]["full_path"]["value"], supplied["path"])
            self.assertEqual(item["fields"]["owner_uid"]["value"], supplied["owner"])
            self.assertEqual(item["fields"]["group_id"]["value"], str(supplied["group"]))
            self.assertEqual(item["provenance"], {
                "source_ref": self.supplied["source"], "target_ref": self.supplied["target"],
            })
            requirement, = observed["require_results"]
            field, = requirement["field_results"]
            self.assertEqual(requirement["require_ref"], f"/tests/{test_id}/require")
            self.assertEqual(field["require_ref"], f"/tests/{test_id}/require/fields/owner_uid")
            self.assertEqual(field["observed_values"], [item["fields"]["owner_uid"]])
            self.assertEqual(field["expected_values"], variable["values"])

    def test_item_report_preserves_source_and_marks_omissions(self):
        result = self.result_document["assessment_result"]
        report = self.report_document["item_report"]
        self.assertEqual(report["source_execution_ref"], result["execution_id"])
        for field in ("logical_complete", "population_complete", "evidence_complete"):
            self.assertIs(report["source_completeness"][field], result[field])
        test, = result["tests"]
        original = [row["item"] for row in test["per_item_results"]]
        self.assertEqual(len(original), len(report["items"]))
        for source, projected in zip(original, report["items"], strict=True):
            selection = projected["selection"]
            self.assertEqual(selection, {
                "omitted_elements": ["group_id"],
                "unavailable_elements": [],
                "retained_required_elements": ["full_path", "owner_uid"],
            })
            item = projected["item"]
            self.assertEqual(item, source | {"fields": {"full_path": source["fields"]["full_path"],
                                                       "owner_uid": source["fields"]["owner_uid"]}})
            uses = [use for use in result["field_uses"] if use["item_ref"] == source["id"]]
            self.assertEqual({use["relationship"]: use["used_elements"] for use in uses},
                             {"direct": ["owner_uid"], "variable": ["owner_uid"],
                              "selection": ["full_path"]})
            self.assertTrue(all(use["test_ref"] == test["id"] for use in uses))
            self.assertEqual({field for use in uses for field in use["required_elements"]},
                             set(selection["retained_required_elements"]))
        counts = {"available_count": len(original), "included_count": len(original), "omitted_count": 0}
        self.assertEqual(result["item_materialization"], {
            "scope": "all",
            **counts,
            "consumed_item_refs": test["item_refs"],
            "collections": [{"object_ref": self.supplied["object"], **counts}],
        })

    def test_schema_controls_and_evidence_mutations(self):
        for schema, cases in self.manifest["schema_controls"].items():
            validator = schema_validator(schema)
            admitted = validator.schema["properties"]["status"]["enum"]
            self.assertEqual({row["status"] for row in cases["accept"].values()}, set(admitted))
            for disposition in ("accept", "reject"):
                for name, changes in cases[disposition].items():
                    with self.subTest(schema=schema, case=name):
                        self.assertEqual(validator.is_valid(cases["base"] | changes), disposition == "accept")

        report_schema = schema_validator("item-report.schema.json")
        report = deepcopy(self.report_document)
        selection = report["item_report"]["items"][0]["selection"]
        selection["omitted_elements"].append("group_id")
        self.assertFalse(report_schema.is_valid(report))
        selection["omitted_elements"].pop()
        report["item_report"]["items"][0]["item"]["fields"]["owner_uid"]["redacted"] = True
        self.assertFalse(report_schema.is_valid(report))

        assessment = self.source["assessment"]
        supplied = deepcopy(self.supplied)
        supplied["items"][1]["owner"] = 7
        changed = source_projection(assessment, supplied)
        self.assertEqual(changed["variable_values"], [42, 7])
        self.assertEqual(changed["outcome"], "true")
        self.assertNotEqual(changed, self.manifest["observations"])
        supplied["items"][1]["path"] = "/different-fixture/b"
        self.assertEqual(source_projection(assessment, supplied)["item_order"], ["owner-a"])
