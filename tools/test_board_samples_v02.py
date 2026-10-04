"""Bounded Board-pilot checks, not a collector or general reference scanner.

The checked-in case tables are the oracle. This helper implements only the
operations used by the converter pilot and its supporting examples. It fails
on unsupported forms.
Run directly on Windows or Linux; it does not download or expand any corpus.
"""
from pathlib import Path
import copy
import hashlib
import itertools
import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assessment_expression import AssessmentExpressionEvaluator, ContentError, load_assessments
from assessment_results_v02 import item_validator, validate_result_set
from check_current_authoring_contract import violations
from validate_native_json_schemas import build_validators, document_errors
from validate_generated_capability_semantics import validate_assessment_capability_semantics
from oval_result_truth_tables import (
    aggregate_check, aggregate_operator, aggregate_existence,
    evaluate_collected_object_test, apply_filter_state_result, combine_set_flags,
    evaluate_record_field, evaluate_record_entity,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'board/review-content/0.2.0'
EXISTENCE = dict(all='all_exist', some='at_least_one_exists', none='none_exist', one='only_one_exists', optional='any_exist')
CHECK = dict(all='all', any='at least one', one='only one', none='none satisfy')
OPERATOR = dict(all='AND', any='OR', one='ONE', odd='XOR')

def normalized(outcome):
    return outcome.replace(' ', '_')

def merged(source, variant):
    out = copy.deepcopy(source)
    for section, nodes in variant.items():
        for name, fields in nodes.items():
            current = out.setdefault(section, {}).get(name, {})
            if 'kind' in fields and fields['kind'] != current.get('kind'):
                out[section][name] = copy.deepcopy(fields)
            else:
                out[section][name] = {**current, **copy.deepcopy(fields)}
                if current.get('kind') == 'constant' and 'value' in fields:
                    out[section][name].pop('expression', None)
    return out

def validate_pilot_dataflow(source):
    """Test-only graph guard for the settled acyclic local dataflow requirement.

    Core capability validation currently misses local Variable cycles. This
    independent guard keeps the Board fixtures safe without modifying it.
    Diagnostic names here are pilot-local, not new normative reason codes.
    """
    nodes = {(kind, name):node for section, kind in (('objects','object'), ('variables','variable'), ('states','state'), ('tests','test'))
             for name, node in source.get(section, {}).items()}
    def references(value):
        if isinstance(value, list):
            for child in value: yield from references(child)
        elif isinstance(value, dict):
            for key, child in value.items():
                if key in ('object', 'variable', 'state') and isinstance(child, str):
                    yield (key, child)
                elif key == 'states' and isinstance(child, list):
                    for name in child: yield ('state', name)
                else:
                    yield from references(child)
    edges = {node:set(references(payload)) for node, payload in nodes.items()}
    active, done = [], set()
    def visit(node):
        if node in active:
            raise ContentError('pilot.dataflow_cycle', ' -> '.join('/'.join(n) for n in [*active, node]))
        if node not in nodes:
            raise ContentError('pilot.dataflow_missing_reference', '/'.join(node))
        if node in done: return
        active.append(node)
        for target in edges[node]: visit(target)
        active.pop(); done.add(node)
    for node in nodes: visit(node)

class PilotModel:
    """Evaluate supplied synthetic selected Items, never acquire resources.

    Acquisition/selector execution is deliberately outside this model. Native
    Sets do combine the supplied leaf Object populations. Variable resolution
    and scalar State comparisons are performed here, not supplied as oracles.
    """
    def __init__(self, sources, inputs):
        self.sources, self.inputs = sources, inputs
        self.variables, self.objects, self.comparisons = {}, {}, []
        self.test_results = {}
        self.record_results = []

    def input(self, identity):
        if identity == 'board.dependency':
            return self.inputs
        return self.inputs.get('dependencies', {}).get(identity, self.inputs)

    def variable(self, identity, name):
        key = (identity, name)
        if key in self.variables:
            return self.variables[key]
        source = self.sources[identity]['variables'][name]
        if source['kind'] == 'constant':
            value = source['value'] if 'value' in source else source['expression']['literal']
            result = ('complete', value if isinstance(value, list) else [value])
        elif source['kind'] == 'external':
            record = self.input(identity)['variables'][name]
            result = (record['status'], record['values'])
            if result[0] == 'complete' and any(type(v) is not bool for v in result[1]):
                raise ValueError('Pilot external Boolean binding is invalid')
        elif source['kind'] == 'local':
            expression = source['expression']
            if set(expression) == {'values'}:
                reference = expression['values']
                record = self.object(identity, reference['object'])
                if record['flag'] in ('complete', 'does not exist'):
                    extracted = []
                    for item in record['items']:
                        value = item['fields'][reference['field']]
                        if value.get('status', 'exists') != 'exists' or 'value' not in value:
                            raise ValueError('Unsupported pilot extraction entity status')
                        extracted.append(value['value'])
                    result = ('complete', extracted)
                else:
                    result = ('error' if record['flag'] == 'error' else 'unknown', [])
            elif set(expression) == {'concat'}:
                args = [self.variable(identity, x['variable']) for x in expression['concat']]
                failure = next((status for status, _ in args if status != 'complete'), None)
                result = (failure, []) if failure else ('complete', [''.join(values) for values in itertools.product(*(v for _, v in args))])
            elif set(expression) == {'variable'}:
                result = self.variable(identity, expression['variable'])
            elif set(expression) == {'arithmetic'}:
                arithmetic = expression['arithmetic']
                if arithmetic['operation'] != 'add':
                    raise ValueError('Only pilot arithmetic addition is modeled')
                args = [self.variable(identity, x['variable']) for x in arithmetic['operands']]
                failure = next((status for status, _ in args if status != 'complete'), None)
                result = (failure, []) if failure else ('complete', [sum(values) for values in itertools.product(*(v for _, v in args))])
            else:
                raise ValueError('Unsupported pilot Variable function')
        else:
            raise ValueError('Unsupported pilot Variable kind')
        self.variables[key] = result
        return result

    def state(self, identity, predicate, item):
        if 'all' in predicate:
            return aggregate_operator('AND', [self.state(identity, p, item) for p in predicate['all']])
        if 'record' in predicate:
            return self.record_state(identity, predicate, item)
        field = predicate['field']
        observed = item['fields'].get(field, {'status': 'does_not_exist'})
        values = observed if isinstance(observed, list) else [observed]
        counts = dict(exists=0, does_not_exist=0, error=0, not_collected=0)
        for value in values:
            status = value.get('status', 'exists')
            if status in ('exists', 'complete'):
                counts['exists'] += 1
            elif status in counts:
                counts[status] += 1
            else:
                raise ValueError('Unsupported pilot entity status: ' + status)
        existence = aggregate_existence(EXISTENCE[predicate['existence']], **counts)
        if existence != 'true':
            return existence
        expected = predicate['value']
        if isinstance(expected, dict):
            status, expectations = self.variable(identity, expected['variable'])
            if status != 'complete':
                return status.replace('_', ' ')
            if not expectations:
                return 'error'
        else:
            expectations = [expected]
        rows = []
        for value in values:
            if value.get('status', 'exists') == 'error':
                rows.append('error'); continue
            if value.get('status', 'exists') == 'not_collected':
                rows.append('unknown'); continue
            if value.get('status', 'exists') == 'does_not_exist':
                continue
            if value.get('redacted') or 'value' not in value or value['datatype'] != predicate['datatype']:
                rows.append('error'); continue
            comparisons = []
            for expected_value in expectations:
                observed_value, operation = value['value'], predicate['operation']
                if operation == 'equal':
                    match = observed_value == expected_value
                elif operation == 'equal_ci':
                    match = observed_value.lower() == expected_value.lower()
                elif operation == 'greater_than':
                    match = observed_value > expected_value
                elif operation == 'greater_or_equal':
                    match = observed_value >= expected_value
                elif operation == 'match':
                    # Selected source pattern is simple literal alternatives;
                    # this is not a general OVAL/POSIX regex conformance claim.
                    match = re.search(expected_value, observed_value) is not None
                else:
                    raise ValueError('Unsupported pilot comparison: ' + operation)
                comparisons.append('true' if match else 'false')
                self.comparisons.append(dict(assessment=identity, item=item['id'], field=field, observed=observed_value, expected=expected_value, operation=operation, outcome=comparisons[-1]))
            rows.append(aggregate_check(CHECK[predicate.get('variable_match', 'all')], comparisons))
        return aggregate_check(CHECK[predicate['match']], rows)

    def record_state(self, identity, predicate, item):
        """Keep fields correlated within each supplied record entity.

        Missing expected fields follow inherited OVAL EntityStateFieldType:
        error, rather than a false scalar existence predicate. This helper
        models only the selected WMI State; acquisition remains untested.
        """
        field, requirements = predicate['field'], predicate['record']
        records = item['fields'].get(field, [])
        records = records if isinstance(records, list) else [records]
        counts = dict(exists=0, does_not_exist=0, error=0, not_collected=0)
        for record in records:
            counts[record.get('status', 'exists')] += 1
        existence = aggregate_existence(EXISTENCE[requirements['existence']], **counts)
        if existence != 'true':
            return existence
        outcomes = []
        for index, record in enumerate(records):
            status = record.get('status', 'exists')
            if status == 'does_not_exist':
                continue
            if status in ('error', 'not_collected'):
                outcome = 'error' if status == 'error' else 'unknown'
            elif record.get('datatype') != 'record' or 'value' not in record:
                outcome = 'error'
            else:
                fields = record['value']
                results = []
                for name, comparison in requirements['fields'].items():
                    if name not in fields:
                        results.append(evaluate_record_field(name, []))
                    else:
                        nested_item = {**item, 'fields': {name: fields[name]}}
                        start = len(self.comparisons)
                        results.append(self.state(identity, {'field': name, **comparison}, nested_item))
                        for row in self.comparisons[start:]:
                            row['record_index'] = index
                outcome = evaluate_record_entity(results)
            outcomes.append(outcome)
            self.record_results.append(dict(assessment=identity, item=item['id'], field=field,
                                            record_index=index, outcome=outcome))
        return aggregate_check(CHECK[requirements['match']], outcomes)

    def object(self, identity, name):
        key = (identity, name)
        if key in self.objects:
            return self.objects[key]
        source = self.sources[identity]['objects'][name]
        if 'set' not in source:
            record = copy.deepcopy(self.input(identity)['objects'][name])
        else:
            record = self.selection(identity, source['set'])
        self.objects[key] = record
        return record

    def selection(self, identity, expression):
        operator = expression['operator']
        if operator not in ('union', 'intersection'):
            raise ValueError('Only pilot union and intersection are modeled')
        selected_records = []
        for operand in expression['operands']:
            selected = self.selection(identity, operand['set']) if 'set' in operand else copy.deepcopy(self.object(identity, operand['object']))
            for flt in operand.get('filters', []):
                kept = []
                for item in selected['items']:
                    state = self.sources[identity]['states'][flt['state']]['state']
                    decision = apply_filter_state_result(flt['action'], self.state(identity, state, item))
                    if decision == 'error':
                        selected = {'flag': 'error', 'items': []}; break
                    if decision:
                        kept.append(item)
                else:
                    selected['items'] = kept
            selected_records.append(selected)
        first, *rest = selected_records
        flag = first['flag']; items = {item['id']:item for item in first['items']}
        for selected in rest:
            flag = combine_set_flags(operator.upper(), flag, selected['flag'])
            right = {item['id']:item for item in selected['items']}
            items = {**items, **right} if operator == 'union' else {key:items[key] for key in items.keys() & right.keys()}
        return {'flag':flag, 'items':list(items.values())}

    def test(self, identity, name, context):
        source = self.sources[identity]['tests'][name]
        if source['capability'] == 'variable.value':
            variable_name = source['variable']
            status, values = self.variable(identity, variable_name)
            if status != 'complete':
                return normalized(status)
            if not values:
                return 'error'
            datatype = self.sources[identity]['variables'][variable_name]['datatype']
            record = {'flag': 'complete', 'items': [{'id': 'variable-' + variable_name, 'status': 'exists', 'fields': {'value': [{'datatype': datatype, 'value': v} for v in values]}}]}
        elif source['capability'] == 'independent.family':
            inputs = self.input(identity)
            if 'provider_status' in inputs:
                # Synthetic Test-provider lifecycle injection, not acquisition
                # evidence or an invented collected-object status.
                return inputs['provider_status']
            record = {'flag': inputs.get('system_flag', 'complete'), 'items': inputs.get('system_items', [])}
        else:
            record = self.object(identity, source['object'])
        results = []
        for item in record['items']:
            states = [self.state(identity, self.sources[identity]['states'][s]['state'], item) for s in source.get('states', [])]
            if states:
                results.append(aggregate_operator(OPERATOR[source.get('states_match', 'all')], states))
        return normalized(evaluate_collected_object_test(record['flag'], existence=EXISTENCE[source['check_existence']], check=CHECK[source['check']], item_results=results, has_state=bool(source.get('states')), exists=len(record['items'])))

def run_case(sources, name, case):
    sources = copy.deepcopy(sources)
    identity = 'board.' + name
    sources[identity] = merged(sources[identity], case['input'].get('variant', {}))
    validate_pilot_dataflow(sources[identity])
    model = PilotModel(sources, case['input'])
    def evaluate(identity, name, context):
        outcome = model.test(identity, name, context)
        model.test_results[f'{identity}:{name}'] = outcome
        return outcome
    result = AssessmentExpressionEvaluator(sources).run(identity, evaluate, target='synthetic-board-target')
    return result, model

class BoardSamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_assessments(PACKAGE / 'content')
        cls.manifest = json.loads((PACKAGE / 'manifest.json').read_text())
        cls.entries = cls.manifest['samples'] + cls.manifest.get('supporting_examples', [])

    def test_strict_schemas_semantics_and_source_presentation(self):
        validator = build_validators(ROOT / 'schema/v0.2.0')['assessment.schema.json']
        for name, source in self.sources.items():
            with self.subTest(name=name):
                doc = {'assessment': source}
                self.assertEqual(list(document_errors(validator, doc)), [])
                self.assertEqual(validate_assessment_capability_semantics(doc), [])
                self.assertEqual(violations(doc), [])
                validate_pilot_dataflow(source)
        for sample in self.entries:
            table = json.loads((PACKAGE/sample['expected']).read_text())
            for case in table['cases']:
                source = merged(self.sources['board.'+sample['name']], case['input'].get('variant', {}))
                with self.subTest(variant=case['id'], sample=sample['name']):
                    self.assertEqual(list(document_errors(validator, {'assessment':source})), [])
                    self.assertEqual(validate_assessment_capability_semantics({'assessment':source}), [])
        AssessmentExpressionEvaluator(self.sources)

    def test_independent_known_results_and_scheduling(self):
        count = 0
        for sample in self.entries:
            table = json.loads((PACKAGE / sample['expected']).read_text())
            for case in table['cases']:
                with self.subTest(sample=sample['name'], case=case['id']):
                    self.assertTrue(case['synthetic']); self.assertTrue(case['rationale'])
                    result, model = run_case(self.sources, sample['name'], case)
                    self.assertEqual(result['outcome'], case['expected']['outcome'])
                    self.assertEqual(model.test_results, case['expected']['test_outcomes'])
                    for variable, values in case['expected'].get('resolved_variables', {}).items():
                        self.assertEqual(model.variables[('board.'+sample['name'], variable)][1], values)
                    if 'record_outcomes' in case['expected']:
                        self.assertEqual([row['outcome'] for row in model.record_results], case['expected']['record_outcomes'])
                    if 'executed_tests' in case['expected']:
                        self.assertEqual(result['executed_tests'], case['expected']['executed_tests'])
                        self.assertEqual(len(result['invocations']) - 1, case['expected']['dependency_invocations'])
                        reused = sum(t['kind'] == 'dependency' and t['reused'] for t in result['trace'])
                        self.assertEqual(reused, case['expected']['reused_references'])
                    # Supplied Items are genuine 0.2.0 typed Item shapes, with
                    # explicit synthetic provenance; there is no live evidence.
                    inputs = [case['input'], *case['input'].get('dependencies', {}).values()]
                    for record in inputs:
                        items = list(record.get('system_items', []))
                        for obj in record.get('objects', {}).values(): items.extend(obj['items'])
                        for item in items: item_validator(item['capability']).validate(item)
                    count += 1
        self.assertEqual(count, 48)

    def test_variable_multivalues_are_not_independent_items(self):
        case = json.loads((PACKAGE/'expected/concat.json').read_text())['cases'][1]
        result, model = run_case(self.sources, 'concat', case)
        self.assertEqual(result['outcome'], 'false')
        self.assertEqual(model.variables[('board.concat','combined-values')][1], ['abc123','abc456','xyz123','xyz456'])

    def test_inventory_and_pinned_extract_hashes(self):
        self.assertEqual(len(self.manifest['samples']), 6)
        self.assertEqual(len(self.manifest['supporting_examples']), 4)
        for sample in self.entries:
            self.assertEqual(sample['human_review_status'], 'pending-review')
            for key in ('assessment','expected','provenance','explanation'):
                self.assertTrue((PACKAGE/sample[key]).is_file(), sample[key])
            for key in ('assessment','expected'):
                self.assertEqual(hashlib.sha256((PACKAGE/sample[key]).read_bytes()).hexdigest(), sample[key+'_sha256'])
            provenance = json.loads((PACKAGE/sample['provenance']).read_text())
            if 'revision' in provenance:
                self.assertEqual(provenance['revision'], 'e3538595c5083b9c34d937a81d319234df9bbfaa')
                data = (PACKAGE/sample['source_extract']).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), provenance['extract_sha256'])
                root = ET.fromstring(data)
                ids = {n.get('id') for n in root.iter() if n.get('id')}
                self.assertEqual(ids, {n['id'] for n in provenance['source_nodes']})

    def test_selected_source_conversion_roundtrips(self):
        from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
        from scap_ng_roundtrip_v003.native_assessment_to_oval import build
        from scap_ng_roundtrip_v003.compare_oval_semantics import compare
        for sample in self.entries:
            if sample['origin'] not in ('converted', 'manual-source-transcription'): continue
            with self.subTest(sample=sample['name']), tempfile.TemporaryDirectory() as temp:
                path = PACKAGE/sample['source_extract']
                root = ET.parse(path).getroot()
                lowered, error = lower_definition(root, sample['source_definition'], 'source-roundtrip', collection_graph=True)
                self.assertIsNone(error)
                tree, regenerated_id = build(lowered)
                reverse = Path(temp)/'reverse.xml'; tree.write(reverse, encoding='utf-8')
                parity = compare(path, reverse, sample['source_definition'], regenerated_id, root_only=True)
                self.assertTrue(parity['equal'], parity)
        # Intermediate parity is one gate, not scanner equivalence. The
        # companion conversion tests also reproduce strict native output.

    def test_selected_source_extracts_are_schema_valid(self):
        from lxml import etree
        schema = etree.XMLSchema(etree.parse(str(ROOT/'third_party/scap-1.4-schemas/omni-schema.xsd')))
        for path in (PACKAGE/'sources').glob('*.xml'):
            with self.subTest(source=path.name):
                schema.assertValid(etree.parse(str(path)))

    def test_source_comparison_crosswalks_match_source(self):
        from capability_registry import load_mapping
        from scap_upconvert_v003.native_capability_mapping import COMMON_CROSSWALK
        def scalar(text, datatype):
            return int(text) if datatype == 'int' else text
        for sample in self.entries:
            if sample['origin'] not in ('converted', 'manual-source-transcription'): continue
            source = ET.parse(PACKAGE/sample['source_extract']).getroot()
            nodes = {n.get('id'):n for n in source.iter() if n.get('id')}
            provenance = json.loads((PACKAGE/sample['provenance']).read_text())
            native = self.sources[sample['assessment_id']]
            bindings = provenance['native_bindings']
            for ident, node in nodes.items():
                kind = node.tag.rsplit('}', 1)[-1]
                if kind.endswith('_test'):
                    test = native['tests'][bindings[ident].split('/')[1]]
                    self.assertEqual(test['check_existence'], COMMON_CROSSWALK['existence'][node.get('check_existence', 'all_exist')])
                    self.assertEqual(test['check'], COMMON_CROSSWALK['check'][node.get('check')])
                elif kind.endswith('_state'):
                    state = native['states'][bindings[ident].split('/')[1]]
                    mapping = load_mapping(state['capability'], '0.2.0')
                    body = state['state']; predicates = body.get('all', [body])
                    fields = {p['field']:p for p in predicates}
                    for entity in node:
                        name = entity.tag.rsplit('}', 1)[-1]
                        predicate = fields[mapping['native']['state_field_map'][name]]
                        if 'record' in predicate:
                            self.assertEqual(predicate['record']['match'], COMMON_CROSSWALK['check'][entity.get('entity_check', 'all')])
                            for field in entity:
                                actual = predicate['record']['fields'][field.get('name')]
                                self.assertEqual(actual['operation'], COMMON_CROSSWALK['operation'][field.get('operation', 'equals')])
                                self.assertEqual(actual['value'], scalar(field.text, field.get('datatype', 'string')))
                                self.assertEqual(actual['match'], COMMON_CROSSWALK['check'][field.get('entity_check', 'all')])
                            continue
                        self.assertEqual(predicate['operation'], COMMON_CROSSWALK['operation'][entity.get('operation', 'equals')])
                        self.assertEqual(predicate['match'], COMMON_CROSSWALK['check'][entity.get('entity_check', 'all')])
                        self.assertEqual(predicate['existence'], COMMON_CROSSWALK['existence'][entity.get('check_existence', 'at_least_one_exists')])
                        if entity.get('var_ref'):
                            self.assertEqual(predicate['value'], {'variable':bindings[entity.get('var_ref')].split('/')[1]})
                            self.assertEqual(predicate['variable_match'], COMMON_CROSSWALK['check'][entity.get('var_check', 'all')])
                        else:
                            value = scalar(entity.text, entity.get('datatype', 'string'))
                            if name == 'hive': value = mapping['migration_crosswalk']['hive'][value]
                            self.assertEqual(predicate['value'], value)
                elif kind == 'constant_variable':
                    variable = native['variables'][bindings[ident].split('/')[1]]
                    values = [scalar(v.text, node.get('datatype')) for v in node]
                    actual = variable['value']; actual = actual if isinstance(actual, list) else [actual]
                    self.assertEqual(actual, values)

    def test_invalid_reference_and_literal(self):
        missing = copy.deepcopy(self.sources)
        missing['board.dependency']['evaluate']['else'] = {'test':'test-missing'}
        with self.assertRaises(ContentError): AssessmentExpressionEvaluator(missing)
        doc = {'assessment':copy.deepcopy(self.sources['board.constants'])}
        doc['assessment']['states']['equals-nine']['state']['value'] = '9'
        diagnostics = validate_assessment_capability_semantics(doc)
        self.assertTrue(any(row['code'] == 'assessment.native_literal_datatype' for row in diagnostics), diagnostics)

    def test_linked_expected_evidence(self):
        document = json.loads((PACKAGE/'expected/unix-file.result-set.json').read_text())
        validate_result_set(document, self.sources)
        row = document['assessment_results'][0]['assessment_result']
        self.assertEqual(row['outcome'], 'true')
        comparison = row['tests'][0]['per_item_results'][0]['state_results'][0]['entity_results'][0]['comparison_results'][0]
        self.assertEqual(comparison['item_value']['value'], comparison['expected_value']['value'])
        self.assertTrue(row['population_complete'])

    def test_minimal_source_datatype_disagreement_is_preserved(self):
        path = ROOT/'tests/focused-regressions/board-pilot/binary-source.xml'
        root = ET.parse(path).getroot()
        variable = next(n for n in root.iter() if n.get('id') == 'oval:org.mitre.oval.test:var:945')
        state = next(n for n in root.iter() if n.get('id') == 'oval:org.mitre.oval.test:ste:266')
        self.assertEqual(variable.get('datatype'), 'binary')
        self.assertEqual(variable[0].text, 'true')
        self.assertIsNone(re.fullmatch(r'(?:[0-9a-fA-F]{2})*', variable[0].text))
        self.assertEqual(state[0].get('datatype'), 'boolean')
        self.assertEqual(state[0].text, 'true')

    def test_strict_converter_gap_is_rejected(self):
        from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
        from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary
        from scap_upconvert_v003.native_capability_mapping import apply_ready_capability_mappings
        root = ET.parse(ROOT/'tests/focused-regressions/board-pilot/constant-source.xml').getroot()
        lowered, error = lower_definition(root, 'oval:org.mitre.oval.test:def:92', 'converter-gap', collection_graph=True)
        self.assertIsNone(error)
        native = apply_ready_capability_mappings(align_assessment_vocabulary(lowered), ROOT/'schema/v0.2.0/capability-mappings/supported')
        native['assessment']['specification']['version'] = '0.2.0'
        validator = build_validators(ROOT/'schema/v0.2.0')['assessment.schema.json']
        errors = list(document_errors(validator, native))
        self.assertTrue(any('Unknown 0.2.0 capability: independent.variable' in e.message for e in errors), errors)

    def test_local_variable_cycle_validator_gap_is_visible(self):
        import yaml
        document = yaml.safe_load((ROOT/'tests/focused-regressions/board-pilot/variable-cycle.assessment.yaml').read_text())
        source = document['assessment']
        validator = build_validators(ROOT/'schema/v0.2.0')['assessment.schema.json']
        self.assertEqual(list(document_errors(validator, document)), [])
        # Known gap, not acceptance: schemas cannot express the acyclic rule,
        # and current core capability semantics return no diagnostic for it.
        self.assertEqual(validate_assessment_capability_semantics(document), [])
        with self.assertRaisesRegex(ContentError, 'pilot.dataflow_cycle'):
            validate_pilot_dataflow(source)

if __name__ == '__main__':
    import argparse
    import subprocess
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='Write a validation receipt; never overwrite an oracle')
    args, remaining = parser.parse_known_args()
    result = unittest.main(argv=[sys.argv[0], *remaining], exit=False).result
    if args.report:
        commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        report = dict(source_commit=commit, status='passed' if result.wasSuccessful() else 'failed', tests_run=result.testsRun,
                      tracked_worktree_clean=subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--'], cwd=ROOT).returncode == 0,
                      sample_count=6, supporting_examples=4, independent_semantic_cases=48,
                      primary_semantic_cases=31, supporting_semantic_cases=17, converted_source_roundtrips=6,
                      supporting_manual_source_roundtrips=2,
                      source_extracts_xsd_validated=8, minimal_reproducers=4,
                      source_revision='e3538595c5083b9c34d937a81d319234df9bbfaa',
                      human_review_status='pending-review', live_collectors_run=False,
                      scanner_equivalence_claimed=False, niwc_65_corpus_run=False)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    raise SystemExit(not result.wasSuccessful())
