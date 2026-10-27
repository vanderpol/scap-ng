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

from v04_source_package_semantics import Source, META, OD, local, keys, need, source_hierarchy, native_hierarchy

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = json.loads((ROOT / 'tests/fixtures/v04-scalar-proof-contracts.json').read_text())['capabilities']
FILE_BEHAVIORS = {'max_depth', 'recurse', 'recurse_direction', 'recurse_file_system'}


def source_alias(predicate, aliases):
    if not aliases:
        return predicate
    operand = predicate.get('operand', {})
    need(predicate.get('operation') in ('equals', 'not_equal'), 'unproved alias-domain comparison')
    if predicate['operation'] == 'not_equal':
        need(len(set(aliases.values())) == len(aliases), 'unproved non-bijective enum inequality')
    def projected(term):
        # This independent term already retains Object acquisition, filters,
        # graph dependencies and local/unique boundaries. Only a projection of
        # the SAME frozen alias domain can commute with its bijective rename.
        if 'local' in term:
            need(term['local'].get('datatype') == 'string', 'unproved enum Variable datatype')
            return {'local': {**term['local'], 'expression': projected(term['local']['expression'])}}
        if 'unique' in term:
            return {'unique': projected(term['unique'])}
        value = term.get('values', {})
        obj = value.get('object', {})
        record = contract(obj.get('capability'))
        need(record is not None, 'unproved enum Variable collection')
        source_fields = [k for k, v in record['fields'].items() if v == value.get('field')]
        need(len(source_fields) == 1 and record.get('field_aliases', {}).get(source_fields[0]) == aliases,
             'unproved enum Variable domain')
        need(value.get('source_alias_domain') == aliases, 'unproved enum Variable source vocabulary')
        return {'values': {k: v for k, v in value.items() if k != 'source_alias_domain'}}
    if 'local' in operand:
        need(len(set(aliases.values())) == len(aliases), 'unproved non-bijective enum Variable domain')
        return {**predicate, 'operand': projected(operand)}
    def rename(value):
        need(value.get('datatype') == 'string' and value.get('value') in aliases,
             'unproved alias-domain comparison or Variable')
        return {**value, 'value': aliases[value['value']]}
    renamed = ({'constant_values': [rename(v) for v in operand['constant_values']]}
               if 'constant_values' in operand else rename(operand))
    return {**predicate, 'operand': renamed}


def source_traversal(behaviors, fields, kind):
    """Read original FileBehaviors independently of production lowering."""
    values = {} if behaviors is None else behaviors.attrib
    direction = values.get('recurse_direction', 'none')
    need(direction in ('none', 'down'), 'unproved/deprecated file recursion direction')
    depth = int(values.get('max_depth', '-1'))
    need(depth >= -1, 'invalid original max_depth')
    windows = kind == 'windows_file_traversal'
    options = ({'directories': 'directories', 'junctions': 'junctions',
                'junctions and directories': 'junctions_and_directories'} if windows else
               {'directories': 'directories', 'symlinks': 'symlinks',
                'symlinks and directories': 'symlinks_and_directories'})
    recurse = values.get('recurse', 'directories' if windows else 'symlinks and directories')
    need(recurse in options, 'unproved/deprecated file recursion option')
    scope = values.get('recurse_file_system', 'all')
    need(scope in ('all', 'local', 'defined'), 'invalid original filesystem scope')
    result = {'filesystem': {'all': 'all', 'local': 'local', 'defined': 'same'}[scope]}
    directory = fields.get('directory')
    if direction == 'down' and 'full_path' not in fields and isinstance(directory, dict) and directory.get('operation') == 'equals':
        result['traversal'] = {'max_depth': None if depth == -1 else depth,
                               'recurse': options[recurse], 'direction': 'down'}
    return result


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
            need((record.get('behaviors') or record.get('traversal')) and behaviors is None and not len(child) and
                 not (child.text or '').strip(), 'unsupported/duplicate scalar behaviors')
            traversal_fields = ({'max_depth', 'recurse_direction'} if record.get('traversal') == 'hierarchy_traversal'
                                else FILE_BEHAVIORS if record.get('traversal') else set())
            keys(child, set(record.get('behaviors', {})) | traversal_fields,
                 'original scalar behaviors')
            behaviors = child
            continue
        name = local(child)
        need(child.tag == '{' + record['source']['namespace'] + '}' + name
             and name in record['selectors'] and name not in fields, 'unknown scalar source acquisition field')
        nil = '{http://www.w3.org/2001/XMLSchema-instance}nil'
        if nil in child.attrib:
            keys(child, {nil, 'datatype'}, 'nil scalar selector')
            need(name in record.get('nullable_selectors', []) and child.get(nil) in ('true', '1') and
                 not len(child) and not (child.text or '').strip() and child.get('datatype', 'string') == 'string',
                 'unproved nil scalar selector')
            fields[name] = None
        else:
            fields[name] = source_alias(reader.entity(child, selector=True), record.get('selector_aliases', {}).get(name))
    result = {'capability': capability, 'selectors': {record['selectors'][k]: v for k, v in fields.items()}}
    if record.get('traversal') == 'hierarchy_traversal':
        result['selectors'].update(source_hierarchy(behaviors, result['selectors'].get('key')))
    elif record.get('traversal'):
        result['selectors'].update(source_traversal(behaviors, result['selectors'], record['traversal']))
    for name, specification in record.get('behaviors', {}).items():
        value = behaviors.get(name) if behaviors is not None else None
        if value is None:
            value = specification['default']
        else:
            if specification['type'] == 'boolean':
                need(value in ('false', 'true', '0', '1'), 'invalid original scalar Boolean behavior')
                value = value in ('true', '1')
            else:
                need(specification['type'] == 'string' and isinstance(value, str), 'unproved scalar behavior type')
        need('enum' not in specification or value in specification['enum'], 'unproved original scalar behavior value')
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
            if 'field' in value:
                return {**value, 'field': record['fields'][value['field']],
                        'predicate': source_alias(value['predicate'], record.get('field_aliases', {}).get(value['field']))}
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
    traversal = ({'traversal'} if record.get('traversal') == 'hierarchy_traversal' else
                 {'filesystem', 'traversal'} if record.get('traversal') else set())
    keys(node, allowed | behaviors.keys() | traversal | {'capability', 'object_title', 'filters'}, 'native scalar Object')
    result = {'capability': capability, 'selectors': {
        key: None if value is None else reader.predicate(value, selector=True)
        for key, value in node.items() if key in allowed}}
    if record.get('traversal') == 'hierarchy_traversal':
        if 'traversal' in node:
            result['selectors']['traversal'] = native_hierarchy(node['traversal'])
    elif record.get('traversal'):
        need(node.get('filesystem') in ('all', 'local', 'same'), 'missing/invalid native filesystem')
        result['selectors']['filesystem'] = node['filesystem']
        if 'traversal' in node:
            value = node['traversal']
            keys(value, {'max_depth', 'recurse'}, 'native file traversal')
            need(set(value) == {'max_depth', 'recurse'}, 'native traversal requires explicit controls')
            result['selectors']['traversal'] = {**value, 'direction': 'down'}
    for name, specification in behaviors.items():
        need(name in node and isinstance(node[name], bool if specification['type'] == 'boolean' else str),
             'missing/invalid native scalar behavior')
        need('enum' not in specification or node[name] in specification['enum'], 'unproved native scalar behavior value')
        result['selectors'][name] = node[name]
    if node.get('filters'):
        result['filters'] = reader.filters(node['filters'])
    return result


def no_object(capability):
    record = contract(capability)
    return record is not None and record['source_kind'] == 'none'
