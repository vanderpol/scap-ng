#!/usr/bin/env python3
"""Regression guards for fixture and compilation-view CI wiring; Refs #248 #239 #232."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
from test_v04_public_cli_smoke import schema_valid_docs, authoring_archives
from v04_canonical_source_ir import compile_pair
from validate_v04_fields_condition_preview import compile_candidate_view
from v04_restore_missing_applicability import PINS

ROOT = Path(__file__).resolve().parents[1]
PIN = 'e3538595c5083b9c34d937a81d319234df9bbfaa'


class CIIntegrationTests(unittest.TestCase):
    def test_discovered_source_tests_have_original_pinned_sparse_fixtures(self):
        workflow = yaml.safe_load((ROOT/'.github/workflows/rebaseline-smoke.yml').read_text())
        steps = workflow['jobs']['smoke']['steps']
        regression = next(s for s in steps if s.get('name') == 'Run maintained tool regressions')
        checkout = next(s for s in steps if s.get('with',{}).get('repository') == 'OVAL-Community/SCAP-Self-Assertion')['with']
        self.assertEqual(checkout['ref'], PIN)
        sparse = set(checkout['sparse-checkout'].splitlines())
        expected = {
            'SCAP_NG_APPARMOR_SOURCE_XML':'linux/linux-def_apparmorstatus_test.xml',
            'SCAP_NG_ENVIRONMENT58_SOURCE_XML':'linux/ind-def_environmentvariable58_test_linux.xml',
            'SCAP_NG_UNAME_SOURCE_XML':'unix/unix-def_uname_test.xml',
            'OVAL_GATEKEEPER_SOURCE':'macos/macos-def_gatekeeper_test.xml',
        }
        for variable,suffix in expected.items():
            relative = 'SCAP_1.4/OVAL_Test_Content/'+suffix
            self.assertEqual(regression['env'][variable], checkout['path']+'/'+relative)
            self.assertIn(relative,sparse)
        self.assertIn('run_current_tool_regressions.py',regression['run'])

    def test_both_preview_validation_calls_supply_the_same_pinned_source(self):
        workflow = yaml.safe_load((ROOT/'.github/workflows/v04-fields-condition-preview.yml').read_text())
        steps = workflow['jobs']['source-reversible-fields-scope']['steps']
        source = next(s['run'] for s in steps if s.get('name') == 'Obtain immutable original shared Applicability dependencies')
        self.assertIn(PINS['original_03'],source)
        self.assertIn('sha256sum -c -',source)
        calls=[s['run'] for s in steps if 'python tools/validate_v04_fields_condition_preview.py' in s.get('run','')]
        self.assertEqual(len(calls),2)
        for call in calls:
            self.assertIn('--original-03 work/dependencies/scap-ng-0.3-six-stig-authoring.zip',call)

    def proof(self):
        return {'source_reconstruction':'PASS','yaml_json_byte_parity':'PASS',
                'native_source_schema':'PASS','legacy_source_inverse':'PASS',
                'documents':4012,'tests':1390,'legacy_dependency_restoration':{
                    'source_documents':4001,'restored_dependency_documents':11,
                    'source_sha256':PINS['original_03']}}

    def test_preview_uses_existing_strict_source_reversible_typed_view(self):
        proof=self.proof()
        with patch('validate_v04_fields_condition_preview.compile_pair',return_value=(b'IR',proof)) as compiler:
            self.assertEqual(compile_candidate_view('preview.json.zip','preview.yaml.zip','source03.zip'),proof)
        compiler.assert_called_once_with('preview.json.zip','preview.yaml.zip',
            validate_schema=True,legacy_review=True,legacy_original_03='source03.zip')

    def test_raw_or_partial_compilation_view_is_never_reported_as_success(self):
        mutations=[lambda p:p.update(documents=4001,tests=1375),
                   lambda p:p.update(documents=4013),lambda p:p.update(tests=1389),
                   lambda p:p['legacy_dependency_restoration'].update(restored_dependency_documents=10),
                   lambda p:p['legacy_dependency_restoration'].update(source_documents=4000)]
        for field in ('source_reconstruction','yaml_json_byte_parity','native_source_schema','legacy_source_inverse'):
            mutations.append(lambda p,field=field:p.update({field:'NOT_TESTED'}))
        for mutate in mutations:
            proof=self.proof();mutate(proof)
            with self.subTest(proof=proof),patch('validate_v04_fields_condition_preview.compile_pair',return_value=(b'',proof)):
                with self.assertRaisesRegex(ValueError,'failed closed canonical typed source IR'):
                    compile_candidate_view('j','y','source')

    def test_compiler_failure_is_not_swallowed(self):
        with patch('validate_v04_fields_condition_preview.compile_pair',side_effect=ValueError('unresolved Applicability Assessment')):
            with self.assertRaisesRegex(ValueError,'unresolved Applicability Assessment'):
                compile_candidate_view('j','y','source')

    def test_changed_original_source_is_rejected_and_archives_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            archives=authoring_archives(schema_valid_docs(),root)
            before=[p.read_bytes() for p in archives]
            original=root/'changed-original.zip';original.write_bytes(b'untrusted scratch XML is not original source')
            with self.assertRaisesRegex(ValueError,'digest mismatch'):
                compile_candidate_view(*archives,original)
            self.assertEqual([p.read_bytes() for p in archives],before)

    def test_strict_compiler_still_rejects_unresolved_oracle_applicability(self):
        docs=deepcopy(schema_valid_docs())
        docs['authoring/oracle_linux_9/applicability.json']={'applicability':{
            'id':'oracle-linux-9.applicability','conditions':{
                'autofs-installed':{'assessment':'ng.shared.the-autofs-package-is-installed'}}}}
        with tempfile.TemporaryDirectory() as temp:
            archives=authoring_archives(docs,Path(temp))
            with self.assertRaisesRegex(ValueError,'unresolved.*Applicability Assessment'):
                compile_pair(*archives)


if __name__ == '__main__':
    unittest.main()
