# `unix.file`: advanced constraints

<!-- Generated; canonical schema is the source. -->

[Basic reference](reference.md). [Exact-pointer gaps](PARITY-CHECKLIST.md).

Object reference versus inline Object is a separate `oneOf` from selector pairing. See the [Object grammar](../../../schema/native-selector.schema.json#/$defs/unix_file_object).

| Field | Source / technical details |
| --- | --- |
| `filepath` | `required`: `[]` |
| `path` | `required`: `[]` |
| `filename` | [Selector grammar](../../../schema/native-selector.schema.json#/$defs/unix_file_filename_selector) |
| `filesystem` | `enum`: `["all", "local", "same"]`; `default`: `"local"` |
| `traversal` | `required`: `["max_depth", "recurse"]` |

### `traversal` children

| Child | Schema constraints / annotations |
| --- | --- |
| `max_depth` | `oneOf`: `[{"type": "integer", "minimum": 0}, {"const": "unlimited"}]`; `default`: `"unlimited"` |
| `recurse` | `minLength`: `1`; `enum`: `["directories", "symlinks", "symlinks_and_directories"]`; `default`: `"symlinks_and_directories"` |

## Maps, repeated values and status

- Item `fields`: 0..n total entries. Each named key is counted independently.
- A field value selects one typed wrapper or an array. Empty arrays remain allowed unless a schema `minItems` says otherwise; this does not imply a successful requirement.
- `typed_value.value` has conditional presence: status/redaction can forbid it; record datatype can require it. An optional map key says nothing about this inner payload.
- [Typed value/status rules](../../../schema/result-types.schema.json#/$defs/typed_value) and [complete requirement/condition grammar](../../../schema/assessment-language.schema.json#/$defs/canonical_all_items_requirement) retain their own hierarchy.

## Proposed datatype assertions

| Field | Datatype tag | Payload type | Values per key |
| --- | --- | --- | --- |
| `full_path` | `string` | string | 1..1 or 0..n |
| `directory` | `string` | string | 1..1 or 0..n |
| `name` | `string` | string | 1..1 or 0..n |
| `type` | `string` | string | 1..1 or 0..n |
| `owner_uid` | `integer` | integer | 1..1 or 0..n |
| `owner_gid` | `integer` | integer | 1..1 or 0..n |
| `size` | `integer` | integer | 1..1 or 0..n |
| `access_time` | `integer` | integer | 1..1 or 0..n |
| `change_time` | `integer` | integer | 1..1 or 0..n |
| `modify_time` | `integer` | integer | 1..1 or 0..n |
| `setuid` | `boolean` | boolean | 1..1 or 0..n |
| `setgid` | `boolean` | boolean | 1..1 or 0..n |
| `sticky` | `boolean` | boolean | 1..1 or 0..n |
| `owner_read` | `boolean` | boolean | 1..1 or 0..n |
| `owner_write` | `boolean` | boolean | 1..1 or 0..n |
| `owner_execute` | `boolean` | boolean | 1..1 or 0..n |
| `group_read` | `boolean` | boolean | 1..1 or 0..n |
| `group_write` | `boolean` | boolean | 1..1 or 0..n |
| `group_execute` | `boolean` | boolean | 1..1 or 0..n |
| `other_read` | `boolean` | boolean | 1..1 or 0..n |
| `other_write` | `boolean` | boolean | 1..1 or 0..n |
| `other_execute` | `boolean` | boolean | 1..1 or 0..n |
| `has_extended_acl` | `boolean` | boolean | 1..1 or 0..n |

These next-version assertions intentionally reject datatype/value inconsistencies accepted structurally by frozen 0.4.0. [Before/after vectors and integration limits](CANONICAL-INTEGRATION.md). No new bound or selector-pairing assertion is added by rendering.

## Defaults and unresolved behavior

Schema `default` is an annotation, not automatic value insertion. Existing new-authoring controls require explicit serialization and preservation of overrides. No runtime fallback is inferred. Missing descriptions/types/bounds or unsupported structures produce errors or `unspecified`/`conditional`, not historical defaults.
