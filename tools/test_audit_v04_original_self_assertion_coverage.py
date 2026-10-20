#!/usr/bin/env python3
"""0.4.0 original Self-Assertion denominator and missing-source regression tests."""
import tempfile
from pathlib import Path
import unittest

from audit_v04_original_self_assertion_coverage import audit


OVAL="http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND=OVAL+"#independent"


def source(test_ref="oval:demo:tst:1", duplicate=False):
    t='<ind:variable_test id="oval:demo:tst:1" version="1" check="all"/>' 
    return f'''<?xml version="1.0"?>
<oval_definitions xmlns="{OVAL}" xmlns:ind="{IND}">
  <definitions><definition id="oval:demo:def:1" version="1" class="compliance">
   <metadata><title>Test one</title></metadata>
   <criteria><criterion test_ref="{test_ref}"/></criteria>
  </definition></definitions>
  <tests>{t}{t if duplicate else ""}</tests>
  <objects><ind:variable_object id="oval:demo:obj:1" version="1"/>
  </objects>
  <states><ind:variable_state id="oval:demo:ste:1" version="1"/></states>
  <variables><constant_variable id="oval:demo:var:1" version="1" datatype="string">
    <value>foo</value></constant_variable></variables>
</oval_definitions>'''


class CoverageLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.target=self.root/"independent"/"variable.xml"
        self.target.parent.mkdir(parents=True)
        self.target.write_text(source())

    def test_entire_source_file_and_test_are_accounted_for_without_false_pass(self):
        report=audit(self.root)
        self.assertEqual(report["summary"]["files"],1)
        self.assertEqual(report["summary"]["definitions"],1)
        self.assertEqual(report["summary"]["tests"],1)
        self.assertEqual(report["summary"]["current_040_converted_and_proven"],0)
        row=report["definitions"][0]
        self.assertEqual(row["referenced_tests"],["oval:demo:tst:1"])
        self.assertEqual(row["oval_xml_semantic_roundtrip"],"NOT_RUN")
        self.assertFalse(report["current_040_semantic_roundtrip_proven"])
        self.assertEqual(sum(report["test_capabilities"].values()),1)

    def test_missing_definition_reference_rejected(self):
        self.target.write_text(source(test_ref="oval:demo:tst:999"))
        with self.assertRaisesRegex(ValueError,"unknown Test"):
            audit(self.root)

    def test_duplicate_test_identity_rejected(self):
        self.target.write_text(source(duplicate=True))
        with self.assertRaisesRegex(ValueError,"duplicate original Test"):
            audit(self.root)

    def test_original_pinned_population_never_silently_shrinks(self):
        with self.assertRaisesRegex(ValueError,"denominator"):
            audit(self.root,assert_pinned=True)


if __name__=="__main__":
    unittest.main()
