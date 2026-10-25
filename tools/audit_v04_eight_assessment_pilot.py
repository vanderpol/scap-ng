#!/usr/bin/env python3
"""Eight exact packaged Assessments → original SCAP proof pilot, never 883 (#251).

Inputs are read-only. Pins come from the reviewed independent acceptance ledger.
Only successful independent proofs may advance the separate coverage overlay.
"""
import argparse
from collections import Counter
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

from verify_v04_package_consumer import (archive_members, authoring, canonical, digest,
                                        expression_plan, read_json, require)
from v04_source_package_semantics import Source, Unsupported, compare, local, xml_term

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/audit/v04-package-acceptance'
# Fixed before comparison; no fallback selection when a graph cannot be proved.
CASES = (
    ('rhel_9', 'SV-257889', 'Extended Definition; file/password Sets, Filters and for_each'),
    ('oracle_linux_9', 'SV-271844', 'Source-specific absence; do not elevate archive exception'),
    ('ms_windows_11', 'SV-253254', 'Extended Definition; Enterprise/EnterpriseS State OR'),
    ('ms_windows_server_2025', 'SV-278001', 'Nested AND/OR/NOT, shared Object, constant arrays and WMI records'),
    ('ms_windows_server_dns', 'SV-259345', 'Absence, dynamic commands and object_component/concat Variables'),
    ('apache_server_2-4_unix_server', 'SV-214228', 'Configuration discovery and 18-variable function graph'),
    ('rhel_9', 'SV-258179', 'Additional complex case: pinned all_exist normalization and 24-Test graph'),
    ('ms_windows_11', 'SV-253260', 'Additional complex case: nested BitLocker registry decision graph'),
)


def original(inputs, platform, rule, pins, *, source_type=Source):
    pin = pins[platform]
    path = inputs / pin['file']
    require(sha256(path.read_bytes()).hexdigest() == pin['zip_sha256'], 'original ZIP pin mismatch')
    with zipfile.ZipFile(path) as z:
        require(z.testzip() is None, 'original ZIP CRC mismatch')
        matches = []
        for name in z.namelist():
            if not name.endswith('.xml'):
                continue
            raw = z.read(name)
            root = ET.fromstring(raw)
            rules = [n for n in root.iter() if local(n) == 'Rule'
                     and re.search(r'_rule_' + re.escape(rule) + r'r[0-9]+_rule$', n.get('id', ''))]
            matches.extend((name, raw, root, r) for r in rules)
    require(len(matches) == 1, 'original XCCDF Rule missing/ambiguous: ' + rule)
    member, raw, root, r = matches[0]
    ids = {}
    for n in root.iter():
        if n.get('id') and local(n) in ('component', 'extended-component', 'component-ref'):
            require(n.get('id') not in ids, 'duplicate SCAP identifier')
            ids[n.get('id')] = n
    all_checks, refs = [], []
    require(not any(local(n) == 'complex-check' for n in r.iter()), 'XCCDF complex-check needs independent proof')
    for check in r:
        if local(check) != 'check':
            continue
        info = {'attributes': dict(check.attrib),
                'references': [dict(c.attrib) for c in check if local(c) == 'check-content-ref']}
        all_checks.append(info)
        if check.get('system') == 'http://oval.mitre.org/XMLSchema/oval-definitions-5':
            require(set(check.attrib) <= {'system', 'selector'} and
                    all(local(c) == 'check-content-ref' for c in check), 'OVAL check has unproved imports/logic')
            refs += info['references']
    require(refs, 'no original automated check')
    # Duplicate default/automated alternatives are retained and shown identical;
    # distinct automated checks are never silently reduced to one.
    unique = {tuple(sorted(r.items())) for r in refs}
    require(len(unique) == 1, 'multiple distinct original OVAL checks require explicit combination proof')
    ref = dict(next(iter(unique)))
    require(set(ref) == {'href', 'name'}, 'check-content-ref attributes')
    uris = [n.get('uri') for n in root.iter() if local(n) == 'uri' and n.get('name') == ref['href']]
    require(len(set(uris)) == 1 and uris[0].startswith('#'), 'SCAP catalog href unresolved/ambiguous')
    cref = ids[uris[0][1:]]
    require(local(cref) == 'component-ref', 'catalog target is not component-ref')
    href = cref.get('{http://www.w3.org/1999/xlink}href', '')
    require(href.startswith('#') and href[1:] in ids, 'SCAP component reference unresolved')
    comp = ids[href[1:]]
    ovals = [n for n in comp if n.tag == '{http://oval.mitre.org/XMLSchema/oval-definitions-5}oval_definitions']
    require(len(ovals) == 1, 'catalog did not resolve one original OVAL component')
    source = source_type(ovals[0])
    closure = source.closure(ref['name'])
    return source, ref['name'], {'source_zip': pin['file'], 'source_zip_sha256': pin['zip_sha256'],
        'revision': pin['revision'], 'source_path': pin['source_path'],
        'xml_member': member, 'xml_sha256': sha256(raw).hexdigest(),
        'xccdf_rule': r.get('id'), 'xccdf_rule_sha256': digest(xml_term(r)),
        'all_xccdf_checks': all_checks, 'distinct_oval_checks': len(unique),
        'catalog_href': ref['href'], 'component_ref': cref.get('id'), 'component': comp.get('id'),
        'definition': ref['name'], 'source_dependency_closure': closure,
        'closure_sha256': digest(closure)}


