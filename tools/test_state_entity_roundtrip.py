#!/usr/bin/env python3
"""Regression: test existence != state entity existence in v003 conversion."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest
from xml.etree import ElementTree as ET

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_ng_roundtrip_v003.native_assessment_to_oval import build

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
UNIX = OD + "#unix"

SOURCE = f"""<oval_definitions xmlns="{OD}" xmlns:unix="{UNIX}">
<definitions><definition id="oval:example:def:1" version="1" class="compliance">
<metadata><title>Entity cardinality</title><description>Test</description></metadata>
<criteria><criterion test_ref="oval:example:tst:1" comment="test"/></criteria>
</definition></definitions>
<tests><unix:file_test id="oval:example:tst:1" version="1"
check="all" check_existence="at_least_one_exists">
<unix:object object_ref="oval:example:obj:1"/>
<unix:state state_ref="oval:example:ste:1"/>
</unix:file_test></tests>
<objects><unix:file_object id="oval:example:obj:1" version="1">
<unix:path>/tmp</unix:path><unix:filename>demo</unix:filename>
</unix:file_object></objects>
<states><unix:file_state id="oval:example:ste:1" version="1">
<unix:filename operation="equals" check_existence="none_exist">demo</unix:filename>
</unix:file_state></states>
</oval_definitions>"""


class StateEntityRoundTripTests(unittest.TestCase):
    def test_native_and_reverse_preserve_independent_existence(self):
        source = ET.fromstring(SOURCE)
        native, error = lower_definition(source, "oval:example:def:1", "entity-cardinality")
        self.assertIsNone(error, error)
        self.assertIsNotNone(native)
        checks = list(native["assessment"]["checks"].values())
        self.assertEqual(len(checks), 1)
        assertion = checks[0]["assert"]
        self.assertEqual(assertion["existence"], "at_least_one_exists")
        self.assertEqual(assertion["state"]["entity_existence"], "none_exist")

        tree, _ = build(native)
        root = tree.getroot()
        test = root.find(f".//{{{UNIX}}}file_test")
        state_entity = root.find(f".//{{{UNIX}}}file_state/{{{UNIX}}}filename")
        self.assertIsNotNone(test)
        self.assertIsNotNone(state_entity)
        self.assertEqual(test.get("check_existence"), "at_least_one_exists")
        self.assertEqual(state_entity.get("check_existence"), "none_exist")

    def test_state_identity_precedes_predicates_in_generated_source(self):
        # Readability is a source-format contract. It MUST NOT alter semantics.
        source = ET.fromstring(SOURCE)
        native, error = lower_definition(source, "oval:example:def:1", "state-order")
        self.assertIsNone(error, error)
        check = next(iter(native["assessment"]["checks"].values()))
        assertion = check["assert"]
        self.assertLess(list(assertion).index("state_title"),
                        list(assertion).index("state"))
        self.assertLess(list(assertion).index("state_capability"),
                        list(assertion).index("state"))
        self.assertEqual(assertion["state_capability"], "unix.file")
        self.assertEqual(assertion["state"]["field"], "filename")

    def test_multiple_state_headers_precede_each_state(self):
        source = ET.fromstring(SOURCE)
        state_node = source.find(f".//{{{UNIX}}}file_state")
        duplicate = ET.fromstring(ET.tostring(state_node, encoding="unicode"))
        duplicate.set("id", "oval:example:ste:2")
        source.find(f".//{{{OD}}}states").append(duplicate)
        test_node = source.find(f".//{{{UNIX}}}file_test")
        ET.SubElement(test_node, f"{{{UNIX}}}state",
                      {"state_ref": "oval:example:ste:2"})
        native, error = lower_definition(source, "oval:example:def:1", "states-order")
        self.assertIsNone(error, error)
        assertion = next(iter(native["assessment"]["checks"].values()))["assert"]
        for item in assertion["states"]:
            self.assertEqual(list(item)[:3],
                             ["state_title", "capability", "state"])

    def test_oval_definition_deprecation_stays_out_of_native_source(self):
        source = ET.fromstring(SOURCE)
        native, error = lower_definition(source, "oval:example:def:1", "active-definition")
        self.assertIsNone(error, error)
        self.assertNotIn("deprecated", native["assessment"])
        source_def = source.find(f".//{{{OD}}}definition")
        source_def.set("deprecated", "false")
        explicit, error = lower_definition(source, "oval:example:def:1", "explicit-false")
        self.assertIsNone(error, error)
        self.assertNotIn("deprecated", explicit["assessment"])
        source_def.set("deprecated", "true")
        rejected, error = lower_definition(source, "oval:example:def:1", "obsolete")
        self.assertIsNone(rejected)
        self.assertEqual(error, "deprecated_oval_definition")

    def test_mixed_test_object_capability_is_rejected(self):
        source = ET.fromstring(SOURCE)
        obj = source.find(f".//{{{UNIX}}}file_object")
        obj.tag = f"{{{UNIX}}}process58_object"
        native, error = lower_definition(source, "oval:example:def:1", "mixed-object")
        self.assertIsNone(native)
        self.assertEqual(
            error,
            "test_collection_capability_mismatch:unix.file!=unix.process58",
        )

    def test_mixed_test_state_capability_is_rejected(self):
        source = ET.fromstring(SOURCE)
        state = source.find(f".//{{{UNIX}}}file_state")
        state.tag = f"{{{UNIX}}}process58_state"
        native, error = lower_definition(source, "oval:example:def:1", "mixed-state")
        self.assertIsNone(native)
        self.assertEqual(
            error,
            "test_state_capability_mismatch:unix.file!=unix.process58",
        )

    def test_required_test_check_is_not_invented(self):
        source = ET.fromstring(SOURCE.replace('check="all" ', ''))
        native, error = lower_definition(source, "oval:example:def:1", "invalid-check")
        self.assertIsNone(native)
        self.assertEqual(error, "invalid_oval_missing_required_test_check")

    def test_state_entity_default_is_explicit_in_native(self):
        source = ET.fromstring(SOURCE.replace(' check_existence="none_exist"', ""))
        native, error = lower_definition(source, "oval:example:def:1", "default-cardinality")
        self.assertIsNone(error, error)
        predicate = next(iter(native["assessment"]["checks"].values()))["assert"]["state"]
        self.assertEqual(predicate["entity_existence"], "at_least_one_exists")
        self.assertEqual(predicate["entity_check"], "all")
        self.assertEqual(predicate["datatype"], "string")
        self.assertEqual(predicate["operation"], "equals")
        self.assertIs(predicate["mask"], False)

    def test_variable_reference_defaults_are_explicit_in_object_and_state(self):
        variable = (
            '<variables><constant_variable id="oval:example:var:1" '
            'version="1" datatype="string" comment="test">'
            '<value>demo</value></constant_variable></variables>'
        )
        source = ET.fromstring(
            SOURCE.replace(
                '<unix:filename>demo</unix:filename>',
                '<unix:filename var_ref="oval:example:var:1"/>',
            ).replace(
                '<unix:filename operation="equals" check_existence="none_exist">demo</unix:filename>',
                '<unix:filename var_ref="oval:example:var:1"/>',
            ).replace('</oval_definitions>', variable + '</oval_definitions>')
        )
        native, error = lower_definition(source, "oval:example:def:1", "variable-defaults")
        self.assertIsNone(error, error)
        assessment = native["assessment"]
        check = next(iter(assessment["checks"].values()))
        selection = check["collect"]["select"]["filename"]
        self.assertEqual(selection["variable_check"], "all")
        self.assertEqual(selection["datatype"], "string")
        self.assertEqual(selection["operation"], "equals")
        self.assertIs(selection["mask"], False)
        self.assertNotIn("entity_existence", selection)
        state = check["assert"]["state"]
        self.assertEqual(state["variable_check"], "all")
        self.assertEqual(state["entity_existence"], "at_least_one_exists")
        self.assertEqual(state["entity_check"], "all")
        self.assertEqual(state["datatype"], "string")

    def test_invalid_source_variable_datatype_is_not_invented(self):
        source = ET.fromstring(
            SOURCE.replace(
                '<unix:path>/tmp</unix:path>',
                '<unix:path var_ref="oval:example:var:1"/>',
            ).replace(
                '</oval_definitions>',
                '<variables><constant_variable id="oval:example:var:1" '
                'version="1" comment="test"><value>/tmp</value>'
                '</constant_variable></variables></oval_definitions>',
            )
        )
        native, error = lower_definition(source, "oval:example:def:1", "invalid-var")
        self.assertIsNone(native)
        self.assertEqual(error, "invalid_oval_missing_required_variable_datatype")


if __name__ == "__main__":
    unittest.main()
