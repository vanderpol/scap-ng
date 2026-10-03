#!/usr/bin/env python3
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile
from jsonschema import ValidationError
from result_package_v02 import write_result_package,verify_result_package,encode,decode
import test_assessment_results_v02 as fixtures

class ResultPackageTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.AssessmentResultTests();self.fixture.setUp();self.results=self.fixture.build();self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'fixture.results.zip'
        entry=self.results['entry_execution_id'];outcome='fail'
        identity={'id':'results.conditional','version':1,'mode':'automated'}
        self.benchmark={'benchmark_result':{'result_schema_version':'0.2.0','run_id':'fixture-run','started_at':'2026-10-03T00:00:00Z','completed_at':'2026-10-03T00:00:01Z',
            'benchmark':{'id':'fixture.benchmark','version':1},'target_ref':'fixture-target',
            'effective_policy':{'profile':None,'tailoring':None,'selected_rules':['rule-ownership'],'disabled_rules':[],'check_selectors':{'rule-ownership':'automated'},'parameters':{},'organizational_inputs':{}},
            'summary':{'total':1,'pass':0,'fail':1,'not_applicable':0,'not_evaluated':0,'error':0,'unknown':0},
            'rule_results':[{'rule_id':'rule-ownership','outcome':outcome,'assessment':identity,'message':'Ownership fixture failed','check_selector':'automated',
                             'instances':[{'id':'ownership-instance','outcome':outcome,'assessment_result_ref':entry,'assessment_invocation_id':entry}]}]}}
        self.scan={'scan_result':{'result_schema_version':'0.2.0','run_id':'fixture-run','started_at':'2026-10-03T00:00:00Z','scanner':{'name':'synthetic-result-producer'},'targets':[{'id':'fixture-target'}],
            'benchmark_results':[{'benchmark_result_ref':'fixture-benchmark-result','benchmark_id':'fixture.benchmark','benchmark_version':1,'target_ref':'fixture-target'}],
            'assessment_result_refs':[r['assessment_result']['execution_id'] for r in self.results['assessment_results']],'signature_status':'unsigned'}}
    def write(self,**kwargs):
        return write_result_package(self.path,self.scan,{'fixture-benchmark-result':self.benchmark},[self.results],assessments=self.fixture.sources,**kwargs)
    def mutate(self,change,rehash=False):
        with zipfile.ZipFile(self.path) as z:members={i.filename:z.read(i) for i in z.infolist()}
        manifest=decode(members['manifest.json']);change(members,manifest)
        if rehash:
            for row in manifest['members']:
                row['sha256']=hashlib.sha256(members[row['path']]).hexdigest();row['size']=len(members[row['path']])
        members['manifest.json']=encode(manifest)
        with zipfile.ZipFile(self.path,'w') as z:
            for name,raw in members.items():z.writestr(name,raw)
    def test_committed_known_result(self):
        root=Path(__file__).resolve().parents[1]/'tests/result-package-0.2.0'
        inputs=decode((root/'package-input.json').read_bytes())
        write_result_package(self.path,inputs['scan'],inputs['benchmarks'],inputs['result_sets'],assessments=self.fixture.sources)
        self.assertEqual(verify_result_package(self.path,assessments=self.fixture.sources),decode((root/'expected-results/receipt.json').read_bytes()))

    def test_roundtrip_integrity_and_source_aware_validation(self):
        self.write();actual=verify_result_package(self.path,assessments=self.fixture.sources)
        self.assertEqual(actual['assessment_results'],2);self.assertEqual(actual['signature_status'],'unsigned')
        self.assertEqual(actual['semantic_validation'],'references_and_expression_scheduling')
        self.assertEqual(verify_result_package(self.path)['semantic_validation'],'references')
    def test_repeat_writes_deterministic_and_input_immutable(self):
        original=copy.deepcopy(self.results);self.write();raw=self.path.read_bytes();self.write();self.assertEqual(raw,self.path.read_bytes());self.assertEqual(original,self.results)
    def test_member_tampering_rejected(self):
        self.write();self.mutate(lambda files,m:files.update({m['members'][0]['path']:b'{}'}))
        with self.assertRaises(ValueError):verify_result_package(self.path)
    def test_rehashed_wrong_execution_rejected(self):
        self.write()
        def change(files,m):
            row=next(r for r in m['members'] if r['kind']=='benchmark_result');doc=decode(files[row['path']]);doc['benchmark_result']['rule_results'][0]['instances'][0]['assessment_invocation_id']='wrong';files[row['path']]=encode(doc)
        self.mutate(change,True)
        with self.assertRaises(ValueError):verify_result_package(self.path)
    def test_missing_and_extra_members_rejected(self):
        self.write();self.mutate(lambda files,m:files.update({'unexpected.json':b'{}'}))
        with self.assertRaises(ValueError):verify_result_package(self.path)
        self.write();self.mutate(lambda files,m:files.pop(m['members'][0]['path']))
        with self.assertRaises((ValueError,KeyError)):verify_result_package(self.path)
    def test_unsafe_duplicate_and_case_collision_paths_rejected(self):
        self.write();self.mutate(lambda files,m:files.update({'../escape.json':b'{}'}))
        with self.assertRaises(ValueError):verify_result_package(self.path)
        self.write()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            with zipfile.ZipFile(self.path,'a') as z:z.writestr('manifest.json',b'{}')
        with self.assertRaises(ValueError):verify_result_package(self.path)
        self.write();self.mutate(lambda files,m:files.update({'MANIFEST.JSON':b'{}'}))
        with self.assertRaises(ValueError):verify_result_package(self.path)
    def test_resource_bounds_and_symlink_rejected(self):
        self.write()
        with self.assertRaises(ValueError):verify_result_package(self.path,max_members=1)
        with self.assertRaises(ValueError):verify_result_package(self.path,max_uncompressed_bytes=1)
        info=zipfile.ZipInfo('link.json');info.create_system=3;info.external_attr=0o120777<<16
        with zipfile.ZipFile(self.path,'a') as z:z.writestr(info,b'outside')
        with self.assertRaises(ValueError):verify_result_package(self.path)
    def test_run_target_summary_and_selected_rule_mismatches_rejected(self):
        for field,value in [('run_id','wrong'),('target_ref','wrong')]:
            original=copy.deepcopy(self.benchmark);self.benchmark['benchmark_result'][field]=value
            with self.assertRaises(ValueError):self.write()
            self.benchmark=original
        self.benchmark['benchmark_result']['summary']['fail']=0
        with self.assertRaises(ValueError):self.write()
        self.benchmark['benchmark_result']['summary']['fail']=1;self.benchmark['benchmark_result']['effective_policy']['selected_rules']=[]
        with self.assertRaises(ValueError):self.write()
    def test_unreachable_overlapping_and_wrong_dependency_groups_rejected(self):
        self.write();self.mutate(lambda files,m:m['evaluation_groups'].append(copy.deepcopy(m['evaluation_groups'][0])))
        with self.assertRaises(ValueError):verify_result_package(self.path)
        self.write();self.mutate(lambda files,m:m['evaluation_groups'][0].update(entry_execution_id=self.results['assessment_results'][0]['assessment_result']['execution_id']))
        with self.assertRaises(ValueError):verify_result_package(self.path)
    def test_wrong_assessment_identity_and_missing_scan_registry_rejected(self):
        self.benchmark['benchmark_result']['rule_results'][0]['assessment']['version']=2
        with self.assertRaises(ValueError):self.write()
        self.benchmark['benchmark_result']['rule_results'][0]['assessment']['version']=1;self.scan['scan_result']['assessment_result_refs']=[]
        with self.assertRaises(ValueError):self.write()
    def test_redaction_and_local_item_reference_errors_rejected_without_sources(self):
        self.results['assessment_results'][0]['assessment_result']['items'][0]['fields']['owner_uid']['redacted']=True
        with self.assertRaises((ValueError,ValidationError)):self.write()
        self.setUp();self.write()
        def change(files,m):
            row=next(r for r in m['members'] if r['id']==self.results['assessment_results'][0]['assessment_result']['execution_id']);doc=decode(files[row['path']]);doc['assessment_result']['tests'][0]['item_refs']=['missing'];files[row['path']]=encode(doc)
        self.mutate(change,True)
        with self.assertRaises(ValueError):verify_result_package(self.path)
    def test_skipped_rule_without_execution_and_unsigned_status(self):
        rule=self.benchmark['benchmark_result']['rule_results'][0];rule['outcome']='not_evaluated';rule['instances'][0].update(outcome='not_evaluated',assessment_result_ref=None,assessment_invocation_id=None)
        self.benchmark['benchmark_result']['summary'].update(fail=0,not_evaluated=1);self.write();verify_result_package(self.path)
        self.scan['scan_result']['signature_status']='verified'
        with self.assertRaises(ValueError):self.write()
    def test_multiple_invocation_contexts_keep_distinct_artifacts(self):
        second=self.fixture.build();self.scan['scan_result']['assessment_result_refs'] += [r['assessment_result']['execution_id'] for r in second['assessment_results']]
        self.benchmark['benchmark_result']['rule_results'][0]['instances'].append({'id':'second','outcome':'fail','assessment_result_ref':second['entry_execution_id'],'assessment_invocation_id':second['entry_execution_id']})
        write_result_package(self.path,self.scan,{'fixture-benchmark-result':self.benchmark},[self.results,second],assessments=self.fixture.sources)
        self.assertEqual(verify_result_package(self.path,assessments=self.fixture.sources)['assessment_results'],4)
    def test_unbound_evidence_and_scope_pollution_rejected(self):
        self.benchmark['benchmark_result']['rule_results'][0]['evidence_refs']=['missing-evidence']
        with self.assertRaises(ValueError):self.write()
        self.benchmark['benchmark_result']['rule_results'][0].pop('evidence_refs');self.benchmark['benchmark_result']['rule_results'][0]['items']=[]
        with self.assertRaises(ValidationError):self.write()

if __name__=='__main__':unittest.main()
