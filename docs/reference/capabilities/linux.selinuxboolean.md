# linux.selinuxboolean

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `linux.selinuxboolean` is used to check the current and pending status of a SELinux boolean.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.selinuxboolean.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `linux.selinuxboolean` to define the items to evaluate based on a specified state.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/object/properties/set) |
| `name` | string | 0..1 | The name of the SELinux boolean. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/linux_selinuxboolean_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_object/oneOf/1).

## Item

This item describes the current and pending status of a SELinux boolean.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | string | 0..1 | The name of the SELinux boolean. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/meanings/properties/name) |
| `current_status` | boolean | 0..1 | Current state of the specified SELinux boolean. | [/$defs/meanings/properties/current_status](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/meanings/properties/current_status) |
| `pending_status` | boolean | 0..1 | Pending state of the specified SELinux boolean. | [/$defs/meanings/properties/pending_status](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/meanings/properties/pending_status) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes SELinux boolean's current and pending status.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.selinuxboolean.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
