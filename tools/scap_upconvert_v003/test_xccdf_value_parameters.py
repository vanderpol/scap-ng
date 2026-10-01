#!/usr/bin/env python3
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scap_upconvert_v003.convert_full_review import (
    render_parameters,
    check_parameter_bindings,
)

X="http://checklists.nist.gov/xccdf/1.2"


class XccdfValueParameterTests(unittest.TestCase):
    def test_value_and_check_export_mapping(self):
        root=ET.fromstring(f"""
        <Benchmark xmlns="{X}">
          <Value id="xccdf_example_value_timeout_var" type="number" operator="less than or equal">
            <description>Maximum timeout.</description>
            <value>600</value>
            <value selector="five_minutes">300</value>
            <value selector="ten_minutes">600</value>
          </Value>
          <Rule id="r1">
            <check system="http://oval.mitre.org/XMLSchema/oval-definitions-5">
              <check-export export-name="oval:example:var:1" value-id="xccdf_example_value_timeout_var"/>
              <check-content-ref href="oval.xml" name="oval:example:def:1"/>
            </check>
          </Rule>
        </Benchmark>
        """)
        parameters,ids=render_parameters(root)
        self.assertEqual(len(parameters),1)
        parameter=parameters[0]
        self.assertEqual(parameter["id"],"timeout_var")
        self.assertEqual(parameter["type"],"number")
        self.assertEqual(parameter["value"],600)
        self.assertEqual(parameter["constraints"]["comparison_operator"],"less than or equal")
        self.assertEqual(
            parameter["constraints"]["choices"],
            [
                {"selector":"five_minutes","value":300},
                {"selector":"ten_minutes","value":600},
            ],
        )
        check=root.find(f".//{{{X}}}check")
        self.assertEqual(
            check_parameter_bindings(check,ids),
            {"oval:example:var:1":"timeout_var"},
        )

    def test_unknown_value_binding_fails_closed(self):
        check=ET.fromstring(f"""
        <check xmlns="{X}">
          <check-export export-name="oval:example:var:1" value-id="missing"/>
        </check>
        """)
        with self.assertRaisesRegex(ValueError,"Unresolved XCCDF Value binding"):
            check_parameter_bindings(check,{})


if __name__=="__main__":
    unittest.main()
