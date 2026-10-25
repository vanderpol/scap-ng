#!/usr/bin/env python3
"""Read-only 4,012-source/six-package Object audit and one corrected candidate.

No source archive or published package output; no corpus semantic-proof sweep.
The separately emitted candidate uses the explicit historical migration API.
Refs #251.
"""
import argparse
from collections import Counter
import csv
from hashlib import sha256
import json
from pathlib import Path
import zipfile

from audit_v04_eight_assessment_pilot import BASE, ROOT, original
from v04_a_authoring_graph_index import read_authoring_archive
from v04_flat_object_authoring import flatten_document, restore_document, load_catalog, dump_hybrid
from v04_object_contract import object_sites, object_errors, format_path
from v04_expanded_source_proof import ExpandedSource, expanded_compare
from verify_v04_package_consumer import digest, read_json, require
from v04_native_bundle_compiler import compile_from_pair


def census(documents, view, catalog, cache):
    sites, failures, changed = [], [], []
    counts, by_capability, by_context = Counter(), Counter(), Counter()
    for name, doc in sorted(documents.items()):
        fixed, proof = flatten_document(doc, catalog)
        require(restore_document(fixed, proof) == doc, 'Object migration source inverse failed')
        key = digest(doc)
        if key not in cache:
            before = [{'path': format_path(e.path), 'message': e.message, 'validator': e.validator}
                      for e in object_errors(doc)]
            after = [{'path': format_path(e.path), 'message': e.message, 'validator': e.validator}
                     for e in object_errors(fixed)]
            cache[key] = before, after
        before, after = cache[key]
        require(before or not after, 'previously valid canonical document lost acceptance: ' + name)
        counts.update(documents=1, invalid_before=bool(before), invalid_after=bool(after),
                      schema_errors_before=len(before), schema_errors_after=len(after),
                      changed_documents=bool(proof['edits']), wrapper_edits=len(proof['edits']))
        if proof['edits']:
            changed.append({'document': name, 'edits': proof['edits']})
        if before or after:
            failures.append({'document': name, 'before': before, 'after_flatten_only': after})
        fixed_sites = {s.path: s for s in object_sites(fixed.get('assessment', {}))}
        for s in object_sites(doc.get('assessment', {})):
            wrappers = sorted(set(s.node) & {'select', 'collect'} - ({'select'} if s.capability == 'windows.cmdlet' else set()))
            exception = s.capability == 'windows.cmdlet' and 'select' in s.node
            by_capability[s.capability] += 1
            by_context[s.context] += 1
            counts.update(object_sites=1, variable_sites=s.context.startswith('variable'),
                          generic_wrapper_sites=bool(wrappers), cmdlet_select_exceptions=exception)
            sites.append({'view': view, 'document': name, 'path': format_path(s.path),
                'parent_section': s.context, 'capability': s.capability,
                'explicit_capability': s.node.get('capability', ''),
                'inherited_capability': s.inherited or '', 'generic_wrappers': ';'.join(wrappers),
                'cmdlet_select_exception': exception, 'before_sha256': digest(s.node),
                'after_sha256': digest(fixed_sites[s.path].node)})
    return {'view': view, 'counts': dict(counts), 'by_capability': dict(by_capability),
            'by_parent_section': dict(by_context), 'canonical_document_regressions': 0,
            'invalid_documents': failures, 'changed_documents': changed}, sites


