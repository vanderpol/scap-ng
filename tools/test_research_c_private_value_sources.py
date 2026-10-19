#!/usr/bin/env python3
"""Refs #245: inline Objects are useful for *view*, not silent rewrites."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_c_private_value_sources import (
    inspect_private_value_sources, verify_private_value_source_view
)

ROOT = Path(__file__).resolve().parents[1]
APACHE = (ROOT/'research/requirements-first-language/contract-candidate/corpus/'
          'source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml')


def fixture():
    return {'id':'source-private-test','mode':'automated',
            'shared_objects': {'named-file-object':{'capability':'unix.file',
              'select':{'full_path':{'equals':'/etc/example'}}}},
            'variables': {
             'private-path-variable':{'kind':'local','datatype':'string',
               'title':'Find the source path from command output',
               'expression':{'regex_capture':{'pattern':'(/etc/\\S+)',
                 'value':{'values':{'field':'stdout_line','object':{
                   'capability':'independent.shellcommand',
                   'collect':{'command':'read --paths', 'shell':'bash'}}}}}}},
             'shared-path-variable':{'kind':'local','datatype':'string',
               'title':'Reuse named file source',
               'expression':{'values':{'field':'full_path',
                                       'object':'named-file-object'}}}},
            'tests':{'check-test':{'test_title':'Example check',
              'capability':'unix.file','object':'named-file-object',
              'states':[{'path':{'equals':{'variable':'private-path-variable'}}}]}},
            'evaluate':{'test':'check-test'}}


class PrivateValueScopeTests(unittest.TestCase):
    def test_private_acquisition_one_card_preserves_original_graph(self):
        src=fixture(); before=deepcopy(src)
        r=inspect_private_value_sources(src)
        self.assertEqual(src,before)
        self.assertEqual(r['summary']['named_variables'],2)
        self.assertEqual(r['summary']['private_value_cards'],1)
        self.assertEqual(r['summary']['named_shared_object_value_sources'],1)
        self.assertEqual(r['summary']['inline_object_acquisitions'],1)
        cards={x['source_variable_id']:x for x in r['variables']}
        self.assertTrue(cards['private-path-variable']['display_as_one_derived_value'])
        self.assertFalse(cards['shared-path-variable']['display_as_one_derived_value'])
        self.assertEqual(cards['private-path-variable']['direct_source_consumers'],1)
        self.assertEqual(verify_private_value_source_view(r,src),before)
        self.assertFalse(r['automatic_migration_authorized'])

    def test_dynamic_command_remains_explicit_even_in_private_card(self):
        d=fixture()
        d['variables']['private-path-variable']['expression']['regex_capture']['value']['values']['object']['collect']['command']={
            'variable':'shared-path-variable'}
        r=inspect_private_value_sources(d)
        card=next(x for x in r['variables'] if x['source_variable_id']=='private-path-variable')
        self.assertTrue(card['display_as_one_derived_value'])
        self.assertIn('dynamic_collection_arguments',card['value_sources'][0]['hazards'])
        self.assertTrue(card['explicit_dependency_required'])
        self.assertFalse(card['compiler_may_inline_or_deduplicate'])

    def test_complex_set_or_filters_cannot_be_presented_as_one_simple_source(self):
        d=fixture()
        obj=d['variables']['private-path-variable']['expression']['regex_capture']['value']['values']['object']
        obj.pop('collect')
        obj['set']={'operator':'union','operands':[{'object':'named-file-object',
           'filters':[{'exclude':{'type':{'equals':'directory'}}}]}]}
        r=inspect_private_value_sources(d)
        card=next(x for x in r['variables'] if x['source_variable_id']=='private-path-variable')
        self.assertFalse(card['display_as_one_derived_value'])
        self.assertEqual(set(card['value_sources'][0]['hazards']),
                         {'set_population','filter_population'})

    def test_multiple_private_sources_keep_visible(self):
        d=fixture()
        old=deepcopy(d['variables']['private-path-variable']['expression'])
        d['variables']['private-path-variable']['expression']={'concat':[old,deepcopy(old)]}
        r=inspect_private_value_sources(d)
        card=next(x for x in r['variables'] if x['source_variable_id']=='private-path-variable')
        self.assertEqual(len(card['value_sources']),2)
        self.assertFalse(card['display_as_one_derived_value'])

    def test_missing_projection_field_cannot_be_silent(self):
        d=fixture()
        d['variables']['private-path-variable']['expression']['regex_capture']['value']['values'].pop('field')
        card=next(x for x in inspect_private_value_sources(d)['variables'] if x['source_variable_id']=='private-path-variable')
        self.assertFalse(card['display_as_one_derived_value'])
        self.assertEqual(len(card['unsupported_object_contexts']),1)

    def test_source_change_or_tamper_refused(self):
        d=fixture(); r=inspect_private_value_sources(d)
        x=deepcopy(d); x['variables']['private-path-variable']['expression']['regex_capture']['pattern']='.*'
        with self.assertRaisesRegex(ValueError,'changed'):
            verify_private_value_source_view(r,x)
        x=deepcopy(r); x['variables'][0]['display_as_one_derived_value']=False
        with self.assertRaisesRegex(ValueError,'changed'):
            verify_private_value_source_view(x,d)

    @unittest.skipUnless(APACHE.exists(), "real Apache fixture only on checked-out repository")
    def test_real_apache_nineteen_variables_keep_private_source_and_dynamic_edges(self):
        import yaml
        d=yaml.safe_load(APACHE.read_text())['assessment']
        self.assertEqual(len(d['variables']),19)
        r=inspect_private_value_sources(d)
        self.assertEqual(r['summary']['named_variables'],19)
        self.assertGreater(r['summary']['inline_object_acquisitions'],0)
        self.assertGreater(r['summary']['private_value_cards'],0)
        self.assertTrue(any('dynamic_collection_arguments' in s['hazards']
           for x in r['variables'] for s in x['value_sources']))
        self.assertEqual(verify_private_value_source_view(r,d),d)
        self.assertFalse(r['source_parity_proven'])

if __name__=='__main__': unittest.main()
