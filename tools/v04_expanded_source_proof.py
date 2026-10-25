#!/usr/bin/env python3
"""Bounded independent proof expansion; no production lowering or evaluator (#251).

OVAL rule anchors and native obligations are documented in the engineering
packet. Reading additional syntax never automatically discharges an obligation.
"""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from v04_source_package_semantics import (Source, Native, Unsupported, OD, META,
    boolean, compare, digest, keys, literal, local, need, xml_term)

ROOT = Path(__file__).resolve().parents[1]
EXTRA = {OD + '#unix}file': 'unix.file', OD + '#unix}password': 'unix.password',
         OD + '#independent}textfilecontent54': 'independent.textfilecontent54'}
NAMES = {'filepath': 'full_path', 'path': 'directory', 'filename': 'name'}
FILE_FIELDS = {**NAMES, 'suid': 'setuid', 'sgid': 'setgid', 'gwrite': 'group_write',
               'gexec': 'group_execute', 'oread': 'other_read', 'owrite': 'other_write',
               'oexec': 'other_execute'}
APPROVED_SOURCE = ROOT / 'research/assessment-simplification/evidence/rhel_9/SV-258179/source-oval.xml'
APPROVED_SHA = '463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9'
APPROVED_DEF = 'oval:mil.disa.stig.defs:def:230413'
DECISION = 'https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6388735943'


def predicate_order(term):
    """Only State conjunction/disjunction commutes; not Filters/functions/evaluate.

    Preserve duplicate operands, quantifier scopes and all six-state operators.
    OVAL AND/OR tables are commutative; no Boolean two-state identities used.
    """
    if isinstance(term, dict) and len(term) == 1 and next(iter(term)) in ('and', 'or'):
        op, values = next(iter(term.items()))
        return boolean(op, sorted((predicate_order(v) for v in values), key=digest))
    return term


def actual_items_evidence(status, items, *, claims_complete_success=False):
    """Proof admission guard, not a Test/collector evaluator. Preserve diagnostics."""
    need(status in ('complete', 'incomplete', 'error', 'not_collected', 'does_not_exist', 'not_applicable'),
         'unknown collection flag')
    need(all(i in ('exists', 'error', 'not_collected') for i in items),
         'synthetic nonexistent Item outside approved contract')
    need(status != 'does_not_exist' or not items, 'absent collection contains Items')
    need(status != 'complete' or all(i == 'exists' for i in items),
         'error/unknown evidence cannot become complete')
    need(not claims_complete_success or status == 'complete',
         'incomplete/error/unknown evidence cannot claim complete success')
    return {'collection_status': status, 'item_statuses': list(items)}


