#!/usr/bin/env python3
"""Single-capability proposal renderer. Reads local pinned schemas; no network."""
import argparse

from hashlib import sha256
import json
from pathlib import Path
import sys

import yaml

from schema_documentation import (pointer, code, absolute, parts, bounds, affects,
    property_occurrences, collection_occurrences, types, display_type, options, schema_node, registry)

ROOT = Path(__file__).resolve().parents[1]
PILOT = Path('docs/pilots/unix-file')
PREFIX = 'https://scap-ng.dev/schema/v0.4.1/'
ANNOTATIONS = PILOT / 'schema-next/capabilities/unix.file.schema.json'
NEXT = 'https://scap-ng.dev/schema/next/'
OUTPUT = PILOT / 'reference.md'
ADVANCED = PILOT / 'constraints.md'
PARITY = PILOT / 'PARITY-CHECKLIST.md'


def description_paths(node, path=''):
    if isinstance(node, dict):
        if 'description' in node:
            yield path
        for key, value in node.items():
            yield from description_paths(value, path + '/' + key)


def description(schema, path):
    value = pointer(schema, path).get('description')
    if not isinstance(value, str) or not value.strip() :
        raise ValueError('Missing description: ' + path)
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
    while 'description' not in node and node.get('$ref', '').startswith('#/'):
        location = node['$ref'][1:]
        node = pointer(schema, location)
    return {'description': description(schema, location), 'schema': str(ANNOTATIONS), 'pointer': location}


def load_schemas(root=ROOT):
    schema = json.loads((root / ANNOTATIONS).read_text())
    sources = json.loads((root / PILOT / 'source-map.json').read_text())
    actual = {str(p.relative_to(root)): sha256(p.read_bytes()).hexdigest()
              for p in sorted((root / 'schema').rglob('*.json'))}
    # Archive source hashes are retained for the original research receipt,
    # but cannot validate the ONE active 0.4.1 authoring schema.
    if sources.get('current_schema_version') != '0.4.1':
        raise ValueError('Pilot has not been explicitly qualified against active SCAP-NG 0.4.1')
    if actual != sources.get('current_schema_sha256'):
        raise ValueError('Active 0.4.1 schema differs from the reviewed pilot input')
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


def child(node, uri, name, root=ROOT, context=None):
    schemas = [p['properties'][name] for p in parts(node, uri, root, context) if name in p.get('properties', {})]
    if not schemas:
        raise ValueError('Unspecified property schema: ' + name)
    return {'allOf': schemas}


def item_shape(node, uri, root=ROOT):
    payloads, values = [], []
    for p in parts(node, uri, root):
        for branch in p.get('oneOf', []):
            if types(branch, uri, root) == 'array':
                values.append(collection_occurrences(branch, uri, 'array', root))
                value = next(n['items'] for n in parts(branch, uri, root) if 'items' in n)
            else:
                values.append('1..1')
                value = branch
            payloads.append(types(child(value, uri, 'value', root), uri, root))
    if not payloads:
        raise ValueError('Unsupported Item single/array schema; explicit review required')
    return ' or '.join(dict.fromkeys(payloads)), ' or '.join(dict.fromkeys(values))


def table_row(*values):
    return '| ' + ' | '.join(str(v).strip().replace('|', '&#124;').replace('\n', ' ') for v in values) + ' |'


def inputs(root):
    schema, sources, *_ = load_schemas(root)
    uri, defs = schema['$id'], schema['$defs']
    native_uri = defs['object']['$ref']
    native = schema_node(root, native_uri)
    inline = next(n for n in native['oneOf'] if n.get('type') == 'object')
    obj = {'allOf': [absolute(inline, native_uri), absolute({k: v for k, v in defs['object'].items() if k != '$ref'}, uri)]}
    field_map = child(defs['item'], uri, 'fields', root)
    return schema, sources, uri, defs, obj, field_map


