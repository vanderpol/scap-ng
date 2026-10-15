#!/usr/bin/env python3
"""0.4 research: static array folding + State field-key + exact pair aliases.

Every simplification must expand into the EXACT parsed source document after
reconstructing the static Variable. value_match is never changed by require.
"""
import json
from copy import deepcopy
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from research_static_literal_collections import inline_constants, reexpand_constants
from research_04_field_key_authoring import fold_document, unfold_document
from research_04_quantifier_aliases import shorten_pair, expand_pair

ALL={"existence":"one_or_more","match":"all"}
SOME={"existence":"one_or_more","match":"one_or_more"}

def source_with_static_arrays():
    return {
        "assessment":{
            "mode":"automated",
            "variables":{
                "directories-variable":{
                    "kind":"constant","datatype":"string",
                    "expression":{"literal":["/lib","/lib64","/usr/lib","/usr/lib64"]}
                },
                "permitted-owner-uids-variable":{
                    "kind":"constant","datatype":"integer",
                    "expression":{"literal":["0","1000"]}
                },
            },
            "tests":{
                "library-dir-test":{
                    "capability":"unix.file",
                    "object":{
                        "capability":"unix.file",
                        "select":{
                            "directory":{
                                "value":{"variable":"directories-variable"},
                                "operation":"equals",
                                "datatype":"string",
                                "value_match":"one"
                            }
                        }
                    },
                    "states":[
                        {"field":"owner_uid",
                         "value":{"variable":"permitted-owner-uids-variable"},
                         "operation":"equals","datatype":"integer",
                         "value_match":"one","existence":"one_or_more",
                         "match":"all"},
                        {"field":"full_path","value":"/lib",
                         "operation":"equals",
                         "existence":"one_or_more","match":"one_or_more"},
                    ],
                    "reported_elements":"all",
                    "states_match":"all",
                    "existence":"one_or_more","match":"all",
                }
            },
            "evaluate":{"test":"library-dir-test"},
        }
    }

def shorten_folded_compiled_prototype(fielded):
    compact=deepcopy(fielded)
    test=compact["assessment"]["tests"]["library-dir-test"]
    compact["assessment"]["tests"]["library-dir-test"]=shorten_pair(
        test,pair=ALL,label="at_least_one_all_match"
    )
    test=compact["assessment"]["tests"]["library-dir-test"]
    assert isinstance(test["states"],list)
    for entry in test["states"]:
        field,payload=next(iter(entry.items()))
        if field=="owner_uid":
            entry[field]=shorten_pair(payload,pair=ALL,label="at_least_one_all_match")
        elif field=="full_path":
            entry[field]=shorten_pair(payload,pair=SOME,label="at_least_one_some_match")
    return compact

def expand_prototype(compact):
    canonical=deepcopy(compact)
    test=canonical["assessment"]["tests"]["library-dir-test"]
    canonical["assessment"]["tests"]["library-dir-test"]=expand_pair(
        test,pair=ALL,label="at_least_one_all_match"
    )
    test=canonical["assessment"]["tests"]["library-dir-test"]
    for entry in test["states"]:
        field,payload=next(iter(entry.items()))
        if field=="owner_uid":
            entry[field]=expand_pair(payload,pair=ALL,label="at_least_one_all_match")
        elif field=="full_path":
            entry[field]=expand_pair(payload,pair=SOME,label="at_least_one_some_match")
    return unfold_document(canonical)


