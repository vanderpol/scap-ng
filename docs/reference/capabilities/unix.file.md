# unix.file

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Link versus target metadata, filesystem boundaries, cycle handling, timestamp units and effective-access/ACL interpretation remain unresolved. Permission bits are not an effective-access guarantee. See issue #29 and the existing semantic research.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/set) |
| `filepath` | object | 0..1 | Absolute path for a file on the machine. | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filepath) |
| `path` | object | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/path) |
| `filename` | null, object | 0..1 | Name of a file to evaluate. | [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filename) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/object/properties/filesystem](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filesystem) |
| `traversal` | object | 0..1 | Controls recursive searching through directories and symbolic links. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/traversal) |

### traversal

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Entry types to follow during recursion. | [/$defs/file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal/allOf/1/properties/recurse) |

Validation shape: [/$defs/unix_file_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | array, object | 0..1 | Full path of the collected entry. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/full_path) |
| `directory` | array, object | 0..1 | Directory component of the collected path. | [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/directory) |
| `name` | array, object | 0..1 | Entry name without the directory. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/name) |
| `type` | array, object | 0..1 | Kind of filesystem entry. | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/type) |
| `owner_gid` | array, object | 0..1 | Numeric group ID of the owning group. | [/$defs/meanings/properties/owner_gid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_gid) |
| `owner_uid` | array, object | 0..1 | Numeric user ID of the owner. | [/$defs/meanings/properties/owner_uid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_uid) |
| `access_time` | array, object | 0..1 | Last data-access time. | [/$defs/meanings/properties/access_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/access_time) |
| `change_time` | array, object | 0..1 | Last inode-status change, not creation time. | [/$defs/meanings/properties/change_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/change_time) |
| `modify_time` | array, object | 0..1 | Last content-modification time. | [/$defs/meanings/properties/modify_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/modify_time) |
| `size` | array, object | 0..1 | File size. | [/$defs/meanings/properties/size](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/size) |
| `setuid` | array, object | 0..1 | Set-user-ID permission flag. | [/$defs/meanings/properties/setuid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setuid) |
| `setgid` | array, object | 0..1 | Set-group-ID permission flag. | [/$defs/meanings/properties/setgid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setgid) |
| `sticky` | array, object | 0..1 | Sticky/restricted-deletion flag. | [/$defs/meanings/properties/sticky](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/sticky) |
| `owner_read` | array, object | 0..1 | Whether the owner-read permission bit is set. | [/$defs/meanings/properties/owner_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_read) |
| `owner_write` | array, object | 0..1 | Whether the owner-write permission bit is set. | [/$defs/meanings/properties/owner_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_write) |
| `owner_execute` | array, object | 0..1 | Whether the owner-execute/search permission bit is set. | [/$defs/meanings/properties/owner_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_execute) |
| `group_read` | array, object | 0..1 | Whether the group-read permission bit is set. | [/$defs/meanings/properties/group_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_read) |
| `group_write` | array, object | 0..1 | Whether the group-write permission bit is set. | [/$defs/meanings/properties/group_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_write) |
| `group_execute` | array, object | 0..1 | Whether the group-execute/search permission bit is set. | [/$defs/meanings/properties/group_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_execute) |
| `other_read` | array, object | 0..1 | Whether the other-read permission bit is set. | [/$defs/meanings/properties/other_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_read) |
| `other_write` | array, object | 0..1 | Whether the other-write permission bit is set. | [/$defs/meanings/properties/other_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_write) |
| `other_execute` | array, object | 0..1 | Whether the other-execute/search permission bit is set. | [/$defs/meanings/properties/other_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_execute) |
| `has_extended_acl` | array, object | 0..1 | Whether ACL permissions differ from standard UNIX permissions. | [/$defs/meanings/properties/has_extended_acl](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/has_extended_acl) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

### Condition logic

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |

### Item existence requirement

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Existence only; there is no satisfaction operation without a comparison. | [/$defs/item_presence_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/item_presence_requirement/properties/item_requirement) |


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/unix.file.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`filepath` | string | source-derived |
| Object.`path` | string | source-derived |
| Object.`filename` | string | source-derived |
| Item.`full_path` | string | editorially-approved |
| Item.`directory` | string | editorially-approved |
| Item.`name` | string | editorially-approved |
| Item.`type` | string | editorially-approved |
| Item.`owner_gid` | integer | editorially-approved |
| Item.`owner_uid` | integer | editorially-approved |
| Item.`access_time` | integer | editorially-approved |
| Item.`change_time` | integer | editorially-approved |
| Item.`modify_time` | integer | editorially-approved |
| Item.`size` | integer | editorially-approved |
| Item.`setuid` | boolean | editorially-approved |
| Item.`setgid` | boolean | editorially-approved |
| Item.`sticky` | boolean | editorially-approved |
| Item.`owner_read` | boolean | editorially-approved |
| Item.`owner_write` | boolean | editorially-approved |
| Item.`owner_execute` | boolean | editorially-approved |
| Item.`group_read` | boolean | editorially-approved |
| Item.`group_write` | boolean | editorially-approved |
| Item.`group_execute` | boolean | editorially-approved |
| Item.`other_read` | boolean | editorially-approved |
| Item.`other_write` | boolean | editorially-approved |
| Item.`other_execute` | boolean | editorially-approved |
| Item.`has_extended_acl` | boolean | editorially-approved |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.file.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
