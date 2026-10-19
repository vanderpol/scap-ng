#!/usr/bin/env python3
"""Refs #245: adversarial field/record/Item scopes, synthetic WMI-like Items."""
from copy import deepcopy
from itertools import product
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_same_record_evidence import evaluate_same_record_requirement

REQUIRED={"first":1,"second":2}

def observed(items=(),status="complete"):
    return {"capability":"windows.wmi.query",
            "status":status,
            "items":[{"id":f"rec-{i}","record":deepcopy(row)}
                     for i,row in enumerate(items)]}

def run(items,status="complete",mode="any_item"):
    return evaluate_same_record_requirement(
        REQUIRED,observed(items,status),item_scope=mode)

class CCorrelatedRecordRegression(unittest.TestCase):
    def test_good_record_satisfies_two_fields_of_same_parent(self):
        match={"first":[1],"second":[2]}
        result=run([match])
        self.assertEqual(result["result"],"true")
        self.assertEqual(result["per_item_results"],
                         [{"id":"rec-0","outcome":"true"}])
        self.assertTrue(result["all_fields_same_record"])
        self.assertFalse(result["scanner_executed"])

    def test_two_wrong_records_cannot_borrow_one_field_from_each_other(self):
        a={"first":[1],"second":[0]}
        b={"first":[0],"second":[2]}
        result=run([a,b])
        self.assertEqual(result["result"],"false")
        self.assertEqual([x["outcome"] for x in result["per_item_results"]],
                         ["false","false"])
        self.assertTrue(any(x["first"]==[1] for x in (a,b)))
        self.assertTrue(any(x["second"]==[2] for x in (a,b)))

    def test_item_scope_some_vs_every_is_not_the_same(self):
        good={"first":[1],"second":[2]}
        bad={"first":[1],"second":[9]}
        self.assertEqual(run([good,bad],mode="any_item")["result"],"true")
        self.assertEqual(run([good,bad],mode="every_item")["result"],"false")

    def test_missing_field_is_record_error_not_empty_item(self):
        bad={"first":[1]}
        r=run([bad])
        self.assertEqual(r["result"],"error")
        self.assertEqual(r["per_item_results"][0]["outcome"],"error")

    def test_multivalue_field_is_all_values_not_any_one_matching(self):
        item={"first":[1,0],"second":[2]}
        self.assertEqual(run([item])["result"],"false")
        self.assertEqual(run([{"first":[1,1],"second":[2]}])["result"],"true")

    def test_wrong_datatype_rejected_as_match_not_coerced(self):
        self.assertEqual(run([{"first":["1"],"second":[2]}])["result"],"false")
        self.assertEqual(run([{"first":[True],"second":[2]}])["result"],"false")

    def test_complete_empty_incomplete_error_distinct(self):
        for status,expect in (
            ("complete","false"),("incomplete","unknown"),
            ("error","error"),("not_collected","unknown"),
            ("not_applicable","not_applicable")
        ):
            with self.subTest(status=status):
                self.assertEqual(run([],status=status)["result"],expect)

    def test_incomplete_good_all_unknown_bad_all_false(self):
        good={"first":[1],"second":[2]}
        bad={"first":[1],"second":[0]}
        self.assertEqual(run([good],"incomplete",mode="every_item")["result"],"unknown")
        self.assertEqual(run([bad],"incomplete",mode="every_item")["result"],"false")
        self.assertEqual(run([good],"incomplete",mode="any_item")["result"],"true")

    def test_all_primitive_pair_combinations_preserve_item_correlation(self):
        for (f1,f2),(g1,g2) in product(
            product((0,1), (0,2)),repeat=2):
            expected_any=((f1==1 and f2==2) or (g1==1 and g2==2))
            expected_all=((f1==1 and f2==2) and (g1==1 and g2==2))
            population=[{"first":[f1],"second":[f2]},
                        {"first":[g1],"second":[g2]}]
            with self.subTest(population=population):
                self.assertEqual(run(population,mode="any_item")["result"],
                                 "true" if expected_any else "false")
                self.assertEqual(run(population,mode="every_item")["result"],
                                 "true" if expected_all else "false")

    def test_duplicate_ids_and_unsupported_extraneous_schema_fails_closed(self):
        bad=observed([{"first":[1],"second":[2]},
                      {"first":[1],"second":[2]}])
        bad["items"][1]["id"]="rec-0"
        with self.assertRaisesRegex(ValueError,"duplicate"):
            evaluate_same_record_requirement(REQUIRED,bad,item_scope="every_item")
        broken=observed([])
        broken["status"]="error"
        broken["items"]=[{"id":"n","record":{"first":[1],"second":[2]}}]
        with self.assertRaisesRegex(ValueError,"terminal"):
            evaluate_same_record_requirement(REQUIRED,broken,item_scope="any_item")

if __name__=="__main__":
    unittest.main()
