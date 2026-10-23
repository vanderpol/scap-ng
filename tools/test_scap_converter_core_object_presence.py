#!/usr/bin/env python3
"""Positive, mutation and pinned-source checks for native Object-only Tests."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator

from scap_converter_core import convert, postprocess_automated_assessment
from v04_native_bundle_compiler import compile_assessment_program


OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IOS = OD + "#ios"
ID = "oval:sample.ios:def:1"


def source():
    return f'''<oval_definitions xmlns="{OD}" xmlns:ios="{IOS}">
  <definitions><definition id="{ID}" class="miscellaneous" version="1">
    <metadata><title>Check sample section presence</title>
      <description>Check a simple IOS section</description></metadata>
    <criteria operator="AND"><criterion test_ref="oval:sample.ios:tst:1"/></criteria>
  </definition></definitions>
  <tests><ios:section_test id="oval:sample.ios:tst:1" version="1"
      comment="Find matching sections" check="all" check_existence="any_exist">
    <ios:object object_ref="oval:sample.ios:obj:1"/>
  </ios:section_test></tests>
  <objects><ios:section_object id="oval:sample.ios:obj:1" version="1">
    <ios:section_command operation="pattern match">^line vty.*</ios:section_command>
  </ios:section_object></objects>
</oval_definitions>'''.encode()


class ObjectPresenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "oval.xml"

    def conversion(self, original):
        self.path.write_bytes(original)
        return convert(self.path, ID)

    def test_source_verified_may_be_absent_regex_and_compiler(self):
        native, evidence = self.conversion(source())
        a = native["assessment"]
        tid, test = next(iter(a["tests"].items()))
        self.assertEqual(test["object"]["section_command"],
                         {"matches_regex": "^line vty.*"})
        self.assertEqual(test["require"], {"items": "may_be_absent"})
        self.assertEqual(a["evaluate"], {"test": tid})
        program = compile_assessment_program(a)
        self.assertEqual(program["test_instructions"][0]["opcode"],
                         "CHECK_COLLECTION_PRESENCE")
        self.assertFalse(program["scanner_evaluated"])
        self.assertTrue(evidence["v003_source_lowering_reused"])
        self.assertTrue(evidence["original_oval_object_presence_attested"])
        self.assertFalse(evidence["scanner_parity"])
        from pathlib import Path
        import json
        schema = json.loads((Path(__file__).resolve().parents[1] /
                             "schema/v0.4.0/assessment-language.schema.json").read_text())
        self.assertFalse(list(Draft202012Validator(schema).iter_errors(native)))

    def test_other_explicit_source_existence_quantifiers(self):
        for source_existence, items in (
            ("at_least_one_exists", "one_or_more"),
            ("none_exist", "none"),
            ("only_one_exists", "exactly_one"),
        ):
            with self.subTest(existence=source_existence):
                root = ET.fromstring(source())
                next(n for n in root.iter() if n.tag == "{" + IOS + "}section_test").set(
                    "check_existence", source_existence)
                native, _ = self.conversion(ET.tostring(root))
                test = next(iter(native["assessment"]["tests"].values()))
                self.assertEqual(test["require"], {"items": items})

    def test_original_at_least_one_item_check_with_no_states(self):
        root = ET.fromstring(source())
        next(n for n in root.iter() if n.tag == "{" + IOS + "}section_test").set(
            "check", "at least one")
        native, _ = self.conversion(ET.tostring(root))
        self.assertEqual(next(iter(native["assessment"]["tests"].values()))["require"],
                         {"items": "may_be_absent"})

    def test_original_oval_source_mutations_fail_closed(self):
        def set_attr(root, suffix, attribute, value):
            next(x for x in root.iter() if x.tag.endswith("}" + suffix)).set(attribute, value)

        mutants = (
            ("negated criterion", lambda root: set_attr(root, "criterion", "negate", "true")),
            ("unproven existence", lambda root: set_attr(
                root, "section_test", "check_existence", "all_exist")),
            ("unknown Test attribute", lambda root: set_attr(
                root, "section_test", "foo", "bar")),
            ("var_ref selector", lambda root: set_attr(
                root, "section_command", "var_ref", "oval:a:var:1")),
            ("unexpected Object selector", lambda root: next(
                x for x in root.iter() if x.tag.endswith("}section_object")
            ).append(ET.Element("{" + IOS + "}other"))),
            ("wrong original comparator", lambda root: set_attr(
                root, "section_command", "operation", "not equal")),
        )
        for name, mutate in mutants:
            with self.subTest(name=name):
                root = ET.fromstring(source())
                mutate(root)
                with self.assertRaises(ValueError):
                    self.conversion(ET.tostring(root))

    def test_mature_03_graph_corruption_rejected_against_original_xml(self):
        def mutate_lowering(*args, **kwargs):
            aligned, report = postprocess_automated_assessment(*args, **kwargs)
            aligned = deepcopy(aligned)
            obj = next(iter(aligned["assessment"]["objects"].values()))
            obj["select"]["section_command"]["value"] = "^other.*"
            return aligned, report
        with patch("scap_converter_core.postprocess_automated_assessment",
                   side_effect=mutate_lowering):
            with self.assertRaisesRegex(ValueError, "drift"):
                self.conversion(source())

    def test_immutable_external_real_oval_samples_if_available(self):
        for env_name, definition, cap in (
            ("SCAP_NG_ASA_LINE_SOURCE_XML", "oval:org.joval.asa.test:def:6", "asa.line"),
            ("SCAP_NG_IOS_BGP_SOURCE_XML", "oval:org.joval.ios.test:def:1", "ios.bgpneighbor"),
            ("SCAP_NG_IOS_SECTION_SOURCE_XML", "oval:org.joval.ios.test:def:1", "ios.section"),
        ):
            value = os.getenv(env_name)
            if value:
                with self.subTest(source=env_name):
                    native, evidence = convert(Path(value), definition)
                    self.assertEqual(evidence["capability"], cap)
                    expected = "one_or_more" if cap == "asa.line" else "may_be_absent"
                    self.assertEqual(next(iter(native["assessment"]["tests"].values()))["require"],
                                     {"items": expected})


if __name__ == "__main__":
    unittest.main()
