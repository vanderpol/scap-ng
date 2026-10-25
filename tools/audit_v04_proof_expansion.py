#!/usr/bin/env python3
"""Committed 24-case Windows manifest + original eight pilot revisits (#251).

No general corpus iteration or conversion CLI. Only these 32 fixed cases run.
Timing/cost data is separate so semantic proof evidence remains reproducible.
"""
import argparse
from collections import Counter
import csv
from hashlib import sha256
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET
import zipfile

try:
    import resource
except ImportError:  # Windows: RSS is optional telemetry, never a proof dependency.
    resource = None

from audit_v04_eight_assessment_pilot import BASE, ROOT, CASES, original, packaged
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from verify_v04_package_consumer import digest, read_json, require
from v04_source_package_semantics import Unsupported, local

MANIFEST = ROOT / 'docs/audit/v04-proof-expansion/windows24-manifest.json'
MANIFEST_SHA256 = '9969b6bdfa832e4aba03bf28fc20291c74839e74ddfc8153b4faf61049808598'
PILOT = ROOT / 'docs/audit/v04-eight-assessment-pilot/results.json'
PILOT_CSV = PILOT.with_name('results-coverage.csv')


def manifest_rows():
    require(sha256(MANIFEST.read_bytes()).hexdigest() == MANIFEST_SHA256,
            'committed pre-comparison manifest changed; no substitutions permitted')
    m = json.loads(MANIFEST.read_text())
    require(m['status'] == 'FIXED_BEFORE_SOURCE_COMPARISON_NO_SUCCESS_QUOTA', 'unfrozen manifest')
    rows = m['cases']
    require(len(rows) == 24 and len({r['assessment'] for r in rows}) == 24, '24 unique identities required')
    require(Counter(r['platform'] for r in rows) == {
        'ms_windows_11': 8, 'ms_windows_server_2025': 8, 'ms_windows_server_dns': 8}, 'manifest balance')
    prior = json.loads(PILOT.read_text())
    old = {c['assessment'] for c in prior['cases'] if c['outcome'].startswith('PROVED')}
    require(not old & {r['assessment'] for r in rows}, 'manifest repeats prior proof')
    return rows


def features(source, trace):
    nodes = [source.nodes[n['id']] for n in trace['source_dependency_closure']['nodes']]
    return {'source_nodes': len(nodes), 'kinds': dict(Counter(source.kind[n.get('id')] for n in nodes)),
        'test_types': dict(Counter(n.tag for n in nodes if source.kind[n.get('id')] == 'tests')),
        'multi_state_tests': sum(sum(local(c) == 'state' for c in n) > 1 for n in nodes
                                 if source.kind[n.get('id')] == 'tests'),
        'constructs': dict(Counter(local(c) for n in nodes for c in n.iter()
            if local(c) in {'set', 'filter', 'concat', 'regex_capture', 'merge', 'unique',
                            'object_component', 'variable_component', 'extend_definition'}))}


def extract_fixture(source, definition, assessment, program, record):
    root = ET.Element('{http://oval.mitre.org/XMLSchema/oval-definitions-5}oval_definitions')
    for kind in ('definitions', 'tests', 'objects', 'states', 'variables'):
        nodes = [n for n in record['source_dependency_closure']['nodes'] if n['kind'] == kind]
        if nodes:
            section = ET.SubElement(root, '{http://oval.mitre.org/XMLSchema/oval-definitions-5}' + kind)
            section.extend(source.nodes[n['id']] for n in nodes)
    return {'source_xml': ET.tostring(root, encoding='unicode'), 'source_definition': definition,
            'assessment': assessment, 'compiled_program': program,
            'provenance': {k: v for k, v in record.items() if k not in
                ('comparisons', 'test_bindings', 'unsupported_obligations')},
            'expected_outcome': record['outcome']}


