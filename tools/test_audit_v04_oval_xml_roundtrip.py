#!/usr/bin/env python3
"""0.4.0 XML->NG->XML differential audit positive and adversarial tests (#248)."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from audit_v04_oval_xml_roundtrip import audit, FORMAT


OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND=OD+"#independent"
OC="http://oval.mitre.org/XMLSchema/oval-common-5"

def oval_xml(*, action="include", value="Bluetooth"):
    # Minimal actual OVAL-namespace graph with a direct original Object Filter
    # and no Set. No claim of XSD validation for this isolated XML fixture.
    return f'''<?xml version="1.0" encoding="utf-8"?>
<oval_definitions xmlns="{OD}" xmlns:ind="{IND}" xmlns:oval="{OC}">
  <definitions>
    <definition id="oval:org.demo:def:1" version="1" class="inventory">
      <metadata><title>Bluetooth installed</title>
      <description>Check installed Bluetooth devices</description></metadata>
      <criteria><criterion test_ref="oval:org.demo:tst:1"/></criteria>
    </definition>
  </definitions>
  <tests><ind:shellcommand_test id="oval:org.demo:tst:1" version="1"
      check="all" check_existence="at_least_one_exists">
    <ind:object object_ref="oval:org.demo:obj:1"/>
  </ind:shellcommand_test></tests>
  <objects><ind:shellcommand_object id="oval:org.demo:obj:1" version="1">
    <ind:shell>powershell</ind:shell>
    <ind:command>(Get-PnpDevice -class bluetooth -status OK).class</ind:command>
    <filter action="{action}">oval:org.demo:ste:1</filter>
  </ind:shellcommand_object></objects>
  <states><ind:shellcommand_state id="oval:org.demo:ste:1" version="1">
    <ind:stdout_line operation="case insensitive equals">{value}</ind:stdout_line>
  </ind:shellcommand_state></states>
</oval_definitions>
'''

def assessment(version="0.4.0"):
    return {"assessment":{"id":"condition.bluetooth-installation.assessment",
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":version},
        "mode":"automated","tests":{
            "report-bluetooth-test":{"capability":"independent.shellcommand",
                "object":{"collect":{"shell":"powershell",
                        "command":"(Get-PnpDevice -class bluetooth -status OK).class"},
                    "filters":[{"include":{"stdout_line":{
                        "case_insensitive_equals":"Bluetooth"}}}]},
                "require":{"items":"one_or_more"}}},
        "evaluate":{"test":"report-bluetooth-test"}}}

class RealXmlRoundtripAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.original=self.root/"original.xml"
        self.output=self.root/"emitted.xml"
        self.native=self.root/"native.json"
        self.original.write_text(oval_xml())
        self.output.write_text(oval_xml())
        self.native.write_text(json.dumps(assessment()))
        self.row={"case_id":"Bluetooth demo","status":"converted",
                  "forward_profile":"0.4.0","reverse_profile":"0.4.0",
                  "source_definition":"oval:org.demo:def:1",
                  "regenerated_definition":"oval:org.demo:def:1"}
        self.update_pins()

    def update_pins(self):
        for kind,file in (("original",self.original),
                          ("regenerated",self.output),
                          ("native_assessment",self.native)):
            self.row[kind]=file.name
            self.row[kind+"_sha256"]=sha256(file.read_bytes()).hexdigest()

    def report(self,*,cases=None,expected=None):
        return audit({"format":FORMAT,"profile":"0.4.0",
                      "cases":cases if cases is not None else [self.row]},
                     self.root,expected=expected)

    def test_identical_oval_semantic_graph_reports_only_xml_parity(self):
        result=self.report(expected=1)
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["outcome_counts"],{"EQUAL":1})
        self.assertFalse(result["cases"][0]["scanner_executed"])
        self.assertFalse(result["cases"][0]["schema_validated"])
        self.assertEqual(result["xsd_validation"],"NOT_RUN")

    def test_filter_action_loss_is_detected_despite_valid_xml(self):
        self.output.write_text(oval_xml(action="exclude"))
        self.update_pins()
        r=self.report()
        self.assertEqual(r["status"],"FAIL")
        self.assertEqual(r["cases"][0]["status"],"DIFFERENT")
        self.assertIn("semantic_diff",r["cases"][0])

    def test_filter_comparison_value_change_is_detected(self):
        self.output.write_text(oval_xml(value="WiFi"))
        self.update_pins()
        r=self.report()
        self.assertEqual(r["cases"][0]["status"],"DIFFERENT")

    def test_original_sha_pin_is_mandatory_and_fail_closed(self):
        self.row["original_sha256"]="0"*64
        r=self.report()
        self.assertEqual(r["cases"][0]["status"],"ERROR")
        self.assertIn("SHA-256",r["cases"][0]["reason"])

    def test_non_v04_authoring_does_not_count_as_pass(self):
        self.native.write_text(json.dumps(assessment(version="0.3.0")))
        self.update_pins()
        self.assertEqual(self.report()["cases"][0]["status"],"ERROR")
        self.row["reverse_profile"]="0.3.0"
        self.assertEqual(self.report()["cases"][0]["status"],"ERROR")

    def test_blocked_definitions_never_count_as_pass(self):
        blocked=deepcopy(self.row)
        blocked["status"]="blocked"
        blocked["blocker"]="Publisher-deprecated Test"
        self.assertEqual(self.report(cases=[blocked])["status"],"FAIL")
        self.assertEqual(self.report(cases=[blocked])["outcome_counts"],{"BLOCKED":1})

    def test_missing_or_duplicate_cases_not_green(self):
        with self.assertRaisesRegex(ValueError,"expected 167"):
            self.report(expected=167)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.report(cases=[self.row,deepcopy(self.row)])

    def test_original_path_not_usable_as_exported_output(self):
        self.row["regenerated"]="original.xml"
        self.row["regenerated_sha256"]=self.row["original_sha256"]
        self.assertEqual(self.report()["cases"][0]["status"],"ERROR")

    def test_missing_definition_or_unparsable_xml_fails_closed(self):
        self.row["source_definition"]="oval:org.demo:def:999"
        self.assertEqual(self.report()["cases"][0]["status"],"ERROR")
        self.row["source_definition"]="oval:org.demo:def:1"
        self.output.write_text("<not-oval/>")
        self.update_pins()
        self.assertEqual(self.report()["cases"][0]["status"],"ERROR")

if __name__=="__main__":
    unittest.main()
