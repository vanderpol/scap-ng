#!/usr/bin/env python3
"""Regression checks for explicit Rule→Policy→Assessment source references."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from build_rhel9_split_policy_review import dump, resolve_source_ref


class ExplicitAuthoringReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "package"
        self.rule = self.root / "rules" / "r.rule.yaml"
        self.policy = self.root / "policies" / "r.policy.yaml"
        self.assessment = self.root / "assessments" / "automated" / "check.assessment.yaml"
        dump(self.rule, {"rule": {"id": "r", "policy": "../policies/r.policy.yaml"}})
        dump(self.policy, {"policy": {"id": "policy.r", "default_check": "automated",
                                       "checks": {"automated": {
                                           "assessment": "../assessments/automated/check.assessment.yaml"
                                       }}}})
        dump(self.assessment, {"assessment": {"id": "check"}})

    def test_explicit_relative_chain_resolves(self):
        self.assertEqual(
            resolve_source_ref(self.root, self.rule, "../policies/r.policy.yaml",
                               "policy", "policy.r"), self.policy.resolve()
        )
        self.assertEqual(
            resolve_source_ref(self.root, self.policy,
                               "../assessments/automated/check.assessment.yaml",
                               "assessment", "check"), self.assessment.resolve()
        )

    def test_wrong_identity_fails_even_when_file_exists(self):
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            resolve_source_ref(self.root, self.policy,
                               "../assessments/automated/check.assessment.yaml",
                               "assessment", "wrong")

    def test_missing_and_absolute_path_fail(self):
        for reference in ("../assessments/missing.yaml", str(self.assessment.resolve())):
            with self.subTest(reference=reference), self.assertRaises(ValueError):
                resolve_source_ref(self.root, self.policy, reference,
                                   "assessment", "check")

    def test_nonportable_and_null_source_paths_are_rejected(self):
        for reference in ("C:/assessment.yaml", "nested" + chr(92) + "file.yaml",
                          "path" + chr(0) + ".yaml"):
            with self.subTest(reference=repr(reference)), self.assertRaisesRegex(
                ValueError, "portable source path"
            ):
                resolve_source_ref(self.root, self.policy, reference,
                                   "assessment", "check")

    def test_wrong_object_kind_fails(self):
        with self.assertRaisesRegex(ValueError, "document type"):
            resolve_source_ref(self.root, self.policy,
                               "../assessments/automated/check.assessment.yaml",
                               "policy", "check")

    def test_escape_and_symlink_escape_fail(self):
        external = Path(self.tmp.name) / "outside.yaml"
        dump(external, {"assessment": {"id": "outside"}})
        for reference in ("../../outside.yaml", "../assessments/automated/escape.yaml"):
            if reference.endswith("escape.yaml"):
                (self.assessment.parent / "escape.yaml").symlink_to(external)
            with self.subTest(reference=reference), self.assertRaisesRegex(ValueError, "escapes"):
                resolve_source_ref(self.root, self.policy, reference,
                                   "assessment", "outside")


if __name__ == "__main__":
    unittest.main()
