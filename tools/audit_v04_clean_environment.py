#!/usr/bin/env python3
"""Pinned clean-extract public entrypoint acceptance; no tags or releases (#251).

Use a separately created venv installed from the acceptance hash lock. Input XML
is explicit and pinned; no original-source corpus import or scanner is performed.
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = '6966982d66e004f77ceb9e5ccceb5161275a79729d4178f290f99efd3b8b84a7'
WRAP = r'''
from pathlib import Path
import sys,json,yaml
root,out,assessment=map(Path,sys.argv[1:]);sys.path.insert(0,str(root/'tools'))
import test_v04_public_cli_smoke as smoke
assert Path(smoke.__file__).is_relative_to(root)
docs=smoke.schema_valid_docs();native=json.loads(assessment.read_text())
docs['authoring/demo/assessments/a1.json']=native
docs['authoring/demo/rules/r1.json']['rule']['assessment_choices']['automated']['assessment']=native['assessment']['id']
docs['authoring/demo/applicability.json']={'applicability':{'id':'demo-applicability','conditions':{}}}
out.mkdir();smoke.authoring_archives(docs,out)
for name,doc in docs.items():
 p=out/name.removesuffix('.json');p=p.with_suffix(p.suffix+'.yaml')
 if 'benchmark' in doc:p=p.with_name('benchmark.yaml')
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(yaml.safe_dump(doc))
print(json.dumps({'wrapper':'synthetic closed Benchmark/Rule/Assessment/catalog', 'helper':smoke.__file__}))
'''
VERIFY = r'''
from pathlib import Path
import sys,json
root,bundle=map(Path,sys.argv[1:]);sys.path.insert(0,str(root/'tools'))
import v04_native_bundle_compiler as c
assert Path(c.__file__).is_relative_to(root)
print(json.dumps(c.verify_bundle(bundle.read_bytes())))
'''


def run(repo, ref, python, source, evidence):
    if sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError('original Self-Assertion family source SHA mismatch')
    evidence = evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    cwd = evidence / 'outside-checkout'
    cwd.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith('PYTHON')}
    commands = []
    def execute(name, args):
        proc = subprocess.run(list(map(str, args)), cwd=cwd, env=env,
                              text=True, capture_output=True)
        (evidence / (name + '.log')).write_text(proc.stdout + proc.stderr)
        commands.append({'step': name, 'argv': list(map(str, args)), 'cwd': str(cwd),
                         'returncode': proc.returncode})
        (evidence / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
        proc.check_returncode()
        return proc.stdout
    distributions = json.loads(execute('environment', [python, '-I', '-c',
        "import sys,json,importlib.metadata as m;assert sys.prefix!=sys.base_prefix;"
        "print(json.dumps({'python':sys.version,'distributions':{d.metadata['Name']:d.version for d in m.distributions()}}))"]))
    # Two independently written archives at the identical Git ref must match.
    for suffix in ('first', 'repeat'):
        execute('build-' + suffix, [python, '-E', '-s', repo / 'tools/build_versioned_toolchain.py',
            '--repo', repo, '--version', '0.4.0', '--ref', ref,
            '--output-dir', evidence / suffix])
    archive, = (evidence / 'first').glob('*.zip')
    repeat, = (evidence / 'repeat').glob('*.zip')
    if archive.read_bytes() != repeat.read_bytes():
        raise ValueError('pinned toolchain archive is not reproducible')
    extract = evidence / 'extract'
    checked = json.loads(execute('verify-toolchain', [python, '-E', '-s',
        repo / 'tools/build_versioned_toolchain.py', '--verify', archive]))
    with zipfile.ZipFile(archive) as z:
        z.extractall(extract)  # The public verifier checked safe paths and exact inventory.
    root = extract / 'scap-ng-0.4.0-toolchain'
    if (root / '.git').exists() or not (root / 'tools/verify_v04_package_consumer.py').is_file():
        raise ValueError('expected an independent-verifier candidate snapshot without .git')
    execute('verify-extracted-toolchain', [python, '-E', '-s', root / 'tools/build_versioned_toolchain.py',
                                         '--verify', archive])
    copied = cwd / 'original-family.xml'
    shutil.copyfile(source, copied)
    assessment = evidence / 'family.json'
    execute('convert', [python, '-E', '-s', root / 'tools/scap_converter_core.py',
        '--source-xml', copied, '--definition-id', 'oval:org.mitre.oval.test:def:95',
        '--assessment-id', 'clean-source-family-assessment', '--output', assessment,
        '--evidence', evidence / 'source-proof.json'])
    execute('wrap', [python, '-I', '-c', WRAP, root, evidence / 'authoring', assessment])
    execute('validate', [python, '-E', '-s', root / 'tools/validate_native_json_schemas.py',
        evidence / 'authoring/authoring', '--schema-dir', root / 'schema/v0.4.0',
        '--report', evidence / 'validator.json'])
    validation = json.loads((evidence / 'validator.json').read_text())
    if (validation['documents_checked'], validation['valid'], validation['unclassified_yaml']) != (4, 4, 0):
        raise ValueError('public validator did not actually validate all four documents')
    execute('compile', [python, '-E', '-s', root / 'tools/v04_native_bundle_compiler.py',
        '--json-archive', evidence / 'authoring/json.zip', '--yaml-archive', evidence / 'authoring/yaml.zip',
        '--output-dir', evidence / 'compiled', '--report', evidence / 'compiler.json'])
    bundle = evidence / 'compiled/demo.scapng'
    execute('existing-verifier', [python, '-I', '-c', VERIFY, root, bundle])
    execute('independent-consumer', [python, '-E', '-s', root / 'tools/verify_v04_package_consumer.py',
        bundle, '--source-json', evidence / 'authoring/json.zip',
        '--source-yaml', evidence / 'authoring/yaml.zip', '--report', evidence / 'consumer.json'])
    result = {'status': 'CLEAN_PINNED_PUBLIC_ENTRYPOINTS_PASS_NOT_SCANNER_OR_TRUST',
              'source_commit': checked['source_commit'], 'toolchain_files': checked['files'],
              'toolchain_sha256': sha256(archive.read_bytes()).hexdigest(),
              'repeat_toolchain_bytes_equal': True, 'source_xml_sha256': SOURCE_SHA,
              'bundle_sha256': sha256(bundle.read_bytes()).hexdigest(),
              'consumer': json.loads((evidence / 'consumer.json').read_text()),
              'validator_documents': validation['documents_checked'], 'environment': distributions,
              'commands': commands, 'scanner_evaluated': False, 'publisher_trust_verified': False}
    (evidence / 'clean-report.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=ROOT)
    p.add_argument('--ref', required=True)
    p.add_argument('--python', required=True, type=Path)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--evidence-dir', required=True, type=Path)
    a = p.parse_args()
    result = run(a.repo.resolve(), a.ref, a.python.resolve(), a.source.resolve(), a.evidence_dir)
    print(json.dumps({'status': result['status'], 'source_commit': result['source_commit'],
                      'toolchain_sha256': result['toolchain_sha256']}))
