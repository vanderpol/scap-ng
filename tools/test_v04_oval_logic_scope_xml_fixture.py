#!/usr/bin/env python3
"""OVAL 5.12.3 native operator-level scope fixture guards, no scanner."""
from pathlib import Path
import unittest
from lxml import etree
from validate_v04_oval_5123 import check

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND=OD+"#independent"
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"tests/v04-oval-operator-scopes/oval-independent-operators.xml"
SCHEMAS=ROOT/"work/oval-5123/oval-schemas"


class OperatorScopeXsdTests(unittest.TestCase):
    def test_original_fixture_is_oval_root_with_each_operator_at_both_levels(self):
        source=etree.parse(str(FIXTURE))
        tests=source.findall(".//{"+IND+"}shellcommand_test")
        states=source.findall(".//{"+IND+"}shellcommand_state")
        self.assertEqual(len(tests),6)
        self.assertEqual(len(states),6)
        self.assertEqual(len(source.findall(".//{"+OD+"}definition")),6)
        self.assertEqual([t.get("state_operator") for t in tests],
                         ["OR","ONE","XOR","AND","AND","AND"])
        self.assertEqual([s.get("operator") for s in states],
                         ["AND","AND","AND","OR","ONE","XOR"])
        self.assertEqual([[x.get("state_ref") for x in t.findall("{"+IND+"}state")]
                          for t in tests[:3]],
                         [[f"oval:scap-ng.logic-scope:ste:{i}" for i in span]
                          for span in ((1,2),(1,2,3),(1,2,3))])

    def test_real_oval_5123_xsd_accepts_four_distinct_boolean_operators(self):
        if not SCHEMAS.exists():
            self.skipTest("Run in the pinned OVAL 5.12.3 schema checkout workflow")
        result=check(SCHEMAS,FIXTURE,"independent")
        self.assertEqual(result["status"],"PASS",result["diagnostics"])

    def test_oval_xsd_rejects_substituting_any_for_or(self):
        if not SCHEMAS.exists():
            self.skipTest("Run in the pinned OVAL 5.12.3 schema checkout workflow")
        root=etree.parse(str(FIXTURE))
        root.findall(".//{"+IND+"}shellcommand_test")[0].set("state_operator","ANY")
        target=ROOT/"work/oval-5123/invalid-oval-operator.xml"
        target.write_bytes(etree.tostring(root,xml_declaration=True,encoding="utf-8"))
        result=check(SCHEMAS,target,"independent")
        self.assertEqual(result["status"],"FAIL")

    def test_oval_xsd_rejects_substituting_any_for_state_or(self):
        if not SCHEMAS.exists():
            self.skipTest("Run in the pinned OVAL 5.12.3 schema checkout workflow")
        root=etree.parse(str(FIXTURE))
        root.findall(".//{"+IND+"}shellcommand_state")[3].set("operator","ANY")
        target=ROOT/"work/oval-5123/invalid-state-field-operator.xml"
        target.write_bytes(etree.tostring(root,xml_declaration=True,encoding="utf-8"))
        result=check(SCHEMAS,target,"independent")
        self.assertEqual(result["status"],"FAIL")


if __name__=="__main__":
    unittest.main()
