#!/usr/bin/env python3
"""Revalidate pinned six-STIG review source under the approved 0.4 grammar.

This is a bounded, reversible *authoring review archive* adapter, not an
original-SCAP importer or evidence of OVAL/scanner equivalence. The original
SCAP source proof of the input release must be evaluated independently.

Refs #232 #233 #251.
"""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

from build_v04_canonical_six_stigs import promote, recover, render_authoring
from v04_a_authoring_graph_index import read_authoring_archive

ORACLE_SOURCE_SHA256 = '6733abd693380b43b2350c2692775e4ff902f895f16899db97b34fecf7fba74d'
ORACLE_PATH = 'authoring/oracle_linux_9/assessments/automated/SV-271844.automated.json'
ORACLE_TEST = 'confirm-interactive-user-s-home-directories-exist-test'
ORACLE_OVAL_TEST = 'oval:navy.navwar.niwcatlantic.scc.rhel8:tst:27184401'
ORACLE_OVAL_STATE = 'oval:navy.navwar.niwcatlantic.scc.rhel8:ste:27184401'
ORACLE_OVAL_OBJECT = 'oval:navy.navwar.niwcatlantic.scc.rhel8:obj:27184401'
ORACLE_OLD_REQUIRE = {'items': 'may_be_absent', 'all_items_must': [
    {'fields': {'stderr_line': {'field_requirement': 'none_exist',
                                'matches_regex': '.*'}}}]}


def attest_oracle_source(path):
    """Pin the *unmodified* published source XML and its exact State binding."""
    if fingerprint(path) != ORACLE_SOURCE_SHA256:
        raise ValueError('approved Oracle Linux SCAP source SHA-256 mismatch')
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('Oracle SCAP archive CRC mismatch')
        members = [n for n in archive.namelist() if n.endswith('.xml')]
        if len(members) != 1:
            raise ValueError('expected one published Oracle SCAP datastream')
        raw = archive.read(members[0])
    root = ET.fromstring(raw)
    ids = {node.get('id'): node for node in root.iter() if node.get('id')}
    test = ids.get(ORACLE_OVAL_TEST)
    state = ids.get(ORACLE_OVAL_STATE)
    if (test is None or not test.tag.endswith('}shellcommand_test')
            or test.get('check_existence') != 'any_exist' or test.get('check') != 'all'
            or state is None or not state.tag.endswith('}shellcommand_state')):
        raise ValueError('pinned Oracle OVAL Test/State identity or existence changed')
    refs = {(child.tag.rsplit('}', 1)[-1], child.get('object_ref'), child.get('state_ref'))
            for child in test}
    if refs != {('object', ORACLE_OVAL_OBJECT, None),
                ('state', None, ORACLE_OVAL_STATE)}:
        raise ValueError('Oracle Test no longer has the approved Object/State graph')
    children = list(state)
    if (len(children) != 1 or not children[0].tag.endswith('}stderr_line')
            or children[0].attrib != {'check_existence': 'none_exist',
                                     'operation': 'pattern match'}
            or children[0].text != '.*'):
        raise ValueError('Oracle OVAL absence operand differs from owner-approved exception')
    return {'source_zip_sha256': ORACLE_SOURCE_SHA256,
            'source_xml_sha256': sha256(raw).hexdigest(),
            'source_member': members[0], 'source_test_id': ORACLE_OVAL_TEST,
            'source_state_id': ORACLE_OVAL_STATE, 'source_object_id': ORACLE_OVAL_OBJECT,
            'source_test_attributes': dict(test.attrib),
            'source_field_attributes': dict(children[0].attrib),
            'source_field_text': children[0].text,
            'decision': 'owner-approved Oracle SV-271844 redundant universal matcher removal 2026-10-24'}


