#!/usr/bin/env python3
"""Fresh direct-0.4 experiment: pinned SCAP -> a labeled two-Rule fixture.

Conversion uses current capability metadata, not old NG renderers or IRs.
Public validation, compilation and independent proof are separate commands.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import time
import zipfile

from v04_direct_scap_source import (
    SourceModel, UnsupportedSource, OVAL, XCCDF, attributes, digest, ensure,
    local_name, native_identifier, xml_identity,
)

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = ('windows.registry', 'independent.shellcommand')
EXISTENCE = {'at_least_one_exists': 'one_or_more', 'none_exist': 'none',
             'only_one_exists': 'exactly_one', 'any_exist': 'may_be_absent'}
MATCHING = {'all': 'every', 'at least one': 'one_or_more', 'none satisfy': 'none', 'only one': 'exactly_one'}
COMPARISONS = {'equals': 'equals', 'not equal': 'not_equal', 'pattern match': 'matches_regex',
               'case insensitive equals': 'case_insensitive_equals', 'less than': 'less_than'}
SET_OPERATORS = {'UNION': 'union', 'INTERSECTION': 'intersection', 'COMPLEMENT': 'difference'}


def load_mappings():
    mappings = [json.loads((ROOT / f'schema/v0.4.0/capability-mappings/supported/{name}.json').read_text())
                for name in CAPABILITIES]
    ensure(all(mapping['specification_version'] == '0.4.0' for mapping in mappings), 'mapping version mismatch')
    return mappings


def logical_condition(operator, children):
    ensure(operator in ('AND', 'OR') and children, f'unsupported/empty logical operator: {operator}')
    # A sole AND/OR operand preserves all six results; no two-valued rewrites.
    return children[0] if len(children) == 1 else {operator.lower(): children}


class AssessmentConverter:
    """One typed recursive visitor per component/Assessment, with explicit caches.

    References return native dictionaries/literal arrays, never an intermediate
    representation. `used` is external provenance; other containers are native
    declarations. Cached values are copied so a consumer cannot mutate a peer.
    """
    def __init__(self, source, component_id, mappings):
        self.source, self.component_id, self.mappings = source, component_id, mappings
        self.active, self.cache, self.used = set(), {}, {}
        self.tests, self.variables, self.shared_objects = {}, {}, {}

    def capability(self, element, kind):
        matches = [mapping for mapping in self.mappings if element.tag ==
                   f'{{{mapping["source"]["namespace"]}}}{mapping["source"].get(kind)}']
        ensure(len(matches) == 1, f'unsupported {kind} capability: {element.tag}')
        return matches[0]

    def reference(self, identifier, kind):
        key = kind, identifier
        ensure(key not in self.active, f'cyclic {kind} dependency: {identifier}')
        if key in self.cache:
            return deepcopy(self.cache[key])
        element = self.source.node(self.component_id, identifier, kind)
        permitted = {'definition': {'class'}, 'test': {'check', 'check_existence', 'state_operator'},
                     'object': set(), 'state': {'operator'}, 'variable': {'datatype'}}
        attributes(element, {'id', 'version', 'comment'} | permitted[kind])
        if kind in ('definition', 'variable'):
            ensure(element.tag.startswith(f'{{{OVAL}}}'), 'Definition/Variable namespace mismatch')
        self.active.add(key)
        self.used[identifier] = {'kind': kind, 'sha256': digest(xml_identity(element))}
        try:
            result = getattr(self, 'convert_' + kind)(element)
            self.cache[key] = result
            return deepcopy(result)
        finally:
            self.active.remove(key)

    def convert_definition(self, element):
        criteria = element.findall(f'{{{OVAL}}}criteria')
        ensure(len(criteria) == 1, 'one Definition criteria boundary required')
        return self.criteria(criteria[0])

    def criteria(self, element):
        attributes(element, {'operator', 'comment', 'negate'})
        ensure(element.get('negate', 'false') in ('true', 'false'), 'unsupported negate lexical')
        children = []
        for child in element:
            if child.tag == f'{{{OVAL}}}criteria':
                value = self.criteria(child)
            else:
                kind = {'criterion': 'test', 'extend_definition': 'definition'}.get(local_name(child))
                ensure(kind and child.tag == f'{{{OVAL}}}{local_name(child)}', 'unsupported criteria child')
                attributes(child, {kind + '_ref', 'comment', 'negate'})
                value = self.reference(child.get(kind + '_ref'), kind)
                ensure(child.get('negate', 'false') in ('true', 'false'), 'unsupported negate lexical')
                if child.get('negate') == 'true':
                    value = {'not': value}
            children.append(value)
        value = logical_condition(element.get('operator', 'AND'), children)
        return {'not': value} if element.get('negate') == 'true' else value

    def convert_test(self, element):
        mapping = self.capability(element, 'test')
        objects = element.findall(f'{{{mapping["source"]["namespace"]}}}object')
        ensure(len(objects) == 1, 'one Test Object required')
        conditions = []
        for child in element:
            kind = local_name(child)
            ensure(kind in ('object', 'state') and child.tag == f'{{{mapping["source"]["namespace"]}}}{kind}', 'Test child namespace/shape')
            attributes(child, {kind + '_ref'})
            ensure(not len(child), 'Test reference has children')
            if kind == 'state':
                self.same_family(child.get('state_ref'), 'state', mapping)
                conditions.append(self.reference(child.get('state_ref'), 'state'))
        found = element.get('check_existence', 'at_least_one_exists')
        ensure(found in EXISTENCE, f'unsupported Test existence: {found}')
        requirement = {'items_found': EXISTENCE[found]}
        if conditions:
            ensure(element.get('check') in MATCHING and found != 'none_exist', 'unsupported Test matching/absence combination')
            requirement.update(items_satisfying=MATCHING[element.get('check')])
            requirement.update(logical_condition(element.get('state_operator', 'AND'), conditions))
        object_id = objects[0].get('object_ref')
        self.same_family(object_id, 'object', mapping)
        acquisition = self.reference(object_id, 'object')
        if isinstance(acquisition, dict):
            acquisition.pop('capability')  # Test inheritance; Variable/private Objects keep their own capability.
        identifier = native_identifier(element, 'test')
        self.tests[identifier] = {'test_title': element.get('comment', ''), 'capability': mapping['capability'],
                                  'object': acquisition, 'require': requirement, 'reported_elements': 'all'}
        return {'test': identifier}

    def same_family(self, identifier, kind, mapping):
        node = self.source.node(self.component_id, identifier, kind)
        ensure(self.capability(node, kind)['capability'] == mapping['capability'], f'{kind} capability mismatch: {identifier}')

    def convert_state(self, element):
        mapping = self.capability(element, 'state')
        conditions, seen = [], set()
        for child in element:
            field = local_name(child)
            ensure(child.tag.startswith(f'{{{mapping["source"]["namespace"]}}}') and
                   field in mapping['native']['state_field_map'], 'unsupported State field/namespace')
            ensure(field not in seen, 'repeated State field outside bounded proof')
            seen.add(field)
            conditions.append({'fields': {mapping['native']['state_field_map'][field]: self.predicate(child, mapping)}})
        return logical_condition(element.get('operator', 'AND'), conditions)

    def convert_object(self, element):
        mapping = self.capability(element, 'object')
        acquisition = {'capability': mapping['capability']}
        sets = element.findall(f'{{{OVAL}}}set')
        if sets:
            ensure(len(element) == 1, 'Set cannot mix with leaf acquisition or direct Filters')
            acquisition['set'] = self.set_expression(sets[0], mapping)
        else:
            selectors = mapping['native'].get('selector_map', {})
            parameters = mapping['native'].get('collection_parameter_source_map', {})
            filters = []
            for child in element:
                if child.tag == f'{{{OVAL}}}filter':
                    filters.append(self.filter(child, mapping))
                    continue
                field = local_name(child)
                ensure(child.tag.startswith(f'{{{mapping["source"]["namespace"]}}}') and
                       field in selectors.keys() | parameters.keys(), f'unsupported Object field: {field}')
                target = selectors.get(field, parameters.get(field))
                ensure(target not in acquisition, 'duplicate Object field')
                acquisition[target] = self.predicate(child, mapping, selector=True) if field in selectors else self.parameter(child)
            for path, value in mapping.get('migration_crosswalk', {}).get('materialized_defaults', {}).items():
                ensure(path.startswith('behaviors.'), 'unrecognized acquisition default')
                acquisition[path.split('.')[1]] = value
            if filters:
                acquisition['filters'] = filters
        # Source identity, not payload equality, determines shared acquisitions.
        if self.source.object_references[self.component_id, element.get('id')] > 1:
            identifier = native_identifier(element, 'object')
            self.shared_objects[identifier] = acquisition
            return identifier
        return acquisition

    def set_expression(self, element, mapping):
        attributes(element, {'set_operator'})
        operator = element.get('set_operator', 'UNION')
        ensure(operator in SET_OPERATORS, f'unsupported Set operator: {operator}')
        nested = element.findall(f'{{{OVAL}}}set')
        references = element.findall(f'{{{OVAL}}}object_reference')
        filters = element.findall(f'{{{OVAL}}}filter')
        ensure(bool(nested) != bool(references), 'Set must contain nested Sets or Object references, not both')
        ensure(1 <= len(nested or references) <= 2, 'OVAL Set arity outside 1..2')
        ensure(len(element) == len(nested) + len(references) + len(filters) and not (nested and filters), 'unsupported Set child/filter placement')
        operands = []
        if nested:
            operands = [{'set': self.set_expression(child, mapping)} for child in nested]
        else:
            predicates = [self.filter(child, mapping) for child in filters]
            for reference in references:
                attributes(reference, set())
                ensure(not len(reference), 'object_reference has children')
                identifier = (reference.text or '').strip()
                self.same_family(identifier, 'object', mapping)
                # OVAL applies each ordered Filter to EACH operand before the
                # operator. A root post-Set Filter would change that boundary.
                operands.append({'object': self.reference(identifier, 'object'), 'filters': deepcopy(predicates)})
        return {'operator': SET_OPERATORS[operator], 'operands': operands}

    def filter(self, element, mapping):
        attributes(element, {'action'})
        ensure(not len(element), 'Filter must reference a State')
        action = element.get('action', 'exclude')
        ensure(action in ('include', 'exclude'), f'unsupported Filter action: {action}')
        identifier = (element.text or '').strip()
        self.same_family(identifier, 'state', mapping)
        return {action: self.filter_condition(self.reference(identifier, 'state'))}

    def filter_condition(self, condition):
        # The approved Filter grammar names a single field directly; Test
        # conditions use a `fields` leaf. Quantifiers and logical boundaries
        # are identical. Render this typed condition, never arbitrary records.
        if 'fields' in condition:
            ensure(len(condition['fields']) == 1, 'Filter requires one field per leaf')
            return condition['fields']
        operator, children = next(iter(condition.items()))
        return {operator: [self.filter_condition(child) for child in children]}

    def convert_variable(self, element):
        datatype = element.get('datatype')
        ensure(datatype in ('string', 'int', 'boolean'), f'unsupported Variable datatype: {datatype}')
        if local_name(element) == 'constant_variable':
            ensure(len(element) and all(child.tag == f'{{{OVAL}}}value' and not child.attrib and not len(child) for child in element), 'malformed constant Variable')
            # Immutable source constants become typed expected arrays. Keep the
            # consumer's var_check separately; never infer it from array length.
            return [self.literal(datatype, child.text or '') for child in element]
        ensure(local_name(element) == 'local_variable' and len(element) == 1, 'external/malformed Variable unsupported')
        identifier = native_identifier(element, 'variable')
        self.variables[identifier] = {'kind': 'local', 'datatype': 'integer' if datatype == 'int' else datatype,
                                      'expression': self.function(element[0])}
        return {'variable': identifier}

    def function(self, element):
        ensure(element.tag.startswith(f'{{{OVAL}}}'), 'function namespace mismatch')
        operation = local_name(element)
        if operation == 'literal_component':
            attributes(element, {'datatype'})
            ensure(not len(element), 'literal_component has children')
            return {'literal': {'datatype': element.get('datatype', 'string'),
                                'value': self.literal(element.get('datatype', 'string'), element.text or '')}}
        if operation == 'variable_component':
            attributes(element, {'var_ref'})
            value = self.reference(element.get('var_ref'), 'variable')
            ensure(not len(element) and isinstance(value, dict), 'constant array function needs Cartesian proof')
            return value
        if operation == 'object_component':
            attributes(element, {'object_ref', 'item_field'})
            ensure(not len(element), 'object_component has children')
            identifier = element.get('object_ref')
            mapping = self.capability(self.source.node(self.component_id, identifier, 'object'), 'object')
            ensure(element.get('item_field') in mapping['native']['state_field_map'], 'unknown object_component field')
            return {'values': {'object': self.reference(identifier, 'object'),
                               'field': mapping['native']['state_field_map'][element.get('item_field')]}}
        ensure(operation in ('concat', 'regex_capture'), f'unsupported function: {operation}')
        attributes(element, {'pattern'} if operation == 'regex_capture' else set())
        ensure(len(element) and (operation != 'regex_capture' or (len(element) == 1 and 'pattern' in element.attrib)), 'function arity/pattern')
        values = [self.function(child) for child in element]
        return {'concat': values} if operation == 'concat' else {'regex_capture': {'pattern': element.get('pattern'), 'value': values[0]}}

    @staticmethod
    def literal(datatype, text):
        ensure(datatype in ('string', 'int', 'boolean'), f'unsupported scalar datatype: {datatype}')
        if datatype == 'boolean':
            ensure(text in ('true', 'false', '1', '0'), 'invalid boolean literal')
            return text in ('true', '1')
        try:
            return int(text) if datatype == 'int' else text
        except ValueError as error:
            raise UnsupportedSource(f'invalid {datatype} literal: {text!r}') from error

    def operand(self, element):
        if element.get('var_ref'):
            variable = self.source.node(self.component_id, element.get('var_ref'), 'variable')
            # Cross-datatype OVAL casts can produce error/unknown results; do
            # not silently infer a target type from a literal array's values.
            ensure(variable.get('datatype') == element.get('datatype', 'string'), 'Variable cast outside bounded proof')
            return self.reference(element.get('var_ref'), 'variable')
        return self.literal(element.get('datatype', 'string'), element.text or '')

    def parameter(self, element):
        attributes(element, {'datatype', 'operation', 'var_ref'})
        ensure(not len(element) and element.get('datatype', 'string') == 'string' and
               element.get('operation', 'equals') == 'equals', 'unsupported acquisition parameter comparison/type')
        value = self.operand(element)
        ensure(isinstance(value, (str, dict)), 'array acquisition parameter unsupported')
        return value

    def predicate(self, element, mapping, selector=False):
        attributes(element, {'datatype', 'operation', 'var_ref', 'var_check'} |
                   (set() if selector else {'entity_check', 'check_existence'}))
        ensure(not len(element), 'record/nested entity unsupported')
        existence = element.get('check_existence', 'at_least_one_exists')
        if existence == 'none_exist':
            ensure(not selector and set(element.attrib) == {'check_existence'} and not element.text, 'comparator-bearing absence blocked')
            return {'values_found': 'none'}
        operation = element.get('operation', 'equals')
        ensure(existence in EXISTENCE and operation in COMPARISONS, 'unsupported entity existence/comparator')
        value = self.operand(element)
        crosswalk = mapping['native'].get('selector_value_crosswalk' if selector else 'state_value_crosswalk', {}).get(local_name(element))
        if crosswalk:
            ensure(operation == 'equals' and isinstance(value, str) and value in mapping['migration_crosswalk'][crosswalk], 'unsupported enum comparison/value')
            value = mapping['migration_crosswalk'][crosswalk][value]
        result = {COMPARISONS[operation]: value}
        if element.get('datatype', 'string') != 'string':
            result['datatype'] = 'integer' if element.get('datatype') == 'int' else element.get('datatype')
        if element.get('var_ref'):
            ensure(element.get('var_check', 'all') in MATCHING, 'unsupported var_check')
            result['value_match'] = MATCHING[element.get('var_check', 'all')]
        if not selector:
            ensure(element.get('entity_check', 'all') in MATCHING, 'unsupported entity_check')
            result.update(values_found=EXISTENCE[existence], values_matching=MATCHING[element.get('entity_check', 'all')])
        return result


def convert(source: SourceModel, rule_ids: list[str]):
    """Return (native documents by relative path, external source trace); no I/O."""
    ensure(len(rule_ids) == 2 and len(set(rule_ids)) == 2, 'exactly two distinct source Rules required')
    mappings = load_mappings()
    documents, rule_trace, rule_links = {}, [], {}
    for source_id in rule_ids:
        ensure(source_id in source.rules, f'source Rule not found: {source_id}')
        rule = source.rules[source_id]
        component, definition, omitted_checks = source.automated_check(rule)
        converter = AssessmentConverter(source, component, mappings)
        expression = converter.reference(definition, 'definition')
        rule_id = native_identifier(rule, 'rule')
        assessment_id = rule_id.removesuffix('-rule') + '-assessment'
        title = rule.findtext(f'{{{XCCDF}}}title', '')
        assessment = {'id': assessment_id, 'version': 1, 'assessment_title': title,
            'mode': 'automated', 'class': source.node(component, definition, 'definition').get('class'),
            'purpose': 'assessment', 'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'},
            'tests': converter.tests, 'evaluate': expression}
        for section in ('variables', 'shared_objects'):
            if getattr(converter, section):
                assessment[section] = getattr(converter, section)
        documents[f'authoring/direct-slice/assessments/{assessment_id}.json'] = {'assessment': assessment}
        # This is a compilation fixture, not a full Rule-policy renderer.
        native_rule = {'id': rule_id, 'version': rule.findtext(f'{{{XCCDF}}}version', ''), 'title': title,
            'severity': rule.get('severity', 'unknown'), 'role': 'full', 'weight': float(rule.get('weight', '1')),
            'discussion': rule.findtext(f'{{{XCCDF}}}description', ''), 'rationale': None,
            'extensions': {}, 'warnings': [], 'identifiers': [], 'references': [], 'requires': [], 'conflicts': [],
            'applicability': [], 'parameters': {}, 'remediation': {}, 'organizational_input_requirements': {},
            'assessment_choices': {'automated': {'assessment': assessment_id}}, 'default_assessment_choice': 'automated'}
        documents[f'authoring/direct-slice/rules/{rule_id}.json'] = {'rule': native_rule}
        rule_links[source_id] = rule_id
        rule_trace.append({'source_rule': source_id, 'source_rule_sha256': digest(xml_identity(rule)),
            'component': component, 'definition': definition, 'native_rule': rule_id, 'assessment': assessment_id,
            'dependencies': converter.used, 'omitted_checks': omitted_checks,
            'source_platforms': [child.get('idref') for child in rule.findall(f'{{{XCCDF}}}platform')]})
    benchmark = source.benchmark
    ensure(all(source.rule_selected(source.rules[identifier]) for identifier in rule_ids), 'disabled source defaults unsupported')
    profiles, profile_trace = [], []
    for profile in benchmark.findall(f'{{{XCCDF}}}Profile'):
        selection = {identifier: source.rule_selected(source.rules[identifier], profile) for identifier in rule_ids}
        identifier = native_identifier(profile, 'profile')
        profiles.append({'id': identifier, 'title': profile.findtext(f'{{{XCCDF}}}title'),
                         'disabled_rules': [rule_links[rule] for rule, enabled in selection.items() if not enabled]})
        profile_trace.append({'source_id': profile.get('id'), 'source_sha256': digest(xml_identity(profile)),
                              'native_id': identifier, 'selected': selection})
    wrapper = {'id': 'direct-slice', 'ng_schema_version': '0.4.0', 'use_case': 'compliance',
        'version': {'value': benchmark.findtext(f'{{{XCCDF}}}version', '')},
        'assessment_specifications': [{'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}],
        'title': [{'text': '[TWO-RULE PROTOTYPE SUBSET] ' + benchmark.findtext(f'{{{XCCDF}}}title', ''), 'language': 'en'}],
        'description': [{'text': benchmark.findtext(f'{{{XCCDF}}}description', ''), 'language': 'en'}],
        'language': benchmark.get('{http://www.w3.org/XML/1998/namespace}lang'),
        'status': [{'value': child.text, **child.attrib} for child in benchmark.findall(f'{{{XCCDF}}}status')],
        'metadata': {'prototype_subset': True, 'omitted_rule_count': len(source.rules) - 2},
        'notices': [], 'front_matter': [], 'rear_matter': [], 'references': [], 'text_blocks': [],
        'platform': {'id': 'fixture-platform', 'title': 'Compilation fixture; applicability not converted', 'applicability': {}},
        'applicability_catalog': 'fixture-applicability', 'scoring': [], 'parameters': [], 'default_selection': True,
        'groups': [], 'profiles': profiles, 'rules': list(rule_links.values())}
    documents['authoring/direct-slice/benchmark.json'] = {'benchmark': wrapper}
    documents['authoring/direct-slice/applicability.json'] = {'applicability': {'id': 'fixture-applicability', 'conditions': {}}}
    trace = {'format': 'direct-converter-spike/1', 'source_zip_sha256': source.zip_sha256, 'source_xml_sha256': source.xml_sha256,
        'source_member': source.member, 'source_benchmark_component': source.benchmark_component,
        'component_hashes': source.component_hashes, 'rules': rule_trace, 'profiles': profile_trace,
        'source_benchmark_metadata': [xml_identity(child) for child in benchmark if local_name(child) not in ('Group', 'Rule', 'Profile', 'Value')],
        'omitted_rules': sorted(set(source.rules) - set(rule_ids)), 'xml_parse_calls': source.parse_count,
        'component_index_passes': len(source.components), 'mapping_sha256': {m['capability']: digest(m) for m in mappings},
        'scope': 'Automated Assessment/selection subset, not full Rule-policy or Benchmark conversion',
        'unsupported': ['other Rules', 'manual execution', 'CPE/platform execution', 'full Rule metadata/remediation/scoring',
                        'behaviors', 'records', 'all_exist', 'other capabilities/functions'],
        'coverage_promoted': False, 'scanner_evaluated': False}
    return documents, trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--rule', action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args()
    ensure(not arguments.output.exists(), 'output exists; refusing overwrite')
    started = time.perf_counter()
    source = SourceModel(arguments.source, arguments.sha256)
    indexed = time.perf_counter()
    documents, trace = convert(source, arguments.rule)
    converted = time.perf_counter()
    import yaml
    for relative, document in documents.items():
        target = arguments.output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(document, indent=2) + '\n')
        target.with_suffix('.yaml').write_text(yaml.safe_dump(document, sort_keys=False))
    (arguments.output / 'source-trace.json').write_text(json.dumps(trace, indent=2) + '\n')
    metrics = {'parse_index': indexed - started, 'conversion': converted - indexed}
    try:
        import resource
        metrics['process_peak_rss_kib_linux'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:
        metrics['process_peak_rss_kib_linux'] = None
    (arguments.output / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
    print(json.dumps(metrics))


if __name__ == '__main__':
    try:
        main()
    except (UnsupportedSource, zipfile.BadZipFile, OSError) as error:
        raise SystemExit(str(error))
