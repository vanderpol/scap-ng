"""Independent YAML acquisition and record identity terms; no renderer imports.

The approved mapping drops OVAL's lowercase/caret transport encoding. Decode
that source contract separately; native record keys already have YAML identity.
YAML Path text stays opaque here: matching terms do not claim probe execution.
"""
from copy import deepcopy
import re

from v04_source_package_semantics import OD, META, keys, local, need
from v04_scalar_source_proof import source_traversal, FILE_BEHAVIORS

CAP = 'independent.yamlfilecontent'
NAMES = {'filepath': 'full_path', 'path': 'directory', 'filename': 'name',
         'content': 'content', 'yamlpath': 'yamlpath', 'value': 'value'}


def original_key(name):
    need(name and not re.search('[A-Z]', name), 'invalid original YAML record key')
    decoded = re.sub(r'\^(\^|[a-z])', lambda m: m[1].upper(), name)
    encoded = ''.join('^^' if c == '^' else '^' + c.lower() if 'A' <= c <= 'Z' else c
                      for c in decoded)
    need(encoded == name, 'unproved original YAML key escape')
    return decoded


def source_state(reader, identifier):
    node = reader.get(identifier, 'states')
    keys(node, META | {'operator'}, 'YAML State')
    need(all(c.tag == '{' + OD + '#independent}' + local(c) and local(c) in NAMES
             for c in node), 'unknown original YAML State field')
    # Copy for transport-key decoding; source nodes and dependency identities
    # remain unchanged. Entity typing/matching is read by the shared proof API.
    copied = deepcopy(node)
    for entity in copied:
        if local(entity) == 'value':
            need(entity.get('datatype') == 'record', 'YAML value requires original record datatype')
            for field in entity:
                need(field.tag == '{' + OD + '}field', 'foreign YAML record field')
                field.set('name', original_key(field.get('name')))
    terms = [{'field': NAMES[local(c)], 'predicate': reader.entity(c)} for c in copied]
    op = node.get('operator', 'AND').lower()
    need(op in ('and', 'or', 'one', 'xor') and terms, 'YAML State operator/fields')
    return terms[0] if len(terms) == 1 and op in ('and', 'or') else {op: terms}


def source_object(reader, identifier):
    node = reader.get(identifier, 'objects')
    keys(node, META, 'YAML Object')
    need(identifier not in reader.active, 'cyclic YAML Object')
    reader.active.add(identifier)
    try:
        sets = node.findall('{' + OD + '}set')
        if sets:
            need(len(node) == 1, 'YAML Set mixed with selectors')
            return {'capability': CAP, 'set': reader.set_term(sets[0], CAP)}
        fields, behaviors, filters = {}, None, []
        for child in node:
            name = local(child)
            if child.tag == '{' + OD + '}filter':
                filters.append(child)
            elif child.tag == '{' + OD + '#independent}behaviors':
                need(behaviors is None and not len(child) and not (child.text or '').strip(),
                     'duplicate/nonempty YAML behaviors')
                keys(child, FILE_BEHAVIORS, 'YAML file behaviors')
                behaviors = child
            else:
                need(child.tag == '{' + OD + '#independent}' + name and name in NAMES and
                     name != 'value' and NAMES[name] not in fields, 'unknown/duplicate YAML selector')
                fields[NAMES[name]] = reader.entity(child, selector=True)
        need(set(fields) in ({'full_path', 'yamlpath'}, {'directory', 'name', 'yamlpath'},
                             {'content', 'yamlpath'}), 'YAML acquisition alternative')
        need(all(fields[k]['operation'] == 'equals' for k in ('content', 'yamlpath') if k in fields),
             'YAML input/query requires equality')
        if 'content' in fields:
            need(behaviors is None, 'unproved inline YAML file behaviors')
        else:
            attrs = {} if behaviors is None else behaviors.attrib
            need('full_path' not in fields or not set(attrs) & {'max_depth', 'recurse_direction'},
                 'invalid original YAML filepath recursion attributes')
            selector = fields.get('full_path', fields.get('directory'))
            need(attrs.get('recurse_file_system') != 'defined' or selector['operation'] == 'equals',
                 'invalid original YAML filesystem/pattern selection')
            fields.update(source_traversal(behaviors, fields, 'file_traversal'))
        result = {'capability': CAP, 'selectors': fields}
        if filters:
            result['filters'] = reader.filters(filters, CAP)
        return result
    finally:
        reader.active.remove(identifier)


def native_object(reader, node):
    allowed = {'full_path', 'directory', 'name', 'content', 'yamlpath', 'filesystem', 'traversal'}
    keys(node, allowed | {'capability', 'object_title', 'filters'}, 'native YAML Object')
    selectors = set(node) & {'full_path', 'directory', 'name', 'content', 'yamlpath'}
    need(selectors in ({'full_path', 'yamlpath'}, {'directory', 'name', 'yamlpath'},
                       {'content', 'yamlpath'}), 'native YAML acquisition alternative')
    fields = {k: reader.predicate(node[k], selector=True) for k in selectors}
    need(all(fields[k]['operation'] == 'equals' for k in ('content', 'yamlpath') if k in fields),
         'native YAML input/query equality')
    if 'content' in fields:
        need(not set(node) & {'filesystem', 'traversal'}, 'native inline YAML file behaviors')
    else:
        need(node.get('filesystem') in ('all', 'local', 'same'), 'native YAML filesystem scope')
        fields['filesystem'] = node['filesystem']
        if 'traversal' in node:
            need('directory' in fields and fields['directory']['operation'] == 'equals',
                 'native YAML traversal selector')
            keys(node['traversal'], {'max_depth', 'recurse'}, 'native YAML traversal')
            fields['traversal'] = {**node['traversal'], 'direction': 'down'}
    result = {'capability': CAP, 'selectors': fields}
    if node.get('filters'):
        result['filters'] = reader.filters(node['filters'])
    return result
