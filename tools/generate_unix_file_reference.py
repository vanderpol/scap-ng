#!/usr/bin/env python3
"""Single-capability proposal renderer. Reads local pinned schemas; no network."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PILOT = Path('docs/pilots/unix-file')
PREFIX = 'https://scap-ng.dev/schema/v0.4.0/'
ANNOTATIONS = PILOT / 'unix-file.annotations.schema.json'
OUTPUT = PILOT / 'reference.md'


def pointer(document, path):
    for token in path.lstrip('/').split('/') if path else []:
        token = token.replace('~1', '/').replace('~0', '~')
        document = document[int(token)] if isinstance(document, list) else document[token]
    return document


def description_paths(node, path=''):
    if isinstance(node, dict):
        if 'description' in node:
            yield path
        for key, value in node.items():
            yield from description_paths(value, path + '/' + key)


def description(schema, path):
    value = pointer(schema, path).get('description')
    if not isinstance(value, str) or not value.strip() or '\n' in value:
        raise ValueError('Missing or multiline description: ' + path)
    return value


def hover(schema, role, path):
    """Offline proposed-pack property lookup; returns exact description origin.

    Only resolves local annotation references. Does not emulate VS Code's UI,
    evaluate predicates, or register this proposal in an editor's production pack.
    """
    location = '/$defs/' + role
    node = pointer(schema, location)
    for name in path.split('.') if path else []:
        if name not in node.get('properties', {}) and node.get('$ref', '').startswith('#/'):
            location = node['$ref'][1:]
            node = pointer(schema, location)
        if name not in node.get('properties', {}):
            raise ValueError('No proposed description mapping: ' + role + '.' + path)
        location += '/properties/' + name
        node = node['properties'][name]
    return {'description': description(schema, location), 'schema': str(ANNOTATIONS), 'pointer': location}


def load_model(root=ROOT):
    schema = json.loads((root / ANNOTATIONS).read_text())
    sources = json.loads((root / PILOT / 'source-map.json').read_text())
    actual = {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
              for p in sorted((root / 'schema').rglob('*.json'))}
    if actual != sources['frozen_schema_sha256']:
        raise ValueError('Frozen schema pack differs from the pinned pilot input')
    mapping = json.loads((root / 'schema/capability-mappings/supported/unix.file.json').read_text())['native']
    native = json.loads((root / 'schema/native-selector.schema.json').read_text())['$defs']['unix_file_object']['oneOf'][1]
    common = json.loads((root / 'schema/capability-common.schema.json').read_text())['$defs']
    fields = schema['$defs']['field_meanings']['properties']
    if set(fields) != set(mapping['state_field_map'].values()):
        raise ValueError('Missing or unknown Item field mapping')
    if not set(fields) <= set(mapping['field_datatypes']):
        raise ValueError('Missing Item datatype mapping')
    objects = schema['$defs']['object']['properties']
    if set(objects) != set(mapping['selector_map'].values()) | {'filesystem', 'traversal'}:
        raise ValueError('Missing or unknown Object selector/control mapping')
    for name in objects:
        if name not in native['properties']:
            raise ValueError('Missing Object schema node: ' + name)
    if native['properties']['traversal']['$ref'] != 'capability-common.schema.json#/$defs/file_traversal':
        raise ValueError('Traversal schema binding changed')
    if set(objects['traversal']['properties']) != set(common['file_traversal_base']['properties']):
        raise ValueError('Missing or unknown traversal child mapping')
    paths = set(description_paths(schema))
    if paths != set(sources['descriptions']):
        raise ValueError('Missing or unknown description provenance mapping')
    for path in paths:
        description(schema, path)
        native_file, _, fragment = sources['descriptions'][path]['native_pointer'].partition('#')
        pointer(json.loads((root / 'schema' / native_file).read_text()), fragment)
    return schema, sources, mapping, native, common


def code(value):
    return '`' + str(value) + '`'


def suggestions(node):
    policy = node['x-scap-ng-authoring']
    if not all(policy.get(k) is True for k in ['new_authoring_only', 'serialize_explicitly', 'preserve_overrides']):
        raise ValueError('Unsupported default policy')
    return 'Authoring suggestion: ' + code(node['default']) + '; serialize explicitly, no runtime fallback.'


def render(root=ROOT):
    schema, sources, mapping, native, common = load_model(root)
    defs = schema['$defs']
    meaning = lambda role, path='': hover(schema, role, path)['description']
    alternatives = mapping['object_selector_alternatives']
    if alternatives != [['filepath'], ['path', 'filename']]:
        raise ValueError('Unsupported selector alternatives; review renderer')
    lines = ['# `unix.file`', '', '<!-- Generated by tools/generate_unix_file_reference.py; edit the proposed schema descriptions. -->', '',
             meaning('object'), '', '## Object', '',
             'Selection form: ' + ' **or** '.join(' + '.join(map(code, alt)) for alt in alternatives) + '.', '',
             '| Field | Meaning | Constraints / suggestions |', '| --- | --- | --- |']
    for name in defs['object']['properties']:
        note = ''
        if name == 'filesystem':
            note = ', '.join(map(code, common['filesystem_scope']['enum'])) + '. ' + suggestions(common['filesystem_scope'])
        elif name == 'traversal':
            note = 'Optional object; both children below are required when present.'
        lines.append(f'| {code(name)} | {meaning("object", name)} | {note} |')
    base = common['file_traversal_base']
    depth = base['properties']['max_depth']
    recurse = common['file_traversal']['allOf'][1]['properties']['recurse']
    if base['required'] != ['max_depth', 'recurse'] or depth['oneOf'] != [{'type': 'integer', 'minimum': 0}, {'const': 'unlimited'}]:
        raise ValueError('Unsupported traversal constraints; review renderer')
    lines += ['', '### `traversal`', '', '| Field | Meaning | Allowed values / constraints |', '| --- | --- | --- |']
    values = {'max_depth': f'integer ≥ {depth["oneOf"][0]["minimum"]} or {code(depth["oneOf"][1]["const"])}',
              'recurse': ', '.join(map(code, recurse['enum']))}
    for name, node in [('max_depth', depth), ('recurse', recurse)]:
        lines.append(f'| {code(name)} | {meaning("object", "traversal." + name)} | Required: {values[name]}. {suggestions(node)} |')
    lines += ['', '## Collected Item', '', '| Field | Meaning | Datatype |', '| --- | --- | --- |']
    for name in defs['field_meanings']['properties']:
        lines.append(f'| {code(name)} | {meaning("item", "fields." + name)} | {", ".join(mapping["field_datatypes"][name])} |')
    lines += ['', '## Require', '', meaning('require') + ' [Shared requirement grammar](../../../schema/assessment-language.schema.json#/$defs/canonical_all_items_requirement).', '',
              '## Important behavior', '', '| Topic | Meaning / caveat |', '| --- | --- |',
              '| Metadata | ' + meaning('field_meanings') + ' |',
              '| Absence / errors | ' + meaning('item') + ' |', '',
              '## Illustration', '', 'Illustrative Object → collected Item fields excerpt; not an executed scan:', '',
              '```yaml', 'object:', '  path: {equals: /example}', '  filename: {equals: config}', '  filesystem: all',
              '  traversal:', '    max_depth: 1', '    recurse: directories', '# → Item fields excerpt:', 'fields:',
              '  full_path: {datatype: string, status: exists, value: /example/config}',
              '  owner_uid: {datatype: integer, status: exists, value: 1000}', '```', '',
              '## Sources', '',
              '[Proposed schema descriptions](unix-file.annotations.schema.json); [pinned native sources and review records](source-map.json).', '',
              'Based on the OVAL 5.12.3 UNIX file test/object/item documentation: '
              '[definitions](https://github.com/OVAL-Community/OVAL/blob/' + sources['historical_source']['commit'] + '/oval-schemas/unix-definitions-schema.xsd#L167-L572), '
              '[collected Item](https://github.com/OVAL-Community/OVAL/blob/' + sources['historical_source']['commit'] + '/oval-schemas/unix-system-characteristics-schema.xsd#L59-L270).', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--hover', metavar='ROLE.PROPERTY.PATH')
    args = parser.parse_args()
    try:
        if args.hover:
            schema, *_ = load_model()
            role, _, path = args.hover.partition('.')
            print(json.dumps(hover(schema, role, path), indent=2))
            return 0
        content = render().encode('utf-8')
        target = ROOT / OUTPUT
        if args.check:
            if not target.exists() or target.read_bytes() != content:
                print('unix.file pilot reference is stale', file=sys.stderr)
                return 1
            print('unix.file pilot exact-byte check passed')
        else:
            target.write_bytes(content)
        return 0
    except (ValueError, KeyError, IndexError) as exc:
        print('unix.file pilot: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
