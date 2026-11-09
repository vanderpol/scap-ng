"""Validate immutable native conformance fixtures; optionally execute a real RI binary."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import yaml

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'conformance/0.4/model-a'


def check(binary=None, supplied_evidence=False):
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
    if supplied_evidence:
        catalog = json.loads((ROOT / 'conformance/0.4/supplied-evidence.json').read_text())
        for row in catalog['cases']:
            raw = (ROOT / row['fixture']).read_bytes()
            assert sha256(raw).hexdigest() == row['sha256']
            fixture = yaml.safe_load(raw)
            document = {'assessment': fixture['assessment']}
            validator.validate(document)
            result = {'id': fixture['id'], 'syntax_valid': True, 'executed': False}
            if binary:
                test_id = fixture['assessment']['evaluate']['test']
                request = {'schema_family_sha256': catalog['schema_family_sha256'],
                           'assessment_document': document,
                           'bindings': {'/assessment/tests/' + test_id: {
                               'collection_result': fixture['collection_result'],
                               'collected_items': fixture['collected_items']}}}
                proc = subprocess.run([str(binary)], input=json.dumps(request), text=True,
                                      capture_output=True, timeout=20)
                assert proc.returncode == 0, (row['fixture'], proc.stdout, proc.stderr)
                actual = json.loads(proc.stdout)
                assert actual['technical_outcome'] == row['expected_technical_outcome'], actual
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
    p.add_argument('--supplied-evidence', action='store_true')
    args = p.parse_args()
    if args.output and args.output.exists():
        p.error('refusing to overwrite evidence')
    result = check(args.ri_binary, args.supplied_evidence)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(f"{result['schema_validated']} schema-valid fixtures; {result['actually_executed']} actually executed.")


if __name__ == '__main__':
    main()
