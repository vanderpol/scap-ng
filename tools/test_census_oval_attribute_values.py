#!/usr/bin/env python3
from pathlib import Path
import tempfile
import unittest
import zipfile

from census_oval_attribute_values import scan_path, scan_xml_bytes


NS="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix"
XML=f"""<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 xmlns:u="{NS}">
 <objects>
  <u:file_object id="oval:test:obj:1" version="1">
   <u:behaviors recurse="files" recurse_direction="up"/>
   <u:path>/etc</u:path><u:filename>passwd</u:filename>
  </u:file_object>
  <u:file_object id="oval:test:obj:2" version="1">
   <u:behaviors recurse_file_system="local"/>
   <u:filepath>/etc/shadow</u:filepath>
  </u:file_object>
 </objects>
</oval_definitions>""".encode()


class OvalAttributeCensusTests(unittest.TestCase):
    def test_counts_only_requested_explicit_attributes(self):
        rows=scan_xml_bytes(
            XML,
            source="synthetic.xml",
            member=None,
            namespace=NS,
            element="behaviors",
            attributes={"recurse","recurse_direction"},
        )
        self.assertEqual(
            {(r["attribute"],r["value"]) for r in rows},
            {("recurse","files"),("recurse_direction","up")},
        )

    def test_xsd_defaults_are_not_invented(self):
        rows=scan_xml_bytes(
            XML,
            source="synthetic.xml",
            member=None,
            namespace=NS,
            element="behaviors",
            attributes={"max_depth"},
        )
        self.assertEqual(rows,[])

    def test_namespace_and_element_scope_are_strict(self):
        rows=scan_xml_bytes(
            b"""<root xmlns:u="http://example.invalid"><u:behaviors recurse="files"/></root>""",
            source="wrong.xml",
            member=None,
            namespace=NS,
            element="behaviors",
            attributes={"recurse"},
        )
        self.assertEqual(rows,[])

    def test_zip_members_are_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"content.zip"
            with zipfile.ZipFile(path,"w") as zf:
                zf.writestr("one.xml",XML)
                zf.writestr("ignore.txt",'recurse="files"')
            rows=scan_path(
                path,
                namespace=NS,
                element="behaviors",
                attributes={"recurse"},
            )
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["member"],"one.xml")


if __name__=="__main__":
    unittest.main()
