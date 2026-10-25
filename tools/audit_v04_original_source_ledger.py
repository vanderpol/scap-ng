#!/usr/bin/env python3
"""Original six-source inventory, bounded proof ledger and migration accounting.

No corpus conversion: only five already-proved original fixtures are admitted
through the current converter. Archive migration is never original-source parity.
Refs #251.
"""
import argparse
import csv
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from scap_converter_core import convert
from scap_ng_roundtrip_v003.compare_oval_semantics import Model
from verify_v04_package_consumer import authoring
from migrate_v04_six_stig_review_archive import attest_oracle_source, ORACLE_SOURCE_SHA256

ROOT = Path(__file__).resolve().parents[1]
PIN = '8c8e5dff860af6b1290ee9273a282db24278f8d5'
FILES = {
    'rhel_9': ('U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip',
               '70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5'),
    'oracle_linux_9': ('U_Oracle_Linux_9_V1R4_STIG_SCAP_1-4_Benchmark-enhancedV5-signed.zip', ORACLE_SOURCE_SHA256),
    'ms_windows_11': ('U_MS_Windows_11_V2R10_STIG_SCAP_1-4_Benchmark-enhancedV18-signed.zip',
                      'e4b8d55b58aa80124bd0974977af4c7f7bde35c748e2940e02857419292d8c3d'),
    'ms_windows_server_2025': ('U_MS_Windows_Server_2025_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV1-signed.zip',
                             '2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0'),
    'ms_windows_server_dns': ('U_MS_Windows_Server_DNS_V2R3_STIG_SCAP_1-4_Benchmark-enhancedV8-signed.zip',
                            'f674b67e74acbd3037093d50e33dc20765bd9d45a6c9ed2be5d463d009a6c6b8'),
    'apache_server_2-4_unix_server': ('U_Apache_Server_2-4_UNIX_Server_V3R2_STIG_SCAP_1-4_Benchmark-enhancedV2-signed.zip',
                                    '8894123788ba415373625eaecdbbd834f190668697803c3319393c11889f1b80'),
}
PROOFS = (
    ('rhel_9', 'SV-257889', 'oval:mil.disa.stig.defs:def:230325'),
    ('ms_windows_server_2025', 'SV-278001', 'oval:navy.navwar.niwcatlantic.scc.windows:def:278001'),
    ('ms_windows_server_dns', 'SV-259345', 'oval:navy.navwar.niwcatlantic.scc.windows:def:259345'),
    ('ms_windows_11', 'SV-253254', 'oval:mil.disa.stig.defs:def:253254'),
    ('rhel_9', 'SV-258179', 'oval:mil.disa.stig.defs:def:230413'),
)


def tag(node):
    return node.tag.rsplit('}', 1)[-1]


