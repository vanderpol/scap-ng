#!/usr/bin/env python3
"""Pinned four-Test OVAL variable source through the shared 0.3 -> 0.4 core.

The external OVAL-Community fixture is fetched at its immutable commit in CI
and is never silently synthesized or substituted. Ref #232 #248 #229.
"""
from __future__ import annotations
from build_v04_canonical_six_stigs import promote
from test_scap_converter_core import legacy_oracle_view
from v04_canonical_source_ir import _schema_validators


from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator

from audit_v04_original_oval_variable_test import IND, tag
from convert_v04_oval_independent_variable_test import convert as independent_convert
from export_v04_oval_independent_variable_test import emit
from scap_converter_core import convert, postprocess_automated_assessment
from scap_ng_roundtrip_v003.compare_oval_semantics import compare as compare_oval
from v04_native_bundle_compiler import compile_assessment_program


SOURCE_SHA256 = "878fa0adc9e27e518fbdac75756b04ef8ed0c9facf937caf98576dc185414b85"
DID = "oval:org.mitre.oval.test:def:538"
SCHEMA = json.loads((Path(__file__).resolve().parents[1] /
                     "schema/v0.4.0/assessment-language.schema.json").read_text())


class MatureVariableLoweringIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.environ.get("SCAP_NG_VARIABLE_SOURCE_XML")
        if not path:
            # The repository-wide smoke runner discovers *every* test module
            # but does not checkout external source. The dedicated converter
            # workflow supplies the pinned file and executes every case.
            raise unittest.SkipTest(
                "pinned OVAL fixture unavailable; dedicated converter workflow must set "
                "SCAP_NG_VARIABLE_SOURCE_XML")
        cls.original = Path(path).read_bytes()
        if sha256(cls.original).hexdigest() != SOURCE_SHA256:
            raise RuntimeError("external pinned OVAL variable fixture SHA256 does not match")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.path = self.directory / "source.xml"
        self.path.write_bytes(self.original)

    def test_four_way_shared_lowering_matches_independent_040_and_compiles(self):
        native, evidence = convert(self.path, DID)
        expected, _ = independent_convert(self.original)
        self.assertEqual(native, promote(expected, legacy_review=True)[0])
        self.assertFalse(list(_schema_validators(Path(__file__).resolve().parents[1] / 'schema/v0.4.0')['assessment'].iter_errors(native)))
        self.assertEqual(evidence["source_sha256"], SOURCE_SHA256)
        self.assertTrue(evidence["v003_source_lowering_reused"])
        self.assertTrue(evidence["independent_variable_import_agreement"])
        self.assertFalse(evidence["scanner_parity"])
        self.assertFalse(evidence["full_oval_coverage"])
        assessment = native["assessment"]
        self.assertEqual(len(assessment["variables"]), 2)
        self.assertEqual(len(assessment["tests"]), 4)
        comparisons = {(t["variable"], t["require"]["fields"]["value"]["equals"]["variable"])
                       for t in assessment["tests"].values()}
        keys = set(assessment["variables"])
        self.assertEqual(comparisons, {(a, b) for a in keys for b in keys})
        for test in assessment["tests"].values():
            self.assertEqual(test["require"]["items_satisfying"], "one_or_more")
            self.assertEqual(test["require"]["fields"]["value"]["value_match"], "one_or_more")
        program = compile_assessment_program(assessment)
        self.assertEqual([t["opcode"] for t in program["test_instructions"]],
                         ["CHECK_ITEM_CONDITION"] * 4)

        # Independently regenerate OVAL from this shared core's result, not
        # the previously validated standalone importer output.
        tree, exported_did = emit(legacy_oracle_view(native))
        exported = self.directory / "regenerated.xml"
        exported.write_bytes(ET.tostring(tree.getroot(), encoding="utf-8"))
        semantic = compare_oval(self.path, exported, source_root=DID,
                                regenerated_root=exported_did, root_only=True)
        self.assertTrue(semantic["equal"], semantic)

    def test_cli_and_authoring_identity_override(self):
        out = self.directory / "converted.json"
        evidence = self.directory / "provenance.json"
        completed = subprocess.run([
            sys.executable, str(Path(__file__).with_name("scap_converter_core.py")),
            "--source-xml", str(self.path), "--definition-id", DID,
            "--assessment-id", "custom-oval-variable-assessment",
            "--output", str(out), "--evidence", str(evidence),
        ], check=True, capture_output=True, text=True)
        self.assertIn("VARIABLE_FOUR_WAY_LOCKSTEP", completed.stdout)
        self.assertEqual(json.loads(out.read_text())["assessment"]["id"],
                         "custom-oval-variable-assessment")
        self.assertTrue(json.loads(evidence.read_text())["v003_source_lowering_reused"])

    def test_source_quantifier_and_comparison_mutations_rejected(self):
        operations = (
            ("state var_check", lambda root: next(node for node in root.iter()
              if node.tag == tag(IND, "value")).set("var_check", "all")),
            ("Test item check", lambda root: next(node for node in root.iter()
              if node.tag == tag(IND, "variable_test")).set("check", "all")),
            ("lost cross-variable pair", lambda root: next(node for node in root.iter()
              if node.tag == tag(IND, "state") and node.get("state_ref")).set(
                "state_ref", "oval:org.mitre.oval.test:ste:1")),
        )
        for label, operation in operations:
            with self.subTest(label=label):
                root = ET.fromstring(self.original)
                operation(root)
                self.path.write_bytes(ET.tostring(root))
                with self.assertRaises(ValueError):
                    convert(self.path, DID)

    def test_corrupt_03_state_binding_is_detected_by_differential(self):
        def corrupted(*args, **kwargs):
            aligned, report = postprocess_automated_assessment(*args, **kwargs)
            aligned = deepcopy(aligned)
            states = list(aligned["assessment"]["states"].values())
            states[0]["state"]["value"]["variable"] = (
                states[1]["state"]["value"]["variable"])
            return aligned, report

        with patch("scap_converter_core.postprocess_automated_assessment",
                   side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "differs"):
                convert(self.path, DID)


if __name__ == "__main__":
    unittest.main()