def merge_coverage(previous, results):
    rows = [dict(r) for r in previous]
    old = {r['id'] for r in rows if r['packaged_original_oval_equivalence'].startswith('PROVED')}
    proofs = {r['assessment']: r for r in results if r['outcome'].startswith('PROVED')}
    require(old <= proofs.keys(), 'previous exact proof did not reproduce; stop for regression')
    require(len(proofs) == sum(r['assessment'] in proofs for r in results), 'duplicate proof identity')
    for row in rows:
        if row['id'] in proofs:
            proof = proofs[row['id']]
            require(row['mode'] == 'automated' and row['proof_assessment_sha256'] in ('', proof['assessment_sha256'])
                    and row['proof_program_sha256'] in ('', proof['program_sha256']), 'proof graph identity drift')
            row.update(packaged_original_oval_equivalence=proof['outcome'], proof_case=proof['case'],
                       proof_assessment_sha256=proof['assessment_sha256'], proof_program_sha256=proof['program_sha256'])
    require(sum(r['mode'] == 'automated' for r in rows) == 883 and len({r['id'] for r in rows}) == len(rows),
            'unique automated denominator drift')
    require(sum(r['packaged_original_oval_equivalence'].startswith('PROVED') for r in rows) == len(proofs),
            'proof references missing from coverage inventory')
    return rows, {'old_proved': len(old), 'new_proved': len(proofs), 'delta': len(proofs) - len(old),
                  'denominator': 883, 'remaining_unverified': 883 - len(proofs),
                  'proved_percent': len(proofs) * 100 / 883}


