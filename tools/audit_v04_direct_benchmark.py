"""Independent acceptance gates for the fresh converter; no lowering is reused."""
from hashlib import sha256
import io
import json
from pathlib import Path
import zipfile
import subprocess
import sys
import time
import statistics

from v04_direct_scap_source import OVAL, XCCDF, OCIL
from v04_source_package_semantics import Source, digest, xml_term
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from audit_v04_eight_assessment_pilot import verify_program

X = '{' + XCCDF + '}'
D = '{http://scap.nist.gov/schema/scap/source/1.2}'
HREF = '{http://www.w3.org/1999/xlink}href'


def verify_original(root, documents, trace, *, require_proof=True):
    """Independent XCCDF resolver plus unmodified original/native operand readers."""
    components = {node.get('id'): node[0] for node in root.findall(D + 'component')}
    stream, = root.findall(D + 'data-stream')
    references = {node.get('id'): node for node in stream.iter(D + 'component-ref')}
    checklist, = stream.findall(D + 'checklists/' + D + 'component-ref')
    benchmark = components[checklist.get(HREF)[1:]]
    parents = {child: parent for parent in benchmark.iter() for child in parent}
    rules = {rule.get('id'): rule for rule in benchmark.iter(X + 'Rule')}
    native_rules = {doc['rule']['id']: doc['rule'] for doc in documents.values() if 'rule' in doc}
    assessments = {doc['assessment']['id']: doc['assessment'] for doc in documents.values() if 'assessment' in doc}
    native_benchmark, = [doc['benchmark'] for doc in documents.values() if 'benchmark' in doc]
    outcomes = []
    for binding in trace['rules']:
        assert binding['source_rule'] in rules, 'source Rule identity changed'
        rule = rules[binding['source_rule']]
        assert digest(xml_term(rule)) == binding['source_rule_sha256'], 'source Rule provenance changed'
        checks = rule.findall(X + 'check')
        defaults = [check for check in checks if not check.get('selector')]
        assert len(defaults) == 1 and defaults[0].get('system') == OVAL, 'competing default check'
        selected = []
        omitted = []
        for check in checks:
            if check.get('system') == OVAL:
                assert check.get('selector', '') in ('', 'automated'), 'conditional OVAL selector'
                reference, = check.findall(X + 'check-content-ref')
                selected.append((reference.get('href'), reference.get('name')))
            else:
                assert (check.get('system'), check.get('selector')) == (OCIL, 'manual'), 'competing non-OVAL alternative'
                omitted.append({'system': OCIL, 'selector': 'manual', 'sha256': digest(xml_term(check))})
        assert len(set(selected)) == 1 and omitted == binding['omitted_checks'], 'unreported check alternative'
        href, definition = selected[0]
        uri, = [node for node in checklist.iter() if node.get('name') == href and node.tag.endswith('}uri')]
        component = references[uri.get('uri')[1:]].get(HREF)[1:]
        assert (component, definition) == (binding['component'], binding['definition']), 'component-scoped href divergence'
        source = ExpandedSource(components[component])
        closure = source.closure(definition)
        assert {node['id']: node['sha256'] for node in closure['nodes']} == {
            identifier: info['sha256'] for identifier, info in binding['dependencies'].items()}, 'dependency closure changed'
        assert native_rules[binding['native_rule']]['assessment_choices']['automated']['assessment'] == binding['assessment'], 'Rule/Assessment link changed'
        result = expanded_compare(source, definition, assessments[binding['assessment']])
        assert result['outcome'] != 'MISMATCH', 'operand divergence: ' + json.dumps(result)
        if require_proof:
            assert result['outcome'] == 'PROVED', 'unproved: ' + json.dumps(result)
        outcomes.append(result)
    assert native_benchmark['default_selection'] is True, 'default selection changed'
    for profile in benchmark.findall(X + 'Profile'):
        assert all(child.tag in (X + 'title', X + 'description', X + 'select') for child in profile), 'Profile refinement unsupported'
        row, = [row for row in trace['profiles'] if row['source_id'] == profile.get('id')]
        overrides = {child.get('idref'): child.get('selected') == 'true' for child in profile.findall(X + 'select')}
        disabled = []
        for binding in trace['rules']:
            item, selected = rules[binding['source_rule']], True
            while item is not benchmark:
                selected = selected and overrides.get(item.get('id'), item.get('selected', 'true') == 'true')
                item = parents[item]
            assert row['selected'][binding['source_rule']] == selected, 'Profile trace changed'
            if not selected:
                disabled.append(binding['native_rule'])
        native, = [p for p in native_benchmark['profiles'] if p['id'] == row['native_id']]
        assert set(native['disabled_rules']) == set(disabled), 'Profile selection divergence'
    return outcomes


