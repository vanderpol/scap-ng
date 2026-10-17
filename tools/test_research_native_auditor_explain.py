#!/usr/bin/env python3
"""Ensure text shown to auditors is generated from the tested policy AST."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_native_contract_candidate import EXAMPLES,read
from research_native_auditor_explain import render

class NativeAuditorExplanationTests(unittest.TestCase):
    def test_all_nine_have_nonempty_explanation(self):
        for file in sorted(EXAMPLES.glob("*.yaml")):
            with self.subTest(file=file.name):
                text=render(read(file))
                self.assertIn("What must be true",text)
                self.assertIn("Source-conversion boundary",text)
                self.assertIn("Evidence and status rules",text)

    def test_filesystem_existence_only_has_no_redundant_property(self):
        explanation=render(read(EXAMPLES/"09-linux-var-tmp-exists.yaml"))
        self.assertIn("At least one Linux mount whose mount point equals /var/tmp must exist.",explanation)
        self.assertNotIn("Required: ",explanation)

    def test_required_home_and_optional_guest_explicit(self):
        required=render(read(EXAMPLES/"01-required-home.yaml"))
        optional=render(read(EXAMPLES/"02-optional-guest.yaml"))
        self.assertIn("At least one matching resource must exist",required)
        self.assertIn("No matching resource is required to exist if selection is confirmed complete.",optional)
        self.assertNotIn("if_empty",required)
        self.assertNotIn("if_empty",optional)

    def test_nested_dns_completeness_and_both_key_types_visible(self):
        text=render(read(EXAMPLES/"08-dns-signing-nested.yaml"))
        for word in ("zone-signing key belonging to the same DNS zone",
                     "key-signing key belonging to the same DNS zone",
                     "between 48 and 168","signed equals true",
                     "At least one matching resource must exist"):
            with self.subTest(word=word):
                self.assertIn(word,text)

    def test_registry_source_contract_visible(self):
        text=render(read(EXAMPLES/"03-named-registry.yaml"))
        self.assertIn("The uniquely identified Windows registry value",text)
        self.assertIn("view=64bit",text)
        self.assertIn("value equals 0",text)

    def test_apache_alternatives_all_visible_and_not_falsely_effective(self):
        text=render(read(EXAMPLES/"04-apache-two-settings.yaml"))
        self.assertIn("ALL of these conditions must hold",text)
        self.assertIn("integer value is at least 100",text)
        self.assertIn("Apache configuration directive observation",text)
        self.assertNotIn("effective Apache setting",text)

    def test_permission_bitmask_means_bit_subset(self):
        text=render(read(EXAMPLES/"07-linux-permission-bits.yaml"))
        self.assertIn("contains only bits allowed by octal 0740",text)
        self.assertNotIn("less than or equal to 0740",text)

    def test_windows_alternatives_are_any_group(self):
        text=render(read(EXAMPLES/"06-windows-privilege-or.yaml"))
        self.assertIn("AT LEAST ONE of these alternatives must hold",text)
        self.assertIn("principal equals Guests",text)
        self.assertIn("principal equals Everyone",text)

if __name__=="__main__":unittest.main()
