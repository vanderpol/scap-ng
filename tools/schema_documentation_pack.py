"""Offline loader for an exact, externally pinned review documentation pack.

No repository history, network, live editor integration or schema installation.
The future consumer must supply the immutable manifest digest it reviewed.
"""
from hashlib import sha256
import json
from pathlib import Path
from urllib.parse import urljoin

from jsonschema import Draft202012Validator
from schema_documentation import SchemaStore, description_lookup


def content_digest(raw):
    return sha256(raw).hexdigest()


def object_digest(value):
    return content_digest(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def resolve_help(store, capability, role, field, metadata):
    matches = [row for row in metadata['entries'] if (row['capability'], row['role'], row['field']) == (capability, role, field)]
    if len(matches) != 1:
        raise ValueError('Unknown or ambiguous capability/role/field dispatch')
    row = matches[0]
    found = description_lookup(store, row['schema_pointer'])
    if found['description_pointer'] != row['description_pointer'] or found['description'] != row['description']:
        raise ValueError('Stale or misrouted editor description')
    return found


def load_pack(directory, expected_manifest_sha256):
    directory = Path(directory).resolve()
    def read(name):
        path = (directory / name).resolve()
        if not path.is_relative_to(directory) or not path.is_file():
            raise ValueError('Missing/outside review pack file: ' + name)
        return path.read_bytes()
    if not expected_manifest_sha256:
        raise ValueError('An external immutable manifest pin is required')
    raw = read('manifest.json')
    if content_digest(raw) != expected_manifest_sha256:
        raise ValueError('Review manifest does not match external pin')
    manifest = json.loads(raw)
    lock = json.loads(read('pack-lock.json'))
    if (lock['manifest_sha256'] != expected_manifest_sha256 or lock['source_commits'] != manifest['source_commits']
            or lock['review_only'] is not True or manifest['review_only'] is not True or manifest['release_version'] is not None):
        raise ValueError('Review pack lock/identity mismatch')
    if content_digest(read('input-pins.json')) != manifest['input_pins_sha256']:
        raise ValueError('Source input pin manifest drifted')
    docs = {}
    expected_paths = set()
    for uri, record in manifest['resources'].items():
        if not uri.startswith(manifest['namespace']):
            raise ValueError('Competing namespace in review pack')
        resource_raw = read(record['file'])
        if content_digest(resource_raw) != record['sha256']:
            raise ValueError('Schema resource hash mismatch: ' + uri)
        doc = json.loads(resource_raw)
        if doc['$id'] != uri:
            raise ValueError('Schema identity mismatch: ' + uri)
        Draft202012Validator.check_schema(doc)
        docs[uri] = doc
        expected_paths.add(record['file'])
    actual_paths = {str(p.relative_to(directory)) for p in (directory / 'schemas').rglob('*.json')}
    if actual_paths != expected_paths:
        raise ValueError('Missing/extra schema resource in review pack')
    for name, expected in manifest['generated_files'].items():
        if content_digest(read(name)) != expected:
            raise ValueError('Generated pack file hash mismatch: ' + name)
    store = SchemaStore(docs)
    def refs(node):
        if isinstance(node, dict):
            if '$ref' in node:
                yield node['$ref']
            for value in node.values():
                yield from refs(value)
        elif isinstance(node, list):
            for value in node:
                yield from refs(value)
    for uri, doc in docs.items():
        for ref in refs(doc):
            store.node(urljoin(uri, ref))
    metadata = json.loads(read('editor-metadata.json'))
    if (metadata['resource_index_sha256'] != object_digest(manifest['resources'])
            or metadata['source_commits'] != manifest['source_commits'] or metadata['review_only'] is not True
            or metadata['release_version'] is not None or metadata['live_vscode_ui_verified'] is not False):
        raise ValueError('Editor metadata pack identity mismatch')
    for row in metadata['entries']:
        resolve_help(store, row['capability'], row['role'], row['field'], metadata)
    return store, metadata
