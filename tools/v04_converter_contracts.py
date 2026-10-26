#!/usr/bin/env python3
"""Regenerate current native contracts and audit converter mapping targets.

This exports deterministic schema data, not generated Python or a conversion IR.
It neither enables capabilities nor guesses missing source correspondences.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from generate_capability_schema_v04 import generate

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def obsolete_paths(value, path=()):
    """Recognize obsolete path tokens, not legitimate cmdlet object.select."""
    if isinstance(value, dict):
        for name, child in value.items():
            yield from obsolete_paths(child, path + (name,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from obsolete_paths(child, path + (index,))
    elif isinstance(value, str):
        if any(token.strip('`\"\'(:').startswith(('select.', 'collect.')) for token in value.split()):
            yield '.'.join(map(str, path)) + ': obsolete acquisition path ' + value


def contract(mapping, root=ROOT):
    """Approved mapping -> current schema data and explicit source routing gaps."""
    errors = list(obsolete_paths(mapping))
    if errors:
        raise ValueError('; '.join(errors))
    schema = generate(mapping, root)
    Draft202012Validator.check_schema(schema)
    definitions = schema['$defs']
    object_fields = definitions.get('object', {}).get('properties', {})
    test_fields = definitions['test']['properties']
    require_fields = {}
    for alternative in definitions.get('state_predicate', {}).get('oneOf', []):
        require_fields.update(alternative.get('properties', {}))
    native = mapping['native']
    for source, target in {**native.get('selector_map', {}),
                           **native.get('collection_parameter_source_map', {})}.items():
        if target not in object_fields:
            raise ValueError(f'{source}: unknown native Object field {target}')
    routes = {}
    crosswalk = mapping.get('migration_crosswalk', {})
    for section in ('object', 'behaviors'):
        for source, target in crosswalk.get(section, {}).items():
            if not isinstance(target, str) or not target.startswith(('object.', 'test.')):
                continue  # Explicit rejection/normalization markers are not field routes.
            scope, name = target.split('.', 1)
            fields = object_fields if scope == 'object' else test_fields
            if name not in fields:
                raise ValueError(f'{section}.{source}: unknown canonical target {target}')
            routes[f'{section}.{source}'] = target
    filesystem = crosswalk.get('traversal', {}).get('recurse_file_system.all')
    if filesystem is not None and filesystem != 'all':
        raise ValueError('filesystem scope must preserve the approved native all value')
    routed_parameters = set(native.get('collection_parameter_source_map', {}).values())
    routed_parameters.update(target.removeprefix('object.') for target in routes.values())
    # A same-named default is usable routing evidence, not permission to infer
    # arbitrary source-to-target names or new source semantics.
    routed_parameters.update(name.removeprefix('behaviors.') for name in
                             crosswalk.get('materialized_defaults', {}) if name.startswith('behaviors.'))
    return {
        'capability': mapping['capability'], 'schema_id': schema['$id'],
        'mapping_sha256': fingerprint(mapping), 'schema_sha256': fingerprint(schema),
        'source': mapping['source'], 'native_test_source': native.get('test_source'),
        'object_fields': object_fields, 'require_fields': require_fields,
        'canonical_source_routes': routes,
        'parameters_without_explicit_source_route': sorted(set(native.get('collection_parameters', {})) - routed_parameters),
        'schema': schema,
    }


def snapshot(root=ROOT):
    mappings = sorted((root / 'schema/v0.4.0/capability-mappings/supported').glob('*.json'))
    if not mappings:
        raise ValueError('no current capability mappings found')
    contracts, failures = [], []
    for path in mappings:
        try:
            contracts.append(contract(json.loads(path.read_text()), root))
        except (ValueError, KeyError, SchemaError) as error:
            failures.append({'capability': path.stem, 'error': str(error)})
    names = [item['capability'] for item in contracts]
    if len(names) != len(set(names)):
        raise ValueError('duplicate capability identity')
    schemas = {}
    for path in sorted((root / 'schema/v0.4.0').glob('*.json')):
        value = json.loads(path.read_text())
        if '$schema' in value:
            schemas[path.name] = value
    return {'schema_version': '0.4.0', 'schema_fingerprint': fingerprint(schemas),
            'normative_schemas': schemas, 'capabilities': contracts,
            'failures': failures,
            'summary': {'capabilities': len(mappings), 'generated': len(contracts), 'invalid_contracts': len(failures),
                        'source_route_review': {c['capability']: c['parameters_without_explicit_source_route']
                                                for c in contracts if c['parameters_without_explicit_source_route']}},
            'scope': 'Regenerated contract data; no capability admission, semantic proof, Python rewriting or release authority'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = snapshot(ROOT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['summary'], sort_keys=True))
    if result['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
