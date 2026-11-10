# iosxe.global

Proposed documentation; frozen 0.4.0 validation is unchanged.

The global test is used to check for the existence of a particular line in the IOS-XE config file under the global context.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/iosxe.global.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a global test to define the object to be evaluated.

For the most part this object checks for existence and is used without a state comparision.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/iosxe.global.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/iosxe.global.schema.json#/$defs/object/properties/filters) |
| `global_command` | string | 0..1 | Specific line in the IOS-XE config file under the global context. | [/$defs/object/properties/global_command](../../../proposed-schema/documentation/capabilities/iosxe.global.schema.json#/$defs/object/properties/global_command) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Sotres information about the existence of a particular line in the IOS-XE config file under the global context

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `global_command` | string | 0..1 | Specific line in the IOS-XE config file under the global context. | [/$defs/meanings/properties/global_command](../../../proposed-schema/documentation/capabilities/iosxe.global.schema.json#/$defs/meanings/properties/global_command) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/iosxe.global.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/iosxe.global.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `iosxe-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
