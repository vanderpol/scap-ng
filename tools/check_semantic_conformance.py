"""Validate immutable native conformance fixtures; optionally execute a real RI binary."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'conformance/0.4/model-a'


def check(binary=None):
    freeze = json.loads((ROOT / 'conformance/0.4/frozen-schema-sha256.json').read_text())
    for path, expected in freeze['files'].items():
        assert sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    schemas = [json.loads(p.read_text()) for p in (ROOT / 'schema').glob('*.schema.json')]
    registry = Registry().with_resources((s['$id'], Resource.from_contents(s)) for s in schemas)
    validator = Draft202012Validator(next(s for s in schemas if s['$id'].endswith('/assessment.schema.json')), registry=registry)
    manifest = json.loads((PACK / 'manifest.json').read_text())
    cases = []
    for row in manifest['cases']:
        raw = (PACK / row['assessment']).read_bytes()
        assert sha256(raw).hexdigest() == row['sha256'], row['id']
        document = json.loads(raw)
        validator.validate(document)
        result = {'id': row['id'], 'syntax_valid': True, 'executed': False}
        if binary:
            request = {'schema_family_sha256': manifest['schema_family_sha256'],
                       'assessment_document': document, 'bindings': {}}
            proc = subprocess.run([str(binary), '--test', row['test']], input=json.dumps(request),
                                  text=True, capture_output=True, timeout=20)
            assert proc.returncode == 0, (row['id'], proc.stdout, proc.stderr)
            actual = json.loads(proc.stdout)
            assert actual['technical_outcome'] == row['expected']['technical_outcome'], (row['id'], actual)
            assert actual['item_id'] == '' and actual['outcome_scope'] == 'test'
            for key in ('items_found', 'items_satisfying', 'values_found', 'values_matching'):
                assert actual['cardinality'][key] == row['expected'][key], (row['id'], actual)
            result.update(executed=True, exit_code=proc.returncode, actual=actual,
                          request_keys=sorted(request))
        cases.append(result)
    return {'schema_commit': manifest['schema_commit'], 'cases': cases,
            'schema_validated': len(cases), 'actually_executed': sum(c['executed'] for c in cases),
            'expected_results_sent_to_engine': False, 'scanner_equivalence': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ri-binary', type=Path)
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    if args.output and args.output.exists():
        p.error('refusing to overwrite evidence')
    result = check(args.ri_binary)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(f"{result['schema_validated']} schema-valid fixtures; {result['actually_executed']} actually executed.")


if __name__ == '__main__':
    main()
