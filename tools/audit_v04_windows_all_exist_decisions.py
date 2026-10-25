#!/usr/bin/env python3
"""Read-only source-pinned owner decision evidence; no new normalization (#251).

Uses existing OVAL result-table reference helpers, not a scanner or converter.
No package, proof ledger or source fixture is rewritten.
"""
import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from oval_result_truth_tables import evaluate_collected_object_test, RESULTS
from v04_source_package_semantics import Source, local, xml_term

ROOT = Path(__file__).resolve().parents[1]
CASES = ((1, '828744b1b12806e6b13f46eb4a946b29474c3e3d6cffa61d21e937756f370f05'),
         (15, '0d5729d8ebf5c92b6320ae6741c1bb799a3d06f02b8571bf80a719a72e00c78e'))


def fixture(number, expected):
    p = ROOT / f'tests/fixtures/v04-proof-expansion/windows-{number:02}.json'
    if sha256(p.read_bytes()).hexdigest() != expected:
        raise ValueError('reviewed original-source fixture drift')
    return json.loads(p.read_text())


def vectors():
    """Exercise the EXISTING reference helper, without ratifying all its rows.

    Includes algebraic inputs not admissible as complete successful evidence.
    Incomplete all_exist has a separately recorded source-text discrepancy;
    these diagnostic rows are not a new normative evaluator or admission.
    """
    rows = []
    statuses = sorted(RESULTS)
    for flag in ('complete', 'incomplete', 'error', 'not collected', 'does not exist', 'not applicable'):
        for n in range(3):
            for states in itertools.product(statuses, repeat=n):
                for dne, err, nc in itertools.product(range(2), repeat=3):
                    args = dict(check='all', has_state=True, item_results=list(states),
                                exists=n, does_not_exist=dne, error=err, not_collected=nc)
                    old = evaluate_collected_object_test(flag, existence='all_exist', **args)
                    new = evaluate_collected_object_test(flag, existence='at_least_one_exists', **args)
                    rows.append({'flag': flag, **args, 'reference_helper_all_exist': old,
                        'reference_helper_at_least_one_exists': new, 'equal': old == new,
                        'complete_actual_items_only': flag == 'complete' and not (dne or err or nc)})
    return rows


def analyze(inputs=None):
    cases = []
    for number, pin in CASES:
        f = fixture(number, pin)
        source = Source(ET.fromstring(f['source_xml']))
        closure = source.closure(f['source_definition'])
        if closure != f['provenance']['source_dependency_closure']:
            raise ValueError('original-source closure drift')
        if inputs is not None:
            from audit_v04_eight_assessment_pilot import original, BASE
            pins = json.loads((BASE / 'source-ledger.json').read_text())['sources']
            _, definition, trace = original(inputs, f['provenance']['platform'], f['provenance']['rule'], pins)
            for key in ('xml_sha256', 'xccdf_rule_sha256', 'closure_sha256'):
                if trace[key] != f['provenance'][key]:
                    raise ValueError('original SCAP ZIP/fixture mismatch: ' + key)
            if definition != f['source_definition']:
                raise ValueError('original Definition mismatch')
        tests = []
        for entry in closure['nodes']:
            if entry['kind'] != 'tests':
                continue
            t = source.nodes[entry['id']]
            if t.get('check_existence') != 'all_exist' or t.get('check') != 'all':
                raise ValueError('read-only all_exist case changed')
            refs = [c.get('object_ref') for c in t if local(c) == 'object']
            states = [c.get('state_ref') for c in t if local(c) == 'state']
            if len(refs) != 1 or len(states) != 1:
                raise ValueError('source Test population/State changed')
            obj, state = source.nodes[refs[0]], source.nodes[states[0]]
            is_wmi = local(obj) == 'wmi57_object'
            tests.append({'id': t.get('id'), 'attributes': dict(t.attrib),
                'original_test': xml_term(t), 'original_object': xml_term(obj),
                'original_state': xml_term(state), 'object_id': refs[0], 'state_id': states[0],
                'population': 'collector-defined WQL result rows' if is_wmi else 'one literal registry value identity',
                'conditional_complete_no_dne_table_equivalence': True,
                'normalization_approved': False, 'proof_promoted': False})
        cases.append({'rule': f['provenance']['rule'], 'fixture': f'windows-{number:02}.json',
            'fixture_sha256': pin, 'source_provenance': f['provenance'], 'tests': tests,
            'existing_proof_outcome': f['expected_outcome'],
            'original_zip_verified_this_run': inputs is not None})
    rows = vectors()
    eligible = [r for r in rows if r['complete_actual_items_only']]
    if not all(r['equal'] for r in eligible):
        raise ValueError('conditional complete/no-DNE table claim disproved')
    return {'status': 'OWNER_DECISION_REQUIRED_READ_ONLY', 'cases': cases,
        'reference': 'pinned OVAL 5.12.3 TestType/ExistenceEnumeration; existing oval_result_truth_tables.py',
        'reference_schema_sha256': sha256((ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/oval-results-schema.xsd').read_bytes()).hexdigest(),
        'vectors': rows, 'vector_count_per_test': len(rows), 'tests': sum(len(c['tests']) for c in cases),
        'conditional_complete_actual_item_vectors': len(eligible),
        'differences_per_test': sum(not r['equal'] for r in rows),
        'matrix_scope': 'existing-helper algebraic diagnostics; not every combination is admissible system-characteristics evidence; incomplete all_exist discrepancy below is not ratified',
        'source_text_counterexample': {
            'source': 'oval-results-schema.xsd TestType documentation, incomplete exception 3a',
            'quote': 'If the check attribute evaluation results in "false", then the OVAL Test result must be "false"',
            'input': {'flag': 'incomplete', 'exists': 1, 'does_not_exist': 0,
                      'error': 0, 'not_collected': 0, 'item_results': ['false'],
                      'check': 'all', 'check_existence': 'all_exist'},
            'existing_helper_result': 'unknown', 'source_text_expected_result': 'false',
            'disposition': 'OWNER_REVIEW_REQUIRED; helper, existing approved normalization and production semantics unchanged'},
        'normalizations_implemented': 0, 'coverage_promoted': False, 'scanner_evaluated': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--inputs-dir', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = analyze(a.inputs_dir)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'tests', 'vector_count_per_test',
        'conditional_complete_actual_item_vectors', 'differences_per_test')}))