def normalized_oracle_document(name, original, source_attestation):
    if name != ORACLE_PATH:
        return original, None
    if source_attestation is None:
        raise ValueError('pinned original Oracle OVAL attestation required')
    source_test = original['assessment']['tests'][ORACLE_TEST]
    if (source_test.get('capability') != 'independent.shellcommand'
            or source_test.get('require') != ORACLE_OLD_REQUIRE):
        raise ValueError('Oracle review predicate does not match approved source shape')
    normalized = deepcopy(original)
    normalized_field = normalized['assessment']['tests'][ORACLE_TEST]['require'][
        'all_items_must'][0]['fields']['stderr_line']
    if normalized_field.pop('matches_regex') != '.*':
        raise ValueError('Oracle universal matcher unexpectedly changed')
    # Exact inverse to the immutable review document; original OVAL is retained
    # separately in the source-attested migration report, never edited in place.
    reconstructed = deepcopy(normalized)
    reconstructed['assessment']['tests'][ORACLE_TEST]['require'][
        'all_items_must'][0]['fields']['stderr_line']['matches_regex'] = '.*'
    if reconstructed != original:
        raise ValueError('Oracle owner-approved narrow source inversion failed')
    return normalized, {'path': name, 'test_id': ORACLE_TEST,
                        'original_requirement': deepcopy(source_test['require']),
                        'normalized_source_requirement': deepcopy(
                            normalized['assessment']['tests'][ORACLE_TEST]['require']),
                        'original_document_sha256': sha256(json.dumps(
                            original, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
                        'original_oval': source_attestation}


def fingerprint(path):
    return sha256(path.read_bytes()).hexdigest()


def paired_documents(json_path, yaml_path):
    json_docs = read_authoring_archive(json_path, 'json')
    yaml_docs = read_authoring_archive(yaml_path, 'yaml')
    json_names = set(json_docs)
    yaml_names = {name.removesuffix('.yaml') + '.json': name for name in yaml_docs}
    if json_names != set(yaml_names):
        raise ValueError('six-STIG YAML/JSON member sets differ')
    if len(json_names) != 4012:
        raise ValueError(f'expected 4,012 source documents, found {len(json_names)}')
    for name, source in json_docs.items():
        if source != yaml_docs[yaml_names[name]]:
            raise ValueError(f'original YAML/JSON graph differs: {name}')
    return json_docs


def upgrade_documents(documents, *, oracle_attestation=None):
    """Apply only the checked existing legacy-review bridge; fail closed."""
    outputs = {}
    counts = Counter()
    changed = []
    blockers = []
    exceptions = []
    for name, original in sorted(documents.items()):
        try:
            normalized, exception = normalized_oracle_document(name, original, oracle_attestation)
            upgraded, statistics = promote(normalized, legacy_review=True)
            recover(upgraded, normalized, legacy_review=True)
        except ValueError as exc:
            blockers.append({'path': name, 'reason': str(exc)})
            continue
        if upgraded != original:
            changed.append(name)
        outputs[name] = upgraded
        counts.update(statistics)
        if exception:
            exceptions.append(exception)
    return outputs, counts, changed, blockers, exceptions


def write_archive(path, documents, fmt):
    if fmt not in ('json', 'yaml'):
        raise ValueError('unsupported format')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for json_name, document in sorted(documents.items()):
            name = json_name if fmt == 'json' else json_name.removesuffix('.json') + '.yaml'
            archive.writestr(name, render_authoring(document, is_yaml=fmt == 'yaml'))
        archive.writestr('READ-ME-FIRST.txt',
            'SCAP-NG 0.4.0 six-STIG authoring grammar migration (Refs #232 #233 #251).\n'
            'Source is a checksum-pinned prior review archive; no fresh original\n'
            'SCAP 1.4 import, signer-trust or scanner equivalence is claimed.\n')


def run(json_path, yaml_path, out_json, out_yaml, report_path, expected_json,
        expected_yaml, oracle_source):
    if out_json.resolve() == out_yaml.resolve():
        raise ValueError('JSON and YAML output paths must differ')
    if out_json.exists() or out_yaml.exists():
        raise FileExistsError('refusing to overwrite an existing review archive')
    source_hashes = {'json': fingerprint(json_path), 'yaml': fingerprint(yaml_path)}
    if source_hashes != {'json': expected_json, 'yaml': expected_yaml}:
        raise ValueError('source archive SHA-256 does not match explicit source pins')
    attestation = attest_oracle_source(oracle_source)
    source = paired_documents(json_path, yaml_path)
    output, counts, changed, blockers, exceptions = upgrade_documents(
        source, oracle_attestation=attestation)
    if blockers:
        report = {'status': 'BLOCKED_UNREPRESENTABLE_SOURCE_REQUIREMENTS',
                  'source_sha256': source_hashes, 'documents': len(source),
                  'converted_documents': len(output), 'blocked_documents': len(blockers),
                  'blockers': blockers, 'counts': dict(counts),
                  'approved_source_exceptions': exceptions,
                  'output_archives_written': False, 'scanner_evaluated': False}
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + '\n')
        return report
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_yaml.parent.mkdir(parents=True, exist_ok=True)
    write_archive(out_json, output, 'json')
    write_archive(out_yaml, output, 'yaml')
    if paired_documents(out_json, out_yaml) != output:
        raise ValueError('output YAML/JSON parsed graph mismatch')
    # Full schema/reference/compiler verification is the *subsequent* independent
    # gate; never label this migration step itself compiled or release-ready.
    report = {'status': 'REVERSIBLE_REVIEW_GRAMMAR_MIGRATION_ONLY',
              'source_sha256': source_hashes,
              'output_sha256': {'json': fingerprint(out_json), 'yaml': fingerprint(out_yaml)},
              'documents': len(output), 'changed_documents': len(changed),
              'counts': dict(counts), 'changed_paths': changed,
              'approved_source_exceptions': exceptions,
              'source_inverse': 'PASS', 'yaml_json_parity': 'PASS',
              'original_scap_import': False, 'schema_validated': False,
              'scanner_evaluated': False, 'publisher_trust_verified': False}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-json', type=Path, required=True)
    p.add_argument('--source-yaml', type=Path, required=True)
    p.add_argument('--expected-json-sha256', required=True)
    p.add_argument('--expected-yaml-sha256', required=True)
    p.add_argument('--oracle-source-zip', type=Path, required=True,
                   help='exact original NIWC Oracle Linux 9 signed SCAP 1.4 ZIP')
    p.add_argument('--out-json', type=Path, required=True)
    p.add_argument('--out-yaml', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    result = run(a.source_json, a.source_yaml, a.out_json, a.out_yaml, a.report,
                 a.expected_json_sha256, a.expected_yaml_sha256, a.oracle_source_zip)
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('changed_paths', 'blockers')}, indent=2))
    if result['status'] != 'REVERSIBLE_REVIEW_GRAMMAR_MIGRATION_ONLY':
        raise SystemExit(2)