def packaged(bundle, rule, expected_hash):
    require(sha256(bundle.read_bytes()).hexdigest() == expected_hash, 'reviewed bundle SHA mismatch')
    members = archive_members(bundle)
    m = read_json(members['META-INF/manifest.json'])
    require(m['format_version'] == '0.4.0', 'package version')
    infos = list(m['objects'].values()) + list(m['build_provenance']['compiled_programs'].values())
    require(set(members) == {'META-INF/manifest.json'} | {i['path'] for i in infos}, 'package member closure')
    for i in infos:
        raw = members[i['path']]
        require(len(raw) == i['size'] and sha256(raw).hexdigest() == i['sha256'], 'member hash/size')
        require(canonical(read_json(raw)) == raw, 'noncanonical package member')
    r = read_json(members[m['objects'][rule]['path']])['rule']
    aid = r['assessment_choices']['automated']['assessment']
    info = m['objects'][aid]
    a = read_json(members[info['path']])['assessment']
    require(a['id'] == aid and a['mode'] == 'automated', 'not actual packaged automation')
    program_info = m['build_provenance']['compiled_programs'][aid]
    program = read_json(members[program_info['path']])
    verify_program(a, program)
    return a, {'benchmark': m['benchmark_id'], 'package': bundle.name, 'package_sha256': expected_hash,
        'manifest_sha256': sha256(members['META-INF/manifest.json']).hexdigest(),
        'rule': rule, 'rule_path': m['objects'][rule]['path'],
        'assessment': aid, 'assessment_path': info['path'], 'assessment_sha256': info['sha256'],
        'program_path': program_info['path'], 'program_sha256': program_info['sha256'],
        'compiled_operands_and_result_plan_match_exact_packaged_source': True}


def verify_program(a, program):
    aid = a['id']
    require(set(program) == {'format', 'assessment_id', 'assessment_source_sha256', 'test_instructions',
        'result_instructions', 'result_requires', 'result_expression_sha256', 'scanner_evaluated'}, 'program keys')
    require(program['format'] == 'scap-ng-0.4.0-native-assessment-program/0.1'
            and program['scanner_evaluated'] is False, 'program format/runtime claim')
    require(program['assessment_id'] == aid and program['assessment_source_sha256'] == digest(a), 'program identity')
    require([x['test_id'] for x in program['test_instructions']] == sorted(a['tests']), 'program Test inventory')
    for instruction in program['test_instructions']:
        t = a['tests'][instruction['test_id']]
        require(instruction == {'test_id': instruction['test_id'], 'capability': t['capability'],
            'opcode': 'CHECK_COLLECTION_PRESENCE' if set(t['require']) == {'items_found'} else 'CHECK_ITEM_CONDITION',
            'source_test_sha256': digest(t), 'operands': t}, 'compiled operand divergence')
    plan, required = expression_plan(a)
    require(program['result_instructions'] == plan and program['result_requires'] == required
            and program['result_expression_sha256'] == digest(a['evaluate']), 'compiled Boolean divergence')


