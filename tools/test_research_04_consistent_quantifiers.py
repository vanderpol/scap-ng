#!/usr/bin/env python3
"""#235: preserve nested Windows record semantics with one consistent vocabulary."""
import unittest
from copy import deepcopy
from jsonschema import Draft202012Validator
from research_04_consistent_quantifiers import (
    to_consistent, from_consistent, schema_for_consistent,
    document_to_consistent, document_to_flat, modernize, demodernize,
)

ORIGINAL_WMI={
    'items':'at_least_one','match':'all','scope':'states','or':[
        {'result':{'records':'at_least_one','match':'all',
                   'domainrole':{'is':'1'}}},
        {'result':{'records':'at_least_one','match':'all',
                   'domainrole':{'is':'3'}}}
    ]
}
ORIGINAL_FIELDS={
    'items':'if_present','match':'all','scope':'fields','and':[
        {'setuid':{'is':False}},{'setgid':{'is':False}}
    ],'all_fields_must_exist':True,
}

class ConsistentAuthoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Deliberately minimal external base; full schema integration is exercised
        # against the real repository schema in the pinned 872-Assessment workflow.
        base={'$schema':'https://json-schema.org/draft/2020-12/schema',
              '$defs':{'requirement':{'oneOf':[
                  {'type':'object','required':['items'],'properties':{
                      'items':{'enum':['at_least_one','exactly_one','none','if_present','legacy_all_exist']}},
                      'additionalProperties':False},
                  {'type':'object','required':['items','match','value'],
                      'properties':{'items':{'const':'at_least_one'},
                                    'match':{'const':'some'},'value':{'type':'object'}},
                      'additionalProperties':False},
                  {'type':'object','required':['items','match','value'],
                      'properties':{'items':{'const':'at_least_one'},
                                    'match':{'const':'all'},'value':{'type':'object'}},
                      'additionalProperties':False},
                  {'type':'object','required':['items','match','value'],
                      'properties':{'items':{'const':'if_present'},
                                    'match':{'const':'all'},'value':{'type':'object'}},
                      'additionalProperties':False},
              ]}}}
        schema=schema_for_consistent(base)
        Draft202012Validator.check_schema(schema)
        cls.validator=Draft202012Validator({'$schema':base['$schema'],
                                             '$defs':schema['$defs'],
                                             '$ref':'#/$defs/requirement'})

    def test_original_windows_full_state_or(self):
        authored=to_consistent(ORIGINAL_WMI)
        self.assertNotIn('scope',str(authored))
        self.assertEqual(['states'],[k for k in authored if k=='states'])
        self.assertEqual(ORIGINAL_WMI,from_consistent(authored))
        self.assertTrue(self.validator.is_valid(authored))
        branches=authored['states']['or']
        self.assertEqual(['1','3'],[x['result']['domainrole']['is'] for x in branches])
        self.assertTrue(all(x['result']['match']=='all' for x in branches))

    def test_scope_fields_required_without_true(self):
        authored=to_consistent(ORIGINAL_FIELDS)
        self.assertEqual('all',authored['fields']['presence'])
        self.assertNotIn('all_fields_must_exist',str(authored))
        self.assertEqual(ORIGINAL_FIELDS,from_consistent(authored))
        self.assertTrue(self.validator.is_valid(authored))
        self.assertEqual(False,authored['fields']['and'][0]['setuid']['is'])

    def test_some_items_becomes_at_least_one(self):
        original={'items':'at_least_one','match':'some','trustee_name':{'is':'Guests'}}
        new=to_consistent(original)
        self.assertEqual('at_least_one',new['match'])
        self.assertEqual(original,from_consistent(new))
        self.assertTrue(self.validator.is_valid(new))

    def test_some_records_becomes_at_least_one(self):
        original={'items':'at_least_one','match':'all','result':{
            'records':'at_least_one','match':'some','domainrole':{'is':'1'}}}
        new=to_consistent(original)
        self.assertEqual('at_least_one',new['result']['match'])
        self.assertEqual(original,from_consistent(new))
        self.assertTrue(self.validator.is_valid(new))

    def test_literal_comparator_value_some_is_not_renamed(self):
        original={'items':'at_least_one','match':'some',
                  'value':{'is':'some','valid':True}}
        converted=to_consistent(original)
        self.assertEqual('some',converted['value']['is'])
        self.assertEqual(True,converted['value']['valid'])
        self.assertEqual(original,from_consistent(converted))

    def test_nested_groups_round_trip(self):
        original={'items':'at_least_one','match':'all','scope':'states','and':[
            {'scope':'fields','and':[{'x':{'is':1}}, {'y':{'is':2}}],
             'all_fields_must_exist':True},
            {'scope':'fields','or':[{'x':{'is':3}}, {'y':{'is':4}}]},
        ]}
        new=to_consistent(original)
        self.assertEqual('all',new['states']['and'][0]['fields']['presence'])
        self.assertEqual(original,from_consistent(new))
        self.assertTrue(self.validator.is_valid(new))

    def test_reject_unsupported_and_ambiguous_scopes(self):
        candidates=[
            {'states':{'or':[]}},
            {'states':{'or':[{'x':{'is':1}}]}},
            {'fields':{'and':[]}},
            {'states':{'and':[{'x':{'is':1}},{'y':{'is':2}}],
                       'presence':'all'}},
            {'states':{'and':[{'x':{'is':1}},{'y':{'is':2}}],
                       'or':[{'z':{'is':3}}]}},
            {'scope':'states','or':[{'x':{'is':1}},{'y':{'is':2}}]},
            {'states':{'or':[{'x':{'is':1}},{'y':{'is':2}}]},
             'fields':{'and':[{'x':{'is':1}}]}},
            {'condition':{'x':{'is':1}}},
        ]
        for bad in candidates:
            candidate={'items':'at_least_one','match':'all',**deepcopy(bad)}
            with self.subTest(candidate=candidate):
                self.assertFalse(self.validator.is_valid(candidate))
                with self.assertRaises((ValueError,TypeError,KeyError)):
                    from_consistent(candidate)

    def test_cannot_flatten_or_of_whole_states_to_per_record_membership(self):
        # A mixed-record population [1,3] satisfies a per-record membership
        # test but NOT all records match the same whole State alternative.
        records=['1','3']
        state_1=all(record=='1' for record in records)
        state_3=all(record=='3' for record in records)
        wrong_membership=all(record in ('1','3') for record in records)
        self.assertFalse(state_1 or state_3)
        self.assertTrue(wrong_membership)

if __name__=='__main__':
    unittest.main()