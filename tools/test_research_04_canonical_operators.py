#!/usr/bin/env python3
"""Issue #235: existing SCAP-NG operators rather than English-first aliases."""
import unittest
from copy import deepcopy
from jsonschema import Draft202012Validator
from research_04_canonical_operators import (
    ALIASES,INVERSE,FRIENDLY_TO_SOURCE,PREFIXES,
    change_comparators,require_to_canonical,require_from_canonical,
    to_canonical_document,from_canonical_document,schema_for_canonical,
)

WMI={'items':'at_least_one','match':'all','states':{'or':[
    {'result':{'records':'at_least_one','match':'all','domainrole':{'is':'1'}}},
    {'result':{'records':'at_least_one','match':'all','domainrole':{'is':'3'}}},
]}}

class CanonicalOperators(unittest.TestCase):
    def test_all_original_04_operators_are_inverted(self):
        expected={'is':'equals','is_not':'not_equal',
            'equals_ignoring_case':'case_insensitive_equals',
            'is_not_ignoring_case':'case_insensitive_not_equal',
            'at_least':'greater_than_or_equal',
            'at_most':'less_than_or_equal',
            'version_at_least':'version_greater_than_or_equal'}
        self.assertEqual(expected,FRIENDLY_TO_SOURCE)
        self.assertEqual(len(ALIASES),len(INVERSE))
        for alias,native in ALIASES.items():
            with self.subTest(alias=alias):
                value={'operand': [True, False]}
                authored={alias:value}
                updated=change_comparators(authored,forward=True)
                self.assertEqual({native:value},updated)
                self.assertEqual(authored,change_comparators(updated,forward=False))

    def test_windows_wmi_nested_record_state_alternatives(self):
        new=require_to_canonical(WMI)
        self.assertEqual('states',next(k for k in new if k=='states'))
        self.assertEqual(['1','3'],[x['result']['domainrole']['equals']
                                     for x in new['states']['or']])
        self.assertEqual(WMI,require_from_canonical(new))
        self.assertEqual('all',new['states']['or'][0]['result']['match'])
        self.assertEqual('at_least_one',new['states']['or'][0]['result']['records'])

    def test_existing_case_insensitive_operator(self):
        original={'items':'at_least_one','match':'at_least_one',
                  'trustee_name':{'equals_ignoring_case':'Guests'}}
        updated=require_to_canonical(original)
        self.assertEqual({'case_insensitive_equals':'Guests'},updated['trustee_name'])
        self.assertEqual(original,require_from_canonical(updated))

    def test_negative_comparison_and_bounds(self):
        src={'items':'at_least_one','match':'all','fields':{'and':[
            {'a':{'is_not':False}},
            {'b':{'at_least':48}},
            {'c':{'at_most':168}},
            {'d':{'is_not_ignoring_case':'Admins'}},
        ]}}
        updated=require_to_canonical(src)
        fields=updated['fields']['and']
        self.assertEqual({'not_equal':False},fields[0]['a'])
        self.assertEqual({'greater_than_or_equal':48},fields[1]['b'])
        self.assertEqual({'less_than_or_equal':168},fields[2]['c'])
        self.assertEqual({'case_insensitive_not_equal':'Admins'},fields[3]['d'])
        self.assertEqual(src,require_from_canonical(updated))

    def test_prefixed_field_cardinality(self):
        orig={'items':'at_least_one','match':'all',
              'mount_options':{'at_least_one_value_is':'nosuid'}}
        updated=require_to_canonical(orig)
        self.assertEqual({'at_least_one_value_equals':'nosuid'},updated['mount_options'])
        self.assertEqual(orig,require_from_canonical(updated))
        orig2={'items':'if_present','match':'all',
               'stdout_line':{'when_present_matches_regex':r'KeepAlive On'}}
        self.assertEqual(orig2,require_to_canonical(orig2))
        self.assertEqual(orig2,require_from_canonical(orig2))

    def test_source_operands_and_boolean_data_unmodified(self):
        original={'metadata':{'id':'SV-test'},'sources':{
            'query':{'where':{'username':{'equals':'bob'}},'read_only':False}},
            'checks':{'a':{'require':deepcopy(WMI)}}}
        updated=to_canonical_document(original)
        self.assertEqual(original['sources'],updated['sources'])
        self.assertEqual(original['metadata'],updated['metadata'])
        self.assertEqual(original,from_canonical_document(updated))

    def test_schema_rejects_aliases_at_nested_levels(self):
        base={'$schema':'https://json-schema.org/draft/2020-12/schema',
          '$defs':{'requirement':{'oneOf':[
            {'type':'object','required':['items'],'properties':{
                'items':{'enum':['at_least_one']}},'additionalProperties':False},
            {'type':'object','required':['items','match','value'],
             'properties':{'items':{'const':'at_least_one'},'match':{'const':'all'},
                           'value':{'type':'object'}},'additionalProperties':False},
          ]}}}
        schema=schema_for_canonical(base)
        Draft202012Validator.check_schema(schema)
        v=Draft202012Validator({'$schema':base['$schema'],'$defs':schema['$defs'],
                               '$ref':'#/$defs/requirement'})
        correct={'items':'at_least_one','match':'all','value':{'equals':True}}
        self.assertTrue(v.is_valid(correct))
        for alias in ['is','equals_ignoring_case','at_least',
                      'at_least_one_value_is','when_present_at_least_one_value_is']:
            bad=deepcopy(correct);bad['value']={alias:'x'}
            with self.subTest(alias=alias):
                self.assertFalse(v.is_valid(bad))
        self.assertTrue(v.is_valid({'items':'at_least_one'}))

if __name__=='__main__':
    unittest.main()