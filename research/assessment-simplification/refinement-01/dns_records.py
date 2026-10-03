"""Strict decoder + bounded predicate model for a proposed administrative adapter.

No subprocesses or Windows queries execute here. This tests a new collector
contract, not equivalence to the legacy shellcommand/variable_instance graph.
"""
import json
from oval_result_truth_tables import aggregate_operator


def decode(text, *, exit_code=0, timed_out=False, maximum_bytes=1_000_000):
    if timed_out or exit_code != 0 or len(text.encode('utf-8')) > maximum_bytes:
        raise ValueError('transport failure or output budget exceeded')
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError('duplicate JSON property')
            result[k] = v
        return result
    doc = json.loads(text, object_pairs_hook=unique)
    if not isinstance(doc, dict) or set(doc) != {'format', 'snapshot_id', 'inventory', 'zones'} or doc['format'] != 'research.dns-rr.v1':
        raise ValueError('unknown envelope')
    if not isinstance(doc['snapshot_id'], str) or not doc['snapshot_id']:
        raise ValueError('missing snapshot identity')
    inventory = doc['inventory']
    if not isinstance(inventory, dict) or set(inventory) != {'status', 'keys'} or inventory['status'] not in ('complete', 'incomplete', 'error', 'not_collected'):
        raise ValueError('invalid inventory')
    keys = inventory['keys']
    if not isinstance(keys, list) or any(not isinstance(k, str) or not k for k in keys) or len(keys) != len(set(keys)):
        raise ValueError('invalid/duplicate inventory keys')
    if not isinstance(doc['zones'], list):
        raise ValueError('zones must be a list')
    seen = set()
    for z in doc['zones']:
        if not isinstance(z, dict) or set(z) != {'key', 'integrated', 'signed', 'rr'} or not isinstance(z['key'], str) or z['key'] not in keys or z['key'] in seen:
            raise ValueError('unknown or duplicate zone key')
        seen.add(z['key'])
        if type(z['integrated']) is not bool or type(z['signed']) is not bool:
            raise ValueError('zone flags must be observed Booleans')
        if not isinstance(z['rr'], dict) or set(z['rr']) != {'RRSIG', 'DNSKEY', 'NSEC3'}:
            raise ValueError('missing or unexpected RR type')
        for observation in z['rr'].values():
            if not isinstance(observation, dict) or observation.get('status') not in ('complete', 'error', 'not_collected', 'incomplete'):
                raise ValueError('invalid RR status')
            if observation['status'] in ('complete', 'incomplete'):
                if set(observation) != {'status', 'count'} or type(observation['count']) is not int or observation['count'] < 0:
                    raise ValueError('invalid count')
            elif set(observation) != {'status'}:
                raise ValueError('error-like observations cannot pretend to have a count')
    return doc


def evaluate(doc):
    """Explicit stronger per-zone research contract, configuration purpose only.

    Classified-network and platform applicability remain separate Assessments.
    Complete no-zone/all-integrated inventories bypass RR predicates, mirroring
    the source's server-wide exception. No claim about original scope correlation.
    """
    inv = doc['inventory']
    if inv['status'] == 'error':
        return 'error'
    if inv['status'] == 'not_collected':
        return 'unknown'
    complete = inv['status'] == 'complete'
    zones = {z['key']: z for z in doc['zones']}
    if complete and not inv['keys']:
        return 'true'
    if complete and set(zones) == set(inv['keys']) and all(z['integrated'] for z in zones.values()):
        return 'true'
    results = []
    for key in inv['keys']:
        if key not in zones:
            results.append('error' if complete else 'unknown')
            continue
        z = zones[key]
        fields = ['true' if z['signed'] else 'false']
        for obs in z['rr'].values():
            if obs['status'] == 'error':
                fields.append('error')
            elif obs['status'] == 'complete':
                fields.append('true' if obs['count'] > 0 else 'false')
            else:
                fields.append('unknown')
        results.append(aggregate_operator('AND', fields))
    if not complete:
        results.append('unknown')
    return aggregate_operator('AND', results)