class ExpandedSource(Source):
    def __init__(self, oval):
        super().__init__(oval)
        self.normalization_ids, self.normalizations = set(), []

    def admit_pinned_rhel_normalization(self, definition, trace):
        raw = APPROVED_SOURCE.read_bytes()
        need(sha256(raw).hexdigest() == APPROVED_SHA, 'approved normalization fixture hash changed')
        approved = Source(ET.fromstring(raw))
        closure = approved.closure(APPROVED_DEF)
        current = self.closure(definition)
        approved_nodes = {n['id']: n for n in closure['nodes']}
        # Original wrapper is permitted only for the exact full SCAP/Rule pin.
        need(trace['source_zip_sha256'] == '70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5'
             and definition == 'oval:mil.disa.stig.rhel9os:def:258179', 'unapproved RHEL source scope')
        expected = [n for n in current['nodes'] if n['id'] != definition]
        need(len(expected) == len(closure['nodes']) and all(approved_nodes.get(n['id']) == n for n in expected),
             'original closure differs from approved normalization source')
        ids = {n['id'] for n in expected if n['kind'] == 'tests' and
               self.nodes[n['id']].get('check_existence') == 'all_exist'}
        need(len(ids) == 16 and all(not any(local(c) == 'state' for c in self.nodes[i]) for i in ids),
             'approved all_exist Test population changed')
        self.normalization_ids = ids
        schema = ROOT / 'schema/v0.4.0/collected-item.schema.json'
        need(set(json.loads(schema.read_text())['properties']['status']['enum']) ==
             {'exists', 'error', 'not_collected'}, 'actual-Items schema contract changed')
        self.item_schema_sha256 = sha256(schema.read_bytes()).hexdigest()

    def capability(self, n, suffix):
        return EXTRA.get(n.tag[1:].removesuffix(suffix)) or super().capability(n, suffix)

    def function(self, n):
        name = local(n)
        if name not in ('regex_capture', 'merge', 'unique'):
            value = super().function(n)
            # A one-valued typed constant component is exactly a literal,
            # with no dynamic status or aggregation boundary to erase.
            if name == 'variable_component' and 'constant_values' in value:
                need(len(value['constant_values']) == 1, 'multi-value constant component needs independent Cartesian proof')
                return {'literal': value['constant_values'][0]}
            return value
        need(n.tag == '{' + OD + '}' + name, 'foreign function namespace')
        keys(n, {'pattern'} if name == 'regex_capture' else
             {'delimiter', 'sort', 'order'} if name == 'merge' else set(), 'function ' + name)
        values = [self.function(c) for c in n]
        need(values, 'empty function')
        if name == 'regex_capture':
            need(len(values) == 1 and 'pattern' in n.attrib, 'regex_capture operand/pattern')
            return {'regex_capture': {'pattern': n.get('pattern'), 'value': values[0]}}
        if name == 'unique':
            need(len(values) == 1, 'multi-component unique proof not in this batch')
            return {'unique': values[0]}
        need(len(values) == 1, 'multi-component merge proof not in this batch')
        return {'merge': {'delimiter': n.get('delimiter', ''), 'sort': n.get('sort', 'document'),
                          'order': n.get('order', 'ascending'), 'values': values[0]}}

    def state(self, ident, cap):
        if cap == 'unix.file':
            need(all(local(c) in set(FILE_FIELDS) | {'type', 'sticky'} for c in self.get(ident, 'states')),
                 'file State field outside bounded proof rules')
        if cap == 'unix.password':
            need(all(local(c) in {'user_id', 'home_dir'} for c in self.get(ident, 'states')),
                 'password State field outside bounded proof rules')
        value = super().state(ident, cap)
        def rename(n):
            if 'field' in n:
                return {**n, 'field': FILE_FIELDS.get(n['field'], n['field']) if cap == 'unix.file' else n['field']}
            op, children = next(iter(n.items()))
            return {op: [rename(c) for c in children]}
        return predicate_order(rename(value))

    def filters(self, nodes, cap):
        result = []
        for n in nodes:
            need(n.tag == '{' + OD + '}filter', 'foreign Filter namespace')
            keys(n, {'action'}, 'Filter')
            action = n.get('action', 'exclude')
            need(action in ('include', 'exclude'), 'Filter action')
            result.append({action: self.state((n.text or '').strip(), cap)})
        return result

    def set_term(self, n, cap):
        keys(n, {'set_operator'}, 'Set')
        op = {'UNION': 'union', 'INTERSECTION': 'intersection', 'COMPLEMENT': 'difference'}.get(
            n.get('set_operator', 'UNION'))
        need(op, 'Set operator')
        refs = [c for c in n if local(c) in ('object_reference', 'set')]
        filters = [c for c in n if local(c) == 'filter']
        need(1 <= len(refs) <= 2 and len(refs) + len(filters) == len(n), 'Set children/arity')
        need(not filters or all(local(c) == 'object_reference' for c in refs), 'filters on nested Sets')
        operands = []
        for c in refs:
            need(c.tag == '{' + OD + '}' + local(c), 'Set child namespace')
            if local(c) == 'set':
                operand = {'capability': cap, 'set': self.set_term(c, cap)}
            else:
                keys(c, set(), 'object_reference')
                operand = self.object((c.text or '').strip())
                need(operand['capability'] == cap, 'Set Object family')
            operands.append({'object': operand, 'filters': self.filters(filters, cap)})
        # SetOperatorEnumeration explicitly makes EVERY one-operand Set the
        # complete referenced object (after its Filters), including COMPLEMENT.
        return {'operator': 'identity' if len(operands) == 1 else op, 'operands': operands}

    def object(self, ident):
        n = self.get(ident, 'objects')
        cap = self.capability(n, '_object')
        sets = n.findall('{' + OD + '}set')
        if sets:
            # SetType belongs to the common OVAL Object grammar, independent
            # of collector family. Never fall back to leaf selector reading.
            need(ident not in self.active, 'cyclic Object')
            keys(n, META, 'Set Object')
            need(len(n) == 1 and len(sets) == 1, 'Set mixed with leaf acquisition')
            self.active.add(ident)
            try:
                return {'capability': cap, 'set': self.set_term(sets[0], cap)}
            finally:
                self.active.remove(ident)
        if cap not in ('unix.file', 'unix.password', 'independent.textfilecontent54'):
            if cap == 'independent.shellcommand':
                # shellcommand.pattern is an intrinsic regex collector parameter
                # (its 5.12.3 element documentation), not an equals selector.
                n = deepcopy(n)
                for c in n:
                    if local(c) == 'pattern' and 'operation' not in c.attrib:
                        c.set('operation', 'pattern match')
                old = self.nodes[ident]
                self.nodes[ident] = n
                try:
                    return super().object(ident)
                finally:
                    self.nodes[ident] = old
            return super().object(ident)
        need(ident not in self.active, 'cyclic Object')
        self.active.add(ident)
        keys(n, META, 'Object')
        sets = [c for c in n if local(c) == 'set']
        if sets:
            need(len(n) == 1, 'Set mixed with selectors')
            value = {'capability': cap, 'set': self.set_term(sets[0], cap)}
        else:
            fields, behaviors = {}, {}
            fs = [c for c in n if local(c) == 'filter']
            for c in n:
                name = local(c)
                if name == 'filter':
                    continue
                need(c.tag.rsplit('}', 1)[0] == n.tag.rsplit('}', 1)[0], 'Object field namespace')
                if name == 'behaviors':
                    need(not behaviors, 'duplicate behaviors')
                    behaviors = dict(c.attrib)
                    continue
                allowed = {'unix.password': {'username'}, 'unix.file': {'filepath', 'path', 'filename'},
                           'independent.textfilecontent54': {'filepath', 'path', 'filename', 'pattern', 'instance'}}[cap]
                need(name in allowed and NAMES.get(name, name) not in fields, 'unproved/duplicate selector ' + name)
                fields[NAMES.get(name, name)] = self.entity(c, selector=True)
            if cap == 'unix.file':
                keys(behaviors, {'max_depth', 'recurse', 'recurse_direction', 'recurse_file_system'}, 'file behaviors')
                need(behaviors.get('recurse_direction', 'none') == 'down', 'file recursion direction not downward')
                depth = int(behaviors.get('max_depth', -1))
                recurse = behaviors.get('recurse', 'symlinks and directories')
                need(recurse in ('symlinks', 'directories', 'symlinks and directories'), 'deprecated/unproved recursion')
                fields['traversal'] = {'max_depth': None if depth == -1 else depth,
                    'recurse': 'symlinks_and_directories' if recurse == 'symlinks and directories' else recurse,
                    'direction': 'down'}
                fields['filesystem'] = {'all': 'all', 'local': 'local', 'defined': 'same'}[
                    behaviors.get('recurse_file_system', 'all')]
            elif cap == 'independent.textfilecontent54':
                keys(behaviors, {'ignore_case', 'multiline', 'singleline', 'item_creation', 'recurse_file_system'},
                     'textfile behaviors')
                fields['filesystem'] = behaviors.get('recurse_file_system', 'all')
                for name, default in (('ignore_case', 'false'), ('multiline', 'true'), ('singleline', 'false')):
                    v = behaviors.get(name, default)
                    need(v in ('true', 'false', '0', '1'), 'behavior boolean')
                    fields[name] = v in ('true', '1')
                fields['item_creation'] = behaviors.get('item_creation', 'all_object_elements_fullfilled')
            value = {'capability': cap, 'selectors': fields}
            if fs:
                value['filters'] = self.filters(fs, cap)
        self.active.remove(ident)
        return value

    def test(self, ident):
        n = self.get(ident, 'tests')
        if n.get('check_existence') != 'all_exist':
            result = super().test(ident)
            if 'condition' in result:
                result['condition'] = predicate_order(result['condition'])
            return result
        need(ident in self.normalization_ids, 'all_exist outside exact approved source proof')
        replacement = deepcopy(n)
        replacement.set('check_existence', 'at_least_one_exists')
        self.nodes[ident] = replacement
        try:
            result = super().test(ident)
        finally:
            self.nodes[ident] = n
        obj_id = next(c.get('object_ref') for c in n if local(c) == 'object')
        obj = self.get(obj_id, 'objects')
        self.normalizations.append({'source_test': ident, 'source_test_version': n.get('version'),
            'source_test_sha256': digest(xml_term(n)), 'source_object': obj_id,
            'source_object_version': obj.get('version'), 'source_object_sha256': digest(xml_term(obj)),
            'approved_source_sha256': APPROVED_SHA, 'owner_decision': DECISION,
            'approved_definition': APPROVED_DEF, 'actual_items_schema_sha256': self.item_schema_sha256,
            'contract': 'scap-ng-0.4.0/actual-items-test-all-exist/1',
            'unrestricted_oval_equivalence': False, 'original': 'all_exist', 'native': 'one_or_more',
            'status_policy': 'preserve error/incomplete/not_collected; no synthetic nonexistent Items'})
        return result


