#!/usr/bin/env python3
"""Make two source-pinned, explicitly non-release 0.4 authoring review slices.

This operation reads an immutable human-v2 authoring export, confirms the
Windows Registry Test's one-State OVAL dependency in the evidence sidecar,
and writes NEW sample paths only. It does not upgrade proofs or infer missing
publisher policy/applicability data. Refs #264.
"""

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

import yaml

from v04_direct_yaml import authoring_yaml
from v04_field_requirement import validate_test
from v04_human_authoring_compact import compact_source_state, compact_test_requirement, restore
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors


ROOT = Path(__file__).resolve().parents[1]
CASES = (
    ('ms_windows_11', 'SV-253475'),
    ('rhel_9', 'SV-257851'),
)


def read_yaml(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('missing/unsafe pinned source: ' + str(path))
    raw = path.read_bytes()
    return yaml.safe_load(raw), sha256(raw).hexdigest()


def source_binding(source, scope, sv):
    trace = json.loads((source / 'records' / 'streams' / (scope + '.source-trace.json')).read_text())
    bindings = [row for row in trace['rules'] if '_rule_' + sv in row['source_rule']]
    if len(bindings) != 1:
        raise ValueError('source Rule provenance ambiguous: ' + scope + '/' + sv)
    return bindings[0], trace


def sample(source, destination, scope, sv, validators):
    scope_root = source / 'authoring' / scope
    inputs = {
        'benchmark.yaml': scope_root / 'benchmark.yaml',
        'applicability.yaml': scope_root / 'applicability.yaml',
        f'rules/{sv}.rule.yaml': scope_root / 'rules' / f'{sv}.rule.yaml',
        f'assessments/automated/{sv}.automated.yaml':
            scope_root / 'assessments' / 'automated' / f'{sv}.automated.yaml',
    }
    loaded, input_hashes = {}, {}
    for relative, path in inputs.items():
        loaded[relative], input_hashes[relative] = read_yaml(path)
    benchmark, rule, assessment, applicability = (
        loaded['benchmark.yaml']['benchmark'],
        loaded[f'rules/{sv}.rule.yaml']['rule'],
        loaded[f'assessments/automated/{sv}.automated.yaml']['assessment'],
        loaded['applicability.yaml']['applicability'],
    )
    binding, source_trace = source_binding(source, scope, sv)
    if (binding['assessment'] != assessment['id']
            or binding['native_rule'] != rule['id']
            or rule['assessment_choices']['automated']['assessment'] != assessment['id']):
        raise ValueError('source provenance/Rule/Assessment link mismatch: ' + sv)
    if (len(assessment['tests']) != 1 or benchmark.get('id') != 'direct-slice'
            or benchmark.get('applicability_catalog') != applicability['id']):
        raise ValueError('changed source fixture structure: ' + sv)
    transforms = []
    if scope == 'ms_windows_11':
        states = [node for node, value in binding['dependencies'].items() if value['kind'] == 'state']
        if states != ['oval:mil.disa.stig.win:ste:20000001']:
            raise ValueError('the Windows scalar AND is not uniquely one source State')
        test = next(iter(assessment['tests'].values()))
        requirement = deepcopy(test['require'])
        if set(requirement) != {'items_found', 'items_satisfying', 'and'}:
            raise ValueError('Windows State shape differs from the pinned projection')
        within_state, state_edit = compact_source_state({'and': requirement['and']})
        if not state_edit:
            raise ValueError('Windows original State not compactable')
        root = {key: value for key, value in requirement.items() if key != 'and'}
        root.update(within_state)
        compacted, test_edit = compact_test_requirement(root)
        if not test_edit or restore(compacted, test_edit) != root or restore(within_state, state_edit) != {'and': requirement['and']}:
            raise ValueError('Windows candidate not source-exact invertible')
        test['require'] = compacted
        transforms = [{'source_state': states[0], **state_edit}, {'source_test':
                       next(node for node, value in binding['dependencies'].items() if value['kind'] == 'test'),
                       **test_edit}]

    # These are structurally complete *sample slices*, never full STIGs.
    benchmark['id'] = scope + '-' + sv.lower() + '-authoring-review'
    benchmark['title'][0]['text'] = '[SINGLE-RULE AUTHORING REVIEW — NOT COMPLETE STIG] ' + benchmark['title'][0]['text'].removeprefix('[AUTOMATED PROTOTYPE SUBSET] ')
    benchmark['metadata'] = {'sample_only': True, 'derived_from_review': scope,
                             'selected_native_rules': 1,
                             'native_rules_in_source_export': len(benchmark['rules']),
                             'applicability_not_converted': True}
    benchmark['rules'] = [rule['id']]
    benchmark['profiles'] = []  # Complete original Profiles cannot be asserted for an excerpt.

    result = {}
    for relative, doc in loaded.items():
        kind = next(iter(doc))
        result[relative] = {kind: doc[kind]}
    for test in assessment['tests'].values():
        validate_test(test)
    for relative, document in result.items():
        kind = next(iter(document))
        errors = list(document_errors(validators[kind + '.schema.json'], document))
        if errors:
            raise ValueError(scope + '/' + relative + ': ' + str(errors[0]))
    compiler_documents = {
        'authoring/' + scope + '/' + Path(relative).with_suffix('.json').as_posix(): doc
        for relative, doc in result.items()}
    raw, compilation = build_bundle(compiler_documents)
    if not raw.startswith(b'PK'):
        raise ValueError('invalid compiled sample container')

    output_files = {}
    for relative, document in result.items():
        path = destination / scope / relative
        if path.exists():
            raise ValueError('sample exists: ' + str(path))
        path.parent.mkdir(parents=True, exist_ok=True)
        content = authoring_yaml(document).encode()
        path.write_bytes(content)
        if yaml.safe_load(content) != document:
            raise ValueError('sample YAML round trip failed')
        output_files[relative] = sha256(content).hexdigest()
    return {'scope': scope, 'sv_id': sv, 'source_rule': binding['source_rule'],
            'source_oval_definition': binding['definition'],
            'source_zip_sha256': source_trace['source_zip_sha256'],
            'source_xml_sha256': source_trace['source_xml_sha256'],
            'source_member': source_trace['source_member'],
            'source_dependencies_sha256': binding['dependencies'],
            'original_yaml_sha256': input_hashes,
            'candidate_yaml_sha256': output_files,
            'source_compaction_edits': transforms,
            'schema_documents_valid': 4, 'package_compiles': True,
            'source_static_proof_claim': False, 'scanner_verified': False,
            'publisher_applicability_verified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True,
                        help='human-v2 extracted root containing authoring/ and records/')
    parser.add_argument('--output', type=Path, required=True,
                        help='must not exist; stage into new review folder')
    args = parser.parse_args()
    if args.output.exists() or not (args.source_root / 'records/streams').is_dir():
        raise ValueError('output must be new, source must contain pinned evidence')
    validators = build_validators(ROOT / 'schema/v0.4.0')
    receipts = [sample(args.source_root, args.output, scope, sv, validators)
                for scope, sv in CASES]
    (args.output / 'REVIEW-RECEIPT.json').write_text(json.dumps({
        'status': 'SCHEMA_AND_COMPILATION_ONLY',
        'format': 'scap-ng-v04-two-sample-review/1', 'source': 'human-v2 immutable archive',
        'samples': receipts}, indent=2) + '\n')
    print(json.dumps({'scopes': [x['scope'] for x in receipts],
                      'valid_documents': 8, 'compiled_sample_packages': 2,
                      'source_proof_promoted': 0, 'scanner_verified': False}))


if __name__ == '__main__':
    main()