def render(root=ROOT):
    schema, sources, uri, defs, obj, field_map = inputs(root)
    meaning = lambda role, path='': hover(schema, role, path)['description'].split('\n\n')[0]
    lines = ['# `unix.file`', '', '<!-- Generated: python tools/generate_unix_file_reference.py -->', '',
             '**Review-only proposed overlay; not an accepted replacement for active SCAP-NG 0.4.1.**', '',
             meaning('object'), '', '`n` means no schema upper bound. Occurrences count properties or named map keys; array values are counted separately.', '',
             '## Object', '', 'Selection forms: `filepath` **or** `path` + `filename`. The schema does not enforce this pairing; see the [gap checklist](PARITY-CHECKLIST.md).', '',
             '[Advanced constraints and shared grammar](constraints.md).', '',
             '| Field | Type | Occurrences | Description |', '| --- | --- | --- | --- |']
    for name in defs['object']['properties']:
        node = child(obj, uri, name, root)
        lines.append(table_row(code(name), display_type(node, uri, root), property_occurrences(obj, uri, name, root), meaning('object', name) + ' ' + options(node, uri, root)))
    traversal = child(obj, uri, 'traversal', root)
    lines += ['', '### `traversal`', '', 'Child occurrences apply **when `traversal` is present**. Suggestions are serialized for new authoring; no runtime fallback is established.', '',
              '| Field | Type | Occurrences | Description |', '| --- | --- | --- | --- |']
    for name in defs['object']['properties']['traversal']['properties']:
        node = child(traversal, uri, name, root)
        lines.append(table_row(code(name), display_type(node, uri, root), property_occurrences(traversal, uri, name, root), meaning('object', 'traversal.' + name) + ' ' + options(node, uri, root)))
    field_nodes = {name: child(field_map, uri, name, root) for name in defs['field_meanings']['properties']}
    shapes = {name: item_shape(node, uri, root) for name, node in field_nodes.items()}
    common_values = set(shape[1] for shape in shapes.values())
    lines += ['', '## Collected Item', '',
              '`fields` is a dynamic map (' + collection_occurrences(field_map, uri, 'map', root) + ' entries). Each row counts its named key, not all map entries.', '',
              'Types below describe payloads inside typed values. A present key holds ' + (next(iter(common_values)) if len(common_values) == 1 else 'the per-row bound') + ' typed values (one wrapper or an array); payload omission depends on field status/redaction.', '',
              'Units, file-kind labels and directory-only names remain unspecified; see the gap checklist.', '',
              '| Field | Type | Occurrences | Description |', '| --- | --- | --- | --- |']
    for name, (kind, values) in shapes.items():
        occurrence = property_occurrences(field_map, uri, name, root) + ' key'
        if len(common_values) != 1:
            occurrence += '; ' + values + ' values'
        payload = child(defs['value_' + name], uri, 'value', root)
        vocabulary = options(payload, uri, root)
        if len(vocabulary) > 100:
            vocabulary = '[Payload constraints](constraints.md).'
        lines.append(table_row(code(name), kind, occurrence, meaning('item', 'fields.' + name) + ' ' + vocabulary))
    context = {'item_requirement': {'items_found': 'one_or_more', 'items_satisfying': 'every'}, 'field_requirement': {'values_found': 'one_or_more', 'values_matching': 'every'}, 'fields': {'owner_uid': {'equals': 1000}}}
    lines += ['', '## Require', '', meaning('require'), '',
              'For comparison Tests, in the selected requirement context; existence-only Tests use the [shared Item-presence requirement](../../../schema/assessment-language.schema.json#/$defs/item_presence_requirement).', '',
              '| Field | Type | Occurrences | Description |', '| --- | --- | --- | --- |']
    comparison = {'allOf': [{'$ref': PREFIX + 'assessment-language.schema.json#/$defs/canonical_all_items_requirement'}, {'properties': defs['require']['properties']}]}
    for name in ['item_requirement', 'field_requirement', 'fields']:
        node = child(defs['require'], uri, name, root, context)
        lines.append(table_row(code(name), types(node, uri, root), property_occurrences(comparison, uri, name, root), meaning('require', name)))
    lines += ['', '### Requirement children', '', 'Occurrences below apply when their parent is present in the comparison context.']
    for parent, names in [('item_requirement', ['items_found', 'items_satisfying']), ('field_requirement', ['values_found', 'values_matching'])]:
        lines += ['', '#### ' + code(parent), '', '| Field | Type | Occurrences | Description |', '| --- | --- | --- | --- |']
        scope = child(defs['require'], uri, parent, root, context)
        for name in names:
            node = child(scope, uri, name, root)
            lines.append(table_row(code(name), types(node, uri, root), property_occurrences(scope, uri, name, root), meaning('require', parent + '.' + name)))
    require_map = child(defs['require'], uri, 'fields', root, context)
    lines += ['', 'When `fields` is selected: ' + collection_occurrences(require_map, uri, 'map', root) + ' entries; each named predicate key occurs ' + property_occurrences(require_map, uri, 'owner_uid', root) + '. Item counts and field-value counts use the [shared cardinality grammar](../../../schema/assessment-language.schema.json#/$defs/paired_requirement).', '',
              '## Important behavior', '', '| Topic | Distinction |', '| --- | --- |']
    for label, text in [
        ('Directory / children', defs['object']['properties']['filename']['description'].split('\n\n')[1]),
        ('Traversal', defs['object']['properties']['traversal']['description'].split('\n\n')[1]),
        ('Directory permissions', defs['value_owner_read']['description']),
        ('Links / filesystem', defs['object']['properties']['filesystem']['description'].split('\n\n')[1]),
        ('Absence / errors', defs['item']['description'])]:
        lines.append(table_row(label, text))
    lines += ['', '## Illustration', '', 'Illustrative Object → Item fields excerpt; not an executed scan:', '',
              '```yaml', yaml.safe_dump({'object': defs['object']['examples'][0]}, sort_keys=False, default_flow_style=None, width=100).rstrip(),
              '# → Item fields excerpt:', yaml.safe_dump({'fields': defs['item']['examples'][0]['fields']}, sort_keys=False, default_flow_style=None, width=100).rstrip(), '```', '',
              '## Sources', '', '[Canonical proposal](schema-next/capabilities/unix.file.schema.json); [parity and gaps](PARITY-CHECKLIST.md); [source pins](source-map.json).', '',
              'Based on the OVAL 5.12.3 UNIX file test/object/item documentation: [definitions](' + sources['readthedocs']['definitions']['url'] + '#file-object), [Item](' + sources['readthedocs']['items']['url'] + '#file-item).', '']
    return '\n'.join(lines)


