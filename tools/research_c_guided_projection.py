#!/usr/bin/env python3
"""Refs #245: experimental C -> Guided controls + compiler-checked edits.

NOT normative C; no GUI, scanner, source-preserving YAML writer, migration,
production patch format, capability expansion or semantic acceptance. This
adapts the existing C research grammar without introducing another dialect.
"""
from __future__ import annotations
from copy import deepcopy
import re

GUIDE_VERSION = 'c-guided-research/0.1'
MODES = frozenset({'any_item', 'every_item', 'one_matching_item',
                   'no_matching_item', 'exactly_one_item'})
PRESENCE = frozenset({'present', 'absent', 'one_item_exists',
                      'all_items_exist', 'optional'})
COMBINE = frozenset({'every', 'one_of', 'not', 'exactly_one', 'odd_count'})
IDENTIFIER = re.compile(r'[a-z][a-z0-9_]{0,63}\Z')


def _shape(document):
    if not isinstance(document, dict):
        raise ValueError('C source document must be a mapping')
    if set(document) == {'from', 'must'}:
        return None, {'single_check': document}, {'check': 'single_check'}
    if set(document) != {'id', 'checks', 'require'} or (
        type(document['id']) is not str or not document['id'] or
        not isinstance(document['checks'], dict) or
        not (1 <= len(document['checks']) <= 50)
    ):
        raise ValueError('unsupported C Assessment research shape')
    checks = document['checks']
    if any(type(k) is not str or not IDENTIFIER.fullmatch(k)
           for k in checks):
        raise ValueError('C check name must have safe identity')
    return document['id'], checks, document['require']


def _logic(node, valid_names, depth=0):
    if depth > 128:
        raise ValueError('C condition nesting exceeds supported limit')
    if not isinstance(node, dict) or len(node) != 1:
        raise ValueError('C require expression must have one named operator')
    op, value = next(iter(node.items()))
    if op == 'check':
        if type(value) is not str or value not in valid_names:
            raise ValueError('unresolved C check in composition')
        return {'kind': 'check', 'check_id': value}
    if op not in COMBINE:
        raise ValueError('unknown C boolean operator')
    if op == 'not':
        return {'kind': 'not', 'child': _logic(value, valid_names, depth + 1)}
    if not isinstance(value, list) or not value or len(value) > 100:
        raise ValueError('nonempty, bounded C condition list required')
    return {'kind': op, 'children': [_logic(n, valid_names, depth + 1) for n in value]}


def _fields(must):
    if type(must) is str:
        if must not in PRESENCE:
            raise ValueError('unrecognized presence requirement')
        return must, [], False, False
    if not isinstance(must, dict) or not must:
        raise ValueError('C Item requirement must be explicit')
    if len(must) == 1 and next(iter(must)) in MODES:
        mode, fields = next(iter(must.items()))
        locked = False
    elif set(must) in ({'items_exist', 'items_match', 'fields'},
                       {'special_source_requirement', 'fields'}):
        mode, fields, locked = 'advanced_source_requirement', must['fields'], True
    else:
        # The prototype compiler permits bare must; Guided should not present
        # a hidden any_item meaning as an author-friendly default.
        mode, fields, locked = 'implicit_any_item', must, True
    if not isinstance(fields, dict) or not fields:
        raise ValueError('same-Item requirement needs field predicates')
    rows = []
    for name, value in fields.items():
        if type(name) is not str or not name:
            raise ValueError('empty expected field name')
        if isinstance(value, dict) and len(value) == 1:
            op, expected = next(iter(value.items()))
        else:
            op, expected = 'equals', value
        rows.append({'field': name, 'comparison': op,
                     'expected': deepcopy(expected),
                     'expected_type': type(expected).__name__,
                     'same_item': True})
    return mode, rows, locked, False


def project_c_guided(document):
    """Lossless *read-only* tree projection for supported research shapes.

    The returned view is not source YAML and must never be serialized as it.
    """
    assessment_id, checks, expression = _shape(document)
    cards = []
    for name, check in checks.items():
        if not isinstance(check, dict) or set(check) != {'from', 'must'}:
            raise ValueError('every check needs one from and one must')
        frm = check['from']
        if not isinstance(frm, dict) or len(frm) != 1:
            raise ValueError('one pinned source capability per check')
        capability, params = next(iter(frm.items()))
        if type(capability) is not str or not isinstance(params, dict):
            raise ValueError('source capability requires selector/arguments')
        mode, rows, locked, _ = _fields(check['must'])
        cards.append({'id': name,
                      'source': {'capability': capability,
                                 'parameters': deepcopy(params)},
                      'population_requirement': mode,
                      'field_conditions': rows,
                      'editable_with_pinned_compiler': not locked,
                      'meaning_warning':
                          'Bare must hides any_item semantics; choose explicit item scope'
                          if mode == 'implicit_any_item' else
                          'Advanced requirement needs expert source-backed review'
                          if locked else None})
    logic = _logic(expression, set(checks))
    return {'projection': GUIDE_VERSION,
            'assessment_id': assessment_id,
            'checks': cards,
            'combine_checks': logic,
            'view_only_not_authoritative': True,
            'scanner_verified': False,
            'source_format_preserved': False,
            'authored_C_grammar_approved': False}


def _replace_check_refs(node, old, new):
    if isinstance(node, dict):
        if set(node) == {'check'} and node['check'] == old:
            node['check'] = new
        else:
            for value in node.values():
                _replace_check_refs(value, old, new)
    elif isinstance(node, list):
        for value in node:
            _replace_check_refs(value, old, new)


