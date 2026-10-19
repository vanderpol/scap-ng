#!/usr/bin/env python3
"""#245 regression: readability overlay cannot change nested OVAL semantics."""
from copy import deepcopy
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_hybrid_must_overlay import (
    present_hybrid_must,compile_hybrid_must,prove_original_hybrid)

def source():
    # Small concrete two-check Set, Filter, multi-value constant graph.
    # The FULL 7-Test OVAL Self-Assertion source is also checked in CI.
    obj_a="collect-file-tree"
    obj_b="collected-filtered-set"
    sid="source-state"
    state={"capability":"unix.file","state_title":"Selected support paths",
       "state":{"datatype":"string","entity_check":"all",
                "entity_existence":"at_least_one_exists","field":"path",
                "operation":"equals","value":{"variable":"support-paths"},
                "variable_check":"only one"}}
    return {"assessment_title":"OVAL Set/Filter Test",
      "class":"compliance","evaluate":{"all":[
         {"test":"test-complement"},{"test":"test-union"}]},
      "id":"original-oval-set-test","mode":"automated",
      "objects":{
        obj_a:{"capability":"unix.file","object_title":"Collect support paths",
          "select":{"path":{"datatype":"string","operation":"equals",
                            "value":"/opt/support"}}},
        obj_b:{"capability":"unix.file","object_title":"Combine filtered file tree",
          "set":{"operator":"union","members":[{"object":obj_a}],
                 "filters":[{"action":"exclude","state":sid}]}}},
      "purpose":"assessment","specification":{"id":"scap-ng","version":"0.3.0"},
      "states":{sid:state},
      "tests":{
        "test-complement":{"capability":"unix.file","check":"all",
          "check_existence":"only_one_exists","object":obj_b,
          "reported_elements":"all","states":[sid],
          "test_title":"Test COMPLEMENT source semantics"},
        "test-union":{"capability":"unix.file","check":"all",
          "check_existence":"at_least_one_exists","object":obj_b,
          "reported_elements":"all","states":[sid],
          "test_title":"Test UNION source semantics"}},
      "variables":{"support-paths":{
          "datatype":"string","kind":"constant","title":"Two possible paths",
          "expression":{"literal":["/opt/support/a","/opt/support/b"]}}},
      "version":"0.3.0"}

class HybridCResearchTests(unittest.TestCase):
    def test_exact_full_source_graph_roundtrip(self):
        before=source()
        original=deepcopy(before)
        c=present_hybrid_must(before)
        self.assertEqual(before,original)
        self.assertEqual(set(c["checks"]),{"complement","union"})
        self.assertEqual(c["checks"]["complement"]["must"],{
            "items_exist":"exactly_one","items_match":"every",
            "states":["source-state"]})
        self.assertEqual(c["require"],{"and":[
            {"check":"complement"},{"check":"union"}]})
        self.assertEqual(compile_hybrid_must(c),before)
        result=prove_original_hybrid(before,c)
        self.assertEqual(result["source_set_count"],1)
        self.assertEqual(result["source_variable_count"],1)
        self.assertFalse(result["OVAL_runtime_parity_proven"])

    def test_existence_semantics_not_implicitly_repaired(self):
        native=source()
        c=present_hybrid_must(native)
        c["checks"]["complement"]["must"]["items_exist"]="one_or_more"
        self.assertEqual(compile_hybrid_must(c)["tests"][
            "test-complement"]["check_existence"],"at_least_one_exists")
        with self.assertRaisesRegex(ValueError,"differs from pinned"):
            prove_original_hybrid(native,c)

    def test_nested_filter_population_mutation_not_overlooked(self):
        native=source()
        c=present_hybrid_must(native)
        obj=c["compatibility"]["objects"]["collected-filtered-set"]
        obj["set"]["filters"][0]["action"]="include"
        with self.assertRaisesRegex(ValueError,"differs from pinned"):
            prove_original_hybrid(native,c)

    def test_constant_multiplicity_incompatibility_is_visible(self):
        native=source()
        c=present_hybrid_must(native)
        c["compatibility"]["variables"]["support-paths"][
            "expression"]["literal"].pop()
        with self.assertRaisesRegex(ValueError,"differs from pinned"):
            prove_original_hybrid(native,c)

    def test_unreferenced_or_duplicate_check_is_rejected(self):
        c=present_hybrid_must(source())
        c["require"]={"and":[{"check":"complement"},{"check":"complement"}]}
        with self.assertRaisesRegex(ValueError,"each Test"):
            compile_hybrid_must(c)
        c=present_hybrid_must(source())
        del c["checks"]["union"]
        with self.assertRaisesRegex(ValueError,"unresolved Test"):
            compile_hybrid_must(c)

    def test_missing_documentation_does_not_silently_pass(self):
        c=present_hybrid_must(source())
        c["checks"]["union"]["description"]=""
        with self.assertRaisesRegex(ValueError,"documentation"):
            compile_hybrid_must(c)

    def test_unsupported_check_and_existence_must_not_default(self):
        native=source()
        native["tests"]["test-union"]["check_existence"]="arbitrary"
        with self.assertRaisesRegex(ValueError,"quantifier"):
            present_hybrid_must(native)
        c=present_hybrid_must(source())
        c["checks"]["union"]["must"]["items_match"]="anything"
        with self.assertRaisesRegex(ValueError,"matching/existence"):
            compile_hybrid_must(c)

    def test_unknown_source_fields_rejected(self):
        native=source()
        native["tests"]["test-union"]["mask"]=True
        with self.assertRaisesRegex(ValueError,"unknown original Test"):
            present_hybrid_must(native)

if __name__=="__main__":
    unittest.main()
