#!/usr/bin/env python3
"""Eleven fixed original-source cases; separate proof records, never corpus edits (#251)."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from audit_v04_eight_assessment_pilot import verify_program
from inventory_v04_six_source_requirements import closure_validity
from oval_result_truth_tables import evaluate_collected_object_test
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from v04_native_bundle_compiler import compile_assessment_program
from v04_source_package_semantics import digest, need
from validate_native_json_schemas import build_validators, document_errors

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'tests/fixtures/v04-independent-validation'


def result_contract_findings():
    """Expose an existing reference-model discrepancy, without deciding/fixing it."""
    path = ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/oval-results-schema.xsd'
    root = ET.fromstring(path.read_bytes())
    paragraphs = [' '.join(''.join(n.itertext()).split()) for n in root.iter()
                  if n.tag.endswith('}documentation')]
    paragraph, = [p for p in paragraphs if '3a) If the check attribute evaluation' in p]
    quote = '3a) If the check attribute evaluation results in "false", then the OVAL Test result must be "false";'
    need(quote in paragraph, 'pinned incomplete-collection rule changed')
    observed = evaluate_collected_object_test('incomplete', existence='all_exist', check='all',
                                              exists=1, item_results=['false'])
    return [{'classification': 'REFERENCE_MODEL_REVIEW_REQUIRED', 'rule': 'SV-278021',
             'source_test': 'oval:mil.disa.stig.win:tst:25327800', 'source_contract': str(path.relative_to(ROOT)),
             'source_contract_sha256': sha256(path.read_bytes()).hexdigest(), 'anchor': 'TestType, incomplete exception 3a',
             'quote': quote, 'input': {'flag': 'incomplete', 'check_existence': 'all_exist', 'check': 'all',
                                      'exists': 1, 'item_results': ['false']},
             'literal_exception_3a_result': 'false', 'existing_reference_helper_result': observed,
             'decision': 'Resolve ordered existence/exception interpretation before using this helper as independent all_exist proof; no scanner or schema change made'}]


def namespace(identifier):
    if (identifier or '').startswith('oval:mil.disa.'):
        return 'DISA'
    if (identifier or '').startswith('oval:navy.navwar.niwcatlantic.'):
        return 'NIWC'
    return 'UNATTRIBUTED'


def load_case(row, fixtures=FIXTURES):
    raw = (fixtures / row['fixture']).read_bytes()
    xml = (fixtures / row['xml']).read_bytes()
    need(sha256(raw).hexdigest() == row['fixture_sha256'], 'fixture hash changed')
    need(sha256(xml).hexdigest() == row['xml_sha256'], 'source slice hash changed')
    case = json.loads(raw)
    source = ExpandedSource(ET.fromstring(xml))
    closure = source.closure(case['source_definition'])
    need({n['id']: n['sha256'] for n in closure['nodes']} == case['source_node_hashes'],
         'original dependency identity/hash changed')
    return case, source, closure


def run(*, originals=None):
    manifest = json.loads((FIXTURES / 'manifest.json').read_text())
    validators = build_validators(ROOT / 'schema/v0.4.0')
    component_checks, exact_sources, cases = {}, {}, []
    validator = None
    if originals is not None:
        from oval_source_validation import SourceValidator
        validator = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
    for row in manifest['cases']:
        case, source, closure = load_case(row)
        validity = case['original_component_validity']
        if originals is not None:
            from lxml import etree as E
            pin = case['source_zip']
            key = (pin['sha256'], case['component'])
            if key not in component_checks:
                raw = (originals / pin['file']).read_bytes()
                need(sha256(raw).hexdigest() == pin['sha256'], 'original archive hash changed')
                with zipfile.ZipFile(originals / pin['file']) as archive:
                    xml = archive.read(case['source_xml_member'])
                need(sha256(xml).hexdigest() == case['source_member_sha256'], 'original member hash changed')
                root = E.fromstring(xml, E.XMLParser(resolve_entities=False, no_network=True))
                matches = [c[0] for c in root if c.tag.endswith('}component') and c.get('id') == case['component']]
                need(len(matches) == 1, 'ambiguous original component')
                # Rejoin every sliced node to the actual pinned original.
                exact_sources[key] = ExpandedSource(ET.fromstring(E.tostring(matches[0])))
                component_checks[key] = validator.validate(matches[0])
            need(exact_sources[key].closure(case['source_definition']) == closure, 'slice/original closure differs')
            dependencies = [{'id': n['id'], 'component': case['component']} for n in closure['nodes']]
            validity = closure_validity(dependencies, {case['component']: component_checks[key]})
            need(validity == case['original_component_validity'], 'original validation observations changed')
        issues = [{**issue, 'namespace': namespace(issue.get('source_id'))} for issue in validity['issues']]
        result = {'rule': row['rule'], 'source_rule': case['source_rule'],
                  'source_definition': case['source_definition'], 'definition_namespace': namespace(case['source_definition']),
                  'source_zip_sha256': case['source_zip']['sha256'], 'source_rule_sha256': case['source_rule_sha256'],
                  'source_dependency_closure': closure, 'source_validity': validity['status'], 'source_issues': issues,
                  'frozen_status': case['frozen_status'], 'already_in_frozen_proof_floor': case['already_in_frozen_proof_floor']}
        if validity['status'] != 'VALID':
            result['outcome'] = 'EXCLUDED_SOURCE_INVALID'
        elif any(i['kind'] == 'deprecated' for i in issues):
            result['outcome'] = 'EXCLUDED_SOURCE_DEPRECATED'
        elif case['native'] is None:
            result['outcome'] = 'NO_NATIVE_CANDIDATE'
        else:
            document = case['native']
            need(digest(document['assessment']) == case['authoring_sha256'], 'frozen authoring hash changed')
            errors = list(document_errors(validators['assessment.schema.json'], document))
            need(not errors, 'native schema: ' + str(errors[:1]))
            program = compile_assessment_program(document['assessment'])
            need(digest(program) == case['program_sha256'], 'frozen compiled program changed')
            verify_program(document['assessment'], program)
            proof = expanded_compare(source, case['source_definition'], document['assessment'])
            result.update(outcome=proof['outcome'], proof=proof, authoring_sha256=case['authoring_sha256'],
                          program_sha256=case['program_sha256'], native_schema='PASS',
                          independent_program_operand_check='PASS')
        cases.append(result)
    defects = {n: [dict(rule=c['rule'], **i) for c in cases for i in c['source_issues'] if i['namespace'] == n]
               for n in ('DISA', 'NIWC', 'UNATTRIBUTED')}
    return {'format': 'scap-ng/bounded-source-validation/1', 'cases': cases,
            'outcomes': dict(Counter(c['outcome'] for c in cases)), 'source_findings_by_namespace': defects,
            'original_validation': 'REPLAYED_PINNED_ARCHIVES' if originals is not None else 'RETAINED_FULL_COMPONENT_OBSERVATIONS',
            'proof_floor_records_preserved': manifest['baseline_proof_records'],
            'new_records_outside_frozen_floor': sum(c['outcome'] == 'PROVED' and not c['already_in_frozen_proof_floor'] for c in cases),
            'corpus_statuses_modified': False, 'scanner_evaluated': False,
            'reference_model_findings': result_contract_findings(),
            'limitations': manifest['limitations'] + ['Structural typed-term proof, not scanner-runtime equivalence; no count function execution/flag evaluator added']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--originals', type=Path, help='optional directory containing the exact pinned original ZIPs')
    parser.add_argument('--output', type=Path, required=True, help='new report file; source and corpus stay read-only')
    args = parser.parse_args()
    report = run(originals=args.originals)
    with args.output.open('x') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(json.dumps({'cases': len(report['cases']), 'outcomes': report['outcomes'],
                      'new_records_outside_frozen_floor': report['new_records_outside_frozen_floor']}))
