#!/usr/bin/env python3
import unittest
from lxml import etree

from scap14_rule_splitter import embedded_components, component_kind

DS="http://scap.nist.gov/schema/scap/source/1.2"
CPE="http://cpe.mitre.org/dictionary/2.0"


class ExtendedComponentTests(unittest.TestCase):
    def test_extended_component_is_preserved(self):
        root=etree.fromstring(f"""
        <ds:data-stream-collection xmlns:ds="{DS}" xmlns:cpe="{CPE}">
          <ds:extended-component id="cpe-dict">
            <cpe:cpe-list>
              <cpe:cpe-item name="cpe:/o:example:os">
                <cpe:check system="http://oval.mitre.org/XMLSchema/oval-definitions-5">oval:example:def:1</cpe:check>
              </cpe:cpe-item>
            </cpe:cpe-list>
          </ds:extended-component>
        </ds:data-stream-collection>
        """)
        components,refs=embedded_components(root)
        self.assertIn("cpe-dict",components)
        self.assertEqual(component_kind(components["cpe-dict"]),"cpe-list")
        self.assertEqual(refs,{})


if __name__=="__main__":
    unittest.main()
