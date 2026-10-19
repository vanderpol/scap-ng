#!/usr/bin/env python3
"""#245 Bounded exporter checks with independent authored source XML/Test text."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_oval_self_assertion_bridge import export, original_test_refs, original_source, review_native

OVAL="http://oval.mitre.org/XMLSchema/oval-definitions-5"
UNIX="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix"
XML=f"""<oval_definitions xmlns="{OVAL}" xmlns:unix="{UNIX}">
<definitions>
<definition id="oval:org.example:def:100" version="1" class="miscellaneous">
 <metadata><title>Check retained source comments</title>
 <description>This description is part of source authority.</description></metadata>
 <criteria><criterion comment="Expected result" test_ref="oval:org.example:tst:43" /></criteria>
</definition></definitions>
<tests><unix:file_test id="oval:org.example:tst:43" version="1"
 comment="Exactly one example file must exist." check_existence="only_one_exists"
 check="all" /></tests>
</oval_definitions>"""

def fixture(tmp,stage="equal"):
    root=Path(tmp)
    src=root/"original"
    src.mkdir()
    (src/"file.xml").write_text(XML,encoding="utf-8")
    native=root/"native"
    native.mkdir()
    output=native/"one.native.json"
    output.write_text(json.dumps({"assessment":{"id":"source-id","mode":"automated",
        "tests":{"meaningful-native-test":{
            "test_title":"Exactly one example file must exist.",
            "require":"only_one_exists"}},
        "evaluate":{"test":"meaningful-native-test"}}}),encoding="utf-8")
    report=root/"report.json"
    report.write_text(json.dumps({"results":[{
        "file":"file.xml","definition_id":"oval:org.example:def:100",
        "stage":stage,"equal":stage=="equal",
        **({"native":str(output)} if stage=="equal" else
           {"unsupported_features":[{"feature":"example-gate"}]})
        }],"parse_failures":[]}),encoding="utf-8")
    return src,native,report,root/"converted"

class COVALSourceBridgeTests(unittest.TestCase):
    def test_exact_A_roundtrip_generates_source_pinned_read_only_C_review(self):
        with TemporaryDirectory() as tmp:
            src,native,report,out=fixture(tmp)
            result=export(src,report,native,out)
            self.assertEqual((result["source_definition_count"],result["source_test_count"]), (1,1))
            self.assertEqual((result["A_source_parity_review_definitions"],
                              result["native_0_4_C_converted_definitions"]), (1,0))
            self.assertEqual(result["failed_A_roundtrip_or_unsupported_definitions"],0)
            doc=json.loads((out/result["exported_views"][0]["review_file"]).read_text())
            self.assertEqual(doc["status"],"C_READ_ONLY_SOURCE_REVIEW_A_COMPATIBILITY_FALLBACK")
            self.assertEqual(doc["source"]["definition_title"],"Check retained source comments")
            self.assertEqual(doc["source"]["definition_description"],
                             "This description is part of source authority.")
            self.assertEqual(doc["source"]["original_test_documentation"][0]["comment"],
                             "Exactly one example file must exist.")
            self.assertEqual(doc["source"]["original_test_documentation"][0]["check_existence"],
                             "only_one_exists")
            self.assertEqual(doc["C_read_only_view"]["checks"][
                "exactly-one-example-file-must-exist"]["description"],
                "Exactly one example file must exist.")
            self.assertEqual(doc["A_source_compatibility_fallback"]["evaluate"],
                             {"test":"meaningful-native-test"})
            self.assertFalse(doc["C_read_only_view"]["C_source_independent_compilation_proven"])

    def test_explicit_unsupported_is_counted_never_fabricated_as_conversion(self):
        with TemporaryDirectory() as tmp:
            src,native,report,out=fixture(tmp,stage="lower")
            got=export(src,report,native,out)
            self.assertEqual(got["A_source_parity_review_definitions"],0)
            self.assertEqual(got["native_0_4_C_converted_definitions"],0)
            self.assertEqual(got["failed_A_roundtrip_or_unsupported_definitions"],1)
            self.assertEqual(got["blocked_definitions"][0]["unsupported_features"],
                             [{"feature":"example-gate"}])

    def test_exact_source_inventory_required(self):
        with TemporaryDirectory() as tmp:
            src,native,report,out=fixture(tmp)
            r=json.loads(report.read_text());r["results"]=[]
            report.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,"does not account"):
                export(src,report,native,out)
            r["results"]=[{"file":"file.xml","definition_id":"oval:org.example:def:100",
                           "stage":"equal","equal":True}]
            report.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,"native output"):
                export(src,report,native,out)

    def test_nonexistent_or_untrusted_original_Test_not_accepted(self):
        with TemporaryDirectory() as tmp:
            src,native,report,out=fixture(tmp)
            path=src/"file.xml"
            path.write_text(XML.replace('tst:43" />','tst:99" />'))
            with self.assertRaisesRegex(ValueError,"missing referenced"):
                export(src,report,native,out)
            path.write_text(XML)
            raw=json.loads(report.read_text())
            raw["results"][0]["native"]=str(src/"file.xml")
            report.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError,"escapes roundtrip"):
                export(src,report,native,out)

    def test_internal_name_not_invented_as_original_comment(self):
        with TemporaryDirectory() as tmp:
            src,native,report,out=fixture(tmp)
            a=native/"one.native.json"
            doc=json.loads(a.read_text())
            doc["assessment"]["tests"]["meaningful-native-test"].pop("test_title")
            a.write_text(json.dumps(doc))
            r=export(src,report,native,out)
            view=json.loads((out/r["exported_views"][0]["review_file"]).read_text())
            check=next(iter(view["C_read_only_view"]["checks"].values()))
            self.assertIsNone(check["description"])
            self.assertTrue(check["description_missing"])
            self.assertEqual(view["source"]["original_test_documentation"][0]["comment"],
                             "Exactly one example file must exist.")

    def test_deprecated_criterion_reference_cycle_blocks_safely(self):
        with TemporaryDirectory() as tmp:
            src,native,report,out=fixture(tmp)
            root=ET.parse(src/"file.xml").getroot()
            ns=lambda name:"{"+OVAL+"}"+name
            defs=next(x for x in root if x.tag==ns("definitions"))
            d=defs[0];crit=next(x for x in d if x.tag==ns("criteria"))
            for child in list(crit):crit.remove(child)
            ET.SubElement(crit,ns("extend_definition"),
                          {"definition_ref":d.attrib["id"]})
            ET.ElementTree(root).write(src/"file.xml",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"cyclic extended"):
                export(src,report,native,out)

if __name__=="__main__":
    unittest.main()
