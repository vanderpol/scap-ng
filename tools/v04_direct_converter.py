#!/usr/bin/env python3
"""Fresh direct-0.4 experiment: pinned SCAP -> an explicitly partial automated subset.

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
CAPABILITIES = ('windows.registry', 'independent.shellcommand', 'windows.auditeventpolicysubcategories',
                'windows.userright', 'windows.wmi.query', 'windows.passwordpolicy', 'windows.lockoutpolicy',
                'windows.service')
EXISTENCE = {'at_least_one_exists': 'one_or_more', 'none_exist': 'none',
             'only_one_exists': 'exactly_one', 'any_exist': 'may_be_absent'}
MATCHING = {'all': 'every', 'at least one': 'one_or_more', 'none satisfy': 'none', 'only one': 'exactly_one'}
COMPARISONS = {'equals': 'equals', 'not equal': 'not_equal', 'pattern match': 'matches_regex',
               'case insensitive equals': 'case_insensitive_equals', 'less than': 'less_than',
               'greater than': 'greater_than', 'greater than or equal': 'greater_than_or_equal',
               'less than or equal': 'less_than_or_equal'}
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
        self.object_uses = None
        self.selector_equivalences = []

    def capability(self, element, kind):
        matches = [mapping for mapping in self.mappings if element.tag ==
                   f'{{{mapping["source"]["namespace"]}}}{mapping["source"].get(kind)}']
        ensure(len(matches) == 1, f'unsupported {kind} capability: {element.tag}')
        return matches[0]

    def reference(self, identifier, kind):
        if self.object_uses is None:
            self.object_uses = self.source.object_uses(self.component_id, identifier, kind)
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
        if mapping['native'].get('test_source', {}).get('kind') == 'none':
            # The version-local contract deliberately omits meaningless source
            # singleton Objects. The source dependency remains in provenance.
            ensure(acquisition == {}, 'singleton system source must have no acquisition parameters')
            self.tests[identifier].pop('object')
        return {'test': identifier}

    def same_family(self, identifier, kind, mapping):
        node = self.source.node(self.component_id, identifier, kind)
        ensure(self.capability(node, kind)['capability'] == mapping['capability'], f'{kind} capability mismatch: {identifier}')

    def convert_state(self, element):
        from v04_direct_system_policy import policy_entity
        mapping = self.capability(element, 'state')
        conditions, seen = [], set()
        for child in element:
            field = local_name(child)
            ensure(child.tag.startswith(f'{{{mapping["source"]["namespace"]}}}') and
                   field in mapping['native']['state_field_map'], 'unsupported State field/namespace')
            ensure(field not in seen, 'repeated State field outside bounded proof')
            seen.add(field)
            conditions.append({'fields': {mapping['native']['state_field_map'][field]:
                                          self.predicate(policy_entity(child, mapping), mapping)}})
        return logical_condition(element.get('operator', 'AND'), conditions)

    def convert_object(self, element):
        mapping = self.capability(element, 'object')
        acquisition = {'capability': mapping['capability']}
        if mapping['native'].get('test_source', {}).get('kind') == 'none':
            ensure(not len(element), 'singleton system source cannot have selectors, Sets or Filters')
            return acquisition
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
                if (field in selectors and child.get('operation') == 'case insensitive equals'
                        and 'equals' in acquisition[target]):
                    self.selector_equivalences.append({'source_object': element.get('id'),
                        'source_selector': {'tag': child.tag, 'attributes': dict(child.attrib), 'value': child.text},
                        'native_selector': target,
                        'native_comparator': 'equals', 'reason': 'closed Registry hive domain equality',
                        'source_contract': 'OVAL 5.12.3 EntityObjectRegistryHiveType/EntityItemRegistryHiveType'})
            for path, value in mapping.get('migration_crosswalk', {}).get('materialized_defaults', {}).items():
                ensure(path.startswith('behaviors.'), 'unrecognized acquisition default')
                acquisition[path.split('.')[1]] = value
            if filters:
                acquisition['filters'] = filters
        # Source identity, not payload equality, determines shared acquisitions.
        if self.object_uses[element.get('id')] > 1:
            title = self.object_title(element, mapping)
            identifier = native_identifier(element, 'object', title=title)
            acquisition['object_title'] = title
            self.shared_objects[identifier] = acquisition
            return identifier
        return acquisition

    def object_title(self, element, mapping):
        """Describe source acquisition facts, never infer an unstated purpose."""
        comment = (element.get('comment') or '').strip()
        def words(value):
            return ' '.join(value.lower().replace('.', ' ').replace('_', ' ').replace('-', ' ').split())
        generic = {words(mapping['capability']), words(mapping['capability'] + ' object'),
                   words(mapping['capability'] + ' acquisition'), words(local_name(element))}
        if comment and words(comment) not in generic:
            return comment
        details = []
        described_fields = (mapping['native'].get('selector_map', {}).keys() |
                            mapping['native'].get('collection_parameter_source_map', {}).keys())
        for child in element:
            if local_name(child) in described_fields:
                value = 'from a source Variable' if child.get('var_ref') else repr(child.text or '')
                details.append(f'{local_name(child)} {child.get("operation", "equals")} {value}')
        ensure(details, 'shared acquisition has no source-grounded title')
        return local_name(element).removesuffix('_object').replace('_', ' ').capitalize() + ': ' + '; '.join(details)

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
                acquisition = self.reference(identifier, 'object')
                if isinstance(acquisition, dict):
                    acquisition.pop('capability')  # Inherit down this same-family Set boundary.
                operands.append({'object': acquisition, 'filters': deepcopy(predicates)})
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
            ensure(mapping['native'].get('test_source', {}).get('kind') != 'none',
                   'singleton system source has no approved Variable Object acquisition')
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

    def record_predicate(self, element, mapping):
        """Preserve a complete record before combining its named field results."""
        attributes(element, {'datatype', 'operation', 'entity_check', 'check_existence'})
        ensure(element.get('operation', 'equals') == 'equals', 'unsupported record comparator')
        found = element.get('check_existence', 'at_least_one_exists')
        matching = element.get('entity_check', 'all')
        ensure(found in EXISTENCE and found != 'none_exist' and matching in MATCHING,
               'record absence/quantifier outside bounded source proof')
        ensure(len(element) and not (element.text or '').strip(), 'record requires named fields')
        fields = {}
        for child in element:
            name = child.get('name')
            ensure(child.tag == f'{{{OVAL}}}field' and name and name not in fields
                   and not any('A' <= c <= 'Z' for c in name), 'invalid/duplicate original record field')
            fields[name] = self.predicate(child, mapping, record_field=True)
        # Member lookup is inside this record: missing required members remain
        # errors. Field-value cardinality does not turn lookup failure into an
        # empty successful record, or borrow a value from another record.
        return {'record': {'records_found': EXISTENCE[found], 'records_matching': MATCHING[matching],
                           'fields': fields}}

    def predicate(self, element, mapping, selector=False, *, record_field=False):
        if element.get('datatype') == 'record':
            ensure(not selector and not record_field, 'nested/selector record outside source grammar')
            return self.record_predicate(element, mapping)
        attributes(element, {'datatype', 'operation', 'var_ref', 'var_check'} |
                   ({'name', 'entity_check'} if record_field else set() if selector else {'entity_check', 'check_existence'}))
        ensure(not len(element), 'record/nested entity unsupported')
        existence = element.get('check_existence', 'at_least_one_exists')
        if existence == 'none_exist':
            ensure(not selector and set(element.attrib) == {'check_existence'} and not element.text, 'comparator-bearing absence blocked')
            return {'values_found': 'none'}
        operation = element.get('operation', 'equals')
        ensure(existence in EXISTENCE and operation in COMPARISONS, 'unsupported entity existence/comparator')
        if operation in ('greater than', 'greater than or equal', 'less than or equal'):
            ensure(element.get('datatype') == 'int', 'ordered comparison expansion requires integer source datatype')
        value = self.operand(element)
        crosswalk = mapping['native'].get('selector_value_crosswalk' if selector else 'state_value_crosswalk', {}).get(local_name(element))
        if crosswalk:
            aliases = mapping['migration_crosswalk'][crosswalk]
            if operation != 'equals':
                # Original Object/Item hives are a closed, case-distinct domain.
                # The independent XSD relation proof covers every pair (including
                # the empty error placeholder). Only nonempty literal acquisition
                # selectors are admitted; States and dynamic operands stay strict.
                enumeration = mapping['native'].get('selector_value_enums', {}).get(local_name(element), [])
                domain = {k: v for k, v in aliases.items() if v in enumeration}
                ensure(selector and mapping['capability'] == 'windows.registry' and local_name(element) == 'hive'
                       and operation == 'case insensitive equals' and element.get('datatype', 'string') == 'string'
                       and not element.get('var_ref') and isinstance(value, str) and value in domain
                       and len({k.casefold() for k in domain}) == len(domain)
                       and len(set(domain.values())) == len(domain), 'unsupported enum comparison/value')
                operation = 'equals'
            ensure(isinstance(value, str) and value in aliases, 'unsupported enum comparison/value')
            value = aliases[value]
        if selector:
            field = mapping['native']['selector_map'].get(local_name(element))
            enumeration = mapping['native'].get('selector_value_enums', {}).get(field)
            if enumeration:
                ensure(operation == 'equals', 'unsupported enum selector comparator')
                expected = value if isinstance(value, list) else [value]
                ensure(all(isinstance(v, str) and v in enumeration for v in expected),
                       'enum selector requires known supported values')
        if not selector:
            native_field = mapping['native']['state_field_map'].get(local_name(element))
            enumeration = mapping['native'].get('state_value_enums', {}).get(native_field)
            if enumeration:
                expected = value if isinstance(value, list) else [value]
                ensure(all(isinstance(v, str) and v in enumeration for v in expected),
                       'unsupported enum comparison/value')
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


def dependency_blockers(source, node, mappings):
    """Probe independent obligations even when an earlier sibling failed.

    Uses the same conversion primitives, never a second acceptance grammar.
    Unsupported capability internals remain unidentified, not guessed support.
    """
    from v04_direct_inventory import issue
    problems = []
    component, identifier, kind = node['component'], node['id'], node['kind']
    element = source.node(component, identifier, kind)

    def probe(label, method, *args):
        try:
            method(*args)
        except (UnsupportedSource, ValueError) as error:
            problem = issue(blocker_category(str(error)), str(error), identifier, component)
            problem['source_path'] = label
            problems.append(problem)

    visitor = AssessmentConverter(source, component, mappings)
    probe('closure', visitor.reference, identifier, kind)
    # Quantifier support is independent of which capability failed first.
    if kind == 'test':
        found = element.get('check_existence', 'at_least_one_exists')
        probe('@check_existence', ensure, found in EXISTENCE, f'unsupported Test existence: {found}')
    if kind in ('state', 'object'):
        try:
            mapping = visitor.capability(element, kind)
        except UnsupportedSource:
            return problems
        for number, child in enumerate(element):
            label, name = f'{child.tag}[{number}]', local_name(child)
            if kind == 'state':
                probe(label, visitor.predicate, child, mapping)
            elif name in mapping['native'].get('selector_map', {}):
                probe(label, visitor.predicate, child, mapping, True)
            elif name in mapping['native'].get('collection_parameter_source_map', {}):
                probe(label, visitor.parameter, child)
            if child.tag == '{' + OVAL + '}filter':
                probe(label, visitor.filter, child, mapping)
            if child.tag == '{' + OVAL + '}set':
                for nested in child.iter():
                    if nested.tag == '{' + OVAL + '}set':
                        probe(label, visitor.set_expression, nested, mapping)
                    elif nested.tag == '{' + OVAL + '}filter':
                        probe(label, visitor.filter, nested, mapping)
    if kind == 'variable' and local_name(element) == 'local_variable':
        for child in element.iter():
            if child is not element:
                probe(child.tag, visitor.function, child)
    return problems


def convert_rule(source, source_id, mappings):
    """Convert one entire automated closure; failures leave no emitted artifacts."""
    documents = {}
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
        'purpose': 'assessment', 'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}}
    for section in ('shared_objects', 'variables'):
        if getattr(converter, section):
            assessment[section] = getattr(converter, section)
    assessment.update(tests=converter.tests, evaluate=expression)
    documents[f'authoring/direct-slice/assessments/{assessment_id}.json'] = {'assessment': assessment}
    # This is a compilation fixture, not a full Rule-policy renderer.
    native_rule = {'id': rule_id, 'version': rule.findtext(f'{{{XCCDF}}}version', ''), 'title': title,
        'severity': rule.get('severity', 'unknown'), 'role': 'full', 'weight': float(rule.get('weight', '1')),
        'discussion': rule.findtext(f'{{{XCCDF}}}description', ''), 'rationale': None,
        'extensions': {}, 'warnings': [], 'identifiers': [], 'references': [], 'requires': [], 'conflicts': [],
        'applicability': [], 'parameters': {}, 'remediation': {}, 'organizational_input_requirements': {},
        'assessment_choices': {'automated': {'assessment': assessment_id}}, 'default_assessment_choice': 'automated'}
    documents[f'authoring/direct-slice/rules/{rule_id}.json'] = {'rule': native_rule}
    binding = {'source_rule': source_id, 'source_rule_sha256': digest(xml_identity(rule)),
        'component': component, 'definition': definition, 'native_rule': rule_id, 'assessment': assessment_id,
        'dependencies': converter.used, 'omitted_checks': omitted_checks,
        'source_platforms': [child.get('idref') for child in rule.findall(f'{{{XCCDF}}}platform')]}
    if converter.selector_equivalences:
        binding['selector_equivalences'] = converter.selector_equivalences
    return documents, binding


def convert(source: SourceModel, rule_ids: list[str]):
    """Strict focused API; any unsupported selection fails the entire request."""
    ensure(rule_ids and len(set(rule_ids)) == len(rule_ids), 'distinct source Rules required')
    mappings = load_mappings()
    documents, bindings = {}, []
    for source_id in rule_ids:
        native, binding = convert_rule(source, source_id, mappings)
        documents.update(native)
        bindings.append(binding)
    return assemble_subset(source, documents, bindings, mappings)


def assemble_subset(source, documents, rule_trace, mappings):
    """Project selection only over emitted Rules; an empty subset has no package."""
    rule_ids = [row['source_rule'] for row in rule_trace]
    rule_links = {row['source_rule']: row['native_rule'] for row in rule_trace}
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
        'title': [{'text': '[AUTOMATED PROTOTYPE SUBSET] ' + benchmark.findtext(f'{{{XCCDF}}}title', ''), 'language': 'en'}],
        'description': [{'text': benchmark.findtext(f'{{{XCCDF}}}description', ''), 'language': 'en'}],
        'language': benchmark.get('{http://www.w3.org/XML/1998/namespace}lang'),
        'status': [{'value': child.text, **child.attrib} for child in benchmark.findall(f'{{{XCCDF}}}status')],
        'metadata': {'prototype_subset': True, 'omitted_rule_count': len(source.rules) - len(rule_ids)},
        'notices': [], 'front_matter': [], 'rear_matter': [], 'references': [], 'text_blocks': [],
        'platform': {'id': 'fixture-platform', 'title': 'Compilation fixture; applicability not converted', 'applicability': {}},
        'applicability_catalog': 'fixture-applicability', 'scoring': [], 'parameters': [], 'default_selection': True,
        'groups': [], 'profiles': profiles, 'rules': list(rule_links.values())}
    if rule_ids:
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
                        'behaviors', 'record-level Variables, nested records, record absence and masking',
                        'all_exist', 'other capabilities/functions'],
        'coverage_promoted': False, 'scanner_evaluated': False}
    return documents, trace


def blocker_category(message):
    if 'unresolved' in message or 'cyclic' in message or 'wrong reference kind' in message:
        return 'source-invalid'
    if 'capability' in message:
        return 'unsupported-capability'
    if any(word in message for word in ('check selector', 'OVAL check', 'Profile', 'source default', 'non-OVAL', 'complex-check')):
        return 'unsupported-selection'
    return 'unsupported-construct'


def convert_benchmark(source, *, inventory_only=False, timings=None):
    """Inventory all Rules; isolate expected per-Rule failures and validate admission.

    Native output is atomic per Rule. Diagnostic probes of blocked closures are
    cached per source node; they never produce content or change admission.
    Unexpected programming exceptions and global integrity faults propagate.
    """
    from v04_direct_inventory import SourceInventory, issue, summarize
    started = time.perf_counter()
    inventory = SourceInventory(source)
    rows = inventory.rules()
    inventory_counts = inventory.counts(rows)
    measured = {'inventory': time.perf_counter() - started, 'conversion': 0.0,
                'validation': 0.0, 'diagnostics': 0.0}
    mappings = load_mappings()
    documents, bindings, probes = {}, [], {}
    if not inventory_only:
        from validate_native_json_schemas import build_validators, document_errors
        validators = build_validators(ROOT / 'schema/v0.4.0')
        for row in rows:
            blockers = list(row['inventory_problems'])
            native, binding = {}, None
            started = time.perf_counter()
            try:
                rule = source.rules[row['source_rule']]
                ensure(source.rule_selected(rule), 'disabled source defaults unsupported')
                native, binding = convert_rule(source, row['source_rule'], mappings)
            except (UnsupportedSource, ValueError) as error:
                blockers.append(issue(blocker_category(str(error)), str(error), row['source_rule']))
            measured['conversion'] += time.perf_counter() - started
            started = time.perf_counter()
            if binding is not None:
                for path, document in native.items():
                    kind, = document
                    for error in document_errors(validators[kind + '.schema.json'], document):
                        blockers.append(issue('schema-semantic', f'{path}: {error.message}', row['source_rule']))
            measured['validation'] += time.perf_counter() - started
            started = time.perf_counter()
            if blockers:
                # Probe every dependency, including those beyond the first failed
                # branch. Retain exact node IDs; never swallow unexpected errors.
                for node in row['dependencies']:
                    key = node['component'], node['id']
                    if key not in probes:
                        probes[key] = dependency_blockers(source, node, mappings)
                    blockers.extend(probes[key])
                # Distinct source contexts are kept even when diagnostics repeat.
                row['blockers'] = list({digest(b): b for b in blockers}.values())
                row['primary_blocker'] = row['blockers'][0]
                row['status'] = 'blocked'
            else:
                documents.update(native)
                bindings.append(binding)
                row.update(status='converted', proof_level='authoring_validated', artifacts=sorted(native))
            measured['diagnostics'] += time.perf_counter() - started
    started = time.perf_counter()
    documents, trace = assemble_subset(source, documents, bindings, mappings)
    manifest = {'format': 'direct-benchmark-coverage/1', 'source_zip_sha256': source.zip_sha256,
        'source_xml_sha256': source.xml_sha256, 'source_member': source.member,
        'source_benchmark_component': source.benchmark_component,
        'component_hashes': source.component_hashes, 'mode': 'inventory' if inventory_only else 'automatic',
        'scope': 'Automated subset only; not complete Benchmark, manual, applicability or policy equivalence',
        'proof_contract': 'Conversion emits authoring_validated only. Compilation and independent source proof are separate gates.',
        'blocker_contract': 'All reference/selection inventory problems, conversion/schema diagnostics, dependency-node failures and independent supported entity/function/filter/quantifier obligations. Unsupported capability internals are not interpreted; further blockers may become discoverable only after implementation.',
        'inventory': inventory_counts, 'summary': summarize(rows), 'rules': rows,
        'coverage_promoted': False, 'scanner_evaluated': False}
    measured['assembly'] = time.perf_counter() - started
    if timings is not None:
        timings.update(measured)
    return documents, trace, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--sha256', required=True)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--rule', action='append', help='strict focused selection; repeatable')
    selection.add_argument('--all-rules', action='store_true', help='inventory all, convert supported closures automatically')
    selection.add_argument('--inventory-only', action='store_true', help='discover every Rule without conversion')
    parser.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args()
    ensure(not arguments.output.exists(), 'output exists; refusing overwrite')
    started = time.perf_counter()
    source = SourceModel(arguments.source, arguments.sha256)
    indexed = time.perf_counter()
    manifest = None
    stages = {}
    if arguments.rule:
        documents, trace = convert(source, arguments.rule)
    else:
        documents, trace, manifest = convert_benchmark(source, inventory_only=arguments.inventory_only, timings=stages)
    converted = time.perf_counter()
    from v04_direct_yaml import authoring_yaml
    arguments.output.mkdir(parents=True)
    for relative, document in documents.items():
        target = arguments.output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(document, indent=2) + '\n')
        target.with_suffix('.yaml').write_text(authoring_yaml(document))
    (arguments.output / 'source-trace.json').write_text(json.dumps(trace, indent=2) + '\n')
    if manifest is not None:
        from v04_direct_inventory import coverage_markdown
        (arguments.output / 'coverage.json').write_text(json.dumps(manifest, indent=2) + '\n')
        (arguments.output / 'coverage.md').write_text(coverage_markdown(manifest))
    metrics = {'parse_index': indexed - started, 'conversion': converted - indexed}
    if stages:
        metrics['stages'] = stages
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
