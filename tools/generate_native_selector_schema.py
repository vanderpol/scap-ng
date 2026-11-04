from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'schema'
MAPPINGS = SCHEMA / 'capability-mappings' / 'supported'
INPUT = SCHEMA / 'native-selector-contracts.json'
OUTPUT = SCHEMA / 'native-selector.schema.json'
AUDIT_JSON = ROOT / 'docs' / 'metadata' / 'native-selector-audit.json'
AUDIT_MD = ROOT / 'docs' / 'ISSUE14-SELECTOR-AUDIT.md'


def load(path):
    return json.loads(path.read_text())


def selector_value(enum=None):
    refs = [
        {'$ref': 'capability-common.schema.json#/$defs/variable_reference'},
        {'$ref': 'capability-common.schema.json#/$defs/input_reference'},
    ]
    scalar = {'type': 'string'} if enum is None else {'type': 'string', 'enum': enum}
    item = {'type': 'string'} if enum is None else {'type': 'string', 'enum': enum}
    return {'oneOf': [scalar, {'type': 'array', 'minItems': 1, 'items': item}, *refs]}


def selector_predicate(contract, enum=None):
    operators = contract['operators']
    metadata = ['datatype', 'value_match', 'redact_result']
    props = {
        'datatype': {'type': 'string', 'const': 'string'},
        'value_match': {'$ref': 'assessment-language.schema.json#/$defs/cardinality'},
        'redact_result': {'const': True},
    }
    value = selector_value(enum)
    for op in operators:
        props[op] = value
    return {
        'allOf': [
            {'$ref': 'assessment-language.schema.json#/$defs/object_selector_predicate'},
            {'propertyNames': {'enum': [*metadata, *operators]}},
            {'properties': props},
        ],
        'description': contract.get('notes', 'Capability-specific native selector predicate.'),
    }


def object_schema(capability, selectors, mapping):
    defs = {}
    prefix = capability.replace('.', '_')
    for field, contract in selectors.items():
        mapped_field = mapping.get('native', {}).get('selector_map', {}).get(field, field)
        enum = (mapping.get('native', {}).get('selector_value_enums', {}).get(field)
                or mapping.get('native', {}).get('selector_value_enums', {}).get(mapped_field))
        defs[f'{prefix}_{field}_selector'] = selector_predicate(contract, enum)
    nullable = set(mapping.get('native', {}).get('nullable_selectors', [])) | {
        field for field, contract in selectors.items() if contract.get('nullable', False)
    }
    selector_props = {}
    for field in selectors:
        ref = {'$ref': f'#/$defs/{prefix}_{field}_selector'}
        selector_props[field] = {'oneOf': [ref, {'type': 'null'}]} if field in nullable else ref
    props = {
        'capability': {'type': 'string', 'minLength': 1},
        'filters': {'type': 'array', 'minItems': 1, 'items': {'$ref': 'capability-common.schema.json#/$defs/state_filter'}},
        **selector_props,
    }
    return defs, {
        'oneOf': [
            {'$ref': 'capability-common.schema.json#/$defs/object_reference'},
            {
                'type': 'object',
                'properties': props,
                'additionalProperties': False,
                'allOf': [
                    {'$ref': 'capability-common.schema.json#/$defs/inline_object'},
                ],
                'description': f'{capability} inline Object with reviewed native selector constraints.',
            },
        ],
        'title': f'{capability} Object',
    }


