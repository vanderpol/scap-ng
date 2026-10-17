#!/usr/bin/env python3
"""Issue #235: field presence belongs to State field scope, not Item count."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from research_04_field_presence_policy import to_policy, from_policy, schema_policy

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/assessment-simplification/english-first-04/fixed-require.editor.schema.json'


def whole_doc(check):
    return {'metadata':{},'sources':{},'checks':{'t':check},'evaluate':{'test':'t'}}


def check(require, **extras):
    return {'check':'Test','inspect':'independent.shellcommand',
            'require':require,'report_elements':'all',**extras}


class StateFieldPresencePolicies(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator=Draft202012Validator(schema_policy(json.loads(BASE.read_text())))

    def test_dns_inherited_required_field_scope(self):
        req={'items':'at_least_one','match':'all','states':{'and':[
            {'stdout_line':{'greater_than_or_equal':48}},
            {'stdout_line':{'less_than_or_equal':168}},
        ]}}
        old=whole_doc(check(req,all_state_fields_exist=True))
        new=to_policy(old)
        self.assertEqual('all',new['checks']['t']['require']['field_presence'])
        self.assertNotIn('all_state_fields_exist',new['checks']['t'])
        self.assertEqual(old,from_policy(new))
        self.assertTrue(self.validator.is_valid(new))
        self.assertEqual(2,len(new['checks']['t']['require']['states']['and']))

    def test_optional_test_field_scope_not_confused_with_items(self):
        old=whole_doc(check({'items':'at_least_one','match':'all','stdout_line':{
              'matches_regex':'KeepAlive On'}},all_state_fields_when_present=True))
        new=to_policy(old)
        self.assertEqual('at_least_one',new['checks']['t']['require']['items'])
        self.assertEqual('if_present',new['checks']['t']['require']['field_presence'])
        self.assertEqual(old,from_policy(new))
        self.assertTrue(self.validator.is_valid(new))

    def test_group_local_presence_not_hoisted(self):
        req={'items':'if_present','match':'all','fields':{'and':[
            {'setuid':{'equals':False}}, {'setgid':{'equals':False}}],
            'presence':'all'}}
        old=whole_doc(check(req))
        self.assertEqual(old,to_policy(old))
        self.assertEqual(old,from_policy(old))
        self.assertTrue(self.validator.is_valid(old))

    def test_records_do_not_inherit_or_mutate_local_quantifiers(self):
        req={'items':'at_least_one','match':'all','states':{'or':[
            {'result':{'records':'at_least_one','match':'all','domainrole':{'equals':'1'}}},
            {'result':{'records':'at_least_one','match':'all','domainrole':{'equals':'3'}}},
        ]}}
        old=whole_doc(check(req))
        self.assertEqual(old,to_policy(old))
        self.assertEqual(old,from_policy(old))
        self.assertTrue(self.validator.is_valid(old))

    def test_scoping_conflicts_are_errors_not_defaults(self):
        req={'items':'at_least_one','match':'all','stdout_line':{'equals':'x'}}
        cases=[
            check(req,all_state_fields_exist=True,all_state_fields_when_present=True),
            check(req,all_state_fields_exist=False),
            check({'items':'at_least_one','match':'all','field_presence':'all','stdout_line':{'equals':'x'}},all_state_fields_exist=True),
            check({'items':'none'},all_state_fields_exist=True),
        ]
        for c in cases:
            with self.subTest(c=c), self.assertRaises(ValueError):
                to_policy(whole_doc(c))

    def test_old_boolean_and_broad_scope_rejected_by_schema_and_decoder(self):
        good=to_policy(whole_doc(check({'items':'at_least_one','match':'all',
           'stdout_line':{'equals':'x'}},all_state_fields_exist=True)))
        for extra in [{'all_state_fields_exist':True},{'all_state_fields_when_present':True}]:
            bad=json.loads(json.dumps(good))
            bad['checks']['t'].update(extra)
            self.assertFalse(self.validator.is_valid(bad))
            with self.assertRaises(ValueError):from_policy(bad)
        for key,val in [('scope','items_and_fields'),('field_presence','unrecognized')]:
            bad=json.loads(json.dumps(good))
            bad['checks']['t']['require'][key]=val
            self.assertFalse(self.validator.is_valid(bad))

    def test_bare_presence_only_requirement_rejects_field_policy(self):
        bad=whole_doc(check({'items':'none','field_presence':'all'}))
        self.assertFalse(self.validator.is_valid(bad))

    def test_no_nested_field_presence_leak_into_record(self):
        doc=whole_doc(check({'items':'at_least_one','match':'all','result':{
            'records':'at_least_one','match':'all','field_presence':'all',
            'domainrole':{'equals':'1'}}}))
        with self.assertRaises(ValueError):from_policy(doc)

if __name__=='__main__':unittest.main()