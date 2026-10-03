"""Independent, bounded XML projection for the two finite-row source graphs.

This does not import table_expansion or its templates. Defaults below are from
the pinned OVAL 5.12.3 schemas; original explicitness stays in source evidence.
Only scalar constant/concat Variables and the three selected families are
supported. Unfamiliar logic fails instead of receiving guessed semantics.
"""
from itertools import product
from lxml import etree

EXISTENCE = {'all_exist': 'all', 'at_least_one_exists': 'some'}
OPERATION = {'equals': 'equal', 'pattern match': 'match', 'greater than or equal': 'greater_or_equal'}


def local(node):
    return etree.QName(node).localname


def project_xml(path):
    root = etree.parse(str(path)).getroot()
    nodes = {n.get('id'): n for n in root.iter() if n.get('id')}
    active = set()

    def values(n):
        tag = local(n)
        if tag == 'variable_component':
            return values(nodes[n.get('var_ref')])
        if tag in ('value', 'literal_component'):
            return [n.text or '']
        if tag in ('local_variable', 'constant_variable'):
            ident = n.get('id')
            if ident in active:
                raise ValueError('Variable cycle')
            active.add(ident)
            children = [c for c in n if local(c) != 'notes']
            result = [v for c in children for v in values(c)]
            active.remove(ident)
            return result
        if tag == 'concat':
            return [''.join(v) for v in product(*(values(c) for c in n))]
        raise ValueError('unsupported Variable function: ' + tag)

    def entity(n, state=False):
        resolved = values(nodes[n.get('var_ref')]) if n.get('var_ref') else [n.text or '']
        if len(resolved) != 1:
            raise ValueError('finite-table proof requires one resolved value')
        item = {'value': resolved[0], 'operation': OPERATION[n.get('operation', 'equals')],
                'datatype': {'int': 'integer'}.get(n.get('datatype', 'string'), n.get('datatype', 'string'))}
        if state:
            if n.get('entity_check', 'all') != 'all' or n.get('check_existence', 'at_least_one_exists') != 'at_least_one_exists':
                raise ValueError('unsupported State entity semantics')
            item.update(match='all', existence='some')
        return item

    rows = []
    for t in root.find('{*}tests'):
        family = local(t).removesuffix('_test')
        if family not in ('textfilecontent54', 'file', 'symlink'):
            raise ValueError('unsupported Test family')
        cap = ('independent.' if family == 'textfilecontent54' else 'unix.') + family
        o = nodes[t.find('{*}object').get('object_ref')]
        selectors = {}
        for e in o:
            if local(e) == 'behaviors':
                continue
            if local(e) not in ('filepath', 'pattern', 'instance'):
                raise ValueError('unsupported selector')
            selectors['full_path' if local(e) == 'filepath' else local(e)] = entity(e)
        states = []
        for ref in t.findall('{*}state'):
            st = nodes[ref.get('state_ref')]
            if st.get('operator', 'AND') != 'AND':
                raise ValueError('unsupported State operator')
            fields = [e for e in st if local(e) != 'notes']
            if len(fields) != 1:
                raise ValueError('only one-field States are in this projection')
            states.append({'field': local(fields[0]), **entity(fields[0], state=True)})
        row = {'capability': cap, 'select': selectors, 'states': states,
               'existence': EXISTENCE[t.get('check_existence', 'at_least_one_exists')], 'match': t.get('check'),
               'state_operator': t.get('state_operator', 'AND')}
        if family == 'textfilecontent54':
            b = o.find('{*}behaviors')
            attrs = {} if b is None else dict(b.attrib)
            row['filesystem'] = {'all': 'any', 'local': 'local', 'defined': 'same'}[attrs.get('recurse_file_system', 'all')]
            row['collect'] = {k: attrs.get(k, default) in ('true', '1') for k, default in
                              [('ignore_case', 'false'), ('multiline', 'true'), ('singleline', 'false')]}
            row['collect']['item_creation'] = attrs.get('item_creation', 'all_object_elements_fullfilled')
        if row['match'] != 'all' or row['state_operator'] != 'AND':
            raise ValueError('unsupported Test operators')
        rows.append((t.get('id'), row))
    return rows


def project_native(document):
    a = document['assessment']
    rows = []
    for name, t in a['tests'].items():
        o = a['objects'][t['object']]
        select = {}
        for key, val in o['select'].items():
            key = 'full_path' if key == 'filepath' else key
            select[key] = {**val, 'operation': OPERATION.get(val['operation'], val['operation'])}
        states = []
        for ref in t.get('states', []):
            st = a['states'][ref]['state']
            states.append({'field': st['field'], 'value': st['value'],
                           'operation': OPERATION.get(st['operation'], st['operation']), 'datatype': st['datatype'],
                           'match': st.get('match', st.get('entity_check')),
                           'existence': st.get('existence', EXISTENCE.get(st.get('entity_existence')))})
        row = {'capability': t['capability'], 'select': select, 'states': states,
               'existence': t['existence'], 'match': t['match'], 'state_operator': 'AND'}
        if t['capability'] == 'independent.textfilecontent54':
            row.update(filesystem=o['filesystem'], collect=o['collect'])
        rows.append((name, row))
    return rows


def assert_and_tree(document):
    """Only flatten AND for this experiment; refuse negation/other leaf kinds."""
    found = []
    def walk(n):
        if set(n) == {'test'}:
            found.append(n['test'])
        elif set(n) == {'all'} and n['all']:
            for c in n['all']:
                walk(c)
        else:
            raise ValueError('not a pure nonempty AND/Test tree')
    walk(document['assessment']['evaluate'])
    if len(found) != len(set(found)) or set(found) != set(document['assessment']['tests']):
        raise ValueError('tree must cover every Test once')
    return found


def assert_source_and_tree(path, seed):
    root = etree.parse(str(path)).getroot()
    nodes = {n.get('id'): n for n in root.iter() if n.get('id')}
    active, found = set(), []
    def walk(n):
        tag = local(n)
        if n.get('negate', 'false') not in ('false', '0') or n.get('applicability_check', 'false') not in ('false', '0'):
            raise ValueError('negation/applicability is outside finite AND lowering')
        if tag == 'criterion':
            found.append(n.get('test_ref'))
        elif tag == 'extend_definition':
            ident = n.get('definition_ref')
            if ident in active:
                raise ValueError('Definition cycle')
            active.add(ident)
            walk(nodes[ident].find('{*}criteria'))
            active.remove(ident)
        elif tag == 'criteria' and n.get('operator', 'AND') == 'AND' and len(n):
            for c in n:
                walk(c)
        else:
            raise ValueError('unsupported source logical shape')
    active.add(seed)
    walk(nodes[seed].find('{*}criteria'))
    all_tests = {n.get('id') for n in root.find('{*}tests')}
    if len(found) != len(set(found)) or set(found) != all_tests:
        raise ValueError('source tree does not cover each Test exactly once')
    return found
