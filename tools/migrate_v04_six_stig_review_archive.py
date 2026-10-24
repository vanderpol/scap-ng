#!/usr/bin/env python3
"""Revalidate pinned six-STIG review source under the approved 0.4 grammar.

This is a bounded, reversible *authoring review archive* adapter, not an
original-SCAP importer or evidence of OVAL/scanner equivalence. The original
SCAP source proof of the input release must be evaluated independently.

Refs #232 #233 #251.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import zipfile

from build_v04_canonical_six_stigs import promote, recover, render_authoring
from v04_a_authoring_graph_index import read_authoring_archive


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


def upgrade_documents(documents):
    """Apply only the checked existing legacy-review bridge; fail closed."""
    outputs = {}
    counts = Counter()
    changed = []
    blockers = []
    for name, original in sorted(documents.items()):
        try:
            upgraded, statistics = promote(original, legacy_review=True)
            recover(upgraded, original, legacy_review=True)
        except ValueError as exc:
            blockers.append({'path': name, 'reason': str(exc)})
            continue
        if upgraded != original:
            changed.append(name)
        outputs[name] = upgraded
        counts.update(statistics)
    return outputs, counts, changed, blockers


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


def run(json_path, yaml_path, out_json, out_yaml, report_path, expected_json, expected_yaml):
    if out_json.resolve() == out_yaml.resolve():
        raise ValueError('JSON and YAML output paths must differ')
    if out_json.exists() or out_yaml.exists():
        raise FileExistsError('refusing to overwrite an existing review archive')
    source_hashes = {'json': fingerprint(json_path), 'yaml': fingerprint(yaml_path)}
    if source_hashes != {'json': expected_json, 'yaml': expected_yaml}:
        raise ValueError('source archive SHA-256 does not match explicit source pins')
    source = paired_documents(json_path, yaml_path)
    output, counts, changed, blockers = upgrade_documents(source)
    if blockers:
        report = {'status': 'BLOCKED_UNREPRESENTABLE_SOURCE_REQUIREMENTS',
                  'source_sha256': source_hashes, 'documents': len(source),
                  'converted_documents': len(output), 'blocked_documents': len(blockers),
                  'blockers': blockers, 'counts': dict(counts),
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
    p.add_argument('--out-json', type=Path, required=True)
    p.add_argument('--out-yaml', type=Path, required=True)
    p.add_argument('--report', type=Path, required=True)
    a = p.parse_args()
    result = run(a.source_json, a.source_yaml, a.out_json, a.out_yaml, a.report,
                 a.expected_json_sha256, a.expected_yaml_sha256)
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('changed_paths', 'blockers')}, indent=2))
    if result['status'] != 'REVERSIBLE_REVIEW_GRAMMAR_MIGRATION_ONLY':
        raise SystemExit(2)