def coverage(inventory, cases, by_platform):
    """Overlay does not rewrite historical audit evidence or imply shared proof."""
    proved = {c['assessment']: c for c in cases if c['outcome'] in
              ('PROVED', 'PROVED_WITH_EXPLICIT_APPROVED_NORMALIZATION')}
    rows = []
    for old in inventory:
        row = dict(old)
        if row['id'] in proved:
            proof = proved[row['id']]
            require(row['mode'] == 'automated', 'manual proof promotion')
            row['packaged_original_oval_equivalence'] = proof['outcome']
            row['proof_case'] = proof['case']
            row['proof_assessment_sha256'] = proof['assessment_sha256']
            row['proof_program_sha256'] = proof['program_sha256']
        rows.append(row)
    require(sum(r['mode'] == 'automated' for r in rows) == 883, 'automated denominator drift')
    require(len(proved) == sum(r['packaged_original_oval_equivalence'].startswith('PROVED') for r in rows),
            'proof identity inventory mismatch')
    return {'automated_denominator': 883, 'proved': len(proved), 'unverified': 883 - len(proved),
            'proved_percent': len(proved) * 100 / 883, 'per_platform': by_platform,
            'assessment_inventory': rows, 'scope': 'eight-case overlay on immutable historical migration inventory'}


