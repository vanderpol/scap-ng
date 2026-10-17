#!/usr/bin/env python3
"""Issue #235: two competing, independently invertible `require` presentations."""
import unittest
from copy import deepcopy
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from research_04_require_presentation_comparison import (
    PRESENCE, COMPARISONS, encode, decode, schema_for, transformed, reverted,
)
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/assessment-simplification/english-first-04/fixed-require.editor.schema.json'

class DualRequirementPresentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads(BASE.read_text())
        cls.validators={kind:Draft202012Validator(schema_for(cls.base,kind))
                        for kind in ('split','merged')}

    def _example(self, req):
        return {'metadata':{},'sources':{},'checks':{
            'x':{'check':'RHEL /home nosuid','inspect':'linux.partition',
                 'require':req,'report_elements':'all'}},'evaluate':{'test':'x'}}

    def test_all_fifteen_source_modes_are_source_exact_in_both_grammars(self):
        for mode in [*PRESENCE,*COMPARISONS]:
            original={'items':mode}
            if mode in COMPARISONS:
                original['condition']={'mount_options':{'at_least_one_value_is':'nosuid'}}
            for style in self.validators:
                with self.subTest(mode=mode,style=style):
                    result=encode(original,style)
                    self.assertEqual(original,decode(result,style))
                    self.assertTrue(self.validators[style].is_valid(self._example(result)))

    def test_full_document_round_trip_preserves_wmi_state_grouping(self):
        original=self._example({'items':'at_least_one_all_match',
            'condition':{'scope':'states','or':[
                {'result':{'at_least_one_record_exists':True,
                           'every_record':{'domainrole':{'is':'1'}}}},
                {'result':{'at_least_one_record_exists':True,
                           'every_record':{'domainrole':{'is':'3'}}}},
            ]}})
        original['checks']['x']['inspect']='windows.wmi.query'
        for style in self.validators:
            doc=transformed(original,style)
            self.assertEqual(original,reverted(doc,style))
            self.assertTrue(self.validators[style].is_valid(doc))
            condition=doc['checks']['x']['require']
            condition=(condition['condition'] if style=='split' else next(iter(condition.values())))
            self.assertEqual('states',condition['scope'])

    def test_none_exists_is_not_none_match(self):
        one=encode({'items':'none'},'split')
        other=encode({'items':'if_present_none_match','condition':{'value':{'is':'X'}}},'split')
        self.assertNotEqual(one,other)
        self.assertEqual('none',decode(one,'split')['items'])
        self.assertEqual('if_present_none_match',decode(other,'split')['items'])

    def test_exactly_one_exists_is_not_exactly_one_matches(self):
        a=encode({'items':'exactly_one'},'split')
        b=encode({'items':'at_least_one_one_match','condition':{'value':{'is':'X'}}},'split')
        self.assertNotEqual(a,b)
        self.assertEqual('exactly_one',decode(a,'split')['items'])
        self.assertEqual('at_least_one_one_match',decode(b,'split')['items'])

    def test_legacy_all_exist_does_not_silently_turn_into_at_least_one(self):
        a=encode({'items':'all_exist_all_match','condition':{'value':{'is':'X'}}},'split')
        self.assertEqual('legacy_all_exist',a['items'])
        self.assertEqual('all_exist_all_match',decode(a,'split')['items'])

    def test_empty_or_unexpected_forms_fail_closed(self):
        bad_split=[{}, {'items':'at_least_one','match':'all'},
            {'items':'none','condition':{'value':{'is':1}}},
            {'items':'exactly_one','match':'none','condition':{'value':{'is':1}}},
            {'items':'at_least_one','match':'all','condition':{}},
            {'items':'at_least_one','match':'all','condition':{'value':{'is':'X'}},'extra':1},
            {'items':'all_exist'}, {'items':'at_least_one','match':'any','condition':{'value':{'is':'X'}}}]
        bad_merged=[{}, {'at_least_one_exists':False},
            {'at_least_one_exists':{'value':{'is':'X'}}},
            {'at_least_one_exists_and_all_match':True},
            {'at_least_one_exists_and_all_match':{}},
            {'at_least_one_exists':True,'none_exist':True},
            {'unknown_combined_phrase':{'value':{'is':'X'}}}]
        for style, cases in (('split',bad_split),('merged',bad_merged)):
            for req in cases:
                with self.subTest(style=style,req=req):
                    self.assertFalse(self.validators[style].is_valid(self._example(req)))
                    with self.assertRaises((ValueError,TypeError)):
                        decode(req,style)

    def test_incorrect_group_scope_rejected_by_existing_condition_contract(self):
        wrong={'or':[{'result':{'every_record':{'domainrole':{'is':'1'}}}},
                     {'result':{'every_record':{'domainrole':{'is':'3'}}}}]}
        for style in self.validators:
            req=encode({'items':'at_least_one_all_match','condition':wrong},style)
            self.assertFalse(self.validators[style].is_valid(self._example(req)))

if __name__=='__main__':
    unittest.main()