#!/usr/bin/env python3
"""#245 Inline original source constants: correct 0.4-C vs typed A graph."""
from copy import deepcopy
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_hybrid_inline_expectations import (
    present_inline_expectations,compile_inline_expectations,prove_inline_original)
from test_research_c_hybrid_must_overlay import source

class InlineRealOVALConstantsTests(unittest.TestCase):
    def test_original_single_multivalue_string_variable_moves_to_expected_field(self):
        native=source()
        original=deepcopy(native)
        authored=present_inline_expectations(native)
        self.assertEqual(native,original)
        self.assertEqual(authored["compatibility"]["variables"],{})
        self.assertEqual(authored["compatibility"]["states"],{})
        self.assertEqual(authored["expected_values"]["source-state"]["equals"],
                         ["/opt/support/a","/opt/support/b"])
        self.assertEqual(authored["expected_values"]["source-state"]["value_match"],"one")
        self.assertEqual(compile_inline_expectations(authored),native)
        proof=prove_inline_original(native,authored)
        self.assertEqual(proof["authored_constant_variable_declarations"],0)
        self.assertEqual(proof["compiler_rehydrated_source_variables"],1)
        self.assertFalse(proof["OVAL_runtime_parity_proven"])

    def test_changed_array_or_quantifier_is_not_equivalent(self):
        native=source();c=present_inline_expectations(native)
        c["expected_values"]["source-state"]["equals"].append("/opt/support/z")
        with self.assertRaisesRegex(ValueError,"changed source OVAL"):
            prove_inline_original(native,c)
        c=present_inline_expectations(native)
        c["expected_values"]["source-state"]["value_match"]="some"
        with self.assertRaisesRegex(ValueError,"quantifier"):
            compile_inline_expectations(c)

    def test_shared_constant_cross_consumer_cannot_be_silently_inlined(self):
        native=source()
        native["variables"]["support-paths"]["expression"]["literal"]=["/a","/b"]
        native["objects"]["collect-file-tree"]["select"]["another"]={
            "equals":{"variable":"support-paths"}}
        with self.assertRaisesRegex(ValueError,"other consumers"):
            present_inline_expectations(native)

    def test_non_constant_variable_not_removed(self):
        native=source();native["variables"]["support-paths"]["kind"]="local"
        with self.assertRaisesRegex(ValueError,"unsupported constant"):
            present_inline_expectations(native)

    def test_unknown_scalar_datatype_not_retyped(self):
        native=source();state=native["states"]["source-state"]["state"]
        state["datatype"]="version"
        with self.assertRaisesRegex(ValueError,"typed State"):
            present_inline_expectations(native)

    def test_source_title_and_id_provenance_preserved(self):
        native=source()
        c=present_inline_expectations(native)
        name=c["expected_values"]["source-state"]["source_constant"]
        self.assertEqual(name["id"],"support-paths")
        self.assertEqual(name["description"],"Two possible paths")
        c["expected_values"]["source-state"]["source_constant"]["id"]="bad-id"
        with self.assertRaisesRegex(ValueError,"changed source OVAL"):
            prove_inline_original(native,c)

    def test_state_reference_wrong_with_inline_contract_rejected(self):
        native=source();c=present_inline_expectations(native)
        c["checks"]["union"]["must"]["states"]=["does-not-exist"]
        with self.assertRaisesRegex(ValueError,"State"):
            compile_inline_expectations(c)

if __name__=="__main__":
    unittest.main()