def fingerprint(node):
    def tree(n):
        return [n.tag, sorted(n.attrib.items()), n.text if not len(n) else None,
                [tree(c) for c in n]]
    return sha256(json.dumps(tree(node), ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def inventory(path, expected=None):
    checksum = sha256(path.read_bytes()).hexdigest()
    if expected is not None and checksum != expected:
        raise ValueError('original source ZIP pin mismatch: ' + path.name)
    records, components, rules = [], [], []
    constructs = Counter()
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('original source CRC mismatch')
        for name in sorted(archive.namelist()):
            if not name.endswith('.xml'):
                continue
            raw = archive.read(name)
            root = ET.fromstring(raw)
            rules += [n.get('id') for n in root.iter() if tag(n) == 'Rule']
            for index, oval in enumerate(n for n in root.iter() if tag(n) == 'oval_definitions'):
                for section in oval:
                    if tag(section) in ('objects', 'states', 'variables'):
                        constructs[tag(section)] += len(section)
                constructs.update(sets=sum(tag(n) == 'set' for n in oval.iter()),
                                  filters=sum(tag(n) == 'filter' for n in oval.iter()),
                                  variable_references=sum('var_ref' in n.attrib for n in oval.iter()))
                component = {'member': name, 'index': index, 'xml_sha256': sha256(raw).hexdigest(),
                             'oval_tree_sha256': fingerprint(oval)}
                components.append((component, oval))
                for section in oval:
                    if tag(section) not in ('definitions', 'tests'):
                        continue
                    for n in section:
                        record = {'kind': 'definition' if tag(section) == 'definitions' else 'test',
                            'id': n.get('id'), 'version': n.get('version'), 'type': n.tag,
                            'member': name, 'oval_component_index': index,
                            'source_tree_sha256': fingerprint(n),
                            'status': 'unverified_original_source_not_converted_in_this_audit'}
                        if record['kind'] == 'test':
                            record.update(check=n.get('check', 'all'),
                                check_existence=n.get('check_existence', 'at_least_one_exists'),
                                state_operator=n.get('state_operator', 'AND'),
                                object_refs=[c.get('object_ref') for c in n if tag(c) == 'object'],
                                state_refs=[c.get('state_ref') for c in n if tag(c) == 'state'])
                        else:
                            record.update(test_refs=[c.get('test_ref') for c in n.iter() if tag(c) == 'criterion'],
                                definition_refs=[c.get('definition_ref') for c in n.iter()
                                                 if tag(c) == 'extend_definition'])
                        records.append(record)
    return {'file': path.name, 'zip_sha256': checksum, 'original_rule_ids': rules,
            'construct_counts': dict(constructs),
            'components': [x[0] for x in components], 'records': records}, components


def run(inputs, current_authoring, output, migration_report):
    migration = json.loads(migration_report.read_text())
    if (migration.get('status') != 'REVERSIBLE_REVIEW_GRAMMAR_MIGRATION_ONLY'
            or migration.get('original_scap_import') is not False
            or migration['output_sha256']['json'] != sha256(current_authoring.read_bytes()).hexdigest()):
        raise ValueError('review migration provenance does not match authoring archive')
    sources, models, verified, normalizations = {}, {}, [], []
    with tempfile.TemporaryDirectory() as td:
        for platform, (filename, checksum) in FILES.items():
            path = inputs / filename
            source, components = inventory(path, checksum)
            source.update(repository='niwc-atlantic/scap-content-library', revision=PIN,
                          source_path='Current/' + filename)
            models[platform] = []
            for i, (_, component) in enumerate(components):
                p = Path(td) / f'{platform}-{i}.xml'
                p.write_bytes(ET.tostring(component))
                models[platform].append(Model(p))
            sources[platform] = source
        for platform, rule, definition in PROOFS:
            fixture = ROOT / 'research/assessment-simplification/evidence' / platform / rule / 'source-oval.xml'
            source_model = Model(fixture)
            matches = [m for m in models[platform] if definition in m.definitions
                       and m.definition(definition) == source_model.definition(definition)]
            if len(matches) != 1:
                raise ValueError('source fixture not uniquely matched to original SCAP: ' + definition)
            native, evidence = convert(fixture, definition, assessment_id=rule.lower() + '-source-audit-assessment')
            proof = {'platform': platform, 'rule': rule, 'definition_id': definition,
                     'fixture': fixture.relative_to(ROOT).as_posix(),
                     'fixture_sha256': sha256(fixture.read_bytes()).hexdigest(),
                     'original_scap_zip_sha256': sources[platform]['zip_sha256'],
                     'original_root_semantics_match': True,
                     'native_assessment_sha256': sha256(json.dumps(native, sort_keys=True,
                         ensure_ascii=False, separators=(',', ':')).encode()).hexdigest(),
                     'test_ids': sorted(source_model.tests), 'packaged_graph_equivalence': False,
                     'evidence_scope': 'bounded standalone original-source admission, not migrated package parity',
                     'normalizations': evidence.get('test_existence_normalizations', [])}
            verified.append(proof)
            affected = set(proof['test_ids'])
            normalized_ids = {r['source_test_id'] for r in proof['normalizations']}
            for record in sources[platform]['records']:
                if record['kind'] == 'definition' and record['id'] == definition:
                    record['status'] = 'verified_standalone_original_source_root_not_package_parity'
                    record['approved_normalization_required'] = bool(normalized_ids)
                if record['kind'] == 'test' and record['id'] in affected:
                    record['status'] = 'covered_by_verified_standalone_source_root_not_package_parity'
                    record['approved_normalization_required'] = record['id'] in normalized_ids
            normalizations += proof['normalizations']
        oracle = attest_oracle_source(inputs / FILES['oracle_linux_9'][0])
        normalizations.append({'platform': 'oracle_linux_9', 'scope': 'approved review-archive exception only',
                               'original_oval': oracle, 'original_oval_equivalence': False})
    docs = authoring(current_authoring)
    migrations = [{'path': path, 'id': ident, 'mode': doc['assessment']['mode'],
                   'provenance': 'historical_review_archive_migration',
                   'packaged_original_oval_equivalence': 'unverified'}
                  for (kind, ident), (path, doc) in sorted(docs.items()) if kind == 'assessment']
    totals = Counter()
    for platform, source in sources.items():
        c = Counter(r['kind'] for r in source['records'])
        c['verified_definition_roots'] = sum(r['kind'] == 'definition' and r['status'].startswith('verified_')
                                              for r in source['records'])
        c['covered_source_tests'] = sum(r['kind'] == 'test' and r['status'].startswith('covered_')
                                       for r in source['records'])
        c['definition_roots_with_approved_normalization'] = sum(
            r['kind'] == 'definition' and r.get('approved_normalization_required', False)
            for r in source['records'])
        c['covered_tests_with_approved_normalization'] = sum(
            r['kind'] == 'test' and r.get('approved_normalization_required', False)
            for r in source['records'])
        source['counts'] = dict(c)
        totals.update(c)
    automated = sum(r['mode'] == 'automated' for r in migrations)
    percentages = {
        'standalone_definition_root_percent': 100 * totals['verified_definition_roots'] / totals['definition'],
        'standalone_source_test_percent': 100 * totals['covered_source_tests'] / totals['test'],
        'packaged_automated_assessment_original_equivalence_percent': 0.0,
    }
    report = {'status': 'ORIGINAL_SOURCE_LEDGER_NOT_SCANNER_OR_FULL_CONVERSION_CLAIM',
              'denominator_scope': 'sum of declarations within each original benchmark/OVAL component; '
                                   'do not collapse cross-benchmark shared IDs',
              'counts': dict(totals), 'percentages': percentages,
              'migrated_assessments': len(migrations), 'migrated_automated_assessments': automated,
              'review_archive_migration': {k: migration[k] for k in
                  ('source_sha256', 'output_sha256', 'documents', 'changed_documents', 'counts',
                   'source_inverse', 'yaml_json_parity', 'original_scap_import')},
              'packaged_automated_assessments_with_original_equivalence_proof': 0,
              'unverified_constructs': 'All unverified records retain types, quantifiers and refs; '
                  'not attempted is not classified as unsupported. No broad converter sweep was run.',
              'standalone_proofs': verified, 'approved_source_specific_normalizations': normalizations,
              'sources': sources, 'assessment_migration_inventory': migrations,
              'scanner_evaluated': False, 'publisher_trust_verified': False}
    write_ledger(report, output)
    return report


def write_ledger(report, output):
    """Compact inspectable CSV declarations; summary never replaces denominators."""
    output.parent.mkdir(parents=True, exist_ok=True)
    records = output.with_name(output.stem + '-original-records.csv')
    fields = ['platform', 'kind', 'id', 'version', 'type', 'member', 'oval_component_index',
              'source_tree_sha256', 'status', 'approved_normalization_required',
              'check_existence', 'check', 'state_operator', 'object_refs', 'state_refs', 'test_refs', 'definition_refs']
    with records.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for platform, source in report['sources'].items():
            for record in source['records']:
                row = {k: record.get(k, '') for k in fields}
                row['platform'] = platform
                writer.writerow({k: json.dumps(v, separators=(',', ':')) if isinstance(v, list) else v
                                 for k, v in row.items()})
    migrations = output.with_name(output.stem + '-migrated-assessments.csv')
    with migrations.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['path', 'id', 'mode', 'provenance',
                                                    'packaged_original_oval_equivalence'])
        writer.writeheader()
        writer.writerows(report['assessment_migration_inventory'])
    summary = {**report, 'sources': {platform: {k: v for k, v in source.items() if k != 'records'}
                                     for platform, source in report['sources'].items()}}
    del summary['assessment_migration_inventory']
    summary['record_inventories'] = [{'path': path.name, 'sha256': sha256(path.read_bytes()).hexdigest(),
                                       'bytes': path.stat().st_size} for path in (records, migrations)]
    output.write_text(json.dumps(summary, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs-dir', required=True, type=Path)
    parser.add_argument('--authoring-json', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--migration-report', required=True, type=Path)
    a = parser.parse_args()
    result = run(a.inputs_dir, a.authoring_json, a.report, a.migration_report)
    print(json.dumps({'counts': result['counts'], 'percentages': result['percentages']}))
