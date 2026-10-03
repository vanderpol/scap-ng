#!/usr/bin/env python3
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from lxml import etree as ET
from audit_oval_new_tests import scan,contract,tree,materialize,snapshot,ROOT

X='http://www.w3.org/2001/XMLSchema'
K='urn:oval:v6:definitions:kubernetes'

class NewTestAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.before=Path(self.tmp.name)/'before';self.after=Path(self.tmp.name)/'after'
        self.before.mkdir();self.after.mkdir()
    def schema(self,folder,kind='definitions',family='sample',body=''):
        path=folder/f'{family}-{kind}-schema.xsd'
        path.write_text(f'<x:schema xmlns:x="{X}" xmlns:f="urn:{family}:{kind}" targetNamespace="urn:{family}:{kind}">{body}</x:schema>',encoding='utf-8')
        return path
    def fixture(self,stem='new',existing=False):
        body=f'<x:element name="{stem}_test"/><x:element name="{stem}_object"/><x:element name="{stem}_state"/>'
        self.schema(self.after,body=body)
        self.schema(self.after,'system-characteristics',body=f'<x:element name="{stem}_item"/>')
        if existing:self.schema(self.before,body=f'<x:element name="{stem}_test"><x:complexType><x:attribute name="old"/></x:complexType></x:element>')
    def test_new_family_discovery_and_unmapped_disposition(self):
        self.fixture();result=scan(self.before,self.after)
        self.assertEqual([(r['family'],r['test']) for r in result['new_tests']],[('sample','new_test')])
        self.assertIsNone(result['new_tests'][0]['existing_native_mapping'])
        self.assertEqual(result['new_tests'][0]['disposition'],'needs_native_design_and_fixtures')
    def test_existing_test_differences_excluded(self):
        self.fixture(existing=True);result=scan(self.before,self.after)
        self.assertEqual(result['new_tests'],[])
    def test_same_name_in_different_family_is_new(self):
        self.fixture();self.schema(self.before,family='other',body='<x:element name="new_test"/>')
        self.assertEqual(len(scan(self.before,self.after)['new_tests']),1)
    def test_missing_associated_item_rejected(self):
        self.fixture();(self.after/'sample-system-characteristics-schema.xsd').write_text(f'<x:schema xmlns:x="{X}"/>')
        with self.assertRaisesRegex(ValueError,'Incomplete'):scan(self.before,self.after)
    def test_cardinality_and_type_constraints_preserved(self):
        p=self.schema(self.after,body='<x:complexType name="Values"><x:sequence><x:element name="value" type="x:string" minOccurs="0" maxOccurs="unbounded" nillable="true"/></x:sequence><x:attribute name="datatype" fixed="string"/></x:complexType>')
        root=tree(p);value=contract(root[0],[root])
        self.assertEqual(value['fields'][0]['max_occurs'],'unbounded');self.assertEqual(value['fields'][0]['min_occurs'],'0');self.assertEqual(value['fields'][0]['nillable'],'true')
        self.assertEqual(value['attributes'][0]['fixed'],'string')
    def test_inherited_fields_remain_linked_to_exact_type(self):
        self.fixture();p=self.schema(self.after,body='<x:complexType name="Device"><x:sequence><x:element name="device_key" type="x:string"/></x:sequence></x:complexType><x:element name="new_test"/><x:element name="new_object"><x:complexType><x:complexContent><x:extension base="f:Device"/></x:complexContent></x:complexType></x:element><x:element name="new_state"/>')
        r=scan(self.before,self.after);ref=r['new_tests'][0]['contracts']['object']['inherited'][0]['type_ref']
        self.assertEqual(r['referenced_types'][ref]['fields'][0]['name'],'device_key')
    def test_choice_alternatives_are_not_flattened_into_required_fields(self):
        p=self.schema(self.after,body='<x:complexType name="Alternatives"><x:choice><x:element name="one"/><x:element name="two"/></x:choice></x:complexType>')
        root=tree(p);model=contract(root[0],[root])['content_model'][0]
        self.assertEqual(model['kind'],'choice');self.assertEqual([n['attributes']['name'] for n in model['children']],['one','two'])

    def test_circular_inheritance_rejected(self):
        p=self.schema(self.after,body='<x:complexType name="A"><x:complexContent><x:extension base="f:B"/></x:complexContent></x:complexType><x:complexType name="B"><x:complexContent><x:extension base="f:A"/></x:complexContent></x:complexType>')
        root=tree(p)
        with self.assertRaisesRegex(ValueError,'Circular'):contract(root[0],[root])
    def test_type_resolution_uses_namespace_not_local_name(self):
        p=self.schema(self.after,body='<x:complexType name="Value"><x:attribute name="correct"/></x:complexType><x:element name="node" type="f:Value"/>')
        other=tree(self.schema(self.before,family='other',body='<x:complexType name="Value"><x:attribute name="wrong"/></x:complexType>'))
        root=tree(p);ref=contract(root[1],[other,root])['inherited'][0]['type_ref']
        self.assertEqual(ref,'{urn:sample:definitions}Value')
    def test_committed_inventory_has_complete_contracts_and_no_existing_tests(self):
        r=json.loads((ROOT/'docs/audit/capability-coverage-2026-10-03/oval-new-tests.json').read_text())
        self.assertEqual(len(r['new_tests']),22);self.assertEqual(sum(t['family']=='esx' for t in r['new_tests']),20)
        for t in r['new_tests']:
            self.assertEqual(set(t['contracts']),{'test','object','state','item'})
            self.assertTrue(set(t['type_refs'])<=r['referenced_types'].keys())
            self.assertIn(t['test'],next(f for f in r['definition_files'] if f['file']==t['definitions_file'])['added_tests'])
    def test_pinned_kubernetes_binding_rule_contexts_do_not_match_actual_tests(self):
        r=json.loads((ROOT/'docs/audit/capability-coverage-2026-10-03/oval-new-tests.json').read_text())
        for row in [t for t in r['new_tests'] if t['family']=='kubernetes']:
            owner=ET.Element('{'+K+'}'+row['test']);ET.SubElement(owner,'{'+K+'}object',object_ref='wrong');ET.SubElement(owner,'{'+K+'}state',state_ref='wrong')
            for assertion in row['contracts']['test']['assertions']:
                self.assertTrue(assertion['context'].startswith('kube-def:test/'))
                self.assertEqual(owner.getroottree().xpath('//'+assertion['context'],namespaces={'kube-def':K}),[])
                corrected=assertion['context'].replace('kube-def:test/','kube-def:'+row['test']+'/')
                self.assertEqual(len(owner.getroottree().xpath('//'+corrected,namespaces={'kube-def':K})),1)
    def test_snapshot_preserves_git_blob_bytes_instead_of_checkout_newlines(self):
        raw=b'<schema>committed</schema>\r\n'
        with patch('audit_oval_new_tests.subprocess.check_output',side_effect=['schemas/source.xsd\nschemas/README.md\n',raw]):
            snapshot(self.before,'HEAD','schemas',self.after)
        self.assertEqual((self.after/'source.xsd').read_bytes(),raw)
        self.assertFalse((self.after/'README.md').exists())

    def test_wrong_upstream_pin_rejected(self):
        with patch('audit_oval_new_tests.subprocess.check_output',return_value='wrong\n'):
            with self.assertRaisesRegex(ValueError,'pinned'):materialize(self.after,self.before)

if __name__=='__main__':unittest.main()
