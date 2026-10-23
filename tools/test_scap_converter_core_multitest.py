#!/usr/bin/env python3
"""Original OVAL AND with multiple no-State Objects -> maintained native 0.4."""
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


OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IOS = OD + "#ios"
ID = "oval:sample.ios:def:17"


def source():
    return f'''<oval_definitions xmlns="{OD}" xmlns:ios="{IOS}">
  <definitions><definition id="{ID}" version="1" class="compliance">
    <metadata><title>Verify two IOS settings</title><description>Two direct checks</description></metadata>
    <criteria operator="AND">
      <criterion test_ref="oval:sample.ios:tst:1"/>
      <criterion test_ref="oval:sample.ios:tst:2"/>
    </criteria>
  </definition></definitions>
  <tests>
    <ios:global_test id="oval:sample.ios:tst:1" version="1"
      comment="Expect first global command" check="all"
      check_existence="at_least_one_exists">
      <ios:object object_ref="oval:sample.ios:obj:1"/>
    </ios:global_test>
    <ios:global_test id="oval:sample.ios:tst:2" version="1"
      comment="Expect second global command" check="all"
      check_existence="at_least_one_exists">
      <ios:object object_ref="oval:sample.ios:obj:2"/>
    </ios:global_test>
  </tests>
  <objects>
    <ios:global_object id="oval:sample.ios:obj:1" version="1">
      <ios:global_command>boot-start-marker</ios:global_command>
    </ios:global_object>
    <ios:global_object id="oval:sample.ios:obj:2" version="1">
      <ios:global_command operation="pattern match">service timestamps</ios:global_command>
    </ios:global_object>
  </objects>
</oval_definitions>'''.encode()


class MultiDirectPresenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "test.xml"

    def convert(self, raw):
        self.path.write_bytes(raw)
        return convert(self.path, ID)

    def test_source_exact_two_test_and_compiles(self):
        doc, evidence = self.convert(source())
        assessment = doc["assessment"]
        tests = list(assessment["tests"].values())
        self.assertEqual(len(tests), 2)
        self.assertEqual(tests[0]["object"]["global_command"],
                         {"equals": "boot-start-marker"})
        self.assertEqual(tests[1]["object"]["global_command"],
                         {"matches_regex": "service timestamps"})
        self.assertEqual(len(assessment["evaluate"]["and"]), 2)
        self.assertTrue(evidence["original_oval_multi_direct_and_attested"])
        self.assertTrue(evidence["v003_source_lowering_reused"])
        self.assertFalse(evidence["scanner_parity"])
        compiled = compile_assessment_program(assessment)
        self.assertEqual(len(compiled["test_instructions"]), 2)
        self.assertEqual({x["opcode"] for x in compiled["test_instructions"]},
                         {"CHECK_COLLECTION_PRESENCE"})

    def test_or_negation_uncommon_check_and_shared_object_rejected(self):
        def test_xml(mutate):
            root = ET.fromstring(source())
            mutate(root)
            with self.assertRaises(ValueError):
                self.convert(ET.tostring(root))

        def criteria(root):
            return next(x for x in root.iter() if x.tag == "{" + OD + "}criteria")
        def test2(root):
            return next(x for x in root.iter() if x.get("id") == "oval:sample.ios:tst:2")
        mutations = (
            ("OR", lambda root: criteria(root).set("operator", "OR")),
            ("negated criterion", lambda root: criteria(root)[1].set("negate", "true")),
            ("unsupported check", lambda root: test2(root).set("check", "only one")),
            ("shared Object", lambda root: test2(root)[0].set(
                "object_ref", "oval:sample.ios:obj:1")),
            ("unreviewed State", lambda root: ET.SubElement(
                test2(root), "{" + IOS + "}state", {"state_ref": "oval:sample.ios:ste:2"})),
        )
        for name, mutate in mutations:
            with self.subTest(name=name):
                test_xml(mutate)

    def test_mature_03_selector_drift_caught_against_original(self):
        def mutate_lowering(*args, **kwargs):
            result, report = postprocess_automated_assessment(*args, **kwargs)
            result = deepcopy(result)
            objects = result["assessment"]["objects"]
            next(iter(objects.values()))["select"]["global_command"]["value"] = "bogus"
            return result, report
        with patch("scap_converter_core.postprocess_automated_assessment",
                   side_effect=mutate_lowering):
            with self.assertRaisesRegex(ValueError, "drift"):
                self.convert(source())

    def test_immutable_real_ios_global_source_if_available(self):
        path = os.getenv("SCAP_NG_IOS_GLOBAL_SOURCE_XML")
        if not path:
            self.skipTest("CI supplies pinned original IOS global source")
        native, evidence = convert(Path(path),
                                   "oval:navy.navwar.niwcatlantic.scc.ios:def:1")
        self.assertEqual(len(native["assessment"]["tests"]), 2)
        self.assertTrue(evidence["original_oval_multi_direct_and_attested"])


if __name__ == "__main__":
    unittest.main()
