"""Current authoring boundary for retained independent OVAL proof readers.

The private source views below are exporter inputs only, never authoring or
compiler input. Source readers still check pinned XML and every original
assertion. No capability-specific conversion decision belongs here. Refs #251.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

from build_v04_canonical_six_stigs import promote
from research_04_one_grammar_proof import CODES
from v04_canonical_source_ir import _schema_validators, validate_docs

ROOT = Path(__file__).resolve().parents[1]
FOUND = {'none': 'none', 'exactly_one': 'one', 'one_or_more': 'one_or_more',
         'every': 'all', 'may_be_absent': 'optional'}
MATCH = {'none': 'none', 'exactly_one': 'one', 'one_or_more': 'one_or_more', 'every': 'all'}
PRESENCE = {'none': 'none_exist', 'exactly_one': 'only_one_exists',
            'one_or_more': 'at_least_one_exists', 'may_be_absent': 'may_be_absent'}


@lru_cache(maxsize=1)
def validators():
    return _schema_validators(ROOT / 'schema/v0.4.0')


def current_document(source_view):
    """Project a freshly XML-derived proof view through the approved upgrader."""
    result, _ = promote(source_view, legacy_review=True)
    for test in result['assessment']['tests'].values():
        obj = test.get('object')
        if isinstance(obj, dict) and obj.get('capability') == test['capability']:
            del obj['capability']
    validate_docs({'authoring/source-proof.json': result}, validators())
    return result


def _pair(counts, prefix):
    return CODES[(FOUND[counts[prefix + '_found']], MATCH[counts[prefix + '_matching']])]


def _predicate(value, inherited):
    value = deepcopy(value)
    if 'record' in value:
        record = value['record']
        return {'record': {'require': _pair(record, 'records'), 'fields': {
            key: _predicate(pred, record.get('field_requirement'))
            for key, pred in record['fields'].items()}}}
    explicit = {key: value.pop(key) for key in ('values_found', 'values_matching') if key in value}
    counts = explicit or value.pop('field_requirement', inherited)
    if counts is None:
        raise ValueError('source proof: missing explicit/inherited field cardinality')
    value['require'] = _pair(counts, 'values')
    if 'value_match' in value:
        value['value_match'] = MATCH[value['value_match']]
    return value


def _condition(condition, inherited=None):
    inherited = condition.get('field_requirement', inherited)
    if 'fields' in condition:
        parts = [{key: _predicate(value, inherited)} for key, value in condition['fields'].items()]
        return parts[0] if len(parts) == 1 else {'and': parts}
    operator, = [key for key in ('and', 'or', 'one', 'xor') if key in condition]
    return {operator: [_condition(child, inherited) for child in condition[operator]]}


def _object_view(node):
    if isinstance(node, list):
        return [_object_view(value) for value in node]
    if not isinstance(node, dict):
        return deepcopy(node)
    result = {}
    for key, value in node.items():
        if key == 'filters':
            result[key] = [{action: _filter_view(condition) for action, condition in filt.items()}
                           for filt in value]
        elif key in ('selection_match', 'value_match'):
            result[key] = MATCH[value]
        else:
            result[key] = _object_view(value)
    return result


def _filter_view(condition):
    operators = [key for key in ('and', 'or', 'one', 'xor') if key in condition]
    if operators:
        operator, = operators
        return {operator: [_filter_view(child) for child in condition[operator]]}
    return {key: _predicate(value, None) for key, value in condition.items()}


def independent_export_view(document, *, inline_capability=True):
    """Validate current input, then expose explicit counts to old reverse readers.

    Existing independent exporters retain their original source-shape assertions.
    This bridge does not accept old authoring or recover source from hashes.
    """
    validate_docs({'authoring/source-proof.json': document}, validators())
    result = deepcopy(document)
    assessment = result['assessment']
    for section in ('shared_objects', 'variables'):
        if section in assessment:
            assessment[section] = _object_view(assessment[section])
    for test in assessment['tests'].values():
        requirement = test['require']
        if set(requirement) == {'items_found'}:
            test['require'] = PRESENCE[requirement['items_found']]
        else:
            test['require'] = CODES[(FOUND[requirement['items_found']], MATCH[requirement['items_satisfying']])]
            test['states'] = [_condition(requirement)]
        if isinstance(test.get('object'), dict):
            test['object'] = _object_view(test['object'])
            if inline_capability:
                test['object']['capability'] = test['capability']
    return result


def compile_proofs(documents, output):
    """Compile each source Assessment in an explicitly synthetic minimal wrapper.

    JSON/YAML pass the unchanged public typed compiler. A separate consumer
    verifies native packages and every compiled operand against its authoring.
    These wrappers make no complete original-Benchmark coverage claim.
    """
    import io
    import json
    import zipfile
    import yaml
    from v04_canonical_source_ir import compile_pair, decode_and_verify
    from v04_native_bundle_compiler import build_bundle
    from verify_v04_package_consumer import verify

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for document in documents:
        identity = document['assessment']['id']
        benchmark = {key: [] for key in ('title', 'description', 'status', 'notices',
            'front_matter', 'rear_matter', 'references', 'text_blocks', 'scoring',
            'parameters', 'groups', 'profiles')}
        benchmark.update(id='source-proof', ng_schema_version=None, use_case='compliance',
            language='en', version={'value': '1'}, metadata={},
            platform={'id': 'proof-platform', 'title': 'Synthetic proof wrapper', 'applicability': {}},
            applicability_catalog='proof-applicability', default_selection=True, rules=['proof-rule'],
            assessment_specifications=[{'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}])
        rule = {key: [] for key in ('warnings', 'identifiers', 'references', 'requires', 'conflicts', 'applicability')}
        rule.update(id='proof-rule', version='1', title='Synthetic proof wrapper', severity='medium',
            role='full', weight=1, discussion='', rationale=None, extensions={}, parameters={},
            remediation={}, organizational_input_requirements={},
            assessment_choices={'automated': {'assessment': identity}}, default_assessment_choice='automated')
        docs = {'authoring/proof/benchmark.json': {'benchmark': benchmark},
                'authoring/proof/applicability.json': {'applicability': {'id': 'proof-applicability', 'conditions': {}}},
                'authoring/proof/rules/proof.json': {'rule': rule},
                'authoring/proof/assessments/proof.json': document}
        archives = []
        for fmt in ('json', 'yaml'):
            target = output / (identity + '.' + fmt + '.zip')
            with zipfile.ZipFile(target, 'w') as package:
                for name, value in docs.items():
                    text = json.dumps(value) if fmt == 'json' else yaml.safe_dump(value, sort_keys=False)
                    package.writestr(name.removesuffix('.json') + '.' + fmt, text)
            archives.append(target)
        compiled, report = compile_pair(*archives)
        native = decode_and_verify(json.loads(compiled))
        raw, _ = build_bundle(native)
        package_path = output / (identity + '.scapng')
        package_path.write_bytes(raw)
        consumer = verify(package_path)
        results.append({'assessment': identity, 'compiler': report, 'independent_consumer': consumer,
                        'synthetic_benchmark_wrapper': True})
    (output / 'compilation-proof.json').write_text(json.dumps(results, indent=2) + '\n')
    return results
