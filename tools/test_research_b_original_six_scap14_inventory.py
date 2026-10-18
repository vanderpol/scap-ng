#!/usr/bin/env python3
"""#237 original 1.4 source archive pin, OVAL family/count and view integrity."""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_original_six_scap14_inventory import (
    archive_scan,inventory,markdown,FILES,REVISION,KNOWN_SHA,
)

XML=b'''<?xml version="1.0" encoding="UTF-8"?>
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
  xmlns:oval="http://oval.mitre.org/XMLSchema/oval-common-5"
  xmlns:win="http://oval.mitre.org/XMLSchema/oval-definitions-5#windows">
  <generator><oval:schema_version>5.12.3</oval:schema_version></generator>
  <definitions><definition id="oval:example:def:1"/></definitions>
  <tests><win:registry_test id="oval:example:tst:1"/></tests>
  <objects>
    <win:registry_object id="oval:example:obj:1">
      <win:hive>HKEY_LOCAL_MACHINE</win:hive>
      <win:key operation="case insensitive equals">Software\\Example</win:key>
      <win:name operation="case insensitive equals">Key</win:name>
    </win:registry_object>
  </objects>
  <states><win:registry_state id="oval:example:ste:1"/></states>
  <variables>
    <local_variable id="oval:example:var:1"><merge delimiter=" " sort="document"/></local_variable>
  </variables>
</oval_definitions>'''


class OriginalSourceInventoryTests(unittest.TestCase):
    def make_zip(self,path,raw=XML):
        with zipfile.ZipFile(path,"w") as z:
            z.writestr("scap-original.xml",raw)
            z.writestr("README.txt","archived source; do not execute")
        return path

    def test_real_source_manifest_six_known_pinned_names(self):
        self.assertEqual(len(FILES),6)
        self.assertEqual(len(set(FILES.values())),6)
        self.assertEqual(len(REVISION),40)
        self.assertEqual(set(KNOWN_SHA),{
            "rhel_9","ms_windows_server_2025",
            "ms_windows_server_dns","apache_server_2-4_unix_server"})

    def test_original_oval_source_objects_and_case_insensitive_operator(self):
        with TemporaryDirectory() as temp:
            path=self.make_zip(Path(temp)/"sample.zip")
            record=archive_scan(path)
            self.assertEqual(record["oval_xml_documents"],1)
            self.assertEqual(record["declarations"]["definitions"],1)
            self.assertEqual(record["declarations"]["tests"],1)
            self.assertEqual(record["declarations"]["variables"],1)
            self.assertEqual(record["registry_views"],{"source_omitted":1})
            self.assertEqual(record["registry_key_name_selector_operations"],{
                "key:case insensitive equals":1,"name:case insensitive equals":1})
            self.assertEqual(record["merge_sort_forms"],{"sort=document;order=ascending":1})
            self.assertEqual(record["oval_schema_versions"],{"5.12.3":1})
            self.assertFalse(record["scanner_execution_verified"])

    def test_wrong_sha_and_missing_archive_rejected(self):
        with TemporaryDirectory() as temp:
            path=self.make_zip(Path(temp)/"x.zip")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                archive_scan(path,expected_sha="0"*64)
            with self.assertRaisesRegex(ValueError,"missing pinned"):
                archive_scan(Path(temp)/"missing.zip")

    def test_all_stream_archives_required_and_separate_from_conversions(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            for name in FILES.values():
                self.make_zip(root/name)
            # Avoid substituting synthetic fixture zips for real pins.
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                inventory(root)
            self.assertIn("not",markdown({
                "git_revision":REVISION,
                "streams":{"fixture":{
                  "declarations":{"tests":1,"objects":1},
                  "oval_xml_documents":1,"zip_sha256":"bad"}}}))


if __name__=="__main__":
    unittest.main()
