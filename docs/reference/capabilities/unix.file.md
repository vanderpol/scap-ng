# unix.file

Proposed documentation; frozen 0.4.1 validation is unchanged.

The file test is used to check metadata associated with UNIX files, of the sort returned by either an ls command, stat command or stat() system call.

**Contract status: unresolved.** Link versus target metadata, filesystem boundaries, cycle handling, timestamp units and effective-access/ACL interpretation remain unresolved. Permission bits are not an effective-access guarantee. See issue #29 and the existing semantic research.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/unix.file.md) retain the validated encodings and any broader schema acceptance.

## Object

A file object defines the path and filename of the file(s).

In addition, a number of behaviors may be provided that help guide the collection of objects.

The Object is used by a file test to define the specific file(s) to be evaluated.

The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/set) |
| `filepath` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filepath) |
| `path` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/path) |
| `filename` | string | 0..1 | Name of a file to evaluate. | [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filename) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/object/properties/filesystem](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filesystem) |
| `traversal` | object | 0..1 | Controls recursive searching through directories and symbolic links. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/traversal) |

### traversal

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Entry types to follow during recursion. | [/$defs/file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal/allOf/1/properties/recurse) |

Validation shape: [/$defs/unix_file_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1).

## Item

The file item holds information about the individual files found on a system.

Each file item contains path and filename information as well as its type, associated user and group ids, relevant dates, and the privileges granted.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | string | 0..1 | Full path of the collected entry. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the collected path. | [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/directory) |
| `name` | string | 0..1 | Entry name without the directory. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/name) |
| `type` | string | 0..1 | Kind of filesystem entry. | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/type) |
| `owner_gid` | integer | 0..1 | Numeric group ID of the owning group. | [/$defs/meanings/properties/owner_gid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_gid) |
| `owner_uid` | integer | 0..1 | Numeric user ID of the owner. | [/$defs/meanings/properties/owner_uid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_uid) |
| `access_time` | integer | 0..1 | Last data-access time. | [/$defs/meanings/properties/access_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/access_time) |
| `change_time` | integer | 0..1 | Last inode-status change, not creation time. | [/$defs/meanings/properties/change_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/change_time) |
| `modify_time` | integer | 0..1 | Last content-modification time. | [/$defs/meanings/properties/modify_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/modify_time) |
| `size` | integer | 0..1 | File size. | [/$defs/meanings/properties/size](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/size) |
| `setuid` | boolean | 0..1 | Set-user-ID permission flag. | [/$defs/meanings/properties/setuid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setuid) |
| `setgid` | boolean | 0..1 | Set-group-ID permission flag. | [/$defs/meanings/properties/setgid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setgid) |
| `sticky` | boolean | 0..1 | Sticky/restricted-deletion flag. | [/$defs/meanings/properties/sticky](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/sticky) |
| `owner_read` | boolean | 0..1 | Whether the owner-read permission bit is set. | [/$defs/meanings/properties/owner_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_read) |
| `owner_write` | boolean | 0..1 | Whether the owner-write permission bit is set. | [/$defs/meanings/properties/owner_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_write) |
| `owner_execute` | boolean | 0..1 | Whether the owner-execute/search permission bit is set. | [/$defs/meanings/properties/owner_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_execute) |
| `group_read` | boolean | 0..1 | Whether the group-read permission bit is set. | [/$defs/meanings/properties/group_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_read) |
| `group_write` | boolean | 0..1 | Whether the group-write permission bit is set. | [/$defs/meanings/properties/group_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_write) |
| `group_execute` | boolean | 0..1 | Whether the group-execute/search permission bit is set. | [/$defs/meanings/properties/group_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_execute) |
| `other_read` | boolean | 0..1 | Whether the other-read permission bit is set. | [/$defs/meanings/properties/other_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_read) |
| `other_write` | boolean | 0..1 | Whether the other-write permission bit is set. | [/$defs/meanings/properties/other_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_write) |
| `other_execute` | boolean | 0..1 | Whether the other-execute/search permission bit is set. | [/$defs/meanings/properties/other_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_execute) |
| `has_extended_acl` | boolean | 0..1 | Whether ACL permissions differ from standard UNIX permissions. | [/$defs/meanings/properties/has_extended_acl](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/has_extended_acl) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different metadata associated with a UNIX file.

This includes the path, filename, type, group id, user id, size, etc.

In addition, the permission associated with the file are also included.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/unix.file.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.file.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

## Examples

**Illustrative expected outcomes; native evaluation unverified.** Syntax validation is reported separately from evaluation. For these compliance teaching cases only, technical `true` is labelled Pass and `false` Fail; a consuming Rule defines policy outcomes. Items are explicit synthetic evidence, not observations from a scanned host.

Both cases use this native Test (inline Object and Require):

```yaml
tests:
  unix-file-example-test:
    test_title: Compare the explicitly supplied owner_uid
    capability: unix.file
    object:
      filepath: {equals: /etc/passwd}
    require:
      item_requirement: {items_found: one_or_more, items_satisfying: every}
      field_requirement: {values_found: one_or_more, values_matching: every}
      fields:
        owner_uid: {datatype: integer, equals: 0}
    reported_elements: all
evaluate: {test: unix-file-example-test}
```

### Pass — expected `true` (unverified)

The supplied owner_uid is 0, so the explicit integer equality to 0 matches.

```yaml
collection_result:
  id: unix-file-pass-collection
  capability: unix.file
  status: complete
  item_refs: [unix-file-pass-item]
  logical_complete: true
  population_complete: true
collected_items:
- id: unix-file-pass-item
  capability: unix.file
  status: exists
  fields:
    full_path: {datatype: string, status: exists, value: /etc/passwd}
    owner_uid: {datatype: integer, status: exists, value: 0}
  provenance: {kind: synthetic-documentation-fixture}
```

[Complete version-pinned fixture](../../../examples/paired/v0.4.1/unix.file.pass.yaml).

### Fail — expected `false` (unverified)

The supplied owner_uid is 1000, so the explicit integer equality to 0 does not match.

```yaml
collection_result:
  id: unix-file-fail-collection
  capability: unix.file
  status: complete
  item_refs: [unix-file-fail-item]
  logical_complete: true
  population_complete: true
collected_items:
- id: unix-file-fail-item
  capability: unix.file
  status: exists
  fields:
    full_path: {datatype: string, status: exists, value: /etc/passwd}
    owner_uid: {datatype: integer, status: exists, value: 1000}
  provenance: {kind: synthetic-documentation-fixture}
```

[Complete version-pinned fixture](../../../examples/paired/v0.4.1/unix.file.fail.yaml).

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
