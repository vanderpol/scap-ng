"""Regression guards for pinned six-STIG shared Applicability repair (#232 #239)."""
import unittest

from v04_restore_missing_applicability import _missing


class ApplicabilityRestorationTests(unittest.TestCase):
    def fixture(self):
        docs = {
            "authoring/rhel_9/applicability.json": {"applicability": {
                "id": "rhel.applicability", "conditions": {}}},
            "authoring/oracle_linux_9/applicability.json": {"applicability": {
                "id": "oracle.applicability", "conditions": {}}},
        }
        for number in range(11):
            for prefix in ("rhel_9", "oracle_linux_9"):
                catalog = docs[f"authoring/{prefix}/applicability.json"]["applicability"]
                catalog["conditions"][f"condition.{number}"] = {
                    "assessment": f"ng.shared.check-{number}"}
        return docs

    def test_expected_22_links_require_11_unique_shared_assessments(self):
        self.assertEqual(_missing(self.fixture()),
                         {f"ng.shared.check-{i}" for i in range(11)})

    def test_new_or_missing_reference_does_not_waive_graph_integrity(self):
        docs = self.fixture()
        docs["authoring/rhel_9/applicability.json"]["applicability"][
            "conditions"]["new.condition"] = {"assessment": "unexpected"}
        with self.assertRaisesRegex(ValueError, "omission census changed"):
            _missing(docs)

    def test_unresolved_rule_choice_still_fails_closed(self):
        docs = self.fixture()
        docs["authoring/rhel_9/rules/SV-TEST.rule.json"] = {"rule": {
            "id": "SV-TEST", "default_assessment_choice": "automated",
            "assessment_choices": {"automated": {"assessment": "missing"}}}}
        with self.assertRaisesRegex(ValueError, "unexpected historical source graph defects"):
            _missing(docs)


if __name__ == "__main__":
    unittest.main()
