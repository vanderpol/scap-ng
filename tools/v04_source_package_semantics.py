#!/usr/bin/env python3
"""Independent, deliberately bounded OVAL/native semantic-term comparison (#251).

No converter, exporter, compiler or execution engine. Accepted terms preserve
collection/evidence boundaries and quantifiers, not just two-valued outcomes.
Unknown syntax is unsupported, never discarded. This is not a scanner.
"""
from hashlib import sha256
import json
import xml.etree.ElementTree as ET

OD = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'
CAPS = {OD + '#windows}registry': 'windows.registry',
        OD + '#windows}wmi57': 'windows.wmi.query',
        OD + '#independent}shellcommand': 'independent.shellcommand'}
FOUND = {'at_least_one_exists': 'one_or_more', 'none_exist': 'none',
         'only_one_exists': 'exactly_one', 'any_exist': 'may_be_absent'}
FIELD_FOUND = {**FOUND, 'all_exist': 'every'}
CHECK = {'all': 'every', 'at least one': 'one_or_more', 'none satisfy': 'none',
         'only one': 'exactly_one'}
OPS = {'equals': 'equals', 'not equal': 'not_equal', 'pattern match': 'matches_regex',
       'greater than': 'greater_than', 'greater than or equal': 'greater_than_or_equal',
       'less than': 'less_than', 'less than or equal': 'less_than_or_equal',
       'case insensitive equals': 'case_insensitive_equals',
       'case insensitive not equal': 'case_insensitive_not_equal'}
META = {'id', 'version', 'comment'}
REGISTRY_HIVES = frozenset('HKEY_' + name for name in (
    'CLASSES_ROOT', 'CURRENT_CONFIG', 'CURRENT_USER', 'CURRENT_USER_LOCAL_SETTINGS', 'LOCAL_MACHINE', 'USERS'))


class Unsupported(ValueError):
    """No independent proof rule for the indicated source/native construct."""


def need(ok, message):
    if not ok:
        raise Unsupported(message)


def local(n):
    return n.tag.rsplit('}', 1)[-1]


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(',', ':')).encode()).hexdigest()


def xml_term(n):
    """Namespace/attributes/leaf whitespace preserved; ignore indentation only."""
    return [n.tag, sorted(n.attrib.items()), n.text if not len(n) else None,
            [xml_term(c) for c in n]]


def keys(node, allowed, label):
    actual = set(node.attrib) if isinstance(node, ET.Element) else set(node)
    need(actual <= set(allowed), label + ': unsupported keys ' + str(sorted(actual - set(allowed))))


def boolean(op, children):
    need(op in ('and', 'or', 'one', 'xor') and children, 'unsupported/empty Boolean ' + op)
    # Sole AND/OR is an identity for all OVAL result states. Do not apply
    # two-valued tautologies, NOT cancellation, distributivity or short-circuiting.
    if op in ('and', 'or') and len(children) == 1:
        return children[0]
    return {op: children}


def literal(datatype, value):
    if datatype == 'string':
        need(isinstance(value, str), 'string operand type')
    elif datatype in ('int', 'integer'):
        need(not isinstance(value, bool), 'integer operand type')
        value, datatype = int(value), 'integer'
    elif datatype == 'boolean':
        need(value in (True, False, 'true', 'false', '1', '0'), 'boolean operand')
        value = value in (True, 'true', '1')
    else:
        raise Unsupported('datatype proof unavailable: ' + datatype)
    return {'datatype': datatype, 'value': value}


