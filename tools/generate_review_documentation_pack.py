#!/usr/bin/env python3
"""Issue #43 Phase A: one review-only schema/documentation/editor-metadata pack.

No release version, production editor association, scanner behavior or frozen
schema is changed. --materialize writes only the purpose-specific pack tree.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import subprocess
from urllib.parse import urljoin, urldefrag

from jsonschema import Draft202012Validator
import yaml

import audit_schema_documentation as audit
from generate_approved_annotation_pilot import remap
from generate_unix_file_reference import child
from schema_documentation_pack import load_pack, resolve_help
from schema_documentation import (SchemaStore, pointer, parts, types, options,
    display_type, property_occurrences, collection_occurrences, description_lookup)

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('docs/review-packs/issue43-phase-a')
PREFIX = 'https://scap-ng.dev/schema/review/issue43-phase-a/'
CAP = PREFIX + 'capabilities/unix.file.schema.json'
SOURCE = Path('docs/pilots/unix-file/schema-next/capabilities/unix.file.schema.json')
COMMITS = {'native': audit.NATIVE_COMMIT, 'pr39': audit.PILOT_COMMIT,
           'pr41': '532fbbfe52a220d2672256ac54d1e117d69cd043'}


def encode(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def digest(raw):
    return sha256(raw).hexdigest()


def resource_file(uri):
    if not uri.startswith(PREFIX):
        raise ValueError('Outside coordinated review namespace: ' + uri)
    return DEST / 'schemas' / uri[len(PREFIX):]


def refs(node):
    if isinstance(node, dict):
        if '$ref' in node:
            yield node['$ref']
        for v in node.values():
            yield from refs(v)
    elif isinstance(node, list):
        for v in node:
            yield from refs(v)


def _historical_overlay(root, workspace, pins):
    """Overlay non-native historical helper files by exact Git blob receipt."""
    for path, expected in pins['files'].items():
        candidates = list(pins['source_commits'].values())
        candidates += subprocess.check_output(
            ['git', '-C', str(root), 'log', '--all', '--format=%H', '--', path], text=True).split()
        for commit in dict.fromkeys(candidates):
            try:
                raw = subprocess.check_output(['git', '-C', str(root), 'show', f'{commit}:{path}'], stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                continue
            if digest(raw) == expected:
                target = workspace / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                break
        else:
            raise ValueError('Unable to materialize historical input: ' + path)


def build(root=ROOT):
    if root == ROOT:
        with audit.historical_workspace(root) as workspace:
            pins = json.loads((root / DEST / 'input-pins.json').read_text())
            pinned_file = workspace / DEST / 'input-pins.json'
            pinned_file.parent.mkdir(parents=True, exist_ok=True)
            pinned_file.write_text((root / DEST / 'input-pins.json').read_text())
            _historical_overlay(root, workspace, pins)
            # The worksheet/review-note records were amended after the native
            # schema commit; materialize their exact recorded Git blobs too.
            for path in ('docs/research/issue40/review-notes.json',
                         'docs/research/issue40/editorial-batch.json',
                         'docs/research/issue40/editorial-batch-2.json',
                         'docs/research/issue40/schema-manifest.json'):
                expected = digest((root / path).read_bytes())
                candidates = subprocess.check_output(['git', '-C', str(root), 'log', '--all', '--format=%H', '--', path], text=True).split()
                for commit in candidates:
                    try:
                        raw = subprocess.check_output(['git', '-C', str(root), 'show', f'{commit}:{path}'], stderr=subprocess.DEVNULL)
                    except subprocess.CalledProcessError:
                        continue
                    if digest(raw) == expected:
                        target = workspace / path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw); break
            return _build(workspace)

def _build(root=ROOT):
    pins = json.loads((root / DEST / 'input-pins.json').read_text())
    if pins['source_commits'] != COMMITS or pins['review_only'] is not True:
        raise ValueError('Unexpected historical source commit or release identity')
    for name, expected in pins['files'].items():
        if digest((root / name).read_bytes()) != expected:
            raise ValueError('Pinned source input drifted: ' + name)
    result = audit.audit(root, active=False)
    routes = {uri: PREFIX + uri.rsplit('/', 1)[-1] for uri in sorted(result['documents'])}
    docs = {routes[uri]: remap(doc, uri, routes) for uri, doc in result['documents'].items()}
    # Known authoring-condition pointers are metadata routing, not new assertions.
    metadata_routes = []
    def authoring_routes(node, base, path=''):
        if isinstance(node, list):
            for i, value in enumerate(node):
                authoring_routes(value, base, path + '/' + str(i))
        elif isinstance(node, dict):
            if 'condition_schema' in node:
                old = node['condition_schema']; uri, frag = urldefrag(old)
                if uri in routes:
                    node['condition_schema'] = routes[uri] + '#' + frag
                    metadata_routes.append({'resource': base, 'pointer': path + '/condition_schema', 'old': old, 'new': node['condition_schema']})
            for key, value in node.items():
                authoring_routes(value, base, path + '/' + audit.escape(key))
    for uri, doc in docs.items():
        authoring_routes(doc, uri)
    original = deepcopy(docs)
    annotations = []
    def annotate(target, text, source, source_pointer, provenance):
        uri, frag = urldefrag(target)
        node = pointer(docs[uri], frag)
        annotations.append({'source_file': source, 'source_pointer': source_pointer,
            'description_owner': target + '/description', 'previous_description': node.get('description'), 'provenance': provenance})
        node['description'] = text
    pilot = json.loads((root / SOURCE).read_text())
    source_map = json.loads((root / 'docs/pilots/unix-file/source-map.json').read_text())
    fields = deepcopy(pilot['$defs']['field_meanings'])
    cap = {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': CAP,
           '$comment': 'Review-only annotation library. No datatype/tag tightening or runtime semantics.',
           '$defs': {'field_meanings': fields}}
    docs[CAP] = cap
    for source_pointer, info in source_map['descriptions'].items():
        text = pointer(pilot, source_pointer)['description']
        if source_pointer.startswith('/$defs/field_meanings'):
            target = CAP + '#' + source_pointer
            # field_meanings was copied solely as ordinary schema annotations.
            pointer(cap, source_pointer).pop('description')
        elif source_pointer == '/$defs/value_owner_read':
            target = CAP + '#/$defs/field_meanings/properties/owner_read'
            text = pointer(cap, '/$defs/field_meanings/properties/owner_read')['description'] + '\n\n' + text
        else:
            native_file, frag = info['native_pointer'].split('#') if '#' in info['native_pointer'] else (info['native_pointer'], '')
            target = PREFIX + native_file + '#' + frag
        annotate(target, text, str(SOURCE), source_pointer, {'pr': 39, 'commit': COMMITS['pr39'], 'source_record': info})
    selection = json.loads((root / 'docs/pilots/approved-annotations/selection.json').read_text())
    core = []
    batches = {name: audit.editorial_batch(result, root, name)[0] for name in sorted({e['batch'] for e in selection['entries']})}
    for entry in selection['entries']:
        row = next(r for r in batches[entry['batch']]['proposals'] if r['id'] == entry['case'])
        if row['classification'] != 'editorial' or row['editorial_status'] not in {'accepted_as_written', 'accepted_with_revision'}:
            raise ValueError('Semantic hold cannot enter review pack')
        target = routes[row['schema_uri']] + '#' + row['pointer']
        annotate(target, row['author_description'], str(audit.DEST / entry['batch']), '/proposals/' + str(batches[entry['batch']]['proposals'].index(row)) + '/author_description', {'pr': 41, 'commit': COMMITS['pr41'], 'case': row['id'], 'approval_url': row['editorial_review_url']})
        core.append({'name': entry['name'], 'schema_pointer': routes[row['schema_uri']] + '#' + entry.get('lookup_pointer', row['pointer']), 'description_owner': target + '/description', 'witnesses': row['checks']})
    # Annotation-only applicators preserve the generic 0.4 Item/Require grammar.
    field_props = {name: {'$ref': CAP + '#/$defs/field_meanings/properties/' + name} for name in fields['properties']}
    overlay = {'properties': {'fields': {'properties': field_props}}}
    for op in ['and', 'or', 'one', 'xor']:
        overlay['properties'][op] = {'items': {'$ref': CAP + '#/$defs/require_help'}}
    cap['$defs']['require_help'] = overlay
    cap['$defs']['item_help'] = {'properties': {'fields': {'properties': deepcopy(field_props)}}}
    def conditional(target):
        return {'if': {'required': ['capability'], 'properties': {'capability': {'const': 'unix.file'}}}, 'then': {'$ref': target}}
    dispatch = [
        (PREFIX + 'assessment-language.schema.json#/$defs/test', conditional(CAP + '#/$defs/test_help')),
        (PREFIX + 'collected-item.schema.json#', conditional(CAP + '#/$defs/item_help'))]
    cap['$defs']['test_help'] = {'properties': {'require': {'$ref': CAP + '#/$defs/require_help'}}}
    for target, branch in dispatch:
        uri, frag = urldefrag(target)
        pointer(docs[uri], frag).setdefault('allOf', []).append(branch)
    # Independently reversible native tree delta: remove two neutral dispatch
    # branches and restore only changed annotations. $defs on CAP are proved
    # assertion-free below; no type/value tightening is copied from PR #39.
    restored = deepcopy(docs)
    for target, _branch in dispatch:
        uri, frag = urldefrag(target); pointer(restored[uri], frag)['allOf'].pop()
        if 'allOf' not in pointer(original[uri], frag):
            pointer(restored[uri], frag).pop('allOf')
    for a in reversed(annotations):
        uri, frag = urldefrag(a['description_owner']); parent = pointer(restored[uri], frag.rsplit('/', 1)[0])
        if a['previous_description'] is None:
            parent.pop('description', None)
        else:
            parent['description'] = a['previous_description']
    for uri in original:
        if restored[uri] != original[uri]:
            raise ValueError('Unapproved structural/annotation delta: ' + uri)
    def neutral(node, seen=()):
        if not isinstance(node, dict) or set(node) - {'description', '$ref', 'properties', 'items'}:
            return False
        if '$ref' in node:
            target = node['$ref']
            if not target.startswith(CAP + '#'):
                return False
            if target not in seen and not neutral(pointer(cap, target.split('#')[1]), seen + (target,)):
                return False
        return all(neutral(v, seen) for v in node.get('properties', {}).values()) and ('items' not in node or neutral(node['items'], seen))
    if not all(neutral(n) for n in cap['$defs'].values()):
        raise ValueError('Capability annotation dispatch contains validation assertions')
    store = SchemaStore(docs)
    for uri, doc in docs.items():
        Draft202012Validator.check_schema(doc)
        for ref in refs(doc):
            absolute = urljoin(uri, ref)
            if not absolute.startswith(PREFIX):
                raise ValueError('Competing/outside schema namespace: ' + absolute)
            store.node(absolute)
    vectors = json.loads((root / 'tests/fixtures/issue43-validation-cases.json').read_text())
    cases = deepcopy(vectors['cases'])
    for selected in core:
        for i, case in enumerate(selected['witnesses']):
            uri, frag = urldefrag(case['schema_uri'])
            if 'instance_file' in case:
                raw = (root / case['instance_file']).read_bytes()
                if digest(raw) != case['instance_sha256']:
                    raise ValueError('Pinned core witness drifted')
                instance = yaml.safe_load(raw)
            else:
                instance = case['instance']
            cases.append({'name': 'core-' + selected['name'] + '-' + str(i), 'schema_file': uri.rsplit('/', 1)[-1], 'pointer': frag, 'instance': instance, 'expected_valid': case['expected_valid']})
    evidence = []
    for case in cases:
        before = Draft202012Validator({'$ref': audit.PREFIX + case['schema_file'] + '#' + case['pointer']}, registry=result['store'].registry).is_valid(case['instance'])
        after = Draft202012Validator({'$ref': PREFIX + case['schema_file'] + '#' + case['pointer']}, registry=store.registry).is_valid(case['instance'])
        if before != case['expected_valid'] or after != case['expected_valid']:
            raise ValueError('Before/after structural witness disagrees: ' + case['name'] + ' / ' + str((before, after)))
        evidence.append({'name': case['name'], 'expected_valid': case['expected_valid'], 'native_valid': before, 'review_pack_valid': after})
    provenance = {'source_commits': COMMITS, 'annotations': annotations, 'metadata_uri_routes': metadata_routes,
                  'structural_parity': [{'resource': uri, 'normalized_restored_sha256': audit.digest(restored[uri]), 'normalized_native_sha256': audit.digest(original[uri])} for uri in sorted(original)],
                  'neutral_dispatch_branches': [target for target, _ in dispatch],
                  'validation_evidence': evidence, 'validation_cases': cases,
                  'held_proposals_excluded': {name: [r['id'] for r in batch['proposals'] if r['classification'] != 'editorial'] for name, batch in batches.items()}}
    return store, provenance, core, pins


def outputs(store, provenance, core, pins):
    entries = []
    def entry(capability, role, field, schema_pointer, parent=None, parent_name=None, context=None):
        found = description_lookup(store, schema_pointer)
        node = store.node(schema_pointer)
        rows = {'capability': capability, 'role': role, 'field': field, 'schema_pointer': schema_pointer,
                'description_pointer': found['description_pointer'], 'description': found['description'],
                'type': (display_type(node, schema_pointer, store) if role == 'object' else types(node, schema_pointer, store)), 'options': options(node, schema_pointer, store)}
        if parent is not None:
            rows['parent_schema_pointer'] = parent
            if context is not None and isinstance(context, dict):
                for shape in parts(node, schema_pointer, store):
                    if 'enum' in shape:
                        validator = Draft202012Validator({'$ref': parent}, registry=store.registry)
                        choices = [v for v in shape['enum'] if validator.is_valid(dict(context, **{parent_name or field: v}))]
                        rows['options'] = options({'enum': choices}, schema_pointer, store)
                        rows['options_context'] = context
            rows['occurrences'] = property_occurrences(store.node(parent), parent, parent_name or field, store, context)
        else:
            rows['occurrences'] = '—'
        entries.append(rows)
    obj = PREFIX + 'native-selector.schema.json#/$defs/unix_file_object'
    inline = obj + '/oneOf/1'
    object_fields = ['filepath', 'path', 'filename', 'filesystem', 'traversal']
    for name in object_fields:
        entry('unix.file', 'object', name, inline + '/properties/' + name, inline)
    traversal = PREFIX + 'capability-common.schema.json#/$defs/file_traversal'
    for name, ptr in [('max_depth', '/$defs/file_traversal_base/properties/max_depth'), ('recurse', '/$defs/file_traversal/allOf/1/properties/recurse')]:
        entry('unix.file', 'object', 'traversal.' + name, PREFIX + 'capability-common.schema.json#' + ptr, traversal, name)
    field_map = PREFIX + 'collected-item.schema.json#/properties/fields'
    req_map = PREFIX + 'assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields'
    for name in store.node(CAP + '#/$defs/field_meanings')['properties']:
        for role in ['item', 'require']:
            schema_ptr = CAP + '#/$defs/' + ('item_help' if role == 'item' else 'require_help') + '/properties/fields/properties/' + name
            entry('unix.file', role, 'fields.' + name, schema_ptr)
            if role == 'item':
                entries[-1]['type'] = types(store.node(field_map)['additionalProperties'], field_map, store)
                entries[-1]['occurrences'] = property_occurrences(store.node(field_map), field_map, name, store) + ' key'
                entries[-1]['validation_pointer'] = field_map + '/additionalProperties'
            else:
                entries[-1]['type'] = types(store.node(PREFIX + 'assessment-language.schema.json#/$defs/canonical_field_predicate'), PREFIX + 'assessment-language.schema.json', store)
                entries[-1]['occurrences'] = property_occurrences(store.node(req_map), req_map, name, store) + ' key'
                entries[-1]['validation_pointer'] = req_map + '/additionalProperties'
    req = PREFIX + 'assessment-language.schema.json#/$defs/canonical_all_items_requirement'
    context = {'item_requirement': {'items_found': 'one_or_more', 'items_satisfying': 'every'}, 'field_requirement': {'values_found': 'one_or_more', 'values_matching': 'every'}, 'fields': {'name': {'equals': 'x'}}}
    for name in ['item_requirement', 'field_requirement', 'fields']:
        entry('unix.file', 'require', name, req + '/properties/' + name, req)
    for parent, names, source in [('item_requirement', ['items_found', 'items_satisfying'], req + '/properties/item_requirement'), ('field_requirement', ['values_found', 'values_matching'], PREFIX + 'assessment-language.schema.json#/$defs/paired_requirement')]:
        for name in names:
            entry('unix.file', 'require', parent + '.' + name, source + '/properties/' + name, source, name, context['field_requirement'] if parent == 'field_requirement' else None)
    for row in core:
        entry('core', 'shared', row['name'], row['schema_pointer'])
    resources = {uri: {'file': str(resource_file(uri).relative_to(DEST)), 'sha256': digest(encode(doc).encode())} for uri, doc in sorted(store.documents.items())}
    metadata = {'format': 'scap-ng-review-editor-metadata-1', 'review_only': True, 'release_version': None,
                'resource_index_sha256': audit.digest(resources), 'source_commits': COMMITS, 'live_vscode_ui_verified': False,
                'yaml_entrypoints': {'assessment': PREFIX + 'assessment.schema.json', 'collected_item': PREFIX + 'collected-item.schema.json'}, 'entries': entries}
    def cell(v):
        return str(v).replace('|', '&#124;').replace('\n', ' ')
    def table(rows):
        return ['| Field | Type | Occurrences | Description |', '| --- | --- | --- | --- |'] + ['| ' + ' | '.join(cell(v) for v in [r['field'], r['type'], r['occurrences'], r['description'].split('\n\n')[0] + (' ' + r['options'] if r['options'] else '')]) + ' |' for r in rows]
    lines = ['# Review-only documentation pack', '', '<!-- Generated: python tools/generate_review_documentation_pack.py -->', '',
             '**Issue #43 Phase A only; no approved release or live editor proof.**', '', '[Advanced constraints](constraints.md) · [Integration receipt](RECEIPT.md).', '', '## unix.file Object', '',
             description_lookup(store, obj)['description'].split('\n\n')[0], '',
             'Occurrences below apply to the inline Object branch. Selector pairing is not enforced by 0.4.0; no new pairing rule is added.', '']
    lines += table([r for r in entries if r['role'] == 'object' and '.' not in r['field']])
    lines += ['', '### traversal', '', 'Child occurrences apply when traversal is present; array/map entries are separate from named properties.', ''] + table([r for r in entries if r['role'] == 'object' and '.' in r['field']])
    lines += ['', '## unix.file collected Item', '',
              'The generic 0.4.0 typed-value wrapper or array remains accepted. Payload types are not tightened to PR #39’s proposed field datatypes. Status/redaction constraints still apply. Each row counts its named key.', ''] + table([r for r in entries if r['role'] == 'item'])
    lines += ['', '## unix.file Require', '', 'Comparison context; existence-only uses its separate native alternative. Field-value counts and Item counts remain independent.', ''] + table([r for r in entries if r['role'] == 'require' and '.' not in r['field']])
    for parent in ['item_requirement', 'field_requirement']:
        lines += ['', '### ' + parent, ''] + table([r for r in entries if r['role'] == 'require' and r['field'].startswith(parent + '.')])
    lines += ['', 'Field predicates use the same field descriptions as collected Items; [all exact field routes](editor-metadata.json) point to one owner per field.', '', '## Approved core/shared examples', ''] + table([r for r in entries if r['capability'] == 'core'])
    lines += ['', 'This is a review slice. Nine proposed semantic descriptions and foreach authoring remain excluded. Offline lookup does not establish live YAML/Graphical help or scanner equivalence.', '']
    basic = '\n'.join(lines)
    advanced = ['# Review pack: advanced constraints', '', '<!-- Generated; same JSON Schemas as the basic reference and editor metadata. -->', '', '[Basic reference](reference.md) · [Pointer map](pointer-map.json).', '', '## Exact schema constraints and help origins', '']
    for r in entries:
        if r['role'] == 'require' and r['field'].startswith('fields.'):
            continue
        advanced += ['### ' + r['capability'] + ' / ' + r['role'] + ' / ' + r['field'], '',
                     '**Description:** `' + r['description_pointer'] + '`', '', r['description'], '',
                     '**Shape:** `' + r['schema_pointer'] + '`; [schema file](' + str(resource_file(urldefrag(r['schema_pointer'])[0]).relative_to(DEST)) + ').', '']
        if 'parent_schema_pointer' in r:
            advanced += ['**Parent constraints:** `' + r['parent_schema_pointer'] + '`', '']
        if r['role'] in {'item', 'require'} and r['field'].startswith('fields.'):
            advanced += ['Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.', '']
            continue
        details = []
        for n in parts(store.node(r['schema_pointer']), r['schema_pointer'], store):
            constraints = {k: n[k] for k in ['type', 'enum', 'const', 'default', 'minimum', 'maximum', 'minLength', 'maxLength', 'pattern', 'required', 'minItems', 'maxItems', 'dependentRequired'] if k in n}
            if constraints:
                details.append(constraints)
        advanced += ['```json', json.dumps(details, indent=2), '```', '']
    advanced += ['## Remaining boundaries', '', 'Unknown fields retain generic native validation and receive no invented capability help. Named Object resolution, instance/caret association, runtime errors, traversal/path binding, link/target metadata and mount classification remain separate dispatch/semantic gaps. Defaults are annotations, not inserted runtime values. [Review decisions](RECEIPT.md).', '']
    output = {str(resource_file(uri).relative_to(DEST)): encode(doc) for uri, doc in sorted(store.documents.items())}
    output.update({'reference.md': basic, 'constraints.md': '\n'.join(advanced), 'editor-metadata.json': encode(metadata), 'pointer-map.json': encode({k: v for k, v in provenance.items() if k not in {'validation_evidence', 'validation_cases'}}),
                   'validation-cases.json': encode(provenance['validation_cases']),
                   'validation-evidence.json': encode({'structural_only': True, 'cases': provenance['validation_evidence'], 'count': len(provenance['validation_evidence'])})})
    manifest = {'format': 'scap-ng-review-documentation-pack-1', 'review_only': True, 'release_version': None, 'namespace': PREFIX, 'source_commits': COMMITS,
                'resources': resources, 'generated_files': {name: digest(text.encode()) for name, text in output.items() if not name.startswith('schemas/')},
                'input_pins_sha256': digest(encode(pins).encode()), 'scope': {'capabilities': ['unix.file'], 'core_examples': 8, 'editor_help_routes': len(entries)},
                'structural_parity_proved': True, 'live_vscode_ui_verified': False}
    output['manifest.json'] = encode(manifest)
    output['pack-lock.json'] = encode({'format': 'scap-ng-review-pack-lock-1', 'review_only': True, 'source_commits': COMMITS, 'manifest_sha256': digest(output['manifest.json'].encode())})
    return output


def verify(root=ROOT):
    store, provenance, core, pins = build(root)
    expected = outputs(store, provenance, core, pins)
    actual = {str(p.relative_to(root / DEST)) for p in (root / DEST / 'schemas').rglob('*.json')}
    if actual != {p for p in expected if p.startswith('schemas/')}:
        raise ValueError('Missing or extra coordinated pack resource')
    for name, text in expected.items():
        if not (root / DEST / name).exists() or (root / DEST / name).read_bytes() != text.encode():
            raise ValueError('Stale/missing/hash-mismatched pack file: ' + name)
    return load_pack(root / DEST, digest(expected['manifest.json'].encode()))


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--materialize', action='store_true')
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--help-field', nargs=3, metavar=('CAPABILITY', 'ROLE', 'FIELD'))
    args = parser.parse_args(argv)
    try:
        if args.check or args.help_field:
            store, metadata = verify(root)
            if args.help_field:
                print(encode(resolve_help(store, *args.help_field, metadata)), end='')
            else:
                print(f'Checked single review pack: {len(store.documents)} resources; {len(metadata["entries"])} help routes; no live UI proof.')
        else:
            store, provenance, core, pins = build(root)
            expected = outputs(store, provenance, core, pins)
            if not args.materialize:
                for name, text in expected.items():
                    if name.startswith('schemas/') and (not (root / DEST / name).exists() or (root / DEST / name).read_bytes() != text.encode()):
                        raise ValueError('Schema fixture differs; use explicit --materialize after approved source review')
            for name, text in expected.items():
                path = root / DEST / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(text.encode())
            print(f'Generated single review pack: {len(store.documents)} resources; {len(provenance["annotations"])} source annotations.')
        return 0
    except (ValueError, KeyError) as exc:
        print('Review documentation pack: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
