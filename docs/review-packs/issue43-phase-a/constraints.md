# Review pack: advanced constraints

<!-- Generated; same JSON Schemas as the basic reference and editor metadata. -->

[Basic reference](reference.md) · [Pointer map](pointer-map.json).

## Exact schema constraints and help origins

### unix.file / object / filepath

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filepath/description`

Full path of the selected entry.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filepath`; [schema file](schemas/native-selector.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1`

```json
[
  {
    "type": "object",
    "required": []
  }
]
```

### unix.file / object / path

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/path/description`

Directory containing the selected entry.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/path`; [schema file](schemas/native-selector.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1`

```json
[
  {
    "type": "object",
    "required": []
  }
]
```

### unix.file / object / filename

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filename/description`

Entry name within the selected directory; null selects the directory itself.

A null filename selects the directory itself; matching child names selects entries within it.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filename`; [schema file](schemas/native-selector.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1`

```json
[]
```

### unix.file / object / filesystem

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/filesystem_scope/description`

Filesystem scope: all, local, or the starting filesystem (same).

Filesystem scope is independent of recursion. Link/target metadata, cycle handling and precise local/same mount classification remain unspecified.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filesystem`; [schema file](schemas/native-selector.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1`

```json
[
  {
    "type": "string",
    "enum": [
      "all",
      "local",
      "same"
    ],
    "default": "local"
  }
]
```

### unix.file / object / traversal

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/file_traversal/description`

Controls recursive searching through directories and symbolic links.

Traversal is downward. Its binding to equality-selected path versus filepath is not yet specified consistently by the native contracts.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/traversal`; [schema file](schemas/native-selector.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/native-selector.schema.json#/$defs/unix_file_object/oneOf/1`

```json
[
  {
    "type": "object",
    "required": [
      "max_depth",
      "recurse"
    ]
  },
  {
    "type": "object"
  }
]
```

### unix.file / object / traversal.max_depth

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth/description`

Maximum downward recursion depth; 0 includes only the starting directory.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth`; [schema file](schemas/capability-common.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/file_traversal`

```json
[
  {
    "default": "unlimited"
  }
]
```

### unix.file / object / traversal.recurse

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/file_traversal/allOf/1/properties/recurse/description`

Entry types to follow during recursion.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/file_traversal/allOf/1/properties/recurse`; [schema file](schemas/capability-common.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/file_traversal`

```json
[
  {
    "type": "string",
    "enum": [
      "directories",
      "symlinks",
      "symlinks_and_directories"
    ],
    "default": "symlinks_and_directories"
  }
]
```

### unix.file / item / fields.full_path

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/full_path/description`

Full path of the collected entry.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/full_path`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.directory

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/directory/description`

Directory component of the collected path.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/directory`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.name

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/name/description`

Entry name without the directory.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/name`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.type

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/type/description`

Kind of filesystem entry.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/type`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.owner_uid

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/owner_uid/description`

Numeric user ID of the owner.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/owner_uid`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.owner_gid

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/owner_gid/description`

Numeric group ID of the owning group.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/owner_gid`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.size

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/size/description`

File size.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/size`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.access_time

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/access_time/description`

Last data-access time.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/access_time`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.change_time

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/change_time/description`

Last inode-status change, not creation time.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/change_time`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.modify_time

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/modify_time/description`

Last content-modification time.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/modify_time`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.setuid

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/setuid/description`

Set-user-ID permission flag.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/setuid`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.setgid

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/setgid/description`

Set-group-ID permission flag.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/setgid`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.sticky

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/sticky/description`

Sticky/restricted-deletion flag.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/sticky`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.owner_read

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/owner_read/description`

Whether the owner-read permission bit is set.

Permission flags are bits, not an effective-access guarantee; directory-specific read/write/search interpretation remains unspecified.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/owner_read`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.owner_write

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/owner_write/description`

Whether the owner-write permission bit is set.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/owner_write`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.owner_execute

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/owner_execute/description`

Whether the owner-execute/search permission bit is set.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/owner_execute`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.group_read

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/group_read/description`

Whether the group-read permission bit is set.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/group_read`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.group_write

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/group_write/description`

Whether the group-write permission bit is set.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/group_write`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.group_execute

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/group_execute/description`

Whether the group-execute/search permission bit is set.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/group_execute`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.other_read

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/other_read/description`

Whether the other-read permission bit is set.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/other_read`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.other_write

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/other_write/description`

Whether the other-write permission bit is set.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/other_write`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.other_execute

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/other_execute/description`

Whether the other-execute/search permission bit is set.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/other_execute`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / item / fields.has_extended_acl

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/field_meanings/properties/has_extended_acl/description`

Whether ACL permissions differ from standard UNIX permissions.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capabilities/unix.file.schema.json#/$defs/item_help/properties/fields/properties/has_extended_acl`; [schema file](schemas/capabilities/unix.file.schema.json).

Shared generic [typed-value grammar](schemas/result-types.schema.json) and [field predicate grammar](schemas/assessment-language.schema.json); field payload datatype consistency remains a semantic obligation.

### unix.file / require / item_requirement

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/description`

Independent requirements for the number of selected Items and the number satisfying the comparison.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement`; [schema file](schemas/assessment-language.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement`

```json
[
  {
    "type": "object",
    "required": [
      "items_found",
      "items_satisfying"
    ]
  }
]
```

### unix.file / require / field_requirement

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement/description`

Explicit shared values_found/values_matching pair; a closer complete pair overrides it without runtime defaults.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement`; [schema file](schemas/assessment-language.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement`

```json
[
  {
    "type": "object",
    "required": [
      "values_found",
      "values_matching"
    ]
  },
  {
    "default": {
      "values_found": "one_or_more",
      "values_matching": "every"
    }
  }
]
```

### unix.file / require / fields

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields/description`

One complete condition; distinct field predicates are combined with logical AND.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields`; [schema file](schemas/assessment-language.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement`

```json
[
  {
    "type": "object"
  }
]
```

### unix.file / require / item_requirement.items_found

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/properties/items_found/description`

Required cardinality of selected Items.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/properties/items_found`; [schema file](schemas/assessment-language.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement`

```json
[
  {
    "type": "string",
    "enum": [
      "none",
      "exactly_one",
      "one_or_more",
      "zero_or_more"
    ]
  },
  {
    "default": "one_or_more"
  }
]
```

### unix.file / require / item_requirement.items_satisfying

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/properties/items_satisfying/description`

Required cardinality of Items satisfying the comparison.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/properties/items_satisfying`; [schema file](schemas/assessment-language.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement`

```json
[
  {
    "type": "string",
    "enum": [
      "none",
      "exactly_one",
      "one_or_more",
      "every"
    ]
  },
  {
    "default": "every"
  }
]
```

### unix.file / require / field_requirement.values_found

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/paired_requirement/properties/values_found/description`

Required count of observed values for a field.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/paired_requirement/properties/values_found`; [schema file](schemas/assessment-language.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/paired_requirement`

```json
[
  {
    "type": "string",
    "enum": [
      "none",
      "exactly_one",
      "one_or_more",
      "every",
      "zero_or_more"
    ]
  }
]
```

### unix.file / require / field_requirement.values_matching

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/paired_requirement/properties/values_matching/description`

Required count of observed values satisfying its predicate.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/paired_requirement/properties/values_matching`; [schema file](schemas/assessment-language.schema.json).

**Parent constraints:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/paired_requirement`

```json
[
  {
    "type": "string",
    "enum": [
      "none",
      "exactly_one",
      "one_or_more",
      "every"
    ]
  }
]
```

### core / shared / input-reference

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/input_reference/description`

Uses the value of a declared Input.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/capability-common.schema.json#/$defs/entity_value/oneOf/3`; [schema file](schemas/capability-common.schema.json).

```json
[
  {
    "type": "object",
    "required": [
      "input"
    ]
  }
]
```

### core / shared / input-cardinality

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/cardinality/description`

Sets how many values a supplied Input may contain.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/cardinality`; [schema file](schemas/assessment.schema.json).

```json
[
  {
    "type": "string",
    "enum": [
      "exactly_one",
      "zero_or_one",
      "one_or_more",
      "zero_or_more"
    ]
  }
]
```

### core / shared / input-required

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/required/description`

Specifies whether this Input must be supplied.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/required`; [schema file](schemas/assessment.schema.json).

```json
[
  {
    "type": "boolean"
  }
]
```

### core / shared / field-predicate

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_field_predicate/description`

Compares a collected field's values or checks for confirmed absence.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields/additionalProperties/oneOf/0`; [schema file](schemas/assessment-language.schema.json).

```json
[
  {
    "type": "object"
  }
]
```

### core / shared / else-if

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if/description`

Selects the first true alternative branch when preceding conditions are false.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if`; [schema file](schemas/expression.schema.json).

```json
[
  {
    "type": "array",
    "minItems": 1
  }
]
```

### core / shared / not-evaluated

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated/description`

Declares that this branch cannot be evaluated and provides a reason.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated`; [schema file](schemas/expression.schema.json).

```json
[
  {
    "type": "object",
    "required": [
      "reason"
    ]
  }
]
```

### core / shared / technical-outcome

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/result-types.schema.json#/$defs/technical_outcome/description`

Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/result-types.schema.json#/$defs/technical_outcome`; [schema file](schemas/result-types.schema.json).

```json
[
  {
    "type": "string",
    "enum": [
      "true",
      "false",
      "error",
      "unknown",
      "not_evaluated",
      "not_applicable"
    ]
  }
]
```

### core / shared / value-redaction

**Description:** `https://scap-ng.dev/schema/review/issue43-phase-a/result-types.schema.json#/$defs/typed_value/properties/redacted/description`

Indicates that the value was intentionally omitted from the reported evidence.

**Shape:** `https://scap-ng.dev/schema/review/issue43-phase-a/result-types.schema.json#/$defs/typed_value/properties/redacted`; [schema file](schemas/result-types.schema.json).

```json
[
  {
    "type": "boolean"
  }
]
```

## Remaining boundaries

Unknown fields retain generic native validation and receive no invented capability help. Named Object resolution, instance/caret association, runtime errors, traversal/path binding, link/target metadata and mount classification remain separate dispatch/semantic gaps. Defaults are annotations, not inserted runtime values. [Review decisions](RECEIPT.md).