class Source:
    def __init__(self, oval):
        need(oval.tag == '{' + OD + '}oval_definitions', 'not original OVAL')
        self.nodes, self.kind = {}, {}
        for section in oval:
            if local(section) in ('definitions', 'tests', 'objects', 'states', 'variables'):
                need(section.tag == '{' + OD + '}' + local(section), 'foreign OVAL section')
                for n in section:
                    ident = n.get('id')
                    need(ident and ident not in self.nodes, 'duplicate/missing source ID')
                    self.nodes[ident], self.kind[ident] = n, local(section)
        self.used, self.active = set(), set()

    def get(self, ident, kind=None):
        need(ident in self.nodes, 'missing original reference: ' + str(ident))
        need(kind is None or self.kind[ident] == kind, 'original reference kind: ' + ident)
        self.used.add(ident)
        return self.nodes[ident]

    def closure(self, root):
        """All OVAL reference forms, including filters, sets and variable functions.

        This inventory is intentionally broader than the semantic proof subset.
        A missing/cyclic reference prevents proof even in an unsupported family.
        """
        seen, active, edges = set(), set(), []
        ref_kinds = {'test_ref': 'tests', 'definition_ref': 'definitions',
                     'object_ref': 'objects', 'state_ref': 'states', 'var_ref': 'variables'}
        def visit(ident):
            need(ident not in active, 'cyclic original dependency: ' + ident)
            if ident in seen:
                return
            n = self.get(ident)
            active.add(ident)
            for child in n.iter():
                refs = [(v, ref_kinds[k]) for k, v in child.attrib.items() if k in ref_kinds]
                if local(child) in ('filter', 'object_reference'):
                    refs.append(((child.text or '').strip(),
                                 'states' if local(child) == 'filter' else 'objects'))
                if n.tag == '{' + OD + '#independent}variable_object' and child.tag == '{' + OD + '#independent}var_ref':
                    refs.append(((child.text or '').strip(), 'variables'))
                for ref, kind in refs:
                    self.get(ref, kind)
                    edges.append([ident, ref, local(child)])
                    visit(ref)
            active.remove(ident)
            seen.add(ident)
        visit(root)
        return {'nodes': [{'id': i, 'kind': self.kind[i], 'type': self.nodes[i].tag,
                          'version': self.nodes[i].get('version'),
                          'sha256': digest(xml_term(self.nodes[i]))} for i in sorted(seen)],
                'edges': edges}

    def expression(self, definition):
        need(definition not in self.active, 'cyclic Definition')
        self.active.add(definition)
        n = self.get(definition, 'definitions')
        keys(n, META | {'class', 'deprecated'}, 'Definition')
        need(n.get('deprecated', 'false') == 'false', 'deprecated Definition')
        need(all(local(c) in ('metadata', 'notes', 'criteria') for c in n), 'Definition children')
        cs = [c for c in n if local(c) == 'criteria']
        need(len(cs) == 1, 'Definition must have one complete criteria tree')
        result = self.criteria(cs[0])
        self.active.remove(definition)
        return result

    def criteria(self, n):
        need(n.tag == '{' + OD + '}' + local(n), 'foreign criteria namespace')
        keys(n, {'operator', 'negate', 'comment', 'test_ref', 'definition_ref'}, local(n))
        name = local(n)
        if name == 'criteria':
            result = boolean({'AND': 'and', 'OR': 'or', 'ONE': 'one', 'XOR': 'xor'}[
                n.get('operator', 'AND')], [self.criteria(c) for c in n])
        elif name == 'criterion':
            self.get(n.get('test_ref'), 'tests')
            result = {'test': n.get('test_ref')}
        elif name == 'extend_definition':
            result = self.expression(n.get('definition_ref'))
        else:
            raise Unsupported('criteria node: ' + name)
        need(n.get('negate', 'false') in ('true', 'false'), 'negate lexical value')
        return {'not': result} if n.get('negate') == 'true' else result

    def variable(self, ident):
        need(ident not in self.active, 'cyclic Variable')
        self.active.add(ident)
        n = self.get(ident, 'variables')
        keys(n, META | {'datatype'}, 'Variable')
        datatype = n.get('datatype')
        if local(n) == 'constant_variable':
            need(all(local(c) == 'value' and not c.attrib and not len(c) for c in n),
                 'constant Variable child')
            value = {'constant_values': [literal(datatype, c.text or '') for c in n]}
        elif local(n) == 'local_variable':
            need(len(n) == 1, 'local Variable expression')
            # OVAL int and the native integer spelling name the same primitive;
            # retain the declaration/cast boundary rather than comparing labels.
            value = {'local': {'datatype': 'integer' if datatype == 'int' else datatype,
                               'expression': self.function(n[0])}}
        else:
            raise Unsupported('external/unhandled Variable: ' + ident)
        self.active.remove(ident)
        return value

    def function(self, n):
        name = local(n)
        need(n.tag == '{' + OD + '}' + name, 'foreign function namespace')
        if name == 'literal_component':
            keys(n, {'datatype'}, name)
            return {'literal': literal(n.get('datatype', 'string'), n.text or '')}
        if name == 'variable_component':
            keys(n, {'var_ref'}, name)
            return self.variable(n.get('var_ref'))
        if name == 'object_component':
            keys(n, {'object_ref', 'item_field'}, name)
            return {'values': {'object': self.object(n.get('object_ref')),
                               'field': n.get('item_field')}}
        if name == 'concat':
            keys(n, set(), name)
            return {'concat': [self.function(c) for c in n]}
        raise Unsupported('source function proof unavailable: ' + name)

    def entity(self, n, *, selector=False):
        need(n.tag.startswith('{' + OD + '#') or n.tag == '{' + OD + '}field',
             'foreign entity namespace')
        keys(n, {'operation', 'datatype', 'var_ref', 'var_check', 'entity_check',
                 'check_existence', 'name'}, 'entity ' + local(n))
        found = n.get('check_existence', 'at_least_one_exists')
        need(found in FIELD_FOUND, 'unproved entity existence: ' + found)
        if not selector and found == 'none_exist':
            need(not len(n) and n.text is None and set(n.attrib) <= {'check_existence'},
                 'absence carries comparison/attributes; source-specific review required')
            return {'found': 'none'}
        op = n.get('operation', 'equals')
        need(op in OPS, 'unproved operation: ' + op)
        need(op != 'case insensitive not equal' or n.get('datatype', 'string') == 'string',
             'case-insensitive inequality requires original string datatype')
        if n.get('datatype') == 'record':
            need(not selector and op == 'equals', 'record operation')
            need(all(local(c) == 'field' and c.get('name') for c in n), 'record children')
            pairs = [(c.get('name'), self.entity(c)) for c in n]
            need(len(dict(pairs)) == len(pairs), 'duplicate record field')
            value = {'record': dict(sorted(pairs))}
        elif n.get('var_ref'):
            value = self.variable(n.get('var_ref'))
        else:
            need(not len(n), 'scalar entity children')
            value = literal(n.get('datatype', 'string'), n.text or '')
        datatype = n.get('datatype', 'string')
        result = {'operation': OPS[op], 'comparison_datatype': 'integer' if datatype == 'int' else datatype,
                  'operand': value}
        if n.get('var_ref'):
            # EntityAttributeGroup documentation explicitly specifies 'all'
            # when var_ref is present and var_check omitted (OVAL 5.12.3).
            need(n.get('var_check', 'all') in CHECK, 'var_check')
            result['expected_matching'] = CHECK[n.get('var_check', 'all')]
        if not selector:
            need(n.get('entity_check', 'all') in CHECK, 'entity_check')
            result.update(found=FIELD_FOUND[found], matching=CHECK[n.get('entity_check', 'all')])
        else:
            need(not set(n.attrib) & {'check_existence', 'entity_check'}, 'selector state attributes')
        return result

    def capability(self, n, suffix):
        key = n.tag[1:].removesuffix(suffix)
        need(key in CAPS, 'source family proof unavailable: ' + n.tag)
        return CAPS[key]

    def object(self, ident):
        need(ident not in self.active, 'cyclic Object')
        self.active.add(ident)
        n = self.get(ident, 'objects')
        cap = self.capability(n, '_object')
        keys(n, META, 'Object')
        need(not any(local(c) in ('set', 'filter', 'behaviors') for c in n),
             'Set/Filter/behavior collection proof unavailable: ' + ident)
        fields = {}
        for c in n:
            name = local(c)
            need(c.tag.rsplit('}', 1)[0] == n.tag.rsplit('}', 1)[0], 'Object field namespace')
            need(name not in fields, 'duplicate selector')
            if cap == 'windows.registry':
                need(name in ('hive', 'key', 'name'), 'registry selector')
                value = self.entity(c, selector=True)
                if name == 'hive':
                    old = value['operand'].get('value')
                    need(isinstance(old, str) and old in REGISTRY_HIVES, 'registry hive proof unavailable')
                    value['operand']['value'] = old.removeprefix('HKEY_').lower()
                fields[name] = value
            else:
                need(name in (('shell', 'command', 'pattern') if cap == 'independent.shellcommand'
                              else ('namespace', 'wql')), 'collection parameter: ' + name)
                value = self.entity(c, selector=True)
                expected = 'matches_regex' if name == 'pattern' else 'equals'
                need(value['operation'] == expected and value['comparison_datatype'] == 'string',
                     'collection parameter comparator/datatype')
                fields['query' if name == 'wql' else name] = value['operand']
        if cap == 'independent.shellcommand':
            fields.setdefault('shell', literal('string', 'bash'))
            fields.update(error_if_exit_status_not_0=False, error_if_stderr_exists=False)
        self.active.remove(ident)
        return {'capability': cap, 'selectors': fields}

    def state(self, ident, cap):
        n = self.get(ident, 'states')
        need(self.capability(n, '_state') == cap, 'State family mismatch')
        keys(n, META | {'operator'}, 'State')
        fields = []
        for c in n:
            need(c.tag.rsplit('}', 1)[0] == n.tag.rsplit('}', 1)[0], 'State field namespace')
            value = self.entity(c)
            if cap == 'windows.registry' and local(c) == 'type':
                enums = {'reg_sz': 'string', 'reg_dword': 'dword', 'reg_dword_little_endian': 'dword'}
                old = value['operand']
                need(old.get('datatype') == 'string' and old.get('value') in enums,
                     'registry type proof unavailable')
                value['operand'] = literal('string', enums[old['value']])
            fields.append({'field': local(c), 'predicate': value})
        return boolean(n.get('operator', 'AND').lower(), fields)

    def test(self, ident):
        n = self.get(ident, 'tests')
        keys(n, META | {'check', 'check_existence', 'state_operator', 'deprecated'}, 'Test')
        need(n.get('deprecated', 'false') == 'false', 'deprecated Test')
        cap = self.capability(n, '_test')
        need(all(local(c) in ('object', 'state') for c in n), 'Test children')
        objects = [c for c in n if local(c) == 'object']
        need(len(objects) == 1, 'Test Object boundary')
        for c in n:
            keys(c, {'object_ref'} if local(c) == 'object' else {'state_ref'}, 'Test reference')
        existence = n.get('check_existence', 'at_least_one_exists')
        need(existence in FOUND, 'Test existence requires source-pinned proof: ' + existence)
        states = [self.state(c.get('state_ref'), cap) for c in n if local(c) == 'state']
        result = {'capability': cap, 'object': self.object(objects[0].get('object_ref')),
                  'found': FOUND[existence]}
        need(result['object']['capability'] == cap, 'Test/Object family mismatch')
        if states:
            need(n.get('check') in CHECK, 'Test check')
            result.update(matching=CHECK[n.get('check')],
                          condition=boolean(n.get('state_operator', 'AND').lower(), states))
        return result


