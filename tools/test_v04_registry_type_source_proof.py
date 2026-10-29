"""Original-backed Registry type literals and constant multisets (#251)."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter,load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import digest,xml_identity
from v04_expanded_source_proof import ExpandedSource,ExpandedNative
from v04_native_bundle_compiler import compile_assessment_program
from audit_v04_eight_assessment_pilot import verify_program
from validate_native_json_schemas import build_validators
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/v04-registry-type-proof'
CASES=json.loads((FIXTURE/'provenance.json').read_text())['cases']
O='{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
W='{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}'

def walk(node):
    if isinstance(node,dict):
        yield node
        for value in node.values():yield from walk(value)
    elif isinstance(node,list):
        for value in node:yield from walk(value)

class RegistryTypeSourceProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=build_validators(ROOT/'schema/v0.4.0')['assessment.schema.json']
        cls.source_validator=SourceValidator(ROOT/'third_party/scap-1.4-schemas/oval_5.12.3')
    def original(self,index):
        c=CASES[index];raw=(FIXTURE/c['fixture']).read_bytes();self.assertEqual(sha256(raw).hexdigest(),c['sha256']);root=ET.fromstring(raw)
        nodes={n.get('id'):n for n in root.iter() if n.get('id')};self.assertEqual(set(nodes),{d['id'] for d in c['dependencies']})
        for d in c['dependencies']:self.assertEqual(digest(xml_identity(nodes[d['id']])),d['sha256'])
        return root
    def visitor(self,root):return AssessmentConverter(OvalDocument(root,'original.xml'),'original.xml',load_mappings())
    def proved(self,root,test):
        before=ET.tostring(root);report=check_conversion(self.visitor(root),test,self.schema)
        self.assertTrue(report['schema_valid'],report);self.assertTrue(report['compiled_operands_verified'],report);self.assertEqual(report['source_proof'],'PROVED',report);self.assertEqual(ET.tostring(root),before)
        return assessment_for(self.visitor(root),test)
    def entity(self,root):return next(root.iter(W+'type'))
    def state_id(self,root):return next(n.get('id') for n in root.iter(W+'registry_state') if n.find(W+'type') is not None)
    def test_original_closures_validate_nondeprecated_compile_and_prove(self):
        for i,c in enumerate(CASES):
            root=self.original(i);check=self.source_validator.validate(etree.fromstring(ET.tostring(root)));nodes=list(SourceInventory(OvalDocument(root,'original.xml')).nodes.values());v=closure_validity(nodes,{'original.xml':check});self.assertEqual(v['status'],'VALID',v);self.assertFalse(any(x['kind']=='deprecated' for x in v['issues']))
            for test in c['tests']:
                with self.subTest(fixture=c['fixture'],test=test):self.proved(root,test)
    def test_multi_string_literal_keeps_existing_native_type_and_value_quantifiers(self):
        a=self.proved(self.original(0),CASES[0]['tests'][0]);p=next(n['type'] for n in walk(a['tests']) if isinstance(n.get('type'),dict));self.assertEqual(p['equals'],'multi_string');self.assertEqual(p['values_matching'],'every')
    def test_constant_duplicates_and_all_four_variable_quantifiers_are_retained(self):
        for old,new in [('all','every'),('at least one','one_or_more'),('only one','exactly_one'),('none satisfy','none')]:
            root=self.original(1);e=self.entity(root);e.set('var_check',old);v=next(n for n in root.iter(O+'constant_variable') if n.get('id')==e.get('var_ref'));v.append(deepcopy(v[0]));a=self.proved(root,CASES[1]['tests'][0]);p=next(n['type'] for n in walk(a['tests']) if isinstance(n.get('type'),dict));self.assertEqual(p['equals'],['dword','dword']);self.assertEqual(p['datatype'],'string');self.assertEqual(p['value_match'],new)
    def test_unknown_types_casts_and_nondefault_new_comparators_are_rejected(self):
        for change in ['unknown','cast','pattern match','not equal']:
            root=self.original(1);e=self.entity(root);v=next(n for n in root.iter(O+'constant_variable') if n.get('id')==e.get('var_ref'))
            if change=='unknown':v[0].text='reg_qword'
            elif change=='cast':e.set('datatype','int')
            else:e.set('operation',change)
            with self.subTest(change=change),self.assertRaises(ValueError):ExpandedSource(root).state(self.state_id(root),'windows.registry')
        root=self.original(0);self.entity(root).set('operation','not equal')
        with self.assertRaisesRegex(ValueError,'requires equality'):ExpandedSource(root).state(self.state_id(root),'windows.registry')
    def test_local_enum_graphs_remain_outside_bounded_type_reader(self):
        root=self.original(1);e=self.entity(root);v=next(n for n in root.iter(O+'constant_variable') if n.get('id')==e.get('var_ref'));v.tag=O+'local_variable';v[:]=[];ET.SubElement(v,O+'literal_component',datatype='string').text='reg_dword'
        with self.assertRaises(ValueError):ExpandedSource(root).state(self.state_id(root),'windows.registry')
    def test_registry_projection_filters_cannot_be_dropped_or_inverted(self):
        root=self.original(2);a=self.proved(root,CASES[2]['tests'][0])
        for action in ['drop','exclude']:
            mutant=deepcopy(a);obj=next(n for n in walk(mutant) if 'hive' in n and n.get('filters'))
            if action=='drop':obj.pop('filters')
            else:obj['filters'][0]={'exclude':obj['filters'][0]['include']}
            self.assertFalse(list(self.schema.iter_errors({'assessment':mutant})))
            key=mutant['evaluate']['test'];self.assertNotEqual(ExpandedSource(root).test(CASES[2]['tests'][0]),ExpandedNative(mutant).test(key))
            with self.assertRaises((ValueError,AssertionError)):verify_program(mutant,compile_assessment_program(a))

    def test_registry_filter_unknown_structure_and_dependency_cycles_fail_closed(self):
        for change in ['attribute','namespace','child','cycle']:
            root=self.original(2);obj=next(n for n in root.iter(W+'registry_object') if n.findall(O+'filter'));f=obj.find(O+'filter')
            if change=='attribute':f.set('invented','true')
            elif change=='namespace':f.tag=W+'filter'
            elif change=='child':ET.SubElement(f,O+'invented')
            else:
                state=next(n for n in root.iter(W+'registry_state') if n.get('id')==f.text.strip());value=state.find(W+'value');value.text=None;value.set('var_ref','oval:org.scapng.registry:var:999999');variables=root.find(O+'variables')
                if variables is None:variables=ET.SubElement(root,O+'variables')
                local=ET.SubElement(variables,O+'local_variable',id='oval:org.scapng.registry:var:999999',datatype='string',version='1');ET.SubElement(local,O+'object_component',object_ref=obj.get('id'),item_field='value')
            before=ET.tostring(root)
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'cyclic' if change=='cycle' else '.'):ExpandedSource(root).object(obj.get('id'))
            self.assertEqual(ET.tostring(root),before)

    def test_native_type_and_multiset_mutants_fail_both_independent_readers(self):
        for index in [0,1]:
            root=self.original(index)
            if index:
                e=self.entity(root);v=next(n for n in root.iter(O+'constant_variable') if n.get('id')==e.get('var_ref'));v.append(deepcopy(v[0]));e.set('var_check','only one')
            a=self.proved(root,CASES[index]['tests'][0]);mutant=deepcopy(a);p=next(n['type'] for n in walk(mutant['tests']) if isinstance(n.get('type'),dict))
            p['equals']='string' if index==0 else ['dword']
            self.assertFalse(list(self.schema.iter_errors({'assessment':mutant})))
            key=mutant['evaluate']['test'];self.assertNotEqual(ExpandedSource(root).test(CASES[index]['tests'][0]),ExpandedNative(mutant).test(key))
            with self.assertRaises((ValueError,AssertionError)):verify_program(mutant,compile_assessment_program(a))

if __name__=='__main__':unittest.main()