def run(inputs, bundles, current, output, fixtures=None):
    pins = json.loads((BASE / 'source-ledger.json').read_text())['sources']
    accepted = json.loads((BASE / 'consumer-results.json').read_text())
    docs = authoring(current)
    # Reconstruction ZIP timestamps may differ. Prove the entire authoring graph
    # against immutable native bundle bytes rather than requiring incidental ZIP
    # container bytes from the previous local reconstruction.
    expected_docs = {}
    for platform, accepted_bundle in accepted['results'].items():
        bundle = bundles / (platform + '.scapng')
        require(sha256(bundle.read_bytes()).hexdigest() == accepted_bundle['bundle_sha256'], 'bundle pin mismatch')
        with zipfile.ZipFile(bundle) as z:
            manifest = read_json(z.read('META-INF/manifest.json'))
            for ident, info in manifest['objects'].items():
                doc = read_json(z.read(info['path']))
                kind, body = next(iter(doc.items()))
                require(body['id'] == ident, 'bundle document identity')
                key = (kind, ident)
                require(key not in expected_docs or expected_docs[key] == doc, 'inconsistent shared graph')
                expected_docs[key] = doc
    require(len(docs) == accepted['source_documents'] and
            {k: doc for k, (_, doc) in docs.items()} == expected_docs, 'entire authoring graph differs from pinned packages')
    inventory = list(csv.DictReader(io.StringIO((BASE / 'source-ledger-migrated-assessments.csv').read_text())))
    by_id = {r['id']: r for r in inventory}
    results, platforms = [], {}
    for index, (platform, rule, why) in enumerate(CASES, 1):
        a, packaged_info = packaged(bundles / (platform + '.scapng'), rule,
                                    accepted['results'][platform]['bundle_sha256'])
        aid = a['id']
        require(docs[('assessment', aid)][1] == {'assessment': a}, 'current authoring/exact package mismatch')
        require(by_id[aid]['path'] == docs[('assessment', aid)][0]
                and by_id[aid]['mode'] == 'automated', 'migration ledger mapping mismatch')
        record = {'case': index, 'platform': platform, 'selection_reason': why,
                  **packaged_info, 'authoring_path': by_id[aid]['path']}
        try:
            source, definition, trace = original(inputs, platform, rule, pins)
            record.update(trace)
            record.update(compare(source, definition, a))
            if fixtures:
                # Minimal *complete* original dependency closure, never a newly
                # rendered OVAL conversion. Node fingerprints must remain exact.
                fixtures.mkdir(parents=True, exist_ok=True)
                oval = ET.Element('{http://oval.mitre.org/XMLSchema/oval-definitions-5}oval_definitions')
                for kind in ('definitions', 'tests', 'objects', 'states', 'variables'):
                    nodes = [n for n in trace['source_dependency_closure']['nodes'] if n['kind'] == kind]
                    if nodes:
                        section = ET.SubElement(oval, '{http://oval.mitre.org/XMLSchema/oval-definitions-5}' + kind)
                        section.extend(source.nodes[n['id']] for n in nodes)
                fixture = {'source_xml': ET.tostring(oval, encoding='unicode'),
                           'source_definition': definition, 'assessment': a,
                           'provenance': {k: v for k, v in record.items() if k not in
                             ('comparisons', 'unsupported_obligations', 'test_bindings')},
                           'expected_outcome': record['outcome']}
                with zipfile.ZipFile(bundles / (platform + '.scapng')) as z:
                    fixture['compiled_program'] = read_json(z.read(record['program_path']))
                (fixtures / (platform + '-' + rule + '.json')).write_text(json.dumps(fixture, indent=2) + '\n')
        except (Unsupported, ValueError) as e:
            record.update(outcome='UNVERIFIABLE/UNSUPPORTED', blocker=str(e))
        results.append(record)
    # Denominators are unique native Assessment identities, not package instances.
    for platform in pins:
        own = [r for r in inventory if r['mode'] == 'automated' and
               r['path'].startswith('authoring/' + platform + '/')]
        # Shared graphs are counted separately; Rule fan-out is not proof transfer.
        cases = [r for r in results if r['platform'] == platform]
        platforms[platform] = {'platform_local_automated': len(own), 'pilot_selected': len(cases),
                              'outcomes': dict(Counter(c['outcome'] for c in cases))}
    platforms['shared'] = {'automated': sum(r['mode'] == 'automated' and
        r['path'].startswith('authoring/shared/') for r in inventory)}
    ledger = coverage(inventory, results, platforms)
    coverage_path = output.with_name(output.stem + '-coverage.csv')
    output.parent.mkdir(parents=True, exist_ok=True)
    with coverage_path.open('w', newline='') as stream:
        fields = list(inventory[0]) + ['proof_case', 'proof_assessment_sha256', 'proof_program_sha256']
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(ledger.pop('assessment_inventory'))
    ledger['inventory'] = {'path': coverage_path.name,
        'sha256': sha256(coverage_path.read_bytes()).hexdigest(), 'rows': len(inventory)}
    report = {'status': 'BOUNDED_EIGHT_CASE_SOURCE_PACKAGE_PILOT_NOT_SCANNER_OR_RELEASE_ACCEPTANCE',
        'reviewed_checkpoint': '40c1d198d82cf009650e940d812cd799bc5fd9aa',
        'instructions': 'https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6392094407',
        'source_authoring_sha256': sha256(current.read_bytes()).hexdigest(),
        'source_authoring_graph_sha256': digest([{'kind': k[0], 'id': k[1], 'sha256': digest(doc)}
                                                for k, doc in sorted(expected_docs.items())]),
        'base_migration_inventory_sha256': sha256((BASE / 'source-ledger-migrated-assessments.csv').read_bytes()).hexdigest(),
        'proof_method_sha256': sha256((ROOT / 'tools/v04_source_package_semantics.py').read_bytes()).hexdigest(),
        'cases': results, 'outcomes': dict(Counter(c['outcome'] for c in results)),
        'coverage': ledger, 'scanner_evaluated': False, 'publisher_trust_verified': False,
        'full_883_audit_run': False, 'normalizations_expanded': False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs-dir', required=True, type=Path)
    p.add_argument('--bundles-dir', required=True, type=Path)
    p.add_argument('--authoring-json', required=True, type=Path)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--fixtures-dir', type=Path)
    a = p.parse_args()
    result = run(a.inputs_dir, a.bundles_dir, a.authoring_json, a.report, a.fixtures_dir)
    print(json.dumps({'outcomes': result['outcomes'], 'proved': result['coverage']['proved']}))
