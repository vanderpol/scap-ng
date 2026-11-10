# iosxe.version

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `iosxe.version` is used to check the version of the IOS-XE operating system.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/iosxe.version.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `iosxe.version` to define the different version information associated with an IOS-XE system.

Therefore, there are no child entities defined.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item holds information about the version of the IOS-XE operating system.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `version_string` | string | 0..1 | The entire IOS-XE version string, for example, '03.13.02.S'. | [/$defs/meanings/properties/version_string](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/version_string) |
| `major_release` | integer | 0..1 | The major version piece of the version string. | [/$defs/meanings/properties/major_release](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/major_release) |
| `release` | integer | 0..1 | The minor release piece of the version string. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/release) |
| `rebuild` | integer | 0..1 | The rebuild piece of the version string. | [/$defs/meanings/properties/rebuild](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/rebuild) |
| `train` | string | 0..1 | The train piece of the version string. | [/$defs/meanings/properties/train](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/train) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the version information held within a Cisco IOS-XE Train.

A Cisco IOS-XE train is a vehicle for delivering releases that evolve from a common code base.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/iosxe.version.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `iosxe-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