def render_constraints(root=ROOT):
    schema, _, uri, defs, obj, field_map = inputs(root)
    lines = ['# `unix.file`: advanced constraints', '', '<!-- Generated; canonical schema is the source. -->', '', '[Basic reference](reference.md). [Exact-pointer gaps](PARITY-CHECKLIST.md).', '',
             'Object reference versus inline Object is a separate `oneOf` from selector pairing. See the [Object grammar](../../../schema/native-selector.schema.json#/$defs/unix_file_object).', '',
             '| Field | Source / technical details |', '| --- | --- |']
    for name in defs['object']['properties']:
        node = child(obj, uri, name, root)
        details = []
        for p in parts(node, uri, root):
            for key in ['enum', 'default', 'minimum', 'minLength', 'maxLength', 'pattern', 'required']:
                if key in p:
                    details.append(code(key) + ': ' + code(json.dumps(p[key])))
        lines.append(table_row(code(name), '; '.join(dict.fromkeys(details)) or '[Selector grammar](../../../schema/native-selector.schema.json#/$defs/unix_file_' + name + '_selector)'))
    traversal = child(obj, uri, 'traversal', root)
    lines += ['', '### `traversal` children', '', '| Child | Schema constraints / annotations |', '| --- | --- |']
    for name in defs['object']['properties']['traversal']['properties']:
        details = []
        for p in parts(child(traversal, uri, name, root), uri, root):
            for key in ['oneOf', 'enum', 'default', 'minimum', 'minLength', 'maxLength', 'pattern']:
                if key in p:
                    details.append(code(key) + ': ' + code(json.dumps(p[key])))
        lines.append(table_row(code(name), '; '.join(dict.fromkeys(details))))
    lines += ['', '## Maps, repeated values and status', '',
              '- Item `fields`: ' + collection_occurrences(field_map, uri, 'map', root) + ' total entries. Each named key is counted independently.',
              '- A field value selects one typed wrapper or an array. Empty arrays remain allowed unless a schema `minItems` says otherwise; this does not imply a successful requirement.',
              '- `typed_value.value` has conditional presence: status/redaction can forbid it; record datatype can require it. An optional map key says nothing about this inner payload.',
              '- [Typed value/status rules](../../../schema/result-types.schema.json#/$defs/typed_value) and [complete requirement/condition grammar](../../../schema/assessment-language.schema.json#/$defs/canonical_all_items_requirement) retain their own hierarchy.', '',
              '## Proposed datatype assertions', '', '| Field | Datatype tag | Payload type | Values per key |', '| --- | --- | --- | --- |']
    for name in defs['field_meanings']['properties']:
        value = defs['value_' + name]
        tag = next(p['const'] for p in parts(value['properties']['datatype'], uri, root) if 'const' in p)
        kind, count = item_shape(child(field_map, uri, name, root), uri, root)
        lines.append(table_row(code(name), code(tag), kind, count))
    vocabulary = []
    for name in defs['field_meanings']['properties']:
        payload = child(defs['value_' + name], uri, 'value', root)
        for p in parts(payload, uri, root):
            facts = {k: p[k] for k in ['enum', 'default', 'minimum', 'maximum', 'pattern', 'minLength', 'maxLength'] if k in p}
            if facts:
                vocabulary.append(table_row(code(name), code(json.dumps(facts))))
    if vocabulary:
        lines += ['', '## Payload constraints', '', '| Field | Schema keywords |', '| --- | --- |'] + vocabulary
    lines += ['', 'These next-version assertions intentionally reject datatype/value inconsistencies accepted structurally by active 0.4.1. [Before/after vectors and integration limits](CANONICAL-INTEGRATION.md). No new bound or selector-pairing assertion is added by rendering.', '',
              '## Defaults and unresolved behavior', '',
              'Schema `default` is an annotation, not automatic value insertion. Existing new-authoring controls require explicit serialization and preservation of overrides. No runtime fallback is inferred. Missing descriptions/types/bounds or unsupported structures produce errors or `unspecified`/`conditional`, not historical defaults.', '']
    return '\n'.join(lines)


