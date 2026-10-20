#!/usr/bin/env python3
"""Refs #245: source-independent rehydration of safely inlined State constants."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_c_constant_state_source import (
    present_fixed_state_expectations, compile_fixed_state_expectations,
    prove_fixed_state_source,
)


def original( *, shared=False, selector_use=False, derived=False):
    var_id="source-family-pattern-variable"
    state_id="state-family-matches-source-regex"
    a={
        "id":"roundtrip.oval-org-mitre-oval-test-def-95",
        "mode":"automated",
        "evaluate":{"test":"test-system-family-pattern"},
        "tests":{"test-system-family-pattern":{
            "capability":"independent.family","object":"family-source-object",
            "states":[state_id],"check":"at least one",
            "check_existence":"at_least_one_exists",
            "reported_elements":"all","test_title":"System family is supported"}},
        "objects":{"family-source-object":{
            "capability":"independent.family",
            "object_title":"Original system family Object"}},
        "states":{state_id:{
            "capability":"independent.family",
            "state_title":"Family matches allowed systems",
            "state":{"datatype":"string","field":"family",
                     "entity_existence":"at_least_one_exists",
                     "entity_check":"all","operation":"pattern match",
                     "value":{"variable":var_id},"variable_check":"all"}}},
        "variables":{var_id:{
            "kind":"constant","datatype":"string",
            "expression":{"literal":"(vmware_infrastructure|panos|unix|windows)"},
            "title":"Pattern matching OVAL system families"}},
    }
    if shared:
        a["states"]["another-source-State"]={
            "capability":"independent.family","state_title":"Second consumer",
            "state":deepcopy(a["states"][state_id]["state"])}
    if selector_use:
        a["objects"]["family-source-object"]["select"]={
            "family":{"value":{"variable":var_id},"datatype":"string",
                      "operation":"equals"}}
    if derived:
        a["variables"]["derived-dependency"]={
            "kind":"local","datatype":"string",
            "expression":{"variable":var_id}}
    return a


class SourceFixedStateConstantTests(unittest.TestCase):
    def test_full_original_source_graph_roundtrip_without_original_compile_input(self):
        source=original()
        before=deepcopy(source)
        author, sidecar=present_fixed_state_expectations(source)
        self.assertEqual(source,before)
        self.assertEqual(set(author["expected_values"]),{"expected_family"})
        self.assertEqual(author["expected_values"]["expected_family"],{
            "field":"family","operation":"pattern match","value_match":"all",
            "value":"(vmware_infrastructure|panos|unix|windows)"})
        self.assertNotIn("source-family-pattern-variable",
                         sidecar["source_graph_without_inlined_constants"]["variables"])
        # The compiler receives *only* C author's edited values + sidecar.
        self.assertEqual(compile_fixed_state_expectations(author,sidecar),source)
        proof=prove_fixed_state_source(source,author,sidecar)
        self.assertTrue(proof["recreated_complete_typed_A_graph"])
        self.assertFalse(proof["full_native_C_compilation_proven"])
        self.assertFalse(proof["OVAL_scanner_parity_proven"])

    def test_multi_value_constant_retains_order_duplicates_and_only_one(self):
        source=original()
        var=next(iter(source["variables"].values()))
        var["expression"]["literal"]=["/a","/a","/b"]
        state=next(iter(source["states"].values()))["state"]
        state.update({"operation":"equals","value_match":"one",
                      "variable_check":"only one"})
        author, sidecar=present_fixed_state_expectations(source)
        self.assertEqual(author["expected_values"]["expected_family"]["value"],
                         ["/a","/a","/b"])
        self.assertEqual(compile_fixed_state_expectations(author,sidecar),source)
        modified=deepcopy(author)
        modified["expected_values"]["expected_family"]["value"].append("/c")
        out=compile_fixed_state_expectations(modified,sidecar)
        self.assertEqual(out["variables"]["source-family-pattern-variable"][
            "expression"]["literal"],["/a","/a","/b","/c"])
        with self.assertRaisesRegex(ValueError,"changed original source typed graph"):
            prove_fixed_state_source(source,modified,sidecar)

    def test_shared_or_collector_driving_constant_stays_in_typed_source(self):
        for changes in ({"shared":True},{"selector_use":True},{"derived":True}):
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ValueError,
                                            "no source-proven single-consumer"):
                    present_fixed_state_expectations(original(**changes))

    def test_local_variable_and_unknown_variable_check_do_not_fold(self):
        source=original()
        next(iter(source["variables"].values()))["kind"]="local"
        with self.assertRaisesRegex(ValueError,"no source-proven"):
            present_fixed_state_expectations(source)
        source=original()
        next(iter(source["states"].values()))["state"]["variable_check"]="unknown"
        with self.assertRaisesRegex(ValueError,"no source-proven"):
            present_fixed_state_expectations(source)

    def test_missing_extra_or_rebound_source_identity_rejected(self):
        source=original()
        author,sidecar=present_fixed_state_expectations(source)
        for change in ("missing","extra","wrongmatch","badvalue"):
            with self.subTest(change=change):
                new=deepcopy(author)
                exp=new["expected_values"]
                if change=="missing":exp.clear()
                if change=="extra":exp["expected_unknown"]=deepcopy(exp["expected_family"])
                if change=="wrongmatch":exp["expected_family"]["value_match"]="none satisfy"
                if change=="badvalue":exp["expected_family"]["value"]=[1]
                with self.assertRaises(ValueError):
                    compile_fixed_state_expectations(new,sidecar)
        changed=deepcopy(sidecar)
        changed["bindings"]["expected_family"]["path"][1]="invented"
        with self.assertRaises(ValueError):
            compile_fixed_state_expectations(author,changed)

    def test_reject_duplicate_source_reference_paths(self):
        source=original()
        sid=next(iter(source["states"]))
        source["states"][sid]["state"]={"all":[deepcopy(
            source["states"][sid]["state"]), deepcopy(source["states"][sid]["state"])]}
        with self.assertRaisesRegex(ValueError,"no source-proven single-consumer"):
            present_fixed_state_expectations(source)


if __name__=="__main__":
    unittest.main()
