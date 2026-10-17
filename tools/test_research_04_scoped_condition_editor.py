#!/usr/bin/env python3
"""Issue #235: editor-scope collision regression, scoped State/field logic.

Guards the only dangerous accidental substitution: alternative *whole*
WMI States being treated as an OR of individual fields/records. Complete
source reconstruction is independently exercised by the 872-Assessment CI.
"""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from research_04_fixed_require_editor import (
    state_condition_to_logic,logic_to_state_condition,
    to_fixed_requirement,from_fixed_requirement,
)
from research_english_first_04_evaluate import reject_naive_wmi_alternative_merge

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"research/assessment-simplification/english-first-04/fixed-require.editor.schema.json"

DOMAINROLE_1={
    "result":{"at_least_one_record_exists":True,
              "every_record":{"domainrole":{"is":"1"}}}
}
DOMAINROLE_3={
    "result":{"at_least_one_record_exists":True,
              "every_record":{"domainrole":{"is":"3"}}}
}
FILES={
    "all_of":[{"setuid":{"is":False}},{"setgid":{"is":False}}],
    "all_fields_must_exist":True
}

class ScopedAndOrEditorResearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        document=json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(document)
        cls.validator=Draft202012Validator({
            "$schema":"https://json-schema.org/draft/2020-12/schema",
            "$defs":document["$defs"],
            "$ref":"#/$defs/condition",
        })

    def test_complete_states_have_flat_scope(self):
        original={"any_of":[deepcopy(DOMAINROLE_1),deepcopy(DOMAINROLE_3)]}
        candidate=state_condition_to_logic(original)
        self.assertEqual(set(candidate),{"scope","or"})
        self.assertEqual("states",candidate["scope"])
        self.assertEqual(original,logic_to_state_condition(candidate))
        self.validator.validate(candidate)

    def test_state_fields_have_same_flat_structure(self):
        candidate=state_condition_to_logic(FILES)
        self.assertEqual("fields",candidate["scope"])
        self.assertEqual(set(candidate),{"scope","and","all_fields_must_exist"})
        self.assertEqual(FILES,logic_to_state_condition(candidate))
        self.validator.validate(candidate)

    def test_single_field_needs_no_redundant_scope(self):
        raw={"mount_options":{"at_least_one_value_is":"nosuid"}}
        self.assertEqual(raw,state_condition_to_logic(raw))
        self.assertEqual(raw,logic_to_state_condition(raw))
        self.validator.validate(raw)

    def test_nested_whole_state_and_field_groups_exact(self):
        raw={"all_states":[
            deepcopy(FILES),
            {"or":[{"mount_point":{"is":"/home"}},
                   {"mount_point":{"matches_regex":".*/home"}}]}
        ]}
        # Source State OR is called 'any_of_fields' by the previous reversible
        # grammar, so build a source-valid State group here.
        raw["all_states"][1]={"any_of_fields":[
            {"mount_point":{"is":"/home"}},
            {"mount_point":{"matches_regex":".*/home"}}]}
        canonical=state_condition_to_logic(raw)
        self.assertEqual("states",canonical["scope"])
        self.assertEqual("fields",canonical["and"][0]["scope"])
        self.assertEqual("fields",canonical["and"][1]["scope"])
        self.validator.validate(canonical)
        self.assertEqual(raw,logic_to_state_condition(canonical))

    def test_editor_and_inverse_reject_missing_or_ambiguous_scope(self):
        bad=[
            {"or":[deepcopy(DOMAINROLE_1),deepcopy(DOMAINROLE_3)]},
            {"scope":"states","or":[deepcopy(DOMAINROLE_1)]},
            {"scope":"fields","and":[{"setuid":{"is":False}}],"or":[{"setgid":{"is":False}}]},
            {"scope":"states","and":[{"setuid":{"is":False}},{"setgid":{"is":False}}],
             "all_fields_must_exist":True},
            {"scope":"items","and":[{"setuid":{"is":False}}]},
            {"scope":"fields","and":[]},
        ]
        for case in bad:
            with self.subTest(case=case):
                self.assertFalse(self.validator.is_valid(case))
                with self.assertRaises(ValueError):
                    logic_to_state_condition(case)

    def test_six_state_wmi_counterexample_not_flattenable(self):
        result=reject_naive_wmi_alternative_merge()
        self.assertEqual(["1","3"],result["counterexample_record_values"])
        self.assertEqual("false",result["source_state_alternatives"])
        self.assertEqual("true",result["incorrect_per_record_one_of"])

    def test_full_items_condition_preserved(self):
        req={"at_least_one_item_matches":{"any_of":[DOMAINROLE_1,DOMAINROLE_3]}}
        intermediate=to_fixed_requirement(req)
        self.assertEqual("at_least_one_some_match",intermediate["items"])
        self.assertEqual("states",intermediate["condition"]["scope"])
        self.assertEqual(req,from_fixed_requirement(intermediate))

if __name__=="__main__":
    unittest.main()
