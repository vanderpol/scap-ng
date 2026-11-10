# windows.userright

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `windows.userright` is used to enumerate all of the trustees/SIDs that have been granted a specific user right/privilege.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.userright.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used to collect the trustees/SIDs that have been granted a specific user right/privilege.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/object/properties/filters) |
| `userright` | string | 0..1 | Name of a particular user right/privilege. | [/$defs/object/properties/userright](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/object/properties/userright) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `userright` | string | 0..1 | Name of a particular user right/privilege. | [/$defs/meanings/properties/userright](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/userright) |
| `trustee_name` | string | 0..1 | Unique name associated with the SID that has been granted the specified user right/privilege. | [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/trustee_name) |
| `trustee_sid` | string | 0..1 | SID that has been granted the specified user right/privilege. | [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/trustee_sid) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.userright.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
