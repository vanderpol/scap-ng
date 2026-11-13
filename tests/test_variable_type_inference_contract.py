"""Candidate-only contract checks for owner-approved 0.4 Variable inference.

These tests prove schema shape, not runtime expression/status equivalence.
"""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/'schema'/'v0.4.1'
URI='https://scap-ng.dev/schema/v0.4.1/'


class InferenceSchema(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        pass
    @classmethod
    def setUpClass(cls):
        if not SCHEMA.is_dir():
            raise unittest.SkipTest('Versioned 0.4.1 pack is generated only by candidate qualification CI')
        sources={}
        for file in SCHEMA.glob('*.schema.json'):
            doc=json.loads(file.read_text(encoding='utf-8'))
            resource=Resource.from_contents(doc)
            sources[doc['$id']]=resource
            sources[URI+file.name]=resource
        cls.registry=Registry().with_resources(sources.items())
        cls.variable=json.loads((SCHEMA/'variable-expression.schema.json').read_text())
        cls.common=json.loads((SCHEMA/'capability-common.schema.json').read_text())
        cls.language=json.loads((SCHEMA/'assessment-language.schema.json').read_text())
        cls.validator=Draft202012Validator(cls.variable,registry=cls.registry)

    def test_declaration_has_no_datatype_and_is_not_a_cast(self):
        declaration=self.variable['$defs']['declaration']
        self.assertEqual(declaration['required'],['kind','expression'])
        self.assertEqual(self.variable['$id'],URI+'variable-expression.schema.json')
        self.assertEqual(json.loads((ROOT/'schema'/'variable-expression.schema.json').read_text())['$defs']['declaration']['required'],['kind','datatype','expression'])
        self.assertNotIn('datatype',declaration['properties'])
        self.assertFalse(any('datatype' in c.get('then',{}).get('properties',{})
                             for c in declaration['allOf']))
        for expr in ({'count':{'literal':['x','y']}},
                     {'literal':{'datatype':'version','value':'1.02'}},
                     {'arithmetic':{'arithmetic_operation':'add',
                                    'values':[{'literal':1},{'literal':2}]}}):
            self.validator.validate({'kind':'local','expression':expr})
        errors=list(self.validator.iter_errors({'kind':'local','datatype':'string',
                                               'expression':{'literal':'1'}}))
        self.assertTrue(errors)

    def test_041_assessment_version_is_not_040(self):
        authored=json.loads((SCHEMA/'assessment.schema.json').read_text())
        self.assertEqual(authored['$id'], URI+'assessment.schema.json')
        version=authored['properties']['assessment']['properties']['specification']['properties']['version']
        self.assertEqual(version['const'],'0.4.1')
        original=json.loads((ROOT/'schema'/'assessment.schema.json').read_text())
        self.assertNotIn('const',
                         original['properties']['assessment']['properties']['specification']['properties']['version'])

    def test_explicit_typed_evidence_and_require_are_preserved(self):
        self.assertIn('string',self.common['$defs']['native_datatype']['enum'])
        self.assertIn('version',self.common['$defs']['native_datatype']['enum'])
        self.assertIn('datatype',
                      self.language['$defs']['scalar_field_predicate']['properties'])
        self.assertNotIn('datatype',
                         self.language['$defs']['scalar_field_predicate'].get('required',[]))
        literal=[branch['properties']['literal'] for branch in self.variable['$defs']['expression']['oneOf']
                 if branch.get('required')==['literal']][0]
        typed=[x for x in literal['oneOf'] if x.get('type')=='object']
        self.assertEqual(len(typed),1)
        self.assertEqual(typed[0]['required'],['datatype','value'])

    def test_unapproved_generic_function_remains_invalid(self):
        bad={'kind':'local','expression':{'function':{'name':'cast',
               'arguments':[{'literal':1}],'options':{'datatype':'string'}}}}
        self.assertTrue(list(self.validator.iter_errors(bad)))


if __name__=='__main__':
    unittest.main()
