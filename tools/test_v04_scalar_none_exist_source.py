#!/usr/bin/env python3
"""Source-backed absence-only State field grammar regression. Refs #248 #229."""
from __future__ import annotations

import os
from pathlib import Path
import unittest

from prove_v04_oval_macos_gatekeeper_source import (
    NAME, CAPABILITY, source_to_native,
)
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get(
    "OVAL_GATEKEEPER_SOURCE",
    str(ROOT.parent / "SCAP-Self-Assertion/SCAP_1.4/OVAL_Test_Content/macos/macos-def_gatekeeper_test.xml")))


def sample():
    return source_to_native(SOURCE.read_bytes())


class MacosNoneExistSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validators = _schema_validators(ROOT / "schema/v0.4.0")
        cls.capability = materialize(CAPABILITY)

    def check(self, doc):
        try:
            validate_docs({"source-backed-gatekeeper.json": doc}, self.validators)
        except ValueError:
            generic = False
        else:
            generic = True
        test = doc["assessment"]["tests"][NAME]
        generated = not validate(self.capability, "test", test)
        self.assertEqual(generic, generated, "generic/capability contract disagreement")
        return generic

    def test_original_absence_only_field_passes(self):
        self.assertTrue(self.check(sample()))

    def test_absence_only_field_cannot_require_matches(self):
        doc = sample()
        doc["assessment"]["tests"][NAME]["states"][0]["and"][1][
            "unlabeled"]["require"] = "at_least_one_exists_and_all_match"
        self.assertFalse(self.check(doc))

    def test_absence_only_field_cannot_use_inapplicable_datatype(self):
        doc = sample()
        doc["assessment"]["tests"][NAME]["states"][0]["and"][1][
            "unlabeled"]["datatype"] = "string"
        self.assertFalse(self.check(doc))

    def test_required_comparator_still_enforced_elsewhere(self):
        doc = sample()
        doc["assessment"]["tests"][NAME]["states"][0]["and"][0][
            "enabled"].pop("equals")
        self.assertFalse(self.check(doc))


if __name__ == "__main__":
    unittest.main()