class Native:
    def __init__(self, assessment):
        self.a, self.active = assessment, set()
        self.used = {'tests': set(), 'shared_objects': set(), 'variables': set()}
        keys(assessment, {'id', 'version', 'assessment_title', 'class', 'purpose', 'mode',
                         'specification', 'tests', 'shared_objects', 'variables', 'evaluate'}, 'Assessment')
        need(assessment['mode'] == 'automated' and assessment['specification'] ==
             {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}, 'native version/mode')

    def reference(self, kind, ident):
        need((kind, ident) not in self.active, 'cyclic native reference')
        need(ident in self.a.get(kind, {}), 'missing native reference: ' + str(ident))
        self.used[kind].add(ident)
        return self.a[kind][ident]

    def expression(self, n):
        need(isinstance(n, dict) and len(n) == 1, 'native expression')
        op, value = next(iter(n.items()))
        if op == 'test':
            self.reference('tests', value)
            return {'test': value}
        if op == 'not':
            return {'not': self.expression(value)}
        return boolean(op, [self.expression(c) for c in value])

    def operand(self, value, datatype='string'):
        if isinstance(value, dict):
            if set(value) == {'variable'}:
                ident = value['variable']
                n = self.reference('variables', ident)
                self.active.add(('variables', ident))
                keys(n, {'kind', 'datatype', 'expression', 'title'}, 'Variable')
                need(n['kind'] == 'local', 'native Variable kind')
                result = {'local': {'datatype': n['datatype'], 'expression': self.function(n['expression'])}}
                self.active.remove(('variables', ident))
                return result
            raise Unsupported('native dynamic operand')
        if isinstance(value, list):
            return {'constant_values': [literal(datatype, v) for v in value]}
        return literal(datatype, value)

    def function(self, n):
        need(isinstance(n, dict) and len(n) == 1, 'native function shape')
        op, value = next(iter(n.items()))
        if op == 'literal':
            keys(value, {'datatype', 'value'}, 'literal')
            return {'literal': literal(value['datatype'], value['value'])}
        if op == 'variable':
            return self.operand(n)
        if op == 'values':
            keys(value, {'object', 'field'}, 'values')
            return {'values': {'object': self.object(value['object']), 'field': value['field']}}
        if op == 'concat':
            return {'concat': [self.function(c) for c in value]}
        raise Unsupported('native function proof unavailable: ' + op)

    def predicate(self, n, inherited=None, selector=False):
        need(isinstance(n, dict), 'native predicate type')
        policy = {**(inherited or {}), **n}
        if not selector and policy.get('values_found') == 'none':
            need(set(n) == {'values_found'}, 'native absence redundant fields')
            return {'found': 'none'}
        if 'record' in n:
            keys(n, {'record'}, 'record wrapper')
            r = n['record']
            keys(r, {'records_found', 'records_matching', 'fields'}, 'record')
            return {'operation': 'equals', 'comparison_datatype': 'record',
                    'found': r['records_found'], 'matching': r['records_matching'],
                    'operand': {'record': {k: self.predicate(v) for k, v in sorted(r['fields'].items())}}}
        ops = set(n) & set(OPS.values())
        need(len(ops) == 1, 'native scalar operation')
        op, = ops
        keys(n, {op, 'datatype', 'value_match'} | (set() if selector else
             {'values_found', 'values_matching'}), 'native scalar')
        dt = n.get('datatype', 'boolean' if isinstance(n[op], bool) else
                   'integer' if isinstance(n[op], int) else 'string')
        result = {'operation': op, 'comparison_datatype': dt, 'operand': self.operand(n[op], dt)}
        if 'value_match' in n:
            result['expected_matching'] = n['value_match']
        if not selector:
            need('values_found' in policy and 'values_matching' in policy, 'missing effective field policy')
            result.update(found=policy['values_found'], matching=policy['values_matching'])
        return result

    def condition(self, n, inherited=None):
        policy = n.get('field_requirement', inherited)
        nodes = set(n) & {'and', 'or', 'one', 'xor', 'fields'}
        need(len(nodes) == 1, 'native condition shape')
        op, = nodes
        keys(n, {op, 'items_found', 'items_satisfying', 'field_requirement'}, 'condition')
        if op == 'fields':
            return boolean('and', [{'field': name, 'predicate': self.predicate(v, policy)}
                                   for name, v in n[op].items()])
        return boolean(op, [self.condition(c, policy) for c in n[op]])

    def object(self, n, cap=None):
        if isinstance(n, str):
            ident = n
            value = self.reference('shared_objects', ident)
            self.active.add(('shared_objects', ident))
            result = self.object(value)
            self.active.remove(('shared_objects', ident))
            need(cap is None or result['capability'] == cap, 'native Object family mismatch')
            return result
        cap = n.get('capability', cap)
        allowed = {'windows.registry': {'hive', 'key', 'name'},
                   'independent.shellcommand': {'shell', 'command', 'pattern',
                      'error_if_exit_status_not_0', 'error_if_stderr_exists'},
                   'windows.wmi.query': {'namespace', 'query'}}
        need(cap in allowed, 'native capability proof unavailable: ' + str(cap))
        keys(n, allowed[cap] | {'capability', 'object_title'}, 'native Object')
        fields = {}
        for k, v in n.items():
            if k in ('capability', 'object_title'):
                continue
            fields[k] = (self.predicate(v, selector=True) if cap == 'windows.registry' else
                         v if k.startswith('error_if_') else self.operand(v))
        return {'capability': cap, 'selectors': fields}

    def test(self, ident):
        n = self.reference('tests', ident)
        keys(n, {'capability', 'object', 'test_title', 'reported_elements', 'require'}, 'native Test')
        need(n.get('reported_elements') == 'all', 'reporting/evidence proof requires all')
        r = n['require']
        result = {'capability': n['capability'], 'object': self.object(n['object'], n['capability']),
                  'found': r['items_found']}
        if set(r) != {'items_found'}:
            result.update(matching=r['items_satisfying'], condition=self.condition(r))
        return result


