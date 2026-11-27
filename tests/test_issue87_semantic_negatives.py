"""Check semantic-invalid native fixtures and their single-change controls."""
import copy
import unittest

from conformance.tools.runner import CONFORMANCE, load, validator


class SemanticAuthoringCases(unittest.TestCase):
    def setUp(self):
        self.root = CONFORMANCE / "semantic-negatives"
        self.manifest = load(self.root / "expected.json")
        self.schema = validator()

    def assessment(self, case_id):
        row = self.manifest["cases"][case_id]
        source = self.root / row["file"]
        document = load(source)
        self.schema.validate(document)
        self.assertEqual(document["assessment"]["id"], case_id)
        anchor = row["anchor"].split("#", 1)[0]
        self.assertTrue((CONFORMANCE.parent / anchor).is_file())
        return document

    def test_named_object_reference_requires_local_binding(self):
        case_id = "conformance-dangling-object"
        doc = self.assessment(case_id)
        assessment = doc["assessment"]
        ref = assessment["tests"]["file-test"]["object"]
        self.assertIsInstance(ref, str)
        self.assertNotIn(ref, assessment.get("shared_objects", {}))
        self.assertEqual(self.manifest["cases"][case_id]["authoring_expectation"], "unresolved_named_object")
        corrected = copy.deepcopy(doc)
        corrected["assessment"]["shared_objects"] = {
            ref: {"object_title": "Named control", "capability": "unix.file",
                  "full_path": {"equals": "/tmp/scap-ng-fixture"}},
        }
        self.schema.validate(corrected)
        self.assertIn(ref, corrected["assessment"]["shared_objects"])

    def test_optional_input_guard_does_not_protect_the_false_branch(self):
        case_id = "conformance-unguarded-input"
        doc = self.assessment(case_id)
        assessment = doc["assessment"]
        expression = assessment["evaluate"]
        reference = expression["if"]["input_provided"]
        self.assertFalse(assessment["inputs"][reference]["required"])
        self.assertEqual(expression["else"]["test"], expression["then"]["test"])
        test = assessment["tests"][expression["else"]["test"]]
        operand = test["require"]["fields"]["value"]["equals"]
        self.assertEqual(operand["input"], reference)
        self.assertEqual(
            self.manifest["cases"][case_id]["authoring_expectation"],
            "optional_input_reference_not_dominated",
        )
        corrected = copy.deepcopy(doc)
        corrected["assessment"]["evaluate"]["else"] = {
            "not_evaluated": {"reason": "Optional policy value was omitted"},
        }
        self.schema.validate(corrected)
        self.assertNotIn("test", corrected["assessment"]["evaluate"]["else"])
        self.assertEqual(corrected["assessment"]["evaluate"]["then"], expression["then"])

    def test_dependency_version_must_match_the_resolved_identity(self):
        case_id = "conformance-dependency-version"
        row = self.manifest["cases"][case_id]
        doc = self.assessment(case_id)
        assessment = doc["assessment"]
        alias = assessment["applicability"]["assessment"]
        dependency = assessment["dependencies"][alias]
        target = load(CONFORMANCE / row["target"])["assessment"]
        self.assertEqual(dependency["assessment"], target["id"])
        self.assertNotEqual(dependency["expected_version"], target["version"])
        self.assertEqual(row["authoring_expectation"], "dependency_version_mismatch")
        corrected = copy.deepcopy(doc)
        corrected["assessment"]["dependencies"][alias]["expected_version"] = target["version"]
        self.schema.validate(corrected)
        self.assertEqual(corrected["assessment"]["dependencies"][alias]["expected_version"], target["version"])


if __name__ == "__main__":
    unittest.main()