class FieldKeyStaticCollectionCompatibility(unittest.TestCase):
    def test_exact_whole_assessment_transform_order(self):
        original=source_with_static_arrays()
        folded,proof=inline_constants(original)
        self.assertEqual(len(proof),2)
        fielded,counters=fold_document(folded)
        self.assertEqual(counters["field_key_compacted"],2)
        compact=shorten_folded_compiled_prototype(fielded)

        node=compact["assessment"]["tests"]["library-dir-test"]
        selector=node["object"]["select"]["directory"]
        self.assertEqual(selector["value"],["/lib","/lib64","/usr/lib","/usr/lib64"])
        self.assertEqual(selector["value_match"],"one")  # independent of require
        field_payload=node["states"][0]["owner_uid"]
        self.assertEqual(field_payload["value"],[0,1000])
        self.assertEqual(field_payload["value_match"],"one")
        self.assertEqual(field_payload["require"],"at_least_one_all_match")
        self.assertEqual(node["states"][1]["full_path"]["require"],"at_least_one_some_match")
        self.assertEqual(node["require"],"at_least_one_all_match")

        self.assertEqual(expand_prototype(compact),folded)
        self.assertEqual(reexpand_constants(expand_prototype(compact),proof),original)

    def test_static_inlining_and_field_key_dont_rewrite_value_match(self):
        original=source_with_static_arrays()
        normalized,_=inline_constants(original)
        compact,_=fold_document(normalized)
        compact=shorten_folded_compiled_prototype(compact)
        self.assertEqual(compact["assessment"]["tests"]["library-dir-test"]
                         ["object"]["select"]["directory"]["value_match"],"one")
        self.assertEqual(compact["assessment"]["tests"]["library-dir-test"]
                         ["states"][0]["owner_uid"]["value_match"],"one")

    def test_field_named_value_can_contain_literal_array_and_pair_alias(self):
        field={
            "assessment":{"tests":{"t":{"states":[
                {"field":"value","value":["A","B"],"datatype":"string",
                 "operation":"equals","value_match":"one",
                 "existence":"one_or_more","match":"all"}]}}}
        }
        f,_=fold_document(field)
        payload=f["assessment"]["tests"]["t"]["states"][0]["value"]
        shortened=shorten_pair(payload,pair=ALL,label="at_least_one_all_match")
        f["assessment"]["tests"]["t"]["states"][0]["value"]=shortened
        self.assertEqual(shortened["value"],["A","B"])
        self.assertEqual(shortened["value_match"],"one")
        f["assessment"]["tests"]["t"]["states"][0]["value"]=expand_pair(
            shortened,pair=ALL,label="at_least_one_all_match"
        )
        self.assertEqual(unfold_document(f),field)

    def test_no_alias_can_replace_array_value_match(self):
        pair={"value":["A","B"],"datatype":"string","operation":"equals",
              "value_match":"one","existence":"one_or_more","match":"all"}
        shortened=shorten_pair(pair,pair=ALL,label="at_least_one_all_match")
        self.assertEqual(shortened["value_match"],"one")
        self.assertEqual(expand_pair(shortened,pair=ALL,label="at_least_one_all_match"),pair)
        with self.assertRaisesRegex(ValueError,"conflict"):
            expand_pair({"require":"at_least_one_all_match","existence":"one_or_more"},
                        pair=ALL,label="at_least_one_all_match")

    def test_array_selector_requires_explicit_value_match_in_03_schema(self):
        """Exercise the actual 0.3 shared contract, not a hand-written copy."""
        repo_root=Path(__file__).resolve().parents[1]
        schema=json.loads((repo_root/"schema/v0.3.0/capability-common.schema.json").read_text())
        validator_obj=Draft202012Validator({
            "$schema":"https://json-schema.org/draft/2020-12/schema",
            "$defs":schema["$defs"],
            "$ref":"#/$defs/object_entity_base",
        })
        valid={
            "value":["/lib","/lib64"],"operation":"equals",
            "datatype":"string","value_match":"one"
        }
        self.assertFalse(list(validator_obj.iter_errors(valid)))
        invalid=deepcopy(valid)
        del invalid["value_match"]
        self.assertTrue(list(validator_obj.iter_errors(invalid)))
        validator_state=Draft202012Validator({
            "$schema":"https://json-schema.org/draft/2020-12/schema",
            "$defs":schema["$defs"],
            "$ref":"#/$defs/state_entity_base",
        })
        state={**valid,"existence":"one_or_more","match":"all"}
        self.assertFalse(list(validator_state.iter_errors(state)))
        del state["value_match"]
        self.assertTrue(list(validator_state.iter_errors(state)))

    def test_must_reconstruct_field_shape_before_reexpand_path_identity(self):
        original=source_with_static_arrays()
        folded,proof=inline_constants(original)
        fielded,_=fold_document(folded)
        # Static literal paths recorded under the canonical field wrapper.
        # The Object source path does not change; the State source path does
        # change under field-as-key. Consequently provenance-based reverse
        # expansion must happen after field-key lowering.
        with self.assertRaises((ValueError,KeyError,TypeError)):
            reexpand_constants(fielded,proof)
        self.assertEqual(reexpand_constants(unfold_document(fielded),proof),original)

if __name__=="__main__":
    unittest.main()
