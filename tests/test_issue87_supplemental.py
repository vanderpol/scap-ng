"""Independent checks of the supplemental 0.4.1 fixture and oracle pairs."""
import copy
from pathlib import Path
import sqlite3
import unittest
import xml.etree.ElementTree as ET

from conformance.tools.runner import CONFORMANCE, load, schema_validator
from conformance.tools.oval_source_audit import BASE, scan_xml

CORPUS = CONFORMANCE / "oval-self-assertion"
INDEPENDENT = "{" + BASE + "#independent}"
OVAL = "{" + BASE + "}"


def evaluate_presence_tree(expression, inputs, guards):
    """Resolve only fixture Input guards and return the reached terminal node."""
    if "if" not in expression:
        return expression
    branches = [expression, *expression.get("else_if", [])]
    for branch in branches:
        name = branch["if"]["input_provided"]
        guards.append(name)
        if name in inputs:
            return evaluate_presence_tree(branch["then"], inputs, guards)
    return evaluate_presence_tree(expression["else"], inputs, guards)


class SupplementalConformance(unittest.TestCase):
    def test_documents_and_negative_conditional(self):
        manifest = load(CONFORMANCE / "supplemental-manifest.json")
        schema = schema_validator("assessment.schema.json")
        for case in manifest["cases"]:
            document = load(CONFORMANCE / case["source"])
            with self.subTest(case=case["id"]):
                self.assertIs(
                    schema_validator(case["schema"]).is_valid(document), case["valid"],
                )
                if not case["valid"]:
                    document["assessment"]["evaluate"]["else"] = {"test": "example-test"}
                    schema.validate(document)

    def test_input_presence_walk_matches_independent_branch_expectations(self):
        document = load(CONFORMANCE / "cases/supplemental/conditional-ordered.assessment.yaml")["assessment"]
        inputs = load(CONFORMANCE / "fixtures/conditional-ordered.json")["input_variants"]
        expected = load(CONFORMANCE / "expected/conditional-ordered.json")["variants"]
        self.assertEqual(inputs.keys(), expected.keys())
        for name, fixture in inputs.items():
            with self.subTest(variant=name):
                self.assertLessEqual(fixture.keys(), document["inputs"].keys())
                guards = []
                node = evaluate_presence_tree(document["evaluate"], fixture, guards)
                self.assertEqual(guards, expected[name]["guards_in_order"])
                outcomes = {}
                if "test" in node:
                    test = document["tests"][node["test"]]
                    value = document["variables"][test["variable"]]["expression"]["literal"]
                    target = test["require"]["fields"]["value"]["equals"]
                    result = "true" if value == target else "false"
                    outcomes[node["test"]] = result
                else:
                    self.assertIn("not_evaluated", node)
                    result = "not_evaluated"
                self.assertEqual(outcomes, expected[name]["test_outcomes"])
                self.assertEqual(result, expected[name]["assessment_outcome"])

        # A provided empty population must not be treated as absent. Removing
        # it changes the nested result, while removing the skipped alternative does not.
        fixture = inputs["provided-empty-selects-nested"]
        unchanged = {key: value for key, value in fixture.items() if key != "tertiary-input"}
        decisive = {key: value for key, value in fixture.items() if key != "detail-input"}
        self.assertEqual(evaluate_presence_tree(document["evaluate"], unchanged, []), {"test": "nested-test"})
        self.assertEqual(evaluate_presence_tree(document["evaluate"], decisive, []), {"test": "secondary-test"})

    def test_manual_result_representation_and_independent_mappings(self):
        assessment = load(CONFORMANCE / "cases/supplemental/manual-response.assessment.yaml")["assessment"]
        result = load(CONFORMANCE / "cases/supplemental/manual-response.result.yaml")
        expected = load(CONFORMANCE / "expected/manual-response.json")["variants"]
        choices = {row["value"]: row["outcome"] for row in assessment["response"]["choices"]}
        self.assertEqual(choices, {row["answer"]: row["outcome"] for row in expected.values()})
        receipt = result["manual_assessment_result"]
        self.assertEqual(receipt["assessment"], {"id": assessment["id"], "version": assessment["version"]})
        self.assertEqual(receipt["outcome"], choices[receipt["answer"]])
        self.assertTrue(assessment["response"]["allow_comment"] and receipt["comment"])
        self.assertTrue(assessment["response"]["allow_evidence"] and receipt["evidence_refs"])
        schema = schema_validator("manual-assessment-result.schema.json")
        for answer, outcome in choices.items():
            witness = copy.deepcopy(result)
            witness["manual_assessment_result"].update(answer=answer, outcome=outcome)
            schema.validate(witness)

    def test_source_ids_cite_existing_tests_and_definitions(self):
        expected = load(CORPUS / "expected.json")
        for platform, family, lower, upper, rows in (
            ("unix", "yamlfilecontent", 101, 109, expected["yaml_cases"]),
            ("windows", "yamlfilecontent", 201, 209, expected["yaml_cases"]),
            ("agnostic", "sql512", 301, 303, expected["sql512_cases"]),
        ):
            source = CORPUS / platform / f"ind-def_{family}_test.xml"
            record, tests = scan_xml(source.read_bytes())
            ids = sorted(number for row in rows for number in row["definitions_and_tests"] if lower <= number <= upper)
            self.assertEqual([tag for tag, _ in tests], [INDEPENDENT + family + "_test"] * len(ids))
            self.assertEqual(record["ids"]["tests"], [f"{expected['id_prefix']}:tst:{number}" for number in ids])
            self.assertEqual(record["ids"]["definitions"], [f"{expected['id_prefix']}:def:{number}" for number in ids])
            document = ET.parse(source)
            for number in ids:
                definition = document.find(f".//{OVAL}definition[@id='{expected['id_prefix']}:def:{number}']")
                criterion = definition.find(f"{OVAL}criteria/{OVAL}criterion")
                self.assertEqual(criterion.attrib["test_ref"], f"{expected['id_prefix']}:tst:{number}")

    def test_yaml_selected_records_and_controlled_file_boundaries(self):
        settings = load(CORPUS / "fixtures/yaml/settings.yaml")
        other = load(CORPUS / "fixtures/yaml/other.yaml")
        expected = load(CORPUS / "expected.json")["yaml_cases"]
        wanted = load(CONFORMANCE / "expected/yaml-file-content.json")
        self.assertEqual(settings["settings"], expected[0]["selected_value"])
        self.assertNotEqual(settings["settings"]["myCamelCase^Key"], other["settings"]["myCamelCase^Key"])
        self.assertEqual(settings["sequence"], expected[2]["selected_value"])
        self.assertEqual(settings["sequence"].count("amber"), 2)
        self.assertEqual(settings["single"], expected[7]["selected_value"])
        fixture = CORPUS / "fixtures/yaml"
        self.assertFalse((fixture / "does-not-exist.yaml").exists())
        selected = [p.relative_to(fixture).as_posix() for p in sorted(fixture.glob("*/recursive.yaml"))]
        self.assertEqual(selected, [expected[6]["selected_document"]])
        self.assertEqual(len(list(fixture.rglob("recursive.yaml"))), 2)
        source_cases = {tuple(row["definitions_and_tests"]): row for row in expected}
        for platform in ("unix", "windows"):
            assessment = load(CONFORMANCE / f"cases/collector/yaml-file-{platform}.assessment.yaml")["assessment"]
            tests = assessment["tests"]
            self.assertIn(assessment["id"], wanted["case_ids"])
            self.assertEqual(tests.keys(), wanted["tests"].keys())
            self.assertEqual(tests["typed-key-test"]["object"], tests["field-mismatch-test"]["object"])
            operands = tests["typed-key-test"]["require"]["fields"]["value"]["record"]["fields"]
            self.assertEqual({key: predicate["equals"] for key, predicate in operands.items()}, settings["settings"])
            negative = tests["field-mismatch-test"]["require"]["fields"]["value"]["record"]["fields"]
            self.assertNotEqual(negative["myCamelCase^Key"]["equals"], settings["settings"]["myCamelCase^Key"])
            for expression in assessment["evaluate"]["and"]:
                test = expression.get("not", expression)["test"]
                row = wanted["tests"][test]
                self.assertEqual(row["outcome"], source_cases[tuple(row["oval_cases"])]["outcome"])
                self.assertEqual("not" in expression, row["outcome"] == "false")

    def test_sqlite_fixture_independently_proves_rows_and_decisive_mutation(self):
        expected = load(CORPUS / "expected.json")["sql512_cases"]
        prefix = load(CORPUS / "expected.json")["id_prefix"]
        xml = ET.parse(CORPUS / "agnostic/ind-def_sql512_test.xml")
        db = sqlite3.connect(":memory:")
        self.addCleanup(db.close)
        db.row_factory = sqlite3.Row
        db.executescript((CORPUS / "fixtures/sqlite.sql").read_text(encoding="utf-8"))
        db.execute("PRAGMA query_only = ON")
        for row in expected:
            number, = row["definitions_and_tests"]
            obj = xml.find(f".//{INDEPENDENT}sql512_object[@id='{prefix}:obj:{number}']")
            query = obj.findtext(INDEPENDENT + "sql")
            observed = [dict(value) for value in db.execute(query)]
            self.assertEqual(observed, row["rows"])
            if row["outcome"] is None:
                self.assertFalse(observed)
                continue
            state = xml.find(f".//{INDEPENDENT}sql512_state[@id='{prefix}:ste:{number}']")
            field = state.find(f"{INDEPENDENT}result/{OVAL}field[@name='measurement']")
            matches = observed[0]["measurement"] == int(field.text)
            self.assertEqual("true" if matches else "false", row["outcome"])


if __name__ == "__main__":
    unittest.main()
