"""Refs #245: source complexity triage never claims C conversion capability."""
import copy
import unittest
from research_c_coverage_triage import (
    classify_source_assessment,summarize_verified_documents
)

def fixture(state=None, count=1):
    tests={f"check_{n}":{
        "capability":"windows.passwordpolicy",
        "require":"at_least_one_exists_and_all_match",
        **({"states":copy.deepcopy(state)} if state is not None else {}),
    } for n in range(count)}
    doc={"id":"test","mode":"automated","tests":tests,
         "evaluate":{"test":"check_0"}}
    index={"mode":"automated","source_dataflow":{
        "status":"SOURCE_DATAFLOW_ONLY_NOT_EXECUTABLE","sites":[]}}
    return doc,index

class ConservativeTriage(unittest.TestCase):
    def test_simple_objectless_is_not_proven_equivalent(self):
        a,i=fixture([{"family":{"equals":"windows"}}])
        got=classify_source_assessment(a,i)
        self.assertEqual(got["tier"],"SIMPLE_SOURCE_REVIEW_CANDIDATE")
        self.assertEqual(got["counts"]["objectless_test"],1)
        self.assertFalse(got["C_compiler_proven"])
        self.assertFalse(got["OVAL_source_runtime_parity_proven"])

    def test_dynamic_variable_blocks_simple(self):
        a,i=fixture()
        a["variables"]={"x":{"expression":{"literal":"y"}}}
        self.assertEqual(classify_source_assessment(a,i)["tier"],
                         "DYNAMIC_SOURCE_GRAPH_NEEDS_COMPATIBILITY")

    def test_nested_record_not_scalar(self):
        a,i=fixture([{"result":{"record":{"fields":{
            "domainrole":{"equals":"1"}}}}}])
        a["shared_objects"]={"shared":{"capability":"windows.wmi.query"}}
        a["tests"]["check_0"]["object"]="shared"
        got=classify_source_assessment(a,i)
        self.assertEqual(got["tier"],"RECORD_SOURCE_NEEDS_NARROW_COMPILER_PROOF")
        self.assertEqual(got["counts"]["record_predicate"],1)
        self.assertEqual(got["counts"]["shared_objects"],1)
        self.assertEqual(got["counts"]["objectless_test"],0)

    def test_four_source_site_hazards_remain_distinct(self):
        for feature,output_key in (
            ("filter","filter"),("set","set"),
            ("for_each","foreach"),("projection","selector_projection")
        ):
            a,i=fixture()
            i["source_dataflow"]["sites"]=[{"kind":feature}]
            with self.subTest(feature=feature):
                got=classify_source_assessment(a,i)
                self.assertEqual(got["tier"],"DYNAMIC_SOURCE_GRAPH_NEEDS_COMPATIBILITY")
                self.assertEqual(got["counts"][output_key],1)

    def test_multiple_source_tests_need_composition(self):
        a,i=fixture(count=2)
        got=classify_source_assessment(a,i)
        self.assertEqual(got["tier"],"COMPOSITION_NEEDS_SOURCE_CHECK")
        self.assertEqual(got["counts"]["multiple_tests"],1)

    def test_reject_invalid_envelope_boundaries(self):
        a,i=fixture()
        i["mode"]="manual"
        with self.assertRaisesRegex(ValueError,"matching source"):
            classify_source_assessment(a,i)
        a,i=fixture()
        i["source_dataflow"]["status"]="NOT_VERIFIED"
        with self.assertRaisesRegex(ValueError,"verified source dataflow"):
            classify_source_assessment(a,i)
        with self.assertRaises(ValueError):
            summarize_verified_documents({"a":{"assessment":a}},{})

    def test_synthetic_totals_do_not_promote_to_c_coverage(self):
        a,i=fixture()
        b,j=fixture(count=2);b["id"]="other"
        docs={"authoring/rhel_9/a.json":{"assessment":a},
              "authoring/windows_11/b.json":{"assessment":b}}
        idx={"authoring/rhel_9/a.json":i,"authoring/windows_11/b.json":j}
        result=summarize_verified_documents(docs,idx)
        self.assertEqual(result["assessment_count"],2)
        self.assertEqual(result["named_test_count"],3)
        self.assertEqual(sum(result["tier_counts"].values()),2)
        self.assertEqual(result["C_converted_assessment_count_claimed"],0)
        self.assertEqual(len(result["cases"]),2)
        self.assertIn("windows_11",result["by_source_group"])
        self.assertFalse(result["scanner_runtime_semantics_proven"])

if __name__=="__main__":
    unittest.main()
