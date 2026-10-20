#!/usr/bin/env python3
"""Refs #245: original OVAL typed literal Object-selector binding proof."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_local_literal_inputs import (
    present_literal_collection_inputs,compile_literal_collection_inputs,
    prove_literal_collection_inputs,census)

ROOT=Path(__file__).resolve().parents[1]

def source(*,name='x',datatype='string',value='c:\\path',consumer='filepath'):
    vid='source-typed-variable'; oid='original-object'
    return {'id':'source-fixture','mode':'automated',
        'objects':{oid:{'capability':'windows.registry','object_title':'Original',
          'select':{consumer:{'operation':'equals','datatype':datatype,
            'value':{'variable':vid}}}}},
        'variables':{vid:{'kind':'local','datatype':datatype,'title':name,
           'expression':{'literal':{'datatype':datatype,'value':value}}}}}

class LocalLiteralCollectionBindings(unittest.TestCase):
    def test_selectors_and_source_variable_identity_are_recreated(self):
        a=source(); snapshot=deepcopy(a)
        author,sidecar=present_literal_collection_inputs(a)
        self.assertEqual(a,snapshot)
        self.assertEqual(set(author['collection_inputs']),{'input_filepath'})
        self.assertEqual(set(sidecar['source_graph_without_literal_bindings'][
            'variables']),set())
        self.assertEqual(compile_literal_collection_inputs(author,sidecar),a)
        self.assertTrue(prove_literal_collection_inputs(a,author,sidecar)[
            'original_typed_graph_recreated'])

    def test_bool_int_float_version_binary_are_not_coerced(self):
        cases=[('boolean',True),('integer',4712394792173),
               ('float',-12.432559),('version','9!23%424-65+35,890A314P12'),
               ('binary','10101010')]
        for datatype,value in cases:
            with self.subTest(datatype=datatype):
                a=source(datatype=datatype,value=value)
                author,sidecar=present_literal_collection_inputs(a)
                out=compile_literal_collection_inputs(author,sidecar)
                self.assertEqual(out,a)
                literal=out['variables']['source-typed-variable'][
                    'expression']['literal']
                self.assertIs(type(literal['value']),type(value))

    def test_mismatched_literal_and_variable_datatype_fail_closed(self):
        a=source(datatype='integer',value='9')
        with self.assertRaisesRegex(ValueError,'no source-proven'):
            present_literal_collection_inputs(a)
        a=source()
        author,sidecar=present_literal_collection_inputs(a)
        author['collection_inputs']['input_filepath']['datatype']='version'
        with self.assertRaisesRegex(ValueError,'source datatype'):
            compile_literal_collection_inputs(author,sidecar)

    def test_shared_state_and_derived_references_remain_typed_graph(self):
        for mutation in ['shared_object','state_ref','derived_ref']:
            a=source(); v={'variable':'source-typed-variable'}
            if mutation=='shared_object':
                a['objects']['other']=deepcopy(a['objects']['original-object'])
            if mutation=='state_ref':
                a['states']={'s':{'state':{'value':v}}}
            if mutation=='derived_ref':
                a['variables']['derived']={'kind':'local','datatype':'string',
                                           'expression':v}
            with self.subTest(mutation=mutation):
                with self.assertRaisesRegex(ValueError,'no source-proven'):
                    present_literal_collection_inputs(a)

    def test_selector_missing_duplicate_and_bad_type_are_blocked(self):
        a=source(); author,sidecar=present_literal_collection_inputs(a)
        for mutation in ['wrong_selector','missing','extra','badtype','title']:
            changed=deepcopy(author)
            item=changed['collection_inputs']['input_filepath']
            if mutation=='wrong_selector': item['selector']='other'
            if mutation=='missing': changed['collection_inputs'].clear()
            if mutation=='extra':
                changed['collection_inputs']['input_extra']=deepcopy(item)
            if mutation=='badtype': item['value']=True
            if mutation=='title': item['description']='untrusted'
            with self.subTest(mutation=mutation):
                with self.assertRaises(ValueError):
                    compile_literal_collection_inputs(changed,sidecar)
        modified=deepcopy(sidecar)
        modified['bindings']['input_filepath']['source_path'][1]='wrong_object'
        with self.assertRaises(ValueError):
            compile_literal_collection_inputs(author,modified)

    def test_changed_value_is_not_source_equivalent(self):
        a=source(); author,sidecar=present_literal_collection_inputs(a)
        changed=deepcopy(author)
        changed['collection_inputs']['input_filepath']['value']='different'
        out=compile_literal_collection_inputs(changed,sidecar)
        self.assertEqual(out['variables']['source-typed-variable'][
            'expression']['literal']['value'],'different')
        with self.assertRaisesRegex(ValueError,'does not reproduce original'):
            prove_literal_collection_inputs(a,changed,sidecar)

    def test_full_pinned_original_oval_census_when_corpus_supplied(self):
        # The full pinned corpus is supplied only by the dedicated CI job;
        # focused tests remain independent of an optional local checkout.
        import os
        base=os.environ.get('SCAP_NG_C_REVIEW_DIR')
        manifest=os.environ.get('SCAP_NG_C_NATIVE_MANIFEST')
        if not base or not manifest:
            self.skipTest('run original source corpus through dedicated C workflow')
        report=census(base,json.loads(Path(manifest).read_text(encoding='utf-8')))
        self.assertEqual((report['variable_blocked_definitions'],
                          report['original_definitions_with_inline_local_literals'],
                          report['inlined_local_literal_variables']),(68,8,23))
        self.assertFalse(report['native_C_conversion_proven'])
        self.assertFalse(report['scanner_execution_proven'])

if __name__=='__main__':unittest.main()
