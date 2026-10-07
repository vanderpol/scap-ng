#!/usr/bin/env python3
import unittest

from research_fstab_semantics import (
    REWRITE_ID,
    compare_complete_case,
    compare_incomplete_case,
    modernization_preconditions,
)


class FstabModernizationSemanticTests(unittest.TestCase):
    def test_complete_zero_matching_rows_preserves_false(self):
        result = compare_complete_case([], "nodev")
        self.assertTrue(result["equivalent"])
        self.assertEqual(result["faithful"], "false")
        self.assertEqual(result["candidate"], "false")

    def test_complete_first_row_contains_required_option(self):
        result = compare_complete_case(
            [{"mount_point": "/tmp", "options": "rw,nodev,nosuid"}],
            "nodev",
        )
        self.assertTrue(result["equivalent"])
        self.assertEqual(result["candidate"], "true")

    def test_complete_first_row_lacks_required_option(self):
        result = compare_complete_case(
            [{"mount_point": "/tmp", "options": "rw,nosuid"}],
            "nodev",
        )
        self.assertTrue(result["equivalent"])
        self.assertEqual(result["candidate"], "false")

    def test_source_instance_one_means_later_duplicate_cannot_rescue_first(self):
        result = compare_complete_case(
            [
                {"mount_point": "/tmp", "options": "rw,nosuid"},
                {"mount_point": "/tmp", "options": "rw,nodev"},
            ],
            "nodev",
        )
        self.assertTrue(result["equivalent"])
        self.assertEqual(result["candidate"], "false")

    def test_source_instance_one_means_later_duplicate_cannot_invalidate_first(self):
        result = compare_complete_case(
            [
                {"mount_point": "/tmp", "options": "rw,nodev"},
                {"mount_point": "/tmp", "options": "rw,nosuid"},
            ],
            "nodev",
        )
        self.assertTrue(result["equivalent"])
        self.assertEqual(result["candidate"], "true")

    def test_incomplete_zero_rows_is_not_equivalent(self):
        result = compare_incomplete_case([], "nodev")
        self.assertFalse(result["equivalent"])
        self.assertEqual(result["faithful"], "error")
        self.assertEqual(result["candidate"], "unknown")

    def test_incomplete_matching_option_is_not_equivalent(self):
        result = compare_incomplete_case(
            [{"mount_point": "/tmp", "options": "rw,nodev,nosuid"}],
            "nodev",
        )
        self.assertFalse(result["equivalent"])
        self.assertEqual(result["faithful"], "error")
        self.assertEqual(result["candidate"], "unknown")

    def test_incomplete_nonmatching_option_is_not_equivalent(self):
        result = compare_incomplete_case(
            [{"mount_point": "/tmp", "options": "rw,nosuid"}],
            "nodev",
        )
        self.assertFalse(result["equivalent"])
        self.assertEqual(result["faithful"], "error")
        self.assertEqual(result["candidate"], "false")

    def test_complete_runtime_proof_still_is_not_static_rewrite_permission(self):
        report = modernization_preconditions({
            "source_capability": "independent.textfilecontent54",
            "filepath": "/etc/fstab",
            "instance": 1,
            "source_collection_status": "complete",
            "projection_field": "subexpression",
            "split_delimiter": ",",
            "regex_field_mapping_proven": True,
            "lexical_equivalence_proven": True,
        })
        self.assertTrue(report["bounded_complete_case_proven"])
        self.assertFalse(report["eligible"])
        self.assertIn(
            "runtime_collection_status_not_statically_provable",
            report["reasons"],
        )

    def test_empty_option_capture_is_outside_regex_proof_class(self):
        with self.assertRaisesRegex(ValueError, "outside first proof class"):
            compare_complete_case(
                [{"mount_point": "/tmp", "options": ""}],
                "nodev",
            )

    def test_non_complete_collection_fails_closed(self):
        report = modernization_preconditions({
            "source_capability": "independent.textfilecontent54",
            "filepath": "/etc/fstab",
            "instance": 1,
            "source_collection_status": "incomplete",
            "projection_field": "subexpression",
            "split_delimiter": ",",
            "regex_field_mapping_proven": True,
            "lexical_equivalence_proven": True,
        })
        self.assertEqual(report["rewrite_id"], REWRITE_ID)
        self.assertFalse(report["eligible"])
        self.assertIn("non_complete_collection_not_proven", report["reasons"])

    def test_parser_equivalence_must_be_proven_not_assumed(self):
        report = modernization_preconditions({
            "source_capability": "independent.textfilecontent54",
            "filepath": "/etc/fstab",
            "instance": 1,
            "source_collection_status": "complete",
            "projection_field": "subexpression",
            "split_delimiter": ",",
            "regex_field_mapping_proven": True,
            "lexical_equivalence_proven": False,
        })
        self.assertFalse(report["eligible"])
        self.assertIn(
            "parser_lexical_equivalence_not_proven",
            report["reasons"],
        )


if __name__ == "__main__":
    unittest.main()
