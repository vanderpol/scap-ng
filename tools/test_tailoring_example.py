"""Worked-example policy expectations and fail-closed Tailoring boundaries."""
from copy import deepcopy
from pathlib import Path
import shutil
import tempfile
import unittest
import yaml
from resolve_tailoring_example import resolve
ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'research/iterations/003/examples/tailoring-all-options'
RHEL9_FIXTURE=ROOT/'tools/fixtures/rhel9-tailoring'

class TailoringExample(unittest.TestCase):
    def run_demo(self, directory=DEMO, input=True, name='all-options.tailoring.yaml'):
        return resolve(directory/'benchmark.yaml',directory/'tailoring'/name,
                       directory/'organizational-input.yaml' if input else None)

    def modified(self, mutation, file='tailoring/all-options.tailoring.yaml'):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup)
        root=Path(temporary.name)/'sample';shutil.copytree(DEMO,root)
        path=root/file;doc=yaml.safe_load(path.read_text());mutation(doc)
        path.write_text(yaml.safe_dump(doc,sort_keys=False));return root

    def test_effective_state_and_layer_provenance(self):
        r=self.run_demo()
        self.assertEqual(r['effective_selection'],{'demo-password-length':True,'demo-password-history':True,
                         'demo-log-retention':True,'demo-session-timeout':False,'demo-time-sources':False})
        self.assertFalse(r['tailoring_layers'][0]['selection']['demo-password-length'])
        self.assertEqual([layer['parameter_values']['password_minimum_length'] for layer in r['tailoring_layers']],[14,14])
        self.assertEqual(r['parameter_source']['password_minimum_length'],'profile:site-baseline')
        self.assertEqual(r['assessment_selections']['demo-log-retention']['selector'],'document-review')
        self.assertNotIn('approved_time_sources',r['parameters'])
        self.assertEqual(r['organizational_input']['approved_time_sources']['source'],'example.site-input')

    def test_no_profile_starts_with_every_rule_enabled(self):
        r=self.run_demo(input=False,name='no-profile.tailoring.yaml')
        self.assertTrue(all(r['publisher_selection'].values()))
        self.assertFalse(r['effective_selection']['demo-session-timeout'])
        self.assertEqual(sum(r['effective_selection'].values()),4)

    def test_purpose_and_distinct_creator_authorizer_are_preserved(self):
        result=self.run_demo();layer=result['tailoring_layers'][-1]
        self.assertTrue(layer['purpose'])
        self.assertEqual(layer['provenance']['created_by']['name'],'Example Policy Author')
        self.assertEqual(layer['provenance']['authorized_by']['name'],'Example Approver')
        self.assertEqual(layer['provenance']['authorization_reference'],'EXAMPLE-CHANGE-100')

    def test_draft_authorization_metadata_does_not_change_effective_policy(self):
        original=self.run_demo()
        def draft(doc):
            doc['tailoring']['purpose']='Draft review of the same policy changes.'
            p=doc['tailoring']['provenance']
            p.update(authorized_by=None,authorized_at=None,authorization_reference=None,authorization_status='draft')
        root=self.modified(draft);result=self.run_demo(root)
        for key in ('effective_selection','parameters','assessment_selections'):
            self.assertEqual(result[key],original[key])
        self.assertIsNone(result['tailoring_layers'][-1]['provenance']['authorized_by'])
        self.assertEqual(result['tailoring_layers'][-1]['provenance']['authorization_status'],'draft')

    def test_wrong_publication_is_rejected(self):
        root=self.modified(lambda d:d['tailoring']['benchmark'].update(version='0.2'))
        with self.assertRaisesRegex(ValueError,'binding mismatch'):self.run_demo(root)

    def test_contradictory_group_and_rule_operations_are_rejected(self):
        root=self.modified(lambda d:d['tailoring']['disabled_rules'].append('demo-password-history'))
        with self.assertRaisesRegex(ValueError,'Conflicting Group/Rule'):self.run_demo(root)

    def test_unknown_selector_never_falls_back(self):
        root=self.modified(lambda d:d['tailoring']['check_selectors'].update({'demo-log-retention':'unknown'}))
        with self.assertRaisesRegex(ValueError,'Unknown Rule/Assessment selector'):self.run_demo(root)

    def test_publisher_profile_parameter_type_and_constraints_are_enforced(self):
        for value in (True,7,129,'18'):
            with self.subTest(value=value):
                root=self.modified(lambda d:d['benchmark']['profiles'][0]['parameters'].update(password_minimum_length=value), file='benchmark.yaml')
                with self.assertRaises(ValueError):self.run_demo(root)

    def test_tailoring_parameter_overrides_are_rejected_in_every_layer(self):
        for file in ('tailoring/all-options.tailoring.yaml', 'tailoring/organization-baseline.tailoring.yaml'):
            for values in ({}, {'password_minimum_length':18}):
                with self.subTest(file=file, values=values):
                    root=self.modified(lambda d:d['tailoring'].update(parameters=values), file=file)
                    with self.assertRaisesRegex(ValueError,'Tailoring cannot override publisher Parameters'):
                        self.run_demo(root)

    def test_organizational_input_is_not_a_tailoring_override(self):
        root=self.modified(lambda d:d['tailoring'].update(parameters={'approved_time_sources':['ntp.example.test']}))
        with self.assertRaisesRegex(ValueError,'Tailoring cannot override publisher Parameters'):self.run_demo(root)

    def test_organizational_input_cannot_override_publisher_parameter(self):
        root=self.modified(lambda d:d['organizational_input']['values'].update(password_minimum_length=18), file='organizational-input.yaml')
        with self.assertRaisesRegex(ValueError,'Input cannot override publisher Parameter'):self.run_demo(root)

    def test_execution_mutations_are_rejected(self):
        root=self.modified(lambda d:d['tailoring'].update(commands=['unexpected']))
        with self.assertRaisesRegex(ValueError,'Unsupported Tailoring mutation'):self.run_demo(root)

    def test_parent_identity_and_cycles_are_rejected(self):
        root=self.modified(lambda d:d['tailoring']['extends'].update(version=99))
        with self.assertRaisesRegex(ValueError,'Parent identity/version'):self.run_demo(root)
        def cycle(d):
            d['tailoring']['extends']={'id':'example.site-tailoring','version':2,'source':'all-options.tailoring.yaml'}
        root=self.modified(cycle,file='tailoring/organization-baseline.tailoring.yaml')
        with self.assertRaisesRegex(ValueError,'inheritance cycle'):self.run_demo(root)

    def test_rule_filenames_do_not_define_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'sample';shutil.copytree(DEMO,root)
            p=root/'rules/demo-log-retention.rule.yaml';p.rename(p.with_name('different-name.rule.yaml'))
            self.assertTrue(self.run_demo(root)['effective_selection']['demo-log-retention'])

    def test_rhel9_example_is_bound_to_real_rules_and_methods(self):
        r=resolve(RHEL9_FIXTURE/'benchmark.yaml',
                  DEMO/'tailoring/rhel9-example.tailoring.yaml')
        self.assertEqual(len(r['effective_selection']),3)
        self.assertFalse(r['publisher_selection']['SV-257778']);self.assertTrue(r['effective_selection']['SV-257778'])
        self.assertTrue(r['publisher_selection']['SV-257777']);self.assertFalse(r['effective_selection']['SV-257777'])
        selection=r['assessment_selections']['SV-257784']
        self.assertEqual(selection['selector'],'manual');self.assertTrue(selection['will_be_selected'])
        self.assertEqual(selection['assessment_id'],'SV-257784.manual')

if __name__=='__main__':unittest.main()
