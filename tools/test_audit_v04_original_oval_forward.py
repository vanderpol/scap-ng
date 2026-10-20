#!/usr/bin/env python3
"""Independent OVAL XML->0.4 source-to-authoring differential regression tests."""
from copy import deepcopy
import unittest
import xml.etree.ElementTree as ET

from audit_v04_original_oval_forward import compare,OD,IND,WIN
from test_export_v04_shellcommand_pilot import native as shell_native
from test_export_v04_registry_pilot import fixture as registry_native


def shell_source(*,with_set=False):
    return f'''<oval_definitions xmlns="{OD}" xmlns:ind="{IND}">
      <definitions><definition id="oval:a:def:1" version="18" class="inventory">
      <metadata><title>Bluetooth</title></metadata><criteria>
      <criterion test_ref="oval:a:tst:1"/></criteria></definition></definitions>
      <tests><ind:shellcommand_test id="oval:a:tst:1" version="18"
            comment="Report true if bluetooth installed"
            check_existence="at_least_one_exists" check="all">
            <ind:object object_ref="oval:a:obj:1"/>
      </ind:shellcommand_test></tests>
      <objects><ind:shellcommand_object id="oval:a:obj:1" version="18"
         comment="Run command: Bluetooth">
         <ind:shell>powershell</ind:shell>
         <ind:command>(Get-PnpDevice -class bluetooth -status OK).class</ind:command>
         <filter action="include">oval:a:ste:1</filter>
         {"<set set_operator='UNION'/>" if with_set else ""}
      </ind:shellcommand_object></objects>
      <states><ind:shellcommand_state id="oval:a:ste:1" version="18">
         <ind:stdout_line operation="case insensitive equals">Bluetooth</ind:stdout_line>
      </ind:shellcommand_state></states>
    </oval_definitions>'''.encode()


def registry_source():
    return f'''<oval_definitions xmlns="{OD}" xmlns:win="{WIN}">
      <definitions><definition id="oval:b:def:1" version="18" class="compliance">
      <metadata><title>Bluetooth off</title></metadata><criteria>
      <criterion test_ref="oval:b:tst:1"/></criteria></definition></definitions>
      <tests><win:registry_test id="oval:b:tst:1" version="18"
         comment="Bluetooth radio must be turned off." check="only one"
         check_existence="at_least_one_exists">
        <win:object object_ref="oval:b:obj:1"/>
        <win:state state_ref="oval:b:ste:1"/>
      </win:registry_test></tests>
      <objects><win:registry_object id="oval:b:obj:1" version="18"
         comment="Verify the Bluetooth radio is turned off">
        <win:hive>HKEY_LOCAL_MACHINE</win:hive>
        <win:key>SOFTWARE\\Microsoft\\PolicyManager\\current\\device\\Connectivity</win:key>
        <win:name>AllowBluetooth</win:name>
      </win:registry_object></objects>
      <states><win:registry_state id="oval:b:ste:1" version="18">
         <win:value operation="equals">0</win:value>
      </win:registry_state></states>
    </oval_definitions>'''.encode()


class NativeSourceComparisonTests(unittest.TestCase):
    def test_shell_test_and_original_filter_match(self):
        native=shell_native()
        self.assertEqual(compare(shell_source(),native,"oval:a:def:1")["source_filter_count"],1)

    def test_reject_original_source_set_not_present_in_ng(self):
        with self.assertRaisesRegex(ValueError,"genuine OVAL Set"):
            compare(shell_source(with_set=True),shell_native(),"oval:a:def:1")

    def test_reject_changed_forward_filter_value_and_missing_predicate(self):
        for mutate in (
            lambda x:x["assessment"]["tests"]["bluetooth-test"]["object"]["filters"][0]["include"]["stdout_line"].update(case_insensitive_equals="Camera"),
            lambda x:x["assessment"]["tests"]["bluetooth-test"]["object"].pop("filters"),
            lambda x:x["assessment"]["tests"]["bluetooth-test"]["object"].update(set={"operator":"union","operands":[]}),
            lambda x:x["assessment"]["tests"]["bluetooth-test"].update(require={"items":"none"}),
        ):
            d=shell_native()
            with self.subTest(change=str(mutate)),self.assertRaises(ValueError):
                mutate(d)
                compare(shell_source(),d,"oval:a:def:1")

    def test_registry_original_hive_and_state_exact(self):
        self.assertEqual(compare(registry_source(),registry_native(),"oval:b:def:1")["source_filter_count"],0)
        bad=registry_native()
        bad["assessment"]["tests"]["bluetooth-registry-test"]["states"][0]["value"]["equals"]="1"
        with self.assertRaisesRegex(ValueError,"State"):
            compare(registry_source(),bad,"oval:b:def:1")

    def test_original_oval_bad_test_binding_cannot_be_ignored(self):
        root=ET.fromstring(shell_source())
        c=next(n for n in root.iter() if n.tag=="{"+OD+"}criterion")
        c.set("test_ref","oval:a:tst:999")
        with self.assertRaisesRegex(ValueError,"missing or duplicated"):
            compare(ET.tostring(root),shell_native(),"oval:a:def:1")


if __name__=="__main__":
    unittest.main()
