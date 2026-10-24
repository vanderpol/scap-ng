#!/usr/bin/env python3
"""Pinned real macOS empty singleton Objects with no OVAL State."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scap_converter_core import convert, postprocess_automated_assessment
from v04_native_bundle_compiler import compile_assessment_program


PINNED = (
    ("SCAP_NG_FILEVAULT_SOURCE_XML", "oval:org.joval.test:def:120002",
     "macos.filevault", "83a66de7e3f997cfad206ff33335e28b939717738003329d5c4be0c630e3d22d"),
    ("SCAP_NG_FIRMWAREPASSWORD_SOURCE_XML", "oval:org.joval.test:def:220002",
     "macos.firmwarepassword", "200c768c7add252fb437f3d38b2bcdb839a12b119d1c7af36c82b316d6c01bd2"),
    ("SCAP_NG_PROFILES_SOURCE_XML", "oval:org.joval.test:def:320002",
     "macos.profiles", "21c845bb2076a939d216ca9ea8fa37c1dc783ded7d04a881e274b70df8c6abce"),
)


class SingletonPresenceCoreTests(unittest.TestCase):
    def setUp(self):
        self.sources = [(Path(os.environ[env]), ident, capability, sha)
                        for env, ident, capability, sha in PINNED if env in os.environ]
        if len(self.sources) != len(PINNED):
            self.skipTest("CI supplies three immutable macOS singleton original OVAL files")

    def test_pinned_original_singletons_compile_without_object_or_state(self):
        for path, ident, capability, sha in self.sources:
            with self.subTest(capability=capability):
                raw = path.read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), sha)
                root = ET.fromstring(raw)
                objects = [obj for container in root if container.tag.endswith("objects")
                           for obj in container]
                self.assertEqual(len(objects), 1)
                self.assertEqual(len(objects[0]), 0)
                doc, evidence = convert(path, ident)
                assessment = doc["assessment"]
                self.assertEqual(len(assessment["tests"]), 1)
                test = next(iter(assessment["tests"].values()))
                self.assertEqual(test["capability"], capability)
                self.assertNotIn("object", test)
                self.assertNotIn("states", test)
                self.assertEqual(test["require"], {"items_found": "one_or_more"})
                self.assertTrue(evidence["original_oval_object_presence_attested"])
                program = compile_assessment_program(assessment)
                self.assertEqual(len(program["test_instructions"]), 1)
                self.assertEqual(program["test_instructions"][0]["opcode"],
                                 "CHECK_COLLECTION_PRESENCE")
                self.assertFalse(evidence["scanner_parity"])

    def test_additional_source_object_field_rejected(self):
        path, ident, *_ = self.sources[0]
        root = ET.fromstring(path.read_bytes())
        obj = next(obj for container in root if container.tag.endswith("objects")
                   for obj in container)
        ET.SubElement(obj, obj.tag.rsplit("}", 1)[0] + "}unexpected_selector").text = "x"
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "modified.xml"
            changed.write_bytes(ET.tostring(root))
            with self.assertRaises(ValueError):
                convert(changed, ident)

    def test_original_existence_quantifier_is_preserved(self):
        path, ident, *_ = self.sources[0]
        root = ET.fromstring(path.read_bytes())
        test = next(t for container in root if container.tag.endswith("tests")
                    for t in container)
        test.set("check_existence", "only_one_exists")
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "quantifier.xml"
            changed.write_bytes(ET.tostring(root))
            assessment, _ = convert(changed, ident)
        native_test = next(iter(assessment["assessment"]["tests"].values()))
        self.assertEqual(native_test["require"], {"items_found": "exactly_one"})

    def test_no_unaudited_crosswalk_fallback(self):
        path, ident, capability, _ = self.sources[0]
        real_loads = json.loads

        def removing_crosswalk(contents, *args, **kwargs):
            data = real_loads(contents, *args, **kwargs)
            if (isinstance(data, dict) and data.get("capability") == capability
                    and "object" in data.get("migration_crosswalk", {})):
                data = deepcopy(data)
                del data["migration_crosswalk"]["object"]
            return data

        with patch("v04_source_verified_object_presence.json.loads",
                   side_effect=removing_crosswalk):
            with self.assertRaisesRegex(ValueError, "explicitly declared singleton"):
                convert(path, ident)

    def test_lowered_existence_drift_rejected(self):
        path, ident, *_ = self.sources[0]

        def corrupted(*args, **kwargs):
            doc, report = postprocess_automated_assessment(*args, **kwargs)
            doc = deepcopy(doc)
            test = next(iter(doc["assessment"]["tests"].values()))
            test["existence"] = "one"
            return doc, report

        with patch("scap_converter_core.postprocess_automated_assessment",
                   side_effect=corrupted):
            with self.assertRaisesRegex(ValueError, "Test existence differs"):
                convert(path, ident)


if __name__ == "__main__":
    unittest.main()
