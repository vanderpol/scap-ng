"""#261: native identities, non-destructive layout and editor transaction gates."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scap_ng_library.documents import canonical_yaml, digest, parse, validate
from scap_ng_library.export import export_draft
from scap_ng_library.index import Library
from scap_ng_library.advisory import census
from scap_ng_library.transaction import apply_plan, atomic_write

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/v04-native-library/focused-draft'


class NativeLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared=tempfile.TemporaryDirectory();cls.base=Path(cls.shared.name)/'export'
        cls.receipt=export_draft(FIXTURE,cls.base)
    @classmethod
    def tearDownClass(cls):cls.shared.cleanup()
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)/'library';shutil.copytree(self.base,self.root)
        self.content=self.root/'content'
    def library(self,changed=None,full=False):
        lib=Library(self.content);self.addCleanup(lib.close);lib.refresh(changed,full=full);return lib
    def assessment(self,lib):return lib.rows("WHERE kind='assessment' ORDER BY path")[0]
    def write(self,path,doc):
        target=self.content/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(canonical_yaml(doc))
    def body(self,row):return parse((self.content/row['path']).read_bytes())

    def test_original_derived_linux_windows_shared_object_warning_and_manual_records(self):
        self.assertEqual(self.receipt['conversion_statuses'],{'CONVERTED_VERIFIED':3,'CONVERTED_UNVERIFIED':1,'MANUAL_OCIL_ONLY_PRESERVED':3})
        self.assertEqual(self.receipt['retained_proof_hash_pairs'],3)
        self.assertEqual(self.receipt['compiled_program_hashes_unchanged'],4)
        lib=self.library(full=True);self.assertEqual(lib.check()['status'],'PASS')
        rows=lib.rows("WHERE kind='assessment'",payload=True)
        self.assertTrue(any(json.loads(r['payload'])['assessment'].get('shared_objects') for r in rows))
        self.assertTrue(any(json.loads(r['warnings']) for r in rows))
        for path in self.content.rglob('*'):
            if path.is_file():self.assertEqual(path.suffix,'.yaml');self.assertLessEqual(len(path.relative_to(self.content).as_posix()),190)
        self.assertEqual(len(list((self.root/'records/streams').glob('*.json'))),3)

    def test_export_and_second_analysis_are_idempotent_and_source_untouched(self):
        before={p:sha256(p.read_bytes()).hexdigest() for p in FIXTURE.rglob('*') if p.is_file()}
        output=Path(self.temporary.name)/'second';export_draft(FIXTURE,output)
        for p in (self.base/'content').rglob('*.yaml'):
            self.assertEqual(p.read_bytes(),(output/'content'/p.relative_to(self.base/'content')).read_bytes())
        lib=self.library();self.assertEqual(lib.plan()['changes'],[])
        self.assertEqual(before,{p:sha256(p.read_bytes()).hexdigest() for p in before})
        with self.assertRaises(ValueError):export_draft(FIXTURE,FIXTURE/'nested')
        with self.assertRaises(ValueError):export_draft(FIXTURE,self.root)

    def test_read_only_cache_incremental_edit_and_reverse_closure(self):
        lib=self.library();a=self.assessment(lib);before=(self.root/'metadata/library.sqlite').read_bytes()
        raw=(self.content/a['path']).read_bytes();(self.content/a['path']).write_bytes(raw+b'\n')
        updated=self.library([a['path']]);r=updated.check(changed=[a['path']])
        self.assertEqual(r['status'],'PASS');self.assertEqual(updated.parsed,1)
        self.assertTrue(r['affected_consumers']);self.assertEqual(before,(self.root/'metadata/library.sqlite').read_bytes())
        self.assertTrue(updated.consumers(updated.rows('WHERE path=?',(a['path'],))[0],transitive=True))

    def test_changed_proof_payload_is_reported_unverified_not_inherited(self):
        lib=self.library();a=next(r for r in lib.rows("WHERE kind='assessment'") if r['status']=='CONVERTED_VERIFIED')
        doc=self.body(a);doc['assessment']['assessment_title']+=' updated';self.write(a['path'],doc)
        changed=self.library([a['path']]);r=changed.check(changed=[a['path']])
        self.assertEqual(r['status'],'PASS')
        self.assertIn('proof-no-longer-matches',[d['code'] for d in r['diagnostics']])
        self.assertEqual(changed.rows('WHERE path=?',(a['path'],))[0]['status'],'MODIFIED_UNVERIFIED')

    def test_move_is_identity_neutral_and_preserves_proof_provenance(self):
        lib=self.library();a=self.assessment(lib);old=self.content/a['path'];new=old.with_name('renamed-assessment.yaml');old.rename(new)
        moved=new.relative_to(self.content).as_posix();changed=self.library([a['path'],moved]);self.assertEqual(changed.check()['status'],'PASS')
        row=changed.rows('WHERE path=?',(moved,))[0]
        self.assertEqual((row['id'],row['authoring_sha'],row['status']),(a['id'],a['authoring_sha'],a['status']))
        self.assertTrue(changed.consumers(row))

    def test_duplicate_same_id_even_identical_payload_and_version_is_error(self):
        lib=self.library();a=self.assessment(lib);p=Path(a['path']).with_name('duplicate.yaml').as_posix();self.write(p,self.body(a))
        r=self.library(full=True).check();self.assertEqual(r['status'],'FAIL')
        self.assertIn('duplicate-identity',[d['code'] for d in r['diagnostics']])

    def test_missing_deletion_and_wrong_kind_never_guess(self):
        lib=self.library();a=self.assessment(lib);(self.content/a['path']).unlink()
        r=self.library([a['path']]).check();self.assertEqual(r['status'],'FAIL')
        self.assertIn('missing-target',[d['code'] for d in r['diagnostics']])
        rule=next(r for r in lib.rows("WHERE kind='rule'") if r['scope']==a['scope'])
        doc=self.body(rule);doc['rule']['assessment_choices']['automated']['assessment']=rule['id'];self.write(rule['path'],doc)
        r=self.library([a['path'],rule['path']]).check()
        self.assertIn('wrong-kind',[d['code'] for d in r['diagnostics']])

    def test_cross_private_scope_binding_rejected_and_global_shared_supported(self):
        lib=self.library();a=self.assessment(lib);rule=next(r for r in lib.rows("WHERE kind='rule'") if r['scope']!=a['scope'])
        doc=self.body(rule);doc['rule']['assessment_choices']['automated']['assessment']=a['id'];self.write(rule['path'],doc)
        r=self.library([rule['path']]).check();self.assertIn('cross-scope',[d['code'] for d in r['diagnostics']])
        target=self.content/'assessments/shared/global'/Path(a['path']).name;target.parent.mkdir(parents=True)
        (self.content/a['path']).rename(target)
        r=self.library([a['path'],target.relative_to(self.content).as_posix(),rule['path']]).check()
        self.assertEqual(r['status'],'PASS',r['diagnostics'])

    def test_scope_case_collision_path_collision_and_scope_extension_rejected(self):
        lib=self.library();a=self.assessment(lib)
        original=Path(a['path']);p=original.with_name(original.name.upper());self.write(p.as_posix(),self.body(a))
        r=self.library(full=True).check();self.assertEqual(r['status'],'FAIL')
        p=self.content/'assessments/shared/windows/example.yaml';p.parent.mkdir(parents=True);p.write_bytes(canonical_yaml(self.body(a)))
        r=self.library(full=True).check();self.assertTrue(any('only existing global' in d['message'] for d in r['diagnostics']))

    def test_standalone_manual_assessment_and_dependency_versions_cycles(self):
        standalone=Path(self.temporary.name)/'standalone';standalone.mkdir()
        manual={'assessment':{'id':'review-process','version':1,'assessment_title':'Review process',
            'mode':'manual','class':'compliance','purpose':'assessment','procedure':'Review records.',
            'response':{'type':'human-compliance-disposition','choices':[
                {'value':'compliant','outcome':'true'},{'value':'noncompliant','outcome':'false'}],
                'allow_comment':True,'allow_evidence':True}}}
        validate(manual);(standalone/'review.yaml').write_bytes(canonical_yaml(manual))
        a=Library(standalone);self.addCleanup(a.close);a.refresh();self.assertEqual(a.check()['status'],'PASS')
        primary=deepcopy(self.body(self.assessment(self.library())))
        primary['assessment']['id']='review-primary'
        (standalone/'primary.yaml').write_bytes(canonical_yaml(primary))
        second=deepcopy(primary);second['assessment']['id']='review-secondary';second['assessment']['dependencies']={
            'primary':{'assessment':'review-primary','expected_version':2,'purpose':'assessment'}}
        (standalone/'second.yaml').write_bytes(canonical_yaml(second));a.refresh(full=True)
        self.assertIn('version-mismatch',[d['code'] for d in a.check()['diagnostics']])
        second['assessment']['dependencies']['primary']['expected_version']=1
        primary['assessment']['dependencies']={'second':{'assessment':'review-secondary','expected_version':1,'purpose':'assessment'}}
        (standalone/'primary.yaml').write_bytes(canonical_yaml(primary));(standalone/'second.yaml').write_bytes(canonical_yaml(second));a.refresh(full=True)
        self.assertIn('reference-cycle',[d['code'] for d in a.check()['diagnostics']])

    def test_applicability_reference_and_embedded_profiles_resolve(self):
        lib=self.library();a=self.assessment(lib)
        catalog=next(r for r in lib.rows("WHERE kind='applicability'") if r['scope']==a['scope'])
        doc=self.body(catalog);doc['applicability']['conditions']['example-present']={'assessment':a['id']};self.write(catalog['path'],doc)
        r=self.library([catalog['path']]).check();self.assertEqual(r['status'],'PASS',r['diagnostics'])
        doc['applicability']['conditions']['example-present']['assessment']='missing';self.write(catalog['path'],doc)
        r=self.library([catalog['path']]).check();self.assertIn('missing-target',[d['code'] for d in r['diagnostics']])
        self.assertTrue(any(self.body(b)['benchmark'].get('profiles') for b in lib.rows("WHERE kind='benchmark'")))

    def test_presentation_plan_stale_semantic_mutation_and_rollback(self):
        lib=self.library();a=self.assessment(lib);path=self.content/a['path'];path.write_bytes(path.read_bytes()+b'\n')
        lib=self.library([a['path']]);plan=lib.plan([a['path']]);self.assertEqual(len(plan['changes']),1)
        bad=deepcopy(plan);bad['changes'][0]['replacement']=bad['changes'][0]['replacement'].replace(a['id'],'different-id')
        bad['changes'][0]['after_sha256']=sha256(bad['changes'][0]['replacement'].encode()).hexdigest();bad['plan_sha256']=digest(bad['changes'])
        with self.assertRaises(ValueError):apply_plan(lib,bad)
        result=apply_plan(lib,plan);self.assertEqual(result['changed_files'],[a['path']])
        self.assertEqual(self.library().plan()['changes'],[])
        with self.assertRaises(ValueError):apply_plan(lib,plan)
        # Failure during a multi-file replace restores previously written bytes.
        files=lib.rows("WHERE kind='assessment' ORDER BY path")[:2]
        for row in files:
            p=self.content/row['path'];p.write_bytes(p.read_bytes()+b'\n')
        lib=self.library([r['path'] for r in files]);before={r['path']:(self.content/r['path']).read_bytes() for r in files};plan=lib.plan(list(before))
        calls=0
        def fail_once(path,raw):
            nonlocal calls
            calls+=1
            if calls==2:raise OSError('injected second replacement failure')
            atomic_write(path,raw)
        with patch('scap_ng_library.transaction.atomic_write',side_effect=fail_once),self.assertRaises(OSError):apply_plan(lib,plan)
        self.assertEqual(before,{r:(self.content/r).read_bytes() for r in before})

    def test_reuse_census_never_merges_and_near_is_explicit_bounded(self):
        lib=self.library();a=self.assessment(lib);copy=deepcopy(self.body(a));copy['assessment']['id']='review-copy';self.write(Path(a['path']).with_name('copy.yaml').as_posix(),copy)
        lib=self.library(full=True);before={p:p.read_bytes() for p in self.content.rglob('*.yaml')}
        c=census(lib,near=True,max_pairs=2);self.assertTrue(c['exact_candidates']);self.assertFalse(c['promotion_performed']);self.assertLessEqual(c['near_pairs_examined'],2)
        self.assertEqual(before,{p:p.read_bytes() for p in before})

    def test_parser_rejects_duplicate_keys_alias_cycle_nan_and_path_escape(self):
        for raw in [b'assessment: {id: x, id: y}',b'assessment: &x {id: x, cycle: *x}',b'assessment: {id: x, value: .nan}']:
            with self.subTest(raw=raw),self.assertRaises((ValueError,TypeError)):parse(raw)
        lib=self.library()
        with self.assertRaises(ValueError):lib.update('../escape.yaml',b'assessment: {id: bad}')
        with self.assertRaises(ValueError):lib.update('CON.yaml',b'assessment: {id: bad}')

    def test_unchanged_compiler_programs_and_cli_readonly_contract(self):
        lib=self.library()
        for scope in sorted({r['scope'] for r in lib.rows("WHERE kind='benchmark'")}):
            raw,manifest=lib.compile_scope(scope);self.assertTrue(raw)
            programs=manifest['build_provenance']['compiled_programs']
            for a in lib.rows("WHERE kind='assessment' AND scope=?",(scope,)):
                self.assertEqual(programs[a['id']]['sha256'],a['program_sha'])
        before={p:p.read_bytes() for p in self.content.rglob('*.yaml')}
        for command in ['check','analyze']:
            result=subprocess.run([sys.executable,str(ROOT/'tools/scap_ng_repo_normalizer.py'),'v04',command,str(self.content)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertEqual(json.loads(result.stdout)['status'],'PASS')
        self.assertEqual(before,{p:p.read_bytes() for p in before})


if __name__=='__main__':unittest.main()