def verify_inventory(root, manifest):
    """Reconcile all original checks/closures with the pre-existing source reader."""
    components = {c.get('id'): c[0] for c in root.findall(D + 'component')}
    benchmark = components[manifest['source_benchmark_component']]
    rules = {r.get('id'): r for r in benchmark.iter(X + 'Rule')}
    assert len(rules) == len(manifest['rules'])
    assert set(rules) == {r['source_rule'] for r in manifest['rules']}
    parents = {child: parent for parent in benchmark.iter() for child in parent}
    profiles = {p.get('id'): p for p in benchmark.findall(X + 'Profile')}
    stream, = root.findall(D + 'data-stream')
    references = {r.get('id'): r.get(HREF)[1:] for r in stream.iter(D + 'component-ref')}
    checklist, = stream.findall(D + 'checklists/' + D + 'component-ref')
    catalog = {u.get('name'): references[u.get('uri')[1:]] for u in checklist.iter()
               if u.tag == '{urn:oasis:names:tc:entity:xmlns:xml:catalog}uri'}
    assert sum(manifest['summary']['statuses'].values()) == len(rules)
    for row in manifest['rules']:
        rule = rules[row['source_rule']]
        assert row['source_rule_sha256'] == digest(xml_term(rule))
        assert [c['sha256'] for c in row['checks']] == [digest(xml_term(c)) for c in rule.findall('.//' + X + 'check')]
        for recorded, original in zip(row['checks'], rule.findall('.//' + X + 'check')):
            assert recorded['system'] == original.get('system') and recorded['selector'] == original.get('selector', '')
            assert recorded['references'] == [{'href': r.get('href'), 'name': r.get('name'), 'component': catalog.get(r.get('href'))}
                                               for r in original.findall(X + 'check-content-ref')]
        expected = {}
        for check in row['checks']:
            if check['system'] != OVAL:
                continue
            for ref in check['references']:
                closure = Source(components[ref['component']]).closure(ref['name'])
                expected.update({(ref['component'], n['id']): n['sha256'] for n in closure['nodes']})
        assert expected == {(n['component'], n['id']): n['sha256'] for n in row['dependencies']}, 'inventory closure differs'
        for name, selected in row['selection'].items():
            profile = profiles.get(name)
            overrides = {} if profile is None else {c.get('idref'): c.get('selected') == 'true' for c in profile.findall(X + 'select')}
            item, actual = rule, True
            while item is not benchmark:
                actual &= overrides.get(item.get('id'), item.get('selected', 'true') == 'true')
                item = parents[item]
            assert selected == actual, 'all-Rule Profile inventory differs'
    return {'original_rules': len(rules), 'original_profiles': len(profiles),
            'checks': sum(len(r['checks']) for r in manifest['rules']),
            'independent_reference_and_profile_inventory': 'PASS'}


