"""Verify the canonical manual-choice, package and workbook lifecycle evidence."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from conformance.tools.build_content_fixture import build
from conformance.tools.runner import CONFORMANCE, load, schema_validator

FIXTURE = CONFORMANCE / "manual-lifecycle"


class ManualLifecycleCases(unittest.TestCase):
    def test_each_canonical_response_choice_has_a_standalone_result(self):
        expected = load(FIXTURE / "expected.json")
        assessment = load(CONFORMANCE / expected["assessment_source"])["assessment"]
        positive = load(CONFORMANCE / expected["standalone_result_source"])
        outcomes = load(CONFORMANCE / "expected/manual-response.json")["variants"]
        choices = {choice["value"]: choice for choice in assessment["response"]["choices"]}
        self.assertEqual({row["outcome"] for row in outcomes.values()}, set(expected["completed"]))
        schema = schema_validator("manual-assessment-result.schema.json")

        for name, row in outcomes.items():
            with self.subTest(case=name):
                authored = choices[row["answer"]]
                self.assertEqual(authored["outcome"], row["outcome"])
                candidate = deepcopy(positive)
                body = candidate["manual_assessment_result"]
                body.update(execution_id=f'conformance-manual-{name}', answer=row["answer"],
                            answer_label=authored["label"], outcome=row["outcome"], comment=row["reason"])
                schema.validate(candidate)
                self.assertEqual(body["assessment"], {"id": assessment["id"], "version": assessment["version"]})
                self.assertTrue(body["evidence_refs"])

        invalid = deepcopy(positive)
        invalid["manual_assessment_result"]["outcome"] = "disabled"
        self.assertFalse(schema.is_valid(invalid))

    def test_workbook_receipt_distinguishes_explicit_answers_and_stale_revisions(self):
        expected = load(FIXTURE / "expected.json")
        receipt = load(FIXTURE / "ri-receipt.json")
        sources_path = FIXTURE / "sources.json"
        sources = load(sources_path)
        self.assertEqual(receipt["schema_pin"], sources["schema_pin"])
        with TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            build(package, sources_path)
            self.assertEqual(sha256((package / "manifest.json").read_bytes()).hexdigest(),
                             receipt["manifest_sha256"])
            assessment_digest = sha256((package / "assessments/approval.json").read_bytes()).hexdigest()
            self.assertEqual(receipt["lifecycle"]["initial"]["package_assessment_sha256"], assessment_digest)
            rule = load(package / "rules/approval.json")["rule"]
            choice = rule["assessment_choices"][rule["default_assessment_choice"]]
            self.assertEqual(choice, {"assessment": expected["assessment"], "expected_version": 1})

        fingerprints = set()
        for name, disposition in expected["lifecycle"].items():
            observed = receipt["lifecycle"][name]
            self.assertEqual({key: observed[key] for key in ("status", "imported")}, disposition)
            fingerprints.add(observed["package_assessment_sha256"])
        self.assertEqual(len(fingerprints), len(expected["lifecycle"]))
        for outcome, disposition in expected["completed"].items():
            observed = receipt["completed"][outcome]
            self.assertEqual(observed["imported"], disposition["imported"])
            if not disposition["imported"]:
                self.assertIn(f'invalid answered outcome "{outcome}"', observed["diagnostic"])


if __name__ == "__main__":
    unittest.main()
