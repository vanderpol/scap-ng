#!/usr/bin/env python3
"""Curate 20 Windows 11 and 20 RHEL 9 native v0.4 review examples.

Read-only against the pinned human-v2 source. Copy native Rule/Assessment
YAML byte-for-byte; construct separate, explicitly non-deployable excerpt
Benchmark wrappers. No semantic normalization, proof promotion or 65-stream
regeneration. Refs #264 #265 #266.
"""

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re

import yaml

from v04_direct_yaml import authoring_yaml
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors


ROOT = Path(__file__).resolve().parents[1]
CASES = {'ms_windows_11': 'SV-253475', 'rhel_9': 'SV-257851'}
FEATURES = {'and', 'or', 'xor', 'one', 'not', 'record', 'set', 'filters',
            'value_match', 'dependencies', 'shared_objects', 'inputs', 'variables'}


def walk(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested)


def digest(raw):
    return sha256(raw).hexdigest()


def read(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('missing or unsafe native source ' + str(path))
    raw = path.read_bytes()
    return yaml.safe_load(raw), raw


def inventory(source, scope):
    scope_path = source / 'authoring' / scope
    evidence = json.loads((source / 'records/streams' / (scope + '.json')).read_text())
    trace = json.loads((source / 'records/streams' / (scope + '.source-trace.json')).read_text())
    source_rows = {}
    for row in evidence['original_ledger']['rules']:
        match = re.search(r'SV-\d+', row.get('source_rule', ''))
        if match and row.get('assessment_path'):
            if match.group() in source_rows:
                raise ValueError('ambiguous SV-ID in source ledger: ' + match.group())
            source_rows[match.group()] = row
    trace_rows = {r['source_rule']: r for r in trace['rules']}
    entries = []
    for assessment_path in sorted((scope_path / 'assessments/automated').glob('SV-*.automated.yaml')):
        sv = assessment_path.name.split('.')[0]
        rule_path = scope_path / 'rules' / (sv + '.rule.yaml')
        if sv not in source_rows:
            raise ValueError('missing source Rule ledger ' + sv)
        doc_a, raw_a = read(assessment_path)
        doc_r, raw_r = read(rule_path)
        assessment, rule = doc_a['assessment'], doc_r['rule']
        if rule['assessment_choices']['automated']['assessment'] != assessment['id']:
            raise ValueError('broken Rule/Assessment reference: ' + sv)
        source_row = source_rows[sv]
        if source_row['source_rule'] not in trace_rows:
            raise ValueError('missing pinned source trace for ' + sv)
        tests = assessment.get('tests') or {}
        names = list(walk(assessment))
        capabilities = sorted({t['capability'] for t in tests.values()})
        features = set(names) & FEATURES
        if len(tests) > 1:
            features.add('multiple-tests')
        if len(tests) == 1 and not features:
            features.add('simple-one-test')
        for term in ('items_found', 'items_satisfying', 'values_found', 'values_matching'):
            if term in names:
                features.add('explicit-' + term)
        entries.append({'sv': sv, 'title': rule['title'], 'capabilities': capabilities,
                        'features': sorted(features), 'tests': len(tests),
                        'status': source_row['conversion_status'],
                        'source_rule': source_row['source_rule'],
                        'source_rule_sha256': source_row['source_rule_sha256'],
                        'original_program_sha256': source_row.get('program_sha256'),
                        'source_zip_sha256': trace['source_zip_sha256'],
                        'source_member': trace['source_member'],
                        'assessment': doc_a, 'rule': doc_r,
                        'assessment_raw': raw_a, 'rule_raw': raw_r,
                        'assessment_sha256': digest(raw_a), 'rule_sha256': digest(raw_r),
                        'assessment_path': assessment_path, 'rule_path': rule_path,
                        'lines': len(raw_a.splitlines())})
    return entries


def choose(entries, anchor, limit):
    if limit > len(entries):
        raise ValueError('requested more examples than there are Assessments')
    found = {x['sv']: x for x in entries}
    if anchor not in found:
        raise ValueError('missing selected anchor ' + anchor)
    pool = sorted(entries, key=lambda x: x['sv'])
    chosen = [found[anchor]]
    used = {anchor}
    represented_cap = set(chosen[0]['capabilities'])
    represented_features = set(chosen[0]['features'])
    represented_shapes = {(tuple(chosen[0]['capabilities']), tuple(chosen[0]['features']))}
    sample_cap_counts = Counter(chosen[0]['capabilities'])
    capability_counts = Counter(cap for x in entries for cap in x['capabilities'])

    # Cover uncommon capabilities before taking more examples of a common one.
    while len(chosen) < limit:
        remaining = [x for x in pool if x['sv'] not in used]
        candidates = []
        for row in remaining:
            novel_cap = [cap for cap in row['capabilities'] if cap not in represented_cap]
            novel_features = set(row['features']) - represented_features
            cap_weight = sum(24 + 120 / capability_counts[cap] for cap in novel_cap)
            feature_weight = sum(4 if key != 'simple-one-test' else 8 for key in novel_features)
            shape = (tuple(row['capabilities']), tuple(row['features']))
            shape_bonus = 18 if shape not in represented_shapes else 0
            # Once acquisition coverage is complete, do not fill remaining
            # slots with minor variants of an already represented Test shape.
            repeat_penalty = sum(max(0, sample_cap_counts[c] - 1) * 8
                                 for c in row['capabilities'])
            # Avoid filling the review with unwieldy Assessments when two
            # candidates cover the same concepts. Do not exclude them entirely.
            length_penalty = max(0, row['lines'] - 120) / 40
            status_bonus = 1 if row['status'] == 'CONVERTED_VERIFIED' else 0
            simple_bonus = (5 if row['features'] == ['simple-one-test'] and
                            sum('simple-one-test' in x['features'] for x in chosen) < 3 else 0)
            score = (cap_weight + feature_weight + shape_bonus + status_bonus +
                     simple_bonus - length_penalty - repeat_penalty)
            candidates.append((score, row['lines'], row['sv'], row))
        candidates.sort(key=lambda x: (-x[0], x[1], x[2]))
        pick = candidates[0][3]
        chosen.append(pick)
        used.add(pick['sv'])
        represented_cap.update(pick['capabilities'])
        represented_features.update(pick['features'])
        represented_shapes.add((tuple(pick['capabilities']), tuple(pick['features'])))
        sample_cap_counts.update(pick['capabilities'])
    return chosen


def validate_docs(documents, validators):
    for path, doc in documents.items():
        kind = next(iter(doc))
        errors = list(document_errors(validators[kind + '.schema.json'], doc))
        if errors:
            raise ValueError(path + ': ' + str(errors[0]))


def render_scope(source, output, scope, rows, all_count, validators):
    scope_source = source / 'authoring' / scope
    benchmark_doc, _ = read(scope_source / 'benchmark.yaml')
    applicability_doc, applicability_raw = read(scope_source / 'applicability.yaml')
    benchmark = benchmark_doc['benchmark']
    if benchmark.get('id') != 'direct-slice' or benchmark.get('applicability_catalog') != applicability_doc['applicability']['id']:
        raise ValueError('source Benchmark no longer has expected prototype wrapper')
    benchmark['id'] = scope + '-expanded-authoring-review'
    benchmark['title'][0]['text'] = ('[20-RULE AUTHORING REVIEW — NOT COMPLETE STIG] ' +
        benchmark['title'][0]['text'].removeprefix('[AUTOMATED PROTOTYPE SUBSET] '))
    benchmark['metadata'] = {'review_only': True, 'selected_rules': len(rows),
                             'native_rules_in_v2': all_count,
                             'source_scope': scope, 'applicability_not_converted': True}
    benchmark['rules'] = [x['rule']['rule']['id'] for x in rows]
    benchmark['profiles'] = []  # Cannot present full source Profiles as 20-Rule policy.
    all_docs = {'authoring/' + scope + '/benchmark.json': benchmark_doc,
                'authoring/' + scope + '/applicability.json': applicability_doc}
    scope_dest = output / scope
    scope_dest.mkdir(parents=True)
    (scope_dest / 'benchmark.yaml').write_text(authoring_yaml(benchmark_doc))
    (scope_dest / 'applicability.yaml').write_bytes(applicability_raw)
    receipts = []
    for row in rows:
        sv = row['sv']
        for kind, subdir, doc, raw in (
            ('rule', 'rules', row['rule'], row['rule_raw']),
            ('assessment', 'assessments/automated', row['assessment'], row['assessment_raw'])):
            filename = sv + ('.rule.yaml' if kind == 'rule' else '.automated.yaml')
            path = scope_dest / subdir / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)  # Source-faithful, no compaction or renaming.
            all_docs['authoring/' + scope + '/' + subdir + '/' + filename.replace('.yaml', '.json')] = doc
        receipts.append({key: row[key] for key in (
            'sv', 'title', 'capabilities', 'features', 'tests', 'status', 'source_rule',
            'source_rule_sha256', 'original_program_sha256', 'source_zip_sha256',
            'source_member', 'assessment_sha256', 'rule_sha256', 'lines')})
    validate_docs(all_docs, validators)
    archive, _ = build_bundle(all_docs)
    if not archive.startswith(b'PK'):
        raise ValueError('compiled package did not produce deterministic ZIP header')
    return receipts