def candidate(inputs, documents, catalog, output):
    name = 'authoring/ms_windows_server_2025/assessments/automated/SV-278139.automated.json'
    source = documents[name]
    fixed, proof = flatten_document(source, catalog)
    require(not list(object_errors(fixed)), 'corrected SYSVOL Object graph is still invalid')
    pins = json.loads((BASE / 'source-ledger.json').read_text())['sources']
    oval, definition, trace = original(inputs, 'ms_windows_server_2025', 'SV-278139', pins,
                                      source_type=ExpandedSource)
    comparison = expanded_compare(oval, definition, fixed['assessment'])
    require(comparison['outcome'] == 'PROVED', 'corrected SYSVOL candidate has unresolved original-source semantics')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'SV-278139.corrected.assessment.json').write_text(json.dumps(fixed, indent=2) + '\n')
    rendered = dump_hybrid(fixed)
    (output / 'SV-278139.corrected.assessment.yaml').write_text(rendered)
    # Closed synthetic compilation harness only; positive source proof above
    # uses the exact original Rule/Definition and complete corrected Assessment.
    from test_v04_package_consumer import fixture
    from test_v04_public_cli_smoke import authoring_archives
    import tempfile
    docs = fixture()
    docs['authoring/demo/assessments/a1.json'] = fixed
    docs['authoring/demo/rules/r1.json']['rule']['assessment_choices']['automated']['assessment'] = fixed['assessment']['id']
    with tempfile.TemporaryDirectory() as td:
        js, ya = authoring_archives(docs, Path(td))
        bundles, reports = compile_from_pair(js, ya)
        import io
        with zipfile.ZipFile(io.BytesIO(bundles['demo'])) as z:
            manifest = read_json(z.read('META-INF/manifest.json'))
            row = manifest['build_provenance']['compiled_programs'][fixed['assessment']['id']]
            program = read_json(z.read(row['path']))
    require(program['assessment_source_sha256'] == digest(fixed['assessment']), 'candidate compiled source identity')
    result = {'scope': 'one corrected candidate, not a replacement of the pinned package or coverage promotion',
        'source_document': name, 'before_sha256': digest(source), 'after_sha256': digest(fixed),
        'migration': proof, 'source_inverse_exact': restore_document(fixed, proof) == source,
        'original_source': trace, 'independent_source_comparison': comparison,
        'compiled_program': program, 'compiled_program_sha256': digest(program),
        'yaml_json_compiled_bytes_equal': True, 'compile_harness_report': reports,
        'proof_coverage_changed': False, 'scanner_evaluated': False}
    (output / 'SV-278139.candidate-proof.json').write_text(json.dumps(result, indent=2) + '\n')
    return {'before_sha256': result['before_sha256'], 'after_sha256': result['after_sha256'],
            'source_inverse_exact': True, 'candidate_source_comparison': comparison['outcome'],
            'compiled_program_sha256': result['compiled_program_sha256'], 'coverage_promoted': False}


def run(source_json, source_yaml, bundles, inputs, output):
    accepted = json.loads((BASE / 'consumer-results.json').read_text())
    require(sha256(source_json.read_bytes()).hexdigest() == accepted['source_hashes']['json']
            and sha256(source_yaml.read_bytes()).hexdigest() == accepted['source_hashes']['yaml'], 'pinned source archive drift')
    docs = read_authoring_archive(source_json, 'json')
    yaml_docs = read_authoring_archive(source_yaml, 'yaml')
    require(len(docs) == 4012 and docs == {k.removesuffix('.yaml') + '.json': d for k, d in yaml_docs.items()},
            '4,012-document JSON/YAML source parity failed')
    catalog = load_catalog(ROOT / 'schema/v0.4.0/capability-mappings/supported')
    cache, rows, views = {}, [], []
    view, sites = census(docs, 'authoring', catalog, cache)
    views.append(view)
    rows.extend(sites)
    for platform, pin in accepted['results'].items():
        path = bundles / (platform + '.scapng')
        require(sha256(path.read_bytes()).hexdigest() == pin['bundle_sha256'], 'pinned bundle drift')
        with zipfile.ZipFile(path) as z:
            require(z.testzip() is None, 'bundle CRC mismatch')
            m = read_json(z.read('META-INF/manifest.json'))
            package_docs = {i['path']: read_json(z.read(i['path'])) for i in m['objects'].values()}
        v, sites = census(package_docs, platform, catalog, cache)
        v['bundle_sha256'] = pin['bundle_sha256']
        views.append(v)
        rows.extend(sites)
    output.mkdir(parents=True, exist_ok=True)
    csv_path = output / 'object-sites.csv'
    with csv_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    result = {'status': 'READ_ONLY_OBJECT_CONTRACT_AUDIT_NOT_CORPUS_REGENERATION',
        'source_archive_sha256': accepted['source_hashes'], 'views': views,
        'site_inventory': {'path': csv_path.name, 'rows': len(rows), 'sha256': sha256(csv_path.read_bytes()).hexdigest()},
        'canonicalized_view': 'explicit reversible Object wrapper flattening in memory only; other historical predicate-token defects remain visible',
        'candidate': candidate(inputs, docs, catalog, output),
        'six_packages_or_archives_written': False, 'coverage_promoted': False, 'scanner_evaluated': False}
    (output / 'object-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-json', type=Path, required=True)
    p.add_argument('--source-yaml', type=Path, required=True)
    p.add_argument('--bundles-dir', type=Path, required=True)
    p.add_argument('--inputs-dir', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    a = p.parse_args()
    r = run(a.source_json, a.source_yaml, a.bundles_dir, a.inputs_dir, a.output_dir)
    print(json.dumps({'views': [{k: v[k] for k in ('view', 'counts')} for v in r['views']], 'candidate': r['candidate']}))
