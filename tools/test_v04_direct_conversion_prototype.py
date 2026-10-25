#!/usr/bin/env python3
"""Source-backed independent acceptance, mutants and measurement harness (#251)."""
import ast
from copy import deepcopy
import cProfile
import io
import json
from pathlib import Path
import pstats
try:
    import resource
except ImportError:
    resource = None
import statistics
import subprocess
import sys
import tempfile
import time
import unittest
import xml.etree.ElementTree as ET
import zipfile
from unittest.mock import patch
import yaml

from v04_direct_conversion_prototype import Model, convert
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from v04_source_package_semantics import digest, xml_term
from v04_native_bundle_compiler import build_bundle, compile_from_pair
from validate_native_json_schemas import build_validators, document_errors
from verify_v04_package_consumer import verify
from audit_v04_eight_assessment_pilot import verify_program
from test_v04_public_cli_smoke import authoring_archives

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'tests/fixtures/v04-direct-prototype'
META = json.loads((FIX / 'provenance.json').read_text())
X = '{http://checklists.nist.gov/xccdf/1.2}'
DS = '{http://scap.nist.gov/schema/scap/source/1.2}'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
XL = '{http://www.w3.org/1999/xlink}href'


def check(value, reason):
    if not value:
        raise AssertionError(reason)


def independent(root, docs, trace):
    """Different resolver + unchanged source/native proof readers; not a compiler oracle.

    Independently derives checklist catalog scoping, original dependency closure,
    actual Rule/Assessment links and effective ancestor/Profile selection.
    """
    components = {c.attrib['id']: c[0] for c in root.findall(DS + 'component')}
    stream, = root.findall(DS + 'data-stream')
    refs = {c.attrib['id']: c for c in stream.iter(DS + 'component-ref')}
    checklist, = stream.findall(DS + 'checklists/' + DS + 'component-ref')
    benchmark = components[checklist.attrib[XL][1:]]
    parent = {c: n for n in benchmark.iter() for c in n}
    rules = {n.attrib['id']: n for n in benchmark.iter(X + 'Rule')}
    assessments = {d['assessment']['id']: d['assessment'] for d in docs.values() if 'assessment' in d}
    native_rules = {d['rule']['id']: d['rule'] for d in docs.values() if 'rule' in d}
    native_bench, = [d['benchmark'] for d in docs.values() if 'benchmark' in d]
    proofs = []
    for row in trace['rules']:
        check(row['source_rule'] in rules, 'source Rule identity/binding missing')
        rule = rules[row['source_rule']]
        check(digest(xml_term(rule)) == row['source_rule_sha256'], 'source Rule hash divergence')
        source_links = [c for n in rule.findall(X + 'check') if n.get('system') == O[1:-1] for c in n.findall(X + 'check-content-ref')]
        check(len({(c.get('href'), c.get('name')) for c in source_links}) == 1, 'distinct OVAL alternatives')
        link = source_links[0]
        uris = [n for n in checklist.findall('.//{urn:oasis:names:tc:entity:xmlns:xml:catalog}uri') if n.get('name') == link.get('href')]
        check(len(uris) == 1, 'independent href catalog ambiguity')
        component = refs[uris[0].get('uri')[1:]].get(XL)[1:]
        check(component == row['component'] and link.get('name') == row['definition'], 'scoped component/Definition divergence')
        source = ExpandedSource(components[component])
        closure = source.closure(row['definition'])
        check({n['id']: n['sha256'] for n in closure['nodes']} ==
              {i: info['sha256'] for i, info in row['dependencies'].items()}, 'dependency closure/provenance divergence')
        nr = native_rules[row['native_rule']]
        check(nr['assessment_choices']['automated']['assessment'] == row['assessment'], 'Rule/Assessment link divergence')
        result = expanded_compare(source, row['definition'], assessments[row['assessment']])
        check(result['outcome'] == 'PROVED', 'original operand divergence: ' + json.dumps(
            result.get('first_divergence', result.get('unsupported_obligations'))))
        proofs.append({'rule': row['source_rule'], 'outcome': result['outcome'], 'closure_nodes': len(closure['nodes']),
                       'comparison': result})
    for p in benchmark.findall(X + 'Profile'):
        row, = [r for r in trace['profiles'] if r['source_id'] == p.get('id')]
        check(digest(xml_term(p)) == row['source_sha256'], 'source Profile provenance divergence')
        selectors = {c.get('idref'): c.get('selected') == 'true' for c in p.findall(X + 'select')}
        disabled = []
        for r in trace['rules']:
            lineage, n = [], rules[r['source_rule']]
            while n is not benchmark:
                lineage.append(n)
                n = parent[n]
            enabled = all(selectors.get(n.get('id'), n.get('selected', 'true') == 'true') for n in lineage)
            check(row['selected'][r['source_rule']] == enabled, 'Profile trace selection divergence')
            if not enabled:
                disabled.append(r['native_rule'])
        np, = [n for n in native_bench['profiles'] if n['id'] == row['native_id']]
        check(set(np['disabled_rules']) == set(disabled), 'Profile selection divergence: ' + p.get('id'))
    check(set(native_bench['rules']) == set(native_rules), 'Benchmark Rule closure divergence')
    check(native_bench['default_selection'] is True, 'default Rule selection divergence')
    return proofs


class DirectPrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = Model(FIX / META['fixture'], META['zip_sha256'])
        cls.docs, cls.trace = convert(cls.model, META['rules'])

    def assessment(self, docs=None):
        aid = self.trace['rules'][0]['assessment']
        return next(d['assessment'] for d in (docs or self.docs).values() if 'assessment' in d and d['assessment']['id'] == aid)

    def mutable_model(self):
        return deepcopy(self.model)

    def test_complete_pinned_source_single_parse_and_two_independent_proofs(self):
        self.assertEqual(self.model.xml_sha256, '52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440')
        self.assertEqual(self.model.parse_count, 1)
        self.assertEqual(len(self.model.components), 6)
        proofs = independent(self.model.root, self.docs, self.trace)
        self.assertEqual([p['outcome'] for p in proofs], ['PROVED', 'PROVED'])
        self.assertEqual(len(self.trace['omitted_rules']), 289)
        self.assertEqual(len(self.trace['profiles']), 11)
        self.assertFalse(self.trace['coverage_promoted'])

    def test_public_validator_paired_compiler_and_independent_package_process(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            emitted = root / 'emitted'
            command = [sys.executable, str(ROOT / 'tools/v04_direct_conversion_prototype.py'),
                       str(FIX / META['fixture']), '--sha256', META['zip_sha256'], '--output', str(emitted)]
            for rid in META['rules']:
                command.extend(['--rule', rid])
            proto = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(proto.returncode, 0, proto.stderr)
            actual = {p.relative_to(emitted).as_posix(): json.loads(p.read_text()) for p in emitted.rglob('authoring/**/*.json')}
            self.assertEqual(actual, self.docs)
            self.assertEqual(len(list(emitted.rglob('*.yaml'))), len(actual))
            for path, doc in actual.items():
                self.assertEqual(yaml.safe_load((emitted / path).with_suffix('.yaml').read_text()), doc)
            js, ya = authoring_archives(self.docs, root)
            for kind, archive in [('json', js), ('yaml', ya)]:
                directory = root / kind
                with zipfile.ZipFile(archive) as z:
                    z.extractall(directory)
                proc = subprocess.run([sys.executable, str(ROOT / 'tools/validate_native_json_schemas.py'), str(directory),
                    '--schema-dir', str(ROOT / 'schema/v0.4.0'), '--report', str(root / (kind + '-validation.json'))], capture_output=True, text=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            proc = subprocess.run([sys.executable, str(ROOT / 'tools/v04_native_bundle_compiler.py'),
                '--json-archive', str(js), '--yaml-archive', str(ya), '--output-dir', str(root / 'compiled'),
                '--report', str(root / 'compiler.json')], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            package, = (root / 'compiled').glob('*.scapng')
            verifier = subprocess.run([sys.executable, str(ROOT / 'tools/verify_v04_package_consumer.py'), str(package),
                '--source-json', str(js), '--source-yaml', str(ya)], capture_output=True, text=True)
            self.assertEqual(verifier.returncode, 0, verifier.stderr)
            bundles, _ = compile_from_pair(js, ya)
            self.assertEqual(bundles['direct-slice'], package.read_bytes())
            with zipfile.ZipFile(package) as z:
                manifest = json.loads(z.read('META-INF/manifest.json'))
                for row in self.trace['rules']:
                    path = manifest['build_provenance']['compiled_programs'][row['assessment']]['path']
                    program = json.loads(z.read(path))
                    a = next(d['assessment'] for d in self.docs.values() if 'assessment' in d and d['assessment']['id'] == row['assessment'])
                    verify_program(a, program)

    def test_rule_identity_change_is_generic_but_stale_provenance_fails(self):
        model = self.mutable_model()
        old = META['rules'][0]
        model.rules[old].set('id', 'renamed-source-rule-with-same-content')
        model.index()
        with self.assertRaisesRegex(AssertionError, 'source Rule identity/binding missing'):
            independent(model.root, self.docs, self.trace)
        docs, trace = convert(model, ['renamed-source-rule-with-same-content', META['rules'][1]])
        self.assertEqual([p['outcome'] for p in independent(model.root, docs, trace)], ['PROVED', 'PROVED'])

    def test_nested_selector_variable_and_quantifier_mutants_are_not_equivalent(self):
        for mutation in ('registry-selector', 'variable-dependency', 'quantifier'):
            with self.subTest(mutation=mutation):
                docs = deepcopy(self.docs)
                a = self.assessment(docs)
                if mutation == 'quantifier':
                    next(iter(a['tests'].values()))['require']['items_satisfying'] = 'one_or_more'
                else:
                    var = next(iter(a['variables'].values()))
                    binding = var['expression']['concat'][1]['regex_capture']['value']['values']
                    if mutation == 'registry-selector':
                        binding['object']['name']['equals'] = 'DifferentValue'
                    else:
                        binding['field'] = 'key'
                with self.assertRaisesRegex(AssertionError, 'original operand divergence'):
                    independent(self.model.root, docs, self.trace)

    def test_native_profile_selection_mutation_fails_independently(self):
        docs = deepcopy(self.docs)
        b = next(d['benchmark'] for d in docs.values() if 'benchmark' in d)
        profile = next(p for p in b['profiles'] if p['disabled_rules'])
        profile['disabled_rules'] = []
        with self.assertRaisesRegex(AssertionError, 'Profile selection divergence'):
            independent(self.model.root, docs, self.trace)

    def test_legacy_wrapper_rejected_by_unmodified_validator_and_compiler(self):
        docs = deepcopy(self.docs)
        a = self.assessment(docs)
        var = next(iter(a['variables'].values()))
        obj = var['expression']['concat'][1]['regex_capture']['value']['values']['object']
        obj['select'] = {k: obj.pop(k) for k in ('hive', 'key', 'name')}
        v = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']
        errors = list(document_errors(v, {'assessment': a}))
        self.assertTrue(any('expression.concat[1].regex_capture.value.values.object.select' in e.message for e in errors))
        with self.assertRaisesRegex(ValueError, 'obsolete generic Object select wrapper'):
            build_bundle(docs)

    def test_broken_source_reference_cycle_and_all_exist_fail_closed(self):
        for mutation in ('missing-variable', 'cycle', 'all_exist', 'absence-comparison', 'invalid-test-attribute'):
            model = self.mutable_model()
            cid, _ = model.check(model.rules[META['rules'][0]])
            nodes = model.indices[cid]
            dependencies = self.trace['rules'][0]['dependencies']
            if mutation in ('all_exist', 'invalid-test-attribute'):
                n = next(nodes[i] for i, d in dependencies.items() if d['kind'] == 'test')
                if mutation == 'all_exist':
                    n.set('check_existence', 'all_exist')
                    message = 'unsupported Test existence all_exist'
                else:
                    n.set('class', 'not-a-Test-attribute')
                    message = 'shellcommand_test unsupported attributes'
            elif mutation == 'absence-comparison':
                state = next(nodes[i] for i, d in dependencies.items() if d['kind'] == 'state')
                n = next(n for n in state if n.tag.endswith('}stderr_line') and n.get('check_existence') == 'none_exist')
                n.set('operation', 'equals')
                message = 'comparator-bearing absence blocked'
            else:
                n = next(nodes[i] for i, d in dependencies.items() if d['kind'] == 'variable' and nodes[i].tag == O + 'local_variable')
                local_id = n.get('id')
                if mutation == 'cycle':
                    n.clear(); n.tag = O + 'local_variable'; n.attrib.update(id=local_id, datatype='string', version='1')
                    ET.SubElement(n, O + 'variable_component', var_ref=local_id)
                    message = 'cyclic OVAL dependency'
                else:
                    consumer = next(c for c in model.components[cid].iter() if c.get('var_ref') == local_id)
                    consumer.set('var_ref', 'missing-variable')
                    message = 'unresolved component-scoped OVAL dependency missing-variable'
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, message):
                convert(model, META['rules'])

    def test_component_scope_is_not_global_and_catalog_redirect_is_detected(self):
        model = self.mutable_model()
        cid, definition = model.check(model.rules[META['rules'][0]])
        other = next(k for k, n in model.components.items() if n.tag == O + 'oval_definitions' and k != cid)
        defs = model.components[other].find(O + 'definitions')
        collision = deepcopy(model.indices[cid][definition])
        defs.append(collision)
        model.index()
        docs, trace = convert(model, META['rules'])
        self.assertEqual(docs, self.docs)
        independent(model.root, docs, trace)
        href = next(c.get('href') for n in model.rules[META['rules'][0]].findall(X + 'check') if n.get('system') == O[1:-1] for c in n.findall(X + 'check-content-ref'))
        uri = next(n for n in model.checklist.iter() if n.get('name') == href)
        ref = next(k for k, n in model.refs.items() if n.get(XL) == '#' + other)
        uri.set('uri', '#' + ref)
        model.index()
        with self.assertRaisesRegex(AssertionError, 'scoped component/Definition divergence'):
            independent(model.root, self.docs, self.trace)

    def test_pin_invalid_profile_and_benchmark_scope_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'source ZIP SHA-256 mismatch'):
            Model(FIX / META['fixture'], '0' * 64)
        model = self.mutable_model()
        p = model.benchmark.find(X + 'Profile')
        p.find(X + 'select').set('idref', 'missing-group')
        with self.assertRaisesRegex(ValueError, 'unresolved Profile idref'):
            convert(model, META['rules'])
        with self.assertRaisesRegex(ValueError, 'exactly two distinct source Rules required'):
            convert(self.model, META['rules'][:1])

    def test_prototype_has_no_legacy_schema_converter_or_rule_id_dispatch_dependency(self):
        source = (ROOT / 'tools/v04_direct_conversion_prototype.py').read_text()
        self.assertNotIn('scap_upconvert_v003', source)
        self.assertNotIn('schema/v0.3', source)
        self.assertNotIn('SV-', source)
        imports = [n.module for n in ast.walk(ast.parse(source)) if isinstance(n, ast.ImportFrom)]
        self.assertFalse(any(n and n.startswith(('scap_', 'v04_', 'research_')) for n in imports))


def measurement():
    """Stage times in one fresh process; validation/compiler are unmodified.

    Compiler timing includes its own repeated mandatory preflight. RSS is
    process high-water RSS, not a guessed per-stage allocation measurement.
    """
    rows, bundle_hashes = [], []
    xml_counts = []
    original_parse, original_fromstring = ET.parse, ET.fromstring
    for _ in range(6):
        counts = {'source_fromstring_calls': 0, 'shared_validator_xsd_parse_calls': 0}
        def counted_parse(*args, **kwargs):
            counts['shared_validator_xsd_parse_calls'] += 1
            return original_parse(*args, **kwargs)
        def counted_fromstring(*args, **kwargs):
            counts['source_fromstring_calls'] += 1
            return original_fromstring(*args, **kwargs)
        with patch.object(ET, 'parse', counted_parse), patch.object(ET, 'fromstring', counted_fromstring):
            start = time.perf_counter()
            model = Model(FIX / META['fixture'], META['zip_sha256'])
            parse = time.perf_counter() - start
            start = time.perf_counter(); docs, trace = convert(model, META['rules']); conversion = time.perf_counter() - start
            start = time.perf_counter()
            validators = build_validators(ROOT / 'schema/v0.4.0')
            for doc in docs.values():
                errors = list(document_errors(validators[next(iter(doc)) + '.schema.json'], doc))
                check(not errors, 'public schema validation failed: ' + str(errors[:1]))
            validation = time.perf_counter() - start
            start = time.perf_counter(); bundle, _ = build_bundle(docs); compiler = time.perf_counter() - start
        check(counts['source_fromstring_calls'] == 1, 'source was reparsed')
        xml_counts.append(counts)
        bundle_hashes.append(__import__('hashlib').sha256(bundle).hexdigest())
        rows.append({'parse_index': parse, 'conversion': conversion, 'public_validation': validation, 'compiler_including_preflight': compiler})
    check(len(set(bundle_hashes)) == 1, 'repeated compiler byte reproducibility failed')
    profiler = cProfile.Profile(); profiler.enable(); convert(model, META['rules']); profiler.disable()
    stream = io.StringIO(); pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats('cumulative').print_stats(12)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / 'slice.scapng';p.write_bytes(bundle)
        consumer = verify(p)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else None
    return {'cold_process_stage_call': rows[0], 'warm_process_stage_calls': rows[1:],
        'warm_medians': {k: statistics.median(r[k] for r in rows[1:]) for k in rows[0]},
        'rss_high_water_kib_linux': rss,
        'profile_conversion': stream.getvalue(), 'bundle_sha256': __import__('hashlib').sha256(bundle).hexdigest(),
        'independent_package_consumer': consumer, 'independent_original_source': independent(model.root, docs, trace),
        'xml_parse_calls_per_model': model.parse_count, 'component_index_passes_per_model': len(model.indices),
        'source_zip_sha256': model.zip_sha256, 'source_xml_sha256': model.xml_sha256,
        'instrumented_xml_calls_per_iteration': xml_counts,
        'complexity': {'prototype': complexity('v04_direct_conversion_prototype.py'),
                       'production_reference': complexity('scap_converter_core.py'),
                       'qualification': 'Static repository import closure, including deferred imports; excludes stdlib/third-party implementation lines. Production has much broader supported scope. No equal-feature complexity or speedup claim.'},
        'legacy_stage_timing': 'NOT COMPARABLE: production whole-Benchmark SCAP processing versus a bounded two-Rule miniature; no speedup ratio claimed'}


def complexity(entry):
    directory = ROOT / 'tools'
    pending, modules, external = [directory / entry], {}, set()
    while pending:
        p = pending.pop()
        if p in modules:
            continue
        source = p.read_text()
        modules[p] = {'physical_lines': len(source.splitlines()),
                      'nonblank_noncomment_lines': sum(bool(s.strip()) and not s.lstrip().startswith('#') for s in source.splitlines())}
        for n in ast.walk(ast.parse(source)):
            names = []
            if isinstance(n, ast.Import):
                names = [a.name.split('.') for a in n.names]
            elif isinstance(n, ast.ImportFrom):
                base = list(p.parent.relative_to(directory).parts)
                prefix = (base[:len(base) - n.level + 1] if n.level else []) + ((n.module or '').split('.') if n.module else [])
                names = [prefix] + [prefix + [a.name] for a in n.names]
            for parts in names:
                if not parts:
                    continue
                search = [directory, p.parent, directory / 'scap_upconvert_v003', directory / 'scap_ng_roundtrip_v003']
                candidates = [c for base in search for c in (base.joinpath(*parts).with_suffix('.py'), base.joinpath(*parts) / '__init__.py')]
                found = next((c for c in candidates if c.is_file()), None)
                if found:
                    pending.append(found)
                elif not any((base / (parts[0] + '.py')).exists() or (base / parts[0]).is_dir() for base in search) and parts[0] not in sys.stdlib_module_names and parts[0] != '__future__':
                    external.add(parts[0])
    return {'repository_modules': len(modules), 'physical_lines': sum(v['physical_lines'] for v in modules.values()),
            'nonblank_noncomment_lines': sum(v['nonblank_noncomment_lines'] for v in modules.values()),
            'modules': {str(p.relative_to(ROOT)): v for p, v in sorted(modules.items())},
            'external_import_roots': sorted(external)}


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--measure':
        Path(sys.argv[2]).write_text(json.dumps(measurement(), indent=2) + '\n')
    else:
        unittest.main()
