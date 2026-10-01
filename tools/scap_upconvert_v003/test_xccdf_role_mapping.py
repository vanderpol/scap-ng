#!/usr/bin/env python3
import unittest

from xccdf_role_mapping import canonicalize_rule_result, map_xccdf_role


class XccdfRoleMappingTests(unittest.TestCase):
    def test_full_executes_and_keeps_technical_outcome(self):
        r=canonicalize_rule_result("full","fail")
        self.assertTrue(r["execute"])
        self.assertTrue(r["scoring_eligible"])
        self.assertEqual(r["technical_outcome"],"fail")

    def test_missing_role_defaults_full(self):
        self.assertEqual(map_xccdf_role(None), map_xccdf_role("full"))

    def test_unscored_executes_but_does_not_erase_truth(self):
        r=canonicalize_rule_result("unscored","fail")
        self.assertTrue(r["execute"])
        self.assertFalse(r["scoring_eligible"])
        self.assertEqual(r["reporting_disposition"],"informational")
        self.assertEqual(r["technical_outcome"],"fail")

    def test_unchecked_does_not_execute(self):
        r=canonicalize_rule_result("unchecked")
        self.assertFalse(r["execute"])
        self.assertFalse(r["scoring_eligible"])
        self.assertEqual(r["technical_outcome"],"not_evaluated")
        self.assertEqual(r["reason"],"policy_unchecked")

    def test_unchecked_rejects_fabricated_assessment_outcome(self):
        with self.assertRaises(ValueError):
            canonicalize_rule_result("unchecked","pass")

    def test_executed_roles_require_technical_outcome(self):
        for role in ("full","unscored"):
            with self.subTest(role=role):
                with self.assertRaises(ValueError):
                    canonicalize_rule_result(role)

    def test_unknown_role_fails_closed(self):
        with self.assertRaises(ValueError):
            map_xccdf_role("mystery")


if __name__=="__main__":
    unittest.main()
