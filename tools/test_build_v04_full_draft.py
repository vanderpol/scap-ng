"""Bounded DRAFT admission/preservation tests; never runs the 65-source corpus."""
from copy import copy
from hashlib import sha1, sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from build_v04_full_draft import build_one, diagnostic_mappings, deprecated_tests
from finalize_v04_full_draft import finalize_source
from v04_direct_converter import convert_benchmark, load_mappings
from v04_direct_scap_source import SourceModel, OVAL, XCCDF

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'tests/fixtures/v04-direct-prototype'
PIN=json.loads((F/'provenance.json').read_text())

class FullDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=F/PIN['fixture']
        cls.source=SourceModel(cls.path,PIN['zip_sha256'])
        cls.automated=PIN['rules'][0]
        cls.manual=next(identifier for identifier,rule in cls.source.rules.items()
                        if not any(c.get('system')==OVAL for c in rule.findall('{'+XCCDF+'}check')))
        raw=cls.path.read_bytes()
        cls.pin={'file':cls.path.name,'bytes':len(raw),'sha256':sha256(raw).hexdigest(),
                 'git_blob_sha':sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()}

    def run_draft(self, root, *, baseline=None, known=None):
        # Controlled discovery view, not a published whole-source census. The
        # complete original ZIP/components remain preserved by build_one.
        source=copy(self.source)
        source.rules={k:self.source.rules[k] for k in [self.automated,self.manual]}
        with patch('build_v04_full_draft.SourceModel',return_value=source):
            result=build_one((self.pin,F,root,baseline or {},known or {}))
        target=Path(root)/self.path.stem
        rows=json.loads((target/'ledger.json').read_text())['rules']
        return target,result,rows

    def test_unverified_conversion_does_not_need_proof_and_preserves_every_selected_original(self):
        with tempfile.TemporaryDirectory() as root, patch('v04_expanded_source_proof.expanded_compare',side_effect=AssertionError('proof cannot gate DRAFT')):
            target,result,rows=self.run_draft(root)
            self.assertEqual(result['rules'],2)
            self.assertEqual(result['automated_attempts'],1)
            self.assertEqual(result['statuses'],{'CONVERTED_SCHEMA_VALID_UNVERIFIED':1,'MANUAL_OCIL_ONLY_PRESERVED':1})
            self.assertEqual((target/'source-preservation'/self.path.name).read_bytes(),self.path.read_bytes())
            self.assertTrue((target/'review.html').is_file())
            self.assertTrue(all((target/r['preserved_original_rule']).is_file() for r in rows))
            self.assertTrue(all(r['independent_source_proof']=='NOT_RUN' for r in rows))
            manual=next(r for r in rows if r['source_rule']==self.manual)
            self.assertNotIn('assessment_path',manual)
            self.assertEqual(result['compiled_programs'],1)

    def test_known_invalid_original_never_enters_native_authored_or_executable_output(self):
        with tempfile.TemporaryDirectory() as root:
            target,result,rows=self.run_draft(root,known={self.pin['file']+'!'+self.automated:'Pinned invalid original'})
            self.assertEqual(result['compiled_programs'],0)
            self.assertFalse((target/'UNVERIFIED-diagnostic-candidates.scapng').exists())
            self.assertFalse(list(target.glob('authoring/**/assessments/*.json')))
            self.assertEqual(next(r for r in rows if r['source_rule']==self.automated)['draft_status'],'BLOCKED_EXPLICIT')

    def test_schema_valid_but_uncompilable_authoring_is_explicit_and_not_packaged(self):
        with tempfile.TemporaryDirectory() as root, patch('build_v04_full_draft.compile_assessment_program',side_effect=ValueError('unsupported compiled construct')):
            target,result,rows=self.run_draft(root)
            self.assertEqual(result['compiled_programs'],0)
            row=next(r for r in rows if r['source_rule']==self.automated)
            self.assertEqual(row['compile_status'],'BLOCKED')
            self.assertTrue((target/row['assessment_path']).is_file())
            self.assertFalse((target/'UNVERIFIED-diagnostic-candidates.scapng').exists())

    def test_proof_baseline_mismatch_is_fatal_instead_of_relabeling(self):
        bad={self.pin['file']+'!'+self.automated:{'source_rule_sha256':'incorrect','authoring_sha256':'incorrect','program_sha256':'incorrect'}}
        with tempfile.TemporaryDirectory() as root, self.assertRaisesRegex(ValueError,'baseline drift'):
            self.run_draft(root,baseline=bad)

    def test_diagnostic_mapping_catalog_does_not_activate_production_admission(self):
        before={m['capability'] for m in load_mappings()}
        diagnostic={m['capability'] for m in diagnostic_mappings()}
        self.assertIn('iosxe.line',diagnostic)
        self.assertNotIn('iosxe.line',before)
        self.assertEqual(before,{m['capability'] for m in load_mappings()})
        self.assertTrue(before<diagnostic)

    def test_effective_deprecation_overrides_are_preserved(self):
        deprecated=deprecated_tests()
        prefix='{http://oval.mitre.org/XMLSchema/oval-definitions-5#'
        self.assertIn(prefix+'windows}accesstoken_test',deprecated)
        self.assertNotIn(prefix+'solaris}package_test',deprecated)

    def test_final_reporting_removes_stale_admission_and_recounts_source_exclusions(self):
        key=self.pin['file']+'!'+self.automated
        with tempfile.TemporaryDirectory() as root:
            target,_,_=self.run_draft(root,known={key:'Recorded original invalid'})
            rows,_,retained=finalize_source(target,self.pin,{},known={key:'Recorded original invalid'})
            ledger=json.loads((target/'ledger.json').read_text())
            row=next(r for r in rows if r['source_rule']==self.automated)
            self.assertEqual(row['proof_level'],'none')
            self.assertEqual(row['artifacts'],[])
            self.assertEqual(row['original_source_validation'],'KNOWN_INVALID_OR_DEPRECATED')
            self.assertEqual(ledger['summary']['statuses'].get('converted',0),0)
            self.assertEqual(retained,set())

    def test_final_audit_rejects_known_invalid_content_in_a_native_candidate(self):
        with tempfile.TemporaryDirectory() as root:
            target,_,_=self.run_draft(root)
            with self.assertRaisesRegex(ValueError,'known-invalid original emitted'):
                finalize_source(target,self.pin,{},known={self.pin['file']+'!'+self.automated:'New original invalidity evidence'})

    def test_retained_proof_cannot_move_to_a_different_original_zip_pin(self):
        with tempfile.TemporaryDirectory() as root:
            target,_,rows=self.run_draft(root)
            row=next(r for r in rows if r['source_rule']==self.automated)
            record={k:row[k] for k in ['source_rule_sha256','authoring_sha256','program_sha256']}
            record['source_zip_sha256']='wrong pinned source'
            with self.assertRaisesRegex(ValueError,'original ZIP pin drift'):
                finalize_source(target,self.pin,{self.pin['file']+'!'+self.automated:record})

if __name__=='__main__':unittest.main()
