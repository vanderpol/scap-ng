# unix.uname

Proposed documentation; frozen 0.4.0 validation is unchanged.

The uname test reveals information about the hardware the machine is running on.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/unix.uname.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by an uname test to define those objects to evaluated based on a specified state.

Therefore, there are no child entities defined.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Information about the hardware the machine is running on.

This information is the parsed equivalent of uname -a.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `machine_class` | string | 0..1 | A machine hardware name. | [/$defs/meanings/properties/machine_class](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/machine_class) |
| `node_name` | string | 0..1 | A host name. | [/$defs/meanings/properties/node_name](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/node_name) |
| `os_name` | string | 0..1 | An operating system name. | [/$defs/meanings/properties/os_name](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_name) |
| `os_release` | string | 0..1 | Operating-system release identifier. | [/$defs/meanings/properties/os_release](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_release) |
| `os_version` | string | 0..1 | Operating-system version identifier. | [/$defs/meanings/properties/os_version](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_version) |
| `processor_type` | string | 0..1 | A processor type. | [/$defs/meanings/properties/processor_type](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/processor_type) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the information about the hardware the machine is running one.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/unix.uname.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
