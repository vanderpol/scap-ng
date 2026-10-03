#!/usr/bin/env python3
import copy
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator, ValidationError
from assessment_expression import AssessmentExpressionEvaluator, load_assessments, OUTCOMES
from assessment_results_v02 import assemble_result_set, validate_result_set, SCHEMAS, ROOT

FIXTURES=ROOT/'tests/assessment-results-0.2.0'
class AssessmentResultTests(unittest.TestCase):
    def setUp(self):
        self.sources=load_assessments(FIXTURES/'content')
        self.owner=json.loads((FIXTURES/'ownership-observations.json').read_text())
    def build(self,guard='true',sources=None,owner=None):
        sources=sources or self.sources
        owner=copy.deepcopy(owner or self.owner)
        def provider(identity,test,context):
            if identity=='results.conditional': return guard
            # Concrete ownership comparison from fixture observation and authored State.
            actual=owner['items'][0]['fields']['owner_uid']['value']
            expected=sources[identity]['states']['owner']['state']['value']
            return 'true' if actual==expected else 'false'
        expression=AssessmentExpressionEvaluator(sources).run('results.conditional',provider,target='fixture-target',bindings={'secret':'not-for-output'})
        evidence={'results.conditional':{'tests':[{'id':'test-guard','outcome':guard,'object_refs':[],'item_refs':[],'state_refs':['is-true']}],
                 'objects':[],'items':[],'variables':[{'id':'guard','datatype':'boolean','status':'complete','cardinality':'one','values':[{'datatype':'boolean','value':True}]}],
                 'field_uses':[],'diagnostics':[],'logical_complete':True,'population_complete':True,'evidence_complete':True}}
        if guard=='true': evidence['results.ownership']=owner
        return assemble_result_set(sources,expression,evidence)
    def rows(self,doc): return {r['assessment_result']['assessment']['id']:r['assessment_result'] for r in doc['assessment_results']}
    def test_all_draft_schemas_meta_validate(self):
        for path in SCHEMAS.glob('*.schema.json'): Draft202012Validator.check_schema(json.loads(path.read_text()))
    def test_six_known_results_actual_ownership_and_lazy_dependencies(self):
        for case in json.loads((FIXTURES/'expected-results/cases.json').read_text())['cases']:
            with self.subTest(case=case):
                doc=self.build(case['guard']); rows=self.rows(doc)
                self.assertEqual(rows['results.conditional']['outcome'],case['outcome'])
                self.assertEqual(sorted(rows),case['invoked'])
                if case['guard']=='true':
                    root=rows['results.conditional'];child=rows['results.ownership']
                    self.assertNotEqual(root['execution_id'],child['execution_id'])
                    self.assertEqual([d['reused'] for d in root['dependent_assessments']],[False,True])
                    self.assertEqual({d['execution_id'] for d in root['dependent_assessments']},{child['execution_id']})
                    self.assertEqual(sorted(child['item_report']['items'][0]['item']['fields']),case['ownership_fields'])
                    self.assertIn('owner_user_name',child['items'][0]['fields'])
                self.assertNotIn('not-for-output',json.dumps(doc))
    def reject(self,change):
        doc=self.build();change(doc,self.rows(doc))
        with self.assertRaises((ValueError,ValidationError)): validate_result_set(doc,self.sources)
    def test_reject_dangling_and_cross_invocation_dependencies(self):
        self.reject(lambda d,r:r['results.conditional']['dependent_assessments'][0].update(execution_id='missing'))
        self.reject(lambda d,r:r['results.conditional']['dependent_assessments'][0].update(execution_id=r['results.conditional']['execution_id']))
        self.reject(lambda d,r:r['results.conditional']['dependent_assessments'][0].update(outcome='true'))
    def test_reject_duplicates_and_wrong_target(self):
        self.reject(lambda d,r:d['assessment_results'].append(copy.deepcopy(d['assessment_results'][0])))
        self.reject(lambda d,r:r['results.ownership']['items'].append(copy.deepcopy(r['results.ownership']['items'][0])))
        self.reject(lambda d,r:r['results.ownership'].update(target_ref='other-target'))
        self.reject(lambda d,r:r['results.ownership']['items'][0]['provenance'].update(target_ref='other-target'))
    def test_reject_missing_local_materialization_and_wrong_bindings(self):
        self.reject(lambda d,r:r['results.ownership'].update(items=[]))
        self.reject(lambda d,r:r['results.ownership']['tests'][0].update(object_refs=[]))
        self.reject(lambda d,r:r['results.ownership']['tests'][0].update(state_refs=[]))
        self.reject(lambda d,r:r['results.conditional'].update(variables=[]))
        self.reject(lambda d,r:r['results.ownership']['objects'][0].update(item_refs=[]))
    def test_reject_missing_and_incomplete_lineage(self):
        self.reject(lambda d,r:r['results.ownership'].update(field_uses=[]))
        self.reject(lambda d,r:r['results.ownership']['field_uses'][0].update(used_elements=[]))
        self.reject(lambda d,r:r['results.ownership']['field_uses'][0].update(test_ref='unexecuted-test'))
    def test_reject_forged_projection_and_completeness(self):
        self.reject(lambda d,r:r['results.ownership']['item_report']['items'][0]['item']['fields'].update(owner_uid={'datatype':'integer','value':0}))
        self.reject(lambda d,r:r['results.ownership']['item_report']['source_completeness'].update(population_complete=False))
        owner=copy.deepcopy(self.owner);owner['population_complete']=False;owner['evidence_complete']=False
        doc=self.build(owner=owner);r=self.rows(doc)['results.ownership']
        self.assertFalse(r['population_complete']);self.assertFalse(r['item_report']['source_completeness']['population_complete'])
        self.assertEqual(r['outcome'],'false')
    def test_reject_forged_conditional_trace(self):
        self.reject(lambda d,r:r['results.conditional']['expression_execution']['trace'][-1].update(selected_branch='else'))
        self.reject(lambda d,r:r['results.ownership']['expression_execution']['trace'][0].update(owner_invocation_ref=r['results.conditional']['execution_id']))
    def test_redaction_covers_canonical_items_and_comparison_values(self):
        self.reject(lambda d,r:r['results.ownership']['items'][0]['fields']['owner_uid'].update(redacted=True))
        self.reject(lambda d,r:r['results.ownership']['tests'][0]['per_item_results'][0]['state_results'][0]['entity_results'][0]['comparison_results'][0]['expected_value'].update(redacted=True))
    def test_imported_observations_keep_local_values_and_origin(self):
        owner=copy.deepcopy(self.owner);item=owner['items'][0];item['imported']=True;item['context']['origin']={'result_ref':'original-result','item_ref':'original-item'}
        doc=self.build(owner=owner);row=self.rows(doc)['results.ownership']
        self.assertEqual(row['items'][0]['context']['origin'],item['context']['origin'])
        self.assertEqual(row['items'][0]['fields']['owner_uid']['value'],1001)
        self.assertEqual(row['item_report']['items'][0]['item']['context']['origin'],item['context']['origin'])
    def test_known_field_absence_status_and_resolution_failures(self):
        self.reject(lambda d,r:r['results.ownership']['items'][0]['fields'].update(invented={'datatype':'string','value':'x'}))
        self.reject(lambda d,r:r['results.ownership']['items'][0]['context']['name_resolution']['owner_user_name'].update(source_field='owner_gid'))
        self.reject(lambda d,r:r['results.ownership']['items'][0]['fields']['owner_uid'].update(status='error'))
    def test_producer_evidence_not_mutated_and_report_optional(self):
        original=copy.deepcopy(self.owner);self.build();self.assertEqual(self.owner,original)
        doc=self.build();[r['assessment_result'].pop('item_report') for r in doc['assessment_results']]
        validate_result_set(doc,self.sources)
    def test_missing_result_diagnostic_and_global_ledger(self):
        sources=copy.deepcopy(self.sources);sources['results.conditional']['evaluate']={'test':'test-guard'}
        expression=AssessmentExpressionEvaluator(sources).run('results.conditional',lambda *_:None,target='fixture-target')
        doc=self.build('error',sources=sources);obs={r['assessment_result']['assessment']['id']:{k:v for k,v in r['assessment_result'].items() if k in {'tests','objects','items','variables','field_uses','diagnostics','logical_complete','population_complete','evidence_complete'}} for r in doc['assessment_results']}
        assemble_result_set(sources,expression,obs)
        expression['outcome']='true'
        with self.assertRaises(ValueError): assemble_result_set(sources,expression,obs)

    def test_manual_outcome_provenance_and_redacted_bindings(self):
        source={'id':'results.manual','version':1,'assessment_title':'Fixture manual determination','mode':'manual','class':'compliance','purpose':'assessment',
                'procedure':'Inspect fixture evidence','response':{'type':'fixture-response','choices':[{'value':'yes','outcome':'true'}], 'allow_comment':True,'allow_evidence':True}}
        sources={source['id']:source}
        for outcome in OUTCOMES:
            expression=AssessmentExpressionEvaluator(sources).run(source['id'],lambda *_:self.fail('Manual result invoked Test provider'),target='fixture-target',evaluate_manual=lambda *_:outcome)
            evidence={'tests':[],'objects':[],'items':[],'variables':[],'diagnostics':[],'field_uses':[],
                      'logical_complete':True,'population_complete':True,'evidence_complete':True,
                      'input_bindings':[{'input':'credential','source':'fixture','redacted':True}]}
            if outcome!='not_evaluated':
                evidence['manual_response']={'outcome':outcome,'completed_at':'2026-10-03T00:00:00Z','response_source':'direct','evaluator':{'id':{'scheme':'fixture','value':'reviewer-1'}}}
            doc=assemble_result_set(sources,expression,{source['id']:evidence})
            row=doc['assessment_results'][0]['assessment_result'];self.assertEqual(row['outcome'],outcome)
            if outcome!='not_evaluated':
                row['manual_response']['outcome']='false' if outcome=='true' else 'true'
                with self.assertRaises(ValueError): validate_result_set(doc,sources)
    def test_committed_full_result_example_validates(self):
        validate_result_set(json.loads((FIXTURES/'expected-results/conditional-ownership.result-set.json').read_text()),self.sources)
    def test_separate_runs_have_distinct_execution_identities(self):
        a=self.build();b=self.build()
        self.assertTrue({r['assessment_result']['execution_id'] for r in a['assessment_results']}.isdisjoint({r['assessment_result']['execution_id'] for r in b['assessment_results']}))
    def test_skipped_dependencies_cannot_attach_results(self):
        doc=self.build('false');extra=self.build()['assessment_results'][0]
        doc['assessment_results'].append(extra)
        with self.assertRaises(ValueError): validate_result_set(doc,self.sources)

if __name__=='__main__': unittest.main()
