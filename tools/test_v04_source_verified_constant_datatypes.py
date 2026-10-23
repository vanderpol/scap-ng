#!/usr/bin/env python3
"""Previously independent 0.4 datatypes reconciled against v0.3 lowering."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from convert_v04_oval_variable_datatype_suite import convert as original_importer
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.convert_collection_review import postprocess_automated_assessment
from v04_native_bundle_compiler import compile_assessment_program
from v04_source_verified_constant_variable_matrix import project_datatype_suite


CASES = (
    ("SCAP_NG_BOOLEAN_DATATYPE_SOURCE_XML", "oval_boolean_datatype.xml",
     "oval:org.mitre.oval.test:def:709", 8),
    ("SCAP_NG_STRING_DATATYPE_SOURCE_XML", "oval_string_datatype.xml",
     "oval:org.mitre.oval.test:def:252", 10),
    ("SCAP_NG_INT_DATATYPE_SOURCE_XML", "oval_int_datatype.xml",
     "oval:org.mitre.oval.test:def:356", 20),
)


def source_graph(raw, name, did):
    original, proof = original_importer(raw, name)
    provenance = {}
    v003, failure = lower_definition(
        ET.fromstring(raw), did, original["assessment"]["id"],
        collection_graph=True, provenance=provenance)
    if failure is not None:
        raise AssertionError(f"v0.3 lowering failed: {failure}")
    v003, modern = postprocess_automated_assessment(
        v003, target_ng_version="0.3.0")
    if modern is not None:
        raise AssertionError("unexpected v0.3 modernization")
    return original, v003, provenance


class DatatypeReuseTests(unittest.TestCase):
    def setUp(self):
        self.sources = [(Path(os.environ[env]), name, did, n)
                        for env, name, did, n in CASES if env in os.environ]
        if len(self.sources) != 3:
            self.skipTest("original pinned boolean/string/integer sources required")

    def test_full_original_oval_importer_lockstep(self):
        for path, name, did, count in self.sources:
            with self.subTest(source=name):
                raw = path.read_bytes()
                oracle, v003, provenance = source_graph(raw, name, did)
                native = project_datatype_suite(v003, provenance, raw, name)
                self.assertEqual(native, oracle)
                assessment = native["assessment"]
                self.assertEqual(len(assessment["tests"]), count)
                self.assertEqual(len(compile_assessment_program(assessment)["test_instructions"]),
                                 count)
                self.assertIn("and", assessment["evaluate"])
                self.assertTrue(any("and" in branch for branch in
                                    assessment["evaluate"]["and"]))

    def test_corrupt_mature_03_source_value_is_rejected(self):
        for path, name, did, _ in self.sources:
            with self.subTest(source=name):
                raw = path.read_bytes()
                _, v003, provenance = source_graph(raw, name, did)
                changed = deepcopy(v003)
                sample = next(iter(changed["assessment"]["states"].values()))
                sample["state"]["value"] = "not-the-original"
                with self.assertRaisesRegex(ValueError, "scalar State operation/value drift"):
                    project_datatype_suite(changed, provenance, raw, name)

    def test_corrupt_mature_03_criterion_is_rejected(self):
        path, name, did, _ = self.sources[0]
        raw = path.read_bytes()
        _, v003, provenance = source_graph(raw, name, did)
        changed = deepcopy(v003)
        changed["assessment"]["evaluate"]["all"][0]["all"].reverse()
        with self.assertRaisesRegex(ValueError, "criteria lost"):
            project_datatype_suite(changed, provenance, raw, name)

    def test_corrupt_mature_03_variable_is_rejected(self):
        path, name, did, _ = self.sources[0]
        raw = path.read_bytes()
        _, v003, provenance = source_graph(raw, name, did)
        changed = deepcopy(v003)
        v = next(iter(changed["assessment"]["variables"].values()))
        v["expression"]["literal"] = "false"
        with self.assertRaisesRegex(ValueError, "constant literal drift"):
            project_datatype_suite(changed, provenance, raw, name)

    def test_corrupt_original_source_sha_is_rejected(self):
        path, name, did, _ = self.sources[0]
        raw = path.read_bytes()
        _, v003, provenance = source_graph(raw, name, did)
        with self.assertRaisesRegex(ValueError, "immutable original OVAL SHA"):
            project_datatype_suite(v003, provenance, raw + b" ", name)


if __name__ == "__main__":
    unittest.main()
