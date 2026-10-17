#!/usr/bin/env python3
"""#235: positive and negative tests for direct-field requirements and records."""
import unittest
from copy import deepcopy
from research_04_flat_require import flatten, unflatten, records_to_flat, records_to_source, schema_for_flat
from research_04_require_presentation_comparison import PRESENCE, COMPARISONS
from jsonschema import Draft202012Validator
from pathlib import Path
import json

BASE=Path(__file__).resolve().parents[1]/'research/assessment-simplification/english-first-04/fixed-require.editor.schema.json'

class FlatAuthoringResearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=schema_for_flat(json.loads(BASE.read_text()))
        cls.validator=Draft202012Validator(cls.schema)
    def valid(self,req, inspect='linux.partition'):
        return self.validator.is_valid({'metadata':{},'sources':{},'checks':{
            'a':{'check':'fixture','inspect':inspect,'require':req,'report_elements':'all'}},
             'evaluate':{'test':'a'}})
    def test_all_fifteen_modes_reversible_without_condition(self):
        for mode in [*PRESENCE,*COMPARISONS]:
            src={'items':mode}
            if mode in COMPARISONS:src['condition']={'mount_options':{'at_least_one_value_is':'nosuid'}}
            with self.subTest(mode=mode):
                flat=flatten(src)
                self.assertNotIn('condition',flat)
                self.assertEqual(src,unflatten(flat))
                self.assertTrue(self.valid(flat))
    def test_windows_two_entire_states_reversible(self):
        cond={'scope':'states','or':[
          {'result':{'at_least_one_record_exists':True,'every_record':{'domainrole':{'is':'1'}}}},
          {'result':{'at_least_one_record_exists':True,'every_record':{'domainrole':{'is':'3'}}}}
        ]}
        src={'items':'at_least_one_all_match','condition':cond}
        f=flatten(src)
        self.assertTrue(self.valid(f,'windows.wmi.query'))
        self.assertEqual(f['scope'],'states')
        self.assertEqual(f['or'][0]['result']['records'],'at_least_one')
        self.assertEqual(f['or'][1]['result']['match'],'all')
        self.assertNotIn('at_least_one_record_exists',str(f))
        self.assertEqual(src,unflatten(f))
    def test_other_three_record_modes(self):
        for key in ('some_record','exactly_one_matching_record','no_matching_record'):
            inp={'at_least_one_record_exists':True,key:{'domainrole':{'is':'1'}}}
            f=records_to_flat(inp)
            self.assertNotIn('at_least_one_record_exists',f)
            self.assertEqual(inp,records_to_source(f))
    def test_field_keys_named_and_or_do_not_become_group_operators(self):
        for key in ('and','or','scope'):
            inp={'items':'at_least_one_all_match','condition':{key:{'is':1}}}
            f=flatten(inp)
            self.assertTrue(self.valid(f))
            self.assertEqual(inp,unflatten(f))
    def test_collision_is_rejected_not_guessed(self):
        for k in ('items','match'):
            with self.assertRaisesRegex(ValueError,'collides with reserved'):
                flatten({'items':'at_least_one_all_match','condition':{k:{'is':'X'}}})
    def test_negative_record_flags_do_not_silently_change(self):
        old={'at_least_one_record_exists':False,'every_record':{'domainrole':{'is':'1'}}}
        with self.assertRaises(ValueError):records_to_flat(old)
        with self.assertRaises(ValueError):records_to_source(old)
        for bad in [{'records':'at_least_one','match':'all'},
                    {'records':'exactly_one','match':'all','domainrole':{'is':'1'}},
                    {'records':'at_least_one','match':'unknown','domainrole':{'is':'1'}}]:
            with self.assertRaises(ValueError):records_to_source(bad)
    def test_schema_rejects_old_wrapper_or_wrong_scopes(self):
        good=flatten({'items':'at_least_one_all_match','condition':{'mount_options':{'at_least_one_value_is':'nosuid'}}})
        bad=[dict(good,condition={'value':{'is':'X'}}),
             {'items':'at_least_one','match':'all'},
             {'items':'at_least_one','match':'all','scope':'states','or':[]},
             {'items':'at_least_one','match':'all','scope':'states','or':[{'value':{'is':'1'}}]},
             {'items':'at_least_one','match':'all','scope':'nonsense','or':[{'value':{'is':'1'}}]},
             {'items':'none','value':{'is':'X'}}]
        for b in bad:
            with self.subTest(b=b):
                self.assertFalse(self.valid(b))
                with self.assertRaises((ValueError,TypeError)):
                    unflatten(b)

if __name__=='__main__':unittest.main()