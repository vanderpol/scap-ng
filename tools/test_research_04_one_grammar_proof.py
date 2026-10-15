#!/usr/bin/env python3
"""One-grammar 0.4 authoring acceptance and fail-closed proof, research only."""
import unittest
from copy import deepcopy
from research_04_one_grammar_proof import (
    CODES,PAIR_BY_NAME,EXISTS,MATCHES,make_single,lower_single,
    normalize_inert_source_checks,from_source_pair,back_to_source_pair,
    operator_enum,
)

class SingleGrammarTests(unittest.TestCase):
    def sample(self):
        return {"assessment":{
            "mode":"automated","id":"synthetic.one-grammar",
            "tests":{
              "demo":{
                "capability":"windows.wmi.query",
                "object":{"capability":"windows.wmi.query",
                    "select":{"hive":{"operation":"equals","value":"local_machine"},
                              "paths":{"operation":"equals","value":["a","b"],
                                       "value_match":"one","datatype":"string"}}},
                "states":[
                  {"field":"value","record":{
                    "existence":"one_or_more","match":"one_or_more",
                    "fields":{
                       "productstate":{"operation":"bitwise_and","value":4096,
                                       "existence":"one_or_more","match":"all"},
                       "specversion":{"operation":"pattern_match","value":"2\\.0",
                                      "existence":"one_or_more","match":"one_or_more"}
                    }}},
                  {"all":[{"field":"flag","operation":"pattern_match","value":"PROMISC",
                           "existence":"one_or_more","match":"none"},
                          {"field":"all","operation":"not_equal","value":0,
                           "existence":"one","match":"one"}]}
                ],
                "reported_elements":"all","existence":"one_or_more","match":"all"
              },
              "one-statefree":{
                 "capability":"windows.registry",
                 "existence":"one","match":"one",
                 "object":{"capability":"windows.registry"},
                 "reported_elements":"all",
              },
            },
            "evaluate":{"all":[{"test":"demo"},{"test":"one-statefree"}]}
        }}
    def test_20_unique_explicit_pair_names(self):
        self.assertEqual(len(CODES),20)
        self.assertEqual(len(PAIR_BY_NAME),20)
        for pair,name in CODES.items():
            self.assertEqual(PAIR_BY_NAME[name],pair)
            self.assertIsInstance(name,str)
    def test_complex_record_array_negative_and_state_free(self):
        original=self.sample()
        compact,counters,notes=make_single(original)
        self.assertEqual(len(notes),1) # one/one with no State -> one/all
        self.assertEqual(compact["assessment"]["tests"]["one-statefree"]["require"],"only_one_exists")
        test=compact["assessment"]["tests"]["demo"]
        self.assertEqual(test["require"],"at_least_one_exists_and_all_match")
        self.assertEqual(test["states"][0]["value"]["record"]["require"],
                         "at_least_one_exists_and_some_match")
        self.assertEqual(test["states"][0]["value"]["record"]["fields"]["productstate"]["bitwise_and"],4096)
        self.assertEqual(test["states"][1]["all"][0]["flag"]["require"],
                         "at_least_one_exists_and_none_match")
        self.assertEqual(test["states"][1]["all"][1]["all"]["require"],
                         "only_one_exists_and_only_one_matches")
        self.assertEqual(test["object"]["select"]["paths"]["value_match"],"one")
        self.assertEqual(test["object"]["select"]["paths"]["equals"],["a","b"])
        self.assertEqual(lower_single(compact),normalize_inert_source_checks(original,notes))
        self.assertEqual(original,self.sample())
        self.assertGreaterEqual(counters["record_field_require"],2)
    def test_source_exact_with_state_only_one(self):
        doc=self.sample()
        doc["assessment"]["tests"].pop("one-statefree")
        short,counts,notes=make_single(doc)
        self.assertEqual(notes,[])
        self.assertEqual(lower_single(short),doc)
    def test_no_hidden_default_for_missing_pair(self):
        with self.assertRaisesRegex(ValueError,"Missing explicit"):
            from_source_pair({"operation":"equals","value":0},
                             scope="field",with_states=True,notes=[],label="owner_uid")
        with self.assertRaisesRegex(ValueError,"Missing explicit"):
            from_source_pair({"existence":"one_or_more","operation":"equals","value":0},
                             scope="field",with_states=True,notes=[],label="owner_uid")
    def test_conflicts_and_bad_names_fail(self):
        for data in (
          {"require":"none_exist","existence":"none"},
          {"require":"not-a-real-preset"},
        ):
            with self.subTest(data=data),self.assertRaises(ValueError):
                back_to_source_pair(data,scope="field",with_states=True)
    def test_bad_operator_rejected(self):
        doc=self.sample()
        doc["assessment"]["tests"]["demo"]["states"][1]["all"][0]["operation"]="not_pattern_match"
        with self.assertRaisesRegex(ValueError,"Nonstandard comparison operator"):
            make_single(doc)
    def test_object_set_filter_actions_with_native_predicate_and_missing(self):
        doc=self.sample()
        test=doc["assessment"]["tests"]["demo"]
        test["object"]={
            "capability":"unix.file",
            "set":{"operator":"union","operands":[
                {"object":{"capability":"unix.file",
                           "select":{"directory":{"operation":"equals","value":"/bin"}}},
                 "filters":[
                    {"action":"exclude","field":"mode",
                     "operation":"greater_than","value":493,
                     "existence":"one_or_more","match":"all"},
                    {"action":"include","all":[
                        {"field":"owner_uid","operation":"equals","value":0,
                         "existence":"one_or_more","match":"all"},
                        {"field":"group_uid","operation":"equals","value":0,
                         "existence":"one_or_more","match":"all"}]},
                 ]}
            ]}
        }
        short,counts,notes=make_single(doc)
        filters=short["assessment"]["tests"]["demo"]["object"]["set"]["operands"][0]["filters"]
        self.assertEqual(counts["object_set_filter_verbs"],2)
        self.assertEqual(filters[0]["exclude"]["mode"]["greater_than"],493)
        self.assertEqual(filters[0]["exclude"]["mode"]["require"],
                         "at_least_one_exists_and_all_match")
        self.assertEqual(filters[1]["include"]["all"][0]["owner_uid"]["equals"],0)
        self.assertEqual(lower_single(short),normalize_inert_source_checks(doc,notes))

    def test_nested_windows_collector_field_requirement_not_a_second_dialect(self):
        doc=self.sample()
        test=doc["assessment"]["tests"]["demo"]
        test["object"]={"capability":"windows.cmdlet",
            "collect":{"select":{"fields":{"property":{
                "value":"Enabled","operation":"equals",
                "existence":"one_or_more","match":"all"}}}}}
        short,counts,notes=make_single(doc)
        inner=short["assessment"]["tests"]["demo"]["object"]["collect"]["select"]["fields"]["property"]
        self.assertEqual(inner["require"],"at_least_one_exists_and_all_match")
        self.assertEqual(inner["equals"],"Enabled")
        self.assertNotIn("existence",inner)
        self.assertNotIn("operation",inner)
        self.assertEqual(counts["other_typed_field_require"],1)
        self.assertEqual(lower_single(short),normalize_inert_source_checks(doc,notes))

    def test_every_native_operator_is_covered_by_one_key(self):
        native,compact=operator_enum()
        self.assertEqual(len(native),len(compact))
        self.assertIn("matches_regex",compact)
        self.assertIn("bitwise_and",compact)
        self.assertIn("version_greater_than",compact)
        self.assertNotIn("pattern_match",compact)
    def test_no_undocumented_source_rewrite_of_state_bearing_none(self):
        doc=self.sample()
        test=doc["assessment"]["tests"]["demo"]
        test["existence"]="none"
        test["match"]="all"
        short,_,notes=make_single(doc)
        self.assertEqual(short["assessment"]["tests"]["demo"]["require"],"none_exist")
        self.assertEqual(len(short["assessment"]["tests"]["demo"]["states"]),2)
        self.assertEqual(lower_single(short),normalize_inert_source_checks(doc,notes))

if __name__=="__main__":
    unittest.main()
