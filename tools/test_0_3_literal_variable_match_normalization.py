"""Native 0.3 literal State normalization: preserve OVAL aggregation semantics."""
import unittest
from normalize_0_3_review_surface import normalize_scalar_tree


def change_state(state):
    edits=[]
    doc={"assessment":{"tests":{"check":{"capability":"windows.ntuser","states":[{"capability":"windows.ntuser","state":state}]}}}}
    normalized=normalize_scalar_tree(doc,(),edits)
    return normalized["assessment"]["tests"]["check"]["states"][0]["state"],edits


class LiteralVariableCheckTests(unittest.TestCase):
    def test_real_ntuser_empty_type_literal_has_neutral_var_check_removed(self):
        original={"field":"type","value":"","operation":"equals",
                  "datatype":"string","match":"all","existence":"one_or_more",
                  "variable_match":"one_or_more"}
        state,edits=change_state(original)
        self.assertEqual("",state["value"])
        self.assertEqual("equals",state["operation"])
        self.assertEqual("all",state["match"])
        self.assertEqual("one_or_more",state["existence"])
        self.assertNotIn("variable_match",state)
        self.assertTrue(any(x.get("reason")=="single-literal State value has one comparison operand" for x in edits))

    def test_true_variable_reference_retains_required_quantifier(self):
        original={"field":"type","value":{"variable":"expected-type-variable"},
                  "operation":"equals","datatype":"string","match":"all",
                  "existence":"one_or_more","variable_match":"one_or_more"}
        state,_=change_state(original)
        self.assertEqual("one_or_more",state["variable_match"])

    def test_collection_retains_quantifier(self):
        original={"field":"type","value":["dword","string"],"operation":"equals",
                  "datatype":"string","match":"all","existence":"one_or_more",
                  "variable_match":"one_or_more"}
        state,_=change_state(original)
        self.assertEqual("one_or_more",state["variable_match"])

    def test_different_quantifier_never_dropped_by_heuristic(self):
        original={"field":"type","value":"","operation":"equals",
                  "datatype":"string","match":"all","existence":"one_or_more",
                  "variable_match":"none"}
        state,_=change_state(original)
        self.assertEqual("none",state["variable_match"])


if __name__=="__main__":
    unittest.main()
