#!/usr/bin/env python3
"""Current normalized Rule source-default contract. Synthetic independent fixtures."""
import unittest
from scap_upconvert_v003.audit_selector_mapping import audit_normalized_selection


def check(source_order, source_bindings, native_choices, default, **extras):
    return audit_normalized_selection(
        source_order=source_order, source_bindings=source_bindings,
        native_choices={name: {"assessment": "../" + path}
                        for name, path in native_choices.items()},
        native_default=default, **extras)


class SelectorSourceBindingTests(unittest.TestCase):
    A = "assessments/automated/a.yaml"
    M = "assessments/manual/m.yaml"
    B = "assessments/automated/b.yaml"

    def test_source_default_alias_keeps_automated(self):
        errs, lookup = check(
            ["default", "automated", "manual"],
            {"default": self.A, "automated": self.A, "manual": self.M},
            {"automated": self.A, "manual": self.M}, "automated")
        self.assertEqual(errs, [])
        self.assertEqual(lookup["default"], "automated")

    def test_source_default_alias_keeps_manual(self):
        errs, lookup = check(
            ["default", "manual"],
            {"default": self.M, "manual": self.M},
            {"manual": self.M}, "manual")
        self.assertEqual(errs, [])
        self.assertEqual(lookup["default"], "manual")

    def test_unselected_source_default_preserved_under_generated_label(self):
        errs, lookup = check(
            ["default", "automated", "manual"],
            {"default": self.B, "automated": self.A, "manual": self.M},
            {"automated": self.A, "manual": self.M,
             "publisher-automated": self.B}, "publisher-automated")
        self.assertEqual(errs, [])
        self.assertEqual(lookup["default"], "publisher-automated")

    def test_missing_unselected_check_keeps_first_named_method(self):
        errs, lookup = check(
            ["automated", "manual"],
            {"automated": self.A, "manual": self.M},
            {"automated": self.A, "manual": self.M}, "automated")
        self.assertEqual(errs, [])
        self.assertEqual(lookup["manual"], "manual")

    def test_wrong_default_binding_is_detected(self):
        errs, _ = check(
            ["default", "automated", "manual"],
            {"default": self.A, "automated": self.A, "manual": self.M},
            {"automated": self.A, "manual": self.M}, "manual")
        self.assertTrue(any("source default Assessment binding changed" in e for e in errs))

    def test_named_selector_swapped_under_correct_default_is_detected(self):
        errs, _ = check(
            ["default", "automated", "manual"],
            {"default": self.A, "automated": self.A, "manual": self.M},
            {"automated": self.M, "manual": self.A}, "manual")
        self.assertTrue(any("changed Assessment binding" in e for e in errs))

    def test_stale_default_choice_rejected(self):
        errs, _ = check(
            ["default", "automated"],
            {"default": self.A, "automated": self.A},
            {"default": self.A, "automated": self.A}, "default")
        self.assertTrue(any("redundant literal default" in e for e in errs))

    def test_missing_assessment_choice_rejected(self):
        errs, _ = check(
            ["default", "automated", "manual"],
            {"default": self.A, "automated": self.A, "manual": self.M},
            {"automated": self.A}, "automated")
        self.assertTrue(any("missing named native method" in e for e in errs))

    def test_manual_quarantine_is_explicit(self):
        errs, _ = check(
            ["default", "automated", "manual"],
            {"default": self.A, "automated": self.A, "manual": self.M},
            {"manual": self.M}, "manual",
            quarantined=True, omitted_source_selectors=("default", "automated"))
        self.assertEqual(errs, [])

    def test_quarantine_wrong_default_fails(self):
        errs, _ = check(
            ["default", "automated", "manual"],
            {"default": self.A, "automated": self.A, "manual": self.M},
            {"manual": self.M, "automated": self.A}, "automated",
            quarantined=True, omitted_source_selectors=("default", "automated"))
        self.assertTrue(any("fully quarantined" in e for e in errs))

    def test_undocumented_fallback_fails(self):
        errs, _ = check(
            ["default", "automated"],
            {"default": self.A, "automated": self.A},
            {"manual": self.M}, "manual")
        self.assertTrue(errs)

    def test_invalid_binding_paths_fail(self):
        errs, _ = check(
            ["default"], {"default": "../../escaped"},
            {"automated": self.A}, "automated")
        self.assertTrue(any("invalid source Assessment binding" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
