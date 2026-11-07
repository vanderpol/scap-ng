#!/usr/bin/env python3
"""Read-only field-help census. Nonempty text is evidence, not a usefulness verdict."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs/audits/pr30-description-coverage.json'


def walk(value, pointer=''):
    if isinstance(value, dict):
        yield pointer, value
        for key, child in value.items():
            yield from walk(child, pointer + '/' + key.replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, pointer + '/' + str(index))


def audit():
    schema = ROOT / 'schema'
    frozen = sorted(schema.rglob('*.json'))
    fingerprint = sha256()
    for path in frozen:
        fingerprint.update(path.relative_to(schema).as_posix().encode() + b'\0')
        fingerprint.update(path.read_bytes())
    if len(frozen) != 145 or fingerprint.hexdigest() != '63a61b3eb0ca95790721699f5e63b6f5a16b146660b9545a437519b508351db5':
        raise ValueError('Audit requires the pinned frozen baseline')
    documents = {p.name: json.loads(p.read_text(encoding='utf-8')) for p in schema.glob('*.json')}
    overlays = documents['native-selector.schema.json']['$defs']
    proposal = json.loads((ROOT / 'docs/metadata/schema-documentation-pilot.json').read_text())
    refs = documents['native-selector-contracts.json']['resolved']
    result_only = documents['result-field-extensions.json']['capabilities']
    vocabulary = documents['authoring-vocabulary.en.json']['capabilities']
    ntuser_notes = json.loads((ROOT / 'docs/metadata/windows.ntuser-source-notes.json').read_text())
    all_descriptions = defaultdict(list)
    for path in sorted(schema.rglob('*.json')):
        document = json.loads(path.read_text(encoding='utf-8'))
        for pointer, node in walk(document):
            # A capability field literally called description is not itself an
            # annotation (state_field_map.description is just the field name).
            if pointer.endswith(('/state_field_map', '/field_datatypes', '/item_value_types')):
                continue
            if isinstance(node.get('description'), str) and node['description'].strip():
                text = ' '.join(node['description'].split())
                all_descriptions[text].append(path.relative_to(ROOT).as_posix() + '#' + pointer + '/description')
            if pointer.endswith('/field_documentation'):
                for field, text in node.items():
                    if field != 'description' and isinstance(text, str) and text.strip():
                        all_descriptions[' '.join(text.split())].append(
                            path.relative_to(ROOT).as_posix() + '#' + pointer + '/' + field)
    records = []
    for path in sorted((schema / 'capability-mappings').rglob('*.json')):
        mapping = json.loads(path.read_text())
        native, name = mapping['native'], mapping['capability']
        mapping_path = path.relative_to(ROOT).as_posix()
        overlay = overlays.get(name.replace('.', '_') + '_object')
        inline = next((n for n in overlay['oneOf'] if 'properties' in n), {}) if overlay else {}
        annotations = proposal['capabilities'].get(name, {}).get('properties', {})
        capability_words = vocabulary.get(name, {})
        fields = []
        for role, values in [('selector', native.get('selector_map', {})),
                             ('collection_parameter', native.get('collection_parameters', {}))]:
            for field, value in sorted(values.items()):
                node = inline.get('properties', {}).get(field, {})
                description_refs = []
                if node.get('description'):
                    description_refs.append('schema/native-selector.schema.json#/$defs/' + name.replace('.', '_') + '_object')
                resolved = refs.get(name, {}).get('selectors', {}).get(field)
                if resolved:
                    description_refs.append('schema/native-selector.schema.json#/$defs/' + name.replace('.', '_') + '_' + field + '_selector/description')
                descriptions = []
                if role == 'collection_parameter' and value.get('description'):
                    descriptions.append(mapping_path + '#/native/collection_parameters/' + field + '/description')
                case = native.get('selector_case_semantics', {}).get(field, {})
                if isinstance(case, dict) and case.get('description'):
                    descriptions.append(mapping_path + '#/native/selector_case_semantics/' + field + '/description')
                if native.get('field_documentation', {}).get(field):
                    descriptions.append(mapping_path + '#/native/field_documentation/' + field)
                sidecar = ('docs/metadata/schema-documentation-pilot.json#/capabilities/' + name + '/properties/' + field + '/description'
                           if field in annotations else None)
                fields.append(dict(name=field, role=role, schema_description_refs=description_refs,
                                   mapping_description_refs=descriptions, proposed_author_description_ref=sidecar,
                                   vocabulary_selector_help=capability_words.get('selectors', {}).get(field),
                                   has_frozen_property_description=bool(node.get('description')),
                                   schema_help_class='selector_contract_notes' if resolved else 'no_field_specific_schema_help',
                                   schema_to_proposed_help_link=False))
        mapped_fields = set(native.get('state_field_map', {}).values())
        added = native.get('native_added_state_fields', {})
        added_fields = {value.get('native_name', key) for key, value in added.items()}
        item_fields = sorted(mapped_fields | added_fields)
        controls = sorted(set(inline.get('properties', {})) - set(native.get('selector_map', {})) -
                          set(native.get('collection_parameters', {})) - {'capability'})
        records.append(dict(capability=name, scope=path.parent.name,
                            object_fields=fields, closed_overlay_controls=controls,
                            item_fields=item_fields,
                            native_added_fields=sorted(added_fields - mapped_fields),
                            dynamic_record_fields=native.get('record_state_fields', []),
                            dynamic_record_child_descriptions='not_established' if native.get('record_state_fields') else 'not_applicable',
                            result_only_fields=sorted(result_only.get(name, {})),
                            legacy_item_note_refs={field: 'docs/metadata/windows.ntuser-source-notes.json#/fields/' + field
                                                   for field in ntuser_notes['fields']} if name == 'windows.ntuser' else {},
                            item_field_description_refs={field: mapping_path + '#/native/field_documentation/' + field
                                                         for field in item_fields if native.get('field_documentation', {}).get(field)},
                            item_field_semantic_descriptions=sum(bool(native.get('field_documentation', {}).get(field)) for field in item_fields),
                            require_fields_use_item_inventory=True,
                            require_field_semantic_descriptions=sum(bool(native.get('field_documentation', {}).get(field)) for field in item_fields),
                            require_vocabulary_description_refs={field: 'schema/authoring-vocabulary.en.json#/capabilities/' + name + '/state_fields/' + field + '/description'
                                                                 for field, words in capability_words.get('state_fields', {}).items() if words.get('description')},
                            require_generic_help='schema/assessment-language.schema.json#/$defs/canonical_all_items_requirement',
                            item_generic_help='schema/collected-item.schema.json#/properties/fields',
                            mapping_field_inventory_ref=mapping_path + '#/native/state_field_map',
                            generated_guide='docs/generated/developer-guide-' + name.split('.')[0] +
                            ('-pilot' if name.split('.')[0] in ('windows','unix','independent') else '') + '.md',
                            complete_useful_editor_help_confirmed=False))
    all_fields = [field for record in records for field in record['object_fields']]
    duplicates = [dict(text=text, occurrences=len(locations), locations=locations)
                  for text, locations in sorted(all_descriptions.items()) if len(locations) > 1]
    duplicates.sort(key=lambda row: (-row['occurrences'], row['text']))
    return dict(format='scap-ng/pr30-description-coverage/1',
                reviewed_pr_head='d7c6af21c323c972a095a97d381983899045933b',
                method='Field occurrences per capability, not unique spellings. Nonempty descriptions and selector contract notes are not certified useful author help. Generic predicate help is not field semantics.',
                summary=dict(capabilities=len(records),
                             supported=sum(r['scope']=='supported' for r in records),
                             experimental=sum(r['scope']=='experimental' for r in records),
                             selectors=sum(f['role']=='selector' for f in all_fields),
                             collection_parameters=sum(f['role']=='collection_parameter' for f in all_fields),
                             object_fields_with_direct_property_description=sum(f['has_frozen_property_description'] for f in all_fields),
                             selectors_with_resolved_contract_notes=sum(f['schema_help_class']=='selector_contract_notes' for f in all_fields),
                             object_fields_with_mapping_prose=sum(bool(f['mapping_description_refs']) for f in all_fields),
                             object_fields_with_proposed_author_help=sum(bool(f['proposed_author_description_ref']) for f in all_fields),
                             item_fields=sum(len(r['item_fields']) for r in records),
                             native_added_fields=sum(len(r['native_added_fields']) for r in records),
                             dynamic_record_wrappers=sum(len(r['dynamic_record_fields']) for r in records),
                             result_only_fields=sum(len(r['result_only_fields']) for r in records),
                             item_fields_with_metadata_description=sum(r['item_field_semantic_descriptions'] for r in records),
                             require_fields_with_reusable_metadata_description=sum(r['require_field_semantic_descriptions'] for r in records),
                             require_fields_with_vocabulary_description=sum(len(r['require_vocabulary_description_refs']) for r in records),
                             legacy_item_notes_not_native_help=sum(len(r['legacy_item_note_refs']) for r in records),
                             capabilities_with_complete_useful_editor_help_confirmed=0,
                             frozen_description_occurrences=sum(map(len, all_descriptions.values())),
                             duplicate_description_groups=len(duplicates)),
                capabilities=records, duplicated_frozen_descriptions=duplicates)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = audit()
    raw = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
    if args.check:
        if OUTPUT.read_bytes() != raw.encode():
            raise SystemExit('Description audit drifted')
    else:
        OUTPUT.write_text(raw, encoding='utf-8', newline='\n')
    print(json.dumps(data['summary'], sort_keys=True))


if __name__ == '__main__':
    main()
