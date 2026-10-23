#!/usr/bin/env python3
"""Enforce AND/OR for Boolean logic, preserve Item-matching quantifiers.

The 0.4.0 authoring schema retains backward-compatible logical 'all/any'
but marks them deprecated as spellings for 'and/or'. Cardinality 'all'
and 'one_or_more' are never repurposed as logical operators.
Tests schema metadata and strict validation without changing native semantics.
Refs #248 #239.
"""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, RefResolver


ROOT=Path(__file__).resolve().parents[1]
LANGUAGE=ROOT/"schema/v0.4.0/assessment-language.schema.json"


class LogicalVocabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=json.loads(LANGUAGE.read_text())
        url=cls.schema["$id"]
        cls.resolver=RefResolver.from_schema(cls.schema,store={url:cls.schema})

    def validate_part(self,name,instance):
        validator=Draft202012Validator(
            {"$ref":"#/$defs/"+name,"$defs":self.schema["$defs"]},
            resolver=self.resolver)
        return list(validator.iter_errors(instance))

    def test_evaluate_canonical_and_legacy_input_aliases_remain_schema_compatible(self):
        schema=json.loads((ROOT/"schema/v0.4.0/expression.schema.json").read_text())
        validator=Draft202012Validator(schema)
        leaf={"test":"sample-test"}
        for old,new in (("all","and"),("any","or"),("odd","xor")):
            for op in (old,new):
                with self.subTest(op=op):
                    self.assertFalse(list(validator.iter_errors({op:[leaf]})))
            self.assertTrue(list(validator.iter_errors({old:[leaf],new:[leaf]})))
        for bad in ({"and":[]},{"or":"one_or_more"},{"xor":[{"items":"all"}]}):
            self.assertTrue(list(validator.iter_errors(bad)))

    def test_both_state_entry_grammars_prefer_and_or_not_legacy_all_any(self):
        for name in ("state_entry","scoped_state_entry"):
            branches=self.schema["$defs"][name]["oneOf"]
            for old,new in (("all","and"),("any","or")):
                legacy=next(x for x in branches if x.get("required")==[old])
                preferred=next(x for x in branches if x.get("required")==[new])
                self.assertTrue(legacy["properties"][old]["deprecated"])
                self.assertFalse(preferred["properties"][new].get("deprecated",False))
                self.assertIn("Prefer '"+new+"'",legacy["properties"][old]["description"])

    def test_xor_preferred_to_legacy_odd_at_both_condition_scopes(self):
        for name in ("state_entry","scoped_state_entry"):
            branches=self.schema["$defs"][name]["oneOf"]
            old=next(x for x in branches if x.get("required")==["odd"])
            new=next(x for x in branches if x.get("required")==["xor"])
            self.assertTrue(old["properties"]["odd"]["deprecated"])
            self.assertIn("xor",old["properties"]["odd"]["description"])
            self.assertFalse(new["properties"]["xor"].get("deprecated",False))
            field={"value":{"require":"at_least_one_exists_and_all_match",
                            "equals":0}}
            self.assertFalse(self.validate_part(name,{"xor":[field,field]}))
            self.assertFalse(self.validate_part(name,{"odd":[field,field]}))
            self.assertTrue(self.validate_part(name,{
                "odd":[field],"xor":[field]}))

    def test_explicit_logic_and_old_aliases_validate_only_at_logical_scope(self):
        field={"type":{"require":"at_least_one_exists_and_all_match","equals":"dword"}}
        for op in ("all","any","and","or"):
            item={op:[field]}
            with self.subTest(operator=op):
                self.assertFalse(self.validate_part("scoped_state_entry",item),
                                 f"0.4  compatibility/regression for {op}")
        # A Boolean logical OR must contain child conditions, never a
        # quantifier that can be mistaken for a condition aggregator.
        for bad in ({"or":[]},{"or":"one_or_more"},{"one_or_more":[field]},
                    {"and":[]},{"any":"one_or_more"}):
            with self.subTest(bad=bad):
                self.assertTrue(self.validate_part("scoped_state_entry",bad))

    def test_item_existence_is_not_renamed_or_reinterpreted(self):
        # require.items one_or_more remains an explicit source population
        # check independent of state_operator=OR.
        valid={"items":"one_or_more","all_items_must":[
            {"or":[
                {"value":{"equals":"Enterprise",
                          "require":"at_least_one_exists_and_all_match"}},
                {"value":{"equals":"EnterpriseS",
                          "require":"at_least_one_exists_and_all_match"}}
            ]}
        ]}
        self.assertFalse(self.validate_part("scoped_all_items_requirement",valid))
        self.assertEqual(self.schema["$defs"]["scoped_all_items_requirement"]
                         ["properties"]["items"]["enum"],["one_or_more","may_be_absent"])

    def test_legacy_states_match_any_is_unmodified_for_fallback_cases(self):
        self.assertIn("any",self.schema["$defs"]["test"]["properties"]["states_match"]["enum"])
        # states_match any is a Test-level State-aggregation mechanism,
        # not an Item cardinality alias or an OR field operator.


if __name__=="__main__":
    unittest.main()
