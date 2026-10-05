#!/usr/bin/env python3
"""Assemble/validate invocation-linked draft results from supplied observations.

No acquisition or State comparison is performed here. Replay checks expression
scheduling against recorded Test outcomes; it does not prove their target truth.
"""
from __future__ import annotations
import argparse
import copy
import json
from functools import lru_cache
from pathlib import Path
from capability_registry import load_mapping
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from assessment_expression import AssessmentExpressionEvaluator, load_assessments
from collected_item_contract_v02 import capability_schema, context_errors
from reported_elements import project_items, _check_redaction
from item_materialization_v02 import materialize_observations, validate_materialization

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / 'schema/v0.2.0'
BASE = 'https://scap-ng.dev/schema/v0.2.0/'

@lru_cache(maxsize=1)
def registry():
    docs = [json.loads(p.read_text()) for version in ('v0.1.0', 'v0.2.0')
            for p in (ROOT / 'schema' / version).glob('*.schema.json')]
    return Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in docs)

def validate_schema(name, data):
    schema = json.loads((SCHEMAS / name).read_text())
    Draft202012Validator(schema, registry=registry(), format_checker=FormatChecker()).validate(data)

@lru_cache(maxsize=None)
def item_validator(capability):
    # Closed capability vocabulary and path protection use the reporting registry.
    from reported_elements import capability_fields
    capability_fields(capability)
    mapping = load_mapping(capability)
    schema = capability_schema(mapping)
    if schema is None:
        raise ValueError(f'{capability} does not produce Items')
    schema = json.loads(json.dumps(schema).replace('https://scap-ng.dev/experimental/0.2.0/', BASE))
    return Draft202012Validator(schema, registry=registry(), format_checker=FormatChecker())

def index(rows, label):
    found = {}
    for row in rows:
        if row['id'] in found:
            raise ValueError(f'Duplicate {label}: {row["id"]}')
        found[row['id']] = row
    return found

def check_refs(refs, available, label):
    if len(refs) != len(set(refs)) or not set(refs) <= set(available):
        raise ValueError(f'Invalid {label} references')

def normalized_trace(trace, identities):
    rows = copy.deepcopy(trace)
    for row in rows:
        for key in ('invocation_ref', 'owner_invocation_ref'):
            if key in row:
                if row[key] not in identities:
                    raise ValueError('Dangling expression execution reference')
                row[key] = identities[row[key]]
    return rows

