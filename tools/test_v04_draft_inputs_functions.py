"""Bounded direct expected-input bindings and existing canonical function ASTs."""
from copy import deepcopy
import json
from pathlib import Path
from unittest import TestCase, main
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import OvalDocument
from v04_direct_scap_source import SourceModel, OVAL, XCCDF, xml_identity
from v04_direct_converter import AssessmentConverter, convert_rule, load_mappings, assemble_subset
from v04_native_bundle_compiler import build_bundle, verify_bundle
from validate_native_json_schemas import build_validators, document_errors
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'tests/fixtures/v04-draft-compatibility'
PIN=next(p for p in json.loads((F/'provenance.json').read_text())['sources'] if 'Windows_Defender_Firewall' in p['file'])
RULE='xccdf_mil.disa.fso_rule_SV-241989r922928_rule'

class DraftInputsFunctionsTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.validators=build_validators(ROOT/'schema/v0.4.0')

    def source(self):return SourceModel(F/PIN['file'],PIN['sha256'],draft_compatibility=True)

    def compiled(self,s):
        original=xml_identity(s.root)
        docs,b=convert_rule(s,RULE,load_mappings());docs,_=assemble_subset(s,docs,[b],load_mappings())
        for d in docs.values():
            kind,=d;self.assertFalse(list(document_errors(self.validators[kind+'.schema.json'],d)))
        raw,_=build_bundle(docs);self.assertFalse(verify_bundle(raw)['scanner_evaluated'])
        self.assertEqual(xml_identity(s.root),original)
        return docs,b

    def test_original_exports_keep_typed_input_parameter_default_and_constraints(self):
        docs,b=self.compiled(self.source())
        a=next(d['assessment'] for d in docs.values() if 'assessment' in d)
        benchmark=next(d['benchmark'] for d in docs.values() if 'benchmark' in d)
        rule=next(d['rule'] for d in docs.values() if 'rule' in d)
        input_id,=a['inputs'];contract=a['inputs'][input_id]
        self.assertEqual(contract['datatype'],'integer')
        self.assertEqual(contract['constraints']['allowed'],[0,1])
        parameter,=benchmark['parameters'];self.assertEqual(parameter['value'],1)
        self.assertEqual(parameter['resolution'],'publisher')
        self.assertEqual(rule['assessment_choices']['automated']['inputs'][input_id],{'parameter':parameter['id']})
        self.assertIn({'input':input_id},[v for test in a['tests'].values() for v in self.values(test)])
        self.assertFalse(b['independent_static_proof_eligible'])

    def values(self,value):
        if isinstance(value,dict):
            for child in value.values():yield child;yield from self.values(child)
        elif isinstance(value,list):
            for child in value:yield child;yield from self.values(child)

    def test_missing_publisher_value_remains_required_organizational_input_without_fabricated_default(self):
        s=self.source();value=s.nodes[s.benchmark_component]['xccdf_mil.disa.stig_value_domain_profile_firewall_state_var']
        for node in list(value):
            if node.tag=='{'+XCCDF+'}value' and not node.get('selector'):value.remove(node)
        docs,b=self.compiled(s);parameter,=b['policy_parameters'].values()
        self.assertEqual(parameter['resolution'],'organization')
        self.assertNotIn('value',parameter)

    def test_conflicting_unresolved_wrong_type_and_invalid_default_bindings_fail(self):
        for change in ['conflict','missing','type','default','restriction']:
            s=self.source();rule=s.rules[RULE];exports=rule.findall('.//{'+XCCDF+'}check-export')
            value=s.nodes[s.benchmark_component]['xccdf_mil.disa.stig_value_domain_profile_firewall_state_var']
            if change=='conflict':exports[0].set('value-id','xccdf_mil.disa.stig_value_domain_profile_inbound_connections_var')
            elif change=='missing':
                for e in exports:e.set('value-id','missing-value')
            elif change=='type':value.set('type','string')
            elif change=='default':next(n for n in value if n.tag=='{'+XCCDF+'}value' and not n.get('selector')).text='42'
            else:ET.SubElement(value,'{'+XCCDF+'}lower-bound').text='0'
            with self.subTest(change=change),self.assertRaises(ValueError):convert_rule(s,RULE,load_mappings())

    def test_check_import_is_not_silently_ignored(self):
        s=self.source();check=s.rules[RULE].find('{'+XCCDF+'}check');ET.SubElement(check,'{'+XCCDF+'}check-import',{'import-name':'result'})
        with self.assertRaisesRegex(ValueError,'check-import'):convert_rule(s,RULE,load_mappings())

    def test_new_function_ast_preserves_options_order_and_datatype_without_evaluation(self):
        schema=Draft202012Validator(json.loads((ROOT/'schema/v0.4.0/variable-function-expression.schema.json').read_text()))
        for name,attrs in [('count',{}),('split',{'delimiter':'\\n'}),('substring',{'substring_start':'1','substring_length':'3'})]:
            source=OvalDocument(ET.fromstring('<oval_definitions xmlns="'+OVAL+'"/>'),'original.xml');source.draft_compatibility=True
            visitor=AssessmentConverter(source,'original.xml',load_mappings())
            node=ET.Element('{'+OVAL+'}'+name,attrs);ET.SubElement(node,'{'+OVAL+'}literal_component',datatype='string').text='abc'
            original=ET.tostring(node);result=visitor.function(node)
            schema.validate(result)
            self.assertEqual(result['function']['name'],name)
            self.assertEqual(result['function']['arguments'][0],{'literal':{'datatype':'string','value':'abc'}})
            self.assertEqual(ET.tostring(node),original)
            self.assertEqual(visitor.conversion_warnings[0]['code'],'variable_function_unproved')

    def test_multiple_aggregation_preserves_arguments_and_options_only_in_draft(self):
        source=OvalDocument(ET.fromstring('<oval_definitions xmlns="'+OVAL+'"/>'),'original.xml')
        for name,attrs in [('unique',{}),('merge',{'delimiter':',','sort':'numeric','order':'descending'})]:
            node=ET.Element('{'+OVAL+'}'+name,attrs)
            for value in ['2','1']:ET.SubElement(node,'{'+OVAL+'}literal_component',datatype='int').text=value
            source.draft_compatibility=False
            with self.assertRaises(ValueError):AssessmentConverter(source,'original.xml',load_mappings()).function(node)
            source.draft_compatibility=True
            visitor=AssessmentConverter(source,'original.xml',load_mappings());result=visitor.function(node)
            Draft202012Validator(json.loads((ROOT/'schema/v0.4.0/variable-function-expression.schema.json').read_text())).validate(result)
            self.assertEqual([a['literal']['value'] for a in result['function']['arguments']],[2,1])
            self.assertEqual(result['function']['options'],attrs)
            self.assertEqual(visitor.conversion_warnings[0]['code'],'multiple_aggregation_unproved')

    def test_unknown_function_option_or_missing_required_option_rejects(self):
        source=OvalDocument(ET.fromstring('<oval_definitions xmlns="'+OVAL+'"/>'),'original.xml');source.draft_compatibility=True
        for name,attrs in [('split',{}),('count',{'invented':'1'}),('substring',{'substring_start':'oops','substring_length':'3'}),
                           ('substring',{'substring_start':'2147483648','substring_length':'3'})]:
            node=ET.Element('{'+OVAL+'}'+name,attrs);ET.SubElement(node,'{'+OVAL+'}literal_component',datatype='string').text='abc'
            with self.assertRaises(ValueError):AssessmentConverter(source,'original.xml',load_mappings()).function(node)

if __name__=='__main__':main()
