#!/usr/bin/env python3
"""Generate an isolated next-schema integration proposal, never the frozen pack.

This is a one-time migration demonstration. After approval, the canonical next
schemas would own descriptions/types directly; this migration is not a second
ongoing documentation metadata system.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

from generate_unix_file_reference import ROOT, PILOT, PREFIX, load_schemas

DEST = PILOT / 'schema-next'
NEXT = 'https://scap-ng.dev/schema/next/'
CAPABILITY = NEXT + 'capabilities/unix.file.schema.json'


def proposal():
    source, _, mapping, _, _ = load_schemas()
    fields = source['$defs']['field_meanings']['properties']
    defs = {'field_meanings': deepcopy(source['$defs']['field_meanings'])}
    # Import reviewed existing mapping once into real JSON Schema const/type
    # nodes. Reference generation never consults this migration metadata.
    for datatype in sorted({mapping['field_datatypes'][name][0] for name in fields}):
        if datatype not in {'integer', 'boolean', 'string'}:
            raise ValueError('Datatype requires an explicit integration review: ' + datatype)
        defs['datatype_' + datatype] = {'const': datatype}
    for name in fields:
        types = mapping['field_datatypes'][name]
        if len(types) != 1:
            raise ValueError('Ambiguous field datatype: ' + name)
        datatype = types[0]
        defs['value_' + name] = {
            '$ref': PREFIX + 'result-types.schema.json#/$defs/typed_value',
            'properties': {'datatype': {'$ref': '#/$defs/datatype_' + datatype},
                           'value': {'type': datatype}}}
    defs['item_fields'] = {'properties': {name: {
        '$ref': '#/$defs/field_meanings/properties/' + name,
        'oneOf': [{'$ref': '#/$defs/value_' + name},
                  {'type': 'array', 'items': {'$ref': '#/$defs/value_' + name}}]}
        for name in fields}}
    defs['object'] = deepcopy(source['$defs']['object'])
    defs['item'] = deepcopy(source['$defs']['item'])
    defs['item']['properties'] = {'capability': {'const': 'unix.file'},
                                  'fields': {'$ref': '#/$defs/item_fields'}}
    defs['require'] = deepcopy(source['$defs']['require'])
    # Preserve comparison-free Item-presence requirements as well as comparison.
    defs['require']['$ref'] = PREFIX + 'assessment-language.schema.json#/$defs/test/properties/require'
    defs['require']['properties']['fields'] = {
        'description': source['$defs']['require']['properties']['fields']['description'],
        'properties': {name: {
            '$ref': '#/$defs/field_meanings/properties/' + name,
            'properties': {'datatype': {'$ref': '#/$defs/datatype_' + mapping['field_datatypes'][name][0]}}}
            for name in fields}}
    defs['require_fields'] = defs['require']['properties']['fields']
    defs['require']['properties']['fields'] = {'$ref': '#/$defs/require_fields'}
    defs['condition'] = {
        '$ref': PREFIX + 'assessment-language.schema.json#/$defs/canonical_inherited_condition',
        'properties': {'fields': {'$ref': '#/$defs/require_fields'}}}
    for group in ['and', 'or', 'one', 'xor']:
        branch = {'items': {'$ref': '#/$defs/condition'}}
        defs['require']['properties'][group] = deepcopy(branch)
        defs['condition']['properties'][group] = deepcopy(branch)
    defs['test'] = {'$ref': PREFIX + 'assessment-language.schema.json#/$defs/test',
                    'properties': {'capability': {'const': 'unix.file'},
                                   'object': {'$ref': '#/$defs/object'},
                                   'require': {'$ref': '#/$defs/require'}}}
    common = {'$schema': 'https://json-schema.org/draft/2020-12/schema',
              '$comment': 'Review-only next-schema proposal. next is an unassigned version placeholder. Not installed; frozen 0.4 primitives are reused to isolate the proposed delta.'}
    capability = dict(common, **{'$id': CAPABILITY, '$defs': defs})
    def dispatch(target):
        return {'if': {'required': ['capability'], 'properties': {'capability': {'const': 'unix.file'}}},
                'then': {'$ref': CAPABILITY + '#/$defs/' + target}}
    assessment = dict(common, **{'$id': NEXT + 'assessment.schema.json',
        '$ref': PREFIX + 'assessment.schema.json',
        'properties': {'assessment': {'properties': {'tests': {'additionalProperties': dispatch('test')}}}}})
    item = dict(common, **{'$id': NEXT + 'collected-item.schema.json',
        '$ref': PREFIX + 'collected-item.schema.json', 'allOf': [dispatch('item')]})
    return {DEST / 'capabilities/unix.file.schema.json': capability,
            DEST / 'assessment.schema.json': assessment,
            DEST / 'collected-item.schema.json': item}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, document in proposal().items():
        raw = (json.dumps(document, indent=2) + '\n').encode()
        target = ROOT / path
        if args.check:
            if not target.exists() or target.read_bytes() != raw:
                print('Stale canonical integration proposal: ' + str(path), file=sys.stderr)
                return 1
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    if args.check:
        print('Canonical integration proposal exact-byte check passed (3 schemas)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