def write_feature_matrix(results, path):
    """Observed features in attempted complete graphs, never parser coverage %."""
    rows = []
    names = ['unix.file', 'unix.password', 'independent.textfilecontent54', 'windows.registry',
             'windows.wmi.query', 'independent.shellcommand', 'set', 'filter', 'object_component',
             'concat', 'regex_capture', 'merge', 'unique', 'extend_definition', 'multi_state_tests',
             'conditional_all_exist']
    for name in names:
        def present(c):
            f = c.get('features', {})
            if name == 'conditional_all_exist':
                return bool(c.get('normalizations_applied'))
            if name == 'multi_state_tests':
                return f.get('multi_state_tests', 0) > 0
            if '.' in name:
                suffix = 'wmi57' if name == 'windows.wmi.query' else name.split('.')[-1]
                return any(t.endswith('}' + suffix + '_test') for t in f.get('test_types', {})) or (
                    name == 'unix.password' and any('}password_object' in n['type']
                        for n in c.get('source_dependency_closure', {}).get('nodes', [])))
            return f.get('constructs', {}).get(name, 0) > 0
        cases = [c for c in results if present(c)]
        rows.append({'feature': name, 'attempted_cases': len(cases),
            'proved_cases_including_conditional': sum(c['outcome'].startswith('PROVED') for c in cases),
            'case_ids': ';'.join(c['case'] for c in cases),
            'unverified_cases': ';'.join(c['case'] for c in cases if not c['outcome'].startswith('PROVED'))})
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def run(inputs, bundles, output, fixtures=None):
    rows = manifest_rows()
    pins = json.loads((BASE / 'source-ledger.json').read_text())['sources']
    accepted = json.loads((BASE / 'consumer-results.json').read_text())['results']
    prior = json.loads(PILOT.read_text())
    with PILOT_CSV.open() as stream:
        previous = list(csv.DictReader(stream))
    old_by_key = {(c['platform'], c['rule']): c for c in prior['cases']}
    method = {p: sha256((ROOT / 'tools' / p).read_bytes()).hexdigest() for p in
        ('v04_source_package_semantics.py', 'v04_expanded_source_proof.py', 'audit_v04_eight_assessment_pilot.py',
         'audit_v04_proof_expansion.py')}
    jobs = [('windows-' + str(r['case']).zfill(2), r['platform'], r['rule'], r) for r in rows]
    jobs += [('pilot-' + str(i), p, rule, None) for i, (p, rule, _) in enumerate(CASES, 1)]
    results, timings = [], []
    for case, platform, rule, frozen in jobs:
        wall, cpu = time.perf_counter(), time.process_time()
        a, record = packaged(bundles / (platform + '.scapng'), rule, accepted[platform]['bundle_sha256'])
        record.update(case=case, platform=platform,
                      proof_method_sha256=digest(method),
                      old_outcome=old_by_key.get((platform, rule), {}).get('outcome', 'UNVERIFIED_NOT_ATTEMPTED'))
        if frozen:
            require(record['assessment'] == frozen['assessment']
                and record['assessment_sha256'] == frozen['assessment_member']['sha256']
                and record['program_sha256'] == frozen['compiled_program_member']['sha256']
                and record['package_sha256'] == frozen['package_sha256'], 'fixed candidate drift')
        source = None
        try:
            source, definition, trace = original(inputs, platform, rule, pins, source_type=ExpandedSource)
            record.update(trace, features=features(source, trace))
            if platform == 'rhel_9' and rule == 'SV-258179':
                source.admit_pinned_rhel_normalization(definition, trace)
            record.update(expanded_compare(source, definition, a))
            require(not (platform == 'oracle_linux_9' and record['outcome'].startswith('PROVED')),
                    'Oracle exception must remain unverified')
        except Unsupported as e:
            record.update(outcome='UNVERIFIABLE/UNSUPPORTED', blocker=str(e))
        timings.append({'case': case, 'wall_seconds': time.perf_counter() - wall,
                        'cpu_seconds': time.process_time() - cpu,
                        'process_peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource else None,
                        'source_nodes': record.get('features', {}).get('source_nodes'),
                        'compiled_tests': len(a['tests'])})
        if fixtures and frozen and source:
            fixtures.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(bundles / (platform + '.scapng')) as z:
                program = read_json(z.read(record['program_path']))
            f = extract_fixture(source, definition, a, program, record)
            (fixtures / (case + '.json')).write_text(json.dumps(f, indent=2) + '\n')
        results.append(record)
    coverage, summary = merge_coverage(previous, results)
    output.parent.mkdir(parents=True, exist_ok=True)
    coverage_path = output.with_name(output.stem + '-coverage.csv')
    with coverage_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(coverage[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(coverage)
    summary['per_namespace'] = {namespace: {
        'automated': sum(r['mode'] == 'automated' and r['path'].split('/')[1] == namespace for r in coverage),
        'proved': sum(r['packaged_original_oval_equivalence'].startswith('PROVED')
                      and r['path'].split('/')[1] == namespace for r in coverage)}
        for namespace in sorted({r['path'].split('/')[1] for r in coverage})}
    report = {'status': 'BOUNDED_PROOF_EXPANSION_NOT_SCANNER_OR_RELEASE_ACCEPTANCE',
        'instructions': 'https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6392337337',
        'baseline': '336cb37114aadf51d2810aa669b6325b9c03be7b',
        'manifest_sha256': sha256(MANIFEST.read_bytes()).hexdigest(),
        'baseline_coverage_sha256': sha256(PILOT_CSV.read_bytes()).hexdigest(),
        'proof_method_files': method,
        'rule_anchors_sha256': sha256((ROOT / 'docs/audit/v04-proof-expansion/proof-rule-anchors.json').read_bytes()).hexdigest(),
        'coverage': summary, 'coverage_inventory': {'path': coverage_path.name,
            'sha256': sha256(coverage_path.read_bytes()).hexdigest(), 'rows': len(coverage)},
        'windows_outcomes': dict(Counter(r['outcome'] for r in results[:24])),
        'pilot_outcomes': dict(Counter(r['outcome'] for r in results[24:])),
        'cases': results, 'full_883_audit_run': False, 'source_or_package_regenerated': False,
        'scanner_evaluated': False, 'publisher_trust_verified': False}
    output.write_text(json.dumps(report, indent=2) + '\n')
    write_feature_matrix(results, output.with_name('feature-coverage.csv'))
    output.with_name(output.stem + '-performance.json').write_text(json.dumps({
        'units': 'wall/process CPU seconds; process high-water RSS KiB (not per-case allocation)',
        'cases': timings, 'total_wall_seconds': sum(t['wall_seconds'] for t in timings),
        'total_cpu_seconds': sum(t['cpu_seconds'] for t in timings)}, indent=2) + '\n')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs-dir', type=Path, required=True)
    p.add_argument('--bundles-dir', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    p.add_argument('--fixtures-dir', type=Path)
    a = p.parse_args()
    r = run(a.inputs_dir, a.bundles_dir, a.report, a.fixtures_dir)
    print(json.dumps({k: r[k] for k in ('windows_outcomes', 'pilot_outcomes', 'coverage')}))
