#!/usr/bin/env python3
"""Build a review-only 40-Rule proposed authoring gallery from pinned human-v2.

The source-preserved 40-Rule gallery is the preimage. Rewrite only safe
field-cardinality presentation: hoist a complete values_found/values_matching
pair to Test.require.field_requirement, keep distinct complete field pairs as
overrides, and collapse a scalar AND only when exactly one source State is
pinned for a single-Test Rule. No source or scanner proof is promoted.
Refs #264 #265 #266.
"""

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re

import yaml

from v04_direct_yaml import authoring_yaml
from v04_field_requirement import validate_test
from v04_human_authoring_compact import compact_source_state, restore
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors


ROOT = Path(__file__).resolve().parents[1]
SCOPES = ('ms_windows_11', 'rhel_9')
OPS = ('and', 'or', 'one', 'xor')
PAIR = ('values_found', 'values_matching')


def checksum(blob):
    return sha256(blob).hexdigest()


def load_yaml(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('not a pinned regular file: ' + str(path))
    raw = path.read_bytes()
    return yaml.safe_load(raw), raw


def scalar_fields(requirement):
    """Return (key path, mutable predicate, original pair) for scalar compares."""
    found = []
    exceptions = []

    def visit(node, path):
        if not isinstance(node, dict):
            return
        for name, predicate in node.get('fields', {}).items():
            field_path = (*path, 'fields', name)
            if 'record' in predicate:
                # The current 0.4.0 schema requires independent explicit
                # cardinalities on record-member fields. Test-wide scalar
                # inheritance is not legal across this schema boundary.
                exceptions.append({'path': list(field_path), 'reason': 'record_wrapper'})
                continue
            if predicate.get('values_found') == 'none':
                exceptions.append({'path': list(field_path), 'reason': 'comparison_free_absence'})
                continue
            if all(key in predicate for key in PAIR):
                found.append((field_path, predicate, tuple(predicate[key] for key in PAIR)))
            else:
                exceptions.append({'path': list(field_path), 'reason': 'no_explicit_pair'})
        for op in OPS:
            for index, branch in enumerate(node.get(op, [])):
                visit(branch, (*path, op, index))

    visit(requirement, ('require',))
    return found, exceptions


def without_policies(node):
    """Shape of a Test with all inherited/explicit paired controls erased.

    Comparator-free absence remains a real predicate and is never removed.
    """
    if isinstance(node, list):
        return [without_policies(v) for v in node]
    if isinstance(node, dict):
        is_absence = node.get('values_found') == 'none'
        return {k: without_policies(v) for k, v in node.items()
                if k != 'field_requirement' and
                (is_absence or k not in PAIR)}
    return node


def effective_counts(node):
    """Expand nearest-scoped field-count inheritance into path/value pairs."""
    result = {}

    def visit(branch, path, policy=None):
        if not isinstance(branch, dict):
            return
        policy = branch.get('field_requirement', policy)
        for name, predicate in branch.get('fields', {}).items():
            loc = (*path, 'fields', name)
            if 'record' in predicate:
                visit(predicate['record'], (*loc, 'record'), policy)
                continue
            if predicate.get('values_found') == 'none':
                result[loc] = ('none', None)
                continue
            if all(k in predicate for k in PAIR):
                result[loc] = tuple(predicate[k] for k in PAIR)
            else:
                result[loc] = tuple(policy[k] for k in PAIR) if policy else None
        for op in OPS:
            for i, sub in enumerate(branch.get(op, [])):
                visit(sub, (*path, op, i), policy)

    visit(node, ('require',))
    return result


def proposal(requirement):
    original = deepcopy(requirement)
    if not isinstance(requirement, dict) or 'items_satisfying' not in requirement:
        return original, {'status': 'item-presence-only', 'changes': 0}
    if 'field_requirement' in requirement:
        raise ValueError('source 40-Rule gallery already has Test-wide policy')
    candidate = deepcopy(requirement)
    leaves, exceptions = scalar_fields(candidate)
    if not leaves:
        return original, {'status': 'no-comparison-field', 'changes': 0,
                          'exceptions': exceptions}
    if any(x['reason'] not in {'comparison_free_absence', 'record_wrapper'}
           for x in exceptions):
        # Do not invent a policy for an unknown nested predicate.
        return original, {'status': 'conservative-review-hold', 'changes': 0,
                          'exceptions': exceptions}
    pairs = [entry[2] for entry in leaves]
    counts = Counter(pairs)
    # Stable tie-break: use first field in the existing authoring order.
    winner = max(dict.fromkeys(pairs), key=lambda x: counts[x])
    # Present the shared policy before its fields/groups in readable YAML.
    candidate = {
        **{k: candidate[k] for k in ('items_found', 'items_satisfying') if k in candidate},
        'field_requirement': dict(zip(PAIR, winner)),
        **{k: v for k, v in candidate.items() if k not in ('items_found', 'items_satisfying')},
    }
    leaves, _ = scalar_fields(candidate)
    field_count = 0
    retained_overrides = 0
    for _, predicate, pair in leaves:
        if pair == winner:
            for key in PAIR:
                del predicate[key]
            field_count += 1
        else:
            retained_overrides += 1
    if without_policies(original) != without_policies(candidate):
        raise ValueError('hoisting modified non-cardinality requirement logic')
    if effective_counts(original) != effective_counts(candidate):
        raise ValueError('hoisting modified field requirements')
    return candidate, {'status': 'test-wide-proposed', 'changes': field_count,
                       'default': dict(zip(PAIR, winner)),
                       'overrides': retained_overrides,
                       'exceptions': exceptions}


def single_state_collapse(assessment, binding):
    """Collapse only a uniquely traced one-State, one-Test scalar conjunction."""
    tests = assessment.get('tests', {})
    states = [x for x, val in binding['dependencies'].items() if val['kind'] == 'state']
    if len(tests) != 1 or len(states) != 1:
        return None
    test = next(iter(tests.values()))
    req = test['require']
    if set(req) != {'items_found', 'items_satisfying', 'and'}:
        return None
    new, edit = compact_source_state({'and': req['and']})
    if not edit or restore(new, edit) != {'and': req['and']}:
        return None
    test['require'] = {**{k: v for k, v in req.items() if k != 'and'}, **new}
    return {'source_state': states[0], **edit}


def transform_assessment(doc, trace_binding):
    assessment = deepcopy(doc)
    tests = assessment['assessment']['tests']
    edits = []
    collapse = single_state_collapse(assessment['assessment'], trace_binding)
    if collapse:
        edits.append({'kind': 'pinned-source-state-scalar-and', 'edit': collapse})
    for name, test in tests.items():
        old = deepcopy(doc['assessment']['tests'][name]['require'])
        candidate, detail = proposal(test['require'])
        test['require'] = candidate
        validate_test(test)
        if old != candidate:
            edits.append({'kind': 'field-policy-presentation', 'test': name,
                          'original_require': old, 'candidate_require': deepcopy(candidate),
                          'detail': detail})
        elif detail['status'] == 'conservative-review-hold':
            edits.append({'kind': 'needs-further-review', 'test': name, 'detail': detail})
    return assessment, edits


def render(source, output, validators, scope, original_receipt, trace_root):
    baseline = source / scope
    source_rows = {row['sv']: row for row in original_receipt['samples'][scope]}
    selected = list(source_rows)
    trace = json.loads((trace_root / (scope + '.source-trace.json')).read_text())
    bindings = {}
    for binding in trace['rules']:
        found = re.search(r'SV-\d+', binding['source_rule'])
        if found and found.group() in source_rows:
            if found.group() in bindings:
                raise ValueError('ambiguous source trace: ' + found.group())
            bindings[found.group()] = binding
    if set(bindings) != set(source_rows):
        raise ValueError('pinned source trace does not cover chosen Rules')
    benchmark_doc, _ = load_yaml(baseline / 'benchmark.yaml')
    benchmark = benchmark_doc['benchmark']
    benchmark['id'] = scope + '-proposed-authoring-review'
    benchmark['title'][0]['text'] = benchmark['title'][0]['text'].replace(
        '[20-RULE AUTHORING REVIEW', '[20-RULE PROPOSED AUTHORING REVIEW')
    benchmark['metadata']['proposed_field_policy_review'] = True
    applicability_doc, raw_app = load_yaml(baseline / 'applicability.yaml')
    dest = output / scope
    dest.mkdir(parents=True)
    (dest / 'benchmark.yaml').write_text(authoring_yaml(benchmark_doc))
    (dest / 'applicability.yaml').write_bytes(raw_app)
    all_docs = {'authoring/' + scope + '/benchmark.json': benchmark_doc,
                'authoring/' + scope + '/applicability.json': applicability_doc}
    receipts = []
    for sv in selected:
        old_a, old_a_raw = load_yaml(baseline / 'assessments/automated' / (sv + '.automated.yaml'))
        rule, old_r_raw = load_yaml(baseline / 'rules' / (sv + '.rule.yaml'))
        if checksum(old_a_raw) != source_rows[sv]['assessment_sha256']:
            raise ValueError('baseline Assessment hash mismatch ' + sv)
        if checksum(old_r_raw) != source_rows[sv]['rule_sha256']:
            raise ValueError('baseline Rule hash mismatch ' + sv)
        candidate, edits = transform_assessment(old_a, bindings[sv])
        file_a = dest / 'assessments/automated' / (sv + '.automated.yaml')
        file_r = dest / 'rules' / (sv + '.rule.yaml')
        file_a.parent.mkdir(parents=True, exist_ok=True)
        file_r.parent.mkdir(parents=True, exist_ok=True)
        new_a_raw = authoring_yaml(candidate).encode()
        file_a.write_bytes(new_a_raw)
        file_r.write_bytes(old_r_raw)
        if yaml.safe_load(new_a_raw) != candidate:
            raise ValueError('candidate YAML roundtrip failed')
        all_docs['authoring/' + scope + '/assessments/automated/' + sv + '.automated.json'] = candidate
        all_docs['authoring/' + scope + '/rules/' + sv + '.rule.json'] = rule
        receipts.append({'sv': sv, 'original_sha256': checksum(old_a_raw),
                         'candidate_sha256': checksum(new_a_raw),
                         'rule_sha256': checksum(old_r_raw),
                         'source_rule': bindings[sv]['source_rule'],
                         'source_definition': bindings[sv]['definition'],
                         'source_zip_sha256': trace['source_zip_sha256'],
                         'source_member': trace['source_member'],
                         'original_proof_status': source_rows[sv]['status'],
                         'edits': edits})
    for rel, doc in all_docs.items():
        kind = next(iter(doc))
        errors = list(document_errors(validators[kind + '.schema.json'], doc))
        if errors:
            raise ValueError(rel + ': ' + str(errors[0]))
    blob, _ = build_bundle(all_docs)
    if not blob.startswith(b'PK'):
        raise ValueError('native compiler did not produce a ZIP')
    return receipts


def readme(samples):
    lines = [
        '# SCAP-NG 0.4.0 — 40 proposed human-authoring examples',
        '',
        '**Proposed authoring presentation; October 30, 2026; NOT a release.**',
        '',
        '**Start here to review the proposed form**, not the older as-generated',
        '[40-Rule audit](../v04-expanded-authoring-review/README.md).',
        'These 20 Windows 11 and 20 RHEL 9 pairs use a Test-wide',
        '`require.field_requirement` wherever comparison-bearing scalar fields',
        'are safely traceable. Field pairs remain local only as genuine overrides.',
        'A source-pinned one-State Windows Registry AND is a single `fields` mapping.',
        '',
        'Some Item-presence/record-absence cases do not have a meaningful',
        'field-comparison default. Boolean group boundaries and record aggregation',
        'are deliberately preserved where a source-justified rewrite is unavailable.',
        '**Record member fields are a separate current-schema boundary**:',
        'their explicit per-member value policies remain until record-scope',
        'inheritance is designed and accepted. They have not been silently folded',
        'into the Test-wide scalar policy.',
        'No datatype is inferred or discarded in this review. The current',
        'schema still requires Assessment-root `purpose` and long logical IDs;',
        'those separately approved authoring cleanups have **not** been',
        'silently applied to these examples.',
        '',
        '**Verification boundary:** 84 YAML documents validated against the current',
        '0.4.0 schema; two 20-Rule excerpt packages compiled separately. This does',
        '**not** reprove OVAL semantics, scanner evaluation, source-to-source',
        'equivalence, publisher applicability, or six-state behavior.',
        '**NOT SCANNER-VERIFIED — RESULT UNAVAILABLE.**',
        'The sample Benchmarks are incomplete review wrappers with placeholder',
        'applicability and deliberately omitted full Profiles/manual Rules.',
        '',
        'All Rule YAML is byte-identical to the source-pinned as-generated gallery;',
        'Assessment edits have SHA256 provenance and an exact preimage in',
        '[the edit receipt](REVIEW-RECEIPT.json). No immutable 65-stream artifact',
        'or original proof baseline was changed. Track schema/converter standardization',
        'in [#264](https://github.com/vanderpol/scap-ng/issues/264) and content',
        'completion in [#265](https://github.com/vanderpol/scap-ng/issues/265).',
        f'**{sum(a["original_sha256"] != a["candidate_sha256"] for rows in samples.values() for a in rows)} Assessments changed.** The unchanged Assessments check only',
        'whether Items exist or do not exist; they contain no fields to match,',
        'so adding a field policy to them would be incorrect.',
        '',
    ]
    for scope, rows in samples.items():
        label = 'Windows 11' if scope == 'ms_windows_11' else 'RHEL 9'
        lines.extend([f'## {label} — 20 proposed-format pairs', '',
                      f'[Review Benchmark]({scope}/benchmark.yaml) · '
                      f'[Applicability placeholder]({scope}/applicability.yaml)', '',
                      '| Rule | Proposed Assessment | Policy edits | Original generated |',
                      '| --- | --- | --- | --- |'])
        for row in rows:
            sv = row['sv']
            edits = sum(e['kind'] == 'field-policy-presentation' for e in row['edits'])
            holds = sum(e['kind'] == 'needs-further-review' for e in row['edits'])
            note = (str(edits) + (' Test' if edits == 1 else ' Tests') + ' refactored' if edits else
                    'Item presence only; unchanged') + (f'; {holds} held' if holds else '')
            lines.append(f'| [{sv}]({scope}/rules/{sv}.rule.yaml) | '
                         f'[YAML]({scope}/assessments/automated/{sv}.automated.yaml) | '
                         f'{note} | [Before](../v04-expanded-authoring-review/{scope}/assessments/automated/{sv}.automated.yaml) |')
        lines.append('')
    lines.extend(['## Human review checklist', '',
                  '- Can you understand a simple scalar comparison without an AND tree?',
                  '- Are shared field counts at the Test scope, with local overrides only when needed?',
                  '- Does every meaningful AND/OR/ONE/XOR distinction remain apparent?',
                  '- Are record count policies distinct from scalar field count policies?',
                  '- Which datatypes or required-empty metadata add unnecessary author burden?',
                  '',
                  'Reproduce from the pinned as-generated gallery:', '',
                  '```bash',
                  'python tools/build_v04_proposed_authoring_review.py \\',
                  '  --baseline docs/examples/v04-expanded-authoring-review \\',
                  '  --source-trace-root <human-v2-export-root>/records/streams \\',
                  '  --output <new-nonexistent-directory>',
                  '```', ''])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--source-trace-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('refusing to overwrite any existing review material')
    if not args.source_trace_root.is_dir():
        raise ValueError('missing source trace directory')
    validators = build_validators(ROOT / 'schema/v0.4.0')
    provenance = json.loads((args.baseline / 'REVIEW-RECEIPT.json').read_text())
    args.output.mkdir(parents=True)
    samples = {scope: render(args.baseline, args.output, validators, scope, provenance,
                             args.source_trace_root) for scope in SCOPES}
    (args.output / 'README.md').write_text(readme(samples))
    (args.output / 'REVIEW-RECEIPT.json').write_text(json.dumps({
        'status': 'PROPOSED_AUTHORING_SCHEMA_AND_COMPILATION_ONLY',
        'source': 'immutable-human-v2-linked-as-generated-gallery',
        'schema_valid_documents': 84, 'compiled_excerpt_packages': 2,
        'independent_source_proofs_promoted': 0, 'scanner_verified': False,
        'samples': samples}, indent=2) + '\n')
    print(json.dumps({'scopes': {k:len(v) for k,v in samples.items()},
                      'field_policy_edits': sum(sum(e['kind'] == 'field-policy-presentation'
                                      for e in row['edits']) for rows in samples.values() for row in rows),
                      'schema_valid_documents': 84, 'compiled_excerpt_packages': 2}))


if __name__ == '__main__':
    main()
