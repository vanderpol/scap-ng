"""Independent scalar collection terms from pinned approved identity contracts.

No converter imports or lowering calls. Frozen field identities are approved
crosswalk data, not live converter metadata. A mapping edit requires explicit
proof-contract review; input/output graph structure and operands are read
independently. Complex behaviors and unknown payloads fail closed.
"""
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from v04_source_package_semantics import Source, META, OD, local, keys, need

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = json.loads((ROOT / 'tests/fixtures/v04-scalar-proof-contracts.json').read_text())['capabilities']


@lru_cache(maxsize=None)
def contract(capability):
    record = CONTRACTS.get(capability)
    if record is not None:
        path = ROOT / 'schema/v0.4.0/capability-mappings/supported' / (capability + '.json')
        need(sha256(path.read_bytes()).hexdigest() == record['mapping_sha256'],
             'unreviewed scalar proof mapping: ' + capability)
    return record


def source_capability(node, suffix):
    kind = suffix.lstrip('_')
    for capability, record in CONTRACTS.items():
        if node.tag == '{' + record['source']['namespace'] + '}' + record['source'].get(kind, ''):
            contract(capability)
            return capability
    return None


def source_object(reader, identifier, capability):
    record = contract(capability)
    if record is None:
        return None
    node = reader.get(identifier, 'objects')
    if node.findall('{' + OD + '}set') and record['source_kind'] == 'object':
        return None  # Existing independent Set reader owns recursion/ordering.
    need(identifier not in reader.active, 'cyclic scalar Object')
    reader.active.add(identifier)
    try:
        return source_leaf(reader, identifier, capability, record)
    finally:
        reader.active.remove(identifier)


def source_leaf(reader, identifier, capability, record):
    node = reader.get(identifier, 'objects')
    keys(node, META, 'scalar source Object')
    if record['source_kind'] == 'none':
        need(not len(node), 'system source Object must be empty')
        return {'capability': capability, 'selectors': {}}
    fields, filters, behaviors = {}, [], None
    for child in node:
        if child.tag == '{' + OD + '}filter':
            filters.append(child)
            continue
        if child.tag == '{' + record['source']['namespace'] + '}behaviors':
            need(record.get('behaviors') and behaviors is None and not len(child) and
                 not (child.text or '').strip(), 'unsupported/duplicate scalar behaviors')
            keys(child, record['behaviors'], 'original scalar behaviors')
            behaviors = child
            continue
        name = local(child)
        need(child.tag == '{' + record['source']['namespace'] + '}' + name
             and name in record['selectors'] and name not in fields, 'unknown scalar source acquisition field')
        fields[name] = reader.entity(child, selector=True)
    result = {'capability': capability, 'selectors': {record['selectors'][k]: v for k, v in fields.items()}}
    for name, specification in record.get('behaviors', {}).items():
        value = behaviors.get(name) if behaviors is not None else None
        if value is None:
            value = specification['default']
        else:
            need(specification['type'] == 'boolean' and value in ('false', 'true', '0', '1'),
                 'invalid original scalar Boolean behavior')
            value = value in ('true', '1')
        result['selectors'][specification['field']] = value
    if filters:
        result['filters'] = reader.filters(filters, capability)
    return result


def source_state(reader, identifier, capability):
    record = contract(capability)
    if record is None:
        return None
    node = reader.get(identifier, 'states')
    need(all(c.tag == '{' + record['source']['namespace'] + '}' + local(c)
             and local(c) in record['fields'] for c in node), 'unknown scalar source State field')
    result = Source.state(reader, identifier, capability)
    def rename(value):
        if isinstance(value, dict):
            return {k: record['fields'][v] if k == 'field' else rename(v) for k, v in value.items()}
        if isinstance(value, list):
            return [rename(v) for v in value]
        return value
    return rename(result)


def native_object(reader, node, capability):
    record = contract(capability)
    if record is None or isinstance(node, str):
        return None
    need(record['source_kind'] == 'object', 'system native capability has no Object')
    if 'set' in node:
        keys(node, {'capability', 'object_title', 'set'}, 'native scalar Set')
        return {'capability': capability, 'set': reader.set_term(node['set'], capability)}
    allowed = set(record['selectors'].values())
    behaviors = {s['field']: s for s in record.get('behaviors', {}).values()}
    keys(node, allowed | behaviors.keys() | {'capability', 'object_title', 'filters'}, 'native scalar Object')
    result = {'capability': capability, 'selectors': {
        key: reader.predicate(value, selector=True) for key, value in node.items() if key in allowed}}
    for name, specification in behaviors.items():
        need(name in node and specification['type'] == 'boolean' and isinstance(node[name], bool),
             'missing/invalid native scalar behavior')
        result['selectors'][name] = node[name]
    if node.get('filters'):
        result['filters'] = reader.filters(node['filters'])
    return result


def no_object(capability):
    record = contract(capability)
    return record is not None and record['source_kind'] == 'none'
