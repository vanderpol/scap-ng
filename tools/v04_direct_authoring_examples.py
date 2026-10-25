"""Reproduce six browsable, original-source-proved authoring examples and counts.

Selection is by emitted structure, never an admission allowlist. All supported
Rules are proved and compiled before representatives are copied. Output is new
or empty; generated evidence is not hand-edited. No normative files are changed.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess

import yaml
from v04_direct_scap_source import SourceModel, digest
from v04_direct_converter import convert, convert_benchmark
from v04_direct_yaml import authoring_yaml, compact_registry_object
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors
from v04_object_contract import object_sites

ROOT = Path(__file__).resolve().parents[1]
DEPRECATED = {'state', 'states', 'states_match', 'state_fields_require', 'select', 'collect',
              'matching_items', 'matching_records', 'all', 'any', 'odd'}


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def authoring_statistics(documents):
    counts = Counter()
    for document in documents.values():
        if 'assessment' not in document:
            continue
        assessment = document['assessment']
        counts['assessments'] += 1
        counts['tests'] += len(assessment['tests'])
        shared = assessment.get('shared_objects', {})
        counts['shared_objects'] += len(shared)
        references = Counter(node['object'] for node in walk(assessment)
                             if isinstance(node.get('object'), str))
        counts['multiply_used_named_objects'] += sum(references[name] > 1 for name in shared)
        for test in assessment['tests'].values():
            counts['inline_objects' if isinstance(test.get('object'), dict) else
                   'shared_object_tests' if 'object' in test else 'no_object_tests'] += 1
        for site in object_sites(assessment):
            if site.private and compact_registry_object(site.node, site.capability):
                counts['one_line_objects'] += 1
        for node in walk(assessment):
            counts['deprecated_grammar'] += len(set(node) & DEPRECATED)
    return {key: counts[key] for key in ('assessments', 'tests', 'inline_objects', 'shared_object_tests',
        'no_object_tests', 'shared_objects', 'multiply_used_named_objects', 'one_line_objects', 'deprecated_grammar')}


def choose_examples(documents):
    assessments = [d['assessment'] for d in documents.values() if 'assessment' in d]
    predicates = {
        '01-inline-registry': lambda a: len(a['tests']) == 1 and any(
            compact_registry_object(t.get('object'), t['capability']) for t in a['tests'].values()),
        '02-shared-object': lambda a: bool(a.get('shared_objects')),
        '03-system-audit-policy': lambda a: all(t['capability'] == 'windows.auditeventpolicysubcategories'
                                               and 'object' not in t for t in a['tests'].values()),
        '04-multiple-tests': lambda a: len(a['tests']) > 1 and bool(set(a['evaluate']) & {'and', 'or', 'one', 'xor'}),
        '05-nested-set': lambda a: any('set' in node for node in walk(a)),
        '06-variable-dependencies': lambda a: bool(a.get('variables')),
    }
    selected, used = {}, set()
    for name, predicate in predicates.items():
        assessment = next(a for a in assessments if a['id'] not in used and predicate(a))
        selected[name] = assessment
        used.add(assessment['id'])
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error('output must be new or empty')
    pins = json.loads((ROOT / 'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
    source = SourceModel(ROOT / 'tests/fixtures/v04-direct-prototype' / pins['fixture'], pins['zip_sha256'])
    documents, trace, coverage = convert_benchmark(source)
    proofs = verify_original(source.root, documents, trace)
    programs = verify_compiled(documents, build_bundle(documents)[0])
    baseline = json.loads((ROOT / 'docs/audit/v04-audit-policy-direct.json').read_text())
    old_programs = {p['assessment']: p['program_sha256'] for p in baseline['all_programs']}
    program_comparison = {'baseline_implementation': baseline['result_sha'],
        'baseline_programs': len(old_programs), 'current_programs': len(programs),
        'unchanged_program_hashes': sum(old_programs.get(p['assessment']) == p['program_sha256'] for p in programs),
        'changed_or_new_programs': [p for p in programs if old_programs.get(p['assessment']) != p['program_sha256']]}
    validators = build_validators(ROOT / 'schema/v0.4.0')
    for document in documents.values():
        kind, = document
        assert not list(document_errors(validators[kind + '.schema.json'], document))
        assert yaml.safe_load(authoring_yaml(document)) == document
    selected = choose_examples(documents)
    bindings = {row['assessment']: row for row in trace['rules']}
    # Compile the exact selected subset too; whole-source compilation alone is
    # not evidence that these examples have a closed Benchmark/Rule wrapper.
    subset, subset_trace = convert(source, [bindings[a['id']]['source_rule'] for a in selected.values()])
    verify_original(source.root, subset, subset_trace)
    verify_compiled(subset, build_bundle(subset)[0])
    args.output.mkdir(parents=True, exist_ok=True)
    examples = []
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for name, assessment in selected.items():
        document = {'assessment': assessment}
        filename = assessment['id']
        (args.output / (filename + '.json')).write_text(json.dumps(document, indent=2) + '\n')
        (args.output / (filename + '.yaml')).write_text(authoring_yaml(document))
        examples.append({'category': name, 'file': filename, 'title': assessment['assessment_title'],
            'binding': bindings[assessment['id']],
            'native_sha256': digest(document), 'schema_capability_validation': 'PASS',
            'yaml_json_structural_equality': True, 'compilation': 'PASS', 'original_source_proof': 'PROVED'})
    packet = {'schema_version': '0.4.0', 'converter_commit': commit,
        'source_benchmark': source.benchmark.get('id'), 'source_zip_sha256': source.zip_sha256,
        'source_xml_sha256': source.xml_sha256, 'statistics': authoring_statistics(documents),
        'schema_valid_json_documents': len(documents), 'schema_valid_yaml_documents': len(documents),
        'source_proved': len(proofs), 'compiled_programs': len(programs), 'compiled_unproved': 0,
        'compiled_program_comparison': program_comparison,
        'blocked': len(trace['omitted_rules']), 'examples': examples,
        'limitations': 'Representative automated subset; not complete policy, scanner parity or a production release. '
                        'No nonempty Filter is source-proved in this subset; nested Sets are real original source.'}
    (args.output / 'manifest.json').write_text(json.dumps(packet, indent=2) + '\n')
    links = '\n'.join(f'- {e["category"].split("-", 1)[1]}: [{e["title"]}]({e["file"]}.yaml) · '
                      f'[JSON]({e["file"]}.json)' for e in examples)
    (args.output / 'README.md').write_text('# Direct 0.4.0 representative automated-subset examples\n\n' +
        'Actual converter output from the pinned original Windows Server 2025 SCAP 1.4 package.\n'
        'These are Assessments, not a complete Benchmark or six-STIG release.\n\n' + links + '\n\n' +
        '[Manifest](manifest.json) records original Benchmark/Rule/Definition IDs, dependency hashes, '
        'converter SHA and validation, compilation and independent proof outcomes.\n'
        'The nested Set example has no nonempty Filters; none is independently proved in the current subset.\n\n'
        'Regenerate into a new directory from the pinned converter commit:\n\n'
        '```bash\nPYTHONPATH=tools python tools/v04_direct_authoring_examples.py --output /tmp/direct-authoring-examples\n```\n\n'
        'Use PyYAML 6.0.3 and jsonschema 4.25.1; see the [developer guide](../../developer/DIRECT-V04-CONVERTER.md). '
        'The command revalidates/proves/compiles the entire supported subset and the selected closed wrapper. '
        'Generated files are not edited by hand. Signature trust and scanner equivalence are not claimed.\n')
    print(json.dumps(packet['statistics'], indent=2))


if __name__ == '__main__':
    main()
