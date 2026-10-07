#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import textwrap
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "analyze_oval_foreach_candidates.py"
SPEC = importlib.util.spec_from_file_location("foreach_analyzer", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)

def write_fixture(body: str) -> Path:
    temp = tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8")
    temp.write(textwrap.dedent(body)); temp.close(); return Path(temp.name)

DIRECT = """\
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 xmlns:unix="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix">
 <tests><unix:file_test id="oval:x:tst:1" version="1" check="all" comment="files"><unix:object object_ref="oval:x:obj:2"/></unix:file_test></tests>
 <objects>
  <unix:password_object id="oval:x:obj:1" version="1" comment="users"><unix:username operation="pattern match">.+</unix:username></unix:password_object>
  <unix:file_object id="oval:x:obj:2" version="1" comment="files"><unix:path var_ref="oval:x:var:1" var_check="at least one"/><unix:filename operation="pattern match">^\\..+</unix:filename></unix:file_object>
 </objects><states/>
 <variables><local_variable id="oval:x:var:1" version="1" datatype="string" comment="homes"><object_component object_ref="oval:x:obj:1" item_field="home_dir"/></local_variable></variables>
</oval_definitions>
"""

class ForeachCandidateAnalyzerTests(unittest.TestCase):
    def test_direct_object_projection_is_collection_expansion_review_candidate(self):
        path=write_fixture(DIRECT)
        try: result=MOD.analyze_file(path)
        finally: path.unlink(missing_ok=True)
        candidate=result["candidates"][0]
        self.assertEqual(candidate["classification"],"review_required")
        self.assertEqual(candidate["candidate_family"],"collection_expansion_at_least_one")
        self.assertEqual(candidate["source"]["item_field"],"home_dir")
        self.assertEqual(candidate["targets"][0]["var_check"],"at least one")
        self.assertEqual(candidate["targets"][0]["tests"][0]["check"],"all")
        self.assertTrue(candidate["first_proof_class"]["eligible"])
        self.assertEqual(
            candidate["first_proof_class"]["reasons"],
            [],
        )

    def test_unary_literal_concat_is_recognized_as_bounded_proof_candidate(self):
        path=write_fixture("""\
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 xmlns:ind="http://oval.mitre.org/XMLSchema/oval-definitions-5#independent">
 <tests>
  <ind:textfilecontent54_test id="oval:x:tst:1" version="1" check="all"
    check_existence="at_least_one_exists" comment="lock">
   <ind:object object_ref="oval:x:obj:2"/>
  </ind:textfilecontent54_test>
 </tests>
 <objects>
  <ind:textfilecontent54_object id="oval:x:obj:1" version="1" comment="dbs">
   <ind:filepath>/etc/dconf/profile/user</ind:filepath>
   <ind:pattern operation="pattern match">^system-db:(\\S+)\\s*$</ind:pattern>
   <ind:instance operation="greater than or equal" datatype="int">1</ind:instance>
  </ind:textfilecontent54_object>
  <ind:textfilecontent54_object id="oval:x:obj:2" version="1" comment="locks">
   <ind:path var_ref="oval:x:var:1" var_check="at least one"/>
   <ind:filename operation="pattern match">.*</ind:filename>
   <ind:pattern operation="pattern match">^/org/gnome/example$</ind:pattern>
   <ind:instance operation="greater than or equal" datatype="int">1</ind:instance>
  </ind:textfilecontent54_object>
 </objects><states/>
 <variables>
  <local_variable id="oval:x:var:1" version="1" datatype="string" comment="lock dirs">
   <concat>
    <literal_component>/etc/dconf/db/</literal_component>
    <object_component object_ref="oval:x:obj:1" item_field="subexpression"/>
    <literal_component>.d/locks</literal_component>
   </concat>
  </local_variable>
 </variables>
</oval_definitions>
""")
        try: candidate=MOD.analyze_file(path)["candidates"][0]
        finally: path.unlink(missing_ok=True)
        self.assertEqual(candidate["candidate_family"],"collection_expansion_at_least_one")
        self.assertEqual(candidate["projection_mode"],"unary_literal_concat")
        self.assertEqual(candidate["expression"]["prefix"],"/etc/dconf/db/")
        self.assertEqual(candidate["expression"]["suffix"],".d/locks")
        self.assertEqual(candidate["source"]["item_field"],"subexpression")
        self.assertTrue(candidate["unary_concat_proof_class"]["eligible"])
        self.assertEqual(candidate["unary_concat_proof_class"]["reasons"],[])

    def test_multi_source_concat_remains_cartesian_review_required(self):
        path=write_fixture("""\
<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 xmlns:unix="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix">
<tests/>
<objects>
 <unix:file_object id="oval:x:obj:1" version="1" comment="roots"/>
 <unix:file_object id="oval:x:obj:3" version="1" comment="names"/>
 <unix:file_object id="oval:x:obj:2" version="1" comment="files">
  <unix:filepath var_ref="oval:x:var:1"/>
 </unix:file_object>
</objects><states/>
<variables>
 <local_variable id="oval:x:var:1" version="1" datatype="string" comment="paths">
  <concat>
   <object_component object_ref="oval:x:obj:1" item_field="path"/>
   <literal_component>/</literal_component>
   <object_component object_ref="oval:x:obj:3" item_field="filename"/>
  </concat>
 </local_variable>
</variables>
</oval_definitions>
""")
        try: candidate=MOD.analyze_file(path)["candidates"][0]
        finally: path.unlink(missing_ok=True)
        self.assertEqual(candidate["candidate_family"],"derived_projection")
        self.assertTrue(candidate["expression"]["cross_product_risk"])

    def test_embedded_oval_in_zip_is_analyzed(self):
        datastream=f"""<data-stream-collection xmlns="http://scap.nist.gov/schema/scap/source/1.2"><component id="c1">{DIRECT}</component></data-stream-collection>"""
        temp=tempfile.NamedTemporaryFile(suffix=".zip",delete=False); temp.close(); path=Path(temp.name)
        try:
            with zipfile.ZipFile(path,"w") as z: z.writestr("benchmark.xml",datastream)
            rows=MOD.analyze_input(path)
        finally: path.unlink(missing_ok=True)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["status"],"ok")
        self.assertEqual(rows[0]["families"],{"collection_expansion_at_least_one":1})
        self.assertEqual(
            MOD.summarize(rows)["first_proof_class"],
            {"eligible":1},
        )

    def test_report_never_enables_automatic_rewrite(self):
        path=write_fixture('<oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"><tests/><objects/><states/><variables/></oval_definitions>')
        try: result=MOD.analyze_file(path)
        finally: path.unlink(missing_ok=True)
        report={"rewrite_performed":False,"safe_automatic_enabled":False,"summary":MOD.summarize([result])}
        self.assertFalse(report["rewrite_performed"]); self.assertFalse(report["safe_automatic_enabled"])

if __name__=="__main__":
    unittest.main()
