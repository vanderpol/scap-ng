#!/usr/bin/env python3
"""Refs #245: bounded C Guided form projection / fail-closed patch tests."""
from copy import deepcopy
from pathlib import Path
import sys
import types
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_guided_projection import project_c_guided, propose_guided_edit

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'research/assessment-simplification/compact-authoring-04'
SRC=ROOT/'research/requirements-first-language/contract-candidate/corpus/source-specimens'


def two_windows():
    return {'id': 'c-research-windows-security-combination',
            'checks': {
                'wdigest': {
                    'from': {'windows.registry': {
                        'hive': 'local_machine',
                        'key': 'SYSTEM\\CurrentControlSet\\Control\\SecurityProviders\\Wdigest',
                        'name': 'UseLogonCredential'}},
                    'must': {'every_item': {'type': 'dword', 'value': 0}}},
                'non_ntfs_local_volumes': {
                    'from': {'windows.wmi.query': {
                        'namespace': 'root\\cimv2',
                        'query': 'SELECT deviceid FROM win32_logicaldisk WHERE drivetype=3 AND filesystem!="NTFS"'}},
                    'must': 'absent'}},
            'require': {'every': [{'check': 'wdigest'},
                                  {'check': 'non_ntfs_local_volumes'}]}}


class CResearchGuidedForms(unittest.TestCase):
    def setUp(self):
        self.doc = two_windows()

    def test_combination_distinguishes_two_sources_and_logic_scope(self):
        view = project_c_guided(self.doc)
        self.assertEqual(view['projection'], 'c-guided-research/0.1')
        self.assertEqual(len(view['checks']), 2)
        self.assertEqual(view['combine_checks']['kind'], 'every')
        self.assertEqual([v['check_id'] for v in view['combine_checks']['children']],
                         ['wdigest', 'non_ntfs_local_volumes'])
        wdigest, wmi = view['checks']
        self.assertEqual(wdigest['source']['capability'], 'windows.registry')
        self.assertEqual(wdigest['population_requirement'], 'every_item')
        self.assertEqual({v['field'] for v in wdigest['field_conditions']},
                         {'type', 'value'})
        self.assertTrue(all(v['same_item'] for v in wdigest['field_conditions']))
        self.assertEqual(wmi['population_requirement'], 'absent')
        self.assertEqual(wmi['field_conditions'], [])
        self.assertFalse(view['scanner_verified'])
        self.assertFalse(view['source_format_preserved'])
        self.assertFalse(view['authored_C_grammar_approved'])

    def test_bare_must_is_visible_but_not_guided_editable(self):
        doc = {'from': {'linux.partition': {'mount_point': '/home'}},
               'must': {'mount_options': {'contains': 'nosuid'}}}
        view = project_c_guided(doc)
        self.assertEqual(view['checks'][0]['population_requirement'],
                         'implicit_any_item')
        self.assertFalse(view['checks'][0]['editable_with_pinned_compiler'])
        self.assertIn('hides any_item', view['checks'][0]['meaning_warning'])

    def test_advanced_source_existence_stays_inspectable(self):
        doc = {'from': {'windows.registry': {'name': 'setting'}},
               'must': {'items_exist': 'one_or_more', 'items_match': 'none',
                        'fields': {'value': 0}}}
        view = project_c_guided(doc)
        self.assertEqual(view['checks'][0]['population_requirement'],
                         'advanced_source_requirement')
        self.assertFalse(view['checks'][0]['editable_with_pinned_compiler'])

    def test_nested_logic_preserves_assessment_scope(self):
        doc = two_windows()
        doc['require'] = {'one_of': [{'check': 'wdigest'},
                                   {'not': {'check': 'non_ntfs_local_volumes'}}]}
        result = project_c_guided(doc)
        self.assertEqual(result['combine_checks']['kind'], 'one_of')
        self.assertEqual(result['combine_checks']['children'][1]['kind'], 'not')

    def test_broken_reference_cannot_form_view(self):
        doc = two_windows()
        doc['require']['every'][1]['check'] = 'phantom'
        with self.assertRaisesRegex(ValueError, 'unresolved C check'):
            project_c_guided(doc)

    def test_no_unverified_source_defaults(self):
        for malformed in ({}, {'must': 'present'},
                          {'from': {}, 'must': 'absent'},
                          {'from': {'x': {}, 'y': {}}, 'must': 'present'}):
            with self.subTest(doc=malformed), self.assertRaises(ValueError):
                project_c_guided(malformed)

    def test_atomic_rename_preserves_original_and_updates_refs(self):
        doc = two_windows()
        old = deepcopy(doc)
        prev = sys.modules.get('research_c_composed_assessment')
        fake = types.ModuleType('research_c_composed_assessment')
        def check(document, *, source_documents):
            checks=set(document['checks'])
            refs={x['check'] for x in document['require']['every']}
            if checks != refs: raise ValueError('missing check')
            return {'stage': 'TEST_COMPILER_STUB'}
        fake.compile_c_composed_assessment = check
        sys.modules['research_c_composed_assessment'] = fake
        try:
            result=propose_guided_edit(doc, {'action': 'rename_check',
                                           'check': 'wdigest',
                                           'new_name': 'disable_wdigest'})
        finally:
            if prev is None: del sys.modules['research_c_composed_assessment']
            else: sys.modules['research_c_composed_assessment'] = prev
        self.assertEqual(doc,old)
        revised=result['proposed_C_ast']
        self.assertIn('disable_wdigest',revised['checks'])
        self.assertNotIn('wdigest',revised['checks'])
        self.assertEqual(revised['require']['every'][0], {'check':'disable_wdigest'})
        self.assertTrue(result['requires_source_diff_and_human_approval'])
        self.assertFalse(result['source_text_modified'])
        self.assertFalse(result['scanner_verified'])

    def test_collision_rejected_before_compiler_and_original_untouched(self):
        original=deepcopy(self.doc)
        with self.assertRaisesRegex(ValueError, 'duplicate or invalid'):
            propose_guided_edit(self.doc, {'action': 'rename_check',
                                          'check': 'wdigest',
                                          'new_name': 'non_ntfs_local_volumes'})
        self.assertEqual(self.doc,original)

    def test_semantic_changes_need_explicit_acknowledgement(self):
        original=deepcopy(self.doc)
        for op in ({'action':'set_root_logic','mode':'one_of',
                    'acknowledge_semantic_change':False},
                   {'action':'set_item_scope','check':'wdigest','mode':'any_item',
                    'acknowledge_semantic_change':False},
                   {'action':'set_source_argument','check':'wdigest',
                    'argument':'name','value':'AnotherCredential',
                    'acknowledge_semantic_change':False}):
            with self.subTest(op=op), self.assertRaisesRegex(ValueError,'acknowledgement'):
                propose_guided_edit(self.doc,op)
        self.assertEqual(self.doc,original)

    def test_typed_expected_value_rejects_string_zero_without_compiler(self):
        with self.assertRaisesRegex(ValueError,'type change'):
            propose_guided_edit(self.doc, {'action':'set_expected','check':'wdigest',
                                          'field':'value','value':'0'})

    def test_wmi_presence_not_mistaken_for_editable_field(self):
        with self.assertRaisesRegex(ValueError,'presence-only'):
            propose_guided_edit(self.doc, {'action':'set_expected',
                                          'check':'non_ntfs_local_volumes',
                                          'field':'value','value':0})

    def test_cannot_invent_collection_arguments(self):
        with self.assertRaisesRegex(ValueError, 'cannot invent'):
            propose_guided_edit(self.doc, {'action':'set_source_argument',
                                          'check':'wdigest','argument':'view',
                                          'value':'64bit',
                                          'acknowledge_semantic_change':True})


class CActualCompilerGuidedIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=yaml.safe_load((BASE/'c-two-windows-checks.research.yaml').read_text())
        cls.wmi=yaml.safe_load((SRC/'windows-wmi-query-0-a5018a53e0f6.source.yaml').read_text())
        cls.sources={'non_ntfs_local_volumes': cls.wmi}

    def test_real_source_projection_is_nonmutating(self):
        original=deepcopy(self.doc)
        view=project_c_guided(self.doc)
        self.assertEqual(self.doc,original)
        self.assertEqual([x['population_requirement'] for x in view['checks']],
                         ['every_item','absent'])
        self.assertEqual(view['combine_checks']['kind'],'every')

    def test_rename_updates_all_refs_then_compiles(self):
        doc=deepcopy(self.doc)
        result=propose_guided_edit(doc, {'action':'rename_check',
                            'check':'wdigest','new_name':'disable_wdigest'},
                            source_documents=self.sources)
        self.assertEqual(doc,self.doc)
        result_doc=result['proposed_C_ast']
        self.assertIn('disable_wdigest',result_doc['checks'])
        self.assertEqual(result_doc['require']['every'][0]['check'],'disable_wdigest')
        self.assertEqual(result['compiler_stage'],'C_RESEARCH_COMPOSED_SUPPLIED_RESULTS_NOT_SCANNER')

    def test_item_scope_change_needs_ack_then_compiles(self):
        doc=deepcopy(self.doc)
        result=propose_guided_edit(doc, {'action':'set_item_scope',
                           'check':'wdigest','mode':'any_item',
                           'acknowledge_semantic_change':True},
                           source_documents=self.sources)
        self.assertEqual(result['proposed_C_ast']['checks']['wdigest']['must'],
                         {'any_item':{'type':'dword','value':0}})
        self.assertEqual(self.doc,doc)

    def test_logic_change_needs_ack_then_compiles(self):
        result=propose_guided_edit(self.doc, {'action':'set_root_logic',
                        'mode':'one_of','acknowledge_semantic_change':True},
                        source_documents=self.sources)
        self.assertEqual(result['guided_view']['combine_checks']['kind'],'one_of')

    def test_bad_registry_enum_rejected_by_real_mapping(self):
        with self.assertRaises(ValueError):
            propose_guided_edit(self.doc, {'action':'set_expected',
                           'check':'wdigest','field':'type','value':'unsupported_type'},
                           source_documents=self.sources)

    def test_wmi_query_change_rejected_by_source_compatibility(self):
        old=deepcopy(self.doc)
        with self.assertRaises(ValueError):
            propose_guided_edit(self.doc, {'action':'set_source_argument',
                        'check':'non_ntfs_local_volumes','argument':'query',
                        'value':'SELECT deviceid FROM win32_logicaldisk',
                        'acknowledge_semantic_change':True},
                        source_documents=self.sources)
        self.assertEqual(self.doc,old)

    def test_dns_source_fields_stay_bound_to_A_mapping(self):
        doc=yaml.safe_load((BASE/'c-short-windows-dns-rrl.research.yaml').read_text())
        view=project_c_guided(doc)
        self.assertEqual(view['checks'][0]['source']['capability'],'independent.shellcommand')
        result=propose_guided_edit(doc, {'action':'set_expected',
                            'check':'single_check','field':'stdout_line','value':'Disable'})
        self.assertEqual(result['proposed_C_ast']['must']['every_item']['stdout_line'],
                         'Disable')
        self.assertFalse(result['scanner_verified'])


if __name__ == '__main__':
    unittest.main()