def build():
    source = load(INPUT)
    resolved = source['resolved']
    mappings = {p.stem: load(p) for p in sorted(MAPPINGS.glob('*.json'))}
    supported = set(mappings)
    unknown_capabilities = set(resolved) - supported
    if unknown_capabilities:
        raise SystemExit('resolved contracts reference unknown mappings: ' + repr(sorted(unknown_capabilities)))
    native_tokens = set(source['operator_vocabulary']['native_tokens'])
    defs = {}
    objects = {}
    inventory = []
    for capability, mapping in sorted(mappings.items()):
        native = mapping.get('native', {})
        selector_map = native.get('selector_map', {})
        selected = resolved.get(capability, {}).get('selectors', {})
        unknown = set(selected) - set(selector_map)
        if unknown:
            raise SystemExit(f'{capability}: resolved unknown selectors: {sorted(unknown)}')
        for field in sorted(selector_map):
            mapped_field = selector_map.get(field, field)
            mapping_types = native.get('field_datatypes', {}).get(mapped_field, [])
            enums = (native.get('selector_value_enums', {}).get(field)
                     or native.get('selector_value_enums', {}).get(mapped_field, []))
            if field in selected:
                contract = selected[field]
                if not contract['operators'] or not set(contract['operators']) <= native_tokens:
                    raise SystemExit(f'{capability}.{field}: invalid operator contract')
                if contract['value_types'] != mapping_types:
                    raise SystemExit(f'{capability}.{field}: value types do not match mapping: {contract["value_types"]!r} != {mapping_types!r}')
                if contract.get('enum_source') and not enums:
                    raise SystemExit(f'{capability}.{field}: enum source points to missing mapping enum')
                status, operators = 'resolved', contract['operators']
                notes = contract.get('notes', '')
            else:
                status, operators = 'unresolved', None
                notes = 'Native operator subset has not been reviewed; generic baseline is retained and no restriction is generated.'
            inventory.append({
                'capability': capability,
                'selector': field,
                'status': status,
                'allowed_operators': operators,
                'value_types': mapping_types,
                'enum': enums or None,
                'nullable': selected.get(field, {}).get('nullable', field in native.get('nullable_selectors', [])) if field in selected else field in native.get('nullable_selectors', []),
                'reason': notes,
            })
        if selected:
            local_defs, obj = object_schema(capability, selected, mapping)
            defs.update(local_defs)
            objects[f'{capability.replace(".", "_")}_object'] = obj
    generated_total = len(inventory)
    generated_resolved = sum(item['status'] == 'resolved' for item in inventory)
    generated_unresolved = sum(item['status'] == 'unresolved' for item in inventory)
    source_resolved = sum(len(contract.get('selectors', {}))
                          for contract in resolved.values())
    if (generated_total != generated_resolved + generated_unresolved
            or generated_resolved != source_resolved):
        raise SystemExit(
            'selector inventory reconciliation failed: '
            f'generated={generated_total}/{generated_resolved}/{generated_unresolved}, '
            f'source_resolved={source_resolved}')
    batch = source.get('batch')
    batch_actual = None
    if batch:
        batch_actual = sum(len(source['resolved'].get(cap, {}).get('selectors', {}))
                           for cap in batch.get('resolved_capabilities', []))
        if batch_actual != batch.get('selector_count'):
            raise SystemExit(
                'selector batch accounting mismatch: '
                f'declared={batch.get("selector_count")}, actual={batch_actual}')
    output = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$id': 'https://scap-ng.dev/schema/v0.4.0/native-selector.schema.json',
        'x-scap-ng-version': '0.4.0',
        'x-generated-from': 'native-selector-contracts.json',
        'title': 'SCAP-NG 0.4 capability-specific native Object selectors',
        'description': 'Generated capability-specific selector overlay. Resolved entries close the operator vocabulary and value constraints; unresolved mappings are intentionally not guessed.',
        '$defs': {
            'selector_value_reference': {
                'oneOf': [
                    {'$ref': 'capability-common.schema.json#/$defs/variable_reference'},
                    {'$ref': 'capability-common.schema.json#/$defs/input_reference'},
                ]
            },
            **defs,
            **objects,
        },
    }
    audit = {
        'format': 'scap-ng-native-selector-audit/0.1',
        'schema_version': '0.4.0',
        'source': 'schema/native-selector-contracts.json plus schema/capability-mappings/supported/*.json',
        'resolved_capabilities': sorted(resolved),
        'selector_count': len(inventory),
        'resolved_count': sum(i['status'] == 'resolved' for i in inventory),
        'unresolved_count': generated_unresolved,
        'inventory_reconciliation': {
            'reconciled': True,
            'generated_contract_inventory': {
                'selector_count': generated_total,
                'resolved_count': generated_resolved,
                'unresolved_count': generated_unresolved,
            },
            'source_resolved_count': source_resolved,
            'batch_declared_selector_count': batch.get('selector_count') if batch else None,
            'batch_actual_selector_count': batch_actual,
        },
        'pattern_match_boundary': source['operator_vocabulary']['pattern_match_boundary'],
        'selectors': inventory,
    }
    rows = []
    for item in inventory:
        ops = ', '.join(f'`{x}`' for x in item['allowed_operators']) if item['allowed_operators'] else '— (unresolved)'
        types = ', '.join(f'`{x}`' for x in item['value_types']) or 'not declared'
        enum = ', '.join(f'`{x}`' for x in item['enum']) if item['enum'] else '—'
        nullable = 'yes' if item['nullable'] else 'no'
        rows.append(f"| `{item['capability']}` | `{item['selector']}` | {item['status']} | {ops} | {types} | {enum} | {nullable} | {item['reason']} |")
    md = '''# Issue #14 native Object selector audit

This audit is generated from the supported capability mappings and the reviewed
native contract input in `schema/native-selector-contracts.json`. It is a
schema-contract inventory, not a scanner-implementation claim.

Resolved selectors are enforced by `schema/native-selector.schema.json` and by
capability-conditioned references in the canonical Assessment schema. An
unresolved selector deliberately retains the generic 0.4 baseline; no operator
restriction is inferred from OVAL prose or `selector_source_operations`.

Native 0.4 Object selectors serialize `matches_regex`. The legacy/source
migration spelling `pattern_match` remains a crosswalk value and is not a
native selector property. This boundary is intentional and tested.

| Capability | Selector | Status | Allowed native operators | Value types | Enum | Nullable | Notes |
|---|---|---|---|---|---|---|---|
''' + '\n'.join(rows) + '\n'
    return output, audit, md


def write_or_check(path, value, check):
    text = json.dumps(value, indent=2, ensure_ascii=False) + '\n' if isinstance(value, dict) else value
    if check:
        if not path.exists() or path.read_text() != text:
            raise SystemExit(f'generated file is stale: {path}')
    else:
        path.write_text(text)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    output, audit, md = build()
    write_or_check(OUTPUT, output, args.check)
    write_or_check(AUDIT_JSON, audit, args.check)
    write_or_check(AUDIT_MD, md, args.check)

if __name__ == '__main__':
    main()
