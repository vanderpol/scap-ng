#!/usr/bin/env python3
"""Source OVAL 5.12.3 cardinality audit: exact scopes, defaults, dedup."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from research_04_source_oval_macro_census import analyze_package,kind

OVAL='''<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 xmlns:w="http://oval.mitre.org/XMLSchema/oval-definitions-5#windows">
 <tests>
  <w:registry_test id="test:none" check_existence="none_exist" check="only one">
   <w:object object_ref="object:one"/>
  </w:registry_test>
  <w:registry_test id="test:exists" check="all">
   <w:object object_ref="object:two"/>
   <w:state state_ref="state:one"/>
  </w:registry_test>
 </tests>
 <states>
  <w:registry_state id="state:one">
   <w:value entity_check="all" check_existence="at_least_one_exists">0</w:value>
   <w:name>Test</w:name>
  </w:registry_state>
 </states>
</oval_definitions>'''

class SourceTests(unittest.TestCase):
    def test_scope_and_explicitness(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"U_MS_Windows_11_SCAP_1-4_Benchmark.zip"
            with ZipFile(p,"w") as z:
                z.writestr("first.xml",OVAL)
                z.writestr("copy.xml",OVAL)
            r=analyze_package(p)
            m=r["strata"]["structured_other"]
            self.assertEqual(m["tests"],2)
            self.assertEqual(m["state_free_none_exist"],1)
            self.assertEqual(m["state_free_none_original_match:one"],1)
            self.assertEqual(m["items_pair:one_or_more/all"],1)
            self.assertEqual(m["states"],1)
            self.assertEqual(m["state_field_entities"],2)
            self.assertEqual(m["field_name:value"],1)
            self.assertEqual(m["field_name:name"],1)
            self.assertEqual(m["field_name_collision:value"],1)
            self.assertEqual(m.get("states_with_repeated_field_names",0),0)
            self.assertEqual(m["field_pair:one_or_more/all"],2)
            self.assertEqual(m["existence_origin:schema_default"],1)
            self.assertEqual(m["entity_check_origin:schema_default"],1)
            self.assertEqual(r["distinct_source_test_identities"],2)

    def test_deprecated_none_exist_only_when_absence_only(self):
        source=OVAL.replace('check="only one"', 'check="none exist"')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"U_MS_IIS_10-0_Server_SCAP_1-4_Benchmark.zip"
            with ZipFile(path,"w") as archive:
                archive.writestr("oval.xml",source)
            result=analyze_package(path)["strata"]["structured_other"]
            self.assertEqual(result["deprecated_none_exist_check_normalized_state_free"],1)
            self.assertEqual(result["items_pair:none/all"],1)
            self.assertEqual(result["state_free_none_exist"],1)

        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"U_MS_IIS_10-0_Site_SCAP_1-4_Benchmark.zip"
            with ZipFile(path,"w") as archive:
                archive.writestr("oval.xml",source.replace(
                    '<w:object object_ref="object:one"/>',
                    '<w:object object_ref="object:one"/><w:state state_ref="state:one"/>'))
            result=analyze_package(path)["strata"]["structured_other"]
            self.assertEqual(result["deprecated_none_exist_check_unsafe"],1)
            self.assertEqual(result["unresolved_test_pair:none_exist/none exist"],1)
            self.assertEqual(result.get("state_free_none_exist",0),0)

    def test_macos_is_excluded_from_primary(self):
        self.assertEqual(kind("U_Apple_macOS_15_SCAP_1-4_Benchmark.zip",
                              "windows.registry"),"macos_atypical")
        self.assertEqual(kind("U_RHEL_9_SCAP_1-4_Benchmark.zip",
                              "independent.shellcommand"),"shell_command")
        self.assertEqual(kind("U_MS_SQL_Server_2022_SCAP_1-4_Benchmark.zip",
                              "independent.sqlext"),"unsupported_sqlext")

if __name__=="__main__":
    unittest.main()
