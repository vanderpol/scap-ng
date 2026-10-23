#!/usr/bin/env python3
"""Production 0.4 Test promotion and source-exact inverse (Refs #251 #240).

Input States retain their original boundaries. Only ordinary scalar AND States
are compacted; records, repeated entities and non-AND State operators retain
the explicit source-exact fallback. No collection or result evaluation occurs.
"""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

PAIRS = {'at_least_one_exists_and_all_match': 'one_or_more',
         'may_be_absent_and_all_match': 'may_be_absent'}
PRESENCE = {'at_least_one_exists': 'one_or_more', 'none_exist': 'none',
            'only_one_exists': 'exactly_one', 'all_exist': 'all',
            'may_be_absent': 'may_be_absent'}
LOGIC = {'all': 'and', 'any': 'or', 'one': 'one', 'odd': 'xor',
         'and': 'and', 'or': 'or', 'xor': 'xor'}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False).encode()).hexdigest()


@lru_cache(maxsize=1)
def test_validator():
    from jsonschema import Draft202012Validator
    path = Path(__file__).resolve().parents[1] / 'schema/v0.4.0/assessment-language.schema.json'
    schema = json.loads(path.read_text())
    return Draft202012Validator({'$defs': schema['$defs'], '$ref': '#/$defs/test'})


def validate_test(test):
    errors = list(test_validator().iter_errors(test))
    if errors:
        first = errors[0]
        raise ValueError(f'invalid canonical 0.4 Test at {list(first.path)}: {first.message[:300]}')


class ExplicitFallback(Exception):
    """Known source shape without an independently approved compact lowering."""


def complete_condition(state):
    if not isinstance(state, dict) or not state:
        raise ValueError('invalid source State condition')
    scope = state.get('state_fields_require')
    keys = set(state) - {'state_fields_require'}
    if len(keys) != 1:
        raise ValueError('ambiguous source State condition')
    key = next(iter(keys)); payload = state[key]
    if key in LOGIC and isinstance(payload, list):
        if key not in ('and', 'all'):
            raise ExplicitFallback('non_and_state_operator')
        if not payload:
            raise ValueError('empty source State')
        entries = payload
    else:
        entries = [{key: payload}]
    fields = {}
    for entry in entries:
        if not isinstance(entry, dict) or len(entry) != 1:
            raise ExplicitFallback('nested_state_condition')
        name, predicate = next(iter(entry.items()))
        if not isinstance(predicate, dict) or not predicate:
            raise ExplicitFallback('nested_state_condition')
        if 'record' in predicate:
            raise ExplicitFallback('record_cardinality')
        if name in fields:
            raise ExplicitFallback('repeated_state_field')
        field = deepcopy(predicate)
        if 'field_requirement' in field:
            raise ValueError('mixed source/canonical field requirement')
        if 'require' in field:
            field['field_requirement'] = field.pop('require')
        fields[name] = field
    condition = {'fields': fields}
    if 'state_fields_require' in state:
        condition['field_requirement'] = scope
    return condition


def legacy_review_source(test):
    """Rehydrate the pinned preview's structured Test as source State nodes.

    This is an explicit compatibility boundary, never implicit canonical input
    repair. Reuse normal source promotion for fields, grouping and fallbacks.
    No predicate, Item requirement or State/field cardinality is inferred.
    """
    source = deepcopy(test)
    req = source['require']
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
    """Return canonical/fallback Test and a separate checked inverse ledger."""
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
        validate_test(test)  # Never guess an import dialect from its nesting.
    elif isinstance(requirement, str):
        states = test.get('states')
        if requirement in PAIRS and isinstance(states, list) and states:
            try:
                conditions = [complete_condition(state) for state in states]
                operator = test.get('states_match')
                if operator is not None and operator not in LOGIC:
                    raise ValueError('unknown source Test State operator')
                if len(conditions) > 1 and operator is None:
                    raise ValueError('multiple source States lack explicit State operator')
                if operator is not None:
                    conditions = [{LOGIC[operator]: conditions}]
                req = {'items': PAIRS[requirement], 'all_items_must': conditions}
                if 'state_fields_require' in test:
                    req['field_requirement'] = test.pop('state_fields_require')
                test.pop('states'); test.pop('states_match', None)
                test['require'] = req
                validate_test(test)
                shape = 'all_items_must'
            except ExplicitFallback as exc:
                # Start again from the source: partial projection must not leak.
                test = deepcopy(original)
                if 'collected_items_require' in test:
                    test['require'] = test.pop('collected_items_require')
                diagnostic = str(exc)
                shape = 'explicit_fallback'
        elif requirement in PRESENCE and 'states' not in test and 'states_match' not in test:
            test['require'] = {'items': PRESENCE[requirement]}
            validate_test(test)
            shape = 'presence_only_structured'
        else:
            diagnostic = 'uncommon_test_requirement'
            shape = 'explicit_fallback'
    else:
        raise ValueError('missing or invalid source Test requirement')
    if shape == 'explicit_fallback':
        validate_test(test)
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
    """Index effective declarations without changing the source AST or results.

    Paths identify each field in its complete condition and the nearest authored
    declaration. Each recursive branch receives its own inherited scope.
    """
    if not isinstance(requirement, dict) or 'all_items_must' not in requirement:
        return []
    found = []
    def visit(node, path, inherited, declared_at):
        if 'field_requirement' in node:
            inherited = node['field_requirement']
            declared_at = [*path, 'field_requirement']
        if 'fields' in node:
            for name, predicate in sorted(node['fields'].items()):
                field_path = [*path, 'fields', name]
                effective = predicate.get('field_requirement', inherited)
                declaration = ([*field_path, 'field_requirement']
                               if 'field_requirement' in predicate else declared_at)
                if effective is None:
                    raise ValueError('field has no explicit or inherited requirement')
                found.append({'path': field_path, 'field_requirement': effective,
                              'declaration_path': declaration})
        else:
            for operator in ('and', 'or', 'one', 'xor'):
                if operator in node:
                    for index, child in enumerate(node[operator]):
                        visit(child, [*path, operator, index], inherited, declared_at)
    inherited = requirement.get('field_requirement')
    declared_at = ['require', 'field_requirement'] if inherited is not None else None
    for index, node in enumerate(requirement['all_items_must']):
        visit(node, ['require', 'all_items_must', index], inherited, declared_at)
    return found
