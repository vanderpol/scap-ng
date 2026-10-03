#!/usr/bin/env python3
"""Draft local Item materialization and verified observation-copy imports.

Collection-cache authorization, freshness and resource acquisition belong to the
producer. Importing observations never imports a Test's truth or re-resolves names.
"""
import copy
import hashlib
import json
import re
from reported_elements import _check_redaction


def materialize_observations(observations, *, scope='all'):
    if 'item_materialization' in observations:
        raise ValueError('Provide original available observations, not an already-materialized result')
    if scope not in {'all','consumed'}:
        raise ValueError('Item scope must be all or consumed')
    _check_redaction(observations)
    result=copy.deepcopy(observations)
    available={}
    for item in result['items']:
        if item['id'] in available: raise ValueError('Duplicate available Item identity')
        from assessment_results_v02 import item_validator
        from collected_item_contract_v02 import context_errors
        item_validator(item['capability']).validate(item)
        if context_errors(item): raise ValueError('Invalid available Item context')
        available[item['id']]=item
    consumed=set()
    for test in result['tests']:
        consumed.update(test['item_refs'])
        consumed.update(row['item_ref'] for row in test.get('per_item_results',[]))
    for variable in result['variables']:
        consumed.update(variable.get('item_refs',[]))
    consumed.update(row['item_ref'] for row in result['field_uses'])
    if not consumed <= available.keys():
        raise ValueError('Consumed Item is not locally available')
    kept=set(available) if scope=='all' else consumed
    collections=[]
    seen=set()
    for obj in result['objects']:
        if obj['id'] in seen: raise ValueError('Duplicate Object result identity')
        seen.add(obj['id']); refs=obj['item_refs']
        if len(refs)!=len(set(refs)) or not set(refs)<=available.keys():
            raise ValueError('Collection references unavailable/duplicate Items')
        obj['item_refs']=[ref for ref in refs if ref in kept]
        collections.append({'object_ref':obj['id'],'available_count':len(refs),'included_count':len(obj['item_refs']),
                            'omitted_count':len(refs)-len(obj['item_refs'])})
    result['items']=[item for item in result['items'] if item['id'] in kept]
    for flag in ('population_complete','evidence_complete'):
        if any(item.get('context',{}).get('origin',{}).get('source_completeness',{}).get(flag) is False for item in result['items']):
            result[flag]=False
    result['item_materialization']={'scope':scope,'available_count':len(available),'included_count':len(kept),
                                    'omitted_count':len(available)-len(kept),'consumed_item_refs':sorted(consumed),
                                    'collections':collections}
    return result


def validate_materialization(result):
    for item in result['items']:
        origin=item.get('context',{}).get('origin',{})
        if 'source_digest' in origin:
            if not item.get('imported') or origin['source_execution_ref']!=origin['result_ref']:
                raise ValueError('Pinned origin must identify an imported source execution')
            if result.get('binding_set_id')!=origin['binding_set_id']:
                raise ValueError('Imported Item binding context differs from consumer')
            for flag in ('population_complete','evidence_complete'):
                if origin['source_completeness'][flag] is False and result[flag] is True:
                    raise ValueError('Imported incompleteness was lost')
    metadata=result.get('item_materialization')
    if metadata is None: return
    items={item['id'] for item in result['items']}
    if metadata['included_count']!=len(items) or metadata['available_count']!=metadata['included_count']+metadata['omitted_count']:
        raise ValueError('Invalid Item materialization counts')
    consumed=set()
    for test in result['tests']:
        consumed.update(test['item_refs']);consumed.update(row['item_ref'] for row in test.get('per_item_results',[]))
    for variable in result['variables']: consumed.update(variable.get('item_refs',[]))
    consumed.update(row['item_ref'] for row in result['field_uses'])
    if set(metadata['consumed_item_refs'])!=consumed or not consumed<=items:
        raise ValueError('Invalid consumed Item materialization')
    if metadata['scope']=='consumed' and items!=consumed:
        raise ValueError('Consumed scope includes unused Items')
    if metadata['scope']=='all' and metadata['omitted_count']:
        raise ValueError('All scope cannot omit available Items')
    collections={row['object_ref']:row for row in metadata['collections']}
    if len(collections)!=len(metadata['collections']) or set(collections)!={obj['id'] for obj in result['objects']}:
        raise ValueError('Invalid collection materialization identities')
    for obj in result['objects']:
        row=collections[obj['id']]
        if row['included_count']!=len(obj['item_refs']) or row['available_count']!=row['included_count']+row['omitted_count']:
            raise ValueError('Invalid collection materialization counts')
        if row['available_count']>metadata['available_count'] or row['omitted_count']>metadata['omitted_count']:
            raise ValueError('Collection counts exceed available/omitted Items')
        if metadata['scope']=='all' and row['omitted_count']:
            raise ValueError('All scope cannot omit collection Items')


