#!/usr/bin/env python3
"""Original IOS/IOS XE multi-Test AND reuses the single-Test State adapter."""
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
    ("SCAP_NG_IOS_LINE_SOURCE_XML", "oval:navy.navwar.niwcatlantic.scc.ios:def:1",
     "ios.line"),
    ("SCAP_NG_IOSXE_LINE_SOURCE_XML", "oval:navy.navwar.niwcatlantic.scc.iosxe:def:1",
     "iosxe.line"),
)
OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"


class MultiStateOriginalTests(unittest.TestCase):
    def setUp(self):
        self.cases = [(Path(os.environ[env]), ident, cap)
                      for env, ident, cap in CASES if env in os.environ]
        if len(self.cases) != 2:
            self.skipTest("CI supplies pinned original IOS and IOS XE State source")

    def test_two_source_states_and_compiled_test_instructions(self):
        for source, ident, capability in self.cases:
            with self.subTest(ident=ident):
                doc, proof = convert(source, ident)
                a = doc["assessment"]
                self.assertEqual(len(a["tests"]), 2)
                self.assertEqual(len(a["evaluate"]["and"]), 2)
                self.assertEqual({t["capability"] for t in a["tests"].values()},
                                 {capability})
                self.assertEqual([list(x["require"]["fields"].values())[0]["matches_regex"]
                                  for x in a["tests"].values()],
                                 [".*http server", ".*"])
                self.assertEqual(len(compile_assessment_program(a)["test_instructions"]), 2)
                self.assertTrue(proof["original_oval_multi_state_and_attested"])
                self.assertTrue(proof["v003_source_lowering_reused"])
                self.assertFalse(proof["scanner_parity"])

    def test_original_oval_structure_mutations_rejected(self):
        source, ident, _ = self.cases[0]
        raw = source.read_bytes()

        def criteria(root):
            return next(x for x in root.iter() if x.tag == "{" + OD + "}criteria")

        def tests(root):
            return [x for x in root.iter() if x.tag.endswith("line_test")]

        mutations = {
            "OR": lambda root: criteria(root).set("operator", "OR"),
            "negate": lambda root: criteria(root)[1].set("negate", "true"),
            "source State operator": lambda root: tests(root)[0].set(
                "state_operator", "OR"),
            "missing source Test reference": lambda root: criteria(root)[0].set(
                "test_ref", "oval:missing:tst:1"),
            "repeated original Test": lambda root: criteria(root)[1].set(
                "test_ref", criteria(root)[0].get("test_ref")),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name), tempfile.TemporaryDirectory() as tmp:
                root = ET.fromstring(raw)
                mutate(root)
                changed = Path(tmp) / "changed.xml"
                changed.write_bytes(ET.tostring(root))
                with self.assertRaises(ValueError):
                    convert(changed, ident)

    def test_corrupted_03_state_compared_against_original_oval(self):
        source, ident, _ = self.cases[0]

        def corrupted(*args, **kwargs):
            v003, report = postprocess_automated_assessment(*args, **kwargs)
            v003 = deepcopy(v003)
            first = next(iter(v003["assessment"]["states"].values()))
            first["state"]["value"] = "unexpected-source-value"
            return v003, report

        with patch("scap_converter_core.postprocess_automated_assessment",
                   side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "State field/existence/check/value mismatch"):
                convert(source, ident)


if __name__ == "__main__":
    unittest.main()
