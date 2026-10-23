#!/usr/bin/env python3
"""Pinned AppArmor singleton through mature lowering, never oracle output.

Refs #232 #248.
"""
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

import scap_converter_core as core
from prove_v04_oval_apparmorstatus_source import (
    source_to_native, native_to_oval, SOURCE_DEF, NEW, NAME, SHA, OD,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_v04_public_cli_smoke import schema_valid_docs
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_native_bundle_compiler import build_bundle, verify_bundle


ROOT = Path(__file__).resolve().parents[1]
IDENTITY = "original-linux-apparmorstatus-assessment"


class AppArmorCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Dedicated fast CI supplies this immutable original; absence is a
        # failed prerequisite rather than a silently skipped integration gate.
        cls.source = Path(os.environ["SCAP_NG_APPARMOR_SOURCE_XML"])
        cls.raw = cls.source.read_bytes()
        if sha256(cls.raw).hexdigest() != SHA:
            raise ValueError("pinned original AppArmor source SHA mismatch")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def convert(self):
        return core.convert(self.source, SOURCE_DEF, assessment_id=IDENTITY)

    def test_original_mature_lowering_schema_bundle_and_independent_graph(self):
        with patch.object(core, "lower_definition", wraps=core.lower_definition) as lower:
            native, proof = self.convert()
        lower.assert_called_once()
        self.assertEqual(native, source_to_native(self.raw))
        self.assertEqual(proof["source_sha256"], SHA)
        self.assertEqual(proof["v003_pinned_lowering_sha256"], core.APPARMOR_LOWERING_SHA256)
        self.assertTrue(proof["v003_source_lowering_reused"])
        self.assertTrue(proof["original_oval_apparmor_singleton_integer_state_attested"])
        self.assertFalse(proof["scanner_parity"])
        self.assertFalse(proof["full_oval_coverage"])
        a = native["assessment"]
        self.assertNotIn("objects", a)
        self.assertNotIn("object", a["tests"][NAME])
        self.assertEqual(a["tests"][NAME]["require"], "at_least_one_exists_and_all_match")
        self.assertEqual(a["tests"][NAME]["states"], [{"loaded_profiles_count": {
            "greater_than_or_equal": 0, "datatype": "integer",
            "require": "at_least_one_exists_and_all_match"}}])
        validate_docs({"authoring/apparmor.json": native},
                      _schema_validators(ROOT / "schema/v0.4.0"))
        docs = schema_valid_docs()
        docs["authoring/demo/assessments/a1.json"] = native
        docs["authoring/demo/rules/r1.json"]["rule"]["assessment_choices"]["automated"]["assessment"] = IDENTITY
        bundle, _ = build_bundle(docs, validate_schema=True)
        checked = verify_bundle(bundle, validate_schema=True)
        self.assertEqual((checked["documents"], checked["programs"], checked["tests"]), (3, 1, 1))
        self.assertFalse(checked["scanner_evaluated"])
        exported = self.work / "independently-regenerated.xml"
        native_to_oval(native).write(exported, encoding="utf-8", xml_declaration=True)
        self.assertTrue(compare(self.source, exported, source_root=SOURCE_DEF,
                                regenerated_root=NEW + "def:1", root_only=True)["equal"])

    def test_oracle_is_not_a_production_template_or_lowering_fallback(self):
        with patch("prove_v04_oval_apparmorstatus_source.source_to_native",
                   side_effect=AssertionError("oracle output cannot supply native graph")), \
             patch.object(core, "independent_leaf_import", side_effect=AssertionError("no leaf bypass")):
            native, _ = self.convert()
        self.assertEqual(native, source_to_native(self.raw))
        with patch.object(core, "lower_definition", return_value=(None, "deliberate failure")):
            with self.assertRaisesRegex(ValueError, "0.3 source lowering failed"):
                self.convert()

    def test_default_identity_also_validates(self):
        native, _ = core.convert(self.source, SOURCE_DEF)
        validate_docs({"authoring/apparmor.json": native},
                      _schema_validators(ROOT / "schema/v0.4.0"))
        expected = source_to_native(self.raw)
        expected["assessment"]["id"] = native["assessment"]["id"]
        self.assertEqual(native, expected)

    def test_cli_identity_override_and_evidence(self):
        dest, evidence = self.work / "native.json", self.work / "evidence.json"
        subprocess.run([sys.executable, str(ROOT / "tools/scap_converter_core.py"),
            "--source-xml", str(self.source), "--definition-id", SOURCE_DEF,
            "--assessment-id", "cli-apparmor-assessment", "--output", str(dest),
            "--evidence", str(evidence)], check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(dest.read_text())["assessment"]["id"], "cli-apparmor-assessment")
        self.assertEqual(json.loads(evidence.read_text())["source_sha256"], SHA)

    def test_source_bytes_quantifiers_object_state_and_graph_mutations_fail_closed(self):
        mutations = (
            (b'check="all"', b'check="at least one"'),
            (b'check_existence="at_least_one_exists"', b'check_existence="only_one_exists"'),
            (b'greater than or equal', b'greater than'),
            (b'>0</loaded_profiles_count>', b'>1</loaded_profiles_count>'),
            (b'datatype="int"', b'datatype="string"'),
            (b'<criterion comment=', b'<criterion negate="true" comment='),
            (b'object_ref="oval:com.jovalcm.test:obj:1137"', b'object_ref="oval:missing:obj:1"'),
            (b'comment="The singleton apparmorstatus_object"', b'comment="Changed Object"'),
            (b'</states>', b'</states><variables/>'),
            (b'</objects>', b'<extra_object/></objects>'),
        )
        for old, new in mutations:
            changed = self.raw.replace(old, new, 1)
            self.assertNotEqual(changed, self.raw)
            path = self.work / "mutant.xml"
            path.write_bytes(changed)
            with self.subTest(old=old), patch.object(core, "lower_definition") as lower:
                with self.assertRaisesRegex(ValueError, "source SHA"):
                    core.convert(path, SOURCE_DEF)
                lower.assert_not_called()

    def test_mature_raw_lowering_graph_and_provenance_mutations_rejected(self):
        def assertion(doc):
            return next(iter(doc["assessment"]["tests"].values()))["assertion"]
        mutations = (
            lambda d,p: d["assessment"].update(id="invented-assessment"),
            lambda d,p: assertion(d)["state"].update(value="1"),
            lambda d,p: assertion(d)["state"].update(mask=True),
            lambda d,p: assertion(d).update(item_quantifier="at least one"),
            lambda d,p: assertion(d).update(existence="only_one_exists"),
            lambda d,p: d["assessment"]["evaluate"].update(unproved={}),
            lambda d,p: next(iter(d["assessment"]["collections"].values())).update(select={}),
            lambda d,p: p["source_test_bindings"].clear(),
            lambda d,p: p["source_collection_bindings"].clear(),
        )
        original = core.lower_definition
        for mutate in mutations:
            def corrupt(*args, **kwargs):
                doc, err = original(*args, **kwargs)
                mutate(doc, kwargs["provenance"])
                return doc, err
            with self.subTest(mutation=mutate), patch.object(core, "lower_definition", side_effect=corrupt):
                with self.assertRaisesRegex(ValueError, "lowering graph differs"):
                    self.convert()

    def test_aligned_03_mutations_cannot_be_hidden_by_projection(self):
        def t(d): return next(iter(d["assessment"]["tests"].values()))
        def s(d): return next(iter(d["assessment"]["states"].values()))["state"]
        mutations = (
            lambda d: t(d).update(existence="one"),
            lambda d: t(d).update(match="one_or_more"),
            lambda d: t(d).update(object={}),
            lambda d: t(d).update(states=["missing-state"]),
            lambda d: t(d).update(reported_elements="none"),
            lambda d: t(d).update(capability="linux.partition"),
            lambda d: s(d).update(value=1),
            lambda d: s(d).update(value=False),
            lambda d: s(d).update(datatype="string"),
            lambda d: s(d).update(operation="greater_than"),
            lambda d: s(d).update(field="enforce_mode_profiles_count"),
            lambda d: s(d).update(match="one_or_more"),
            lambda d: s(d).update(existence="optional"),
            lambda d: d["assessment"].update(variables={"hidden-variable": {}}),
            lambda d: d["assessment"].update(objects={"hidden-object": {}}),
            lambda d: d["assessment"].update(evaluate={"not": d["assessment"]["evaluate"]}),
            lambda d: d["assessment"].update(purpose="inventory"),
        )
        original = core.postprocess_automated_assessment
        for mutate in mutations:
            def corrupt(*args, **kwargs):
                doc, report = original(*args, **kwargs)
                doc = deepcopy(doc)
                mutate(doc)
                return doc, report
            with self.subTest(mutation=mutate), patch.object(core, "postprocess_automated_assessment", side_effect=corrupt):
                with self.assertRaises(ValueError):
                    self.convert()

    def test_other_apparmor_source_identity_is_not_newly_supported(self):
        root = ET.fromstring(self.raw)
        root.find("{" + OD + "}definitions")[0].set("id", "oval:unreviewed:def:1")
        path = self.work / "unreviewed.xml"
        path.write_bytes(ET.tostring(root))
        with self.assertRaises(ValueError):
            core.convert(path, "oval:unreviewed:def:1")


if __name__ == "__main__":
    unittest.main()
