# `unix.file`: advanced schema constraints

<!-- Generated from pinned JSON Schema; field meanings remain in the basic reference. -->

[Basic reference](reference.md).

## Object

Schema choice (`oneOf`): `object_reference`: string; minimum length: 1; maximum length: 64; pattern: ^[a-z0-9]+(?:-[a-z0-9]+)*-object$ **or** inline object.

| Field | Constraints / suggestions |
| --- | --- |
| `filepath` | [unix_file_filepath_selector](../../../schema/native-selector.schema.json#/$defs/unix_file_filepath_selector) |
| `path` | [unix_file_path_selector](../../../schema/native-selector.schema.json#/$defs/unix_file_path_selector) |
| `filename` | oneOf([unix_file_filename_selector](../../../schema/native-selector.schema.json#/$defs/unix_file_filename_selector) or null) |
| `filesystem` | string; values: `all`, `local`, `same`; authoring suggestion: `local`; serialize explicitly; no runtime fallback |
| `traversal` | object; required children: `max_depth`, `recurse` |

### `traversal`

| Child | Constraints / suggestions |
| --- | --- |
| `max_depth` | Required; oneOf(integer; minimum: 0 or value: `unlimited`); authoring suggestion: `unlimited`; serialize explicitly; no runtime fallback |
| `recurse` | Required; string; values: `directories`, `symlinks`, `symlinks_and_directories`; minimum length: 1; authoring suggestion: `symlinks_and_directories`; serialize explicitly; no runtime fallback |

## Collected Item

### `fields`

Each field value: oneOf([typed_value](../../../schema/result-types.schema.json#/$defs/typed_value) or array; entries: [typed_value](../../../schema/result-types.schema.json#/$defs/typed_value)).

[Canonical requirement grammar](../../../schema/assessment-language.schema.json#/$defs/canonical_all_items_requirement).
