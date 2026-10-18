#!/usr/bin/env python3
"""#229/#232: fail-closed source-backed complex Test profile regression."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_v04_a_lossless_ir import fixture
from v04_a_source_semantics_profile import source_profile


class ComplexSourceProfileTests(unittest.TestCase):
    def test_reproduce_selected_authored_test_contract(self):
        docs = fixture()
        report = source_profile(docs, ids=("ng.shared.auto",))
        self.assertEqual(report["stage"], "SOURCE_FACTS_ONLY_NOT_EXECUTION")
        self.assertEqual(report["checked_source_assessment_count"], 1)
        a = report["selected_source_assessments"][0]
        self.assertEqual(a["assessment_id"], "ng.shared.auto")
        self.assertEqual(a["mode"], "automated")
        self.assertEqual(a["evaluate_operators"], {"test": 1})
        self.assertEqual(len(a["tests"]), 1)
        self.assertEqual(a["tests"][0]["require"], "at_least_one_exists_and_all_match")
        self.assertEqual(len(a["source_document_sha256"]), 64)
        self.assertIsNone(a["tests"][0]["wmi_record_state_source"])
        self.assertIsNone(a["tests"][0]["wmi_object_source"])

    def test_missing_selected_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing source Assessment anchors"):
            source_profile(fixture(), ids=("does-not-exist",))

    def test_duplicate_source_identity_rejected(self):
        docs = fixture()
        path = "authoring/shared/assessments/ng.shared.auto.json"
        docs["authoring/shared/assessments/duplicate.json"] = deepcopy(docs[path])
        with self.assertRaisesRegex(ValueError, "duplicate Assessment source ID"):
            source_profile(docs, ids=("ng.shared.auto",))

    def test_duplicate_requested_target_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate or empty"):
            source_profile(fixture(), ids=("ng.shared.auto", "ng.shared.auto"))


if __name__ == "__main__":
    unittest.main()
