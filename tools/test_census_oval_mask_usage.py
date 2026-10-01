#!/usr/bin/env python3
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from census_oval_mask_usage import scan_xml_bytes, scan_path, build_summary


XML = b"""<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 xmlns:u="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix">
 <objects>
   <u:file_object id="oval:test:obj:1" version="1">
     <u:path mask="false">/etc</u:path>
   </u:file_object>
 </objects>
 <states>
   <u:file_state id="oval:test:ste:1" version="1">
     <u:filename mask="true">passwd</u:filename>
   </u:file_state>
 </states>
</oval_definitions>"""


class MaskCensusTests(unittest.TestCase):
    def test_counts_only_explicit_mask_attributes(self):
        rows = scan_xml_bytes(XML, "synthetic.xml")
        self.assertEqual(len(rows), 2)
        self.assertEqual({r.value for r in rows}, {"true", "false"})
        self.assertEqual({r.section for r in rows}, {"objects", "states"})
        self.assertEqual({r.capability for r in rows}, {"unix"})

    def test_omitted_mask_is_not_counted(self):
        rows = scan_xml_bytes(
            b"""<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
                 xmlns:u="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix">
                 <objects><u:file_object id="x" version="1"><u:path>/tmp</u:path></u:file_object></objects>
               </oval_definitions>""",
            "omitted.xml",
        )
        self.assertEqual(rows, [])

    def test_zip_members_are_scanned(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "content.zip"
            with zipfile.ZipFile(path, "w") as zf:
                zf.writestr("one.xml", XML)
                zf.writestr("ignore.txt", "mask=true")
            rows = scan_path(path)
        self.assertEqual(len(rows), 2)
        self.assertEqual({r.member for r in rows}, {"one.xml"})

    def test_summary_groups_by_value_capability_and_context(self):
        rows = scan_xml_bytes(XML, "synthetic.xml")
        report = build_summary(rows, ["synthetic.xml"])
        self.assertEqual(report["by_value"], {"false": 1, "true": 1})
        self.assertTrue(report["scope"]["source_explicit_only"])
        self.assertTrue(report["scope"]["xsd_default_false_excluded"])
        self.assertEqual(
            {(x["capability"], x["value"], x["count"]) for x in report["by_capability"]},
            {("unix", "false", 1), ("unix", "true", 1)},
        )


if __name__ == "__main__":
    unittest.main()
