"""Owner-approved 0.4 discovery grammar, not compiler/scanner execution proof."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import yaml
from jsonschema import Draft202012Validator
from test_draft202012_and_examples import schema_registry
from test_schema_integrity import ROOT,load

PROJECT=ROOT.parent


class NativeDiscoverySchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator=Draft202012Validator(load(ROOT/'rule.schema.json'),registry=schema_registry())
        cls.source=yaml.safe_load((PROJECT/'examples/organizational-input/input.rule.yaml').read_text())

    def test_omitted_authoring_index_and_explicit_native_records_are_structurally_valid(self):
        self.validator.validate(self.source)
        doc=deepcopy(self.source)
        doc['rule']['organizational_input_requirements']={'automated':[{'input':'slideshow-value','required':False,
            'uses':[{'kind':'presence','source_path':'/evaluate/if/input_provided'},
                    {'kind':'value','source_path':'/tests/registry-test/require/fields/value/equals/input'}]}]}
        self.validator.validate(doc)

    def test_legacy_tuple_bad_kind_extra_fields_and_bad_pointer_escape_reject(self):
        for use in ({'test':'registry-test','state':'synthetic-state'},
                    {'kind':'other','source_path':'/evaluate/if/input_provided'},
                    {'kind':'value','source_path':'/a~2b/input'},
                    {'kind':'value','source_path':'#/evaluate/if/input_provided'},
                    {'kind':'value','source_path':'/a/input','state':'placeholder'}):
            doc=deepcopy(self.source)
            doc['rule']['organizational_input_requirements']={'automated':[{'input':'slideshow-value','required':False,'uses':[use]}]}
            with self.subTest(use=use):self.assertTrue(list(self.validator.iter_errors(doc)))

    def test_compiled_example_has_real_input_targets_and_matching_parameter_bindings(self):
        folder=PROJECT/'examples/organizational-input'
        compiled=json.loads((folder/'compiled.rule.json').read_text());self.validator.validate(compiled)
        assessment=yaml.safe_load((PROJECT/'examples/windows-optional-organizational-input.assessment.yaml').read_text())['assessment']
        choice=compiled['rule']['assessment_choices']['automated']
        uses=compiled['rule']['organizational_input_requirements']['automated'][0]
        self.assertEqual({row['kind'] for row in uses['uses']},{'value','presence'})
        self.assertEqual(len(uses['uses']),2)
        for use in uses['uses']:
            node=assessment
            for part in use['source_path'][1:].split('/'):
                key=part.replace('~1','/').replace('~0','~')
                node=node[int(key)] if isinstance(node,list) else node[key]
            self.assertIn(node,assessment['inputs'])
            self.assertEqual(choice['inputs'][node]['parameter'],uses['input'])
        for name,kind in [('benchmark.yaml','benchmark'),('applicability.yaml','applicability')]:
            Draft202012Validator(load(ROOT/(kind+'.schema.json')),registry=schema_registry()).validate(yaml.safe_load((folder/name).read_text()))

    def test_compiler_derived_annotation_is_not_a_schema_default(self):
        schema=load(ROOT/'rule.schema.json')['properties']['rule']
        field=schema['properties']['organizational_input_requirements']
        self.assertTrue(field['readOnly']);self.assertNotIn('default',field)
        self.assertNotIn('organizational_input_requirements',schema['required'])

    def test_current_result_has_no_retired_state_slot_field(self):
        result = load(ROOT / 'assessment-result.schema.json')
        properties = result['properties']['assessment_result']['properties']
        consumed = properties['consumed_organizational_inputs']['items']['properties']
        reason = properties['reason']['oneOf'][2]['properties']
        self.assertNotIn('state_slot', consumed)
        self.assertNotIn('state_slot', reason)


if __name__=='__main__':unittest.main()
