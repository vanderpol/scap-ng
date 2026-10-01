#!/usr/bin/env python3
import unittest
import tempfile
import zipfile
from pathlib import Path
from lxml import etree

from scap14_rule_splitter import embedded_components, component_kind, oval_source_roots

DS="http://scap.nist.gov/schema/scap/source/1.2"
CPE="http://cpe.mitre.org/dictionary/2.0"


class ExtendedComponentTests(unittest.TestCase):
    def test_standalone_oval_member_is_discovered(self):
        oval=etree.fromstring(b"""<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"/>""")
        with tempfile.TemporaryDirectory() as td:
            package=Path(td)/"sample.zip"
            with zipfile.ZipFile(package,"w") as zf:
                zf.writestr("inventory.xml",etree.tostring(oval))
            roots=oval_source_roots(package,{})
        self.assertEqual(len(roots),1)
        self.assertEqual(roots[0][0],"zip-member:inventory.xml#oval-1")
        self.assertEqual(component_kind(roots[0][1]),"oval")

    def test_nested_oval_document_is_discovered_from_datastream_xml(self):
        ds=etree.fromstring(f"""
        <ds:data-stream-collection xmlns:ds="{DS}">
          <ds:component id="wrapper">
            <wrapper>
              <oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"/>
            </wrapper>
          </ds:component>
        </ds:data-stream-collection>
        """)
        with tempfile.TemporaryDirectory() as td:
            package=Path(td)/"sample.zip"
            with zipfile.ZipFile(package,"w") as zf:
                zf.writestr("source.xml",etree.tostring(ds))
            roots=oval_source_roots(package,{})
        self.assertEqual(len(roots),1)
        self.assertEqual(component_kind(roots[0][1]),"oval")

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