def first_difference(expected, actual, path='$'):
    if type(expected) is not type(actual):
        return {'path': path, 'source': expected, 'package': actual}
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            return {'path': path, 'source_keys': sorted(expected), 'package_keys': sorted(actual)}
        for key in expected:
            d = first_difference(expected[key], actual[key], path + '.' + key)
            if d:
                return d
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            return {'path': path, 'source_length': len(expected), 'package_length': len(actual)}
        for i, (a, b) in enumerate(zip(expected, actual)):
            d = first_difference(a, b, path + '[' + str(i) + ']')
            if d:
                return d
    elif expected != actual:
        return {'path': path, 'source': expected, 'package': actual}
    return None


def compare(source, definition, assessment, *, native_type=Native):
    """Bind Test IDs by the complete criteria/evaluate structure, never titles."""
    native = native_type(assessment)
    need(assessment.get('class') == source.get(definition, 'definitions').get('class')
         and assessment.get('purpose') == 'assessment', 'Assessment class/purpose boundary')
    expected, actual = source.expression(definition), native.expression(assessment['evaluate'])
    bindings, inverse = {}, {}
    def bind(a, b):
        if isinstance(a, dict) and set(a) == {'test'} and isinstance(b, dict) and set(b) == {'test'}:
            x, y = a['test'], b['test']
            need(bindings.get(x, y) == y and inverse.get(y, x) == x, 'ambiguous/merged Test binding')
            bindings[x], inverse[y] = y, x
            return {'test': x}
        if isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b):
            return {k: bind(a[k], b[k]) for k in a}
        if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
            return [bind(x, y) for x, y in zip(a, b)]
        return b
    rebound = bind(expected, actual)
    difference = first_difference(expected, rebound, '$.evaluate')
    if difference:
        return {'outcome': 'MISMATCH', 'first_divergence': difference, 'test_bindings': bindings}
    terms, unsupported = [], []
    for x, y in bindings.items():
        try:
            a, b = source.test(x), native.test(y)
            difference = first_difference(a, b, '$.tests.' + x)
            terms.append({'source_test': x, 'native_test': y, 'source_term': a,
                          'native_term': b, 'term_sha256': digest(a) if not difference else None})
            if difference:
                return {'outcome': 'MISMATCH', 'first_divergence': difference,
                        'test_bindings': bindings, 'comparisons': terms}
        except Unsupported as e:
            unsupported.append({'source_test': x, 'native_test': y, 'reason': str(e)})
        finally:
            # An unsupported branch is not a dependency cycle in later Tests.
            source.active.clear()
            native.active.clear()
    if not unsupported:
        for kind, used in native.used.items():
            need(used == set(assessment.get(kind, {})), 'unaccounted native declarations: ' + kind)
    return {'outcome': 'UNVERIFIABLE/UNSUPPORTED' if unsupported else 'PROVED',
            'test_bindings': bindings, 'comparisons': terms, 'unsupported_obligations': unsupported,
            'proof_scope': 'structural identity of typed collection/comparison/result terms; not scanner execution',
            'normalizations_applied': []}