def _unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError('Duplicate JSON object member in imported source')
        result[key]=value
    return result


def import_items(source_bytes, *, expected_digest, expected_execution_id, target_ref, binding_set_id,
                 item_refs, local_ids):
    """Verify exact UTF-8 JSON artifact bytes and copy selected Items locally.

    expected_digest is an independently trusted sha256:<hex> pin. It is integrity
    evidence, not a signature, reuse authorization or proof of target truth.
    local_ids explicitly maps original Item identities to caller-chosen local IDs.
    """
    if not isinstance(source_bytes,bytes): raise ValueError('Exact source artifact bytes required')
    digest='sha256:'+hashlib.sha256(source_bytes).hexdigest()
    if not isinstance(expected_digest,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',expected_digest) or digest!=expected_digest:
        raise ValueError('Source artifact digest mismatch')
    source=json.loads(source_bytes.decode('utf-8'),object_pairs_hook=_unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite JSON number')))
    from assessment_results_v02 import validate_schema,item_validator
    validate_schema('assessment-result.schema.json',source)
    _check_redaction(source)
    result=source['assessment_result']
    if result['execution_id']!=expected_execution_id or result['target_ref']!=target_ref:
        raise ValueError('Import execution/target mismatch')
    if not isinstance(binding_set_id,str) or not binding_set_id or result.get('binding_set_id')!=binding_set_id:
        raise ValueError('Import binding context mismatch')
    if len(item_refs)!=len(set(item_refs)) or set(local_ids)!=set(item_refs) or len(set(local_ids.values()))!=len(local_ids):
        raise ValueError('Explicit unique source/local Item mapping required')
    if any(not isinstance(value,str) or not value for value in local_ids.values()):
        raise ValueError('Nonempty local Item identities required')
    available={}
    for item in result['items']:
        if item['id'] in available: raise ValueError('Duplicate source Item identity')
        item_validator(item['capability']).validate(item)
        from collected_item_contract_v02 import context_errors
        if context_errors(item) or item['provenance'].get('target_ref')!=target_ref:
            raise ValueError('Invalid source Item context/target')
        available[item['id']]=item
    validate_materialization(result)
    if not set(item_refs)<=available.keys(): raise ValueError('Imported Item is not materialized in source artifact')
    copied=[]
    for ref in item_refs:
        original=available[ref];item_validator(original['capability']).validate(original)
        from collected_item_contract_v02 import context_errors
        if context_errors(original): raise ValueError('Invalid source Item context')
        if original['provenance'].get('target_ref')!=target_ref: raise ValueError('Source Item target mismatch')
        item=copy.deepcopy(original);item['id']=local_ids[ref];item['imported']=True
        context=item.setdefault('context',{})
        if 'origin' in context:
            context.setdefault('import_history',[]).append(context['origin'])
        context['origin']={'result_ref':expected_execution_id,'item_ref':ref,'source_execution_ref':expected_execution_id,
                           'source_digest':digest,'binding_set_id':binding_set_id,
                           'source_completeness':{key:result[key] for key in ('logical_complete','population_complete','evidence_complete')}}
        copied.append(item)
    return copied
