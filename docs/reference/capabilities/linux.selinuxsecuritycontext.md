# linux.selinuxsecuritycontext

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `linux.selinuxsecuritycontext` is used to check the security context of a file or process on the local system.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.selinuxsecuritycontext.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `linux.selinuxsecuritycontext` to define the security contexts of files and processes to collect from the local system.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/filters) |
| `full_path` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/object/properties/directory](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/directory) |
| `name` | string | 0..1 | Name of a file to evaluate. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/name) |
| `pid` | integer | 0..1 | Process ID of the process. | [/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/pid) |
| `traversal` | object | 0..1 | Controls recursive searching through directories and symbolic links. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/traversal) |

### traversal

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward recursion depth; 0 includes only the starting directory. | [/$defs/file_traversal_base/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal_base/properties/max_depth) |
| `recurse` | string | 1..1 (required) | Entry types to follow during recursion. | [/$defs/file_traversal/allOf/1/properties/recurse](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/file_traversal/allOf/1/properties/recurse) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item describes the SELinux security context of a file or process on the local system.

This item follows the SELinux security context structure: user:role:type:low_sensitivity[:low_category]- high_sensitivity [:high_category].

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | string | 0..1 | Absolute path for a file on the machine. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/full_path) |
| `directory` | string | 0..1 | Directory component of the absolute path to a file on the machine. | [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/directory) |
| `name` | string | 0..1 | The name of the file. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/name) |
| `pid` | integer | 0..1 | The process ID of the process. | [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/pid) |
| `user` | string | 0..1 | SELinux user component of the security context. | [/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/user) |
| `role` | string | 0..1 | SELinux role component of the security context. | [/$defs/meanings/properties/role](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/role) |
| `type` | string | 0..1 | SELinux type or process domain component of the security context. | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/type) |
| `low_sensitivity` | string | 0..1 | Current sensitivity of a file or process. | [/$defs/meanings/properties/low_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/low_sensitivity) |
| `low_category` | string | 0..1 | Set of categories associated with the low sensitivity. | [/$defs/meanings/properties/low_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/low_category) |
| `high_sensitivity` | string | 0..1 | Maximum range for a file or the clearance for a process. | [/$defs/meanings/properties/high_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/high_sensitivity) |
| `high_category` | string | 0..1 | Set of categories associated with the high sensitivity. | [/$defs/meanings/properties/high_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/high_category) |
| `rawlow_sensitivity` | string | 0..1 | Current sensitivity of a file or process but in its raw context. | [/$defs/meanings/properties/rawlow_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawlow_sensitivity) |
| `rawlow_category` | string | 0..1 | Set of categories associated with the low sensitivity but in its raw context. | [/$defs/meanings/properties/rawlow_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawlow_category) |
| `rawhigh_sensitivity` | string | 0..1 | Maximum range for a file or the clearance for a process but in its raw context. | [/$defs/meanings/properties/rawhigh_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawhigh_sensitivity) |
| `rawhigh_category` | string | 0..1 | Set of categories associated with the high sensitivity but in its raw context. | [/$defs/meanings/properties/rawhigh_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawhigh_category) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes SELinux security context's user, type role, low sensitivity, low category, high sensitivity, high category, raw low sensitivity, raw low category, raw high sensitivity, and raw high category.

This state follows the SELinux security context structure: user:role:type:low_sensitivity[:low_category]- high_sensitivity [:high_category].

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.selinuxsecuritycontext.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