def validate_result_set(document, assessments):
    """Structural + source-aware cross-reference/scheduling checks, offline."""
    validate_schema('assessment-result-set.schema.json', document)
    _check_redaction(document)
    results = [row['assessment_result'] for row in document['assessment_results']]
    by_execution = {}
    by_assessment = {}
    for result in results:
        execution = result['execution_id']; identity = result['assessment']['id']
        if execution in by_execution or identity in by_assessment:
            raise ValueError('Duplicate execution/Assessment within this single-context result set')
        source = assessments.get(identity)
        if source is not None: validate_schema('assessment.schema.json', {'assessment':source})
        if source is None or result['assessment']['version'] != source['version']:
            raise ValueError('Assessment source identity/version mismatch')
        for name in ('mode', 'purpose', 'class'):
            if result[name] != source[name]:
                raise ValueError(f'Assessment {name} mismatch')
        if result['target_ref'] != document['target_ref']:
            raise ValueError('Cross-target result reference')
        invocation = result['expression_execution']
        if invocation['invocation_ref'] != execution or invocation['assessment'] != identity or invocation['outcome'] != result['outcome']:
            raise ValueError('Expression/Assessment execution mismatch')
        by_execution[execution] = result; by_assessment[identity] = result
    entry = by_execution.get(document['entry_execution_id'])
    if entry is None:
        raise ValueError('Missing entry execution')
    ids = {execution: row['assessment']['id'] for execution, row in by_execution.items()}
    for result in results:
        source = assessments[result['assessment']['id']]
        tests = index(result['tests'], 'Test'); objects = index(result['objects'], 'Object')
        items = index(result['items'], 'Item'); variables = index(result['variables'], 'Variable')
        invocation = result['expression_execution']
        if set(invocation['executed_tests']) != set(tests):
            raise ValueError('Executed Tests differ from recorded Test results')
        if not set(tests) <= set(source.get('tests', {})) or not set(objects) <= set(source.get('objects', {})) or not set(variables) <= set(source.get('variables', {})):
            raise ValueError('Unknown source Test/Object/Variable')
        for item in items.values():
            item_validator(item['capability']).validate(item)
            errors = context_errors(item)
            if errors: raise ValueError('; '.join(errors))
            target = item['provenance'].get('target_ref')
            if target != document['target_ref']:
                raise ValueError('Item target provenance mismatch')
        validate_materialization(result)
        for variable in variables.values():
            check_refs(variable['item_refs'],items,'Variable/Item')
        for obj in objects.values():
            if obj['capability'] != source['objects'][obj['id']]['capability']:
                raise ValueError('Object capability mismatch')
            check_refs(obj['item_refs'], items, 'Object/Item')
            if any(items[i]['capability'] != obj['capability'] for i in obj['item_refs']):
                raise ValueError('Object/Item capability mismatch')
        for test in tests.values():
            check_refs(test['object_refs'], objects, 'Test/Object')
            check_refs(test['item_refs'], items, 'Test/Item')
            check_refs(test['state_refs'], source.get('states', {}), 'Test/State')
            authored = source['tests'][test['id']]
            if test['object_refs'] and not set(test['item_refs']) <= set().union(*(set(objects[ref]['item_refs']) for ref in test['object_refs'])):
                raise ValueError('Test Items outside referenced Object collection')
            if set(test['object_refs']) != ({authored['object']} if 'object' in authored else set()):
                raise ValueError('Test source Object binding mismatch')
            if set(test['state_refs']) != set(authored.get('states', [])):
                raise ValueError('Test source State binding mismatch')
            if 'variable' in authored and authored['variable'] not in variables:
                raise ValueError('Test source Variable result missing')
            for per_item in test['per_item_results']:
                if per_item['item_ref'] not in test['item_refs']:
                    raise ValueError('Per-Item result outside Test Items')
                for state in per_item['state_results']:
                    if state['state_ref'] not in test['state_refs']:
                        raise ValueError('Per-Item State outside Test States')
                    for entity in state['entity_results']:
                        check_refs(entity.get('variable_refs', []), variables, 'Entity/Variable')
            if authored['capability'] != 'variable.value' and any(items[i]['capability'] != authored['capability'] for i in test['item_refs']):
                raise ValueError('Test/Item capability mismatch')
        for test in tests.values():
            for item_ref in test['item_refs']:
                uses = [u for u in result['field_uses'] if u['test_ref']==test['id'] and u['item_ref']==item_ref]
                if not uses: raise ValueError('Test/Item association lacks field-use lineage')
                used = set().union(*(set(u['used_elements']) for u in uses))
                entities = {e['entity'] for per in test['per_item_results'] if per['item_ref']==item_ref
                            for st in per['state_results'] for e in st['entity_results']}
                if not entities <= used: raise ValueError('Compared entities absent from field-use lineage')
        for use in result['field_uses']:
            if use['test_ref'] not in tests or use['item_ref'] not in items:
                raise ValueError('Field-use reference outside executed local results')
            if use['relationship'] == 'direct' and use['item_ref'] not in tests[use['test_ref']]['item_refs']:
                raise ValueError('Direct field use outside Test Items')
        projection = project_items(source, result['items'], result['field_uses'], source_execution_ref=result['execution_id'],
                                   source_completeness={key: result[key] for key in ('logical_complete','population_complete','evidence_complete')})['item_report']
        if 'item_report' in result and result['item_report'] != projection:
            raise ValueError('Item report differs from canonical Items/actual field uses')
        dependencies = result.get('dependent_assessments', [])
        for dep in dependencies:
            target = by_execution.get(dep['execution_id'])
            declared = source.get('dependencies', {}).get(dep['alias'])
            if target is None or declared is None or declared['expected_id'] != target['assessment']['id'] or declared['expected_version'] != target['assessment']['version']:
                raise ValueError('Dependency execution binding mismatch')
            if dep['assessment'] != target['assessment'] or dep['outcome'] != target['outcome'] or dep['purpose'] != target['purpose']:
                raise ValueError('Dependency result identity/outcome mismatch')
        trace_deps = [(t['alias'],t['invocation_ref'],t['outcome'],t['reused']) for t in invocation['trace'] if t['kind']=='dependency']
        result_deps = [(d['alias'],d['execution_id'],d['outcome'],d['reused']) for d in dependencies]
        if trace_deps != result_deps:
            raise ValueError('Dependency trace/result linkage differs')
    def provider(identity, test, _):
        results = by_assessment.get(identity)
        if results is None: raise ValueError('Missing invoked Assessment')
        tests = {row['id']: row for row in results['tests']}
        if test not in tests: raise ValueError('Missing executed Test')
        if any(d['test'] == f'{identity}:{test}' for d in results['expression_execution']['diagnostics']):
            if tests[test]['outcome'] != 'error': raise ValueError('Missing-result diagnostic requires error')
            return None
        return tests[test]['outcome']
    def manual(identity, _):
        row = by_assessment.get(identity)
        if row is None: raise ValueError('Missing manual invocation')
        response = row.get('manual_response')
        if (response is not None and response.get('outcome') != row['outcome']) or (response is None and row['outcome'] != 'not_evaluated'):
            raise ValueError('Manual response/outcome mismatch')
        return row['outcome']
    replay = AssessmentExpressionEvaluator(assessments).run(entry['assessment']['id'], provider, target=document['target_ref'], evaluate_manual=manual)
    expected = {row['assessment']: row for row in replay['invocations']}
    replay_ids = {row['invocation_ref']: row['assessment'] for row in replay['invocations']}
    if set(expected) != set(by_assessment): raise ValueError('Extra/missing invocation outside executed closure')
    for identity, result in by_assessment.items():
        actual = result['expression_execution']; want = expected[identity]
        if actual['outcome'] != want['outcome'] or actual['executed_tests'] != want['executed_tests'] or actual['diagnostics'] != want['diagnostics']:
            raise ValueError('Expression replay differs from invocation result')
        if normalized_trace(actual['trace'], ids) != normalized_trace(want['trace'], replay_ids):
            raise ValueError('Expression replay differs from recorded scheduling')
    return document

