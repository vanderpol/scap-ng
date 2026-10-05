#!/usr/bin/env python3
import copy
import hashlib
import json
import unittest
from jsonschema import ValidationError
from assessment_results_v02 import assemble_result_set,validate_result_set,validate_schema,ROOT
from assessment_expression import AssessmentExpressionEvaluator
from item_materialization_v02 import materialize_observations,import_items
import test_assessment_results_v02 as result_fixtures

class MaterializationTests(unittest.TestCase):
    def setUp(self):
        self.fixture=result_fixtures.AssessmentResultTests();self.fixture.setUp()
        self.observations=copy.deepcopy(self.fixture.owner)
        extra=copy.deepcopy(self.observations['items'][0]);extra['id']='file-unused';extra['fields']['full_path']['value']='/fixture/unused'
        self.observations['items'].append(extra);self.observations['objects'][0]['item_refs'].append(extra['id'])
        self.source=self.fixture.rows(self.fixture.build())['results.ownership']
        self.source['binding_set_id']='fixture-bindings-empty'
    def bytes(self,source=None): return json.dumps({'assessment_result':source or self.source},sort_keys=True).encode('utf-8')
    def import_one(self,source=None,**overrides):
        data=self.bytes(source);args={'expected_digest':'sha256:'+hashlib.sha256(data).hexdigest(),'expected_execution_id':(source or self.source)['execution_id'],
                                     'target_ref':'fixture-target','binding_set_id':'fixture-bindings-empty','item_refs':['file-config'],'local_ids':{'file-config':'local-file'}}
        args.update(overrides);return import_items(data,**args)
    def consume(self,items,scope='all'):
        source=self.fixture.sources['results.ownership'];graph={source['id']:source}
        expression=AssessmentExpressionEvaluator(graph).run(source['id'],lambda *_:'false',target='fixture-target')
        obs=copy.deepcopy(self.fixture.owner);obs['items']=items;obs['binding_set_id']='fixture-bindings-empty'
        old='file-config';new=items[0]['id']
        obs['tests'][0]['item_refs']=[new];obs['tests'][0]['per_item_results'][0]['item_ref']=new
        obs['objects'][0]['item_refs']=[new];obs['field_uses'][0]['item_ref']=new
        return assemble_result_set(graph,expression,{source['id']:obs},item_scope=scope),graph
    def test_expected_all_and_consumed_materialization(self):
        expected=json.loads((ROOT/'tests/item-materialization-0.2.0/expected-results/scopes.json').read_text())
        for scope in ('all','consumed'):
            result=materialize_observations(self.observations,scope=scope)
            self.assertEqual([item['id'] for item in result['items']],expected[scope]['items'])
            self.assertEqual(result['item_materialization'],expected[scope]['metadata'])
            self.assertEqual(result['objects'][0]['item_refs'],expected[scope]['items'])
            self.assertTrue(result['population_complete']);self.assertTrue(result['evidence_complete'])
    def test_default_all_input_not_mutated(self):
        original=copy.deepcopy(self.observations)
        result=materialize_observations(self.observations);self.assertEqual(len(result['items']),2)
        self.assertEqual(self.observations,original)
    def test_indirect_field_use_and_variable_inputs_are_consumed(self):
        obs=copy.deepcopy(self.observations);obs['field_uses'].append({'test_ref':'test-owner','item_ref':'file-unused','relationship':'filter','used_elements':['owner_uid'],'required_elements':['full_path']})
        self.assertEqual(len(materialize_observations(obs,scope='consumed')['items']),2)
        obs['field_uses'].pop();obs['variables']=[{'id':'extract','item_refs':['file-unused']}]
        self.assertEqual(len(materialize_observations(obs,scope='consumed')['items']),2)
    def test_empty_consumption_retains_counts_without_population_claim(self):
        obs=copy.deepcopy(self.observations);obs['tests']=[];obs['field_uses']=[];obs['population_complete']=False;obs['evidence_complete']=False
        result=materialize_observations(obs,scope='consumed')
        self.assertEqual(result['items'],[]);self.assertEqual(result['item_materialization']['omitted_count'],2)
        self.assertEqual(result['objects'][0]['status'],'complete');self.assertFalse(result['population_complete'])
    def test_reject_missing_duplicate_and_invalid_scope(self):
        for mutate in (lambda o:o['tests'][0]['item_refs'].append('missing'),lambda o:o['items'].append(o['items'][0]),lambda o:o['objects'][0]['item_refs'].append('missing')):
            obs=copy.deepcopy(self.observations);mutate(obs)
            with self.assertRaises(ValueError):materialize_observations(obs,scope='consumed')
        with self.assertRaises(ValueError):materialize_observations(self.observations,scope='none')
    def test_unused_bad_or_redacted_values_cannot_hide_through_consumed_scope(self):
        for mutate in (lambda i:i['fields']['owner_uid'].update(redacted=True),lambda i:i['fields'].update(invented={'datatype':'string','value':'x'})):
            obs=copy.deepcopy(self.observations);mutate(obs['items'][1])
            with self.assertRaises((ValueError,ValidationError)):materialize_observations(obs,scope='consumed')
    def test_verified_import_preserves_values_names_metadata_and_local_identity(self):
        source=copy.deepcopy(self.source);item=self.import_one()[0]
        self.assertEqual(item['id'],'local-file');self.assertTrue(item['imported'])
        self.assertEqual(item['fields'],source['items'][0]['fields'])
        self.assertEqual(item['context']['name_resolution'],source['items'][0]['context']['name_resolution'])
        self.assertEqual(item['context']['origin']['item_ref'],'file-config')
        self.assertEqual(item['context']['origin']['result_ref'],source['execution_id'])
        self.assertEqual(self.source,source)
        doc,graph=self.consume([item]);validate_result_set(doc,graph)
    def test_digest_execution_target_binding_and_missing_observation_rejected(self):
        for args in ({'expected_digest':'sha256:'+'0'*64},{'expected_execution_id':'wrong'},{'target_ref':'wrong'},{'binding_set_id':'wrong'},
                     {'item_refs':['missing'],'local_ids':{'missing':'local-file'}},{'local_ids':{'file-config':''}}):
            with self.subTest(args=args),self.assertRaises(ValueError):self.import_one(**args)
    def test_import_duplicate_mappings_source_ids_and_payload_rejected(self):
        with self.assertRaises(ValueError):self.import_one(item_refs=['file-config','file-config'])
        source=copy.deepcopy(self.source);source['items'].append(copy.deepcopy(source['items'][0]))
        with self.assertRaises(ValueError):self.import_one(source=source)
        source=copy.deepcopy(self.source);source['items'][0]['fields']['owner_uid']['redacted']=True
        with self.assertRaises((ValueError,ValidationError)):self.import_one(source=source)
    def test_reimport_preserves_chain_without_re_resolving(self):
        first=self.import_one()[0];doc,graph=self.consume([first]);source=doc['assessment_results'][0]['assessment_result']
        second=self.import_one(source=source,item_refs=['local-file'],local_ids={'local-file':'second-file'})[0]
        self.assertEqual(second['context']['import_history'],[first['context']['origin']])
        self.assertEqual(second['context']['origin']['item_ref'],'local-file')
        self.assertEqual(second['fields'],first['fields'])
    def test_imported_incompleteness_is_conservative_and_truth_not_imported(self):
        source=copy.deepcopy(self.source);source['population_complete']=False;source['evidence_complete']=False
        item=self.import_one(source=source)[0];doc,graph=self.consume([item]);row=doc['assessment_results'][0]['assessment_result']
        self.assertFalse(row['population_complete']);self.assertFalse(row['evidence_complete']);self.assertEqual(row['outcome'],'false')
        row['population_complete']=True
        with self.assertRaises(ValueError):validate_result_set(doc,graph)
    def test_consumer_binding_and_local_collision_rejected(self):
        item=self.import_one()[0];doc,graph=self.consume([item]);doc['assessment_results'][0]['assessment_result']['binding_set_id']='other'
        with self.assertRaises(ValueError):validate_result_set(doc,graph)
        with self.assertRaises(ValueError):self.consume([item,item])
    def test_metadata_tampering_and_variable_dangling_refs_rejected(self):
        doc=self.fixture.build();row=self.fixture.rows(doc)['results.ownership']
        row['item_materialization']['included_count']=2
        with self.assertRaises(ValueError):validate_result_set(doc,self.fixture.sources)
        doc=self.fixture.build();self.fixture.rows(doc)['results.conditional']['variables'][0]['item_refs']=['missing']
        with self.assertRaises(ValueError):validate_result_set(doc,self.fixture.sources)
    def test_duplicate_json_members_rejected_even_with_matching_digest(self):
        data=self.bytes();data=b'{"assessment_result":null,'+data[1:]
        with self.assertRaises(ValueError):import_items(data,expected_digest='sha256:'+hashlib.sha256(data).hexdigest(),expected_execution_id=self.source['execution_id'],target_ref='fixture-target',binding_set_id='fixture-bindings-empty',item_refs=[],local_ids={})
    def test_pinned_origin_requires_complete_context(self):
        item=self.import_one()[0];del item['context']['origin']['binding_set_id']
        with self.assertRaises(ValidationError):validate_schema('collected-item.schema.json',item)

    def test_board_materialized_item_example_is_valid(self):
        item=json.loads((ROOT/'board/review-content/0.2.0/proposals/item-reuse-materialized-item.json').read_text())
        validate_schema('collected-item.schema.json',item)
        self.assertTrue(item['imported'])
        self.assertEqual(item['context']['origin']['item_ref'],'configuration-file-001')
        self.assertEqual(item['context']['origin']['source_execution_ref'],
                         'shared-file-collection-execution-20261005-001')

    def test_committed_import_snapshot_matches_verified_source_bytes(self):
        directory=ROOT/'tests/item-materialization-0.2.0'
        expected=json.loads((directory/'expected-results/imported-items.json').read_text())
        actual=import_items((directory/'source.assessment-result.json').read_bytes(),expected_digest=expected['source_digest'],expected_execution_id='fixture-source-ownership-execution',target_ref='fixture-target',binding_set_id='fixture-bindings-empty',item_refs=['file-config'],local_ids={'file-config':'local-file'})
        self.assertEqual(actual,expected['items'])

    def test_nonfinite_keywords_and_overflow_numbers_rejected(self):
        for value in (b'NaN',b'Infinity',b'1e999',b'1e-999',b'0.10000000000000001'):
            raw=self.bytes();data=b'{"ignored":'+value+b','+raw[1:]
            with self.subTest(value=value),self.assertRaises(ValueError):
                import_items(data,expected_digest='sha256:'+hashlib.sha256(data).hexdigest(),expected_execution_id=self.source['execution_id'],target_ref='fixture-target',binding_set_id='fixture-bindings-empty',item_refs=[],local_ids={})

if __name__=='__main__':unittest.main()
