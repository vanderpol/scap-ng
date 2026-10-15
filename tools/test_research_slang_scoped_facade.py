#!/usr/bin/env python3
"""Exact one-case presentation lowering and explicit refusal regressions."""
import unittest
from copy import deepcopy

import yaml
from research_slang_scoped_facade import lower, RESEARCH_SAMPLE, UnsupportedFacade


class ScopedAuthoringFacadeTest(unittest.TestCase):
    def setUp(self):
        self.d = yaml.safe_load(RESEARCH_SAMPLE)

    def test_exact_canonical_03_presentation(self):
        expected = yaml.safe_load(r"""
tests:
  home-mounted-nosuid-option-test:
    capability: linux.partition
    object:
      capability: linux.partition
      select:
        mount_point:
          value: .*\\/home
          operation: pattern_match
    states:
      - field: mount_options
        value: nosuid
        operation: equals
        match: one_or_more
        existence: one_or_more
    reported_elements: all
    existence: one_or_more
    match: all
evaluate:
  test: home-mounted-nosuid-option-test
""")
        self.assertEqual(lower(self.d), expected)
        self.assertEqual(lower(self.d)["tests"]["home-mounted-nosuid-option-test"]["object"]["select"]["mount_point"]["value"],
                         self.d["checks"]["home-mounted-nosuid-option"]["select"]["mount_point"]["matches_regex"])

    def test_missing_item_existence_rejected(self):
        del self.d["checks"]["home-mounted-nosuid-option"]["require"]["items"]["exists"]
        with self.assertRaisesRegex(UnsupportedFacade, "required keys"):
            lower(self.d)

    def test_missing_field_existence_rejected(self):
        del self.d["checks"]["home-mounted-nosuid-option"]["expect"]["mount_options"]["values"]["exists"]
        with self.assertRaisesRegex(UnsupportedFacade, "required keys"):
            lower(self.d)

    def test_item_matching_must_not_change(self):
        self.d["checks"]["home-mounted-nosuid-option"]["require"]["items"]["match"] = "one_or_more"
        with self.assertRaisesRegex(UnsupportedFacade, "Item cardinality"):
            lower(self.d)

    def test_state_field_matching_must_not_change(self):
        self.d["checks"]["home-mounted-nosuid-option"]["expect"]["mount_options"]["values"]["match"] = "all"
        with self.assertRaisesRegex(UnsupportedFacade, "field cardinality"):
            lower(self.d)

    def test_unproven_semantic_alias_not_accepted(self):
        check=self.d["checks"]["home-mounted-nosuid-option"]
        check["expect"]={"suid":{"equals":False,"values":{"exists":"one_or_more","match":"one_or_more"}}}
        with self.assertRaisesRegex(UnsupportedFacade, "required keys"):
            lower(self.d)

    def test_unknown_capability_rejected(self):
        self.d["checks"]["home-mounted-nosuid-option"]["on"] = "linux.fake"
        with self.assertRaisesRegex(UnsupportedFacade, "capability"):
            lower(self.d)

    def test_no_implicit_evaluate(self):
        del self.d["evaluate"]
        with self.assertRaisesRegex(UnsupportedFacade, "required keys"):
            lower(self.d)

    def test_unknown_fields_refused(self):
        self.d["checks"]["home-mounted-nosuid-option"]["default"] = "pass"
        with self.assertRaisesRegex(UnsupportedFacade, "required keys"):
            lower(self.d)

    def test_multiple_checks_refused_instead_of_implicit_and(self):
        self.d["checks"]["second-check"]=deepcopy(self.d["checks"]["home-mounted-nosuid-option"])
        with self.assertRaisesRegex(UnsupportedFacade, "one named check"):
            lower(self.d)

    def test_existence_mode_all_not_collapsed_to_matching(self):
        self.d["checks"]["home-mounted-nosuid-option"]["require"]["items"]["exists"]="all"
        with self.assertRaisesRegex(UnsupportedFacade, "Item cardinality"):
            lower(self.d)

    def test_no_silent_evidence_reduction(self):
        self.d["checks"]["home-mounted-nosuid-option"]["evidence"]["fields"] = "none"
        with self.assertRaisesRegex(UnsupportedFacade, "evidence"):
            lower(self.d)


if __name__=="__main__":
    unittest.main()
