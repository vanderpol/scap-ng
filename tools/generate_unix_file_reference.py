#!/usr/bin/env python3
"""Single-capability proposal renderer. Reads local pinned schemas; no network."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from urllib.parse import urljoin

import yaml

ROOT = Path(__file__).resolve().parents[1]
PILOT = Path('docs/pilots/unix-file')
PREFIX = 'https://scap-ng.dev/schema/v0.4.0/'
ANNOTATIONS = PILOT / 'unix-file.annotations.schema.json'
OUTPUT = PILOT / 'reference.md'
ADVANCED = PILOT / 'constraints.md'


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


def load_schemas(root=ROOT):
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


def schema_node(root, uri):
    """Resolve a pinned native JSON Schema URI locally; never fetch references."""
    if not uri.startswith(PREFIX):
        raise ValueError('Outside pinned schema pack: ' + uri)
    file, _, fragment = uri[len(PREFIX):].partition('#')
    return pointer(json.loads((root / 'schema' / file).read_text()), fragment)


def structural(node, uri, root=ROOT):
    """Inspect schema keywords across $ref/allOf without a documentation model.

    oneOf/anyOf stay explicit. This is for rendering, never validation or schema
    rewriting. Conflicting keyword values fail instead of choosing a branch.
    """
    result = {}
    def combine(part):
        for key, value in part.items():
            if key in {'description', 'title', '$comment', 'x-scap-ng-authoring'}:
                result[key] = value
            elif key == 'properties':
                for name, child in value.items():
                    existing = result.setdefault('properties', {}).get(name)
                    result['properties'][name] = child if existing is None else structural(
                        {'allOf': [existing, child]}, uri, root)
            elif key == 'required':
                result[key] = list(dict.fromkeys(result.get(key, []) + value))
            elif key in result and result[key] != value:
                raise ValueError('Unrendered conflicting schema keyword: ' + key)
            else:
                result[key] = value
    if '$ref' in node:
        target = urljoin(uri, node['$ref'])
        combine(structural(schema_node(root, target), target, root))
    for part in node.get('allOf', []):
        combine(structural(part, uri, root))
    combine({key: value for key, value in node.items() if key not in {'$ref', 'allOf'}})
    return result


def constraints(node, uri, root=ROOT):
    """Render actual types, alternatives, bounds, enums and default annotations."""
    if '$ref' in node:
        target = urljoin(uri, node['$ref'])
        referenced = schema_node(root, target)
        if referenced.get('type') not in {'string', 'integer', 'boolean', 'null'}:
            file, _, fragment = target[len(PREFIX):].partition('#')
            label = fragment.rsplit('/', 1)[-1] or file
            return '[' + label + '](../../../schema/' + file + '#' + fragment + ')'
    node = structural(node, uri, root)
    parts = []
    for choice in ['oneOf', 'anyOf']:
        if choice in node:
            parts.append(choice + '(' + ' or '.join(constraints(n, uri, root) for n in node[choice]) + ')')
    if 'type' in node:
        types = node['type'] if isinstance(node['type'], list) else [node['type']]
        parts.append(' / '.join(types))
    if 'enum' in node:
        parts.append('values: ' + ', '.join(map(code, node['enum'])))
    if 'const' in node:
        parts.append('value: ' + code(node['const']))
    for keyword, label in [('minimum', 'minimum'), ('minLength', 'minimum length'), ('maxLength', 'maximum length'), ('pattern', 'pattern'), ('minItems', 'minimum entries')]:
        if keyword in node:
            parts.append(label + ': ' + str(node[keyword]))
    if 'items' in node:
        parts.append('entries: ' + constraints(node['items'], uri, root))
    if 'required' in node:
        parts.append('required children: ' + ', '.join(map(code, node['required'])))
    if 'default' in node:
        policy = node.get('x-scap-ng-authoring', {})
        authoring = all(policy.get(k) is True for k in ['new_authoring_only', 'serialize_explicitly', 'preserve_overrides'])
        parts.append(('authoring suggestion: ' if authoring else 'default annotation: ') + code(node['default']))
        if authoring:
            parts.append('serialize explicitly; no runtime fallback')
    return '; '.join(parts) or 'unconstrained value'


def render(root=ROOT):
    schema, sources, _mapping, _native, _common = load_schemas(root)
    defs = schema['$defs']
    meaning = lambda role, path='': hover(schema, role, path)['description']
    object_uri = defs['object']['$ref']
    object_schema = schema_node(root, object_uri)
    inline = next(n for n in object_schema['oneOf'] if n.get('type') == 'object')
    lines = ['# `unix.file`', '', '<!-- Generated by tools/generate_unix_file_reference.py; edit the proposed schema descriptions. -->', '',
             meaning('object'), '', '## Object', '',
             '[Advanced schema constraints](constraints.md).', '',
             '| Field | Meaning |', '| --- | --- |']
    traversal = structural(inline['properties']['traversal'], object_uri, root)
    for name in defs['object']['properties']:
        lines.append(f'| {code(name)} | {meaning("object", name)} |')
    lines += ['', '### `traversal`', '', 'When present, required children: ' + ', '.join(map(code, traversal.get('required', []))) + '.', '', '| Field | Meaning | Values |', '| --- | --- | --- |']
    for name in defs['object']['properties']['traversal']['properties']:
        lines.append(f'| {code(name)} | {meaning("object", "traversal." + name)} | {basic_values(traversal["properties"][name])} |')
    lines += ['', '## Collected Item', '',
              '| Field | Meaning |', '| --- | --- |']
    for name in defs['field_meanings']['properties']:
        lines.append(f'| {code(name)} | {meaning("item", "fields." + name)} |')
    lines += ['', '## Require', '', meaning('require') + ' [Shared requirement grammar](../../../schema/assessment-language.schema.json#/$defs/canonical_all_items_requirement).', '',
              '## Important behavior', '', '| Topic | Meaning / caveat |', '| --- | --- |',
              '| Metadata | ' + meaning('field_meanings') + ' |',
              '| Absence / errors | ' + meaning('item') + ' |', '',
              '## Illustration', '', 'Illustrative Object → collected Item fields excerpt; not an executed scan:', '',
              '```yaml', yaml.safe_dump({'object': defs['object']['examples'][0]}, sort_keys=False, default_flow_style=None, width=100).rstrip(),
              '# → Item fields excerpt:',
              yaml.safe_dump({'fields': defs['item']['examples'][0]['fields']}, sort_keys=False, default_flow_style=None, width=100).rstrip(), '```', '',
              '## Sources', '',
              '[Proposed schema descriptions](unix-file.annotations.schema.json); [pinned native sources and review records](source-map.json).', '',
              'Based on the OVAL 5.12.3 UNIX file test/object/item documentation: '
              '[definitions](https://github.com/OVAL-Community/OVAL/blob/' + sources['historical_source']['commit'] + '/oval-schemas/unix-definitions-schema.xsd#L167-L572), '
              '[collected Item](https://github.com/OVAL-Community/OVAL/blob/' + sources['historical_source']['commit'] + '/oval-schemas/unix-system-characteristics-schema.xsd#L59-L270).', '']
    return '\n'.join(lines)


def basic_values(node):
    """Short essential vocabulary, without defaults or shared grammar details."""
    if 'oneOf' in node:
        return ' or '.join(basic_values(n) for n in node['oneOf'])
    if 'enum' in node:
        return ', '.join(map(code, node['enum']))
    if 'const' in node:
        return code(node['const'])
    return node.get('type', '') + (' ≥ ' + str(node['minimum']) if 'minimum' in node else '')


def render_constraints(root=ROOT):
    schema, *_ = load_schemas(root)
    uri = schema['$defs']['object']['$ref']
    obj = schema_node(root, uri)
    inline = next(n for n in obj['oneOf'] if n.get('type') == 'object')
    traversal = structural(inline['properties']['traversal'], uri, root)
    lines = ['# `unix.file`: advanced schema constraints', '',
             '<!-- Generated from pinned JSON Schema; field meanings remain in the basic reference. -->', '',
             '[Basic reference](reference.md).', '', '## Object', '',
             'Schema choice (`oneOf`): ' + ' **or** '.join(
                 'inline object' if n.get('type') == 'object' else code(n['$ref'].rsplit('/', 1)[-1]) + ': ' + constraints(n, uri, root)
                 for n in obj['oneOf']) + '.', '',
             '| Field | Constraints / suggestions |', '| --- | --- |']
    for name in schema['$defs']['object']['properties']:
        node = traversal if name == 'traversal' else inline['properties'][name]
        lines.append('| ' + code(name) + ' | ' + constraints(node, uri, root).replace('|', '&#124;') + ' |')
    lines += ['', '### `traversal`', '', '| Child | Constraints / suggestions |', '| --- | --- |']
    for name in schema['$defs']['object']['properties']['traversal']['properties']:
        required = 'Required; ' if name in traversal.get('required', []) else 'Optional; '
        lines.append('| ' + code(name) + ' | ' + required + constraints(traversal['properties'][name], uri, root) + ' |')
    item_uri = schema['$defs']['item']['$ref']
    field = schema_node(root, item_uri)['properties']['fields']['additionalProperties']
    lines += ['', '## Collected Item', '', '### `fields`', '',
              'Each field value: ' + constraints(field, item_uri, root) + '.', '',
              '[Canonical requirement grammar](../../../schema/assessment-language.schema.json#/$defs/canonical_all_items_requirement).', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--hover', metavar='ROLE.PROPERTY.PATH')
    args = parser.parse_args()
    try:
        if args.hover:
            schema, *_ = load_schemas()
            role, _, path = args.hover.partition('.')
            print(json.dumps(hover(schema, role, path), indent=2))
            return 0
        for path, content in [(OUTPUT, render()), (ADVANCED, render_constraints())]:
            target = ROOT / path
            content = content.encode('utf-8')
            if args.check:
                if not target.exists() or target.read_bytes() != content:
                    print('unix.file pilot reference is stale: ' + str(path), file=sys.stderr)
                    return 1
            else:
                target.write_bytes(content)
        if args.check:
            print('unix.file pilot exact-byte check passed (basic and advanced)')
        return 0
    except (ValueError, KeyError, IndexError) as exc:
        print('unix.file pilot: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