def render_parity(root=ROOT):
    schema, sources, *_ = load_schemas(root)
    lines = ['# `unix.file`: parity and exact-pointer gaps', '', '<!-- Generated checklist; historical rows are coverage evidence, never native assertions. -->', '',
             'Compared row-by-row with both fetched 5.12.3 Read the Docs pages and pinned XSDs. Status denotes coverage in the proposal, not acceptance of new runtime semantics. URLs are mutable; [source hashes](source-map.json) identify reviewed bytes. Regeneration is offline.', '',
             '| Coverage | Status | Native location / gap |', '| --- | --- | --- |']
    for name in schema['$defs']['object']['properties']:
        lines.append(table_row('Object `' + name + '`', 'present', '/$defs/object/properties/' + name + '; traversal children retain their parent'))
    for historical, native, status in [('max_depth', '/$defs/object/properties/traversal/properties/max_depth', 'present'), ('recurse', '/$defs/object/properties/traversal/properties/recurse', 'present'), ('recurse_direction', '/$defs/object/properties/traversal', 'native-undecided'), ('recurse_file_system', '/$defs/object/properties/filesystem', 'present')]:
        lines.append(table_row('Behavior `' + historical + '`', status, native + ('; downward construct exists, selector eligibility unresolved' if historical == 'recurse_direction' else '; source defaults/deprecated values not imported')))
    lines.append(table_row('Object behaviors/filter inheritance', 'intentionally shared/link-only', 'behaviors split into traversal/filesystem; filters and Set shapes stay in native-selector.schema.json#/$defs/unix_file_object'))
    reverse = {record['source_field']: path.rsplit('/', 1)[-1] for path, record in sources['descriptions'].items() if 'source_field' in record}
    unresolved = {'name': 'directory-only representation unspecified', 'type': 'file-kind labels/enum unspecified', 'size': 'unit unspecified', 'access_time': 'time unit/resolution unspecified', 'change_time': 'time unit/resolution unspecified', 'modify_time': 'time unit/resolution unspecified', 'has_extended_acl': 'unsupported-ACL/status mapping unspecified'}
    kind_payload = child(schema['$defs']['value_type'], schema['$id'], 'value', root)
    if any('enum' in p for p in parts(kind_payload, schema['$id'], root)):
        unresolved.pop('type', None)
    for row in sources['readthedocs']['items']['rows']:
        name = reverse[row['field']]
        status = 'native-undecided' if name in unresolved else 'present'
        gap = unresolved.get(name, 'meaning/type/key/value bounds present')
        lines.append(table_row('Item `' + row['field'] + '` → `' + name + '`', status, gap + ' (`/$defs/value_' + name + '/properties/value`)'))
    for label, status, location in [
        ('Selector pairing', 'native-undecided', '/$defs/object → native-selector.schema.json#/$defs/unix_file_object/oneOf/1: no pairing assertion; examples show selection forms only'),
        ('Traversal eligibility', 'native-undecided', '/$defs/object/properties/traversal; mapping rules use collected names full_path/directory, so authored-selector binding remains unresolved'),
        ('Directory permissions', 'native-undecided', '/$defs/value_owner_read/description: bit flags do not establish directory effective-access/search semantics'),
        ('Links / filesystem classification', 'native-undecided', '/$defs/object/properties/filesystem: link/target, cycles and local/same classification unresolved'),
        ('Units', 'native-undecided', '/$defs/value_size/properties/value; /$defs/value_access_time/properties/value; /$defs/value_change_time/properties/value; /$defs/value_modify_time/properties/value lack units'),
        ('Absence / partial errors', 'native-undecided', '/$defs/item/description: no synthetic missing Item; detailed propagation remains unspecified'),
        ('Inherited Object/Item/Test/predicates', 'intentionally shared/link-only', '/$defs/object, /$defs/item, /$defs/test and /$defs/require reference canonical shared definitions'),
        ('Require named fields and groups', 'present', '/$defs/require_fields and /$defs/condition: generic map plus known optional keys; not a new whitelist'),
        ('Defaults', 'present', 'shared file_traversal_base/max_depth, file_traversal/recurse and filesystem_scope: explicit new-authoring suggestions, not runtime fallbacks')]:
        lines.append(table_row(label, status, location))
    lines += ['', '## Historical differences (not native requirements)', '', '| Topic | Reviewed difference |', '| --- | --- |']
    for topic, record in sources['historical_differences'].items():
        lines.append(table_row(topic, record['source'] + ' ' + record['native']))
    lines += ['', 'RTD selector occurrences are branch-local; singular optional Item entities do not establish native map/value counts. The datatype tightening is separate and covered by [compatibility vectors](CANONICAL-INTEGRATION.md).', '']
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
        outputs = [(OUTPUT, render()), (ADVANCED, render_constraints()), (PARITY, render_parity())]
        for path, content in outputs:
            target = ROOT / path
            raw = content.encode('utf-8')
            if args.check:
                if not target.exists() or target.read_bytes() != raw:
                    print('Stale unix.file documentation: ' + str(path), file=sys.stderr)
                    return 1
            else:
                target.write_bytes(raw)
        print('unix.file documentation ' + ('check passed' if args.check else 'regenerated') + ' (basic, advanced, parity)')
        return 0
    except (ValueError, KeyError, IndexError) as exc:
        print('unix.file pilot: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