def verify_compiled(documents, bundle):
    """Check every emitted Assessment's exact operands, independently of build success."""
    rows = []
    with zipfile.ZipFile(io.BytesIO(bundle)) as package:
        manifest = json.loads(package.read('META-INF/manifest.json'))
        for document in documents.values():
            if 'assessment' not in document:
                continue
            assessment = document['assessment']
            info = manifest['build_provenance']['compiled_programs'][assessment['id']]
            raw = package.read(info['path'])
            verify_program(assessment, json.loads(raw))
            rows.append({'assessment': assessment['id'], 'program_sha256': sha256(raw).hexdigest(),
                         'operands_match_authoring': True})
    return rows


def public_gates(artifacts, destination):
    """Serialized inputs through unchanged validator/compiler and separate consumer."""
    from validate_native_json_schemas import build_validators, document_errors
    root = Path(__file__).resolve().parents[1]
    destination.mkdir()
    started = time.perf_counter()
    validators = build_validators(root / 'schema/v0.4.0')
    count = 0
    for path in sorted((artifacts / 'authoring').rglob('*.json')):
        document = json.loads(path.read_text())
        kind, = document
        assert not list(document_errors(validators[kind + '.schema.json'], document)), str(path)
        count += 1
    assert count > 0, 'empty validator input is not acceptance'
    subprocess.run([sys.executable, str(root / 'tools/validate_native_json_schemas.py'), str(artifacts / 'authoring'),
        '--schema-dir', str(root / 'schema/v0.4.0'), '--report', str(destination / 'yaml-validation.json')],
        check=True, capture_output=True, text=True)
    report = json.loads((destination / 'yaml-validation.json').read_text())
    assert report['documents_checked'] == report['valid'] == count and report['invalid'] == 0
    validated = time.perf_counter()
    for suffix in ('json', 'yaml'):
        with zipfile.ZipFile(destination / (suffix + '.zip'), 'w') as package:
            for path in sorted((artifacts / 'authoring').rglob('*.' + suffix)):
                package.write(path, path.relative_to(artifacts).as_posix())
    subprocess.run([sys.executable, str(root / 'tools/v04_native_bundle_compiler.py'),
        '--json-archive', str(destination / 'json.zip'), '--yaml-archive', str(destination / 'yaml.zip'),
        '--output-dir', str(destination / 'compiled'), '--report', str(destination / 'compilation.json')],
        check=True, capture_output=True, text=True)
    compiled = time.perf_counter()
    bundle, = (destination / 'compiled').glob('*.scapng')
    process = subprocess.run([sys.executable, str(root / 'tools/verify_v04_package_consumer.py'), str(bundle),
        '--source-json', str(destination / 'json.zip'), '--source-yaml', str(destination / 'yaml.zip')],
        check=True, capture_output=True, text=True)
    return {'json_valid': count, 'yaml_valid': count,
            'validation_seconds': validated - started,
            'paired_compiler_including_preflight_seconds': compiled - validated,
            'consumer_seconds': time.perf_counter() - compiled,
            'consumer': json.loads(process.stdout), 'bundle_sha256': sha256(bundle.read_bytes()).hexdigest()}, bundle


def accepted_coverage(manifest, trace, proofs, programs):
    """Attach proof only after independently checking source and compiled operands."""
    from copy import deepcopy
    from v04_direct_inventory import summarize
    result = deepcopy(manifest)
    by_assessment = {p['assessment']: p for p in programs}
    by_rule = {b['source_rule']: (b, p) for b, p in zip(trace['rules'], proofs)}
    assert len(proofs) == len(trace['rules']) == len(programs)
    for row in result['rules']:
        if row['status'] != 'converted':
            assert not row['artifacts'] and row['proof_level'] == 'none'
            continue
        binding, proof = by_rule[row['source_rule']]
        assert proof['outcome'] in ('PROVED', 'UNVERIFIABLE/UNSUPPORTED')
        program = by_assessment[binding['assessment']]
        row['proof_level'] = 'source_proved' if proof['outcome'] == 'PROVED' else 'compiled_unproved'
        row['proof_outcome'] = proof['outcome']
        row['unsupported_proof_obligations'] = proof.get('unsupported_obligations', [])
        row['program_sha256'] = program['program_sha256']
    result['summary'] = summarize(result['rules'])
    return result


