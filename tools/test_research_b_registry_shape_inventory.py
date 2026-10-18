#!/usr/bin/env python3
"""#237 census guard: overlapping source registry Tests not inflated into Assessments."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_registry_shape_inventory import inventory,markdown


def capsule(aid,tests,mode="automated",evaluate=None):
    return {"source_path":"authoring/"+aid+".yaml",
            "source_document":{"assessment":{
                "id":aid,"mode":mode,"tests":tests,
                "evaluate":evaluate if evaluate is not None else {"test":next(iter(tests),"")} }}}


def registry(value="0",op="equals"):
    return {"capability":"windows.registry","existence":"one_or_more",
            "match":"one","object":{"capability":"windows.registry",
             "select":{"hive":"local_machine",
                       "key":{"operation":"equals","value":"SOFTWARE\\Sample"},
                       "name":{"operation":"equals","value":"Setting"}}},
            "states":[{"field":"value","operation":op,"value":value,
                       "existence":"one_or_more","match":"all"}]}


class RegistryCensusTests(unittest.TestCase):
    def test_test_and_assessment_count_are_distinct(self):
        a=capsule("a",{"t1":registry(),"t2":registry(0)})
        b=capsule("b",{"t1":registry(op="pattern_match")})
        m=capsule("m",{"nothing":registry()},mode="manual")
        r=inventory({"a":a,"b":b,"m":m})
        self.assertEqual(r["distinct_referenced_assessments"],2)
        self.assertEqual(r["registry_test_nodes"],3)
        self.assertEqual(r["dimensions"]["state=value/equals/one_or_more/all/string"],1)
        self.assertEqual(r["dimensions"]["state=value/equals/one_or_more/all/integer"],1)
        self.assertEqual(r["dimensions"]["state=value/pattern_match/one_or_more/all/string"],1)
        self.assertEqual(r["dimensions"]["direct_single_test=True"],1)
        self.assertEqual(r["dimensions"]["direct_single_test=False"],2)
        self.assertIn("original SCAP 1.4",markdown(r))
        self.assertFalse(r["original_source_parity_verified"])

    def test_complex_source_is_counted_without_claiming_simple_lowering(self):
        t=registry()
        t["states"]=[{"all":[{"field":"value","operation":"equals",
                             "value":"0"}]}]
        t["object"]["select"]["windows_view"]="32bit"
        r=inventory({"x":capsule("x",{"test":t})})
        self.assertEqual(r["dimensions"]["exact_HKLM_selector=False"],1)
        self.assertEqual(r["registry_test_nodes"],1)

if __name__=="__main__":
    unittest.main()
