#!/usr/bin/env python3
"""Bounded pinned-production CLI acceptance audit; no scanner or release claim.

Uses the existing production fixtures and an explicitly synthetic policy wrapper
from the maintained integration harness. Does not convert a complete Benchmark,
change release gates, sign content, or sweep the corpus. Refs #251.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

from build_v04_canonical_six_stigs import render_authoring
from test_v04_approved_pipeline import CASES, ROOT
from test_v04_field_requirement_conversion import documents
from v04_native_bundle_compiler import MANIFEST_MEMBER, verify_bundle


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    cases = [*CASES, (
        'ms_windows_11', 'SV-253254',
        'a056aafd7326bac213cab63da8c3746a49dfd5fc03f1812426bc8804e6e32926', 1)]
    report = {
        'source_commit': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'schema_sha256': sha256((ROOT / 'schema/v0.4.0/assessment-language.schema.json')
                                .read_bytes()).hexdigest(),
        'policy_wrapper': 'synthetic integration harness; not original Benchmark/Rule conversion',
        'scanner_evaluated': False, 'production_publisher_trust_verified': False,
        'cases': [],
    }
    for platform, rule, expected_hash, test_count in cases:
        source = ROOT / 'research/assessment-simplification/evidence' / platform / rule / 'source-oval.xml'
        if sha256(source.read_bytes()).hexdigest() != expected_hash:
            raise ValueError(f'pinned source changed: {source}')
        root = ET.parse(source).getroot()
        definition = next(n.get('id') for n in root.iter() if n.tag.endswith('}definition'))
        folder = output / rule
        folder.mkdir(parents=True, exist_ok=True)
        convert_command = [sys.executable, str(ROOT / 'tools/scap_converter_core.py'),
            '--source-xml', str(source), '--definition-id', definition,
            '--assessment-id', 'source-' + rule.lower() + '-assessment',
            '--output', str(folder / 'assessment.json'),
            '--evidence', str(folder / 'conversion.json')]
        subprocess.run(convert_command, cwd=ROOT, check=True, capture_output=True, text=True)
        native = json.loads((folder / 'assessment.json').read_text())
        wrapped = documents(native)
        for ext in ('json', 'yaml'):
            (folder / f'assessment.{ext}').write_text(render_authoring(native, is_yaml=ext == 'yaml'))
            with zipfile.ZipFile(folder / f'authoring.{ext}.zip', 'w') as archive:
                for name, doc in sorted(wrapped.items()):
                    archive.writestr(name.removesuffix('.json') + '.' + ext,
                                     render_authoring(doc, is_yaml=ext == 'yaml'))
        compile_command = [sys.executable, str(ROOT / 'tools/v04_native_bundle_compiler.py'),
            '--json-archive', str(folder / 'authoring.json.zip'),
            '--yaml-archive', str(folder / 'authoring.yaml.zip'),
            '--output-dir', str(folder / 'compiled'), '--report', str(folder / 'compile.json')]
        subprocess.run(compile_command, cwd=ROOT, check=True, capture_output=True, text=True)
        bundles = list((folder / 'compiled').glob('*.scapng'))
        if len(bundles) != 1:
            raise ValueError(f'expected one compiled graph: {rule}')
        bundle = bundles[0].read_bytes()
        verified = verify_bundle(bundle)  # Full current schemas; no bypass.
        if (verified['documents'], verified['programs'], verified['tests']) != (3, 1, test_count):
            raise ValueError(f'unexpected compiled inventory: {rule}')
        if verified['signature_verified'] or verified['scanner_evaluated']:
            raise ValueError('unsupported authentication or scanner claim')
        with zipfile.ZipFile(bundles[0]) as archive:
            manifest = json.loads(archive.read(MANIFEST_MEMBER))
            entry, = manifest['build_provenance']['compiled_programs'].values()
            program_bytes = archive.read(entry['path'])
            (folder / 'compiled.json').write_bytes(program_bytes)
            program = json.loads(program_bytes)
        actual = {r['test_id']: r['operands']['require'] for r in program['test_instructions']}
        expected = {k: v['require'] for k, v in native['assessment']['tests'].items()}
        if actual != expected:
            raise ValueError(f'compiled requirements changed: {rule}')
        artifacts = {str(p.relative_to(output)): sha256(p.read_bytes()).hexdigest()
                     for p in sorted(folder.rglob('*')) if p.is_file()}
        report['cases'].append({
            'platform': platform, 'rule': rule, 'source': str(source.relative_to(ROOT)),
            'source_sha256': expected_hash, 'definition_id': definition,
            'source_test_ids': [n.get('id') for n in root.iter()
                                if n.get('id') and n.tag.endswith('_test')],
            'converter_command': convert_command, 'compiler_command': compile_command,
            'compiled_require_operands': 'UNCHANGED', 'verification': verified,
            'artifacts_sha256': artifacts,
        })
    (output / 'acceptance.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output_dir.resolve())
    print(json.dumps({'cases_passed': len(result['cases']), 'report': str(args.output_dir / 'acceptance.json')}))
