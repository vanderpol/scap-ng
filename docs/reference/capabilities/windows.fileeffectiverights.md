# windows.fileeffectiverights

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/set) |
| `filepath` | object | 0..1 | Absolute path for a file on the machine. | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filepath) |
| `path` | object | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/path) |
| `filename` | null, object | 0..1 | Name of a file to evaluate. | [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filename) |
| `trustee_sid` | object | 0..1 | Unique SID associated with a user, group, system, or program (such as a Windows service). | [/$defs/object/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/trustee_sid) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/object/properties/filesystem](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filesystem) |
| `traversal` | object | 0..1 | Windows file traversal. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/traversal) |

### traversal

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Explicit new-authoring selection for traversal kind; applies only in present traversal. | [/$defs/windows_file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/windows_file_traversal/allOf/1/properties/recurse) |

Validation shape: [/$defs/windows_fileeffectiverights_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | array, object | 0..1 | Absolute path for a file on the machine. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/full_path) |
| `directory` | array, object | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/directory) |
| `name` | array, object | 0..1 | Name of the file. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/name) |
| `trustee_sid` | array, object | 0..1 | Unique SID that associated a user, group, system, or program (such as a Windows service). | [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/trustee_sid) |
| `trustee_name` | array, object | 0..1 | The trustee name associated with this particular DACL. | [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/trustee_name) |
| `standard_delete` | array, object | 0..1 | The right to delete the object. | [/$defs/meanings/properties/standard_delete](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_delete) |
| `standard_read_control` | array, object | 0..1 | The right to read the information in the object's Security Descriptor, not including the information in the SACL. | [/$defs/meanings/properties/standard_read_control](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_read_control) |
| `standard_write_dac` | array, object | 0..1 | The right to modify the DACL in the object's Security Descriptor. | [/$defs/meanings/properties/standard_write_dac](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_write_dac) |
| `standard_write_owner` | array, object | 0..1 | The right to change the owner in the object's Security Descriptor. | [/$defs/meanings/properties/standard_write_owner](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_write_owner) |
| `standard_synchronize` | array, object | 0..1 | The right to use the object for synchronization. | [/$defs/meanings/properties/standard_synchronize](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_synchronize) |
| `access_system_security` | array, object | 0..1 | Indicates access to a system access control list (SACL). | [/$defs/meanings/properties/access_system_security](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/access_system_security) |
| `generic_read` | array, object | 0..1 | Read access. | [/$defs/meanings/properties/generic_read](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_read) |
| `generic_write` | array, object | 0..1 | Write access. | [/$defs/meanings/properties/generic_write](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_write) |
| `generic_execute` | array, object | 0..1 | Execute access. | [/$defs/meanings/properties/generic_execute](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_execute) |
| `generic_all` | array, object | 0..1 | Read, write, and execute access. | [/$defs/meanings/properties/generic_all](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_all) |
| `file_read_data` | array, object | 0..1 | Effective right to read data from the file, or if a directory, grants the right to list the contents of the directory. | [/$defs/meanings/properties/file_read_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_data) |
| `file_write_data` | array, object | 0..1 | Effective right to write data to the file, or if a directory, grants the right to add a file to the directory. | [/$defs/meanings/properties/file_write_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_data) |
| `file_append_data` | array, object | 0..1 | Effective right to append data to the file, or if a directory, grants the right to add a sub-directory to the directory. | [/$defs/meanings/properties/file_append_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_append_data) |
| `file_read_ea` | array, object | 0..1 | Effective right to read extended attributes. | [/$defs/meanings/properties/file_read_ea](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_ea) |
| `file_write_ea` | array, object | 0..1 | Effective right to write extended attributes. | [/$defs/meanings/properties/file_write_ea](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_ea) |
| `file_execute` | array, object | 0..1 | Effective right to execute a file, or if a directory, the right to traverse the directory. | [/$defs/meanings/properties/file_execute](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_execute) |
| `file_delete_child` | array, object | 0..1 | Right to delete a directory and all the files it contains (its children), even if the files are read-only. | [/$defs/meanings/properties/file_delete_child](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_delete_child) |
| `file_read_attributes` | array, object | 0..1 | Effective right to read file, or directory, attributes. | [/$defs/meanings/properties/file_read_attributes](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_attributes) |
| `file_write_attributes` | array, object | 0..1 | Effective right to change file, or directory, attributes. | [/$defs/meanings/properties/file_write_attributes](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_attributes) |

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

[Local schema constraints](../advanced/windows.fileeffectiverights.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`filepath` | string | source-derived |
| Object.`path` | string | source-derived |
| Object.`filename` | string | source-derived |
| Object.`trustee_sid` | string | source-derived |
| Item.`full_path` | string | source-derived |
| Item.`directory` | string | source-derived |
| Item.`name` | string | source-derived |
| Item.`trustee_sid` | string | source-derived |
| Item.`trustee_name` | string | source-derived |
| Item.`standard_delete` | boolean | source-derived |
| Item.`standard_read_control` | boolean | source-derived |
| Item.`standard_write_dac` | boolean | source-derived |
| Item.`standard_write_owner` | boolean | source-derived |
| Item.`standard_synchronize` | boolean | source-derived |
| Item.`access_system_security` | boolean | source-derived |
| Item.`generic_read` | boolean | source-derived |
| Item.`generic_write` | boolean | source-derived |
| Item.`generic_execute` | boolean | source-derived |
| Item.`generic_all` | boolean | source-derived |
| Item.`file_read_data` | boolean | source-derived |
| Item.`file_write_data` | boolean | source-derived |
| Item.`file_append_data` | boolean | source-derived |
| Item.`file_read_ea` | boolean | source-derived |
| Item.`file_write_ea` | boolean | source-derived |
| Item.`file_execute` | boolean | source-derived |
| Item.`file_delete_child` | boolean | source-derived |
| Item.`file_read_attributes` | boolean | source-derived |
| Item.`file_write_attributes` | boolean | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