def markdown(receipts):
    lines = [
        '# SCAP-NG 0.4.0 — expanded Windows 11 and RHEL 9 authoring review',
        '',
        '**October 30, 2026. Non-release, source-faithful review excerpts.**',
        '',
        'These examples preserve the original native Rule and Assessment YAML bytes from',
        'the immutable 65-stream human-v2 package. **They deliberately retain current',
        'authoring problems** so the owner can review more than one favorable sample.',
        'In particular, the samples have not yet adopted the proposed single-field',
        'Test-wide `field_requirement` convention or the approved removal of',
        'Assessment-root `purpose` ([#264](https://github.com/vanderpol/scap-ng/issues/264),',
        '[#266](https://github.com/vanderpol/scap-ng/issues/266)).',
        '',
        'Each scope includes 20 exact source-derived Rule/Assessment pairs, a synthetic',
        'single-scope review Benchmark, and the original empty applicability placeholder.',
        'The Benchmark wrapper is **not a complete STIG**, its Profiles were deliberately',
        'omitted, and **it is not suitable for scanner deployment**. See',
        '[#265](https://github.com/vanderpol/scap-ng/issues/265) for identity,',
        'applicability, manual-coverage, and source-metadata blockers.',
        '',
        '**Validation:** All 84 YAML documents are schema-valid; both separate',
        '20-Rule sample packages compiled. This is **not** independent OVAL equivalence',
        'or a scanner result. **NOT SCANNER-VERIFIED — RESULT UNAVAILABLE.**',
        'The original 65-stream ZIP, full-library proofs and hashes are unchanged.',
        '',
        'For the [two-rule *proposed compact* examples](../v04-two-sample-review/README.md),',
        'see the earlier focused design preview. These expanded samples show the current',
        'as-generated 0.4 baseline instead of silently normalizing it.',
        '',
        '## Browse the samples',
        '',
    ]
    for scope, rows in receipts.items():
        label = 'Windows 11' if scope == 'ms_windows_11' else 'RHEL 9'
        caps = sorted({cap for row in rows for cap in row['capabilities']})
        lines += [f'### {label} — {len(rows)} Rules', '',
                  f'Capabilities represented ({len(caps)}): ' + ', '.join('`'+c+'`' for c in caps), '',
                  f'[Review Benchmark]({scope}/benchmark.yaml) · '
                  f'[Applicability placeholder]({scope}/applicability.yaml)', '',
                  '| SV-ID | Assessment | Rule | Capabilities | Features | Original proof status |',
                  '| --- | --- | --- | --- | --- | --- |']
        for row in rows:
            sv = row['sv']
            caps = ', '.join('`'+c+'`' for c in row['capabilities'])
            features = ', '.join('`'+c+'`' for c in row['features'] if not c.startswith('explicit-')) or 'simple'
            lines.append(f'| {sv} | [YAML]({scope}/assessments/automated/{sv}.automated.yaml) '
                f'| [Rule]({scope}/rules/{sv}.rule.yaml) | {caps} | {features} | '
                f'{row["status"]} |')
        lines += ['', '']
    lines += [
        '## Review points', '',
        '- Are Objects, Tests, `require`, Variables, `evaluate`, records and alternatives readable?',
        '- Do you see repeated or unhelpful metadata? Rule XML markup and long IDs are still present.',
        '- Are the `values_found` / `values_matching` controls and their inheritance understandable?',
        '- Which cases need a native capability instead of a shell command?',
        '- Which source behaviors need independent semantic checks?', '',
        'The [source provenance ledger](REVIEW-RECEIPT.json) preserves the original',
        'source ZIP hash, source Rule IDs, file hashes, original program hashes and',
        'historical proof statuses **as labels**, not as newly established claims.',
        'Do not interpret the subset as a full Benchmark or its historical proofs',
        'as scanner execution.', '',
        'Reproduce out-of-place with:', '',
        '```bash',
        'python tools/build_v04_expanded_authoring_review.py \\',
        '  --source-root <extracted-human-v2-root> \\',
        '  --output <new-nonexistent-directory>',
        '```', '',
    ]
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--per-scope', type=int, default=20)
    args = parser.parse_args()
    if args.per_scope != 20:
        raise ValueError('this published review is intentionally pinned at 20 examples per scope')
    if args.output.exists():
        raise ValueError('refusing to overwrite a review directory')
    if not (args.source_root / 'records/streams').is_dir():
        raise ValueError('missing original provenance sidecars')
    validators = build_validators(ROOT / 'schema/v0.4.0')
    gathered = {}
    for scope, anchor in CASES.items():
        entries = inventory(args.source_root, scope)
        gathered[scope] = (choose(entries, anchor, args.per_scope), len(entries))
    args.output.mkdir(parents=True)
    receipts = {scope: render_scope(args.source_root, args.output, scope, selected, count, validators)
                for scope, (selected, count) in gathered.items()}
    (args.output / 'README.md').write_text(markdown(receipts))
    (args.output / 'REVIEW-RECEIPT.json').write_text(json.dumps({
        'status': 'REVIEW_ONLY_NOT_SCANNER_PROVED', 'format': 'scap-ng-v04-expanded-authoring-review/1',
        'source_archive': 'immutable-human-v2', 'sample_scopes': len(receipts),
        'native_yaml_source_bytes': 'UNCHANGED',
        'schema_validated_documents': 84, 'compiled_isolated_packages': 2,
        'samples': receipts}, indent=2) + '\n')
    print(json.dumps({'per_scope': {k:len(v) for k,v in receipts.items()},
                      'validated_documents':84, 'compiled_isolated_packages':2,
                      'original_proofs_promoted':0}))


if __name__ == '__main__':
    main()
