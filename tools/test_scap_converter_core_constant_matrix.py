#!/usr/bin/env python3
"""Shared 0.3 -> native 0.4 integer constant Variable source-lockstep tests."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scap_converter_core import convert, postprocess_automated_assessment
from v04_native_bundle_compiler import compile_assessment_program


CASES = (
    ("SCAP_NG_CONSTANT_VARIABLE_SOURCE_XML", "oval:org.mitre.oval.test:def:92", 2),
    ("SCAP_NG_CHECK_ENUMERATION_SOURCE_XML", "oval:org.mitre.oval.test:def:170", 10),
)


class ConstantVariableMatrixCoreTests(unittest.TestCase):
    def setUp(self):
        self.sources = [(Path(os.getenv(env)), ident, n) for env, ident, n in CASES
                        if os.getenv(env)]
        if len(self.sources) != 2:
            self.skipTest("CI supplies two immutable original OVAL matrix sources")

    def test_original_definitions_compile_and_preserve_var_checks(self):
        for source, ident, count in self.sources:
            with self.subTest(ident=ident):
                doc, proof = convert(source, ident)
                a = doc["assessment"]
                self.assertEqual(len(a["tests"]), count)
                self.assertEqual(len(a["variables"]), 2)
                self.assertEqual(len(a["evaluate"]["and"]), count)
                self.assertTrue(proof["independent_constant_variable_matrix_agreement"])
                self.assertTrue(proof["v003_source_lowering_reused"])
                self.assertFalse(proof["scanner_parity"])
                self.assertTrue(all(isinstance(x, int) for v in a["variables"].values()
                                    for x in v["expression"]["literal"]))
                self.assertEqual(len(compile_assessment_program(a)["test_instructions"]), count)
                if count == 10:
                    matches = {t["require"]["fields"]["value"].get("value_match")
                               for t in a["tests"].values()}
                    self.assertEqual(matches, {"every", "one_or_more", "none", "exactly_one"})
                    self.assertEqual(sum("not" in x for x in a["evaluate"]["and"]), 5)

    def test_alternate_filepath_and_assessment_id(self):
        source, ident, _ = self.sources[0]
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "renamed-original.xml"
            copy.write_bytes(source.read_bytes())
            doc, proof = convert(copy, ident, assessment_id="user-requested-assessment")
            self.assertEqual(doc["assessment"]["id"], "user-requested-assessment")
            self.assertTrue(proof["independent_constant_variable_matrix_agreement"])

    def test_source_checksum_drift_fails_closed(self):
        for source, ident, _ in self.sources:
            with self.subTest(ident=ident), tempfile.TemporaryDirectory() as tmp:
                root = ET.fromstring(source.read_bytes())
                variable = next(node for node in root.iter() if node.tag.endswith("constant_variable"))
                variable[-1].text = "99999"
                copy = Path(tmp) / "changed-source.xml"
                copy.write_bytes(ET.tostring(root))
                with self.assertRaisesRegex(ValueError, "pinned original source SHA"):
                    convert(copy, ident)

    def test_mature_03_value_and_var_check_drift_rejected(self):
        source, ident, _ = self.sources[1]

        def corrupted(*args, **kwargs):
            v003, report = postprocess_automated_assessment(*args, **kwargs)
            v003 = deepcopy(v003)
            states = v003["assessment"]["states"]
            first = next(iter(states.values()))["state"]
            first["value_match"] = "one"  # source var_check was all
            return v003, report

        with patch("scap_converter_core.postprocess_automated_assessment",
                   side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "differs from independent 0.4 OVAL import"):
                convert(source, ident)

    def test_mature_03_variable_literal_drift_rejected(self):
        source, ident, _ = self.sources[0]

        def corrupted(*args, **kwargs):
            v003, report = postprocess_automated_assessment(*args, **kwargs)
            v003 = deepcopy(v003)
            variable = next(iter(v003["assessment"]["variables"].values()))
            variable["expression"]["literal"] = "999"
            return v003, report

        with patch("scap_converter_core.postprocess_automated_assessment",
                   side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "differs from independent 0.4 OVAL import"):
                convert(source, ident)


if __name__ == "__main__":
    unittest.main()