def _edit(tree, operation):
    if not isinstance(operation, dict) or 'action' not in operation:
        raise ValueError('structured edit action required')
    action = operation['action']
    allowed = {
        'rename_check': {'action', 'check', 'new_name'},
        'set_expected': {'action', 'check', 'field', 'value'},
        'set_item_scope': {'action', 'check', 'mode', 'acknowledge_semantic_change'},
        'set_root_logic': {'action', 'mode', 'acknowledge_semantic_change'},
        'set_source_argument': {'action', 'check', 'argument', 'value',
                                'acknowledge_semantic_change'},
    }
    if action not in allowed or set(operation) != allowed[action]:
        raise ValueError('unknown or ambiguous Guided edit operation')
    _, checks, _ = _shape(tree)
    check_id = operation.get('check')
    if check_id is not None and check_id not in checks:
        raise ValueError('unknown check identity')
    if action == 'rename_check':
        if set(tree) == {'from', 'must'}:
            raise ValueError('standalone C requirement has no named check')
        new = operation['new_name']
        if type(new) is not str or not IDENTIFIER.fullmatch(new) or new in checks:
            raise ValueError('duplicate or invalid check identity')
        if new == check_id:
            raise ValueError('no-op rename')
        tree['checks'] = {new if k == check_id else k: v for k, v in checks.items()}
        _replace_check_refs(tree['require'], check_id, new)
        return
    if action == 'set_root_logic':
        if set(tree) == {'from', 'must'}:
            raise ValueError('standalone C requirement has no logic operator')
        if operation['acknowledge_semantic_change'] is not True:
            raise ValueError('changing AND/OR requires acknowledgement')
        mode = operation['mode']
        current = tree['require']
        if mode not in {'every', 'one_of'} or not isinstance(current, dict) or (
            set(current) not in ({'every'}, {'one_of'})
        ):
            raise ValueError('only explicit same-level AND/OR transition supported')
        if mode == next(iter(current)):
            raise ValueError('no-op operator edit')
        tree['require'] = {mode: deepcopy(next(iter(current.values())))}
        return
    check = checks[check_id]
    if action == 'set_source_argument':
        if operation['acknowledge_semantic_change'] is not True:
            raise ValueError('source population change needs acknowledgement')
        src = check['from']
        capability = next(iter(src))
        field = operation['argument']
        if type(field) is not str or field not in src[capability]:
            raise ValueError('cannot invent selector/collection parameter')
        original = src[capability][field]
        if type(original) is not type(operation['value']):
            raise ValueError('source argument type change forbidden')
        src[capability][field] = deepcopy(operation['value'])
        return
    mode, rows, locked, _ = _fields(check['must'])
    if locked or mode in PRESENCE:
        raise ValueError('advanced/implicit/presence-only requirement needs expert editing')
    if action == 'set_item_scope':
        new = operation['mode']
        if operation['acknowledge_semantic_change'] is not True:
            raise ValueError('Item quantifier change needs acknowledgement')
        if type(new) is not str or new not in MODES or new == mode:
            raise ValueError('unknown or unchanged Item quantifier')
        check['must'] = {new: deepcopy(check['must'][mode])}
        return
    if action == 'set_expected':
        field = operation['field']
        values = check['must'][mode]
        if type(field) is not str or field not in values:
            raise ValueError('expected field must already exist')
        old = values[field]
        if isinstance(old, dict) and len(old) == 1:
            op, previous = next(iter(old.items()))
            if type(previous) is not type(operation['value']):
                raise ValueError('expected-value type change requires different operation')
            values[field] = {op: deepcopy(operation['value'])}
        else:
            if type(old) is not type(operation['value']):
                raise ValueError('expected-value type change forbidden')
            values[field] = deepcopy(operation['value'])
        return


def propose_guided_edit(document, operation, *, source_documents=None):
    """Atomically propose C AST change; compile through existing C/A adapter.

    Parsing/serializing YAML and preserving comments/formatting belong to a
    separate source-safe editor; no source text is ever changed here.
    """
    project_c_guided(document)
    original = deepcopy(document)
    edited = deepcopy(document)
    _edit(edited, operation)
    project_c_guided(edited)
    source_documents = source_documents or {}
    if set(edited) == {'id', 'checks', 'require'}:
        from research_c_composed_assessment import compile_c_composed_assessment
        compiled = compile_c_composed_assessment(edited, source_documents=source_documents)
    else:
        if 'windows.wmi.query' in edited['from']:
            from research_c_wmi_source_compat import lower_c_wmi_absence
            source = source_documents.get('single_check')
            if source is None:
                raise ValueError('WMI source-compatibility document must be pinned')
            compiled = lower_c_wmi_absence(edited, source)
        else:
            from research_c_require_language import compile_c_requirement
            compiled = compile_c_requirement(edited)
    assert document == original
    return {'stage': 'GUIDED_C_RESEARCH_VALIDATED_PROPOSAL_NOT_SOURCE_PATCH',
            'proposed_C_ast': edited,
            'guided_view': project_c_guided(edited),
            'compiler_stage': compiled.get('stage', 'SOURCE_COMPATIBILITY_OR_A_TEST_PIECES'),
            'requires_source_diff_and_human_approval': True,
            'scanner_verified': False,
            'source_text_modified': False}
