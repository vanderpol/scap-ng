"""Explain conversion gaps without changing admission or interpreting results.

Schema limitations require a reviewed, source-pinned case. A native-schema
rejection alone is a converter failure, never evidence to change the schema.
Every classification retains the original message and its evidence basis.
"""
from collections import Counter

IMPLEMENTATION = 'converter_implementation_missing'
SCHEMA = 'capability_schema_limitation'
VARIABLE = 'variable_collection_representation_limitation'
OPERATION = 'unsupported_oval_operation'
SOURCE = 'invalid_original_source'
EXTERNAL = 'external_infrastructure_failure'


def classify_failure(message, *, stage='conversion', validity=None, dependency=None):
    """Evidence precedence: original validity, reviewed gap, then diagnostics."""
    if validity and (validity['status'] != 'VALID' or
                     any(i.get('kind') == 'deprecated' for i in validity.get('issues', []))):
        category, basis = SOURCE, 'original XSD/Schematron/reference/deprecation evidence'
    elif stage == 'infrastructure':
        category, basis = EXTERNAL, 'explicit external infrastructure failure; not source/conversion evidence'
    elif dependency:
        category, basis = dependency['category'], dependency['reason']
        if category not in (SCHEMA, VARIABLE):
            raise ValueError('reviewed schema dependency has invalid category')
    elif any(token in message for token in ('Variable cast', 'unsupported var_check',
            'multi-component merge', 'multi-component unique', 'enum comparison/value',
            'unproved entity existence', 'unproved aggregation')):
        category, basis = VARIABLE, 'unrepresented Variable/collection obligation; no fallback attempted'
    elif any(token in message for token in ('unsupported entity existence/comparator',
            'ordered comparison', 'unsupported function', 'unsupported OVAL operation')):
        category, basis = OPERATION, 'explicit unsupported operation diagnostic'
    else:
        category, basis = IMPLEMENTATION, 'converter or independent proof obligation not implemented/established'
    result = {'category': category, 'stage': stage, 'message': message, 'basis': basis}
    if dependency:
        result['dependency_id'] = dependency['id']
    return result


def summarize_failures(records):
    """Count cases once per category; retain independent blockers on each case."""
    counts = Counter(category for r in records for category in {d['category'] for d in r['failures']})
    return {'cases': len(records),
            'cases_by_category': {k: counts[k] for k in (IMPLEMENTATION, SCHEMA, VARIABLE, OPERATION, SOURCE, EXTERNAL)},
            'cases_by_scope': dict(sorted(Counter(r.get('scope', 'primary_rule') for r in records).items())),
            'counting': 'Each case once per category; categories may overlap. No admission authority.'}
