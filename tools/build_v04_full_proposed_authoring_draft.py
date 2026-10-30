#!/usr/bin/env python3
"""Out-of-place 65-stream proposed authoring draft, never a release/proof.

Uses the same source-conservative presentation transform as the 40-Rule
review. Reads a pinned human-v2 export and retains its full 65-stream source
ledger by SHA/path reference. Copies unchanged files byte-for-byte; never
overwrites an immutable review archive. Refs #264 #265 #266.
"""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from zipfile import ZipFile, ZIP_DEFLATED

import yaml

from build_v04_proposed_authoring_review import transform_assessment
from v04_direct_yaml import authoring_yaml
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors


ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return sha256(raw).hexdigest()


def load_yaml(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('unsafe or missing pinned source: ' + str(path))
    raw = path.read_bytes()
    return yaml.safe_load(raw), raw


def source_bindings(source, scope):
    path = source / 'records/streams' / (scope + '.source-trace.json')
    trace = json.loads(path.read_text())
    bindings = {}
    for row in trace['rules']:
        match = re.search(r'SV-\d+', row['source_rule'])
        if not match:
            continue
        sv = match.group()
        if sv in bindings:
            raise ValueError('duplicate SV-ID source trace: ' + scope + '/' + sv)
        bindings[sv] = row
    return bindings, trace


def validate(doc, relpath, validators):
    kind = next(iter(doc))
    errors = list(document_errors(validators[kind + '.schema.json'], doc))
    if errors:
        raise ValueError(f'{relpath}: {errors[0]}')


def make_scope(source, out, scope, validators):
    src = source / 'authoring' / scope
    dst = out / 'authoring' / scope
    dst.mkdir(parents=True)
    bindings, trace = source_bindings(source, scope)
    files = sorted(src.rglob('*.yaml'))
    if len(files) < 4:
        raise ValueError('unexpectedly empty scope ' + scope)
    checks = Counter()
    edits = []
    documents = {}
    source_summary = Counter()
    for path in files:
        relative = path.relative_to(src)
        if path.is_symlink() or not path.is_file():
            raise ValueError('unsafe file in source')
        doc, original = load_yaml(path)
        kind = next(iter(doc))
        target = dst / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        candidate = doc
        draft = original
        if kind == 'assessment' and relative.parts[:2] == ('assessments', 'automated'):
            sv = relative.name.split('.')[0]
            if sv not in bindings:
                raise ValueError('automated Assessment has no pinned source trace: ' + scope + '/' + sv)
            try:
                candidate, test_edits = transform_assessment(doc, bindings[sv])
            except (ValueError, TypeError, KeyError) as exc:
                # Source conversion and structural validity are retained;
                # never silently rewrite an unsupported shape.
                checks['review_holds'] += 1
                edits.append({'sv': sv, 'status': 'UNCHANGED_NEEDS_REVIEW',
                              'reason': type(exc).__name__ + ': ' + str(exc)[:320],
                              'original_sha256': digest(original)})
            else:
                checks['tests_refactored'] += sum(
                    e['kind'] == 'field-policy-presentation' for e in test_edits)
                checks['pinned_state_folds'] += sum(
                    e['kind'] == 'pinned-source-state-scalar-and' for e in test_edits)
                checks['assessment_review_holds'] += sum(
                    e['kind'] == 'needs-further-review' for e in test_edits)
                if candidate != doc:
                    draft = authoring_yaml(candidate).encode()
                    if yaml.safe_load(draft) != candidate:
                        raise ValueError('YAML presentation roundtrip failed: ' + str(relative))
                    checks['assessments_changed'] += 1
                else:
                    checks['assessments_unchanged'] += 1
                if candidate != doc or test_edits:
                    edits.append({'sv': sv, 'status': ('PROPOSED_FORMAT' if candidate != doc
                                                    else 'UNCHANGED'),
                                  'original_sha256': digest(original),
                                  'candidate_sha256': digest(draft),
                                  'source_rule': bindings[sv]['source_rule'],
                                  'source_definition': bindings[sv]['definition'],
                                  'edits': test_edits})
            checks['automated_assessments'] += 1
        else:
            checks[kind + '_source_identical'] += 1
        validate(candidate, f'{scope}/{relative}', validators)
        target.write_bytes(draft)
        checks['schema_valid_documents'] += 1
        documents['authoring/' + scope + '/' + relative.with_suffix('.json').as_posix()] = candidate
        source_summary[kind] += 1
    # Each native stream is separately compilable; cross-stream placeholder
    # Benchmark/applicability identities are known to collide.
    compiled, _ = build_bundle(documents)
    if not compiled.startswith(b'PK'):
        raise ValueError('native compiler did not return an isolated package')
    checks['compiled_separate_scopes'] += 1
    # Receipts are separate: never re-label an original source proof as proof
    # of a different, merely schema-valid/compilable candidate program.
    return {
        'scope': scope, 'source_archive_sha256': trace['source_zip_sha256'],
        'source_member': trace['source_member'],
        'source_trace_file_sha256': digest(
            (source / 'records/streams' / (scope + '.source-trace.json')).read_bytes()),
        'counts': dict(sorted(checks.items())),
        'document_inventory': dict(sorted(source_summary.items())),
        'changed_and_held_assessments': edits,
        'source_proof_promoted': False,
        'scanner_verified': False,
    }


def package(output, path):
    if path.exists():
        raise ValueError('refusing to overwrite existing candidate ZIP')
    with ZipFile(path, 'w', ZIP_DEFLATED, compresslevel=6) as archive:
        for file in sorted(output.rglob('*')):
            if file.is_file():
                archive.write(file, file.relative_to(output).as_posix())
    return {'name': path.name, 'sha256': digest(path.read_bytes()), 'bytes': path.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--max-scopes', type=int)
    parser.add_argument('--zip-path', type=Path)
    args = parser.parse_args()
    if args.output.exists() or (args.zip_path and args.zip_path.exists()):
        raise ValueError('refusing to overwrite an existing output')
    source = args.source_root
    scopes = sorted(path.name for path in (source / 'authoring').iterdir() if path.is_dir())
    stream_names = sorted(path.name[:-5] for path in
        (source / 'records/streams').glob('*.json') if not path.name.endswith('.source-trace.json'))
    source_only = sorted(set(stream_names) - set(scopes))
    if len(scopes) != 60 or len(stream_names) != 65 or len(source_only) != 5:
        raise ValueError('this is not the pinned 60-native + five-source-only library')
    if args.max_scopes:
        if args.max_scopes < 1:
            raise ValueError('--max-scopes must be positive')
        selected = scopes[:args.max_scopes]
    else:
        selected = scopes
    validators = build_validators(ROOT / 'schema/v0.4.0')
    args.output.mkdir(parents=True)
    receipts = []
    aggregate = Counter()
    for i, scope in enumerate(selected, 1):
        result = make_scope(source, args.output, scope, validators)
        receipts.append(result)
        aggregate.update(result['counts'])
        print(f'{i}/{len(selected)} {scope}: {result["counts"].get("automated_assessments",0)} '
              f'Assessments, {result["counts"].get("assessments_changed",0)} changed, '
              f'{result["counts"].get("review_holds",0)} held', flush=True)
    receipt = {
        'status': 'PROPOSED_FULL_LIBRARY_REVIEW_DRAFT_NOT_SCANNER_PROVED',
        'source': 'immutable-human-v2', 'source_native_streams': len(scopes),
        'source_only_streams': source_only, 'selected_streams': len(selected),
        'all_65_selected': len(selected) == 60,
        'source_records_retained_by_sha_reference': True,
        'new_compiled_proofs_promoted': 0,
        'scanner_verified': False,
        'cross_stream_compilation_claim': False,
        'counts': dict(sorted(aggregate.items())), 'scopes': receipts,
    }
    (args.output / 'REVIEW-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (args.output / 'README.md').write_text(
        '# SCAP-NG 0.4.0 — full-library proposed field-policy review\n\n'
        '**Draft review only. Not final 0.4.0, not scanner-verified.**\n\n'
        f'Contains {len(selected)} of 60 native authoring streams plus receipt references '
        'to all 65 original source streams (five remain source-only).\n'
        'Original files were not modified. This projection only hoists safe '
        'Test-level field count policies and uniquely source-pinned single-State '
        'scalar conjunctions. Datatype, purpose, IDs, Benchmark completeness '
        'and applicability remain separate questions.\n\n'
        'Every changed Assessment has an original preimage and SHA in '
        '[REVIEW-RECEIPT.json](REVIEW-RECEIPT.json). Original static proofs '
        'must not be attributed to changed programs. Each selected '
        'native stream compiled independently.\n')
    if args.zip_path:
        print(json.dumps({'counts': receipt['counts'], 'zip': package(args.output, args.zip_path)},
                         indent=2))
    else:
        print(json.dumps({'counts': receipt['counts']}, indent=2))


if __name__ == '__main__':
    main()
