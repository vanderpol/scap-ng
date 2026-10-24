#!/usr/bin/env python3
"""Pinned family regex Variable OVAL -> maintained 0.3 lowering -> 0.4 core."""
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

from convert_v04_oval_family_constant_variable import (
    convert as independent_family_import, INDEPENDENT, q,
)
from export_v04_oval_family_constant_variable import emit
from scap_converter_core import convert, postprocess_automated_assessment
from scap_ng_roundtrip_v003.compare_oval_semantics import compare as compare_oval
from v04_native_bundle_compiler import compile_assessment_program


PIN_SHA256 = "6966982d66e004f77ceb9e5ccceb5161275a79729d4178f290f99efd3b8b84a7"
DID = "oval:org.mitre.oval.test:def:95"
SCHEMA = json.loads((Path(__file__).resolve().parents[1] /
                     "schema/v0.4.0/assessment-language.schema.json").read_text())


class MatureFamilyVariableIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = os.environ.get("SCAP_NG_FAMILY_SOURCE_XML")
        if not source:
            raise unittest.SkipTest("pinned family OVAL unavailable; dedicated converter workflow "
                                    "must set SCAP_NG_FAMILY_SOURCE_XML")
        cls.raw = Path(source).read_bytes()
        if sha256(cls.raw).hexdigest() != PIN_SHA256:
            raise RuntimeError("external pinned family OVAL fixture SHA256 changed")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.src = self.dir / "family.xml"
        self.src.write_bytes(self.raw)

    def test_mature_source_and_independent_importer_match_schema_compiler_roundtrip(self):
        native, evidence = convert(self.src, DID)
        expected, _ = independent_family_import(self.src)
        self.assertEqual(native, promote(expected, legacy_review=True)[0])
        self.assertFalse(list(_schema_validators(Path(__file__).resolve().parents[1] / 'schema/v0.4.0')['assessment'].iter_errors(native)))
        self.assertTrue(evidence["v003_source_lowering_reused"])
        self.assertTrue(evidence["independent_family_import_agreement"])
        self.assertFalse(evidence["scanner_parity"])
        self.assertFalse(evidence["full_oval_coverage"])
        a = native["assessment"]
        test = a["tests"]["system-family-matches-test"]
        self.assertEqual(test["require"]["items_satisfying"], "one_or_more")
        self.assertEqual(test["require"]["fields"]["family"]["value_match"], "every")
        self.assertEqual(test["require"]["fields"]["family"]["values_matching"],
                         "every")
        compiled = compile_assessment_program(a)
        self.assertEqual(compiled["test_instructions"][0]["opcode"],
                         "CHECK_ITEM_CONDITION")
        tree, exported_did = emit(legacy_oracle_view(native))
        exported = self.dir / "regenerated.xml"
        exported.write_bytes(ET.tostring(tree.getroot(), encoding="utf-8"))
        comparison = compare_oval(self.src, exported, source_root=DID,
                                  regenerated_root=exported_did, root_only=True)
        self.assertTrue(comparison["equal"], comparison)

    def test_cli_assessment_identity_override(self):
        dest = self.dir / "family.json"
        result = subprocess.run([
            sys.executable, str(Path(__file__).with_name("scap_converter_core.py")),
            "--source-xml", str(self.src), "--definition-id", DID,
            "--assessment-id", "custom-family-assessment", "--output", str(dest),
        ], capture_output=True, text=True, check=True)
        self.assertIn("FAMILY_VARIABLE_LOCKSTEP", result.stdout)
        self.assertEqual(json.loads(dest.read_text())["assessment"]["id"],
                         "custom-family-assessment")

    def test_source_mutations_rejected(self):
        mutations = (
            ("State var_check", lambda root: next(x for x in root.iter()
              if x.tag == q(INDEPENDENT, "family") and x.get("var_ref")).set(
                  "var_check", "at least one")),
            ("State operation", lambda root: next(x for x in root.iter()
              if x.tag == q(INDEPENDENT, "family") and x.get("var_ref")).set(
                  "operation", "equals")),
            ("Test check", lambda root: next(x for x in root.iter()
              if x.tag == q(INDEPENDENT, "family_test")).set("check", "all")),
            ("wrong Variable reference", lambda root: next(x for x in root.iter()
              if x.tag == q(INDEPENDENT, "family") and x.get("var_ref")).set(
                  "var_ref", "oval:unresolved:var:999")),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                root = ET.fromstring(self.raw)
                mutate(root)
                self.src.write_bytes(ET.tostring(root))
                with self.assertRaises(ValueError):
                    convert(self.src, DID)

    def test_mutated_03_regex_binding_fail_closed(self):
        def corrupt(*args, **kwargs):
            result, modern = postprocess_automated_assessment(*args, **kwargs)
            result = deepcopy(result)
            s = next(iter(result["assessment"]["states"].values()))["state"]
            s["value_match"] = "one_or_more"
            return result, modern

        with patch("scap_converter_core.postprocess_automated_assessment", side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, "var_check"):
                convert(self.src, DID)


if __name__ == "__main__":
    unittest.main()
