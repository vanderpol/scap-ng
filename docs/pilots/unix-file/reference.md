# `unix.file`

<!-- Generated: python tools/generate_unix_file_reference.py -->

**Proposed next-version schema reference; not the frozen 0.4.0 validation contract.**

Select filesystem entries and collect their metadata for comparison.

`n` means no schema upper bound. Occurrences count properties or named map keys; array values are counted separately.

## Object

Selection forms: `filepath` **or** `path` + `filename`. The schema does not enforce this pairing; see the [gap checklist](PARITY-CHECKLIST.md).

[Advanced constraints and shared grammar](constraints.md).

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| `filepath` | string selector | 0..1 | Full path of the selected entry. |
| `path` | string selector | 0..1 | Directory containing the selected entry. |
| `filename` | string selector or null | 0..1 | Entry name within the selected directory; null selects the directory itself. |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). `all`, `local`, `same`. Editor suggestion: `local`. |
| `traversal` | object | 0..1 | Controls recursive searching through directories and symbolic links. |

### `traversal`

Child occurrences apply **when `traversal` is present**. Suggestions are serialized for new authoring; no runtime fallback is established.

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| `max_depth` | integer or string | 1..1 | Maximum downward recursion depth; 0 includes only the starting directory. integer ≥ 0, `unlimited`. Editor suggestion: `unlimited`. |
| `recurse` | string | 1..1 | Entry types to follow during recursion. `directories`, `symlinks`, `symlinks_and_directories`. Editor suggestion: `symlinks_and_directories`. |

## Collected Item

`fields` is a dynamic map (0..n entries). Each row counts its named key, not all map entries.

Types below describe payloads inside typed values. A present key holds 1..1 or 0..n typed values (one wrapper or an array); payload omission depends on field status/redaction.

Units, file-kind labels and directory-only names remain unspecified; see the gap checklist.

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| `full_path` | string | 0..1 key | Full path of the collected entry. |
| `directory` | string | 0..1 key | Directory component of the collected path. |
| `name` | string | 0..1 key | Entry name without the directory. |
| `type` | string | 0..1 key | Kind of filesystem entry. |
| `owner_uid` | integer | 0..1 key | Numeric user ID of the owner. |
| `owner_gid` | integer | 0..1 key | Numeric group ID of the owning group. |
| `size` | integer | 0..1 key | File size. |
| `access_time` | integer | 0..1 key | Last data-access time. |
| `change_time` | integer | 0..1 key | Last inode-status change, not creation time. |
| `modify_time` | integer | 0..1 key | Last content-modification time. |
| `setuid` | boolean | 0..1 key | Set-user-ID permission flag. |
| `setgid` | boolean | 0..1 key | Set-group-ID permission flag. |
| `sticky` | boolean | 0..1 key | Sticky/restricted-deletion flag. |
| `owner_read` | boolean | 0..1 key | Whether the owner-read permission bit is set. |
| `owner_write` | boolean | 0..1 key | Whether the owner-write permission bit is set. |
| `owner_execute` | boolean | 0..1 key | Whether the owner-execute/search permission bit is set. |
| `group_read` | boolean | 0..1 key | Whether the group-read permission bit is set. |
| `group_write` | boolean | 0..1 key | Whether the group-write permission bit is set. |
| `group_execute` | boolean | 0..1 key | Whether the group-execute/search permission bit is set. |
| `other_read` | boolean | 0..1 key | Whether the other-read permission bit is set. |
| `other_write` | boolean | 0..1 key | Whether the other-write permission bit is set. |
| `other_execute` | boolean | 0..1 key | Whether the other-execute/search permission bit is set. |
| `has_extended_acl` | boolean | 0..1 key | Whether ACL permissions differ from standard UNIX permissions. |

## Require

Compare the collected fields using their declared datatypes and the shared Item/field cardinality rules.

For comparison Tests, in the selected requirement context; existence-only Tests use the [shared Item-presence requirement](../../../schema/assessment-language.schema.json#/$defs/item_presence_requirement).

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| `item_requirement` | object | 1..1 | Independent requirements for the number of selected Items and the number satisfying the comparison. |
| `field_requirement` | object | 1..1 | Explicit shared values_found/values_matching pair; a closer complete pair overrides it without runtime defaults. |
| `fields` | object | conditional | One complete condition; distinct field predicates are combined with logical AND. |

### Requirement children

Occurrences below apply when their parent is present in the comparison context.

#### `item_requirement`

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| `items_found` | string | 1..1 | Required cardinality of selected Items. |
| `items_satisfying` | string | 1..1 | Required cardinality of Items satisfying the comparison. |

#### `field_requirement`

| Field | Type | Occurrences | Description |
| --- | --- | --- | --- |
| `values_found` | string | 1..1 | Required count of observed values for a field. |
| `values_matching` | string | 1..1 | Required count of observed values satisfying its predicate. |

When `fields` is selected: 1..n entries; each named predicate key occurs 0..1. Item counts and field-value counts use the [shared cardinality grammar](../../../schema/assessment-language.schema.json#/$defs/paired_requirement).

## Important behavior

| Topic | Distinction |
| --- | --- |
| Directory / children | A null filename selects the directory itself; matching child names selects entries within it. |
| Traversal | Traversal is downward. Its binding to equality-selected path versus filepath is not yet specified consistently by the native contracts. |
| Directory permissions | Permission flags are bits, not an effective-access guarantee; directory-specific read/write/search interpretation remains unspecified. |
| Links / filesystem | Filesystem scope is independent of recursion. Link/target metadata, cycle handling and precise local/same mount classification remain unspecified. |
| Absence / errors | Nonexistent Items are omitted; collection absence/errors and field statuses remain separate, with detailed error propagation not yet specified. |

## Illustration

Illustrative Object → Item fields excerpt; not an executed scan:

```yaml
object:
  path: {equals: /example}
  filename: {equals: config}
  filesystem: all
  traversal: {max_depth: 1, recurse: directories}
# → Item fields excerpt:
fields:
  full_path: {datatype: string, status: exists, value: /example/config}
  owner_uid: {datatype: integer, status: exists, value: 1000}
```

## Sources

[Canonical proposal](schema-next/capabilities/unix.file.schema.json); [parity and gaps](PARITY-CHECKLIST.md); [source pins](source-map.json).

Based on the OVAL 5.12.3 UNIX file test/object/item documentation: [definitions](https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/unix-definitions-schema.html#file-object), [Item](https://oval-community-guidelines.readthedocs.io/en/base/oval-schema-documentation/unix-system-characteristics-schema.html#file-item).
