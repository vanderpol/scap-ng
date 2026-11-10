#!/usr/bin/env python3
"""Validate linked example syntax and report proof limits; no Test evaluation."""
import argparse
import json
from pathlib import Path

from documentation_examples import Examples
import generate_documentation as reference

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('docs/examples/validation.json')


def report(root=ROOT):
    loader = Examples(root)
    cases = []
    for doc, _ in reference.schemas(root).values():
        for ref, case in loader.load(doc):
            cases.append({'id': case['id'], 'capability': case['capability'], **ref,
                          'schema_validation': 'passed', 'expected': case['expected'],
                          'native_evaluation': 'not_run', 'observed_technical_outcome': None,
                          'reason': 'No qualified current native Object/Require/Item evaluator was available; see EVALUATION.md.'})
    return {'format': 'scap-ng-paired-example-validation-1',
            'totals': {'capabilities': len({c['capability'] for c in cases}), 'examples': len(cases),
                       'syntax_valid': len(cases), 'native_verified': 0, 'native_unverified': len(cases)},
            'cases': sorted(cases, key=lambda c: c['id']), 'source_inputs': dict(sorted(loader.inputs.items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = report()
    text = json.dumps(result, indent=2) + '\n'
    target = ROOT / DEST
    if args.check:
        if not target.exists() or target.read_text() != text:
            raise SystemExit('Stale paired example syntax/proof report')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    print(json.dumps(result['totals'], indent=2))
    print('Syntax checked; native evaluation NOT run. Expectations are not conformance evidence.')


if __name__ == '__main__':
    main()
