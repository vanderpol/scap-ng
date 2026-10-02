#!/usr/bin/env python3
"""Unknown-Test semantics belong to its capability, not an authored result."""
import copy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

import jsonschema

from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary
from scap_ng_roundtrip_v003.native_assessment_to_oval import build

ROOT = Path(__file__).resolve().parents[1]
OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"


class UnknownTestRoundTripTests(unittest.TestCase):
    def test_source_lowering_schema_and_reverse_preserve_objectless_unknown(self):
        # The pinned independent XSD says check is required but ignored by this
        # capability. Exercise different valid source values without inventing
        # an Object or a predetermined runtime result field.
        for check in ("all", "none satisfy", "only one"):
            with self.subTest(check=check):
                source = ET.fromstring(f'''<oval_definitions xmlns="{OD}" xmlns:i="{IND}">
                <definitions><definition id="oval:example:def:1" version="1" class="compliance">
                <metadata><title>Auditor review</title><description>Unknown implementation</description></metadata>
                <criteria><criterion test_ref="oval:example:tst:1"/></criteria>
                </definition></definitions>
                <tests><i:unknown_test id="oval:example:tst:1" version="1" check="{check}" comment="Auditor review"/></tests>
                </oval_definitions>''')
                native, error = lower_definition(source, "oval:example:def:1", "unknown.fixture", collection_graph=True)
                self.assertIsNone(error)
                aligned = align_assessment_vocabulary(native)
                test = next(iter(aligned["assessment"]["tests"].values()))
                self.assertEqual(test["capability"], "independent.unknown")
                self.assertNotIn("result", test)
                self.assertNotIn("object", test)
                schema = json.loads((ROOT / "schema/v0.1.0/assessment.schema.json").read_text())
                validator = jsonschema.Draft202012Validator(schema)
                validator.validate(aligned)
                leaked = copy.deepcopy(aligned)
                next(iter(leaked["assessment"]["tests"].values()))["result"] = "unknown"
                with self.assertRaises(jsonschema.ValidationError):
                    validator.validate(leaked)
                tree, _ = build(aligned)
                regenerated = tree.getroot().find(f".//{{{IND}}}unknown_test")
                self.assertIsNotNone(regenerated)
                self.assertEqual(list(regenerated), [])
                self.assertIsNone(tree.getroot().find(f"{{{OD}}}objects"))


if __name__ == "__main__":
    unittest.main()
