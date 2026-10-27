"""Independent single-input acquisition proof, without command/query expansion.

This module reads source terms, never converter output or lowering helpers.
Record fields use their existing quantified predicates and do not pass here.
"""
from v04_source_package_semantics import need


def single_value(term):
    """A closed scalar expression has no runtime collection/cardinality branch."""
    if set(term) == {'literal'}:
        return term['literal'].get('datatype') == 'string'
    if set(term) == {'local'}:
        return term['local'].get('datatype') == 'string' and single_value(term['local']['expression'])
    if set(term) == {'concat'}:
        return bool(term['concat']) and all(single_value(v) for v in term['concat'])
    if set(term) == {'regex_capture'}:
        return single_value(term['regex_capture']['value'])
    if set(term) == {'unique'}:
        return single_value(term['unique'])
    return False


def parameter_operand(predicate):
    """Retain named scalar expressions; fold only one immutable expected value.

    Static constants and nondefault quantifiers need an explicit singleton
    proof. Existing named runtime inputs with default all retain their approved
    graph/operand correspondence. That evidence does not independently prove
    invocation multiplicity or scanner execution; the acquisition audit records
    that separate obligation rather than changing established admission here.
    """
    operand = predicate['operand']
    if 'expected_matching' not in predicate:
        return operand
    need(predicate['expected_matching'] in ('every', 'one_or_more', 'exactly_one'),
         'unproved complement acquisition parameter')
    if 'constant_values' in operand:
        need(len(operand['constant_values']) == 1, 'unproved multivalue acquisition parameter expansion')
        return operand['constant_values'][0]
    if predicate['expected_matching'] == 'every':
        return operand
    need(single_value(operand), 'unproved runtime acquisition parameter expansion')
    return operand
