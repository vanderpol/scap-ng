#!/usr/bin/env python3
"""Regression of exact OVAL Bluetooth source link extraction."""
import unittest
from audit_v04_bluetooth_oval_source import COMMAND, original_trace, trace_zip

XML = f'''<oval_definitions xmlns:i="http://oval.mitre.org/XMLSchema/oval-definitions-5#independent">
<tests><i:shellcommand_test id="oval:test:2" comment="Report true if Bluetooth installed" check="all">
<object object_ref="oval:obj:2"/></i:shellcommand_test></tests>
<objects>
<i:shellcommand_object id="oval:obj:1"><command>{COMMAND}</command></i:shellcommand_object>
<i:shellcommand_object id="oval:obj:2"><set set_operator="UNION">
<object_reference>oval:obj:1</object_reference><filter action="include">oval:state:1</filter></set></i:shellcommand_object>
</objects>
<states><i:shellcommand_state id="oval:state:1"><stdout_line operation="case insensitive equals">Bluetooth</stdout_line></i:shellcommand_state></states>
</oval_definitions>'''.encode()

class OriginalTraceTests(unittest.TestCase):
    def test_chain_preserves_reference_filter_and_test(self):
        got=original_trace(XML)
        self.assertEqual(len(got["matched_command_objects"]),1)
        self.assertEqual(len(got["related_objects"]),2)
        self.assertEqual(len(got["related_tests"]),1)
        self.assertEqual(len(got["related_states"]),1)
        self.assertEqual(got["source_ovals_object_set_operators"],["UNION"])
        self.assertEqual(got["source_ovals_filter_actions"],["include"])
        self.assertFalse(got["full_scanner_result_parity"])

    def test_missing_exact_command_is_a_failure(self):
        with self.assertRaisesRegex(ValueError, "no Bluetooth"):
            original_trace(XML.replace(b"Get-PnpDevice", b"Get-Nothing"))

    def test_unpinned_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"blob changed"):
            trace_zip(b"fake zip contents")

if __name__=="__main__":
    unittest.main()
