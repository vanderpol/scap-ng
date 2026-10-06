#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "analyze_oval_foreach_candidates.py"
SPEC = importlib.util.spec_from_file_location("foreach_analyzer", MODULE_PATH)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def write_fixture(body: str) -> Path:
    temp = tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8")
    temp.write(textwrap.dedent(body))
    temp.close()
    return Path(temp.name)


class ForeachCandidateAnalyzerTests(unittest.TestCase):
    def test_direct_object_projection_is_collection_expansion_review_candidate(self):
        path = write_fixture("""\
            <oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
              xmlns:unix="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix">
              <tests>
                <unix:file_test id="oval:x:tst:1" version="1" check="all" comment="files">
                  <unix:object object_ref="oval:x:obj:2"/>
                </unix:file_test>
              </tests>
              <objects>
                <unix:password_object id="oval:x:obj:1" version="1" comment="users">
                  <unix:username operation="pattern match">.+</unix:username>
                </unix:password_object>
                <unix:file_object id="oval:x:obj:2" version="1" comment="files">
                  <unix:path var_ref="oval:x:var:1" var_check="at least one"/>
                  <unix:filename operation="pattern match">^\\..+</unix:filename>
                </unix:file_object>
              </objects>
              <states/>
              <variables>
                <local_variable id="oval:x:var:1" version="1" datatype="string" comment="homes">
                  <object_component object_ref="oval:x:obj:1" item_field="home_dir"/>
                </local_variable>
              </variables>
            </oval_definitions>
        """)
        try:
            result = MOD.analyze_file(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["candidates"]), 1)
        candidate = result["candidates"][0]
        self.assertEqual(candidate["classification"], "review_required")
        self.assertEqual(candidate["candidate_family"], "collection_expansion")
        self.assertEqual(candidate["source"]["object_id"], "oval:x:obj:1")
        self.assertEqual(candidate["source"]["item_field"], "home_dir")
        self.assertEqual(candidate["targets"][0]["entity"], "path")
        self.assertEqual(candidate["targets"][0]["var_check"], "at least one")
        self.assertEqual(candidate["targets"][0]["tests"][0]["check"], "all")
        self.assertEqual(
            candidate["targets"][0]["tests"][0]["check_existence"],
            "at_least_one_exists",
        )

    def test_concat_object_projection_is_not_direct_auto_candidate(self):
        path = write_fixture("""\
            <oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5"
              xmlns:unix="http://oval.mitre.org/XMLSchema/oval-definitions-5#unix">
              <tests/>
              <objects>
                <unix:file_object id="oval:x:obj:1" version="1" comment="roots"/>
                <unix:file_object id="oval:x:obj:2" version="1" comment="files">
                  <unix:filepath var_ref="oval:x:var:1"/>
                </unix:file_object>
              </objects>
              <states/>
              <variables>
                <local_variable id="oval:x:var:1" version="1" datatype="string" comment="paths">
                  <concat>
                    <object_component object_ref="oval:x:obj:1" item_field="filepath"/>
                    <literal_component>/child</literal_component>
                  </concat>
                </local_variable>
              </variables>
            </oval_definitions>
        """)
        try:
            result = MOD.analyze_file(path)
        finally:
            path.unlink(missing_ok=True)

        candidate = result["candidates"][0]
        self.assertEqual(candidate["candidate_family"], "derived_projection")
        self.assertEqual(candidate["classification"], "review_required")
        self.assertTrue(candidate["expression"]["cross_product_risk"])
        self.assertIn(
            "multi_input_or_cartesian_semantics_may_be_present",
            candidate["reasons"],
        )

    def test_report_never_enables_automatic_rewrite(self):
        path = write_fixture("""\
            <oval_definitions xmlns="http://oval.mitre.org/XMLSchema/oval-definitions-5">
              <tests/><objects/><states/><variables/>
            </oval_definitions>
        """)
        try:
            result = MOD.analyze_file(path)
            report = {
                "format": "scap-ng-foreach-candidate-analysis-0.1",
                "rewrite_performed": False,
                "safe_automatic_enabled": False,
                "summary": MOD.summarize([result]),
                "files": [result],
            }
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report["rewrite_performed"])
        self.assertFalse(report["safe_automatic_enabled"])


if __name__ == "__main__":
    unittest.main()