def assemble_result_set(assessments, expression, observations, *, include_reports=True, item_scope='all'):
    """Observations are per-invocation evidence, supplied by a trusted producer.

    This evaluator supports one target and one shared binding context per run.
    Repeated contexts must use separate result sets/executions. No raw binding
    values are inferred from expression scheduling records.
    """
    validate_schema('expression-result.schema.json', expression)
    by_id = {row['assessment']:row for row in expression['invocations']}
    if len(by_id) != len(expression['invocations']): raise ValueError('Duplicate invocation ledger identity')
    entry = next((row for row in by_id.values() if row['invocation_ref']==expression['context']['invocation_ref']),None)
    if entry is None or entry['outcome'] != expression['outcome']: raise ValueError('Entry expression/ledger mismatch')
    references = {row['invocation_ref']:row['assessment'] for row in by_id.values()}
    if len(references)!=len(by_id): raise ValueError('Duplicate invocation execution reference')
    normalized_trace(expression['trace'],references)
    for row in by_id.values():
        own = [t for t in expression['trace'] if t['owner_invocation_ref']==row['invocation_ref']]
        if own != row['trace']: raise ValueError('Global trace/invocation ledger mismatch')
    if set(expression['executed_tests']) != {f'{identity}:{test}' for identity,row in by_id.items() for test in row['executed_tests']}:
        raise ValueError('Global Test ledger mismatch')
    if sorted(expression['diagnostics'],key=lambda d:d['test']) != sorted([d for row in by_id.values() for d in row['diagnostics']],key=lambda d:d['test']):
        raise ValueError('Global diagnostic ledger mismatch')
    if set(observations) != set(by_id): raise ValueError('Observations must match the executed invocation closure')
    results = []
    for identity, invocation in by_id.items():
        source = assessments[identity]; evidence = materialize_observations(observations[identity],scope=item_scope)
        if set(evidence) - {'tests','objects','items','variables','diagnostics','field_uses','logical_complete','population_complete','evidence_complete','manual_response','input_bindings','binding_set_id','consumed_organizational_inputs','evidence','evidence_summary','reason','item_materialization'}:
            raise ValueError('Unexpected observation attributes')
        row = dict(evidence, result_schema_version='0.2.0', execution_id=invocation['invocation_ref'],
                   assessment={'id':identity,'version':source['version']}, purpose=source['purpose'],
                   **{'class':source['class']}, mode=source['mode'], outcome=invocation['outcome'],
                   target_ref=expression['context']['target'], expression_execution=copy.deepcopy(invocation), dependent_assessments=[])
        for trace in invocation['trace']:
            if trace['kind'] == 'dependency':
                target = assessments[trace['assessment']]
                row['dependent_assessments'].append({'alias':trace['alias'],'assessment':{'id':target['id'],'version':target['version']},
                    'execution_id':trace['invocation_ref'],'outcome':trace['outcome'],'purpose':target['purpose'],'reused':trace['reused']})
        if include_reports:
            row['item_report'] = project_items(source,row['items'],row['field_uses'],source_execution_ref=row['execution_id'],
                source_completeness={key:row[key] for key in ('logical_complete','population_complete','evidence_complete')})['item_report']
        results.append({'assessment_result':row})
    document = {'entry_execution_id':expression['context']['invocation_ref'],'target_ref':expression['context']['target'],'assessment_results':results}
    return validate_result_set(document, assessments)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assessments',type=Path,required=True)
    parser.add_argument('--result-set',type=Path,required=True)
    args=parser.parse_args()
    validate_result_set(json.loads(args.result_set.read_text()),load_assessments(args.assessments))
    print('Draft result structure, references and expression scheduling verified; target truth not verified')

if __name__=='__main__': main()
