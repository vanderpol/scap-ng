#!/usr/bin/env python3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scap_upconvert_v003 import convert_full_review as full


class CpeAliasResolutionTests(unittest.TestCase):
    def test_distinct_cpe_names_have_distinct_native_condition_ids(self):
        first=full.cpe_applicability_id("cpe:/o:microsoft:windows_server_2012")
        second=full.cpe_applicability_id("cpe:/o:microsoft:windows_server_2012:r2")
        self.assertNotEqual(first,second)

    def test_formatted_cpe_alias_maps_to_same_dictionary_item(self):
        legacy="cpe:/o:apple:macos:15.0"
        formatted="cpe:2.3:o:apple:macos:15.0:*:*:*:*:*:*:*"
        root=ET.Element("{http://cpe.mitre.org/dictionary/2.0}cpe-list")
        item=ET.SubElement(root,"{http://cpe.mitre.org/dictionary/2.0}cpe-item",{"name":legacy})
        ET.SubElement(item,"{http://scap.nist.gov/schema/cpe-extension/2.3}cpe23-item",{"name":formatted})
        check=ET.SubElement(item,"{http://cpe.mitre.org/dictionary/2.0}check",{
            "system":"http://oval.mitre.org/XMLSchema/oval-definitions-5",
        })
        check.text="oval:example:def:1"

        with tempfile.TemporaryDirectory() as td:
            package=Path(td)/"sample.zip"
            with zipfile.ZipFile(package,"w") as zf:
                zf.writestr("dictionary.xml",ET.tostring(root,encoding="utf-8"))
            _,dictionary=full.platform_sources(package)

        self.assertIn(legacy,dictionary)
        self.assertIn(formatted,dictionary)
        self.assertIs(dictionary[legacy],dictionary[formatted])
        self.assertEqual(dictionary[formatted].get("name"),legacy)


if __name__=="__main__":
    unittest.main()
