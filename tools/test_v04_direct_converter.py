"""Fresh prototype acceptance: original XML/independent readers, never old output."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
import time
import statistics
import cProfile
import pstats
import io
from unittest.mock import patch

import yaml
from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL, XCCDF, OCIL
from v04_direct_converter import AssessmentConverter, convert, load_mappings
from v04_source_package_semantics import digest, xml_term
from v04_expanded_source_proof import ExpandedSource, ExpandedNative, expanded_compare
from v04_object_contract import object_errors
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors
from audit_v04_eight_assessment_pilot import verify_program
from oval_result_truth_tables import combine_set_flags, SET_FLAGS

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-direct-prototype'
PINS = json.loads((FIXTURE / 'provenance.json').read_text())
X, O = '{' + XCCDF + '}', '{' + OVAL + '}'
D = '{http://scap.nist.gov/schema/scap/source/1.2}'
HREF = '{http://www.w3.org/1999/xlink}href'


def validate_json_files(inputs, report):
    """Public validator API: its directory CLI discovers YAML files only."""
    validators = build_validators(ROOT / 'schema/v0.4.0')
    results = []
    for path in sorted(inputs.rglob('*.json')):
        document = json.loads(path.read_text())
        kind, = document
        errors = list(document_errors(validators[kind + '.schema.json'], document))
        results.append({'path': str(path.relative_to(inputs)), 'kind': kind,
                        'valid': not errors, 'errors': [str(error) for error in errors]})
    assert len(results) == 6 and all(row['valid'] for row in results), results
    report.write_text(json.dumps({'documents_checked': len(results), 'valid': len(results),
                                 'invalid': 0, 'results': results}, indent=2) + '\n')


from audit_v04_direct_benchmark import verify_original


def source_acquisition_terms(reader, identifier):
    """Independent Set/Filter term reader, bounded to Registry unit compositions."""
    element = reader.get(identifier, 'objects')
    set_node = element.find(O + 'set')
    if set_node is not None:
        return {'capability': 'windows.registry', 'set': source_set_terms(reader, set_node)}
    filters = element.findall(O + 'filter')
    copy = deepcopy(element)
    for child in copy.findall(O + 'filter'):
        copy.remove(child)
    original = reader.nodes[identifier]
    reader.nodes[identifier] = copy
    try:
        value = reader.object(identifier)
    finally:
        reader.nodes[identifier] = original
    if filters:
        value['filters'] = [{f.get('action', 'exclude'): reader.state(f.text.strip(), 'windows.registry')} for f in filters]
    return value


def source_set_terms(reader, node):
    filters = [{f.get('action', 'exclude'): reader.state(f.text.strip(), 'windows.registry')} for f in node.findall(O + 'filter')]
    operands = [{'set': source_set_terms(reader, child)} if child.tag == O + 'set' else
                {'object': source_acquisition_terms(reader, child.text.strip()), 'filters': filters}
                for child in node if child.tag in (O + 'set', O + 'object_reference')]
    operation = {'UNION': 'union', 'INTERSECTION': 'intersection', 'COMPLEMENT': 'difference'}[node.get('set_operator', 'UNION')]
    return {'operator': operation, 'operands': operands}


def native_acquisition_terms(reader, node):
    if isinstance(node, str):
        node = reader.a['shared_objects'][node]
    if 'set' in node:
        return {'capability': 'windows.registry', 'set': native_set_terms(reader, node['set'])}
    value = reader.object({k: v for k, v in node.items() if k != 'filters'}, 'windows.registry')
    if node.get('filters'):
        value['filters'] = [{action: reader.filter_condition(condition) for action, condition in f.items()} for f in node['filters']]
    return value


def native_set_terms(reader, node):
    return {'operator': node['operator'], 'operands': [
        {'set': native_set_terms(reader, operand['set'])} if 'set' in operand else
        {'object': native_acquisition_terms(reader, operand['object']),
         'filters': [{action: reader.filter_condition(condition) for action, condition in f.items()} for f in operand['filters']]}
        for operand in node['operands']]}


class DirectConverterAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(FIXTURE / PINS['fixture'], PINS['zip_sha256'])
        cls.documents, cls.trace = convert(cls.source, PINS['rules'])

    def test_original_rules_profile_and_source_closure(self):
        self.assertEqual(len(verify_original(self.source.root, self.documents, self.trace)), 2)
        self.assertEqual(self.source.parse_count, 1)
        self.assertEqual(len(self.trace['omitted_rules']), 289)
        self.assertEqual(len(self.trace['profiles']), 11)
        self.assertTrue(all(len(row['omitted_checks']) == 1 for row in self.trace['rules']))

    def test_public_cli_validator_compiler_and_independent_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            output = directory / 'source'
            command = [sys.executable, str(ROOT / 'tools/v04_direct_converter.py'), str(FIXTURE / PINS['fixture']),
                       '--sha256', PINS['zip_sha256'], '--output', str(output)]
            for identifier in PINS['rules']:
                command.extend(['--rule', identifier])
            process = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            for path, document in self.documents.items():
                self.assertEqual(json.loads((output / path).read_text()), document)
                self.assertEqual(yaml.safe_load((output / path).with_suffix('.yaml').read_text()), document)
            archives = []
            for suffix in ('json', 'yaml'):
                archive = directory / (suffix + '.zip')
                with zipfile.ZipFile(archive, 'w') as package:
                    for path in (output / 'authoring').rglob('*.' + suffix):
                        package.write(path, path.relative_to(output).as_posix())
                archives.append(archive)
                inputs = directory / suffix
                with zipfile.ZipFile(archive) as package:
                    package.extractall(inputs)
                if suffix == 'json':
                    validate_json_files(inputs, directory / 'json-validation.json')
                    continue
                process = subprocess.run([sys.executable, str(ROOT / 'tools/validate_native_json_schemas.py'), str(inputs),
                    '--schema-dir', str(ROOT / 'schema/v0.4.0'), '--report', str(directory / (suffix + '-validation.json'))], capture_output=True, text=True)
                self.assertEqual(process.returncode, 0, process.stderr)
                self.assertEqual(json.loads((directory / 'yaml-validation.json').read_text())['valid'], 6)
            process = subprocess.run([sys.executable, str(ROOT / 'tools/v04_native_bundle_compiler.py'),
                '--json-archive', str(archives[0]), '--yaml-archive', str(archives[1]),
                '--output-dir', str(directory / 'compiled'), '--report', str(directory / 'compilation.json')], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            bundle, = (directory / 'compiled').glob('*.scapng')
            process = subprocess.run([sys.executable, str(ROOT / 'tools/verify_v04_package_consumer.py'), str(bundle),
                '--source-json', str(archives[0]), '--source-yaml', str(archives[1])], capture_output=True, text=True)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(bundle.read_bytes(), build_bundle(self.documents)[0])
            with zipfile.ZipFile(bundle) as package:
                manifest = json.loads(package.read('META-INF/manifest.json'))
                for document in self.documents.values():
                    if 'assessment' in document:
                        assessment = document['assessment']
                        path = manifest['build_provenance']['compiled_programs'][assessment['id']]['path']
                        verify_program(assessment, json.loads(package.read(path)))

    def test_rejects_conditional_and_competing_check_choices(self):
        for mutation in ('conditional-oval', 'nonoval-default', 'nonoval-automated', 'nonoval-other', 'profile-refinement'):
            source = deepcopy(self.source)
            rule = source.rules[PINS['rules'][0]]
            checks = rule.findall(X + 'check')
            if mutation == 'conditional-oval':
                next(c for c in checks if c.get('selector') == 'automated').set('selector', 'conditional')
            elif mutation == 'profile-refinement':
                ET.SubElement(source.benchmark.find(X + 'Profile'), X + 'refine-rule', idref=rule.get('id'), selector='manual')
            else:
                manual = next(c for c in checks if c.get('system') == OCIL)
                manual.set('selector', {'nonoval-default': '', 'nonoval-automated': 'automated', 'nonoval-other': 'custom'}[mutation])
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, PINS['rules'])

    def test_rule_identity_independence_and_stale_trace(self):
        source = deepcopy(self.source)
        source.rules[PINS['rules'][0]].set('id', 'new-independent-rule-identity')
        source.index()
        with self.assertRaisesRegex(AssertionError, 'source Rule identity changed'):
            verify_original(source.root, self.documents, self.trace)
        documents, trace = convert(source, ['new-independent-rule-identity', PINS['rules'][1]])
        self.assertEqual(len(verify_original(source.root, documents, trace)), 2)

    def test_semantically_wrong_valid_authoring_fails_original_comparison(self):
        for mutation in ('selector', 'variable', 'quantifier', 'profile'):
            documents = deepcopy(self.documents)
            assessment = next(doc['assessment'] for doc in documents.values() if 'assessment' in doc and doc['assessment']['id'] == self.trace['rules'][0]['assessment'])
            if mutation in ('selector', 'variable'):
                binding = next(iter(assessment['variables'].values()))['expression']['concat'][1]['regex_capture']['value']['values']
                if mutation == 'selector':
                    binding['object']['name']['equals'] = 'UnrelatedValue'
                else:
                    binding['field'] = 'key'
            elif mutation == 'quantifier':
                next(iter(assessment['tests'].values()))['require']['items_satisfying'] = 'one_or_more'
            else:
                profile = next(p for d in documents.values() if 'benchmark' in d for p in d['benchmark']['profiles'] if p['disabled_rules'])
                profile['disabled_rules'] = []
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                verify_original(self.source.root, documents, self.trace)

    def test_legacy_selector_and_invalid_predicate_fail_public_gates(self):
        for mutation in ('wrapper', 'invalid-predicate'):
            documents = deepcopy(self.documents)
            assessment = next(doc['assessment'] for doc in documents.values() if 'assessment' in doc and doc['assessment'].get('variables'))
            obj = next(iter(assessment['variables'].values()))['expression']['concat'][1]['regex_capture']['value']['values']['object']
            if mutation == 'wrapper':
                obj['select'] = {field: obj.pop(field) for field in ('hive', 'key', 'name')}
            else:
                obj['hive'] = {'equals': 'not-a-reviewed-hive'}
            validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
            self.assertTrue(list(document_errors(validator, {'assessment': assessment})))
            with self.assertRaises(ValueError):
                build_bundle(documents)

    def test_pinned_nested_registry_set_and_synthetic_filter_placement(self):
        # Actual original Object subtree, not another converted Rule. Synthetic
        # filters use the pinned scalar State; this does not promote source coverage.
        identifier = 'oval:mil.disa.stig.win:obj:25342700'
        component = next(c for c, nodes in self.source.nodes.items() if identifier in nodes)
        for operation in ('UNION', 'INTERSECTION', 'COMPLEMENT'):
            source = deepcopy(self.source)
            root_set = source.nodes[component][identifier].find(O + 'set')
            root_set.set('set_operator', operation)
            ET.SubElement(root_set, O + 'filter', action='include').text = 'oval:mil.disa.stig.win:ste:20000001'
            converter = AssessmentConverter(source, component, load_mappings())
            acquisition = converter.reference(identifier, 'object')
            assessment = {'specification': {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}, 'mode': 'automated',
                          'id': 'unit-assessment', 'class': 'compliance', 'purpose': 'assessment',
                          'shared_objects': converter.shared_objects, 'variables': converter.variables, 'tests': {}, 'evaluate': {'test': 'unused-test'}}
            expected = source_acquisition_terms(ExpandedSource(source.components[component]), identifier)
            actual = native_acquisition_terms(ExpandedNative(assessment), acquisition)
            self.assertEqual(expected, actual)
            assessment['tests']['unit-test'] = {'capability': 'windows.registry', 'object': acquisition}
            self.assertFalse(list(object_errors({'assessment': assessment})))
            documents = deepcopy(self.documents)
            target = next(d['assessment'] for d in documents.values() if 'assessment' in d and d['assessment']['id'] == self.trace['rules'][1]['assessment'])
            obj = deepcopy(acquisition)
            if isinstance(obj, dict):
                obj.pop('capability')
            next(iter(target['tests'].values()))['object'] = obj
            if converter.shared_objects:
                target['shared_objects'] = converter.shared_objects
            build_bundle(documents)  # Full schema and compilation of the labeled unit composition.
            # The ordered complement must not be sorted as if it were AND.
            if operation == 'COMPLEMENT':
                actual['set']['operands'].reverse()
                self.assertNotEqual(expected, actual)
        for first in SET_FLAGS:
            for second in SET_FLAGS:
                self.assertIn(combine_set_flags('UNION', first, second), SET_FLAGS)

    def test_component_collision_and_wrong_catalog_never_use_global_ids(self):
        source = deepcopy(self.source)
        row = self.trace['rules'][0]
        other = next(c for c, root in source.components.items() if root.tag == O + 'oval_definitions' and c != row['component'])
        source.components[other].find(O + 'definitions').append(deepcopy(source.nodes[row['component']][row['definition']]))
        source.index()
        documents, trace = convert(source, PINS['rules'])
        self.assertEqual(documents, self.documents)
        verify_original(source.root, documents, trace)
        rule = source.rules[PINS['rules'][0]]
        href = next(c.find(X + 'check-content-ref').get('href') for c in rule.findall(X + 'check') if c.get('system') == OVAL)
        uri = next(n for n in source.checklist.iter() if n.get('name') == href)
        reference = next(identifier for identifier, n in source.references.items() if n.get(HREF) == '#' + other)
        uri.set('uri', '#' + reference)
        source.index()
        with self.assertRaises(UnsupportedSource):
            convert(source, PINS['rules'])

    def test_documented_integer_comparator_extension_is_source_verified(self):
        # Controlled unit mutation, not another published Rule/proof promotion.
        source = deepcopy(self.source)
        row = self.trace['rules'][1]
        state_id = next(i for i, d in row['dependencies'].items() if d['kind'] == 'state')
        state = source.nodes[row['component']][state_id]
        value = next(child for child in state if child.tag.endswith('}value'))
        value.set('operation', 'less than')
        value.text = '2'
        documents, trace = convert(source, PINS['rules'])
        self.assertEqual(len(verify_original(source.root, documents, trace)), 2)
        build_bundle(documents)
        value.set('operation', 'unreviewed comparison')
        with self.assertRaises(UnsupportedSource):
            convert(source, PINS['rules'])

    def test_direct_filters_shared_identity_and_invalid_sets(self):
        identifier = 'oval:mil.disa.stig.win:obj:25342700'
        component = next(c for c, nodes in self.source.nodes.items() if identifier in nodes)
        source = deepcopy(self.source)
        set_node = source.nodes[component][identifier].find(O + 'set')
        leaf_id = 'oval:mil.disa.stig.win:obj:25342703'
        for reference in set_node.findall(O + 'object_reference'):
            reference.text = leaf_id
        leaf = source.nodes[component][leaf_id]
        for action in ('include', 'exclude'):
            ET.SubElement(leaf, O + 'filter', action=action).text = 'oval:mil.disa.stig.win:ste:20000001'
        source.index()
        converter = AssessmentConverter(source, component, load_mappings())
        acquisition = converter.reference(identifier, 'object')
        self.assertEqual(len(converter.shared_objects), 1)
        assessment = deepcopy(next(d['assessment'] for d in self.documents.values() if 'assessment' in d and d['assessment']['id'] == self.trace['rules'][1]['assessment']))
        assessment['shared_objects'] = converter.shared_objects
        expected = source_acquisition_terms(ExpandedSource(source.components[component]), identifier)
        actual = native_acquisition_terms(ExpandedNative(assessment), acquisition)
        self.assertEqual(expected, actual)
        for mutation in ('arity', 'filter-action', 'missing-reference', 'mixed-set'):
            invalid = deepcopy(source)
            node = invalid.nodes[component][identifier].find(O + 'set')
            if mutation == 'arity':
                ET.SubElement(node, O + 'object_reference').text = leaf_id
            elif mutation == 'filter-action':
                invalid.nodes[component][leaf_id].find(O + 'filter').set('action', 'guess')
            elif mutation == 'missing-reference':
                node[0].text = 'unresolved-object'
            else:
                ET.SubElement(node, O + 'set')
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                AssessmentConverter(invalid, component, load_mappings()).reference(identifier, 'object')

    def test_broken_references_cycles_and_blocked_semantics_fail_closed(self):
        component = self.trace['rules'][0]['component']
        dependencies = self.trace['rules'][0]['dependencies']
        for mutation in ('missing-variable', 'cycle', 'all_exist', 'comparator-absence', 'cast'):
            source = deepcopy(self.source)
            nodes = source.nodes[component]
            if mutation == 'all_exist':
                next(nodes[i] for i, d in dependencies.items() if d['kind'] == 'test').set('check_existence', 'all_exist')
            elif mutation in ('comparator-absence', 'cast'):
                state = next(nodes[i] for i, d in dependencies.items() if d['kind'] == 'state')
                if mutation == 'cast':
                    state.find('{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}stdout_line').set('datatype', 'int')
                else:
                    state.find('{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}stderr_line').set('operation', 'equals')
            else:
                variable = next(nodes[i] for i, d in dependencies.items() if d['kind'] == 'variable' and nodes[i].tag == O + 'local_variable')
                if mutation == 'cycle':
                    identifier = variable.get('id')
                    for child in list(variable):
                        variable.remove(child)
                    ET.SubElement(variable, O + 'variable_component', var_ref=identifier)
                else:
                    next(n for n in source.components[component].iter() if n.get('var_ref') == variable.get('id')).set('var_ref', 'missing-variable')
            with self.subTest(mutation=mutation), self.assertRaises(UnsupportedSource):
                convert(source, PINS['rules'])


def measure_sample():
    """One fresh process: first stage call + five warm calls, no timed proof work."""
    stages, hashes, counters = [], [], []
    original_parse, original_fromstring = ET.parse, ET.fromstring
    for _ in range(6):
        counts = {'source_parses': 0, 'shared_gate_xsd_parses': 0}
        def parse_schema(*args, **kwargs):
            counts['shared_gate_xsd_parses'] += 1
            return original_parse(*args, **kwargs)
        def parse_source(*args, **kwargs):
            counts['source_parses'] += 1
            return original_fromstring(*args, **kwargs)
        with patch.object(ET, 'parse', parse_schema), patch.object(ET, 'fromstring', parse_source):
            started = time.perf_counter()
            source = SourceModel(FIXTURE / PINS['fixture'], PINS['zip_sha256'])
            indexed = time.perf_counter()
            documents, trace = convert(source, PINS['rules'])
            converted = time.perf_counter()
            validators = build_validators(ROOT / 'schema/v0.4.0')
            for document in documents.values():
                assert not list(document_errors(validators[next(iter(document)) + '.schema.json'], document))
            validated = time.perf_counter()
            bundle = build_bundle(documents)[0]
            compiled = time.perf_counter()
        stages.append({'parse_index': indexed - started, 'conversion': converted - indexed,
                       'validation': validated - converted, 'compiler_including_preflight': compiled - validated})
        assert counts['source_parses'] == 1
        counters.append(counts)
        hashes.append(sha256(bundle).hexdigest())
    assert len(set(hashes)) == 1
    profiler = cProfile.Profile()
    profiler.runcall(convert, source, PINS['rules'])
    profile_text = io.StringIO()
    pstats.Stats(profiler, stream=profile_text).strip_dirs().sort_stats('cumulative').print_stats(10)
    try:
        import resource
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except ImportError:
        rss = None
    return {'cold': stages[0], 'warm': stages[1:], 'xml_calls': counters,
            'rss_kib_linux': rss, 'profile_conversion': profile_text.getvalue(),
            'bundle_sha256': hashes[0], 'proofs': verify_original(source.root, documents, trace)}


def measure_and_verify(output):
    """Persist reproducible development evidence, not release assets or golden timings."""
    output = Path(output)
    if output.exists():
        raise SystemExit('measurement output already exists')
    output.mkdir(parents=True)
    samples, standalone = [], []
    for number in range(3):
        result = output / f'sample-{number}.json'
        subprocess.run([sys.executable, __file__, '--sample', str(result)], check=True)
        samples.append(json.loads(result.read_text()))
    for number in range(3):
        destination = output / f'authoring-{number}'
        command = [sys.executable, str(ROOT / 'tools/v04_direct_converter.py'), str(FIXTURE / PINS['fixture']),
                   '--sha256', PINS['zip_sha256'], '--output', str(destination)]
        for identifier in PINS['rules']:
            command.extend(['--rule', identifier])
        started = time.perf_counter()
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        files = {str(path.relative_to(destination)): sha256(path.read_bytes()).hexdigest()
                 for path in destination.rglob('*') if path.is_file() and path.name != 'metrics.json'}
        standalone.append({'wall_seconds': time.perf_counter() - started,
                           'metrics': json.loads(process.stdout), 'files': files})
    assert all(row['files'] == standalone[0]['files'] for row in standalone)
    assert len({row['bundle_sha256'] for row in samples}) == 1
    artifacts = output / 'authoring-0'
    for suffix in ('json', 'yaml'):
        archive = output / (suffix + '.zip')
        with zipfile.ZipFile(archive, 'w') as package:
            for path in sorted((artifacts / 'authoring').rglob('*.' + suffix)):
                package.write(path, path.relative_to(artifacts).as_posix())
        inputs = output / suffix
        with zipfile.ZipFile(archive) as package:
            package.extractall(inputs)
        if suffix == 'json':
            validate_json_files(inputs, output / 'json-validation.json')
            continue
        subprocess.run([sys.executable, str(ROOT / 'tools/validate_native_json_schemas.py'), str(inputs),
                        '--schema-dir', str(ROOT / 'schema/v0.4.0'), '--report', str(output / (suffix + '-validation.json'))], check=True, stdout=subprocess.DEVNULL)
        assert json.loads((output / 'yaml-validation.json').read_text())['valid'] == 6
    subprocess.run([sys.executable, str(ROOT / 'tools/v04_native_bundle_compiler.py'),
                    '--json-archive', str(output / 'json.zip'), '--yaml-archive', str(output / 'yaml.zip'),
                    '--output-dir', str(output / 'compiled'), '--report', str(output / 'compile.json')], check=True, stdout=subprocess.DEVNULL)
    bundle, = (output / 'compiled').glob('*.scapng')
    process = subprocess.run([sys.executable, str(ROOT / 'tools/verify_v04_package_consumer.py'), str(bundle),
                              '--source-json', str(output / 'json.zip'), '--source-yaml', str(output / 'yaml.zip')], check=True, capture_output=True, text=True)
    assert sha256(bundle.read_bytes()).hexdigest() == samples[0]['bundle_sha256']
    result = {'samples': samples, 'standalone': standalone,
              'cold_medians_seconds': {key: statistics.median(s['cold'][key] for s in samples) for key in samples[0]['cold']},
              'warm_medians_seconds': {key: statistics.median(row[key] for s in samples for row in s['warm']) for key in samples[0]['cold']},
              'independent_consumer': json.loads(process.stdout), 'source_pins': PINS,
              'method': '3 fresh processes, 1 cold + 5 warm calls each, then 3 fresh standalone processes; sequential; source rebuilt every call; OS scheduling/caches uncontrolled; compiler includes mandatory preflight'}
    (output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--sample':
        Path(sys.argv[2]).write_text(json.dumps(measure_sample(), indent=2) + '\n')
    elif len(sys.argv) == 3 and sys.argv[1] == '--measure':
        measure_and_verify(sys.argv[2])
    else:
        unittest.main()
