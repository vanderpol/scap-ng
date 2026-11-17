# windows.fileeffectiverights

Proposed documentation; frozen 0.4.1 validation is unchanged.

The file effective rights test is used to check the effective rights associated with Windows files.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.fileeffectiverights.md) retain the validated encodings and any broader schema acceptance.

## Object

The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

The Object is used by a file effective rights test to define the objects used to evalutate against the specified state.

An Object is defined as a combination of a Windows file and trustee SID.

The file represents the file to be evaluated while the trustee SID represents the account (SID) to check effective rights of.

In addition, a number of behaviors may be provided that help guide the collection of objects.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/set) |
| `filepath` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filepath) |
| `path` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/path) |
| `filename` | string | 0..1 | Name of a file to evaluate. | [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filename) |
| `trustee_sid` | string | 0..1 | Unique SID associated with a user, group, system, or program (such as a Windows service). | [/$defs/object/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/trustee_sid) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/object/properties/filesystem](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filesystem) |
| `traversal` | object | 0..1 | Windows file traversal. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/traversal) |

### traversal

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Explicit new-authoring selection for traversal kind; applies only in present traversal. | [/$defs/windows_file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/windows_file_traversal/allOf/1/properties/recurse) |

Validation shape: [/$defs/windows_fileeffectiverights_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1).

## Item

This item stores the effective rights of a file that a discretionary access control list (DACL) structure grants to a specified trustee.

The trustee's effective rights are determined checking all access-allowed and access-denied access control entries (ACEs) in the DACL.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/directory) |
| `name` | string | 0..1 | Name of the file. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/name) |
| `trustee_sid` | string | 0..1 | Unique SID that associated a user, group, system, or program (such as a Windows service). | [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/trustee_sid) |
| `trustee_name` | string | 0..1 | The trustee name associated with this particular DACL. | [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/trustee_name) |
| `standard_delete` | boolean | 0..1 | The right to delete the object. | [/$defs/meanings/properties/standard_delete](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_delete) |
| `standard_read_control` | boolean | 0..1 | The right to read the information in the object's Security Descriptor, not including the information in the SACL. | [/$defs/meanings/properties/standard_read_control](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_read_control) |
| `standard_write_dac` | boolean | 0..1 | The right to modify the DACL in the object's Security Descriptor. | [/$defs/meanings/properties/standard_write_dac](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_write_dac) |
| `standard_write_owner` | boolean | 0..1 | The right to change the owner in the object's Security Descriptor. | [/$defs/meanings/properties/standard_write_owner](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_write_owner) |
| `standard_synchronize` | boolean | 0..1 | The right to use the object for synchronization. | [/$defs/meanings/properties/standard_synchronize](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_synchronize) |
| `access_system_security` | boolean | 0..1 | Indicates access to a system access control list (SACL). | [/$defs/meanings/properties/access_system_security](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/access_system_security) |
| `generic_read` | boolean | 0..1 | Read access. | [/$defs/meanings/properties/generic_read](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_read) |
| `generic_write` | boolean | 0..1 | Write access. | [/$defs/meanings/properties/generic_write](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_write) |
| `generic_execute` | boolean | 0..1 | Execute access. | [/$defs/meanings/properties/generic_execute](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_execute) |
| `generic_all` | boolean | 0..1 | Read, write, and execute access. | [/$defs/meanings/properties/generic_all](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_all) |
| `file_read_data` | boolean | 0..1 | Effective right to read data from the file, or if a directory, grants the right to list the contents of the directory. | [/$defs/meanings/properties/file_read_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_data) |
| `file_write_data` | boolean | 0..1 | Effective right to write data to the file, or if a directory, grants the right to add a file to the directory. | [/$defs/meanings/properties/file_write_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_data) |
| `file_append_data` | boolean | 0..1 | Effective right to append data to the file, or if a directory, grants the right to add a sub-directory to the directory. | [/$defs/meanings/properties/file_append_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_append_data) |
| `file_read_ea` | boolean | 0..1 | Effective right to read extended attributes. | [/$defs/meanings/properties/file_read_ea](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_ea) |
| `file_write_ea` | boolean | 0..1 | Effective right to write extended attributes. | [/$defs/meanings/properties/file_write_ea](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_ea) |
| `file_execute` | boolean | 0..1 | Effective right to execute a file, or if a directory, the right to traverse the directory. | [/$defs/meanings/properties/file_execute](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_execute) |
| `file_delete_child` | boolean | 0..1 | Right to delete a directory and all the files it contains (its children), even if the files are read-only. | [/$defs/meanings/properties/file_delete_child](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_delete_child) |
| `file_read_attributes` | boolean | 0..1 | Effective right to read file, or directory, attributes. | [/$defs/meanings/properties/file_read_attributes](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_attributes) |
| `file_write_attributes` | boolean | 0..1 | Effective right to change file, or directory, attributes. | [/$defs/meanings/properties/file_write_attributes](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_attributes) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.fileeffectiverights.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
