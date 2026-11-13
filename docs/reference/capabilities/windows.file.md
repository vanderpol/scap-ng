# windows.file

Proposed documentation; frozen 0.4.1 validation is unchanged.

The file test is used to check metadata associated with Windows files.

**Contract status: unresolved.** Link/reparse traversal, time representation, ACL/effective-access interpretation and inaccessible-file behavior require native contract evidence.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.file.md) retain the validated encodings and any broader schema acceptance.

## Object

The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

The Object is used by a file test to define the specific file(s) to be evaluated.

A file object defines the path and filename or complete filepath of the file(s).

In addition, a number of behaviors may be provided that help guide the collection of objects.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/set) |
| `filepath` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/filepath) |
| `path` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/path) |
| `filename` | string | 0..1 | Name of a file to evaluate. | [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/filename) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/object/properties/filesystem](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/filesystem) |
| `traversal` | object | 0..1 | Windows file traversal. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/traversal) |

### traversal

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Explicit new-authoring selection for traversal kind; applies only in present traversal. | [/$defs/windows_file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/windows_file_traversal/allOf/1/properties/recurse) |

Validation shape: [/$defs/windows_file_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1).

## Item

This element describes file metadata.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/directory) |
| `name` | string | 0..1 | Name of the file. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/name) |
| `owner` | string | 0..1 | String that contains the name of the owner. | [/$defs/meanings/properties/owner](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/owner) |
| `size` | integer | 0..1 | Size of the file in bytes. | [/$defs/meanings/properties/size](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/size) |
| `access_time` | integer | 0..1 | Time of last access of file. | [/$defs/meanings/properties/access_time](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/access_time) |
| `creation_time` | integer | 0..1 | Time of creation of file. | [/$defs/meanings/properties/creation_time](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/creation_time) |
| `modify_time` | integer | 0..1 | Time of last modification of file. | [/$defs/meanings/properties/modify_time](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/modify_time) |
| `microsoft_checksum` | string | 0..1 | The checksum of the file as supplied by Microsoft's MapFileAndCheckSum function. | [/$defs/meanings/properties/microsoft_checksum](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/microsoft_checksum) |
| `version` | version | 0..1 | Delimited version string of the file. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/version) |
| `type` | string | 0..1 | The type field marks whether the file is a named pipe, standard file, etc. | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/type) |
| `attribute` | string | 0..1 | The attribute field marks a Windows file attribute. | [/$defs/meanings/properties/attribute](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/attribute) |
| `development_class` | string | 0..1 | The development_class field allows the distinction to be made between the GDR development environment and the QFE development environment. | [/$defs/meanings/properties/development_class](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/development_class) |
| `company` | string | 0..1 | A company name to be found within the version-information structure. | [/$defs/meanings/properties/company](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/company) |
| `internal_name` | string | 0..1 | An internal name to be found within the version-information structure. | [/$defs/meanings/properties/internal_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/internal_name) |
| `language` | string | 0..1 | A language to be found within the version-information structure. | [/$defs/meanings/properties/language](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/language) |
| `original_name` | string | 0..1 | An original filename to be found within the version-information structure. | [/$defs/meanings/properties/original_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/original_name) |
| `product_name` | string | 0..1 | A product name to be found within the version-information structure. | [/$defs/meanings/properties/product_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/product_name) |
| `product_version` | string, version | 0..1 | The product version held within the version-information structure. | [/$defs/meanings/properties/product_version](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/product_version) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different metadata associated with a Windows file.

This includes the path, filename, owner, size, last modified time, version, etc.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.file.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.file.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
