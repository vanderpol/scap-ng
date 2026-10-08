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
        self.assertNotIn("value_match",state)
        self.assertTrue(any(x.get("reason")=="single-literal State value has one comparison operand" for x in edits))

    def test_rewritten_actual_ntuser_filter_passes_generated_state_schema(self):
        from pathlib import Path
        import json
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
        from generate_capability_schema import generate
        from validate_native_json_schemas import schema_store

        root=Path(__file__).resolve().parents[1]
        mapping=json.loads((root/"schema/v0.3.0/capability-mappings/supported/windows.ntuser.json").read_text())
        generated=generate(mapping,root,schema_version="0.3.0")
        sources=schema_store(root/"schema/v0.3.0")
        registry=Registry().with_resources(
            (uri,Resource.from_contents(schema)) for uri,schema in sources.items()
        )
        authored={
            "state_title":"This state filters out all items where the type and value were not collected",
            "capability":"windows.ntuser",
            "state":{
                "field":"type","value":"","operation":"equals","datatype":"string",
                "match":"all","variable_match":"one_or_more","existence":"one_or_more",
            },
        }
        rewritten,_=change_state(authored["state"])
        authored["state"]=rewritten
        v=Draft202012Validator(generated["$defs"]["state"],registry=registry)
        errors=list(v.iter_errors(authored))
        self.assertEqual([], [str(e) for e in errors])

    def test_true_variable_reference_retains_required_quantifier(self):
        original={"field":"type","value":{"variable":"expected-type-variable"},
                  "operation":"equals","datatype":"string","match":"all",
                  "existence":"one_or_more","variable_match":"one_or_more"}
        state,_=change_state(original)
        self.assertEqual("one_or_more",state["value_match"])

    def test_old_key_is_renamed_for_native_v03_output(self):
        old={"field":"type","value":{"input":"authorized-types"},
             "operation":"equals","datatype":"string",
             "match":"all","existence":"one_or_more","variable_match":"one"}
        state,edits=change_state(old)
        self.assertNotIn("variable_match",state)
        self.assertEqual(state["value_match"],"one")
        self.assertTrue(any(e.get("original_key")=="variable_match" and
                            e.get("candidate_key")=="value_match" for e in edits))

    def test_ambiguous_legacy_and_new_keys_are_rejected(self):
        old={"field":"type","value":{"input":"authorized-types"},
             "operation":"equals","datatype":"string",
             "match":"all","existence":"one_or_more",
             "variable_match":"all","value_match":"one"}
        with self.assertRaisesRegex(ValueError,"conflicting variable_match and value_match"):
            change_state(old)

    def test_collection_retains_quantifier(self):
        original={"field":"type","value":["dword","string"],"operation":"equals",
                  "datatype":"string","match":"all","existence":"one_or_more",
                  "variable_match":"one_or_more"}
        state,_=change_state(original)
        self.assertEqual("one_or_more",state["value_match"])

    def test_different_quantifier_never_dropped_by_heuristic(self):
        original={"field":"type","value":"","operation":"equals",
                  "datatype":"string","match":"all","existence":"one_or_more",
                  "variable_match":"none"}
        state,_=change_state(original)
        self.assertEqual("none",state["value_match"])


if __name__=="__main__":
    unittest.main()
