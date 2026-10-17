#!/usr/bin/env python3
"""Source-grouping counterexamples for #229/#235; no actual WMI calls."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_windows_role_grouping import (
    role_alternative, test_root_population, normalized_fact_for_item)
from research_requirements_first_evidence import PASS, FAIL, ERROR, UNKNOWN

MEMBER=("1","3")
STANDALONE=("0","2")

def root(ident,*values,status="complete"):
    return {"id":ident, "status":status, "records":[{"domainrole":v} for v in values]}

def population(*roots,status="complete"):
    return {"status":status, "items":list(roots)}

class WmiGroupingTests(unittest.TestCase):
    def test_single_member_records(self):
        for val in ("1","3"):
            self.assertEqual(role_alternative(root("a",val),MEMBER),PASS)
    def test_same_record_values(self):
        self.assertEqual(role_alternative(root("a","1","1"),MEMBER),PASS)
    def test_mixed_records_not_membership(self):
        self.assertEqual(role_alternative(root("a","1","3"),MEMBER),FAIL)
        self.assertEqual(normalized_fact_for_item(root("a","1","3"))["role_name"],"mixed_records")
        self.assertTrue(all(x in MEMBER for x in ("1","3")))
    def test_standalone_mixed_records(self):
        self.assertEqual(role_alternative(root("a","0","2"),STANDALONE),FAIL)
    def test_separate_root_items_have_separate_or_states(self):
        self.assertEqual(test_root_population(population(root("a","1"),root("b","3")),MEMBER),PASS)
        self.assertEqual(test_root_population(population(root("ab","1","3")),MEMBER),FAIL)
    def test_nonmatching_root_item(self):
        self.assertEqual(test_root_population(population(root("a","1"),root("b","0")),MEMBER),FAIL)
    def test_empty_complete_records_fail(self):
        self.assertEqual(role_alternative(root("a"),MEMBER),FAIL)
    def test_empty_incomplete_records_unknown(self):
        self.assertEqual(role_alternative(root("a",status="incomplete"),MEMBER),UNKNOWN)
    def test_partial_positive_unknown(self):
        self.assertEqual(role_alternative(root("a","1",status="incomplete"),MEMBER),UNKNOWN)
    def test_partial_mixed_can_fail(self):
        self.assertEqual(role_alternative(root("a","1","3",status="incomplete"),MEMBER),FAIL)
    def test_root_partial_positive_unknown(self):
        self.assertEqual(test_root_population(population(root("a","1"),status="incomplete"),MEMBER),UNKNOWN)
    def test_root_partial_negative_fail(self):
        self.assertEqual(test_root_population(population(root("a","2"),status="incomplete"),MEMBER),FAIL)
    def test_root_empty_complete_fail(self):
        self.assertEqual(test_root_population(population(),MEMBER),FAIL)
    def test_root_empty_incomplete_unknown(self):
        self.assertEqual(test_root_population(population(status="incomplete"),MEMBER),UNKNOWN)
    def test_missing_expected_record_field_error(self):
        case={"id":"a","status":"complete","records":[{}]}
        self.assertEqual(role_alternative(case,MEMBER),ERROR)
    def test_record_read_error(self):
        case={"id":"a","status":"complete","records":[{"domainrole":"1"},{"status":"error"}]}
        self.assertEqual(role_alternative(case,MEMBER),ERROR)
    def test_nonmatching_record_decisive_over_error(self):
        case={"id":"a","status":"complete","records":[{"domainrole":"2"},{"status":"error"}]}
        self.assertEqual(role_alternative(case,MEMBER),FAIL)
    def test_root_collection_error(self):
        self.assertEqual(test_root_population(population(status="error"),MEMBER),ERROR)
    def test_duplicate_root_id_error(self):
        self.assertEqual(test_root_population(population(root("a","1"),root("a","1")),MEMBER),ERROR)
    def test_no_implicit_integer_coercion(self):
        with self.assertRaisesRegex(ValueError,"exact string"):
            role_alternative(root("a",1),MEMBER)

if __name__=="__main__":unittest.main()
