#!/usr/bin/env python3
"""Independent six-bundle acceptance and actual-package adversarial checks (#251).

Never imports or invokes the compiler. Expected bytes are the reviewed 4e1ec2737
checkpoint; altered, untrusted packages are checked without assuming those hashes.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import zipfile

from verify_v04_package_consumer import authoring, canonical, require, verify, archive_members

EXPECTED = {
    'apache_server_2-4_unix_server': 'f0dc8f1a2f7b1fbdc3dcedc2709b8bc2cd9f4827e93bf9d751708e02b153bc4e',
    'ms_windows_11': 'fd6e8a15ca48979650a289dc0a9476d0f2abf365ddf342f4a08bb685180d2a3e',
    'ms_windows_server_2025': 'c3b08d822ec363a6dadf2f3a3e430b7a3796a784a1f5f96475a4b70dc88577f4',
    'ms_windows_server_dns': '82fdb4d0ea0bd614b799f2de595618a0511d31db600b25bdb5ab3568b28ec834',
    'oracle_linux_9': '61e3336499c27f2f0deb635ebecc68344c18adb923cfad6e6466ba4dcc712b4b',
    'rhel_9': '170b5013d90dbcb197e81b681eae5121ee923ab7c6b28a4f5784034059b5a809',
}


def corrupt(source, target, kind):
    members = archive_members(source)
    manifest = json.loads(members['META-INF/manifest.json'])
    if kind == 'stale_member_hash':
        row = next(iter(manifest['objects'].values()))
        members[row['path']] += b' '
    elif kind == 'unsupported_version':
        manifest['format_version'] = '9.0.0'
    else:
        if kind == 'unresolved_reference_rehashed':
            row = next(r for r in manifest['objects'].values() if r['type'] == 'rule')
            content = json.loads(members[row['path']])
            next(iter(content['rule']['assessment_choices'].values()))['assessment'] = 'unresolved-assessment'
        elif kind == 'forged_program_operands_rehashed':
            row = next(iter(manifest['build_provenance']['compiled_programs'].values()))
            content = json.loads(members[row['path']])
            operand = content['test_instructions'][0]['operands']['require']
            operand['items_found'] = 'none' if operand['items_found'] != 'none' else 'one_or_more'
        else:
            raise ValueError('unknown mutation')
        members[row['path']] = canonical(content)
        row.update(sha256=sha256(members[row['path']]).hexdigest(), size=len(members[row['path']]))
    members['META-INF/manifest.json'] = canonical(manifest)
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in members.items():
            archive.writestr(name, data)


def run(bundle_dir, json_source, yaml_source, output):
    js, ya = authoring(json_source), authoring(yaml_source)
    require({k: d for k, (_, d) in js.items()} == {k: d for k, (_, d) in ya.items()}, 'source format mismatch')
    require({p.stem for p in bundle_dir.glob('*.scapng')} == set(EXPECTED), 'six bundle inventory mismatch')
    results, negatives = {}, []
    for name, checksum in EXPECTED.items():
        path = bundle_dir / (name + '.scapng')
        require(sha256(path.read_bytes()).hexdigest() == checksum, 'reviewed bundle hash mismatch: ' + name)
        results[name] = verify(path, source=js)
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / 'corrupted.scapng'
            for kind in ('stale_member_hash', 'unsupported_version', 'unresolved_reference_rehashed',
                         'forged_program_operands_rehashed'):
                corrupt(path, target, kind)
                try:
                    verify(target)
                except ValueError as exc:
                    negatives.append({'bundle': name, 'case': kind, 'rejected': True,
                                      'diagnostic': str(exc)[:300]})
                else:
                    raise AssertionError('corrupted package accepted: ' + name + '/' + kind)
    result = {'status': 'SIX_BUNDLE_INDEPENDENT_ACCEPTANCE_PASS_NOT_SCANNER_OR_TRUST',
              'reviewed_checkpoint': '4e1ec2737c7b43002282a1d6762896b25b162060',
              'source_hashes': {'json': sha256(json_source.read_bytes()).hexdigest(),
                                'yaml': sha256(yaml_source.read_bytes()).hexdigest()},
              'source_documents': len(js), 'results': results, 'negative_cases': negatives,
              'programs': sum(r['programs'] for r in results.values()),
              'test_references': sum(r['tests'] for r in results.values()),
              'bundle_hashes_match_reviewed_reproduction': True,
              'yaml_json_parsed_and_packaged_graphs_equal': True,
              'scanner_evaluated': False, 'publisher_trust_verified': False}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundles-dir', required=True, type=Path)
    parser.add_argument('--source-json', required=True, type=Path)
    parser.add_argument('--source-yaml', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    a = parser.parse_args()
    result = run(a.bundles_dir, a.source_json, a.source_yaml, a.report)
    print(json.dumps({'status': result['status'], 'programs': result['programs'],
                      'test_references': result['test_references'], 'rejections': len(result['negative_cases'])}))