def main():
    """Reproduce measured public CLI runs, then independent acceptance in this process."""
    import argparse
    from v04_direct_scap_source import SourceModel
    from v04_direct_inventory import coverage_markdown
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--rule', action='append', required=True, help='focused comparison; repeatable, no admission allowlist')
    parser.add_argument('--samples', type=int, default=3)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.samples > 0 and not args.output.exists(), 'positive sample count/new output directory required'
    args.output.mkdir(parents=True)
    root = Path(__file__).resolve().parents[1]
    source = SourceModel(args.source, args.sha256)  # Independent consumer's parse; producer has its own process.
    evidence = {'source_zip_sha256': source.zip_sha256, 'source_xml_sha256': source.xml_sha256,
        'method': 'Sequential fresh public CLI processes; OS caches/scheduling uncontrolled. Each producer parses XML once. This independent verifier parses its own original source once. No production performance ratio.',
        'modes': {}}
    for mode in ('focused', 'inventory', 'automatic'):
        measurements, emissions = [], []
        for number in range(args.samples):
            output = args.output / f'{mode}-{number}'
            command = [sys.executable, str(root / 'tools/v04_direct_converter.py'), str(args.source),
                       '--sha256', args.sha256, '--output', str(output)]
            if mode == 'focused':
                for identifier in args.rule:
                    command.extend(['--rule', identifier])
            else:
                command.append('--inventory-only' if mode == 'inventory' else '--all-rules')
            started = time.perf_counter()
            process = subprocess.run(command, check=True, capture_output=True, text=True)
            metrics = json.loads(process.stdout)
            metrics['wall_seconds'] = time.perf_counter() - started
            metrics['command'] = command
            measurements.append(metrics)
            emissions.append({str(p.relative_to(output)): sha256(p.read_bytes()).hexdigest()
                              for p in output.rglob('*') if p.is_file() and p.name != 'metrics.json'})
        assert all(e == emissions[0] for e in emissions), 'nondeterministic content/manifest/trace'
        artifacts = args.output / f'{mode}-0'
        trace = json.loads((artifacts / 'source-trace.json').read_text())
        assert trace['xml_parse_calls'] == 1
        documents = {str(p.relative_to(artifacts)): json.loads(p.read_text()) for p in (artifacts / 'authoring').rglob('*.json')}
        result = {'measurements': measurements, 'emitted_sha256': emissions[0],
                  'median_wall_seconds': statistics.median(m['wall_seconds'] for m in measurements),
                  'peak_producer_rss_kib_linux': max(m['process_peak_rss_kib_linux'] or 0 for m in measurements)}
        if mode != 'focused':
            manifest = json.loads((artifacts / 'coverage.json').read_text())
            result['inventory'] = verify_inventory(source.root, manifest)
        if documents:
            started = time.perf_counter()
            proofs = verify_original(source.root, documents, trace, require_proof=False)
            result['source_proof_seconds'] = time.perf_counter() - started
            gates, bundle = public_gates(artifacts, args.output / f'{mode}-gates')
            programs = verify_compiled(documents, bundle.read_bytes())
            result.update(public_gates=gates, programs=programs, proofs=proofs)
            if mode == 'automatic':
                coverage = accepted_coverage(manifest, trace, proofs, programs)
                (args.output / 'coverage.json').write_text(json.dumps(coverage, indent=2) + '\n')
                (args.output / 'coverage.md').write_text(coverage_markdown(coverage))
                result['summary'] = coverage['summary']
        else:
            result['public_gates'] = 'not applicable: discovery-only; no authoring or package emitted'
        evidence['modes'][mode] = result
    (args.output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(json.dumps(evidence['modes']['automatic']['summary'], indent=2))


if __name__ == '__main__':
    main()
