#!/usr/bin/env python3
"""Synthetic counterexamples for #235: resource semantics, not scanner parity."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_requirements_first_evidence import (
    PASS,FAIL,ERROR,UNKNOWN,evaluate,population,mount,compare
)

WHERE={"mount_point":{"equals":"/home"}}
MUST={"mount_options":{"contains":"nosuid"}}
GOOD=mount("home-good",["rw","nosuid"])
BAD=mount("home-bad",["rw"])
OTHER=mount("other",["rw"],"/var")

def outcome(status,*items,mode="each",minimum=0,where=WHERE,must=MUST,singleton=False):
    return evaluate(population(status,*items),where=where,must=must,
                    mode=mode,minimum_resources=minimum,singleton=singleton)

class TypedNativePolicyCounterexamples(unittest.TestCase):
    def test_required_mount_complete_zero_fails(self):
        x=outcome("complete",minimum=1)
        self.assertEqual((x.verdict,x.observed,x.selected),(FAIL,0,0))

    def test_optional_population_complete_zero_passes(self):
        self.assertEqual(outcome("complete").verdict,PASS)

    def test_raw_population_not_empty_but_selected_population_empty(self):
        a=outcome("complete",OTHER,minimum=1)
        b=outcome("complete",OTHER)
        self.assertEqual((a.verdict,a.observed,a.selected),(FAIL,1,0))
        self.assertEqual(b.verdict,PASS)

    def test_one_matching_compliant_mount_passes(self):
        self.assertEqual(outcome("complete",GOOD,minimum=1).verdict,PASS)

    def test_one_noncompliant_mount_fails(self):
        self.assertEqual(outcome("complete",BAD,minimum=1).verdict,FAIL)

    def test_all_selected_must_pass_even_with_multiple(self):
        self.assertEqual(outcome("complete",GOOD,BAD,minimum=1).verdict,FAIL)
        self.assertEqual(outcome("complete",GOOD,mount("two",["nosuid"]),minimum=1).verdict,PASS)

    def test_incomplete_zero_does_not_mean_complete_empty(self):
        self.assertEqual(outcome("incomplete",minimum=1).verdict,UNKNOWN)
        self.assertEqual(outcome("incomplete").verdict,UNKNOWN)

    def test_incomplete_failing_witness_proves_failure(self):
        self.assertEqual(outcome("incomplete",BAD,minimum=1).verdict,FAIL)
        self.assertEqual(outcome("incomplete",BAD).verdict,FAIL)

    def test_incomplete_compliant_witness_does_not_prove_all(self):
        self.assertEqual(outcome("incomplete",GOOD,minimum=1).verdict,UNKNOWN)

    def test_provider_error_is_not_noncompliance(self):
        self.assertEqual(outcome("error",minimum=1).verdict,ERROR)

    def test_missing_selection_field_does_not_disappear(self):
        invisible={"id":"mystery","fields":{"mount_options":["rw"]}}
        x=outcome("complete",invisible,minimum=1)
        self.assertEqual((x.verdict,x.selected,x.possible_matches),(UNKNOWN,0,1))
        self.assertEqual(outcome("complete",invisible).verdict,UNKNOWN)

    def test_unreadable_selection_field_causes_evidence_error(self):
        unreadable={"id":"unreadable","fields":{"mount_point":{"field_status":"error"},"mount_options":["rw"]}}
        self.assertEqual(outcome("complete",unreadable).verdict,ERROR)

    def test_missing_required_field_is_not_silently_false_or_pass(self):
        missing={"id":"unknown-option","fields":{"mount_point":"/home"}}
        self.assertEqual(outcome("complete",missing,minimum=1).verdict,UNKNOWN)

    def test_unreadable_required_field_is_error(self):
        unreadable={"id":"unreadable-option","fields":{"mount_point":"/home","mount_options":{"field_status":"error"}}}
        self.assertEqual(outcome("complete",unreadable,minimum=1).verdict,ERROR)

    def test_observed_failure_decisive_even_with_uncertain_selection(self):
        uncertain={"id":"candidate","fields":{"mount_options":["nosuid"]}}
        self.assertEqual(outcome("complete",BAD,uncertain,minimum=1).verdict,FAIL)

    def test_some_witness_and_none_prohibition_remain_decisive_on_partial(self):
        self.assertEqual(outcome("incomplete",GOOD,mode="some").verdict,PASS)
        self.assertEqual(outcome("incomplete",GOOD,mode="none",must=None).verdict,FAIL)
        self.assertEqual(outcome("incomplete",mode="none",must=None).verdict,UNKNOWN)

    def test_some_complete_empty_fails_and_none_complete_empty_passes(self):
        self.assertEqual(outcome("complete",mode="some").verdict,FAIL)
        self.assertEqual(outcome("complete",mode="none",must=None).verdict,PASS)

    def test_exactly_one_counts_selected_not_compliant_items(self):
        self.assertEqual(outcome("complete",GOOD,BAD,mode="exactly_one").verdict,FAIL)
        self.assertEqual(outcome("complete",GOOD,mode="exactly_one").verdict,PASS)
        self.assertEqual(outcome("complete",BAD,mode="exactly_one").verdict,FAIL)
        self.assertEqual(outcome("complete",mode="exactly_one").verdict,FAIL)

    def test_exactly_one_incomplete_decisive_failure_or_unknown_success(self):
        self.assertEqual(outcome("incomplete",BAD,mode="exactly_one").verdict,FAIL)
        self.assertEqual(outcome("incomplete",GOOD,mode="exactly_one").verdict,UNKNOWN)
        self.assertEqual(outcome("incomplete",GOOD,BAD,mode="exactly_one").verdict,FAIL)

    def test_singleton_promise_changes_duplicate_semantics(self):
        self.assertEqual(outcome("complete",GOOD,mount("second-home",["nosuid"]),minimum=1).verdict,PASS)
        self.assertEqual(outcome("complete",GOOD,mount("second-home",["nosuid"]),
                                 mode="exactly_one",singleton=True).verdict,ERROR)
        # Named resource typed as unique therefore cannot silently choose one.

    def test_duplicate_evidence_identity_is_error(self):
        self.assertEqual(outcome("complete",GOOD,GOOD,minimum=1).verdict,ERROR)

    def test_typed_numeric_evaluation_refuses_implicit_string_coercion(self):
        x={"fields":{"validity_hours":72}}
        y={"fields":{"validity_hours":"72"}}
        self.assertEqual(compare(x,"validity_hours",{"between":[48,168]}),PASS)
        with self.assertRaisesRegex(ValueError,"typed numeric"):
            compare(y,"validity_hours",{"between":[48,168]})

    def test_wsgi_wmi_mixed_record_whole_state_counterexample(self):
        # Original source WMI test uses OR of TWO complete-State alternatives:
        # all DomainRole records must be 1, OR all must be 3.
        # A typed one_of [1,3] predicate is not a faithful lowering.
        for values,original in [
            (["1"],True),(["3"],True),(["1","3"],False),
            (["1","1"],True),([],False),(["2"],False)
        ]:
            whole_state=len(values)>0 and (all(x=="1" for x in values) or all(x=="3" for x in values))
            naive_membership=len(values)>0 and all(x in {"1","3"} for x in values)
            self.assertEqual(whole_state,original)
            if values==["1","3"]:
                self.assertTrue(naive_membership)
                self.assertFalse(whole_state)

    def test_apache_two_field_view_cannot_preserve_original_four_probes(self):
        # This is a data-information test: a provider which only outputs an
        # effective directive/value pair discards input-file and source IDs
        # required by the original 4 tests. No claims about actual Apache
        # precedence, collection flags or host runtime are made here.
        a=[{"name":"KeepAlive","value":"On","source":"/etc/httpd/httpd.conf"}]
        b=[{"name":"KeepAlive","value":"On","source":"/etc/httpd/conf.d/other.conf"}]
        flattened=lambda rows:[(r["name"],r["value"]) for r in rows]
        self.assertEqual(flattened(a),flattened(b))
        self.assertNotEqual(a,b)

    def test_dns_two_value_field_requires_value_aggregation_contract(self):
        # Scalar between cannot even be applied to a multi-valued field.
        # We deliberately do not guess whether the original OVAL entity_check
        # would return False/Error/Unknown for this source without its contract.
        x={"fields":{"validity_hours":[72,200]}}
        with self.assertRaisesRegex(ValueError,"typed numeric"):
            compare(x,"validity_hours",{"between":[48,168]})

if __name__=="__main__":unittest.main()
