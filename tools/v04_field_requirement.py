#!/usr/bin/env python3
"""Production 0.4 Test promotion and source-exact inverse (Refs #251 #240).

Source States retain logical boundaries, repeated fields, record counts and
expected-value quantifiers. Unsupported source shapes fail closed; source-only
spellings remain in checked provenance. No collection or evaluation occurs.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

# Source adapter vocabulary, never accepted as authored 0.4 aliases.
from research_04_one_grammar_proof import PAIR_BY_NAME
PAIRS = {'at_least_one_exists_and_all_match': 'one_or_more',
         'may_be_absent_and_all_match': 'may_be_absent'}
PRESENCE = {'at_least_one_exists': 'one_or_more', 'none_exist': 'none',
            'only_one_exists': 'exactly_one', 'all_exist': 'one_or_more',
            'may_be_absent': 'may_be_absent'}
FIELD_EXISTENCE = {'none': 'none', 'one': 'exactly_one',
                   'one_or_more': 'one_or_more', 'all': 'every',
                   'optional': 'may_be_absent'}
MATCH = {'all': 'every', 'one': 'exactly_one',
         'one_or_more': 'one_or_more', 'none': 'none'}
LOGIC = {'all': 'and', 'any': 'or', 'one': 'one', 'odd': 'xor',
         'and': 'and', 'or': 'or', 'xor': 'xor'}


def field_pair(name):
    if name not in PAIR_BY_NAME:
        raise ValueError(f'unmapped source field requirement: {name!r}')
    existence, match = PAIR_BY_NAME[name]
    return {'values_found': FIELD_EXISTENCE[existence],
            'values_matching': MATCH[match]}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False).encode()).hexdigest()


@lru_cache(maxsize=1)
def test_validator():
    from jsonschema import Draft202012Validator
    path = Path(__file__).resolve().parents[1] / 'schema/v0.4.0/assessment-language.schema.json'
    schema = json.loads(path.read_text())
    from referencing import Registry, Resource
    schemas = [json.loads(p.read_text()) for p in path.parent.glob('*.schema.json')]
    registry = Registry().with_resources(
        (s['$id'], Resource.from_contents(s)) for s in schemas)
    return Draft202012Validator({'$id': schema['$id'], '$defs': schema['$defs'],
                                 '$ref': '#/$defs/test'}, registry=registry)


def validate_test(test):
    errors = list(test_validator().iter_errors(test))
    if errors:
        first = errors[0]
        raise ValueError(f'invalid canonical 0.4 Test at {list(first.path)}: {first.message[:300]}')


class ExplicitFallback(Exception):
    """Known source shape without an independently approved compact lowering."""


def source_predicate(predicate):
    if not isinstance(predicate, dict) or not predicate:
        raise ValueError('invalid source field predicate')
    out = deepcopy(predicate)
    if 'field_requirement' in out or 'values_found' in out:
        raise ValueError('mixed source/canonical field requirement')
    if 'record' in out:
        if set(out) != {'record'}:
            raise ValueError('unmapped source record wrapper attributes')
        record = out['record']
        if isinstance(record, dict) and record.get('require') == 'none_exist':
            if set(record) - {'require', 'fields'} or record.get('fields', {}) != {}:
                raise ValueError('record absence cannot discard member predicates or attributes')
            return {'record': {'records_found': 'none'}}
        if not isinstance(record, dict) or not isinstance(record.get('fields'), dict):
            raise ValueError('invalid source record')
        counts = field_pair(record.pop('require', None))
        record['records_found'] = counts['values_found']
        record['records_matching'] = counts['values_matching']
        record['fields'] = {name: source_predicate(value)
                            for name, value in record['fields'].items()}
    elif 'require' in out:
        if out['require'] == 'none_exist':
            # Original Gatekeeper and DNS entities explicitly assert
            # check_existence=none_exist with no operand. Mature XML lowering
            # may materialize that missing text as equals:""/datatype:string.
            # This is an explicit source-dialect migration, not canonical input
            # repair. A present-value equals:"" uses a different source token
            # and is retained. The full lexical source remains in the ledger.
            if (set(out) - {'require', 'equals', 'datatype'}
                    or ('equals' in out and out['equals'] != '')
                    or ('datatype' in out and out['datatype'] not in {'string', 'record'})):
                raise ValueError('field absence cannot discard a meaningful comparison or attributes')
            if out.get('datatype') == 'record':
                # Empty OVAL record entities have no member list for the old
                # mapper to recognize; retain the explicit record type here.
                return {'record': {'records_found': 'none'}}
            return {'values_found': 'none'}
        out.update(field_pair(out.pop('require')))
    if 'value_match' in out:
        if out['value_match'] not in MATCH:
            raise ValueError('unmapped source expected-value quantifier')
        out['value_match'] = MATCH[out['value_match']]
    return out


def complete_condition(state):
    if not isinstance(state, dict) or not state:
        raise ValueError('invalid source State condition')
    keys = set(state) - {'state_fields_require'}
    if len(keys) != 1:
        raise ValueError('ambiguous source State condition')
    key = next(iter(keys)); payload = state[key]
    scope = ({'field_requirement': field_pair(state['state_fields_require'])}
             if 'state_fields_require' in state else {})
    if key in LOGIC and isinstance(payload, list):
        if not payload:
            raise ValueError('empty source State')
        # Keep repeated field predicates and logical boundaries distinct.
        return {**scope, LOGIC[key]: [complete_condition(child) for child in payload]}
    return {**scope, 'fields': {key: source_predicate(payload)}}


def source_object_counts(node, *, filter_condition=False):
    """Versioned source adapter: retain acquisition/Set/Filter position and operands."""
    if isinstance(node, list):
        return [source_object_counts(v, filter_condition=filter_condition) for v in node]
    if not isinstance(node, dict):
        return deepcopy(node)
    if isinstance(node.get('record'), dict) and 'require' in node['record']:
        return source_predicate(node)
    out = {}
    for key, value in node.items():
        if key == 'require' and isinstance(value, str):
            out.update(field_pair(value))
        elif key in ('value_match', 'selection_match'):
            if value not in MATCH:
                raise ValueError(f'unmapped source {key}: {value}')
            out[key] = MATCH[value]
        elif filter_condition and key == 'state_fields_require':
            out['field_requirement'] = field_pair(value)
        else:
            target = LOGIC.get(key, key) if filter_condition and isinstance(value, list) else key
            out[target] = source_object_counts(value,
                filter_condition=filter_condition or key == 'filters')
    return out


def legacy_review_source(test):
    """Rehydrate the pinned preview's structured Test as source State nodes.

    This is an explicit compatibility boundary, never implicit canonical input
    repair. Reuse normal source promotion for fields, grouping and fallbacks.
    No predicate, Item requirement or State/field cardinality is inferred.
    """
    source = deepcopy(test)
    req = source['require']
    if set(req) == {'items'}:
        source['require'] = {'one_or_more': 'at_least_one_exists', 'none': 'none_exist',
                             'exactly_one': 'only_one_exists', 'all': 'all_exist',
                             'may_be_absent': 'may_be_absent'}.get(req['items'])
        if source['require'] is None:
            raise ValueError('unmapped legacy review Item population')
        return source
    if (set(req) - {'items', 'all_items_must', 'field_requirement'}
            or req.get('items') not in PAIRS.values()
            or not isinstance(req.get('all_items_must'), list)
            or not req['all_items_must'] or 'states' in source):
        raise ValueError('unsupported legacy review Test requirement')

    def field(predicate):
        if not isinstance(predicate, dict) or not predicate:
            raise ValueError('invalid legacy review field predicate')
        out = deepcopy(predicate)
        if 'field_requirement' in out:
            if 'require' in out:
                raise ValueError('mixed legacy review field requirements')
            out['require'] = out.pop('field_requirement')
        return out

    def state(node):
        if not isinstance(node, dict) or not node:
            raise ValueError('invalid legacy review condition')
        scopes = set(node) & {'require', 'state_fields_require', 'field_requirement'}
        if len(scopes) > 1:
            raise ValueError('mixed legacy review condition requirements')
        keys = set(node) - scopes
        if len(keys) != 1:
            raise ValueError('ambiguous legacy review condition')
        key = next(iter(keys))
        value = node[key]
        if key in LOGIC:
            if not isinstance(value, list) or not value:
                raise ValueError('empty legacy review logical operands')
            out = {key: [state(child) for child in value]}
        elif key == 'fields':
            if not isinstance(value, dict) or not value:
                raise ValueError('empty legacy review fields')
            out = {'and': [{name: field(predicate)} for name, predicate in value.items()]}
        else:
            out = {key: field(value)}
        if scopes:
            out['state_fields_require'] = node[next(iter(scopes))]
        return out

    source['states'] = [state(node) for node in req['all_items_must']]
    if len(source['states']) > 1 and 'states_match' not in source:
        source['states_match'] = 'all'  # all_items_must is a conjunction.
    if 'field_requirement' in req:
        if 'state_fields_require' in source:
            raise ValueError('mixed legacy review Test field requirements')
        source['state_fields_require'] = req['field_requirement']
    source['require'] = next(key for key, value in PAIRS.items() if value == req['items'])
    return source


def promote_test(original, *, legacy_review=False):
    """Return a schema-valid canonical Test and separate checked source ledger."""
    test = deepcopy(original)
    if 'collected_items_require' in test:
        if 'require' in test:
            raise ValueError('Mixed Test requirement dialect')
        test['require'] = test.pop('collected_items_require')
    requirement = test.get('require')
    diagnostic = None
    shape = 'unchanged'
    if (isinstance(requirement, dict) and legacy_review
            and not test_validator().is_valid(test)):
        candidate, proof = promote_test(legacy_review_source(test))
        return candidate, {**proof, 'source_test': deepcopy(original),
                           'source_sha256': digest(original), 'legacy_review': True}
    if isinstance(requirement, dict):
        validate_test(test)
    elif isinstance(requirement, str):
        states = test.get('states')
        if isinstance(states, list) and states:
            if requirement not in PAIR_BY_NAME:
                raise ValueError(f'unmapped source Test requirement: {requirement}')
            existence, matching = PAIR_BY_NAME[requirement]
            found = FIELD_EXISTENCE[existence]
            if found == 'every':
                diagnostic = 'test_all_exist_normalization_requires_actual_items_contract'
                found = 'one_or_more'  # Approved Test-only crosswalk; source retained below.
            conditions = [complete_condition(state) for state in states]
            operator = test.get('states_match')
            if operator is not None and operator not in LOGIC:
                raise ValueError('unknown source Test State operator')
            if len(conditions) > 1 and operator is None:
                raise ValueError('multiple source States lack explicit State operator')
            condition = ({LOGIC[operator]: conditions} if operator is not None
                         else conditions[0])
            if 'state_fields_require' in test and 'field_requirement' in condition:
                condition = {'and': [condition]}
            req = {'items_found': found, 'items_satisfying': MATCH[matching], **condition}
            if 'state_fields_require' in test:
                req['field_requirement'] = field_pair(test.pop('state_fields_require'))
            test.pop('states'); test.pop('states_match', None)
            test['require'] = req
            shape = 'structured_condition'
        elif requirement in PRESENCE and 'states' not in test and 'states_match' not in test:
            test['require'] = {'items_found': PRESENCE[requirement]}
            if requirement == 'all_exist':
                diagnostic = 'test_all_exist_normalization_requires_actual_items_contract'
            shape = 'presence_only_structured'
        else:
            raise ValueError(f'unrepresentable source Test requirement: {requirement!r}')
        if isinstance(test.get('object'), dict):
            test['object'] = source_object_counts(test['object'])
        validate_test(test)
    else:
        raise ValueError('missing or invalid source Test requirement')
    ledger = {'source_test': deepcopy(original), 'source_sha256': digest(original),
              'candidate_sha256': digest(test), 'shape': shape,
              'diagnostic': diagnostic, 'scanner_parity': False}
    return test, ledger


def restore_test(candidate, ledger):
    if digest(candidate) != ledger['candidate_sha256']:
        raise ValueError('candidate Test changed before source reconstruction')
    source = ledger['source_test']
    if digest(source) != ledger['source_sha256']:
        raise ValueError('source Test ledger checksum mismatch')
    projected, proof = promote_test(source, legacy_review=ledger.get("legacy_review", False))
    if projected != candidate or proof != ledger:
        raise ValueError('source Test inverse/provenance mismatch')
    return deepcopy(source)


def field_scopes(requirement):
    """Index explicit/inherited scalar and record counts without changing the AST."""
    found = []
    def visit(node, path, inherited=None, declared_at=None):
        if not isinstance(node, dict):
            return
        if 'field_requirement' in node:
            inherited = node['field_requirement']
            declared_at = [*path, 'field_requirement']
        for name, predicate in node.get('fields', {}).items():
            field_path = [*path, 'fields', name]
            if 'record' in predicate:
                record = predicate['record']
                found.append({'path': [*field_path, 'record'],
                              'record_requirement': {key: record[key] for key in
                                  ('records_found', 'records_matching') if key in record}})
                visit(record, [*field_path, 'record'])
                continue
            explicit = {key: predicate[key] for key in ('values_found', 'values_matching')
                        if key in predicate}
            effective = explicit or predicate.get('field_requirement', inherited)
            if effective is None:
                raise ValueError('field has no explicit or inherited requirement')
            found.append({'path': field_path, 'field_requirement': effective,
                          'declaration_path': (field_path if explicit else
                              [*field_path, 'field_requirement'] if 'field_requirement' in predicate
                              else declared_at)})
        for operator in ('and', 'or', 'one', 'xor'):
            for index, child in enumerate(node.get(operator, [])):
                visit(child, [*path, operator, index], inherited, declared_at)
    visit(requirement, ['require'])
    return found
