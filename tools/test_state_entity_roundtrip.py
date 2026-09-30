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

    def test_required_test_check_is_not_invented(self):
        source = ET.fromstring(SOURCE.replace('check="all" ', ''))
        native, error = lower_definition(source, "oval:example:def:1", "invalid-check")
        self.assertIsNone(native)
        self.assertEqual(error, "invalid_oval_missing_required_test_check")

    def test_default_absence_remains_unmaterialized_in_native(self):
        source = ET.fromstring(SOURCE.replace(' check_existence="none_exist"', ""))
        native, error = lower_definition(source, "oval:example:def:1", "default-cardinality")
        self.assertIsNone(error, error)
        predicate = next(iter(native["assessment"]["checks"].values()))["assert"]["state"]
        self.assertNotIn("entity_existence", predicate)


if __name__ == "__main__":
    unittest.main()
