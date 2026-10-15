#!/usr/bin/env python3
"""Research-only compiler shorthand positive/negative tests."""
import unittest
from copy import deepcopy
from research_04_compiled_authoring_macros import (
    simplify_predicate, expand_predicate, simplify_doc, expand_doc
)

class MacroTest(unittest.TestCase):
    def test_scalar_operators_reverse_exact(self):
        for op,expected in (("equals","equals"),("pattern_match","matches_regex")):
            for v in ("0",0,False,r".*\\/home"):
                pred={"operation":op,"value":v,"entity_existence":"one_or_more",
                      "entity_check":"all"}
                short,yes=simplify_predicate(pred)
                self.assertTrue(yes)
                self.assertIn(expected,short)
                self.assertEqual(expand_predicate(short),pred)
                self.assertEqual(type(expand_predicate(short)["value"]),type(v))

    def test_no_complex_variable_expression_shortening(self):
        predicate={"operation":"equals","value":{"variable":"some-runtime-variable"}}
        short,yes=simplify_predicate(predicate)
        self.assertFalse(yes)
        self.assertEqual(short,predicate)

    def test_no_implicit_operation(self):
        pred={"value":"v"}
        short,yes=simplify_predicate(pred)
        self.assertFalse(yes)
        self.assertEqual(short,pred)

    def test_reject_ambiguous_shorthand(self):
        for invalid in (
            {"equals":"x","operation":"equals"},
            {"equals":"x","value":"y"},
            {"equals":"x","matches_regex":"x"}
        ):
            with self.assertRaises(ValueError):
                expand_predicate(invalid)

    def test_reject_shorthand_non_scalar(self):
        with self.assertRaisesRegex(ValueError,"not scalar"):
            expand_predicate({"equals":{"variable":"x"}})

    def test_singular_test_state_and_explicit_capability_roundtrip(self):
        doc={"assessment":{"mode":"automated","id":"sample",
             "tests":{"sample-test":{
                 "capability":"unix.file",
                 "object":{"capability":"unix.file","select":{"path":{"value":"/tmp/test","operation":"equals"}}},
                 "states":[{"field":"owner_uid","value":0,"operation":"equals",
                            "existence":"one_or_more","match":"all"}],
                 "existence":"one_or_more","match":"all","reported_elements":"all"
             }},
             "evaluate":{"test":"sample-test"}}}
        source=deepcopy(doc)
        abbreviated,counts=simplify_doc(doc)
        self.assertEqual(abbreviated["assessment"]["evaluate"],"sole_test")
        self.assertEqual(abbreviated["assessment"]["tests"]["sample-test"]["object"]["capability"],"from_test")
        self.assertIn("expect",abbreviated["assessment"]["tests"]["sample-test"])
        self.assertIn("equals",abbreviated["assessment"]["tests"]["sample-test"]["expect"])
        self.assertEqual(expand_doc(abbreviated),source)
        self.assertEqual(doc,source)
        self.assertEqual(counts["selector_comparison"],1)

    def test_sole_test_fail_closed_when_multi(self):
        with self.assertRaisesRegex(ValueError,"exactly one"):
            expand_doc({"assessment":{"tests":{"a":{},"b":{}},"evaluate":"sole_test"}})

    def test_no_implicit_capability(self):
        with self.assertRaisesRegex(ValueError,"absent Test capability"):
            expand_doc({"assessment":{"tests":{"a":{"object":{"capability":"from_test"}}}}})

    def test_no_clobber_of_states_and_expect(self):
        with self.assertRaisesRegex(ValueError,"one State"):
            expand_doc({"assessment":{"tests":{"a":{"states":[{"field":"x"}],"expect":{"field":"y"}}}}})

if __name__=="__main__":
    unittest.main()
