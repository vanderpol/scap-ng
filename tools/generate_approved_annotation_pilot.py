#!/usr/bin/env python3
"""Bounded next-version annotation fixture and shared-renderer integration proof.

--materialize explicitly writes only the isolated proposal schema fixtures.
Normal generation reads their descriptions; --check writes nothing.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import shutil
from urllib.parse import urljoin, urldefrag

from jsonschema import Draft202012Validator
import yaml

import audit_schema_documentation as audit
from schema_documentation import SchemaStore, pointer, types, options, description_lookup

ROOT = Path(__file__).resolve().parents[1]
DEST = Path('docs/pilots/approved-annotations')
NEXT = 'https://scap-ng.dev/schema/proposals/issue40/'
ROUTES = NEXT + 'offline-help.schema.json'
SCHEMAS = DEST / 'schema-next'


def encode(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def remap(node, base, routes):
    """Change resource identity/routing only; preserve all validation assertions."""
    if isinstance(node, list):
        return [remap(v, base, routes) for v in node]
    if not isinstance(node, dict):
        return node
    result = {}
    for k, v in node.items():
        if k in {'$id', '$ref'}:
            uri, fragment = urldefrag(urljoin(base, v))
            result[k] = routes.get(uri, uri) + ('#' + fragment if '#' in v else '')
        else:
            result[k] = remap(v, base, routes)
    return result


def _historical_input_workspace(root, workspace, git_root=None):
    """Overlay the later historical receipts needed by the pilot.

    The native schema comes from the frozen Issue #40 commit, while the
    reviewed wording/selection files were recorded by later review commits.
    Resolve those exact blobs into the isolated archive instead of reading
    today's active 0.4.1 files as if they were 0.4.0 evidence.
    """
    git_root = Path(git_root or root)
    paths = [
        'docs/research/issue40/review-notes.json',
        'docs/research/issue40/editorial-batch.json',
        'docs/research/issue40/editorial-batch-2.json',
        'docs/research/issue40/schema-manifest.json',
        'docs/pilots/approved-annotations/selection.json',
        'docs/pilots/approved-annotations/source-map.json',
    ]
    desired_hashes = {}
    # Editorial witnesses are deliberately restricted to repository examples.
    for name in ('docs/research/issue40/editorial-batch.json',
                 'docs/research/issue40/editorial-batch-2.json'):
        data = json.loads((root / name).read_text())
        for row in data['proposals']:
            for check in row['checks']:
                if 'instance_file' in check:
                    path = check['instance_file']
                    paths.append(path)
                    desired_hashes[path] = check['instance_sha256']
    for path in dict.fromkeys(paths):
        source_raw = (root / path).read_bytes()
        expected_hash = desired_hashes.get(path, sha256(source_raw).hexdigest())
        raw = source_raw
        candidates = subprocess.check_output(
            ['git', '-C', str(git_root), 'log', '--all', '--format=%H', '--', path],
            text=True).split()
        for commit in candidates:
            try:
                raw = subprocess.check_output(
                    ['git', '-C', str(git_root), 'show', f'{commit}:{path}'],
                    stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                continue
            if sha256(raw).hexdigest() == expected_hash:
                break
        target = workspace / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)


def _proposal(root):
    result = audit.audit(root, active=False)
    selection = json.loads((root / DEST / 'selection.json').read_text())
    if selection['production_installation_authorized'] is not False or selection['authorization'] != 'https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721723400':
        raise ValueError('Proposal must not authorize production installation')
    entries = selection['entries']
    if not 6 <= len(entries) <= 10 or len({e['name'] for e in entries}) != len(entries):
        raise ValueError('Bounded integration requires 6–10 distinct entries')
    batches = {name: audit.editorial_batch(result, root, name)[0] for name in {e['batch'] for e in entries}}
    selected = []
    for entry in entries:
        row = next(r for r in batches[entry['batch']]['proposals'] if r['id'] == entry['case'])
        if row['editorial_status'] not in {'accepted_as_written', 'accepted_with_revision'} or row['classification'] != 'editorial' or row['withheld']:
            raise ValueError('Integration cannot install a semantic hold or unapproved description')
        selected.append((entry, row))
    owners = {(row['schema_uri'], row['pointer']) for _, row in selected}
    if len(owners) != len(entries) or len({uri for uri, _ in sorted(owners)}) < 3:
        raise ValueError('Descriptions require distinct owners across at least three schema families')
    routes = {uri: NEXT + Path(urldefrag(uri)[0]).name for uri in sorted({uri for uri, _ in owners})}
    proposed = {routes[uri]: remap(result['documents'][uri], uri, routes) for uri in sorted(routes)}
    help_schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', '$id': ROUTES, '$defs': {}}
    source_map = {'format': 'scap-ng-approved-description-integration-1', 'native_commit': audit.NATIVE_COMMIT,
                  'renderer_base_commit': audit.PILOT_COMMIT, 'authorization': selection['authorization'],
                  'production_installation_authorized': False, 'namespace_is_unpublished_proposal': True,
                  'native_file_hashes': {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest() for p in sorted((root / 'schema').rglob('*.json'))},
                  'resource_routes': routes, 'entries': []}
    manifest = json.loads((root / audit.DEST / 'schema-manifest.json').read_text())
    pinned = {r['file']: r['sha256'] for r in manifest['files']}
    if manifest['native_commit'] != audit.NATIVE_COMMIT or source_map['native_file_hashes'] != pinned:
        raise ValueError('Frozen schema family differs from pinned Phase 1 manifest')
    witnesses = []
    for entry, row in selected:
        uri = routes[row['schema_uri']]
        pointer(proposed[uri], row['pointer'])['description'] = row['author_description']
        lookup = uri + '#' + entry.get('lookup_pointer', row['pointer'])
        help_schema['$defs'][entry['name']] = {'$ref': lookup}
        source_map['entries'].append({'name': entry['name'], 'batch': entry['batch'], 'case': row['id'],
            'approval_url': row['editorial_review_url'], 'old_pointer': row['schema_uri'] + '#' + row['pointer'] + '/description',
            'old_description_present': row['existing_wording'] is not None, 'old_description': row['existing_wording'],
            'new_pointer': uri + '#' + row['pointer'] + '/description', 'lookup_pointer': lookup,
            'fixture_file': str(SCHEMAS / Path(uri).name), 'help_route': ROUTES + '#/$defs/' + entry['name']})
        witnesses.extend(row['checks'])
    normalized = deepcopy(proposed)
    for _, row in selected:
        node = pointer(normalized[routes[row['schema_uri']]], row['pointer'])
        if row['existing_wording'] is None:
            node.pop('description')
        else:
            node['description'] = row['existing_wording']
    inverse = {new: old for old, new in routes.items()}
    for old, new in routes.items():
        if remap(normalized[new], new, inverse) != remap(result['documents'][old], old, {}):
            raise ValueError('Proposal changed a non-selected annotation or validation assertion')
    proposed[ROUTES] = help_schema
    expected = {str(SCHEMAS / Path(uri).name): encode(doc) for uri, doc in proposed.items()}
    return result, source_map, proposed, expected, witnesses


def proposal(root=ROOT):
    # The pilot is historical evidence even when a unit test supplies an
    # isolated root. Rebuild the native 0.4.0 workspace from Git and overlay
    # only that test's reviewed receipt inputs; never reinterpret active 0.4.1
    # schema files as the old pilot contract.
    if root == ROOT or (root / 'docs/research/issue40').is_dir():
        source = root if root != ROOT else ROOT
        with audit.historical_workspace(ROOT) as workspace:
            if root != ROOT:
                for relative in ('docs/research/issue40', 'docs/pilots/approved-annotations'):
                    source_path = root / relative
                    target = workspace / relative
                    if source_path.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        if source_path.is_dir():
                            shutil.copytree(source_path, target, dirs_exist_ok=True)
                        else:
                            shutil.copy2(source_path, target)
            _historical_input_workspace(source, workspace, ROOT)
            return _proposal(workspace)
    return _proposal(root)


def _witness_bytes(root, path, expected_hash):
    raw = (root / path).read_bytes()
    if sha256(raw).hexdigest() == expected_hash:
        return raw
    commits = subprocess.check_output(
        ['git', '-C', str(ROOT), 'log', '--all', '--format=%H', '--', path],
        text=True).split()
    for commit in commits:
        try:
            raw = subprocess.check_output(
                ['git', '-C', str(ROOT), 'show', f'{commit}:{path}'],
                stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            continue
        if sha256(raw).hexdigest() == expected_hash:
            return raw
    raise ValueError('Unable to resolve pinned pilot witness: ' + path)


def load(root=ROOT):
    result, sources, proposed, expected, witnesses = proposal(root)
    actual_paths = {str(p.relative_to(root)) for p in (root / SCHEMAS).glob('*.schema.json')}
    if actual_paths != set(expected):
        raise ValueError('Missing or extra proposed schema fixture')
    for name, content in expected.items():
        if (root / name).read_bytes() != content.encode():
            raise ValueError('Missing/stale proposed description or schema: ' + name)
    documents = dict(result['documents'])
    documents.update({uri: json.loads((root / SCHEMAS / Path(uri).name).read_text()) for uri in proposed})
    store = SchemaStore(documents)
    for uri in proposed:
        Draft202012Validator.check_schema(store.documents[uri])
    # Resolve every $ref in the proposal strictly offline, including recursive
    # grammar edges. node() dereferences the target without recursively walking.
    def refs(node):
        if isinstance(node, dict):
            if '$ref' in node:
                yield node['$ref']
            for child in node.values():
                yield from refs(child)
        elif isinstance(node, list):
            for child in node:
                yield from refs(child)
    for uri in proposed:
        for ref in refs(store.documents[uri]):
            store.node(urljoin(uri, ref))
    for case in witnesses:
        if 'instance_file' in case:
            raw = _witness_bytes(root, case['instance_file'], case['instance_sha256'])
            instance = yaml.safe_load(raw)
        else:
            instance = case['instance']
        old = Draft202012Validator({'$ref': case['schema_uri']}, registry=result['store'].registry)
        base, fragment = urldefrag(case['schema_uri'])
        target = sources['resource_routes'].get(base, base) + '#' + fragment
        new = Draft202012Validator({'$ref': target}, registry=store.registry)
        if old.is_valid(instance) != case['expected_valid'] or new.is_valid(instance) != case['expected_valid']:
            raise ValueError('Before/after validation differs from pinned expectation')
    sources['structural_witness_count'] = len(witnesses)
    sources['proposed_resource_count'] = len(proposed)
    return store, sources


def render(store, sources):
    """All displayed author help is read from actual proposal schema nodes."""
    rows = ['# Approved description integration prototype', '',
            '<!-- Generated: python tools/generate_approved_annotation_pilot.py -->', '',
            '**Isolated next-version proposal; not the frozen 0.4.0 contract.**', '',
            '| Element | Type | Description | Vocabulary / annotations |', '| --- | --- | --- | --- |']
    help_rows = []
    for source in sources['entries']:
        found = description_lookup(store, source['help_route'])
        if found['description_pointer'] != source['new_pointer']:
            raise ValueError('Description resolved to a different canonical owner')
        node = store.node(source['lookup_pointer'])
        def cell(value):
            return str(value).replace('|', '&#124;').replace('\n', ' ')
        rows.append('| ' + ' | '.join(cell(v) for v in [source['name'], types(node, source['lookup_pointer'], store), found['description'], options(node, source['lookup_pointer'], store)]) + ' |')
        help_rows.append({'name': source['name'], **found})
    rows += ['', '## Description origins', '', '| Element | Authoritative proposal annotation |', '| --- | --- |']
    for source in sources['entries']:
        rows.append('| ' + source['name'] + ' | [' + Path(source['fixture_file']).name + '](schema-next/' + Path(source['fixture_file']).name + ') `' + source['new_pointer'] + '` |')
    rows += ['', '[Integration receipt and open routing decisions](RECEIPT.md).', '',
             'Types and vocabulary come from the same schema nodes using PR #39’s shared inspector. Advanced assertions remain in the linked proposal schemas. Offline help follows explicit schema-node routes and local `$ref` edges; it is not a live VS Code hover or an instance-to-caret association test.', '']
    return {'REFERENCE.md': '\n'.join(rows), 'offline-help.json': encode({'format': 'scap-ng-offline-description-lookup-1', 'live_vscode_ui_verified': False, 'entries': help_rows}),
            'source-map.json': encode(sources)}


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--materialize', action='store_true')
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--hover', metavar='NAME')
    args = parser.parse_args(argv)
    try:
        if args.materialize:
            _, _, _, expected, _ = proposal(root)
            for name, content in expected.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content.encode())
        store, sources = load(root)
        if args.hover:
            source = next((s for s in sources['entries'] if s['name'] == args.hover), None)
            if source is None:
                raise ValueError('Unknown offline help route: ' + args.hover)
            print(encode(description_lookup(store, source['help_route'])), end='')
            return 0
        for name, content in render(store, sources).items():
            path = root / DEST / name
            if args.check:
                if not path.exists() or path.read_bytes() != content.encode():
                    raise ValueError('Stale integration artifact: ' + name)
            else:
                path.write_bytes(content.encode())
        print(f'Checked {len(sources["entries"])} descriptions; {sources["structural_witness_count"]} before/after syntax witnesses; offline help only.')
        return 0
    except (ValueError, KeyError) as exc:
        print('Approved annotation pilot: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