class ExpandedNative(Native):
    def function(self, n):
        need(isinstance(n, dict) and len(n) == 1, 'function shape')
        op, v = next(iter(n.items()))
        if op == 'literal' and not isinstance(v, dict):
            return {'literal': literal('string', v)}
        if op == 'regex_capture':
            keys(v, {'pattern', 'value'}, op)
            need(set(v) == {'pattern', 'value'}, 'regex_capture requires pattern and value')
            return {'regex_capture': {'pattern': v['pattern'], 'value': self.function(v['value'])}}
        if op == 'unique':
            return {'unique': self.function(v)}
        if op == 'merge':
            keys(v, {'delimiter', 'sort', 'order', 'values'}, op)
            need(set(v) == {'delimiter', 'sort', 'order', 'values'}, 'merge requires explicit default parameters')
            return {'merge': {'delimiter': v['delimiter'], 'sort': v['sort'], 'order': v['order'],
                              'values': self.function(v['values'])}}
        return super().function(n)

    def condition(self, n, inherited=None):
        return predicate_order(super().condition(n, inherited))

    def filter_condition(self, n):
        need(isinstance(n, dict) and n, 'Filter predicate')
        if set(n) <= {'and', 'or'}:
            op, values = next(iter(n.items()))
            return predicate_order(boolean(op, [self.filter_condition(c) for c in values]))
        if 'fields' in n:
            return self.condition(n)
        terms = []
        for field, predicate in n.items():
            p = deepcopy(predicate)
            if 'require' in p:
                need(p.pop('require') == 'at_least_one_exists_and_all_match', 'unproved Filter field requirement')
                p.update(values_found='one_or_more', values_matching='every')
            terms.append({'field': field, 'predicate': self.predicate(p)})
        return predicate_order(boolean('and', terms))

    def filters(self, fs):
        result = []
        for f in fs:
            need(isinstance(f, dict) and len(f) == 1, 'native Filter')
            action, predicate = next(iter(f.items()))
            need(action in ('include', 'exclude'), 'native Filter action')
            result.append({action: self.filter_condition(predicate)})
        return result

    def set_term(self, n, cap):
        keys(n, {'operator', 'operands'}, 'native Set')
        need(n['operator'] in ('union', 'intersection', 'difference') and 1 <= len(n['operands']) <= 2,
             'native Set operator/arity')
        operands = []
        for operand in n['operands']:
            if 'set' in operand:
                keys(operand, {'set'}, 'nested Set operand')
                obj = {'capability': cap, 'set': self.set_term(operand['set'], cap)}
            else:
                keys(operand, {'object', 'filters'}, 'Set operand')
                obj = self.object(operand['object'], cap)
            need(obj['capability'] == cap, 'Set family')
            operands.append({'object': obj, 'filters': self.filters(operand.get('filters', []))})
        return {'operator': 'identity' if len(operands) == 1 else n['operator'], 'operands': operands}

    def object(self, n, cap=None):
        if isinstance(n, str):
            return super().object(n, cap)
        cap = n.get('capability', cap)
        if 'collect' in n:
            keys(n, {'capability', 'collect', 'object_title'}, 'embedded Object')
            return self.object({**n['collect'], 'capability': cap})
        if 'set' in n:
            keys(n, {'set', 'capability', 'object_title'}, 'Set Object')
            return {'capability': cap, 'set': self.set_term(n['set'], cap)}
        if cap not in ('unix.file', 'unix.password', 'independent.textfilecontent54'):
            return super().object(n, cap)
        allowed = {'unix.password': {'username'}, 'unix.file': {'directory', 'name', 'full_path', 'filesystem', 'traversal'},
                   'independent.textfilecontent54': {'directory', 'name', 'full_path', 'pattern', 'instance',
                      'filesystem', 'ignore_case', 'singleline', 'multiline', 'item_creation'}}[cap]
        keys(n, allowed | {'capability', 'object_title', 'filters', 'for_each'}, 'Object')
        fields = {}
        for k, v in n.items():
            if k in ('capability', 'object_title', 'filters', 'for_each'):
                continue
            if k == 'traversal':
                keys(v, {'max_depth', 'recurse'}, 'traversal')
                fields[k] = {**v, 'direction': 'down'}
            elif k in ('filesystem', 'ignore_case', 'singleline', 'multiline', 'item_creation'):
                fields[k] = v
            elif isinstance(v, dict) and set(v) == {'from'}:
                loop = n.get('for_each')
                need(cap == 'unix.file' and loop and k == 'directory', 'unproved collection expansion')
                keys(loop, {'in', 'item'}, 'for_each')
                prefix = loop['item'] + '.'
                need(v['from'].startswith(prefix), 'for_each scope')
                fields[k] = {'operation': 'equals', 'comparison_datatype': 'string',
                    'operand': {'local': {'datatype': 'string', 'expression': {'values': {
                        'object': self.object(loop['in']), 'field': v['from'][len(prefix):]}}}},
                    'expected_matching': 'one_or_more'}
            else:
                fields[k] = self.predicate(v, selector=True)
        if 'for_each' in n:
            need(any(isinstance(v, dict) and 'from' in v for v in n.values()), 'unused collection expansion')
        value = {'capability': cap, 'selectors': fields}
        if n.get('filters'):
            value['filters'] = self.filters(n['filters'])
        return value


def expanded_compare(source, definition, assessment):
    result = compare(source, definition, assessment, native_type=ExpandedNative)
    if result['outcome'] == 'PROVED' and source.normalizations:
        for row in source.normalizations:
            row['native_test'] = result['test_bindings'][row['source_test']]
        result.update(outcome='PROVED_WITH_EXPLICIT_APPROVED_NORMALIZATION',
                      normalizations_applied=source.normalizations)
    return result
