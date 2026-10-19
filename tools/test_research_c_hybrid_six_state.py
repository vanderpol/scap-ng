#!/usr/bin/env python3
"""Refs #245: C source alias layer retains pinned OVAL six-state AND results.

All leaf Test results are SUPPLIED, not evaluated by a scanner. This tests
the original source criteria versus C-compiled criteria through the existing
OVAL 5.12.3 independently audited Boolean combiner. Collection, State and
full scanner parity remain separate.
"""
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_research_c_hybrid_must_overlay import source as original_set_fixture
from research_c_oval_hybrid_provenance import (
    present_oval_set_provenance,compile_oval_set_provenance)
from research_c_apache_provenance_split import (
    present_apache_provenance_split,compile_apache_split)
from v04_a_truth_plan import compile_expression,execute_supplied_results

APACHE=(Path(__file__).resolve().parents[1]/
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")

CASES=[
    ("all_true",["true"],"true"),
    ("all_false",["false"],"false"),
    ("all_not_applicable",["not_applicable"],"not_applicable"),
    ("false_over_error",["false","error"],"false"),
    ("error_over_unknown",["error","unknown"],"error"),
    ("unknown_over_not_evaluated",["unknown","not_evaluated"],"unknown"),
    ("not_evaluated_over_na",["not_evaluated","not_applicable"],"not_evaluated"),
    ("true_with_na",["true","not_applicable"],"true"),
]

def truth(native,compiled,case,states,expected):
    original=compile_expression(native)
    generated=compile_expression(compiled)
    assert original["requires"]["tests"]==generated["requires"]["tests"]
    keys=original["requires"]["tests"]
    given={key:states[i % len(states)] for i,key in enumerate(keys)}
    a=execute_supplied_results(original,given)
    b=execute_supplied_results(generated,given)
    # Original and C lowering must select precisely the same source Tests.
    # Independently expected outcome from the pinned boolean truth table.
    if a["outcome"]!=expected or b["outcome"]!=expected:
        raise AssertionError((case,a["outcome"],b["outcome"],expected))
    assert a["tests_supplied"]==len(keys)
    assert b["scanner_executed"] is False
    assert b["collections_evaluated"] is False

class CHybridSourceSixStateTests(unittest.TestCase):
    def test_original_set_and_c_aliases_remain_six_state_equivalent(self):
        original=original_set_fixture()
        author,prov=present_oval_set_provenance(original)
        generated=compile_oval_set_provenance(author,prov)
        self.assertEqual(len(original["tests"]),2)
        for case,states,expected in CASES:
            with self.subTest(case=case):
                truth(original,generated,case,states,expected)

    def test_full_apache_five_test_c_compiler_same_source_truth_outcomes(self):
        original=yaml.safe_load(APACHE.read_text(encoding="utf-8"))["assessment"]
        author,prov=present_apache_provenance_split(original)
        generated=compile_apache_split(author,prov)
        self.assertEqual(len(original["tests"]),5)
        for case,states,expected in CASES:
            with self.subTest(case=case):
                truth(original,generated,case,states,expected)

    def test_not_inventing_missing_leaf_as_false_or_unknown(self):
        original=original_set_fixture()
        author,prov=present_oval_set_provenance(original)
        generated=compile_oval_set_provenance(author,prov)
        compiled=compile_expression(generated)
        required=compiled["requires"]["tests"]
        with self.assertRaisesRegex(ValueError,"keys do not match"):
            execute_supplied_results(compiled,{required[0]:"unknown"})

if __name__=="__main__":
    unittest.main()
