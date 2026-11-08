"""Offline, exact-context access to generated proposed documentation artifacts.

This is a transport helper, not an editor installation or a scanner runtime.
Consumers must supply an externally pinned manifest digest.
"""
from hashlib import sha256
import json
from pathlib import Path
import generate_documentation as generator


def load(root, expected_manifest_sha256):
    root = Path(root).resolve()
    path = root / generator.DEST / 'manifest.json'
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected_manifest_sha256:
        raise ValueError('Missing, stale or unpinned documentation manifest')
    manifest = json.loads(raw)
    for group in ('schemas', 'generated'):
        for name, expected in manifest[group].items():
            path = (root / name).resolve()
            if not path.is_relative_to(root):
                raise ValueError('Documentation path escapes pack')
            if sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('Stale documentation resource: ' + name)
    if sha256((root / generator.SOURCE / 'provenance.json').read_bytes()).hexdigest() != manifest['provenance_sha256']:
        raise ValueError('Stale documentation provenance')
    if sha256((root / generator.SOURCE / 'coverage-debt.json').read_bytes()).hexdigest() != manifest['coverage_debt_sha256']:
        raise ValueError('Stale documentation coverage baseline')
    docs = generator.schemas(root)
    generator.check_links(docs)
    help_data = json.loads((root / generator.DEST / 'editor-help.json').read_text())
    for row in help_data['routes'] + help_data['schema_routes']:
        text, owner = generator.resolve(docs, row['schema_pointer'])
        if row['description_pointer'] != (owner + '/description' if owner else None):
            raise ValueError('Incorrect description association')
        if 'description' in row and row['description'] != text:
            raise ValueError('Help differs from authoritative schema')
        if 'capability' in row and owner and '/capabilities/' in owner:
            if generator.node(docs, owner.split('#')[0]).get('x-doc-capability') != row['capability']:
                raise ValueError('Cross-capability help association')
    return help_data


def capability_help(data, capability, role, path):
    """No generic, parent, wrong-role or wrong-capability fallback."""
    row = next((r for r in data['routes'] if r['capability'] == capability
                and r['role'] == role and r['path'] == list(path)), None)
    return row if row and row['description_pointer'] else None


def schema_help(data, schema_pointer):
    route = next((r for r in data['schema_routes'] if r['schema_pointer'] == schema_pointer), None)
    if not route:
        return None
    owner = next(r for r in data['descriptions'] if r['description_pointer'] == route['description_pointer'])
    return dict(owner, status=route['status'])
